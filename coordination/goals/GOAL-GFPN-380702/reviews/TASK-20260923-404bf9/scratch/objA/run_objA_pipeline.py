#!/usr/bin/env python3
"""TASK-20260923-404bf9 (red team) -- proves-too-much OBJECT A, pipeline half.

Runs the PRODUCER's m = 4 random-target cell path (experiments/EXP-GFPN-05ff43/
implementation/pdp_cell.py cmd_cell, arm S4, target_kind random) UNCHANGED at a
small prime where decompositions are common, and compares every target with an
exact truth set computed by independent PARI/GP code (truth_S4.gp).

What this harness supplies (and nothing else):
  * the prime p' = 11, c = 2, and curve C2 (EcGFp5-shaped) as a ladder entry
    (pdp_cell.ladder_entry is monkeypatched to return it);
  * the group data: subgroup_prime := #E and cofactor := 1, so that the
    producer's base_point() returns a point of the WHOLE group and its
    targets() draw R = [k]G over <G>.  At p' <= 41 the producer's own
    convention (largest prime factor) leaves 1-2 decomposable x-values in the
    target subgroup (objA_enumeration.txt), which would make "N*f >= 10" ten
    repeats of one system;
  * the S4 arm polynomial.  The producer's build_arm_polynomial() needs
    >= 495 distinct e-points from 4-subsets of a pool of x in F_p with points,
    which does not exist at p' = 11 (pool <= 10).  The polynomial is therefore
    interpolated by this harness from the PRODUCER'S OWN point-free evaluator
    gfpn5_core.S_poly_res at all C(11+3,4) = 1001 multisets of F_11 (exact
    rref solve over F_11, consistency on all 506 surplus rows), and checked
    to vanish at every witness decomposition of the independent truth set;
  * the lock: every msolve subprocess is wrapped in fcntl.flock on the
    dispatcher's solver lock (machine protection); nothing else in the
    decision / lifting / verification logic is touched.
"""
import os, sys, json, time, fcntl, itertools, math, subprocess, argparse, random, tarfile, glob
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
IMPL = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43", "implementation")
LOCK = "/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/gfpn-solver.lock"
os.environ["GFPN_CACHE_DIR"] = os.path.join(HERE, "cache")
os.environ["GFPN_MEM_CAP_GB"] = "11"
os.environ.setdefault("GFPN_MSOLVE_THREADS", "4")
sys.path.insert(0, IMPL)

import flint
import numpy as np
import gfpn5_core, symmetrize, pdp_common, pdp_cell   # producer's code, as committed

P, CMOD, SHAPE = 11, 2, "ecgfp5_shaped"
A2, A4, A6 = [2], [0, 263 % P], [0]
ORDER = 160752          # ellcard, objA_enumeration.txt (independent PARI)
# E(F_q) = Z/80376 x Z/2 (PARI ellgroup) is not cyclic.  The producer's base_point() with
# cofactor 1 returns its first seeded random point P, whose order is 80376 (printed by the
# truth script in the aborted first attempt and re-asserted below).  Using n := ord(P)
# makes k uniform on [1, ord(G)-1], so R = [k]G is uniform on <G> \ {O} and never O.
ORD_G = 80376

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

# ------------------------------------------------------------------ lock wrapper
_orig_run_msolve = symmetrize.run_msolve
def locked_run_msolve(*a, **k):
    with open(LOCK, "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            return _orig_run_msolve(*a, **k)
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
pdp_cell.run_msolve = locked_run_msolve
pdp_common.run_msolve = locked_run_msolve

ENTRY = {"p": P, "p_bits": P.bit_length(), "cmod": CMOD, "field": f"F_{P}[z]/(z^5 - {CMOD})",
         "curves": {SHAPE: {"model": f"y^2 = x(x^2 + 2x + {263 % P}*z)", "a2": A2, "a4": A4, "a6": A6,
                            "has_rational_2torsion": True, "order": ORDER, "cofactor": 1,
                            "subgroup_prime": ORD_G,
                            "note": "harness-supplied (red team): subgroup_prime := ord(G) = 80376 (not prime; E = Z/80376 x Z/2), cofactor := 1"}}}
pdp_cell.ladder_entry = lambda p: ENTRY
pdp_common.ladder_entry = lambda p: ENTRY

# ------------------------------------------------------------------ S4 polynomial at p' = 11
def build_s4_polynomial(E, F):
    m, K = 4, 8
    monos = symmetrize.monomials_total(m, K)
    N = len(monos)
    pts, rhs = [], []
    for ms in itertools.combinations_with_replacement(range(P), m):
        cs = gfpn5_core.S_poly_res(E, [F(v) for v in ms], K)
        assert len(cs) == K + 1
        pts.append(symmetrize.elem_sym(list(ms), P)); rhs.append(cs)
    M = symmetrize.eval_monomials_rows(pts, monos, P)
    R = len(pts); ncol = N + (K + 1) * 5
    A = flint.nmod_mat(R, ncol, P)
    for i in range(R):
        for j in range(N):
            v = int(M[i, j])
            if v: A[i, j] = v
        for k in range(K + 1):
            c = F.coeffs(rhs[i][k])
            for j in range(5):
                if c[j]: A[i, N + k * 5 + j] = c[j]
    Rr, rank = A.rref()
    # rank of the monomial block must be N and the system consistent (no pivot in the RHS block)
    ok_rank = True
    for i in range(N):
        if int(Rr[i, i]) != 1: ok_rank = False
    surplus_nonzero = 0
    for i in range(N, R):
        for j in range(ncol):
            if int(Rr[i, j]) != 0: surplus_nonzero += 1
    C = np.zeros((K + 1, N, 5), dtype=np.int64)
    for i in range(N):
        for k in range(K + 1):
            for j in range(5):
                C[k, i, j] = int(Rr[i, N + k * 5 + j])
    support = int(np.count_nonzero(C.any(axis=2).any(axis=0)))
    meta = {"arm": "S4", "m": m, "p": P, "N_monomials": N, "support_nonzero_monomials": support,
            "sample_points": R, "holdout_rows": R - N, "held_out_mismatches": surplus_nonzero,
            "rank_ok": ok_rank, "rref_rank": int(rank), "deg_in_X": K,
            "construction": "red-team harness: rref interpolation of gfpn5_core.S_poly_res over all multisets of F_11"}
    return symmetrize.ArmPolynomial("S4", m, monos, P, C, meta)

def eval_pol_at(pol, F, e_vals, xR):
    """Evaluate the arm polynomial at e (F_p ints) and X = xR (F_q) -> F_q element."""
    sp = pol.specialise(F, xR)                       # (N, 5) F_q coefficients
    acc = [0] * 5
    for i, a in enumerate(pol.monos):
        mv = 1
        for v, ex in zip(e_vals, a):
            mv = mv * pow(int(v), ex, P) % P
        if mv:
            for j in range(5):
                acc[j] = (acc[j] + mv * int(sp[i, j])) % P
    return acc

# ------------------------------------------------------------------ truth set (independent GP)
def binom_interval_99(N, f):
    """Central 99% interval of Binomial(N, f): [smallest c with CDF > 0.005, smallest c with CDF >= 0.995]."""
    lo = hi = None; cdf = 0.0
    for c in range(N + 1):
        lp = math.lgamma(N + 1) - math.lgamma(c + 1) - math.lgamma(N - c + 1) + c * math.log(f) + (N - c) * math.log1p(-f)
        cdf += math.exp(lp)
        if lo is None and cdf > 0.005: lo = c
        if hi is None and cdf >= 0.995: hi = c; break
    return lo, hi

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-rate", type=int, default=1400)
    ap.add_argument("--complete", action="store_true")
    ap.add_argument("--target-timeout", type=int, default=600)
    args = ap.parse_args()
    t0 = time.time()
    summary = {"task": "TASK-20260923-404bf9", "object": "A", "p": P, "cmod": CMOD, "curve": ENTRY["curves"][SHAPE]["model"],
               "harness_supplied": ["ladder entry (p', c, curve)", "subgroup_prime := #E, cofactor := 1",
                                    "S4 polynomial by rref interpolation of the producer's S_poly_res",
                                    "fcntl lock around each msolve subprocess"],
               "producer_code_used_unchanged": ["pdp_cell.cmd_cell", "pdp_common.base_point/targets/lift_solution_S/sign_search/make_certificate",
                                                "symmetrize.specialise/descend_and_write/run_msolve/parse_msolve_param/rational_solutions",
                                                "verify_independent.verify", "gfpn5_core (field, curve, S_poly_res)"]}
    F = gfpn5_core.Fq(P, CMOD)
    E, cv = pdp_common.make_curve(F, ENTRY, SHAPE)
    # --- polynomial
    tb = time.time()
    pol = build_s4_polynomial(E, F)
    os.makedirs(os.environ["GFPN_CACHE_DIR"], exist_ok=True)
    cpath = pdp_common.cache_path(P, SHAPE, "S4", 4)
    h = pdp_common.save_polynomial(pol, cpath)
    summary["polynomial"] = {**pol.meta, "sha256": h, "seconds": round(time.time() - tb, 2)}
    log("polynomial", pol.meta)
    assert pol.meta["rank_ok"] and pol.meta["held_out_mismatches"] == 0, "S4 interpolation not exact"
    # --- base point exactly as the producer's cmd_cell computes it
    G, n = pdp_common.base_point(E, cv, P, SHAPE)
    Gj = pdp_common.pt_json(F, G)
    summary["G"] = Gj; summary["n_used_by_targets"] = n
    # --- independent truth set (GP), under the lock
    tout = os.path.join(HERE, "truth_p11_C2.txt")
    gpcmd = (f"P_={P}; C_={CMOD}; A2_={A2}; A4_={A4}; A6_={A6}; OUT_=\"{tout}\"; "
             f"GX_={Gj[0]}; GY_={Gj[1]}; read(\"{os.path.join(HERE, 'truth_S4.gp')}\");")
    with open(LOCK, "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            gp = subprocess.run(["gp", "-q", "-s", "256000000"], input=gpcmd, text=True, capture_output=True, timeout=1800)
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    log("truth gp:", gp.stdout.strip(), gp.stderr.strip()[:500])
    summary["truth_gp_stdout"] = gp.stdout.strip(); summary["truth_gp_stderr"] = gp.stderr.strip()[:2000]
    import ast
    truth = [ast.literal_eval(line) for line in open(tout) if line.strip()]
    logs = {}
    for line in open(tout + ".logs"):
        if line.strip():
            xc, yc, k = ast.literal_eval(line)
            logs[(tuple(xc), tuple(yc))] = k
    ordG = int([s for s in gp.stdout.split() if s.startswith("ordG=")][0].split("=")[1])
    summary["ordG"] = ordG
    S4x = {}
    for xc, yc, in2, wit in truth:
        S4x.setdefault(tuple(xc), {"inS2": False, "witness": wit, "points": []})
        S4x[tuple(xc)]["inS2"] |= bool(in2)
        S4x[tuple(xc)]["points"].append((tuple(xc), tuple(yc)))
    assert ordG == n == ORD_G, (ordG, n)
    in_G = [pt for pt in logs if isinstance(logs[pt], int) and logs[pt] >= 0]
    # targets are R = [k]G with k uniform in [1, n-1], n = ord(G): uniform on <G> \ {O}
    n_dec_in_G = len(in_G)
    f_G = n_dec_in_G / (n - 1)
    summary["truth"] = {"S4_points": len(truth), "S4_x_values": len(S4x), "S4_points_in_<G>": n_dec_in_G,
                        "S4_x_values_in_S2": sum(v["inS2"] for v in S4x.values()),
                        "f_target_distribution": f_G, "f_global_S4_over_E": len(truth) / ORDER}
    log("truth summary", summary["truth"])
    # --- check the polynomial vanishes at every witness decomposition (x-values only; X = x(R))
    bad = 0
    for xc, yc, in2, wit in truth:
        e_vals = symmetrize.elem_sym([int(w) for w in wit], P)
        val = eval_pol_at(pol, F, e_vals, F.from_coeffs(xc))
        if any(val): bad += 1
    summary["polynomial"]["witness_nonvanishing_count"] = bad
    log("witness check: nonvanishing", bad, "of", len(truth))
    assert bad == 0
    # --- RATE TEST: the producer's random-target cell path, unchanged
    def run_cell(rundir, ntargets):
        os.makedirs(os.path.join(rundir, "certificates"), exist_ok=True)
        os.environ["GFPN_RUN_DIR"] = rundir
        a = SimpleNamespace(p=P, shape=SHAPE, arm="S4", m=4, targets=ntargets, target_timeout=args.target_timeout,
                            cell_watchdog=8 * 3600, max_consecutive_not_measured=3, target_kind="random")
        pdp_cell.cmd_cell(a)
        return json.load(open(os.path.join(rundir, "raw-result.json")))
    def compare(raw, label):
        rows = raw["targets"]
        res = {"label": label, "n_targets": len(rows), "n_measured": 0, "truth_decomposable": 0, "pipeline_verified": 0,
               "misses": [], "false_positive": 0, "not_measured": len(raw.get("not_measured", [])),
               "D_values_on_truth_decomposable": {}, "msolve_outcomes": {}}
        for r in rows:
            oc = r["msolve"]["outcome"]; res["msolve_outcomes"][oc] = res["msolve_outcomes"].get(oc, 0) + 1
            if r.get("status") != "measured": continue
            res["n_measured"] += 1
            xt = tuple(r["x_R"]); truthdec = xt in S4x
            found = (r.get("n_relations_verified") or 0) > 0
            res["truth_decomposable"] += truthdec; res["pipeline_verified"] += found
            if found and not truthdec: res["false_positive"] += 1
            if truthdec:
                d = str(r.get("D")); res["D_values_on_truth_decomposable"][d] = res["D_values_on_truth_decomposable"].get(d, 0) + 1
            if truthdec and not found:
                res["misses"].append({"target": r["target"], "k": r["k"], "x_R": r["x_R"], "inS2": S4x[xt]["inS2"],
                                      "witness_x": S4x[xt]["witness"], "D": r.get("D"), "no_solution": r["msolve"].get("no_solution"),
                                      "n_rational_solutions": r.get("n_rational_solutions"), "lift_diagnostics": r.get("lift_diagnostics"),
                                      "msolve_returncode": r["msolve"].get("returncode"), "outcome": r["msolve"].get("outcome")})
        return res
    rate_dir = os.path.join(HERE, "run_rate")
    tr = time.time()
    raw = run_cell(rate_dir, args.n_rate)
    cmp_rate = compare(raw, "rate test: producer targets() stream, seed 2026092001:targets:11:ecgfp5_shaped")
    Nm = cmp_rate["n_measured"]
    lo, hi = binom_interval_99(Nm, f_G) if 0 < f_G < 1 else (None, None)
    cmp_rate.update({"f": f_G, "N_times_f": Nm * f_G, "binomial_99pct_interval": [lo, hi],
                     "observed_verified": cmp_rate["pipeline_verified"],
                     "observed_inside_interval": (lo <= cmp_rate["pipeline_verified"] <= hi) if lo is not None else None,
                     "seconds": round(time.time() - tr, 1)})
    summary["rate_test"] = cmp_rate
    log("RATE TEST", {k: v for k, v in cmp_rate.items() if k != "misses"}, "misses", len(cmp_rate["misses"]))
    json.dump(summary, open(os.path.join(HERE, "objA_summary.json"), "w"), indent=1, default=str)
    # --- SUPPLEMENTARY COMPLETENESS: every decomposable x-value in <G>, through the same path
    if args.complete:
        reps = {}
        for pt in in_G:
            reps.setdefault(pt[0], pt)
        tl = []
        for i, (xc, pt) in enumerate(sorted(reps.items())):
            R = (F.from_coeffs(pt[0]), F.from_coeffs(pt[1]))
            k = int(logs[pt])
            assert E.mul(k, G) == R
            tl.append((i, k, R))
        pdp_cell.targets = lambda E_, G_, n_, p_, shape_, count=20: tl[:count]
        tc = time.time()
        rawc = run_cell(os.path.join(HERE, "run_complete"), len(tl))
        cmp_c = compare(rawc, "supplementary completeness: one target per decomposable x-value in <G> (known k by PARI ellog)")
        cmp_c["seconds"] = round(time.time() - tc, 1)
        cmp_c["recovery_rate"] = cmp_c["pipeline_verified"] / cmp_c["truth_decomposable"] if cmp_c["truth_decomposable"] else None
        summary["completeness_test"] = cmp_c
        log("COMPLETENESS", {k: v for k, v in cmp_c.items() if k != "misses"}, "misses", len(cmp_c["misses"]))
    summary["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(summary, open(os.path.join(HERE, "objA_summary.json"), "w"), indent=1, default=str)
    # --- pack the per-target msolve logs (kept, compressed)
    for rd in ("run_rate", "run_complete"):
        d = os.path.join(HERE, rd)
        if not os.path.isdir(d): continue
        files = sorted(glob.glob(os.path.join(d, "cell_t*.ms.*")))
        if files:
            with tarfile.open(os.path.join(d, "msolve_logs.tar.gz"), "w:gz") as tf:
                for fpath in files: tf.add(fpath, arcname=os.path.basename(fpath))
            for fpath in files: os.remove(fpath)
    log("done", summary["wall_seconds"])

if __name__ == "__main__":
    main()
