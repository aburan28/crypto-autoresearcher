"""EXP-SEMBIN-e76704 -- confirmatory replication of the D_ff vs D_ff^max
separation found exploratorily on 2026-09-27.

Every test here is EXHAUSTIVE over GL_l(F_2), so each preregistered
prediction is an exact integer and there is no sampling ambiguity.

Usage:  python3 run_separation.py OUTDIR
Writes: OUTDIR/results.json, OUTDIR/manifest.json, OUTDIR/log.txt
Exit:   0 = all tests executed (predictions may still fail; see results.json)
        3 = infrastructure failure (never mathematical evidence)
"""
import sys, os, json, time, itertools, random, hashlib, platform

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ffd_semaev import build_system, a_real_xR, random_matched, popcount
from recomb_search import ffd as slow_ffd, new_falls_at as slow_nf, _tables, recombine
from fastfall import Kernel

# ----- frozen preregistered predictions (from the 2026-09-27 exploratory run) -----
PRED = {
    "T1_witness": {"cell": [6, 3], "M": [1, 2, 4, 8, 26],
                   "D_ff_identity": 2, "D_ff_M": 3},
    "T2_semaev_6_3": {"cell": [6, 3], "group_order": 9999360,
                      "upward": 1612800, "upward_zero_generator": 0,
                      "downward": 0, "D_ff_identity": 2, "D_ff_max": 3},
    "T3_semaev_4_2": {"cell": [4, 2], "group_order": 20160,
                      "upward": 0, "D_ff_identity": 2, "D_ff_max": 2},
    "T4_null_4_2":   {"cell": [4, 2], "group_order": 20160,
                      "upward": 5424, "D_ff_identity": 2, "D_ff_max": 3},
}
REGRESSION_CELLS = [(3,2),(4,2),(5,2),(6,2),(7,2),(3,3),(4,3),(5,3),(6,3),(7,3)]

def indep(gs):
    ms = sorted({m for f in gs for m in f}); idx = {m: i for i, m in enumerate(ms)}
    piv = []; keep = []
    for i, f in enumerate(gs):
        cur = 0
        for m in f: cur |= 1 << idx[m]
        for p, pr in piv:
            if (cur >> p) & 1: cur ^= pr
        if cur:
            for c in range(len(ms)):
                if (cur >> c) & 1: piv.append((c, cur)); break
            keep.append(i)
    return [gs[i] for i in keep]

def invertible(rows, l):
    piv = []
    for r in rows:
        cur = r
        for p, pr in piv:
            if (cur >> p) & 1: cur ^= pr
        if cur:
            for c in range(l):
                if (cur >> c) & 1: piv.append((c, cur)); break
    return len(piv) == l

def GL(l):
    for bits in itertools.product(range(1 << l), repeat=l):
        M = list(bits)
        if invertible(M, l): yield M

def cell_systems(n, npr):
    """Exactly the construction and RNG stream of the exploratory null control."""
    rng = random.Random(n * 100 + npr)
    xR = a_real_xR(n, 1, 1, rng)
    basis = ([1] + [1 << j for j in range(1, npr)])[:npr]
    sem = indep(build_system(n, npr, 1, xR, basis))
    null = indep(random_matched(sem, 2 * npr, rng))
    return sem, null, xR

def exhaustive(gs, N):
    K = Kernel(gs, N); l = len(gs); cache = {}
    base = K.ffd([1 << j for j in range(l)], cache)
    order = up = up_zero = down = 0; best = base
    for M in GL(l):
        order += 1
        if K.new_falls(M, base, cache) > 0: continue
        d = K.ffd(M, cache); d = N + 1 if d is None else d
        if d > base:
            up += 1; best = max(best, d)
            if K.zero_gen(M, cache): up_zero += 1
        elif d < base:
            down += 1
    return dict(group_order=order, D_ff_identity=base, upward=up,
                upward_zero_generator=up_zero, downward=down, D_ff_max=best)

def main(out):
    os.makedirs(out, exist_ok=True)
    logf = open(os.path.join(out, "log.txt"), "w")
    def log(*a):
        s = " ".join(str(x) for x in a); print(s, flush=True); logf.write(s + "\n"); logf.flush()
    t0 = time.time(); res = {"tests": {}, "controls": {}}

    # C1: fast kernel == original instrument on the identity, all 10 cells
    reg = []
    for n, npr in REGRESSION_CELLS:
        rng = random.Random(n * 100 + npr); xR = a_real_xR(n, 1, 1, rng)
        basis = ([1] + [1 << j for j in range(1, npr)])[:npr]
        eqs = build_system(n, npr, 1, xR, basis); N = 2 * npr
        s = slow_ffd(eqs, N, tabs=_tables(N)); f = Kernel(eqs, N).ffd([1 << j for j in range(len(eqs))], {})
        reg.append(dict(cell=[n, npr], original=s, fast=f, match=(s == f)))
    res["controls"]["C1_kernel_regression"] = dict(cells=reg, all_match=all(r["match"] for r in reg))
    log("C1 kernel regression all_match =", res["controls"]["C1_kernel_regression"]["all_match"])

    # T1: the witness, checked by the ORIGINAL instrument, plus span invariance (C2)
    sem63, _, _ = cell_systems(6, 3); N = 6
    req = recombine(sem63, PRED["T1_witness"]["M"]); tabs = _tables(N)
    t1 = dict(D_ff_identity=slow_ffd(sem63, N, tabs=tabs), D_ff_M=slow_ffd(req, N, tabs=tabs),
              new_falls_identity=[slow_nf(sem63, N, D, tabs) for D in (1, 2, 3)],
              new_falls_M=[slow_nf(req, N, D, tabs) for D in (1, 2, 3)],
              degrees_identity=[max(popcount(m) for m in f) for f in sem63],
              degrees_M=[max(popcount(m) for m in f) for f in req])
    res["tests"]["T1_witness"] = t1; log("T1", t1)
    res["controls"]["C2_span_invariant"] = (len(indep(sem63)) == len(indep(req)) == len(sem63))
    log("C2 span invariant =", res["controls"]["C2_span_invariant"])

    # T2-T4: exhaustive counts
    for key, gs, N in (("T2_semaev_6_3", sem63, 6),
                       ("T3_semaev_4_2", cell_systems(4, 2)[0], 4),
                       ("T4_null_4_2",   cell_systems(4, 2)[1], 4)):
        ts = time.time(); r = exhaustive(gs, N); r["seconds"] = round(time.time() - ts, 1)
        res["tests"][key] = r; log(key, r)

    # score against frozen predictions
    verdict = {}
    for key, pred in PRED.items():
        got = res["tests"][key]
        checks = {k: (got.get(k) == v) for k, v in pred.items() if k not in ("cell", "M")}
        verdict[key] = dict(pass_=all(checks.values()), checks=checks)
    res["verdict"] = verdict
    res["all_predictions_confirmed"] = all(v["pass_"] for v in verdict.values())
    res["controls_pass"] = res["controls"]["C1_kernel_regression"]["all_match"] and res["controls"]["C2_span_invariant"]
    res["elapsed_seconds"] = round(time.time() - t0, 1)
    log("ALL PREDICTIONS CONFIRMED =", res["all_predictions_confirmed"], " CONTROLS PASS =", res["controls_pass"])
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)

    src = {fn: hashlib.sha256(open(os.path.join(HERE, fn), "rb").read()).hexdigest()
           for fn in sorted(os.listdir(HERE)) if fn.endswith(".py")}
    json.dump(dict(experiment_id="EXP-SEMBIN-e76704", command=" ".join(sys.argv),
                   python=platform.python_version(), platform=platform.platform(),
                   source_sha256=src, preregistered=PRED,
                   started_unix=t0, elapsed_seconds=res["elapsed_seconds"]),
              open(os.path.join(out, "manifest.json"), "w"), indent=1)

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as e:
        import traceback; traceback.print_exc(); sys.exit(3)
