"""TASK-20260926-83cebf blind re-derivation driver (J7).

Computes Q0 (N-CONV stream replay, plus Q0-opt prefixes), Q1 (M_4 on the kept
systems of the replay), Q2-Q5 (pool systems) and wdag-v1 certificates, from the
three specifications and blind-inputs.json alone. Imports no module of the
repository; numpy only.

usage: python3 driver.py --inputs BLIND_INPUTS --out TASKDIR --ckpt CKPTDIR [--resume]
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import br_field as F                # noqa: E402
import br_system as S               # noqa: E402
import br_macaulay as MC            # noqa: E402
import br_linalg as LA              # noqa: E402
import br_closure as CL             # noqa: E402
import br_sat as SAT                # noqa: E402
import br_rcb as RCB                # noqa: E402
import br_draws as DR               # noqa: E402
import br_wdag_check as WC          # noqa: E402
import br_selftest as ST            # noqa: E402
from br_ambiguities import AMBIGUITIES   # noqa: E402

A_CURVE = None
B_CURVE = None


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print("[%s] %s" % (now(), msg), flush=True)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def peak_rss_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def jdump(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, sort_keys=True)
    os.replace(tmp, path)


def jload(path):
    with open(path) as f:
        return json.load(f)


def E_hexkey(E):
    return ",".join(S.row_hex(E))


# ----------------------------------------------------------------------------
class Ctx:
    def __init__(self, args):
        self.args = args
        self.inputs = jload(args.inputs)
        global A_CURVE, B_CURVE
        A_CURVE = int(self.inputs["curve"]["A"])
        B_CURVE = int(self.inputs["curve"]["B"])
        self.A, self.B = A_CURVE, B_CURVE
        self.slots = [(int(s["slot"]), int(s["x_R"])) for s in self.inputs["slots"]]
        assert [s for s, _ in self.slots] == list(range(len(self.slots)))
        self.slot_xr = [x for _, x in self.slots]
        self.ckpt = args.ckpt
        os.makedirs(self.ckpt, exist_ok=True)
        self.sp3 = MC.Space(18, 3, 17)
        self.sp4 = MC.Space(18, 4, 17)
        self.sp3_17 = MC.Space(17, 3, 17)
        self.sp4_17 = MC.Space(17, 4, 17)
        self.timings = {}

    def cp(self, *parts):
        p = os.path.join(self.ckpt, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p


# ----------------------------------------------------------------------------
def phase_selftest(ctx):
    p = ctx.cp("selftest.json")
    if ctx.args.resume and os.path.exists(p):
        r = jload(p)
        if r.get("all_pass"):
            log("selftest: resumed from checkpoint (all pass)")
            return r
    t = time.time()
    r = ST.run_all(ctx.A, ctx.B)
    ctx.timings["selftest_s"] = round(time.time() - t, 1)
    jdump(r, p)
    return r


def phase_construction(ctx):
    t = time.time()
    U = S.union_support(ctx.B)
    SL = S.S_L_positions(U)
    sizes = [int(x) for x in U.sum(axis=1)]
    # Coordinator reading (EXP-CERTBIN-ddfe75 object.union_support): U_k
    # contains all 81 bilinear and all 18 linear columns, plus the constant iff
    # bit k of B is 1; |S_L| = 17*18 + popcount(B). Recorded true/false.
    reading = True
    for k in range(17):
        cols = set(np.flatnonzero(U[k]).tolist())
        want = set(S.BILINEAR_COLS) | set(S.LIN_COLS) | ({0} if (ctx.B >> k) & 1 else set())
        if cols != want:
            reading = False
    ES3 = {slot: S.E_S3(xr, ctx.B) for slot, xr in ctx.slots}
    # every E_S3(x_R) at the slots lies inside U; only bilinear/linear/constant
    inside = all(not (E.astype(bool) & ~U).any() for E in ES3.values())
    nonbil = [c for c in S.QUAD_COLS if c not in S.BILINEAR_COLS]
    parts_ok = all(not E[:, nonbil].any() for E in ES3.values())
    ctx.U, ctx.SL, ctx.ES3 = U, SL, ES3
    ctx.timings["construction_s"] = round(time.time() - t, 1)
    return {
        "U_sizes_per_equation": sizes,
        "U_total": int(U.sum()),
        "U_rows_hex": S.row_hex(U.astype(np.uint8)),
        "S_L_size": len(SL),
        "S_L_positions_row_major": [[k, c] for k, c in SL],
        "S_L_constant_positions": [k for k, c in SL if c == 0],
        "coordinator_reading_of_U_k_holds": reading,
        "expected_S_L_size_under_reading": 17 * 18 + bin(ctx.B).count("1"),
        "E_S3_at_all_144_slots_inside_U": bool(inside),
        "E_S3_at_all_144_slots_only_bilinear_linear_constant": bool(parts_ok),
    }


# ----------------------------------------------------------------------------
def phase_q0(ctx, arm, slots):
    """Replay one arm over the given slots (a prefix, in order). Checkpoint per
    slot with the generator state."""
    rep = DR.ArmReplay(arm, ctx.B, ctx.U, ctx.SL, ctx.slot_xr)
    per_slot = {}
    attempts_all = []
    kept = {}
    t = time.time()
    for slot in slots:
        p = ctx.cp("q0", arm, "slot-%03d.json" % slot)
        if ctx.args.resume and os.path.exists(p):
            ck = jload(p)
            rep.g.bit_generator.state = ck["gen_state_after"]
            for key, (s_, role) in ck["kept_keys"].items():
                rep.kept_keys[key] = (s_, role)
            per_slot[slot] = ck["summary"]
            attempts_all.extend(ck["attempts"])
            for role, kr in ck["kept"].items():
                kept[(slot, role)] = kr
            continue
        attempts, roles, exhausted = rep.run_slot(slot)
        summ = {
            "x_R": ctx.slot_xr[slot] if arm in ("N-CONV", "N-CONVL") else None,
            "attempts": len(attempts),
            "outcomes": {o: sum(1 for a in attempts if a["outcome"] == o)
                         for o in ("kept_unsat", "kept_sat", "discarded", "rejected")},
            "rejections": [{"attempt": a["attempt"], "reason": a["reject_reason"]}
                           for a in attempts if a["outcome"] == "rejected"],
            "exhausted": exhausted,
        }
        kr_all = {}
        for role in ("unsat", "sat"):
            r = roles[role]
            if r is None:
                summ[role] = "EXHAUSTED(cap)"
                continue
            summ[role] = {"attempt": r["attempt"], "s": r["s"], "row_hex": S.row_hex(r["E"])}
            if role == "sat":
                summ[role]["solutions"] = r["solutions"]
            kr_all[role] = {"attempt": r["attempt"], "s": r["s"], "row_hex": S.row_hex(r["E"])}
            if role == "sat":
                kr_all[role]["solutions"] = r["solutions"]
            kept[(slot, role)] = kr_all[role]
        per_slot[slot] = summ
        attempts_all.extend(attempts)
        jdump({"summary": summ, "attempts": attempts, "kept": kr_all,
               "kept_keys": {k: list(v) for k, v in rep.kept_keys.items()},
               "gen_state_after": rep.g.bit_generator.state}, p)
        if slot % 24 == 0:
            log("q0 %s slot %d done (%d attempts so far)" % (arm, slot, len(attempts_all)))
    ctx.timings["q0_%s_s" % arm] = round(time.time() - t, 1)
    return per_slot, attempts_all, kept


def E_from_hex(row_hex):
    E = np.zeros((17, S.NCOL_E), dtype=np.uint8)
    for k, h in enumerate(row_hex):
        x = int(h, 16)
        j = 0
        while x:
            if x & 1:
                E[k, j] = 1
            x >>= 1
            j += 1
    return E


# ----------------------------------------------------------------------------
def closure_record(ctx, E, want_W, want_M3, want_witness=True, solutions=None):
    """M_4 (and M_3), optionally W_4, and a wdag-v1 witness when refuted.
    For satisfiable systems (solutions given), soundness instruments: every
    M_4 row and every W_4 basis row vanishes at every solution, and
    codim(W_4) >= s."""
    rec = {}
    t = time.time()
    M4 = ctx.sp4.build(E)
    st4 = CL.macaulay_stats(ctx.sp4, M4)
    assert st4["P"] == st4["P_direct"], "P routes disagree"
    rec["rank_4"] = st4["rank"]
    rec["one_in_R_4"] = st4["one"]
    rec["dims_by_deg_M4"] = st4["dims_by_deg"][:4]         # d = 0..3
    rec["P"] = st4["P"]
    rec["P_second_route_rank_of_degree4_columns"] = st4["P_direct"]
    if want_M3:
        st3 = CL.macaulay_stats(ctx.sp3, ctx.sp3.build(E))
        rec["rank_3"] = st3["rank"]
        rec["one_in_R_3"] = st3["one"]
    cert = None
    wc = None
    if want_W:
        wc = CL.WClosure(ctx.sp4, M4)
        w = wc.run()
        rec["W4"] = {
            "dims": w["dims"],
            "fixpoint_index": w["fixpoint_index"],
            "one_first_iteration": w["one_first_iteration"],
            "final_dim": w["final_dim"],
            "one": w["one"],
            "dims_by_deg": w["dims_by_deg"],
            "fallen_basis_size_per_iteration": w["fallen_basis_size_per_iteration"],
        }
        refuted = w["one"]
    else:
        refuted = st4["one"]
    if solutions:
        rec["soundness"] = {"M4_rows_vanish_at_all_solutions": CL.vanishes_at(ctx.sp4, M4, solutions)}
        if want_W:
            rec["soundness"]["W4_basis_vanishes_at_all_solutions"] = CL.vanishes_at(ctx.sp4, wc.final_rows, solutions)
            rec["soundness"]["codim_W4"] = ctx.sp4.ncols - rec["W4"]["final_dim"]
            rec["soundness"]["codim_W4_ge_s"] = (ctx.sp4.ncols - rec["W4"]["final_dim"]) >= len(solutions)
    if refuted and want_witness:
        try:
            l0 = CL.LevelZeroSolver(ctx.sp4, M4)
            if wc is not None:
                cert = wc.witness(l0)
            else:
                # M_4 refutation: a one-node wdag with rows only (BR-6)
                ridx = l0.express(ctx.sp4.one_row())
                cert = {"D": 4, "nv": 18, "output": 0,
                        "nodes": [{"id": 0, "rows": [[list(ctx.sp4.mus[r // 17]), r % 17] for r in ridx],
                                   "prods": []}]}
        except Exception as e:           # reported as refuted, unwitnessed
            rec["witness_error"] = repr(e)
            cert = None
    rec["seconds"] = round(time.time() - t, 2)
    return rec, cert


def phase_q1(ctx, kept, roles=("unsat", "sat")):
    out = {}
    certs = {}
    t = time.time()
    for role in roles:
        for slot in range(len(ctx.slots)):
            key = "NCONV-REPLAY:%d:%s" % (slot, role)
            if (slot, role) not in kept:
                out[key] = {"missing": "EXHAUSTED(cap): no kept system"}
                continue
            p = ctx.cp("q1", "%s.json" % key.replace(":", "_"))
            if ctx.args.resume and os.path.exists(p):
                ck = jload(p)
                out[key] = ck["rec"]
                if ck.get("cert"):
                    certs[key] = ck["cert"]
                continue
            E = E_from_hex(kept[(slot, role)]["row_hex"])
            try:
                rec, cert = closure_record(ctx, E, want_W=False, want_M3=False,
                                           solutions=kept[(slot, role)].get("solutions"))
            except Exception as e:      # infrastructure/implementation failure: reported, not a result
                out[key] = {"missing": "exception: %r" % (e,), "traceback": traceback.format_exc()}
                log("q1 %s FAILED: %r" % (key, e))
                continue
            rec["s"] = kept[(slot, role)]["s"]
            out[key] = rec
            if cert is not None:
                certs[key] = cert
            jdump({"rec": rec, "cert": cert}, p)
        log("q1 role %s done" % role)
    ctx.timings["q1_s"] = round(time.time() - t, 1)
    return out, certs


# ----------------------------------------------------------------------------
def identify(ctx, E):
    """Structural identification of a pool system against my own constructions."""
    info = {}
    info["within_U"] = bool(not (E.astype(bool) & ~ctx.U).any())
    exact = [s for s, e in ctx.ES3.items() if np.array_equal(E, e)]
    info["equals_E_S3_at_slots"] = exact
    quad = [s for s, e in ctx.ES3.items() if np.array_equal(E[:, S.QUAD_COLS], e[:, S.QUAD_COLS])]
    info["quadratic_part_equals_Qpart_at_slots"] = quad
    info["quadratic_and_linear_parts_equal_E_S3_at_slots"] = [
        s for s in quad if np.array_equal(E[:, S.LIN_COLS], ctx.ES3[s][:, S.LIN_COLS])]
    Q17 = S.conv17_quadratic()
    info["quadratic_part_is_conv17_Q_k"] = bool(np.array_equal(E[:, S.QUAD_COLS], Q17[:, S.QUAD_COLS]))
    r16 = np.zeros(S.NCOL_E, dtype=np.uint8)
    r16[S.E_COL[1 << 0]] = 1
    r16[S.E_COL[1 << 9]] = 1
    info["row16_is_v0_plus_v9_plus_c"] = bool(np.array_equal(E[16, 1:], r16[1:]))
    return info


def phase_pool(ctx):
    out = {}
    certs = {}
    t0 = time.time()
    for sysrec in ctx.inputs["systems"]:
        label = sysrec["label"]
        p = ctx.cp("pool", "%s.json" % label)
        if ctx.args.resume and os.path.exists(p):
            ck = jload(p)
            out[label] = ck["rec"]
            if ck.get("cert"):
                certs[label] = ck["cert"]
            continue
        t = time.time()
        try:
            rec, cert, s = pool_one(ctx, sysrec)
        except Exception as e:          # infrastructure/implementation failure: reported, not a result
            out[label] = {"missing": "exception: %r" % (e,), "traceback": traceback.format_exc()}
            log("pool %s FAILED: %r" % (label, e))
            continue
        rec["seconds_total"] = round(time.time() - t, 2)
        out[label] = rec
        if cert is not None:
            certs[label] = cert
        jdump({"rec": rec, "cert": cert}, p)
        log("pool %s: s=%d t=%.1fs" % (label, s, time.time() - t))
    ctx.timings["pool_s"] = round(time.time() - t0, 1)
    return out, certs


def pool_one(ctx, sysrec):
    if True:
        E = S.E_from_equations(sysrec["equations"])
        rec = {"identification": identify(ctx, E)}
        s, sols = SAT.count_s(E, want_solutions=True)
        rec["s"] = s
        if s:
            rec["solutions"] = sols if s <= 64 else None
        routes = {"exhaustive_2^18": s}
        ide = rec["identification"]
        if ide["equals_E_S3_at_slots"]:
            for slot in ide["equals_E_S3_at_slots"]:
                xr = ctx.slot_xr[slot]
                routes["oracle_A_root_finding_slot_%d" % slot] = SAT.oracle_A(xr, ctx.B)
                routes["direct_S3_over_VxV_slot_%d" % slot] = SAT.direct_count_VxV(xr, ctx.B)
        # supplementary (not required by BR-4): S_3 descent with another curve
        # constant b' (quadratic and linear parts equal E_S3 at a slot)
        supp = []
        for slot in ide["quadratic_and_linear_parts_equal_E_S3_at_slots"]:
            if slot in ide["equals_E_S3_at_slots"]:
                continue
            bprime = 0
            for k in range(17):
                if E[k, 0]:
                    bprime |= 1 << k
            supp.append({"slot": slot, "b_prime": bprime,
                         "oracle_A_with_b_prime": SAT.oracle_A(ctx.slot_xr[slot], bprime)})
        rec["s_routes"] = routes
        if supp:
            rec["s_supplementary_routes_other_constant"] = supp
        vals = set(routes.values()) | set(x["oracle_A_with_b_prime"] for x in supp)
        rec["s_routes_agree"] = (len(vals) == 1)
        # Q2 / Q3 / Q4
        crec, cert = closure_record(ctx, E, want_W=True, want_M3=True, solutions=sols if s else None)
        rec.update(crec)
        # Q5
        rc = RCB.rc_b(E, ctx.sp3_17, ctx.sp4_17)
        rc.pop("_Ep", None)
        if rc.get("label") == "SUBSTITUTED":
            rc["T5_applicable"] = (rc["dims_by_deg_R4"][3] == rc["rank_R3"])
            rc["derived_final_dim_W4_minus_rank_R4"] = rec["W4"]["final_dim"] - rc["rank_R4"]
            rc["derived_W4_one_equals_one_in_R4"] = (rec["W4"]["one"] == rc["one_in_R4"])
        rec["rc_b"] = rc
        return rec, cert, s


# ----------------------------------------------------------------------------
def check_certificates(ctx, wcerts_path, replay_kept):
    """Re-read wcerts.jsonl.gz and check every record with the independent
    checker, with f_k rebuilt from the pool's own monomial lists or from the
    replay log's row hex (no E from the elimination engine)."""
    pool = {s["label"]: s["equations"] for s in ctx.inputs["systems"]}
    results = {}
    t = time.time()
    with gzip.open(wcerts_path, "rt") as f:
        for line in f:
            rec = json.loads(line)
            key = rec["label_or_replay_key"]
            if key in pool:
                eqs = pool[key]
            else:
                _, slot, role = key.split(":")
                row_hex = replay_kept[(int(slot), role)]["row_hex"]
                eqs = []
                for h in row_hex:
                    x = int(h, 16)
                    eq = []
                    j = 0
                    while x:
                        if x & 1:
                            eq.append(list(S.E_MONOS[j]))
                        x >>= 1
                        j += 1
                    eqs.append(eq)
            res = WC.Checker(eqs, D=4, nv=18, neq=17).check(rec)
            results[key] = res
    ctx.timings["certificate_check_s"] = round(time.time() - t, 1)
    return results


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    t_start = time.time()
    started = now()
    ctx = Ctx(args)
    log("start; numpy %s; python %s" % (np.__version__, platform.python_version()))
    env = {
        "numpy_version": np.__version__,
        "numpy_version_is_2.4.6": np.__version__ == "2.4.6",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
        "rlimit_as_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
        "argv": sys.argv,
        "started_utc": started,
        "resume": bool(args.resume),
    }
    try:
        env["git_head_readonly"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True,
                                                  text=True).stdout.strip()
    except Exception:
        env["git_head_readonly"] = None
    code_hashes = {fn: sha256_file(os.path.join(HERE, fn)) for fn in sorted(os.listdir(HERE)) if fn.endswith(".py")}

    st = phase_selftest(ctx)
    if not st["all_pass"]:
        log("SELF-TEST FAILURE: stopping (BR-2)")
        jdump({"schema": "certbin.nconv.rederivation.v1", "self_tests": st, "stopped": "self-test failure"},
              ctx.cp("STOPPED.json"))
        sys.exit(2)
    log("self-tests pass")
    construction = phase_construction(ctx)
    log("construction: |S_L| = %d" % construction["S_L_size"])

    # Q0 and Q0-opt
    q0_slots, q0_attempts, q0_kept = phase_q0(ctx, "N-CONV", list(range(len(ctx.slots))))
    log("Q0 N-CONV done: %d attempts" % len(q0_attempts))
    q0opt = {}
    q0opt_attempts = []
    for arm in ("N-CONVL", "N-CONV17", "N-ELL144"):
        ps, at, _ = phase_q0(ctx, arm, list(range(10)))
        q0opt[arm] = {"seed": DR.ARM_SEEDS[arm], "slots": {str(k): v for k, v in ps.items()}}
        q0opt_attempts.extend(at)
    log("Q0-opt done")

    # Q1 (unsat required; sat optional)
    q1, q1_certs = phase_q1(ctx, q0_kept)
    log("Q1 done")

    # Q2-Q5
    pool, pool_certs = phase_pool(ctx)
    log("pool done")

    out_dir = args.out
    # --- sealed file 2: stream-replay.jsonl.gz
    sr_path = os.path.join(out_dir, "stream-replay.jsonl.gz")
    with gzip.open(sr_path + ".tmp", "wt") as f:
        for a in q0_attempts + q0opt_attempts:
            f.write(json.dumps(a, sort_keys=True) + "\n")
    os.replace(sr_path + ".tmp", sr_path)
    # --- sealed file 3: wcerts.jsonl.gz (one record per refuted system)
    wc_path = os.path.join(out_dir, "wcerts.jsonl.gz")
    order = [k for k in q1 if k in q1_certs] + [k for k in pool if k in pool_certs]
    allcerts = dict(q1_certs)
    allcerts.update(pool_certs)
    with gzip.open(wc_path + ".tmp", "wt") as f:
        for key in order:
            c = allcerts[key]
            f.write(json.dumps({"label_or_replay_key": key, "D": c["D"], "nv": c["nv"],
                                "nodes": c["nodes"], "output": c["output"]}, sort_keys=True) + "\n")
    os.replace(wc_path + ".tmp", wc_path)
    log("wrote stream-replay and wcerts")
    checks = check_certificates(ctx, wc_path, q0_kept)
    log("certificates checked: %d, valid %d" % (len(checks), sum(1 for r in checks.values() if r["valid"])))

    # refuted, unwitnessed
    unwitnessed = []
    for key, r in q1.items():
        if r.get("one_in_R_4") and key not in q1_certs:
            unwitnessed.append(key)
    for key, r in pool.items():
        if (r.get("W4") or {}).get("one") and key not in pool_certs:
            unwitnessed.append(key)

    # attach check results
    for key in q1:
        if key in checks:
            q1[key]["wdag_check"] = {k: checks[key][k] for k in ("valid", "failed_rules", "node_count", "row_count",
                                                               "max_mu", "max_child_degree")}
    for key in pool:
        if key in checks:
            pool[key]["wdag_check"] = {k: checks[key][k] for k in ("valid", "failed_rules", "node_count",
                                                                 "row_count", "max_mu", "max_child_degree")}

    q1_unsat = {k: v for k, v in q1.items() if k.endswith(":unsat")}
    q1_sat = {k: v for k, v in q1.items() if k.endswith(":sat")}

    def pick(rec, keys):
        return {k: rec.get(k) for k in keys}

    missing_items = []
    for key, r in list(q1.items()) + list(pool.items()):
        if "missing" in r:
            missing_items.append({"item": key, "reason": r["missing"]})
    for slot, v in q0_slots.items():
        for role in v["exhausted"]:
            missing_items.append({"item": "NCONV-REPLAY:%d:%s" % (slot, role), "reason": "EXHAUSTED(cap) in the replay"})
    okpool = {lab: r for lab, r in pool.items() if "missing" not in r}
    Q2 = {lab: pick(r, ["s", "s_routes", "s_supplementary_routes_other_constant", "s_routes_agree", "rank_3",
                        "rank_4", "one_in_R_3", "one_in_R_4", "dims_by_deg_M4", "P",
                        "P_second_route_rank_of_degree4_columns"]) for lab, r in okpool.items()}
    Q3 = {lab: dict(r.get("W4"), soundness_if_satisfiable=r.get("soundness")) for lab, r in okpool.items()}
    # soundness instruments over every satisfiable system computed here
    sat_items = [(k, v) for k, v in q1_sat.items() if "missing" not in v] + \
                [(k, v) for k, v in okpool.items() if v.get("s")]
    soundness_summary = {
        "satisfiable_systems": len(sat_items),
        "refuted_by_M4": sorted(k for k, v in sat_items if v.get("one_in_R_4")),
        "refuted_by_W4": sorted(k for k, v in sat_items if v.get("W4", {}).get("one")),
        "vanishing_failures": sorted(k for k, v in sat_items
                                     if not all(x for x in (v.get("soundness") or {}).values()
                                                if isinstance(x, bool))),
        "note": "every M_4 row and (pool) every W_4 basis row is evaluated at every solution; codim(W_4) >= s",
    }
    Q4 = {lab: {"one_in_W4": r["W4"]["one"],
                "certificate": ("in wcerts.jsonl.gz" if lab in pool_certs else
                                ("refuted, unwitnessed" if r["W4"]["one"] else None)),
                "witness_error": r.get("witness_error"),
                "check": r.get("wdag_check")} for lab, r in okpool.items()}
    Q5 = {lab: r.get("rc_b") for lab, r in okpool.items()}

    red = {
        "schema": "certbin.nconv.rederivation.v1",
        "task_id": "TASK-20260926-83cebf",
        "review_id": ctx.inputs.get("review_id"),
        "joint": "J7",
        "inputs": {
            "blind_inputs_path": args.inputs,
            "blind_inputs_sha256": sha256_file(args.inputs),
            "curve": {"A": ctx.A, "B": ctx.B},
            "field_modulus": "t^17 + t^3 + 1",
        },
        "environment": env,
        "code_sha256": code_hashes,
        "elimination_method": (
            "Bit-packed dense Gauss-Jordan over F_2 (numpy uint64 words, own code br_linalg.rref): columns in "
            "increasing index of the Macaulay column order (descending degrevlex, constant last); pivot = unused "
            "row of smallest index with a 1 in the column; rows never move; the pivot row is XORed into every "
            "other row with a 1 in the column (full=True, RREF) or every other unused row (full=False, echelon). "
            "dims_by_deg(X)[d] = number of echelon rows whose leading monomial has degree <= d (valid for a "
            "degree-descending column order). '1 in X' iff the constant (last) column is a pivot column. "
            "W^(i+1) is computed as W^(i) + span(products): the products are reduced against the RREF of W^(i) "
            "(eight-row lookup tables), the remainder is put in RREF, and the old RREF rows are back-reduced; "
            "the result is the RREF of W^(i+1), whose rows of leading degree <= 3 are the basis multiplied at "
            "the next iteration (full basis every iteration, BR-5). P is computed twice: rank M_4 - "
            "dims_by_deg(M_4)[3], and the rank of the degree-4 column block alone."),
        "self_tests": st,
        "construction": construction,
        "Q0": {
            "arm": "N-CONV", "seed": DR.ARM_SEEDS["N-CONV"],
            "generator": "numpy.random.Generator(numpy.random.PCG64(seed)); one call g.integers(0, 2, size=|S_L|) per attempt",
            "U_S_L": {"S_L_size": construction["S_L_size"], "U_sizes_per_equation": construction["U_sizes_per_equation"]},
            "slots": {str(k): v for k, v in q0_slots.items()},
            "totals": {
                "attempts": len(q0_attempts),
                "kept_unsat": sum(1 for v in q0_slots.values() if isinstance(v.get("unsat"), dict)),
                "kept_sat": sum(1 for v in q0_slots.values() if isinstance(v.get("sat"), dict)),
                "exhausted": {str(k): v["exhausted"] for k, v in q0_slots.items() if v["exhausted"]},
                "rejections": sum(len(v["rejections"]) for v in q0_slots.values()),
                "discarded": sum(v["outcomes"]["discarded"] for v in q0_slots.values()),
            },
        },
        "Q0_opt": q0opt,
        "Q1": {"unsat": q1_unsat, "sat_optional": q1_sat},
        "Q2": Q2,
        "Q3": Q3,
        "Q4": Q4,
        "Q5": Q5,
        "ambiguities": AMBIGUITIES,
        "missing_items": missing_items,
        "missing_items_note": "an empty list means every required item was computed",
        "soundness_summary": soundness_summary,
        "pool_identification": {lab: r["identification"] for lab, r in okpool.items()},
        "pool_solutions": {lab: r.get("solutions") for lab, r in okpool.items() if r["s"]},
        "pool_seconds": {lab: r.get("seconds_total") for lab, r in okpool.items()},
        "certificates": {
            "file": "wcerts.jsonl.gz",
            "records": len(order),
            "checked": len(checks),
            "valid": sum(1 for r in checks.values() if r["valid"]),
            "invalid": sorted(k for k, r in checks.items() if not r["valid"]),
            "refuted_unwitnessed": unwitnessed,
        },
        "timings_seconds": ctx.timings,
        "peak_rss_mb": peak_rss_mb(),
        "wall_seconds": round(time.time() - t_start, 1),
        "finished_utc": now(),
    }
    red_path = os.path.join(out_dir, "rederivation.json")
    with open(red_path + ".tmp", "w") as f:
        json.dump(red, f, sort_keys=True, indent=1)
    os.replace(red_path + ".tmp", red_path)
    log("wrote rederivation.json; wall %.1fs; peak RSS %.1f MB" % (time.time() - t_start, peak_rss_mb()))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(1)
