#!/usr/bin/env python3
"""EXP-CERTBIN-060020 driver (execution.phases).

    driver.py --spec SPEC --plan PLAN --run-id RUN --out RUN_DIR [--resume]
        phases 0-4 and C-LIT (phase 5, in-process); then stops awaiting the
        separate-process phases (determinism, backend, verifier); with
        --resume after them: phase 7 (aggregation, decision rules, report).
    driver.py ... --phase determinism   (C-DET, separate process)
    driver.py ... --phase backend       (C-BACKEND, CRYPTO_AR_GF2_BACKEND=reference)

Checkpoints live in RUN_DIR/checkpoint/; every phase is skipped on --resume
once its checkpoint exists. A per-system closure watchdog (3600 s) and an RSS
guard (3 GiB) checkpoint and exit; they are never results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

import numpy as np

import common as C
from gf2n import field
from curve import Curve
from descent import Descent
from oracles import Exhaustive
import arms as AR
import closures as CL
import rcb as RB

ARMS_ORDER = ["S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]
DRAW_FILES = {"S3-PRIMARY": "draws-S3-PRIMARY.jsonl.gz", "N-CONV19": "draws-N-CONV19.jsonl.gz",
              "N-ELL19": "draws-N-ELL19.jsonl.gz", "N-F219": "draws-N-F219.jsonl.gz",
              "N-AFF19": "draws-N-AFF19.jsonl.gz", "F-RANDX19": "draws-F-RANDX19.jsonl.gz"}
FULL_QUOTAS = {"u400": 400, "sat100": 100, "cap_primary": 5000, "conv_slots": 200, "conv_sat_slots": 50,
               "per_slot": 256, "stream_u": 200, "stream_s": 50, "stream_cap": 20000, "aff_fam": 5,
               "aff_u": 40, "aff_s": 10, "randx_quota": 200, "randx_cap": 30000,
               "t4_first": 50, "nonref_controls": 5, "backend_first": 10, "backend_nonref": 10,
               "lit_first": 5, "lit_nonref": 20}
WATCHDOG_S = 3600
RSS_CAP_MIB = 3 * 1024


class Run:
    def __init__(self, args):
        self.args = args
        self.out = Path(args.out)
        self.ck = self.out / "checkpoint"
        self.ck.mkdir(parents=True, exist_ok=True)
        self.dev = bool(args.dev_quotas or args.dev_seeds)
        runs_dir = (C.EXP / "runs").resolve()
        if self.dev and str(self.out.resolve()).startswith(str(runs_dir)):
            raise SystemExit("development overrides are refused inside the experiment's runs/ directory")
        self.Q = dict(FULL_QUOTAS)
        if args.dev_quotas:
            dq = args.dev_quotas
            self.Q.update(json.loads(open(dq[1:]).read() if dq.startswith("@") else dq))
        self.seeds = dict(C.SEEDS)
        if args.dev_seeds:
            ds = args.dev_seeds
            self.seeds.update(json.loads(open(ds[1:]).read() if ds.startswith("@") else ds))
        self.timer = C.PhaseTimer()
        F = field(C.N, C.MODULUS)
        self.F = F
        self.ctx = AR.Ctx(F, Curve(F, C.A, C.B), Descent(F, C.L, C.B), Exhaustive(C.L))
        self.threads = int(os.environ.get("CRYPTO_AR_GF2_THREADS", "1"))

    # ---- checkpoint helpers ------------------------------------------------------
    def done(self, name):
        return (self.ck / f"{name}.json").exists()

    def mark(self, name, obj):
        C.write_json(self.ck / f"{name}.json", obj)

    def load(self, name):
        return json.loads((self.ck / f"{name}.json").read_text())

    def append_timing(self):
        path = self.ck / "timings.jsonl"
        with open(path, "a") as f:
            for r in self.timer.records:
                f.write(json.dumps(r) + "\n")
        self.timer.records = []


# =============================================================================
# phase 0
# =============================================================================
def phase0(R):
    out = R.out
    ep = out / "engine-provenance" / "engine-provenance.json"
    st = out / "selftest.json"
    res = {"started_utc": C.utc_now()}
    ok = ep.exists() and json.loads(ep.read_text()).get("pass")
    res["C-ENGINE_record_pass"] = bool(ok)
    ok2 = st.exists() and json.loads(st.read_text()).get("pass")
    res["selftest_pass"] = bool(ok2)
    plan_path = Path(R.args.plan)
    res["plan_sha256"] = C.sha256_file(plan_path)
    plan = json.loads(plan_path.read_text())
    res["plan_written_utc"] = plan.get("written_utc")
    res["plan_predates_phase0"] = bool(plan.get("written_utc") and plan["written_utc"] <= res["started_utc"])
    res["spec_sha256"] = C.sha256_file(R.args.spec)
    res["spec_matches_plan"] = res["spec_sha256"] == plan["written_from"]["specification_sha256"]
    res["draw_files_present_before_phase1"] = [f for f in DRAW_FILES.values() if (out / f).exists()]
    if not (ok and ok2 and res["plan_predates_phase0"] and res["spec_matches_plan"]
            and not res["draw_files_present_before_phase1"]):
        res["pass"] = False
        R.mark("phase0-stop", res)
        raise SystemExit(f"phase 0 STOP: {res}")
    # C-SLICE17
    with R.timer("phase0:C-SLICE17"):
        s17 = slice17()
    C.write_json(out / "slice17.json", s17)
    res["C-SLICE17_pass"] = s17["pass"]
    if not s17["pass"]:
        R.mark("phase0-stop", res)
        raise SystemExit("C-SLICE17 failed: STOP before phase 1 (INV-4)")
    res["pass"] = True
    res["impl_module_sha256"] = C.impl_module_hashes()
    R.mark("phase0", res)


def slice17():
    from gf2n import field as fld
    from descent import Descent as Dsc, kernel_basis, combine_rows, substitute
    cj = json.loads((C.ROOT / "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json").read_text())
    F17 = fld(C.N17, C.MODULUS17)
    D17 = Dsc(F17, C.L17, cj["B"])
    sets = json.loads((C.ROOT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json")
                      .read_text())["sets"]
    masks17 = [sum(1 << i for i in m) for m in C.eq_monomials(C.NV17)]
    a_bad, b_bad, n = [], [], 0
    subs = {}
    for name in ("U62", "S62", "C20"):
        for r in sets[name]:
            n += 1
            E = D17.E_direct(r["archived"]["x_R"])
            if C.E_to_hex(E) != r["E_hex"]:
                a_bad.append(r["key"])
            ker = kernel_basis(E[:, 1 + C.NV17:])
            if len(ker) != 1:
                b_bad.append(r["key"])
                continue
            ell = combine_rows(E, ker[0])
            if [int(j) for j in np.flatnonzero(ell[1:1 + C.NV17])] != [0, 9]:
                b_bad.append(r["key"])
            if name == "U62" and r["idx"] in (27, 893):
                eqs2, jstar, aff = substitute(E, ell, masks17, C.NV17)
                r4, _ = CL.macaulay(C.NV17 - 1, 4, C.NEQ17, eqs2, want_cert=False)
                subs[r["idx"]] = r4
    want = {27: [1, 18, 154, 834, 2213], 893: [1, 17, 153, 833, 2212]}
    c_ok = all(subs.get(i, {}).get("dims_by_deg") == w for i, w in want.items())
    return {"field": "t^17 + t^3 + 1", "l": 9, "curve": {"A": cj["A"], "B": cj["B"]},
            "a_instances": n, "a_E_hex_mismatches": a_bad, "b_ell_support_v0_v9_failures": b_bad,
            "c_substituted_profiles": {str(k): v for k, v in subs.items()},
            "c_expected": {str(k): v for k, v in want.items()}, "closure": "Closure(17, 4, 17).macaulay_closure",
            "pass": n == 144 and not a_bad and not b_bad and c_ok}


# =============================================================================
# phases 1-2: instance sets
# =============================================================================
def coordinator_reading(ctx, E, xR):
    """object.parts reading on one S_3 system: only bilinear/linear/constant
    columns; bilinear = phi_{x_R}(t^{i+j}); linear = x_R^2 t^{2j}; constant = B."""
    F, D = ctx.F, ctx.D
    l = C.L
    for c, m in enumerate(C.EQ_MONS):
        col = int(sum(int(E[k, c]) << k for k in range(C.NEQ)))
        if len(m) == 0:
            want = C.B
        elif len(m) == 1:
            j = m[0] % l
            want = F.mul(F.mul(xR, xR), F.mul(1 << j, 1 << j))
        else:
            i, j = m
            if (i < l) == (j < l):
                want = 0
            else:
                tij = F.exp[i + (j - l)]
                want = F.mul(tij, tij) ^ F.mul(xR, tij)
        if col != want:
            return False
    return True


def phase1(R):
    ctx, Q = R.ctx, R.Q
    with R.timer("phase1:S3-PRIMARY"):
        pr = AR.s3_primary(ctx, R.seeds["S3-PRIMARY"], Q["u400"], Q["sat100"], Q["cap_primary"])
    sha = C.write_jsonl_gz(R.out / DRAW_FILES["S3-PRIMARY"], pr["draws"])
    U = ctx.U
    reading = all(coordinator_reading(ctx, C.E_from_hex(r["E_hex"]), r["x_R"]) for r in pr["U400"] + pr["SAT100"])
    within_half = [c for c, m in enumerate(C.EQ_MONS) if len(m) == 2 and ((m[0] < C.L) == (m[1] < C.L))]
    support = {"U_row_sizes": [int(x) for x in U.sum(axis=1)], "U_size": int(U.sum()),
               "Upos": [int(x) for x in ctx.Upos], "S_L_positions": [int(x) for x in ctx.SL_pos],
               "S_L_size": int(ctx.SL_pos.size),
               "S_L_row_sizes": [int(sum(1 for p in ctx.SL_pos if p // C.NCOL == k)) for k in range(C.NEQ)],
               "U_hex": C.E_to_hex(U.astype(np.uint8)),
               "U_has_within_half_quadratic_columns": bool(U[:, within_half].any()),
               "coordinator_reading_object_parts_true_on_S3_primary_kept": bool(reading),
               "tau": ctx.tau, "ell_lin_support": [int(j) for j in np.flatnonzero(ctx.ell_lin)],
               "E0_nnz": int(ctx.E0.sum()), "Ej_nnz": [int(e.sum()) for e in ctx.Ej]}
    C.write_json(R.out / "support.json", support)
    R.mark("phase1", {"U400": pr["U400"], "SAT100": pr["SAT100"], "classified": pr["classified"],
                      "all_x": sorted(pr["all_x"]), "checks": pr["checks"], "shortfall": pr["shortfall"],
                      "attempts": pr["attempts"], "draws_sha256": sha, "reading": reading,
                      "impl_module_sha256": C.impl_module_hashes()})


def phase2(R):
    ctx, Q = R.ctx, R.Q
    p1 = R.load("phase1")
    res = {"draws_sha256": {"S3-PRIMARY": p1["draws_sha256"]}, "impl_module_sha256": C.impl_module_hashes()}
    with R.timer("phase2:N-CONV19"):
        cv = AR.n_conv19(ctx, R.seeds["N-CONV19"], p1["U400"][:Q["conv_slots"]], Q["conv_sat_slots"], Q["per_slot"])
    res["draws_sha256"]["N-CONV19"] = C.write_jsonl_gz(R.out / DRAW_FILES["N-CONV19"], cv["draws"])
    with R.timer("phase2:N-ELL19"):
        ne = AR.stream_arm(ctx, "N-ELL19", R.seeds["N-ELL19"], True, Q["stream_u"], Q["stream_s"], Q["stream_cap"])
    res["draws_sha256"]["N-ELL19"] = C.write_jsonl_gz(R.out / DRAW_FILES["N-ELL19"], ne["draws"])
    with R.timer("phase2:N-F219"):
        nf = AR.stream_arm(ctx, "N-F219", R.seeds["N-F219"], False, Q["stream_u"], Q["stream_s"], Q["stream_cap"])
    res["draws_sha256"]["N-F219"] = C.write_jsonl_gz(R.out / DRAW_FILES["N-F219"], nf["draws"])
    with R.timer("phase2:N-AFF19"):
        na = AR.n_aff19(ctx, R.seeds["N-AFF19"], p1["classified"], Q["aff_fam"], Q["aff_u"], Q["aff_s"])
    res["draws_sha256"]["N-AFF19"] = C.write_jsonl_gz(R.out / DRAW_FILES["N-AFF19"], na["draws"])
    with R.timer("phase2:F-RANDX19"):
        rx = AR.f_randx19(ctx, R.seeds["F-RANDX19"], set(p1["all_x"]), Q["randx_quota"], Q["randx_cap"])
    res["draws_sha256"]["F-RANDX19"] = C.write_jsonl_gz(R.out / DRAW_FILES["F-RANDX19"], rx["draws"])
    rx_reading = all(coordinator_reading(ctx, C.E_from_hex(r["E_hex"]), r["x_R"]) for r in rx["kept"])
    inst = p1["U400"] + p1["SAT100"] + cv["kept"] + ne["kept"] + nf["kept"] + na["kept"] + rx["kept"]
    res["instances_sha256"] = C.write_jsonl_gz(R.out / "instances.jsonl.gz", inst)
    res["sizes"] = {a: sum(1 for r in inst if r["arm"] == a) for a in ARMS_ORDER}
    res["sizes_by_role"] = {a: {ro: sum(1 for r in inst if r["arm"] == a and r["role"] == ro) for ro in ("unsat", "sat")}
                            for a in ARMS_ORDER}
    res["F-RANDX19_strata"] = {s: sum(1 for r in rx["kept"] if r["stratum"] == s) for s in AR.STRATA}
    res["N-AFF19_families"] = {str(d): {ro: sum(1 for r in na["kept"] if r["family"] == d and r["role"] == ro)
                                        for ro in ("unsat", "sat")} for d in range(1, Q["aff_fam"] + 1)}
    res["shortfalls"] = {"S3-PRIMARY": p1["shortfall"], "N-CONV19_exhausted": cv["exhausted"],
                         "N-ELL19": ne["shortfall"], "N-F219": nf["shortfall"], "N-AFF19": na["shortfall"],
                         "F-RANDX19": rx["shortfall"]}
    res["attempts"] = {"S3-PRIMARY": p1["attempts"], "N-CONV19": len(cv["draws"]), "N-ELL19": ne["attempts"],
                       "N-F219": nf["attempts"], "N-AFF19": len(na["draws"]), "F-RANDX19": rx["attempts"]}
    res["checks"] = {"S3-PRIMARY": p1["checks"], "F-RANDX19": rx["checks"],
                     "support_outside_U": {"N-ELL19": ne["outside_U"], "N-F219": nf["outside_U"]},
                     "coordinator_reading_F-RANDX19": rx_reading}
    res["draw_stats"] = draw_stats(R)
    R.mark("phase2", res)


def draw_stats(R):
    out = {}
    for arm, f in DRAW_FILES.items():
        d = C.read_jsonl_gz(R.out / f)
        oc = {}
        for r in d:
            oc[r["outcome"]] = oc.get(r["outcome"], 0) + 1
        with_s = [r for r in d if "s" in r]
        out[arm] = {"attempts": len(d), "outcomes": oc, "with_s": len(with_s),
                    "unsat_fraction_among_classified": (sum(1 for r in with_s if r["s"] == 0) / len(with_s)
                                                        if with_s else None)}
    return out


def load_instances(R):
    return C.read_jsonl_gz(R.out / "instances.jsonl.gz")


# =============================================================================
# phase 3: rc_b and predictions
# =============================================================================
def phase3(R):
    inst = load_instances(R)
    ctx = R.ctx
    recs = []
    preds = []
    with R.timer("phase3:rc_b"):
        def one(r):
            E = C.E_from_hex(r["E_hex"])
            info, _ = RB.rc_b(E, r["arm"], R.F, r.get("x_R"), ctx.ell_lin)
            return info
        infos = CL.kernels.map_threads(one, inst, R.threads)
    for r, info in zip(inst, infos):
        recs.append({"key": r["key"], **info})
        arm = r["arm"]
        p = {"key": r["key"], "arm": arm, "role": r["role"]}
        if arm == "N-ELL19":
            if info.get("substituted") and info.get("T5_applicable"):
                p["prediction"] = "T5"
                p["T5"] = RB.t5_prediction(info)
            else:
                p["prediction"] = "not applicable"
                p["reason"] = info.get("label") if not info.get("substituted") else "T5 condition fails"
        elif arm in ("N-F219", "N-AFF19"):
            p["prediction"] = "conditional-unsubstituted"
            p["condition"] = "rank(M_3) == 399 and dims_by_deg(M_4) == [0, 0, 19, 399, 3819] (checked in phase 4 before W_4 is scored)"
            p["then"] = {"one": False, "final_dim": 3819, "dims_by_deg": list(C.REF_UNSUB),
                         "iterations_to_fixpoint": 0, "W_4_equals_M_4": True}
        else:
            p["prediction"] = "none (S_3 / N-CONV19: no semi-regular prediction; EX-4)"
        preds.append(p)
    sha_r = C.write_jsonl_gz(R.ck / "rcb.jsonl.gz", recs)
    sha_p = C.write_jsonl_gz(R.out / "predictions.jsonl.gz", preds)
    R.mark("phase3", {"predictions_sha256": sha_p, "predictions_written_utc": C.utc_now(), "rcb_sha256": sha_r,
                      "impl_module_sha256": C.impl_module_hashes()})


# =============================================================================
# phase 4: closures
# =============================================================================
class Watch:
    def __init__(self, R):
        self.R = R
        self.inflight = {}
        self.lock = threading.Lock()
        self.stop = False
        self.t = threading.Thread(target=self.loop, daemon=True)
        self.t.start()

    def begin(self, key):
        with self.lock:
            self.inflight[key] = time.time()

    def end(self, key):
        with self.lock:
            self.inflight.pop(key, None)

    def loop(self):
        while not self.stop:
            time.sleep(5)
            now = time.time()
            with self.lock:
                late = [k for k, t in self.inflight.items() if now - t > WATCHDOG_S]
            rss = rss_mib()
            if late or rss > RSS_CAP_MIB:
                obj = {"utc": C.utc_now(), "expired_keys": late, "rss_mib": rss,
                       "reason": "per-system closure watchdog" if late else "RSS guard"}
                prev = []
                p = self.R.ck / "watchdog-expired.json"
                if p.exists():
                    prev = json.loads(p.read_text()).get("history", [])
                obj["history"] = prev + [obj.copy()]
                C.write_json(p, obj)
                print("WATCHDOG", json.dumps(obj), flush=True)
                os._exit(75)


def rss_mib():
    try:
        with open("/proc/self/statm") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 2 ** 20
    except Exception:
        return 0.0


def derived(r4):
    d = r4["dims_by_deg"]
    return {"P": r4["rank"] - d[3], "fallen": d[3], "linear_forms": d[1] - d[0], "syzygy_excess": 3819 - r4["rank"]}


def process_system(r, rcinfo, watch):
    key = r["key"]
    watch.begin(key)
    try:
        t0 = time.time()
        E = C.E_from_hex(r["E_hex"])
        eqs = C.E_to_eqs(E)
        out = {"key": key, "arm": r["arm"], "role": r["role"], "certs": []}
        r3, c3 = CL.macaulay(C.NV, 3, C.NEQ, eqs, want_cert=True)
        r4, c4 = CL.macaulay(C.NV, 4, C.NEQ, eqs, want_cert=True)
        out["M_3"], out["M_4"] = r3, r4
        out["derived"] = derived(r4)
        if c3 is not None:
            out["certs"].append({"key": key, "closure": "M_3", "format": "flat-v1",
                                 "body": {"C": CL.flat_to_json(c3)}, "max_mu": CL.flat_maxdeg(c3)})
        if c4 is not None:
            out["certs"].append({"key": key, "closure": "M_4", "format": "flat-v1",
                                 "body": {"C": CL.flat_to_json(c4)}, "max_mu": CL.flat_maxdeg(c4)})
        t1 = time.time()
        ell_route = None
        ell_cert = None
        if r["arm"] in RB.ELL_ARMS and rcinfo.get("kernel_dim") == 1 and rcinfo.get("applicable"):
            cvec = sum(b << k for k, b in enumerate(rcinfo["c"]))
            ell_row = np.zeros(C.NCOL, dtype=np.uint8)
            ell_row[rcinfo["ell_support"]] = 1
            em = CL.ell_masks_from_row(ell_row, C.EQ_MASKS)
            ell_route, ell_cert = CL.ell_route(CL.get_closure(C.NV, 4, C.NEQ), eqs, em, cvec, want_cert=True)
        out["ell_route"] = ell_route
        t2 = time.time()
        rec, flat, ext, final, cl = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=True,
                                                 general_wdag=not bool(ell_route))
        out["W_4"] = rec
        t3 = time.time()
        wd = None
        if rec["one"]:
            out["certs"].append({"key": key, "closure": "W_4", "format": "flat-v1",
                                 "body": {"C": CL.flat_to_json(flat)}, "max_mu": CL.flat_maxdeg(flat),
                                 "note": "engine flat certificate; counts toward W_4 only if max|mu| <= 2"})
            info = ext["info"] if ext else {"depth": 0, "nb_per_level": [None]}
            if rec["one_first_iteration"] == 0:
                wd, cons = CL.flat_as_wdag(cl, flat), "one-node (M_4 refutation at iteration 0)"
            elif ell_route:
                wd, cons = ell_cert, "ell-route (1 in M_4 + ell * B_{<=3}; prefix-shared chains)"
            else:
                wd, cons = ext.get("wdag") if ext else None, "general (grouped level-wise back-trace)"
            dims_ok = (info["depth"] == rec["one_first_iteration"] and
                       all(info["nb_per_level"][L] == rec["dims"][L - 1] for L in range(1, info["depth"] + 1)))
            out["wdag"] = {"construction": cons, "extractor_depth": info["depth"],
                           "extractor_nb_per_level": info["nb_per_level"], "C-WDAG_dims_ok": bool(dims_ok),
                           "produced": wd is not None}
            if wd is not None:
                out["certs"].append({"key": key, "closure": "W_4", "format": "wdag-v1", "body": wd,
                                     "construction": cons})
        out["wall_seconds_measured"] = {"M_3+M_4": round(t1 - t0, 3), "ell_route": round(t2 - t1, 3),
                                        "W_4+extraction": round(t3 - t2, 3), "total": round(time.time() - t0, 3)}
        return out
    finally:
        watch.end(key)


def load_main(R):
    """Phase-4 per-system results from the atomic gzipped chunk files."""
    done = {}
    d = R.ck / "phase4"
    if d.exists():
        for f in sorted(d.glob("chunk-*.jsonl.gz")):
            for o in C.read_jsonl_gz(f):
                done[o["key"]] = o
    return done


def phase4(R):
    inst = load_instances(R)
    rcb = {r["key"]: r for r in C.read_jsonl_gz(R.ck / "rcb.jsonl.gz")}
    cdir = R.ck / "phase4"
    cdir.mkdir(exist_ok=True)
    done = load_main(R)
    expired = set()
    wp = R.ck / "watchdog-expired.json"
    if wp.exists():
        for h in json.loads(wp.read_text()).get("history", []):
            expired.update(h.get("expired_keys", []))
    todo = [r for r in inst if r["key"] not in done and r["key"] not in expired]
    C.log(f"phase4: {len(done)} done, {len(expired)} expired, {len(todo)} to do, threads {R.threads}")
    watch = Watch(R)
    with R.timer("phase4:closures"):
        B = 40
        nchunk = len(list(cdir.glob("chunk-*.jsonl.gz")))
        for i in range(0, len(todo), B):
            chunk = todo[i:i + B]
            res = CL.kernels.map_threads(lambda r: process_system(r, rcb[r["key"]], watch), chunk, R.threads)
            C.write_jsonl_gz(cdir / f"chunk-{nchunk:05d}.jsonl.gz", res)
            nchunk += 1
            for o in res:
                done[o["key"]] = o
            if (i // B) % 5 == 0:
                C.log(f"phase4: {len(done)}/{len(inst)} rss {rss_mib():.0f} MiB")
    watch.stop = True
    for k in expired:
        done[k] = {"key": k, "undetermined": "UNDETERMINED(budget)", "certs": []}
    R.mark("phase4-main", {"n": len(done), "expired": sorted(expired), "utc": C.utc_now()})


def phase4_post(R):
    """C-T4 W'_4 sets and ann-v1 extraction (C-NONREF), after the main pass."""
    inst = load_instances(R)
    byk = {r["key"]: r for r in inst}
    rcb = {r["key"]: r for r in C.read_jsonl_gz(R.ck / "rcb.jsonl.gz")}
    main = load_main(R)
    Q = R.Q

    def keys(arm, role="unsat"):
        return [r["key"] for r in inst if r["arm"] == arm and r["role"] == role]

    def nonref(k):
        return k in main and "W_4" in main[k] and not main[k]["W_4"]["one"]

    t4 = set(r["key"] for r in inst if r["arm"] == "N-ELL19")
    t4 |= set(keys("S3-U400")[:Q["t4_first"]])
    t4 |= set(keys("N-CONV19")[:Q["t4_first"]])
    t4 |= set(k for k in keys("S3-U400") if nonref(k))
    ann = set(k for k in keys("S3-U400") if nonref(k))
    ann_ctl = {}
    for arm in ("N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"):
        ks = [k for k in keys(arm) if nonref(k)][:Q["nonref_controls"]]
        ann_ctl[arm] = ks
        ann |= set(ks)
    todo = sorted(t4 | ann, key=lambda k: (ARMS_ORDER.index(byk[k]["arm"]), int(k.split(":")[1])))
    post_path = R.ck / "phase4-post.jsonl"
    donep = {}
    if post_path.exists():
        for line in post_path.read_text().splitlines():
            if line.strip():
                o = json.loads(line)
                donep[o["key"]] = o
    todo = [k for k in todo if k not in donep]
    ann_dir = R.ck / "ann"
    ann_dir.mkdir(exist_ok=True)
    watch = Watch(R)

    def work(k):
        watch.begin(k)
        try:
            r = byk[k]
            E = C.E_from_hex(r["E_hex"])
            eqs = C.E_to_eqs(E)
            o = {"key": k}
            if k in ann:
                t = time.time()
                rec, flat, ext, final, cl = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=False)
                Lh = CL.annihilator(final[0], final[1], cl.C)
                body = {"D": 4, "nv": C.NV, "neq": C.NEQ, "L_hex": Lh}
                data = C.jsonl_gz_bytes([{"key": k, "closure": "W_4", "format": "ann-v1", "body": body}])
                (ann_dir / (k.replace(":", "_") + ".jsonl.gz")).write_bytes(data)
                o["ann"] = {"n_functionals": len(Lh), "rerun_record_equal": rec == main[k]["W_4"],
                            "codim": cl.C - rec["final_dim"], "sha256": hashlib.sha256(data).hexdigest(),
                            "bytes": len(data), "seconds_measured": round(time.time() - t, 2)}
            if k in t4:
                info, eqs2 = RB.rc_b(E, r["arm"], R.F, r.get("x_R"), R.ctx.ell_lin, want_eqs=True)
                if eqs2 is None:
                    o["T4"] = {"applicable": False, "reason": info.get("label")}
                else:
                    w2, *_ = CL.w_closure(C.NV - 1, 4, C.NEQ, eqs2, want_cert=False)
                    w = main[k]["W_4"]
                    o["T4"] = {"applicable": True, "W'_4": w2,
                               "final_dim_ok": w["final_dim"] == w2["final_dim"] + C.T4_CONST,
                               "one_ok": w["one"] == w2["one"]}
            return o
        finally:
            watch.end(k)

    with R.timer("phase4:post (W'_4, ann-v1)"):
        with open(post_path, "a") as fh:
            for i in range(0, len(todo), 20):
                res = CL.kernels.map_threads(work, todo[i:i + 20], R.threads)
                for o in res:
                    fh.write(json.dumps(o, sort_keys=True) + "\n")
                    donep[o["key"]] = o
                fh.flush()
    watch.stop = True
    R.mark("phase4-post", {"t4_set": sorted(t4), "ann_set_S3": sorted(k for k in ann if k.startswith("S3-U400")),
                           "ann_set_controls": ann_ctl, "utc": C.utc_now()})


def phase4_write(R):
    """Assemble closures / certificates / annihilators, score the phase-4
    checks, build the negative controls."""
    inst = load_instances(R)
    byk = {r["key"]: r for r in inst}
    rcb = {r["key"]: r for r in C.read_jsonl_gz(R.ck / "rcb.jsonl.gz")}
    preds = {p["key"]: p for p in C.read_jsonl_gz(R.out / "predictions.jsonl.gz")}
    main = load_main(R)
    post = {}
    for line in (R.ck / "phase4-post.jsonl").read_text().splitlines():
        if line.strip():
            o = json.loads(line)
            post[o["key"]] = o
    pinfo = R.load("phase4-post")
    closures, certs = [], []
    checks = {"C-MONO": [], "C-WDAG": [], "C-PRED": [], "C-T4": [], "C-TOP19": [], "C-PS": [],
              "C-ELL": [], "uncertified": []}
    pred_eval = []
    for r in inst:
        k = r["key"]
        m = main.get(k)
        rc = rcb[k]
        row = {"key": k, "arm": r["arm"], "role": r["role"], "s": r["s"],
               "rc_b": {a: b for a, b in rc.items() if a != "key"}}
        for fld in ("slot", "family", "stratum", "x_R", "attempt"):
            if fld in r:
                row[fld] = r[fld]
        if m is None or m.get("undetermined"):
            row["label"] = "UNDETERMINED(budget)"
            closures.append(row)
            continue
        for fld in ("M_3", "M_4", "W_4", "derived", "ell_route", "wdag", "wall_seconds_measured"):
            if fld in m:
                row[fld] = m[fld]
        if k in post:
            if "T4" in post[k]:
                row["T4"] = post[k]["T4"]
            if "ann" in post[k]:
                row["ann"] = post[k]["ann"]
        # labels
        o3, o4, ow = m["M_3"]["one"], m["M_4"]["one"], m["W_4"]["one"]
        if not ((not o3 or o4) and (not o4 or ow)):
            checks["C-MONO"].append(k)
        if ow:
            w = m.get("wdag", {})
            if not w.get("C-WDAG_dims_ok"):
                checks["C-WDAG"].append(k)
            if not w.get("produced"):
                checks["uncertified"].append(k)
        if r["arm"] in RB.ELL_ARMS and rc.get("C-ELL_ok") is False:
            checks["C-ELL"].append(k)
        if r["arm"] in RB.ELL_ARMS and "C-ELL_ok" not in rc:
            checks["C-ELL"].append(k + " (kernel not 1-dimensional)")
        # C-PS
        if r["role"] == "sat":
            codim = 6196 - m["W_4"]["final_dim"]
            ps = {"key": k, "s": r["s"], "codim": codim, "refuted": bool(o3 or o4 or ow),
                  "codim_ge_s": codim >= r["s"], "codim_eq_s": (codim == r["s"]) if r["s"] <= 31 else None}
            row["C-PS"] = ps
            if ps["refuted"] or not ps["codim_ge_s"]:
                checks["C-PS"].append(ps)
        # C-T4
        if "T4" in row and row["T4"].get("applicable"):
            if not (row["T4"]["final_dim_ok"] and row["T4"]["one_ok"]):
                checks["C-T4"].append(k)
        # C-PRED
        p = preds.get(k, {})
        if p.get("prediction") == "T5":
            T5 = p["T5"]
            w = m["W_4"]
            it_pred = 1 if m["M_4"]["rank"] < T5["final_dim"] else 0
            ok = (w["one"] == T5["one"] and w["final_dim"] == T5["final_dim"]
                  and w["dims_by_deg"] == T5["dims_by_deg"] and w["iterations_to_fixpoint"] == it_pred)
            if "full_reference_record" in T5:
                ok = ok and all(w[f] == v for f, v in T5["full_reference_record"].items())
            pred_eval.append({"key": k, "type": "T5", "ok": ok, "full_reference": "full_reference_record" in T5})
            if not ok:
                checks["C-PRED"].append(k)
        elif p.get("prediction") == "conditional-unsubstituted":
            cond = m["M_3"]["rank"] == 399 and m["M_4"]["dims_by_deg"] == C.REF_UNSUB
            if cond:
                w = m["W_4"]
                ok = (not w["one"] and w["final_dim"] == 3819 and w["dims_by_deg"] == C.REF_UNSUB
                      and w["iterations_to_fixpoint"] == 0)
                pred_eval.append({"key": k, "type": "unsubstituted", "ok": ok})
                if not ok:
                    checks["C-PRED"].append(k)
            else:
                pred_eval.append({"key": k, "type": "unsubstituted", "ok": None,
                                  "note": "prediction not applicable (reference profile does not hold)"})
        for c in m["certs"]:
            certs.append({"key": c["key"], "closure": c["closure"], "format": c["format"], "body": c["body"]})
        closures.append(row)
    # C-TOP19
    s3P = {r["key"]: main[r["key"]]["derived"]["P"] for r in inst if r["arm"] == "S3-U400" and r["key"] in main
           and "derived" in main[r["key"]]}
    top = []
    for r in inst:
        if r["arm"] == "N-CONV19" and r["key"] in main and "derived" in main[r["key"]]:
            a = main[r["key"]]["derived"]["P"]
            b = s3P.get(r["s3_key"])
            top.append({"key": r["key"], "slot": r["slot"], "P": a, "P_S3": b, "equal": a == b})
            if a != b:
                checks["C-TOP19"].append(r["key"])
    sha_c = C.write_jsonl_gz(R.out / "closures.jsonl.gz", closures)
    sha_ce = C.write_jsonl_gz(R.out / "certificates.jsonl.gz", certs)
    # annihilators: concatenate per-system files in key order (output_bound applied in phase 7 report)
    ann_dir = R.ck / "ann"
    ann_keys = pinfo["ann_set_S3"] + [k for ks in pinfo["ann_set_controls"].values() for k in ks]
    ann_keys = sorted(set(ann_keys), key=lambda k: (ARMS_ORDER.index(byk[k]["arm"]), int(k.split(":")[1])))
    # output_bound: if the S3-U400 ann-v1 set alone exceeds 100 MiB, keep the
    # first 40 in draw order; the rest stay (verified in-run) in checkpoint/ann/,
    # listed with sha256 and size, flagged "not archived".
    s3_keys = [k for k in ann_keys if k.startswith("S3-U400:")]
    s3_bytes = sum((ann_dir / (k.replace(":", "_") + ".jsonl.gz")).stat().st_size for k in s3_keys
                   if (ann_dir / (k.replace(":", "_") + ".jsonl.gz")).exists())
    bound = s3_bytes > 100 * 2 ** 20
    nonarch = s3_keys[40:] if bound else []
    recs = []
    for k in ann_keys:
        if k in nonarch:
            continue
        f = ann_dir / (k.replace(":", "_") + ".jsonl.gz")
        if f.exists():
            recs.extend(C.read_jsonl_gz(f))
    sha_a = C.write_jsonl_gz(R.out / "annihilators.jsonl.gz", recs)
    na_list = []
    for k in nonarch:
        f = ann_dir / (k.replace(":", "_") + ".jsonl.gz")
        na_list.append({"key": k, "path": str(f.relative_to(R.out)), "sha256": C.sha256_file(f),
                        "bytes": f.stat().st_size, "flag": "not archived (output_bound); verified in-run"})
    C.write_json(R.out / "annihilators-nonarchived.json",
                 {"output_bound_applied": bound, "S3-U400_ann_bytes": s3_bytes, "files": na_list})
    nc = negative_controls(R, inst, main, certs, recs)
    sha_n = C.write_jsonl_gz(R.out / "negative-controls-certificates.jsonl.gz", nc["records"])
    R.mark("phase4", {"closures_sha256": sha_c, "certificates_sha256": sha_ce, "annihilators_sha256": sha_a,
                      "negative_controls_sha256": sha_n, "negative_controls_plan": nc["plan"],
                      "checks": checks, "pred_eval": pred_eval, "top19": top,
                      "impl_module_sha256": C.impl_module_hashes(), "utc": C.utc_now()})


# =============================================================================
# negative controls (C-VERIFIER)
# =============================================================================
def negative_controls(R, inst, main, certs, anns):
    byk = {r["key"]: r for r in inst}
    rng = np.random.Generator(np.random.PCG64(C.SEEDS["S_selftest"] + 999))  # corruption choices only
    recs = []
    plan = {}
    nid = [0]

    def add(kind, typ, key, closure, fmt, body, base):
        recs.append({"nc_id": f"NC-{nid[0]:04d}", "kind": kind, "type": typ, "key": key, "closure": closure,
                     "format": fmt, "body": body, "base_key": base})
        nid[0] += 1

    by_kind = {}
    for c in certs:
        arm = c["key"].split(":")[0]
        if c["closure"] == "M_4" and c["format"] == "flat-v1":
            by_kind.setdefault(("M_4", arm), []).append(c)
        if c["closure"] == "W_4" and c["format"] == "wdag-v1":
            by_kind.setdefault(("W_4", arm), []).append(c)
    w4flat = {}
    for c in certs:
        if c["closure"] == "W_4" and c["format"] == "flat-v1":
            mx = max((len(mu) for mu, k in c["body"]["C"]), default=0)
            if mx == 3:
                w4flat.setdefault(c["key"].split(":")[0], []).append(c)
    for (clo, arm), cs in sorted(by_kind.items()):
        kind = f"{clo}|{arm}"
        plan[kind] = {"base_certificates": len(cs), "types": {}}
        for t in range(3):
            c = cs[t % len(cs)]
            body = json.loads(json.dumps(c["body"]))
            # (a) one row removed
            if c["format"] == "flat-v1":
                b = json.loads(json.dumps(body))
                del b["C"][int(rng.integers(0, len(b["C"])))]
            else:
                b = json.loads(json.dumps(body))
                cand = [i for i, nd in enumerate(b["nodes"]) if nd["rows"]]
                nd = b["nodes"][cand[int(rng.integers(0, len(cand)))]]
                del nd["rows"][int(rng.integers(0, len(nd["rows"])))]
            add(kind, "a", c["key"], clo, c["format"], b, c["key"])
            # (b) one k changed
            b = json.loads(json.dumps(body))
            if c["format"] == "flat-v1":
                i = int(rng.integers(0, len(b["C"])))
                b["C"][i][1] = (b["C"][i][1] + 1 + int(rng.integers(0, C.NEQ - 1))) % C.NEQ
            else:
                cand = [i for i, nd in enumerate(b["nodes"]) if nd["rows"]]
                nd = b["nodes"][cand[int(rng.integers(0, len(cand)))]]
                i = int(rng.integers(0, len(nd["rows"])))
                nd["rows"][i][1] = (nd["rows"][i][1] + 1 + int(rng.integers(0, C.NEQ - 1))) % C.NEQ
            add(kind, "b", c["key"], clo, c["format"], b, c["key"])
            # (c) degree violation
            if clo == "W_4":
                E = C.E_from_hex(byk[c["key"]]["E_hex"])
                quad = [j for j in np.flatnonzero(E.any(axis=0)) if len(C.EQ_MONS[j]) == 2]
                k0 = int(np.flatnonzero(E[:, quad[0]])[0]) if quad else 0
                m0 = C.EQ_MONS[quad[0]] if quad else ()
                free = [v for v in range(C.NV) if v not in m0]
                mu = sorted(int(v) for v in rng.choice(free, size=2, replace=False))
                b = json.loads(json.dumps(body))
                for nd in b["nodes"]:
                    nd["id"] += 1
                    nd["prods"] = [[j, cc + 1] for j, cc in nd["prods"]]
                b["nodes"].insert(0, {"id": 0, "rows": [[mu, k0]], "prods": []})
                b["output"] += 1
                j = int(rng.integers(0, C.NV))
                b["nodes"][b["output"]]["prods"] += [[j, 0], [j, 0]]
                add(kind, "c", c["key"], clo, "wdag-v1", b, c["key"])
            else:
                src = w4flat.get(arm, [])
                if src:
                    s = src[t % len(src)]
                    add(kind, "c", s["key"], "M_4", "flat-v1", s["body"], s["key"])
                else:
                    plan[kind]["types"]["c"] = "vacuous: no verified max|mu| = 3 flat certificate in this arm"
            # (d) re-keyed
            others = sorted(set(x["key"] for x in cs) - {c["key"]})
            if not others:
                others = [r["key"] for r in inst if r["arm"] == arm and r["key"] != c["key"]]
            if others:
                ok = others[t % len(others)]
                add(kind, "d", ok, clo, c["format"], body, c["key"])
        for typ in "abcd":
            plan[kind]["types"].setdefault(typ, sum(1 for x in recs if x["kind"] == kind and x["type"] == typ))
    # ann kinds
    by_arm = {}
    for a in anns:
        by_arm.setdefault(a["key"].split(":")[0], []).append(a)
    mainrec = main
    for arm, al in sorted(by_arm.items()):
        kind = f"ann|{arm}"
        plan[kind] = {"base_certificates": len(al), "types": {}}
        e2_src = [a for a in al if mainrec[a["key"]]["W_4"]["final_dim"] != mainrec[a["key"]]["M_4"]["rank"]]
        for t in range(3):
            a = al[t % len(al)]
            Lh = a["body"]["L_hex"]
            E = C.E_from_hex(byk[a["key"]]["E_hex"])
            eqs = C.E_to_eqs(E)
            cl = CL.get_closure(C.NV, 4, C.NEQ)
            M = cl.build_M(eqs)
            nzr = np.flatnonzero(M.any(axis=1))
            rr = int(nzr[int(rng.integers(0, nzr.size))])
            row = M[rr]
            cols = [w * 64 + b for w in range(cl.W) for b in range(64) if (int(row[w]) >> b) & 1 and w * 64 + b < cl.C]
            cc = cols[int(rng.integers(0, len(cols)))]
            add(kind, "e1", a["key"], "W_4", "ann-v1",
                {**a["body"], "L_hex": Lh + [format(1 << cc, "x")]}, a["key"])
            if e2_src:
                a2 = e2_src[t % len(e2_src)]
                E2 = C.E_from_hex(byk[a2["key"]]["E_hex"])
                M2 = cl.build_M(C.E_to_eqs(E2))
                log = CL.kernels.column_pass(M2, cl.C, keep_ops=False)
                L2 = CL.annihilator(M2[log.ps], log.cs, cl.C)
                add(kind, "e2", a2["key"], "W_4", "ann-v1", {**a2["body"], "L_hex": L2}, a2["key"])
            else:
                plan[kind]["types"]["e2"] = "vacuous: no ann-certified system with W_4 != M_4 in this arm"
            mask = ~(1 << (cl.C - 1))
            add(kind, "e3", a["key"], "W_4", "ann-v1",
                {**a["body"], "L_hex": [format(int(h, 16) & mask, "x") for h in Lh]}, a["key"])
        for typ in ("e1", "e2", "e3"):
            plan[kind]["types"].setdefault(typ, sum(1 for x in recs if x["kind"] == kind and x["type"] == typ))
    return {"records": recs, "plan": plan}


# =============================================================================
# phase 5 (in-process): C-LIT
# =============================================================================
def phase5_lit(R):
    from literal import Literal
    inst = load_instances(R)
    main = {o["key"]: o for o in C.read_jsonl_gz(R.out / "closures.jsonl.gz")}
    sel = lit_backend_selection(inst, main, R.Q["lit_first"], R.Q["lit_nonref"])
    lit = Literal(C.NV, 4, C.NEQ)
    rows = []
    with R.timer("phase5:C-LIT"):
        for k in sel:
            r = next(x for x in inst if x["key"] == k)
            t = time.time()
            lr = lit.w_closure(C.E_to_eqs(C.E_from_hex(r["E_hex"])))
            w = main[k]["W_4"]
            diff = [f for f in ("final_dim", "one", "iterations_to_fixpoint", "dims_by_deg", "dims",
                                "one_first_iteration") if lr[f] != w[f]]
            rows.append({"key": k, "literal": lr, "differences": diff, "seconds_measured": round(time.time() - t, 1)})
    C.write_json(R.out / "literal-check.json", {
        "rule": "own numpy literal W_4 (all products of a basis of W^(i) cap B_{<=3}); imports nothing from the package",
        "selection": "first 5 unsatisfiable systems of S3-U400, N-CONV19, N-ELL19, N-F219, N-AFF19 and of each "
                     "F-RANDX19 stratum, plus up to 20 S3-U400 systems W_4 does not refute",
        "systems": len(rows), "results": rows, "pass": all(not r["differences"] for r in rows) and bool(rows)})
    R.mark("phase5-lit", {"n": len(rows), "utc": C.utc_now()})


def lit_backend_selection(inst, main, first, nonref_n):
    sel = []
    groups = [("S3-U400", None), ("N-CONV19", None), ("N-ELL19", None), ("N-F219", None), ("N-AFF19", None),
              ("F-RANDX19", "X2E"), ("F-RANDX19", "XE-NOT-2E"), ("F-RANDX19", "TWIST")]
    for arm, st in groups:
        ks = [r["key"] for r in inst if r["arm"] == arm and r["role"] == "unsat" and (st is None or r.get("stratum") == st)
              and "W_4" in main.get(r["key"], {})]
        sel += ks[:first]
    nr = [r["key"] for r in inst if r["arm"] == "S3-U400" and "W_4" in main.get(r["key"], {})
          and not main[r["key"]]["W_4"]["one"]]
    for k in nr[:nonref_n]:
        if k not in sel:
            sel.append(k)
    return sel


# =============================================================================
# separate-process phases: determinism (C-DET) and backend (C-BACKEND)
# =============================================================================
def phase_determinism(R):
    out = {"started_utc": C.utc_now(), "process": "separate (--phase determinism)", "pid": os.getpid()}
    p2 = R.load("phase2")
    # (a) regenerate every stream in memory and compare draw-log hashes
    ctx, Q = R.ctx, R.Q
    t = time.time()
    pr = AR.s3_primary(ctx, R.seeds["S3-PRIMARY"], Q["u400"], Q["sat100"], Q["cap_primary"])
    got = {"S3-PRIMARY": hashlib.sha256(C.jsonl_gz_bytes(pr["draws"])).hexdigest()}
    cv = AR.n_conv19(ctx, R.seeds["N-CONV19"], pr["U400"][:Q["conv_slots"]], Q["conv_sat_slots"], Q["per_slot"])
    got["N-CONV19"] = hashlib.sha256(C.jsonl_gz_bytes(cv["draws"])).hexdigest()
    ne = AR.stream_arm(ctx, "N-ELL19", R.seeds["N-ELL19"], True, Q["stream_u"], Q["stream_s"], Q["stream_cap"])
    got["N-ELL19"] = hashlib.sha256(C.jsonl_gz_bytes(ne["draws"])).hexdigest()
    nf = AR.stream_arm(ctx, "N-F219", R.seeds["N-F219"], False, Q["stream_u"], Q["stream_s"], Q["stream_cap"])
    got["N-F219"] = hashlib.sha256(C.jsonl_gz_bytes(nf["draws"])).hexdigest()
    na = AR.n_aff19(ctx, R.seeds["N-AFF19"], pr["classified"], Q["aff_fam"], Q["aff_u"], Q["aff_s"])
    got["N-AFF19"] = hashlib.sha256(C.jsonl_gz_bytes(na["draws"])).hexdigest()
    rx = AR.f_randx19(ctx, R.seeds["F-RANDX19"], pr["all_x"], Q["randx_quota"], Q["randx_cap"])
    got["F-RANDX19"] = hashlib.sha256(C.jsonl_gz_bytes(rx["draws"])).hexdigest()
    inst2 = pr["U400"] + pr["SAT100"] + cv["kept"] + ne["kept"] + nf["kept"] + na["kept"] + rx["kept"]
    on_disk = {a: C.sha256_file(R.out / f) for a, f in DRAW_FILES.items()}
    out["a"] = {"regenerated_sha256": got, "on_disk_sha256": on_disk, "phase2_recorded": p2["draws_sha256"],
                "instances_sha256_regenerated": hashlib.sha256(C.jsonl_gz_bytes(inst2)).hexdigest(),
                "instances_sha256_on_disk": C.sha256_file(R.out / "instances.jsonl.gz"),
                "seconds_measured": round(time.time() - t, 1)}
    out["a"]["pass"] = got == on_disk and out["a"]["instances_sha256_regenerated"] == out["a"]["instances_sha256_on_disk"]
    # (b) recompute M_4, W_4 and rc_b
    inst = load_instances(R)
    main = {o["key"]: o for o in C.read_jsonl_gz(R.out / "closures.jsonl.gz")}
    sel = ([r["key"] for r in inst if r["arm"] == "S3-U400"][:10] + [r["key"] for r in inst if r["arm"] == "S3-SAT100"][:5]
           + [r["key"] for r in inst if r["arm"] == "N-CONV19"][:5])
    byk = {r["key"]: r for r in inst}

    def rec_of(k):
        r = byk[k]
        E = C.E_from_hex(r["E_hex"])
        eqs = C.E_to_eqs(E)
        r4, _ = CL.macaulay(C.NV, 4, C.NEQ, eqs, want_cert=False)
        w, *_ = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=False)
        info, _ = RB.rc_b(E, r["arm"], R.F, r.get("x_R"), R.ctx.ell_lin)
        return {"M_4": r4, "W_4": w, "rc_b": info}

    t = time.time()
    bres = CL.kernels.map_threads(rec_of, sel, R.threads)
    bdiff = [k for k, o in zip(sel, bres) if o["M_4"] != main[k]["M_4"] or o["W_4"] != main[k]["W_4"]
             or o["rc_b"] != main[k]["rc_b"]]
    out["b"] = {"systems": sel, "differences": bdiff, "threads": R.threads, "pass": not bdiff,
                "seconds_measured": round(time.time() - t, 1)}
    # (c) 20 systems with one thread
    sel_c = []
    for arm in ("N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"):
        sel_c += [r["key"] for r in inst if r["arm"] == arm and r["role"] == "unsat"][:4]
    t = time.time()
    cres = CL.kernels.map_threads(rec_of, sel_c, 1)
    cdiff = [k for k, o in zip(sel_c, cres) if o["M_4"] != main[k]["M_4"] or o["W_4"] != main[k]["W_4"]]
    out["c"] = {"systems": sel_c, "threads": 1, "compared_with": f"phase-4 records ({R.threads} threads)",
                "differences": cdiff, "pass": not cdiff, "seconds_measured": round(time.time() - t, 1)}
    out["pass"] = out["a"]["pass"] and out["b"]["pass"] and out["c"]["pass"]
    out["finished_utc"] = C.utc_now()
    out["peak_rss_mib_measured"] = round(C.peak_rss_mib(), 1)
    C.write_json(R.out / "determinism.json", out)
    print("C-DET", "PASS" if out["pass"] else "FAIL", flush=True)


def phase_backend(R):
    from crypto_autoresearcher.gf2 import _native, kernels
    be = kernels.backend()
    out = {"started_utc": C.utc_now(), "process": "separate (--phase backend)", "backend": be,
           "build_info": dict(_native.build_info), "CRYPTO_AR_GF2_BACKEND": os.environ.get("CRYPTO_AR_GF2_BACKEND")}
    if be != "reference":
        out["pass"] = False
        out["error"] = "backend is not reference"
        C.write_json(R.out / "backend-check.json", out)
        return
    inst = load_instances(R)
    main = {o["key"]: o for o in C.read_jsonl_gz(R.out / "closures.jsonl.gz")}
    sel = lit_backend_selection(inst, main, R.Q["backend_first"], R.Q["backend_nonref"])
    byk = {r["key"]: r for r in inst}
    rows = []
    t0 = time.time()
    for k in sel:
        t = time.time()
        eqs = C.E_to_eqs(C.E_from_hex(byk[k]["E_hex"]))
        r4, _ = CL.macaulay(C.NV, 4, C.NEQ, eqs, want_cert=False)
        w, *_ = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=False)
        diff = [f for f in r4 if r4[f] != main[k]["M_4"].get(f)] + [f"W_4.{f}" for f in w if w[f] != main[k]["W_4"].get(f)]
        rows.append({"key": k, "differences": diff, "seconds_measured": round(time.time() - t, 1)})
    out["selection"] = ("first 10 unsatisfiable systems of S3-U400, N-CONV19, N-ELL19, N-F219, N-AFF19 and of each "
                        "F-RANDX19 stratum, plus up to 10 S3-U400 systems W_4 does not refute")
    out["systems"] = len(rows)
    out["results"] = rows
    out["pass"] = bool(rows) and all(not r["differences"] for r in rows)
    out["seconds_measured"] = round(time.time() - t0, 1)
    out["finished_utc"] = C.utc_now()
    out["peak_rss_mib_measured"] = round(C.peak_rss_mib(), 1)
    C.write_json(R.out / "backend-check.json", out)
    print("C-BACKEND", "PASS" if out["pass"] else "FAIL", flush=True)


# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--phase", choices=["determinism", "backend"], default=None)
    ap.add_argument("--dev-quotas", default=None, help="development only (refused inside runs/)")
    ap.add_argument("--dev-seeds", default=None, help="development only (refused inside runs/)")
    args = ap.parse_args()
    R = Run(args)
    if args.phase == "determinism":
        return phase_determinism(R)
    if args.phase == "backend":
        return phase_backend(R)
    if not args.resume and R.done("phase0"):
        raise SystemExit("run directory already has phase 0; use --resume")
    C.log(f"driver start run {args.run_id} threads {R.threads} dev {R.dev}")
    try:
        if not R.done("phase0"):
            phase0(R)
        R.append_timing()
        if not R.done("phase1"):
            phase1(R)
        R.append_timing()
        if not R.done("phase2"):
            phase2(R)
        R.append_timing()
        if not R.done("phase3"):
            phase3(R)
        R.append_timing()
        if not R.done("phase4-main"):
            phase4(R)
        R.append_timing()
        if not R.done("phase4-post"):
            phase4_post(R)
        R.append_timing()
        if not R.done("phase4"):
            with R.timer("phase4:assemble+negative-controls"):
                phase4_write(R)
        R.append_timing()
        if not R.done("phase5-lit"):
            phase5_lit(R)
        R.append_timing()
    finally:
        R.append_timing()
    missing = [f for f in ("determinism.json", "backend-check.json", "certificate-verification.json",
                           "annihilator-verification.json", "construction-verification.json",
                           "draw-replay-verification.json", "negative-controls-verification.json")
               if not (R.out / f).exists()]
    if missing:
        C.log(f"phases 0-4 and C-LIT complete; awaiting separate-process phases: {missing}")
        return 0
    import analysis
    with R.timer("phase7:aggregation"):
        analysis.phase7(R)
    R.append_timing()
    C.log("phase 7 complete")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
