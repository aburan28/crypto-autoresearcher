"""Joint F7 (TASK-20260929-fd1a9f): the prediction (2) exponent against the floor
model, with MC-1 (20000 replicates), MC-2 (200-seed sweeps with Monte Carlo s.d.
and flip fractions) and MC-5 (interval calibration by simulation at this design).

Inputs: the SEALED per-instance table rederivation/out/instances.jsonl (row data
only) and stats.py loaded by file path (frozen bootstrap_slope / fit_exponent).
No solver module is imported. Seeds are declared in the code and in the output.

usage: python3 f7.py <outdir>
"""
import collections
import hashlib
import importlib.util
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
STATS = WT + "/src/crypto_autoresearcher/index_calculus/stats.py"


def load_stats():
    spec = importlib.util.spec_from_file_location("ic_stats_frozen_by_path", STATS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = load_stats()
BASES = {"subgroup": ("subgroup",), "dickson": ("dickson",), "small_x": ("small_x",),
         "random_sub": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
         "random_dick": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}


def series(recs, m, base, mode, quantity):
    """(xs, ys, groups) over main-panel S15 rows of (m, base, mode)."""
    xs, ys, gs = [], [], []
    for r in recs:
        k = r["key"]
        if r["set"] != "S15" or k[0] != "main" or k[3] != m or k[5] != mode or k[4] not in BASES[base] or r["excluded"]:
            continue
        N, Sv = r["N"], r["S3"]
        if quantity == "S3":
            y = math.log2(Sv)
        elif quantity.startswith("ratio_"):
            rr = r[{"ratio_frozen": "r_frozen", "ratio_rank": "r_rank", "ratio_rank1": "r_rank1"}[quantity]]
            if not rr:
                continue
            y = math.log2(Sv / (0.5 * math.sqrt(rr * N)))
        elif quantity.startswith("floor_"):
            rr = r[{"floor_frozen": "r_frozen", "floor_rank": "r_rank", "floor_rank1": "r_rank1"}[quantity]]
            if not rr:
                continue
            y = math.log2(0.5 * math.sqrt(rr * N))
        elif quantity == "model_sqrtFN":
            y = math.log2(math.sqrt(r["fb_size"] * N))
        elif quantity == "r_rank_over_F":
            y = math.log2(r["r_rank"] / r["fb_size"]) if r["r_rank"] else None
        elif quantity == "r_frozen_over_F":
            y = math.log2(r["r_frozen"] / r["fb_size"])
        elif quantity == "S3_over_sqrtFN":
            y = math.log2(Sv / math.sqrt(r["fb_size"] * N))
        else:
            raise ValueError(quantity)
        if y is None:
            continue
        xs.append(r["log2N"])
        ys.append(y)
        gs.append(k[1])
    return xs, ys, gs


def fit(xs, ys, gs, reps, seed):
    return S.bootstrap_slope(xs, ys, gs, reps=reps, level=0.95, seed=seed)


def residual_sd(xs, ys):
    b = S.ols_slope(xs, ys)
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    res = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
    return b, res, statistics.pstdev(res) * math.sqrt(len(res) / (len(res) - 2))


def calibrate(xs, gs, sd, resid, beta0, law, nseries, master):
    """Coverage of the frozen 95% percentile interval (reps 2000, seed 0) and the
    half-width multiplier kappa giving 95% coverage, at this design."""
    rng = random.Random(master)
    cover, zs, above0_false = 0, [], 0
    for _ in range(nseries):
        if law == "gauss":
            eps = [rng.gauss(0, sd) for _ in xs]
        elif law == "t3":
            eps = []
            for _ in xs:
                z = rng.gauss(0, 1)
                chi = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
                eps.append(sd * z / math.sqrt(chi / 3) / math.sqrt(3.0))  # var(t3) = 3
        elif law == "empirical":
            eps = [rng.choice(resid) for _ in xs]
        else:
            raise ValueError(law)
        ys = [beta0 * x + e for x, e in zip(xs, eps)]
        f = S.bootstrap_slope(xs, ys, gs, reps=2000, level=0.95, seed=0)
        b, lo, hi = f["slope"], f["lo"], f["hi"]
        if lo <= beta0 <= hi:
            cover += 1
        hw = (b - lo) if beta0 < b else (hi - b)
        zs.append(abs(b - beta0) / hw if hw > 0 else float("inf"))
        if beta0 == 0 and (hi < 0 or lo > 0):
            above0_false += 1
    zs.sort()
    kappa = zs[int(math.ceil(0.95 * len(zs))) - 1]
    p = cover / nseries
    return {"law": law, "n_series": nseries, "beta0": beta0, "coverage": p,
            "coverage_se": math.sqrt(p * (1 - p) / nseries), "kappa_95": kappa,
            "false_exclusion_rate_of_0": (above0_false / nseries) if beta0 == 0 else None, "master_seed": master}


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    recs = [json.loads(l) for l in open(os.path.join(HERE, "..", "rederivation", "out", "instances.jsonl"))]
    out = {"stats_py_sha256": hashlib.sha256(open(STATS, "rb").read()).hexdigest(), "seeds": {
        "MC-1": "bootstrap_slope(reps=20000, seed=0)", "MC-2": "bootstrap_slope(reps=2000, seed=s) for s in 1..200",
        "MC-5": "random.Random('F7-cal|<quantity>|<law>|<beta0>') per configuration; 1000 series; interval reps 2000 seed 0"}}
    # (b) ratio slopes per (m, base, mode) under r_frozen, r_rank, r_rank1 at 20000 replicates
    slopes = {}
    for m in (3, 4, 5):
        for base in BASES:
            for mode in ("census", "on"):
                for q in ("ratio_frozen", "ratio_rank", "ratio_rank1", "S3"):
                    xs, ys, gs = series(recs, m, base, mode, q)
                    f = fit(xs, ys, gs, 20000, 0)
                    slopes[f"m{m}|{base}|{mode}|{q}"] = {"slope": f["slope"], "lo": f["lo"], "hi": f["hi"], "n": f["n"]}
    out["ratio_slopes_20000"] = slopes
    # m = 4 small_x on: the decision-bearing series
    dec = {}
    for q in ("S3", "ratio_frozen", "ratio_rank", "ratio_rank1", "floor_frozen", "floor_rank", "floor_rank1", "model_sqrtFN",
              "r_rank_over_F", "r_frozen_over_F", "S3_over_sqrtFN"):
        xs, ys, gs = series(recs, 4, "small_x", "on", q)
        f20 = fit(xs, ys, gs, 20000, 0)
        los, his, flips = [], [], 0
        ref_excl = (f20["hi"] < 0) or (f20["lo"] > 0)
        for s in range(1, 201):
            f = fit(xs, ys, gs, 2000, s)
            los.append(f["lo"])
            his.append(f["hi"])
            if ((f["hi"] < 0) or (f["lo"] > 0)) != ref_excl:
                flips += 1
        b, res, sd = residual_sd(xs, ys)
        dec[q] = {"n": f20["n"], "slope": f20["slope"], "lo_20000": f20["lo"], "hi_20000": f20["hi"],
                  "MC2_lo_mean_sd": [statistics.mean(los), statistics.stdev(los)],
                  "MC2_hi_mean_sd": [statistics.mean(his), statistics.stdev(his)],
                  "MC2_flip_fraction_of_excludes_0": flips / 200, "residual_sd": sd}
    out["m4_small_x_on"] = dec
    # sub-range slopes (lower-order-term check) for the ratio under r_rank and r_frozen
    sub = {}
    for q in ("ratio_rank", "ratio_frozen", "S3"):
        xs, ys, gs = series(recs, 4, "small_x", "on", q)
        for lo_b, hi_b in ((12, 22), (22, 32), (20, 32), (12, 32)):
            sel = [(x, y, g) for x, y, g in zip(xs, ys, gs) if lo_b <= g <= hi_b]
            f = fit([a for a, _, _ in sel], [b for _, b, _ in sel], [c for _, _, c in sel], 20000, 0)
            sub[f"{q}|{lo_b}-{hi_b}"] = {"slope": f["slope"], "lo": f["lo"], "hi": f["hi"], "n": f["n"]}
    out["m4_small_x_on_subranges"] = sub
    # (c) MC-5 calibration at this design (55 points, 11 rungs x 5)
    cal = []
    for q in ("S3", "ratio_rank", "ratio_frozen"):
        xs, ys, gs = series(recs, 4, "small_x", "on", q)
        b, res, sd = residual_sd(xs, ys)
        for law in ("gauss", "t3", "empirical"):
            for beta0 in (0.0, b):
                cal.append(dict(calibrate(xs, gs, sd, res, beta0, law, 1000, f"F7-cal|{q}|{law}|{beta0:.6f}"),
                                quantity=q, residual_sd=sd))
    out["MC5_calibration"] = cal
    # calibrated decision on the ratio slopes (worst-case kappa over laws and beta0)
    dd = {}
    for q in ("ratio_rank", "ratio_frozen", "S3"):
        kap = max(c["kappa_95"] for c in cal if c["quantity"] == q)
        d = dec[q]
        lo_c = d["slope"] - kap * (d["slope"] - d["lo_20000"])
        hi_c = d["slope"] + kap * (d["hi_20000"] - d["slope"])
        dd[q] = {"kappa_95_worst": kap, "calibrated_interval": [lo_c, hi_c],
                 "excludes_0": (hi_c < 0) or (lo_c > 0),
                 "margin_hi_to_0": -hi_c, "MC2_sd_hi": d["MC2_hi_mean_sd"][1]}
    out["calibrated_decisions_m4_small_x_on"] = dd
    # every (m, base, on) ratio slope under r_rank, decision with the m4 small_x kappa as a guide only
    json.dump(out, open(os.path.join(outdir, "f7.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({"m4_small_x_on": {q: {k: v for k, v in d.items()} for q, d in dec.items()},
                      "calibrated": dd, "cal": [{k: c[k] for k in ("quantity", "law", "beta0", "coverage", "kappa_95", "false_exclusion_rate_of_0")} for c in cal]},
                     indent=1)[:8000])


if __name__ == "__main__":
    main()
