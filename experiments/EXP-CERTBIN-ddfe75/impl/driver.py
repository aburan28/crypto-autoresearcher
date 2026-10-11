#!/usr/bin/env python3
"""EXP-CERTBIN-ddfe75 driver (N-CONV). Phases per specification execution.phases:

 0  C-SRC, C-ENGINE / C-SELF / C-FIX records present and passing; trial plan hashed
 1  archived arms, C-CONSTRUCT, C-SUPPORT, C-REG (a)-(d), C-ELL on S3-*
 2  fresh draws (four arms, seeded), keep rules, draw logs
 3  rc_b (R'_3, R'_4) on every applicable system; predictions-t5.jsonl.gz hashed
 4  M_4, W_4, W'_4 on every system; flat and wdag-v1 certificates; C-TOP,
    C-T4, C-WDAG; negative-control certificates
 5  C-DET (--phase determinism, separate process)
 6  verifier (separate process; verifier/verify_nconv.py)
 7  aggregation, decision rules, run report (--resume after phase 6)

The first invocation runs phases 0-4 and stops; after phases 5 and 6 a
--resume invocation runs phase 7. Every phase checkpoints under
<out>/checkpoint/; --resume skips completed phases.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402
from common import (ARM_SEEDS, FRESH_ARMS, INPUT_FILES, NEQ, ROOT, e_sha256, hex_to_rows,  # noqa: E402
                    now, read_jsonl_gz, rows_to_eqs, rows_to_hex, sha256_bytes, sha256_file,
                    write_json, write_jsonl_gz)

MEM_CAP = 3 * 1024 ** 3


def apply_mem_cap():
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))
        return {"RLIMIT_AS_bytes": MEM_CAP, "applied": True}
    except Exception as exc:  # pragma: no cover
        return {"RLIMIT_AS_bytes": MEM_CAP, "applied": False, "error": repr(exc)}


def maxrss_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


class Run:
    def __init__(self, args):
        self.args = args
        self.out = Path(args.out)
        self.ck = self.out / "checkpoint"
        self.ck.mkdir(parents=True, exist_ok=True)
        self.plog = self.out / "phase-log.jsonl"

    def log(self, phase, event, **kw):
        ent = {"phase": phase, "event": event, "at": now(), "maxrss_mb": maxrss_mb()}
        ent.update(kw)
        with open(self.plog, "a") as f:
            f.write(json.dumps(ent) + "\n")
        print(f"[driver] phase {phase} {event} {json.dumps(kw)[:300]}", flush=True)

    def done(self, name):
        return (self.ck / f"{name}.done").exists()

    def mark(self, name, **kw):
        (self.ck / f"{name}.done").write_text(json.dumps(dict(at=now(), **kw)) + "\n")

    def save(self, name, obj):
        write_jsonl_gz(self.ck / f"{name}.jsonl.gz", [obj])

    def load(self, name):
        return read_jsonl_gz(self.ck / f"{name}.jsonl.gz")[0]

    def stop(self, phase, control, detail):
        write_json(self.out / "STOP.json", {"phase": phase, "control": control, "detail": detail,
                                            "at": now()})
        self.log(phase, "STOP", control=control)
        print(f"[driver] STOP at phase {phase}: {control}", flush=True)
        sys.exit(4)


def git_state():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    return head, bool(st.strip()), st.splitlines()


# ---------------------------------------------------------------------------
# phase 0
# ---------------------------------------------------------------------------
def phase0(R):
    R.log(0, "start")
    ep = R.out / "engine-provenance" / "summary.json"
    st = R.out / "selftest.json"
    if not ep.exists() or not json.load(open(ep)).get("pass"):
        R.stop(0, "C-ENGINE", "engine-provenance/summary.json missing or failing")
    if not st.exists():
        R.stop(0, "C-SELF", "selftest.json missing")
    stj = json.load(open(st))
    if not stj.get("C-SELF_pass"):
        R.stop(0, "C-SELF", "selftest failing")
    if not stj.get("C-FIX_pass"):
        R.stop(0, "C-FIX", "fixture dimensions differ")
    inputs = {"files": {}, "pass": True}
    for p, want in INPUT_FILES.items():
        got = sha256_file(ROOT / p)
        inputs["files"][p] = {"sha256": got, "bound": want, "equal": got == want}
        inputs["pass"] &= got == want
    inputs["checked_at"] = now()
    write_json(R.out / "inputs.json", inputs)
    if not inputs["pass"]:
        R.stop(0, "C-SRC", [p for p, v in inputs["files"].items() if not v["equal"]])
    plan = Path(R.args.plan)
    spec = Path(R.args.spec)
    info = {"trial_plan_sha256": sha256_file(plan), "trial_plan_path": str(plan),
            "spec_sha256": sha256_file(spec)}
    pj = json.load(open(plan))
    info["trial_plan_written_at"] = pj.get("written_at")
    info["engine_provenance_started"] = json.load(open(ep))["started"]
    info["trial_plan_predates_phase0"] = pj.get("written_at", "9") < info["engine_provenance_started"]
    R.save("p0", info)
    R.log(0, "end", **info)
    R.mark("p0")


# ---------------------------------------------------------------------------
# phase 1
# ---------------------------------------------------------------------------
REG_W4_FIELDS = ["iterations_to_fixpoint", "dims", "final_dim", "one", "one_first_iteration",
                 "dims_by_deg", "new_fallen_per_iteration", "stack_rows_per_iteration"]


def archived_systems(B):
    sets = json.load(open(common.P_INSTANCE_SETS))["sets"]
    sizes = {k: len(v) for k, v in sets.items()}
    xr144 = []
    for sname in ["U62", "S62", "C20"]:
        for r in sets[sname]:
            xr144.append((sname, r["idx"], r["archived"]["x_R"]))
    systems = []
    slot_of = {(s, i): n for n, (s, i, _) in enumerate(xr144)}
    for arm, sname in [("S3-U62", "U62"), ("S3-C20", "C20"), ("S3-S62", "S62"),
                       ("NULL-AFF62", "N-AFF62"), ("NULL-F262", "N-F262")]:
        for pos, r in enumerate(sets[sname]):
            a = r["archived"]
            systems.append({"key": r["key"], "arm": arm, "role": "unsat" if a["s"] == 0 else "sat",
                            "slot": slot_of[(sname, r["idx"])] if arm.startswith("S3-") else pos,
                            "source_set": sname, "idx": r["idx"], "x_R": a["x_R"], "attempt": None,
                            "E_hex": r["E_hex"], "E_sha256": r["E_sha256"], "archived": a})
    nell = json.load(open(common.P_NELL))
    for pos, r in enumerate(nell["instances"]):
        systems.append({"key": "NELL-A20:" + r["label"], "arm": "NELL-A20", "role": "unsat", "slot": pos,
                        "source_set": "NELL-A20", "idx": r["draw"], "x_R": None, "attempt": None,
                        "E_hex": r["E_hex"], "E_sha256": r["E_sha256"],
                        "archived": {"s": 0, "c": r["c"], "label": r["label"]}})
    return sizes, xr144, systems


def closures_archived_job(sysrec):
    import closures
    rows = hex_to_rows(sysrec["E_hex"])
    eqs = rows_to_eqs(rows)
    out = {"key": sysrec["key"]}
    if sysrec["arm"] != "NELL-A20":
        m3, _ = closures.run_m(closures.C3, eqs, False)
        out["M_3"] = m3
    m4, c4 = closures.run_m(closures.C4, eqs, True)
    w4, cw = closures.run_w(closures.C4, eqs, True)
    out["M_4"], out["M_4_cert"] = m4, c4
    out["W_4"], out["W_4_cert"] = w4, cw
    out["rc_b"] = closures.rcb_phase3(rows)
    return out


def phase1(R):
    import construct
    import satcount
    from crypto_autoresearcher.gf2 import kernels
    R.log(1, "start")
    t0 = time.time()
    curve = json.load(open(common.P_CURVE))
    B = int(curve["B"])
    sizes, xr144, systems = archived_systems(B)
    if (sizes.get("U62"), sizes.get("S62"), sizes.get("C20")) != (62, 62, 20) or len(xr144) != 144:
        R.stop(1, "xr144 size (contract defect)", sizes)
    checks = {}
    # C-CONSTRUCT
    sets = json.load(open(common.P_INSTANCE_SETS))["sets"]
    mism = []
    for (sname, idx, xr) in xr144:
        rec = [r for r in sets[sname] if r["idx"] == idx][0]
        if construct.e_s3(xr, B) != hex_to_rows(rec["E_hex"]):
            mism.append(f"{sname}:{idx}")
    checks["C-CONSTRUCT"] = {"checked": len(xr144), "mismatches": mism, "pass": not mism}
    # C-SUPPORT
    import gzip
    U = construct.union_support(B)
    SL = construct.s_l_positions(U)
    p1 = json.load(gzip.open(common.P_P1))
    arch_sizes = p1["F-NULLF2"]["union_support_size_per_eq"]
    my_sizes = [common.popcount(u) for u in U]
    outside = []
    for s in systems:
        if s["arm"] == "NULL-F262":
            rows = hex_to_rows(s["E_hex"])
            if any(r & ~U[k] for k, r in enumerate(rows)):
                outside.append(s["key"])
    bil = 0
    for c in common.BILINEAR_COLS:
        bil |= 1 << c
    lin = 0
    for c in common.LIN_COLS:
        lin |= 1 << c
    reading = all(U[k] == (bil | lin | ((B >> k) & 1)) for k in range(NEQ))
    support = {"U_hex": [format(u, "x") for u in U], "sizes_per_eq": my_sizes,
               "archived_sizes_per_eq": arch_sizes, "sizes_equal": my_sizes == arch_sizes,
               "NULL_F262_outside_U": outside, "S_L": SL, "S_L_size": len(SL),
               "S_L_constant_positions": [k for (k, c) in SL if c == 0],
               "expected_S_L_size_under_reading": 17 * 18 + common.popcount(B),
               "coordinator_reading_true": reading,
               "coordinator_reading": "U_k = 81 bilinear + 18 linear columns, plus the constant iff bit k of B is 1"}
    write_json(R.out / "support.json", support)
    checks["C-SUPPORT"] = {"sizes_equal": my_sizes == arch_sizes, "null_f262_inside_U": not outside,
                           "coordinator_reading_true": reading,
                           "pass": my_sizes == arch_sizes and not outside}
    if not checks["C-CONSTRUCT"]["pass"]:
        R.save("p1_fail", {"checks": checks})
        R.stop(1, "C-CONSTRUCT", mism)
    if not checks["C-SUPPORT"]["pass"]:
        R.save("p1_fail", {"checks": checks})
        R.stop(1, "C-SUPPORT", checks["C-SUPPORT"])
    # own s for archived systems
    for s in systems:
        sc, sols = satcount.count_solutions(hex_to_rows(s["E_hex"]))
        s["s"] = sc
        s["solutions"] = sols if sc > 0 else []
    own_s_mism = [s["key"] for s in systems if s["s"] != s["archived"]["s"]]
    checks["archived_s_own_vs_archived"] = {"mismatches": own_s_mism, "pass": not own_s_mism}
    # closures on archived arms
    t = time.time()
    res = kernels.map_threads(closures_archived_job, systems)
    R.log(1, "closures", n=len(res), seconds=round(time.time() - t, 1))
    byk = {r["key"]: r for r in res}
    # C-REG (a), (b)
    rc1 = {}
    for r in read_jsonl_gz(common.P_RC1_CLOSURES):
        rc1[(r["key"], r["closure"])] = r
    a_bad, b_bad = [], []
    for s in systems:
        if s["arm"] == "NELL-A20":
            continue
        r = byk[s["key"]]
        a = s["archived"]
        if (r["M_3"]["rank"], r["M_3"]["one"], r["M_4"]["rank"], r["M_4"]["one"]) != \
                (a["rank_3"], a["one_in_R_3"], a["rank_4"], a["one_in_R_4"]):
            a_bad.append(s["key"])
        ref = rc1.get((s["key"], "W_4"))
        if ref is None or any(r["W_4"].get(f) != ref.get(f) for f in REG_W4_FIELDS):
            b_bad.append(s["key"])
    # C-REG (c)
    c_bad = []
    u62_893 = None
    for s in systems:
        if not s["arm"].startswith("S3-"):
            continue
        rb = byk[s["key"]]["rc_b"]
        if rb["ell_linear_support"] != [0, 9]:
            c_bad.append(f"{s['key']}: ell support {rb['ell_linear_support']}")
            continue
        prof = rb["R4"]["dims_by_deg"]
        if s["arm"] == "S3-U62":
            want = [1, 17, 153, 833, 2212] if s["idx"] == 893 else [1, 18, 154, 834, 2213]
            if s["idx"] == 893:
                u62_893 = prof
            if prof != want:
                c_bad.append(f"{s['key']}: {prof}")
        elif s["arm"] == "S3-C20":
            if prof != [1, 18, 154, 834, 2213]:
                c_bad.append(f"{s['key']}: {prof}")
    s62 = sorted([s for s in systems if s["arm"] == "S3-S62"], key=lambda x: x["idx"])[:10]
    for s in s62:
        prof = byk[s["key"]]["rc_b"]["R4"]["dims_by_deg"]
        sv = s["s"]
        if prof[:4] != [0, 18 - sv, 154 - sv, 834 - sv]:
            c_bad.append(f"{s['key']}: {prof} s={sv}")
    if u62_893 is None:
        c_bad.append("S3-U62 idx 893 not present")
    # C-REG (d)
    o2 = json.load(open(common.P_O2ENG))
    o2rows = {r["label"]: r["engine"] for r in o2["rows"]}
    d_bad = []
    for s in systems:
        if s["arm"] != "NELL-A20":
            continue
        r = byk[s["key"]]
        ref = o2rows.get(s["archived"]["label"])
        fields = [f for f in ref if f != "certificate_emitted"]
        if any(r["W_4"].get(f) != ref[f] for f in fields) or \
                ref.get("certificate_emitted") != (r["W_4_cert"] is not None):
            d_bad.append(f"{s['key']}: W_4")
        if r["rc_b"].get("R4", {}).get("dims_by_deg") != [0, 0, 16, 288, 2328]:
            d_bad.append(f"{s['key']}: R'_4 {r['rc_b'].get('R4', {}).get('dims_by_deg')}")
    checks["C-REG"] = {"a_mismatches": a_bad, "b_mismatches": b_bad, "c_mismatches": c_bad,
                       "d_mismatches": d_bad, "S3_S62_lowest10": [s["key"] for s in s62],
                       "pass": not (a_bad or b_bad or c_bad or d_bad)}
    # C-ELL on S3-*
    ell_bad = []
    for s in systems:
        if not s["arm"].startswith("S3-"):
            continue
        rb = byk[s["key"]]["rc_b"]
        want = sum(b << k for k, b in enumerate(construct.ell_coeffs(s["x_R"])))
        if rb["kernel_dim"] != 1 or rb["c"] != want:
            ell_bad.append(s["key"])
    checks["C-ELL_S3"] = {"checked": sum(1 for s in systems if s["arm"].startswith("S3-")),
                          "violations": ell_bad, "pass": not ell_bad}
    for s in systems:
        s.pop("archived_rc1", None)
    R.save("p1", {"xr144": xr144, "B": B, "U": [format(u, "x") for u in U], "systems": systems,
                  "results": res, "checks": checks})
    if not checks["C-REG"]["pass"]:
        R.stop(1, "C-REG", checks["C-REG"])
    R.log(1, "end", seconds=round(time.time() - t0, 1),
          checks={k: v["pass"] for k, v in checks.items()})
    R.mark("p1")


# ---------------------------------------------------------------------------
# phase 2
# ---------------------------------------------------------------------------
def phase2(R):
    import draws
    p1 = R.load("p1")
    B = p1["B"]
    U = [int(u, 16) for u in p1["U"]]
    xr144 = [tuple(x) for x in p1["xr144"]]
    ctx = draws.ArmContext(B, U, xr144)
    R.log(2, "start")
    for arm in FRESH_ARMS:
        if R.done(f"p2-{arm}"):
            continue
        t = time.time()
        attempts, kept, exhausted = draws.run_arm(arm, ARM_SEEDS[arm], ctx,
                                                  log_cb=lambda m: print(f"[driver] {m}", flush=True))
        write_jsonl_gz(R.out / f"draws-{arm}.jsonl.gz", attempts)
        systems = []
        for kp in kept:
            slot = kp["slot"]
            bound = arm in ("N-CONV", "N-CONVL")
            rec = {"key": f"{arm}:{slot}:{kp['role']}", "arm": arm, "role": kp["role"], "slot": slot,
                   "source_set": xr144[slot][0] if bound else None,
                   "idx": xr144[slot][1] if bound else None,
                   "x_R": xr144[slot][2] if bound else None,
                   "attempt": kp["attempt"], "E_hex": kp["E_hex"], "E_sha256": kp["E_sha256"],
                   "s": kp["s"], "solutions": kp["solutions"]}
            rec.update(kp["info"])
            systems.append(rec)
        R.save(f"p2-{arm}", {"systems": systems, "exhausted": exhausted, "n_attempts": len(attempts),
                             "draws_sha256": sha256_file(R.out / f"draws-{arm}.jsonl.gz")})
        R.log(2, f"arm {arm}", attempts=len(attempts), kept=len(kept), exhausted=len(exhausted),
              seconds=round(time.time() - t, 1),
              draws_sha256=sha256_file(R.out / f"draws-{arm}.jsonl.gz"))
        R.mark(f"p2-{arm}")
    # instances.jsonl.gz: archived arms first, then fresh arms
    allsys = all_systems(R)
    recs = []
    for s in allsys:
        r = {k: s.get(k) for k in ["key", "arm", "role", "slot", "source_set", "idx", "x_R", "attempt",
                                   "E_hex", "E_sha256", "s"]}
        if s["role"] == "sat":
            r["solutions"] = s["solutions"]
        for k in ("bprime", "c"):
            if k in s:
                r[k] = s[k]
        recs.append(r)
    write_jsonl_gz(R.out / "instances.jsonl.gz", recs)
    R.log(2, "end", instances=len(recs), instances_sha256=sha256_file(R.out / "instances.jsonl.gz"))
    R.mark("p2")


def all_systems(R):
    p1 = R.load("p1")
    out = list(p1["systems"])
    for arm in FRESH_ARMS:
        out.extend(R.load(f"p2-{arm}")["systems"])
    return out


# ---------------------------------------------------------------------------
# phase 3
# ---------------------------------------------------------------------------
def rcb_job(s):
    import closures
    return {"key": s["key"], "rc_b": closures.rcb_phase3(hex_to_rows(s["E_hex"]))}


def phase3(R):
    import construct
    from crypto_autoresearcher.gf2 import kernels
    R.log(3, "start")
    t = time.time()
    p1 = R.load("p1")
    arch_rcb = {r["key"]: r["rc_b"] for r in p1["results"]}
    fresh = [s for s in all_systems(R) if s["arm"] in FRESH_ARMS]
    res = kernels.map_threads(rcb_job, fresh)
    rcbs = dict(arch_rcb)
    for r in res:
        rcbs[r["key"]] = r["rc_b"]
    # C-ELL on fresh N-CONV / N-CONVL
    ell_bad = []
    n = 0
    for s in fresh:
        if s["arm"] not in ("N-CONV", "N-CONVL"):
            continue
        n += 1
        rb = rcbs[s["key"]]
        want = sum(b << k for k, b in enumerate(construct.ell_coeffs(s["x_R"])))
        if rb["kernel_dim"] != 1 or rb["c"] != want:
            ell_bad.append(f"{s['key']}: kernel_dim {rb['kernel_dim']}")
        elif s["arm"] == "N-CONVL" and rb["ell_linear_support"] != [0, 9]:
            ell_bad.append(f"{s['key']}: ell support {rb['ell_linear_support']}")
    preds = []
    for s in all_systems(R):
        rb = rcbs[s["key"]]
        if not rb["substituted"]:
            continue
        preds.append({"key": s["key"], "arm": s["arm"], "role": s["role"],
                      "rank_R3": rb["R3"]["rank"], "R4_dims_by_deg": rb["R4"]["dims_by_deg"],
                      "R4_rank": rb["R4"]["rank"], "one_in_R4": rb["R4"]["one"],
                      "T5_applicable": rb["T5_applicable"],
                      "T5_prediction": rb.get("T5_prediction"),
                      "T4_prediction": "final_dim(W_4) = final_dim(W'_4) + 834; one(W_4) = one(W'_4)"})
    write_jsonl_gz(R.out / "predictions-t5.jsonl.gz", preds)
    h = sha256_file(R.out / "predictions-t5.jsonl.gz")
    R.save("p3", {"rcb": rcbs, "checks": {"C-ELL_fresh": {"checked": n, "violations": ell_bad,
                                                          "pass": not ell_bad}}})
    R.log(3, "end", predictions_t5_sha256=h, n_predictions=len(preds),
          n_T5_applicable=sum(1 for p in preds if p["T5_applicable"]),
          note="predictions-t5.jsonl.gz written and hashed BEFORE phase 4",
          seconds=round(time.time() - t, 1))
    R.mark("p3", predictions_t5_sha256=h)


# ---------------------------------------------------------------------------
# phase 4
# ---------------------------------------------------------------------------
def p4_job(item):
    import closures
    s, rb, prev = item
    rows = hex_to_rows(s["E_hex"])
    eqs = rows_to_eqs(rows)
    out = {"key": s["key"]}
    if prev is None:
        m4, c4 = closures.run_m(closures.C4, eqs, True)
        w4, cw = closures.run_w(closures.C4, eqs, True)
    else:
        m4, c4, w4, cw = prev["M_4"], prev["M_4_cert"], prev["W_4"], prev["W_4_cert"]
    out["M_4"], out["M_4_cert"], out["W_4"], out["W_4_cert"] = m4, c4, w4, cw
    if w4["one"]:
        body, xrec = closures.extract_wdag(rows, w4)
        out["wdag"], out["wdag_extractor"] = body, xrec
    if rb["substituted"]:
        out["W'_4"] = closures.w4_prime(rows, rb)
    return out


def phase4(R):
    import negctl
    from crypto_autoresearcher.gf2 import closure as eclosure
    from crypto_autoresearcher.gf2 import kernels
    R.log(4, "start")
    t0 = time.time()
    p1 = R.load("p1")
    p3 = R.load("p3")
    prev = {r["key"]: r for r in p1["results"]}
    systems = all_systems(R)
    arms_order = ["S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262", "NELL-A20"] + FRESH_ARMS
    for arm in arms_order:
        if R.done(f"p4-{arm}"):
            continue
        t = time.time()
        items = [(s, p3["rcb"][s["key"]], prev.get(s["key"])) for s in systems if s["arm"] == arm]
        res = kernels.map_threads(p4_job, items)
        R.save(f"p4-{arm}", {"results": res})
        R.log(4, f"arm {arm}", n=len(res), seconds=round(time.time() - t, 1),
              w4_refuted=sum(1 for r in res if r["W_4"]["one"]),
              m4_refuted=sum(1 for r in res if r["M_4"]["one"]))
        R.mark(f"p4-{arm}")
    res = {}
    for arm in arms_order:
        for r in R.load(f"p4-{arm}")["results"]:
            res[r["key"]] = r
    rcbs = p3["rcb"]
    # closures.jsonl.gz and certificates.jsonl.gz
    clines, certs = [], []
    import closures as CL
    for s in systems:
        k = s["key"]
        r = res[k]
        base = {"key": k, "arm": s["arm"], "role": s["role"]}
        if "M_3" in prev.get(k, {}):
            clines.append(dict(base, closure="M_3", **prev[k]["M_3"]))
        m4 = dict(r["M_4"])
        m4.update(CL.derived_m4(m4))
        m4["label"] = "refuted" if m4["one"] else "not_refuted"
        m4["profile_is_unsubst_semiregular"] = m4["dims_by_deg"] == CL.UNSUBST_REF
        clines.append(dict(base, closure="M_4", **m4))
        w4 = dict(r["W_4"])
        w4["label"] = "refuted" if w4["one"] else "not_refuted"
        w4["codim"] = 4048 - w4["final_dim"]
        if "wdag_extractor" in r:
            w4["wdag_extractor"] = r["wdag_extractor"]
        clines.append(dict(base, closure="W_4", **w4))
        rb = rcbs[k]
        rl = {kk: vv for kk, vv in rb.items() if kk not in ("R3", "R4")}
        clines.append(dict(base, closure="rc_b", **rl))
        if rb["substituted"]:
            clines.append(dict(base, closure="R'_3", **rb["R3"]))
            clines.append(dict(base, closure="R'_4", **rb["R4"]))
            clines.append(dict(base, closure="W'_4", **r["W'_4"]))
        if r["M_4_cert"] is not None:
            cj = eclosure.cert_to_json([tuple(x) for x in r["M_4_cert"]])
            certs.append(dict(base, closure="M_4", format="flat-v1", source="engine macaulay_closure",
                              max_mu=max((len(mu) for mu, _ in cj), default=0), size=len(cj), body=cj))
        if r["W_4_cert"] is not None:
            cj = eclosure.cert_to_json([tuple(x) for x in r["W_4_cert"]])
            certs.append(dict(base, closure="W_4", format="flat-v1", source="engine w_closure",
                              max_mu=max((len(mu) for mu, _ in cj), default=0), size=len(cj), body=cj))
        if r.get("wdag") is not None:
            b = r["wdag"]
            certs.append(dict(base, closure="W_4", format="wdag-v1", source="impl wdag extractor",
                              node_count=len(b["nodes"]),
                              size=sum(len(n["rows"]) for n in b["nodes"]), body=b))
    for i, c in enumerate(certs):
        c["cid"] = i
    write_jsonl_gz(R.out / "closures.jsonl.gz", clines)
    write_jsonl_gz(R.out / "certificates.jsonl.gz", certs)
    # engine-side instrument checks: C-TOP, C-T4, C-WDAG, C-PS (engine)
    checks = {}
    P = {k: res[k]["M_4"]["rank"] - res[k]["M_4"]["dims_by_deg"][3] for k in res}
    s3_at_slot = {s["slot"]: s["key"] for s in systems if s["arm"].startswith("S3-")}
    top_bad = []
    for s in systems:
        if s["arm"] in ("N-CONV", "N-CONVL"):
            ref = s3_at_slot[s["slot"]]
            if P[s["key"]] != P[ref]:
                top_bad.append(f"{s['key']}: P {P[s['key']]} vs {ref} P {P[ref]}")
    p17 = sorted({P[s["key"]] for s in systems if s["arm"] == "N-CONV17"})
    if len(p17) > 1:
        top_bad.append(f"N-CONV17 P values {p17}")
    checks["C-TOP"] = {"checked": sum(1 for s in systems if s["arm"] in ("N-CONV", "N-CONVL", "N-CONV17")),
                       "N-CONV17_P_values": p17, "violations": top_bad, "pass": not top_bad}
    t4_bad, t5_bad = [], []
    nt4 = nt5 = 0
    for s in systems:
        k = s["key"]
        rb = rcbs[k]
        if not rb["substituted"]:
            continue
        nt4 += 1
        w4, w4p = res[k]["W_4"], res[k]["W'_4"]
        if w4["final_dim"] != w4p["final_dim"] + 834 or w4["one"] != w4p["one"]:
            t4_bad.append(f"{k}: W_4 {w4['final_dim']}/{w4['one']} W'_4 {w4p['final_dim']}/{w4p['one']}")
        if rb["T5_applicable"]:
            nt5 += 1
            pr = rb["T5_prediction"]
            if w4["one"] != pr["W4_refuted"] or w4["final_dim"] != pr["W4_final_dim"]:
                t5_bad.append(f"{k}: W_4 {w4['final_dim']}/{w4['one']} predicted {pr}")
    checks["C-T4"] = {"T4_checked": nt4, "T4_violations": t4_bad, "T5_checked": nt5,
                      "T5_violations": t5_bad, "pass": not (t4_bad or t5_bad)}
    wd_bad, unc = [], []
    nref = 0
    for k, r in res.items():
        if not r["W_4"]["one"]:
            continue
        nref += 1
        x = r.get("wdag_extractor")
        if r.get("wdag") is None:
            unc.append(k)
        if x and x["extractor_dims"] is not None and not (x["dims_equal_engine"] and x["depth_equal_engine"]):
            wd_bad.append(f"{k}: extractor dims {x['extractor_dims']} engine {r['W_4']['dims']}")
    n_eng_ref = sum(1 for r in res.values() if r["M_4"]["one"]) + nref
    n_sub = sum(1 for c in certs if c["format"] == "flat-v1")
    checks["C-WDAG"] = {"W4_refutations": nref, "dimension_mismatches": wd_bad, "uncertified": unc,
                        "engine_refutations_M4_plus_W4": n_eng_ref,
                        "engine_flat_certificates_submitted": n_sub,
                        "every_engine_refutation_submitted": n_sub == n_eng_ref,
                        "pass": not wd_bad and n_sub == n_eng_ref}
    ps_bad, codim = [], []
    for s in systems:
        if s["role"] != "sat":
            continue
        r = res[s["key"]]
        if r["M_4"]["one"] or r["W_4"]["one"]:
            ps_bad.append(f"{s['key']}: refuted (M_4 {r['M_4']['one']}, W_4 {r['W_4']['one']})")
        if s["s"] <= 31:
            cd = 4048 - r["W_4"]["final_dim"]
            codim.append((s["key"], s["s"], cd))
            if cd < s["s"]:
                ps_bad.append(f"{s['key']}: codim {cd} < s {s['s']}")
    checks["C-PS_engine"] = {"satisfiable_controls": sum(1 for s in systems if s["role"] == "sat"),
                             "codim_checked": len(codim), "violations": ps_bad, "pass": not ps_bad}
    # negative controls
    Fcache = {}
    rows_of = {s["key"]: hex_to_rows(s["E_hex"]) for s in systems}

    def F_of(key):
        if key not in Fcache:
            Fcache[key] = negctl.masks_of(rows_of[key], common.COL_MASK)
        return Fcache[key]

    by_arm = {}
    for s in systems:
        if s["role"] == "unsat":
            by_arm.setdefault(s["arm"], []).append(s["key"])
    nc, ncplan = negctl.build(certs, by_arm, F_of)
    write_jsonl_gz(R.out / "negative-controls-certificates.jsonl.gz", nc)
    R.save("p4", {"checks": checks, "ncplan": ncplan})
    R.log(4, "end", seconds=round(time.time() - t0, 1), certificates=len(certs),
          negative_controls=len(nc), checks={k: v["pass"] for k, v in checks.items()},
          certificates_bytes=os.path.getsize(R.out / "certificates.jsonl.gz"))
    R.mark("p4")


# ---------------------------------------------------------------------------
# phase 5: C-DET (separate process)
# ---------------------------------------------------------------------------
def phase_det(R):
    import closures
    import draws
    from crypto_autoresearcher.gf2 import kernels
    t0 = time.time()
    R.log(5, "start")
    p1 = R.load("p1")
    B = p1["B"]
    U = [int(u, 16) for u in p1["U"]]
    xr144 = [tuple(x) for x in p1["xr144"]]
    ctx = draws.ArmContext(B, U, xr144)
    det = {"control": "C-DET", "a_draw_logs": {}, "started": now()}
    for arm in FRESH_ARMS:
        attempts, kept, exh = draws.run_arm(arm, ARM_SEEDS[arm], ctx)
        h_new = sha256_bytes(common.jsonl_gz_bytes(attempts))
        h_file = sha256_file(R.out / f"draws-{arm}.jsonl.gz")
        det["a_draw_logs"][arm] = {"sha256_regenerated": h_new, "sha256_file": h_file, "equal": h_new == h_file}
    systems = all_systems(R)
    p3 = R.load("p3")
    cl = {}
    for r in read_jsonl_gz(R.out / "closures.jsonl.gz"):
        cl[(r["key"], r["closure"])] = r
    sel = sorted([s for s in systems if s["arm"] == "N-CONV" and s["role"] == "unsat"], key=lambda s: s["slot"])[:10]
    sel += sorted([s for s in systems if s["arm"] == "N-CONV" and s["role"] == "sat"], key=lambda s: s["slot"])[:5]
    sel += sorted([s for s in systems if s["arm"] == "N-ELL144" and s["role"] == "unsat"], key=lambda s: s["slot"])[:5]

    def job(s):
        rows = hex_to_rows(s["E_hex"])
        eqs = rows_to_eqs(rows)
        m4, _ = closures.run_m(closures.C4, eqs, False)
        w4, _ = closures.run_w(closures.C4, eqs, False)
        rb = closures.rcb_phase3(rows)
        return s["key"], m4, w4, rb

    def compare(results):
        bad = []
        for key, m4, w4, rb in results:
            for name, got in (("M_4", m4), ("W_4", w4)):
                ref = cl[(key, name)]
                for f in got:
                    if f in ("wall_seconds", "engine_self_check_sum_is_1"):
                        continue
                    if got[f] != ref.get(f):
                        bad.append(f"{key} {name}.{f}")
            ref_rb = p3["rcb"][key]
            for f in ("kernel_dim", "c", "label", "j_star", "T5_applicable"):
                if rb.get(f) != ref_rb.get(f):
                    bad.append(f"{key} rc_b.{f}")
            if rb["substituted"]:
                for f in ("rank", "one", "dims_by_deg"):
                    if rb["R3"][f] != ref_rb["R3"][f] or rb["R4"][f] != ref_rb["R4"][f]:
                        bad.append(f"{key} R'.{f}")
        return bad

    thr = kernels.default_threads()
    r_thr = kernels.map_threads(job, sel, thr)
    r_one = kernels.map_threads(job, sel, 1)
    det["b_recompute"] = {"systems": [s["key"] for s in sel], "threads": thr, "mismatches": compare(r_thr)}
    det["c_threads1"] = {"systems": [s["key"] for s in sel], "threads": 1, "mismatches": compare(r_one)}
    det["pass"] = (all(v["equal"] for v in det["a_draw_logs"].values()) and not det["b_recompute"]["mismatches"]
                   and not det["c_threads1"]["mismatches"] and len(sel) == 20)
    det["finished"] = now()
    det["seconds"] = round(time.time() - t0, 1)
    det["pid"] = os.getpid()
    write_json(R.out / "determinism.json", det)
    R.log(5, "end", pass_=det["pass"], seconds=det["seconds"])


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--phase", default="main", choices=["main", "determinism"])
    args = ap.parse_args()
    os.chdir(ROOT)
    if (common.DEV_SLOTS or common.DEV_SEED_OFFSET) and \
            str(Path(args.out).resolve()).startswith(str((ROOT / "experiments").resolve())):
        raise SystemExit("development overrides NCONV_DEV_* are set: refusing to write under experiments/")
    cap = apply_mem_cap()
    R = Run(args)
    head, dirty, st = git_state()
    inv = {"argv": sys.argv, "at": now(), "pid": os.getpid(), "commit": head, "dirty": dirty,
           "dirty_paths": st, "mem_cap": cap,
           "env": {k: os.environ.get(k) for k in ["CRYPTO_AR_GF2_BACKEND", "PYTHONDONTWRITEBYTECODE",
                                                   "CRYPTO_AR_GF2_THREADS", "RUN_ID", "OPENBLAS_NUM_THREADS"]}}
    with open(R.ck / "invocations.jsonl", "a") as f:
        f.write(json.dumps(inv) + "\n")
    if os.environ.get("CRYPTO_AR_GF2_BACKEND") != "native":
        R.stop(0, "C-ENGINE", "CRYPTO_AR_GF2_BACKEND is not native")
    if args.phase == "determinism":
        if not R.done("p4"):
            R.stop(5, "order", "determinism phase requested before phase 4 completed")
        phase_det(R)
        return 0
    for name, fn in [("p0", phase0), ("p1", phase1), ("p2", phase2), ("p3", phase3), ("p4", phase4)]:
        if R.done(name):
            if not args.resume:
                print(f"[driver] {name} already done; use --resume", flush=True)
                return 5
            continue
        fn(R)
    if (R.out / "certificate-verification.json").exists() and (R.out / "determinism.json").exists():
        import analysis
        analysis.phase7(R, args)
    else:
        print("[driver] phases 0-4 complete. Next: --phase determinism (phase 5), the verifier "
              "(phase 6), then --resume (phase 7).", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
