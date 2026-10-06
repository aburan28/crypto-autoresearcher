#!/usr/bin/env python3
"""TASK-20260929-c40e48 (validator), joint J2: BLIND re-derivation of the
EXP-PFDR-7c8bf2 quantities P0, P2-P6 and the analysis_outcomes id.

Written from experiments/EXP-PFDR-7c8bf2/specification.yaml (text) alone.
Reads ONLY the five committed input files and the frozen stats.py (loaded by
file path, so no crypto_autoresearcher package __init__ and no solver module is
imported). Never opens analyze_floor.py, the run directory or any report.

Two computations (card RV-3):
  (i)  the frozen method: stats.bootstrap_slope(xs, ys, groups=bits,
       reps=2000, level=0.95, seed=0), rows in FILE ORDER (primary; the
       specification does not fix a row order, so SORTED (bits, curve) order
       is also reported as an order-sensitivity check);
  (ii) an own implementation: OLS by hand (numpy float64) and a
       stratified-by-rung percentile bootstrap with numpy's PCG64 RNG,
       2000 reps, 50 independent seeds (Monte Carlo spread of each endpoint),
       plus one 200000-rep reference run.
Agreement criterion, declared before any result was seen: each frozen endpoint
lies within 3 standard deviations (over the 50 own 2000-rep runs, same
order-statistic convention as stats.py) of the mean own endpoint, and the
frozen point slope equals the hand OLS slope to 1e-12.

Usage: python rederive.py --results-dir <dir> --stats <stats.py> --out <dir>
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import math
import random
import resource
import sys
import time

import numpy as np

FILES = [
    "sweep-minfill-20260926",
    "sweep-arity-minfill-20260926",
    "sweep-arity67-20260928",
    "sweep-mitm-20260926",
    "sweep-arity-20260926",
]
# P3: one primary series per (file, m, fb) on engine mitm.
SERIES = [
    ("S3-smallx-filtered", "sweep-minfill-20260926", 3, "small_x"),
    ("S3-random-filtered", "sweep-minfill-20260926", 3, "random"),
    ("S3-subgroup-filtered", "sweep-minfill-20260926", 3, "subgroup"),
    ("S3-smallx-unfiltered", "sweep-arity-minfill-20260926", 3, "small_x"),
    ("S4-smallx", "sweep-arity-minfill-20260926", 4, "small_x"),
    ("S5-smallx", "sweep-arity-minfill-20260926", 5, "small_x"),
    ("S6-smallx", "sweep-arity67-20260928", 6, "small_x"),
    ("S7-smallx", "sweep-arity67-20260928", 7, "small_x"),
]
# analysis_outcomes windows (OUT-CONSISTENT / OUT-PREDICTION-MISS)
WINDOW = {3: (-0.03, 0.03), 5: (-0.03, 0.03), 7: (-0.03, 0.03),
          4: (0.095, 0.155), 6: (0.053, 0.113)}
MODEL = {3: 0.0, 5: 0.0, 7: 0.0, 4: 1 / 8, 6: 1 / 12}


def load_stats(path):
    spec = importlib.util.spec_from_file_location("frozen_stats_7c8bf2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def m_of(method):
    assert method.startswith("ic_m"), method
    return int(method[4:])


# ---------------------------------------------------------------- own bootstrap
def own_ols(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    mx, my = x.mean(), y.mean()
    return float(np.sum((x - mx) * (y - my)) / np.sum((x - mx) ** 2))


def own_boot_slopes(x, y, groups, reps, seed):
    """Stratified (by rung) nonparametric bootstrap of the OLS slope, numpy PCG64."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    rng = np.random.Generator(np.random.PCG64(seed))
    strata = collections.defaultdict(list)
    for i, g in enumerate(groups):
        strata[g].append(i)
    out = []
    done = 0
    while done < reps:  # chunked to keep resident memory small (RV-7)
        k = min(20_000, reps - done)
        cols = []
        for g in sorted(strata):
            mem = np.asarray(strata[g])
            cols.append(mem[rng.integers(0, len(mem), size=(k, len(mem)))])
        idx = np.concatenate(cols, axis=1)  # k x n
        xb, yb = x[idx], y[idx]
        xm = xb.mean(axis=1, keepdims=True)
        ym = yb.mean(axis=1, keepdims=True)
        out.append(np.sum((xb - xm) * (yb - ym), axis=1) / np.sum((xb - xm) ** 2, axis=1))
        done += k
    return np.concatenate(out)


def pct_statspy(sorted_boots, level=0.95):
    n = len(sorted_boots)
    tail = (1 - level) / 2
    return (float(sorted_boots[int(math.floor(tail * (n - 1)))]),
            float(sorted_boots[int(math.ceil((1 - tail) * (n - 1)))]))


def pct_linear(boots, level=0.95):
    tail = (1 - level) / 2
    return (float(np.quantile(boots, tail)), float(np.quantile(boots, 1 - tail)))


def excludes(lo, hi, v):
    return v < lo or v > hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed-scan", type=int, default=200,
                    help="stats.bootstrap_slope seeds 0..K-1 for the Monte Carlo stability scan")
    args = ap.parse_args()
    t0 = time.time()
    stats = load_stats(args.stats)
    assert not any(k.startswith("crypto_autoresearcher") for k in sys.modules), "package imported"

    out = {"task": "TASK-20260929-c40e48", "joint": "J2", "started_unix": t0,
           "inputs": {}, "P0": {}, "stats_py_sha256": sha256(args.stats)}

    # ------------------------------------------------------------------ P0
    rows_by_file = {}
    for f in FILES:
        path = f"{args.results_dir}/{f}.jsonl.gz"
        with gzip.open(path, "rt") as fh:
            lines = fh.read().splitlines()
        rows = [json.loads(l) for l in lines if l.strip()]
        rows_by_file[f] = rows
        cnt = collections.Counter((r.get("method"), r.get("fb"), r.get("engine"), r.get("la_pivot"))
                                  for r in rows)
        out["inputs"][f] = {"sha256": sha256(path), "line_count": len(lines)}
        out["P0"][f] = {
            "counts_by_method_fb_engine_la_pivot": {"|".join(str(x) for x in k): v
                                                    for k, v in sorted(cnt.items(), key=str)},
            "ok_false_rows": [{"bits": r["bits"], "curve": r["curve"], "method": r["method"],
                               "fb": r.get("fb"), "engine": r.get("engine")}
                              for r in rows if r.get("ok") is not True],
        }

    # ------------------------------------------------------------------ P2
    ic = []
    for f in FILES:
        for r in rows_by_file[f]:
            if not str(r.get("method", "")).startswith("ic_") or r.get("ok") is not True:
                continue
            S = r["s3_solves"]
            T = 0 if r["engine"] == "enumerate" else r["table_s3_solves"]
            rr = r["relations"]
            N = r["N"]
            floor = 0.5 * math.sqrt(rr * N)
            ic.append({
                "file": f, "bits": r["bits"], "curve": r["curve"], "method": r["method"],
                "m": m_of(r["method"]), "fb": r["fb"], "engine": r["engine"],
                "S": S, "T": T, "search": S - T, "r": rr, "N": N, "floor": floor,
                "ratio": S / floor, "table_share": T / S, "log2N": r["log2N"],
                "enumerate_table_s3_field": r.get("table_s3_solves"),
            })
    out["P2"] = {"ic_rows_ok": len(ic),
                 "ic_rows_by_file_engine": {f"{k[0]}|{k[1]}": v for k, v in sorted(
                     collections.Counter((x["file"], x["engine"]) for x in ic).items())},
                 "enumerate_rows_with_nonzero_table_s3_field": sum(
                     1 for x in ic if x["engine"] == "enumerate" and x["enumerate_table_s3_field"])}
    with gzip.open(f"{args.out}/j2-floor-rows.jsonl.gz", "wt") as fh:
        for x in ic:
            fh.write(json.dumps(x, sort_keys=True) + "\n")

    # ------------------------------------------------------------------ P3/P4
    fits = {}
    for name, f, m, fb in SERIES:
        srows = [x for x in ic if x["file"] == f and x["m"] == m and x["fb"] == fb and x["engine"] == "mitm"]
        fits[name] = {"file": f, "m": m, "fb": fb, "n_rows": len(srows),
                      "rungs": sorted(collections.Counter(x["bits"] for x in srows).items())}
        for rng_name, lo_bits in (("12..32", 12), ("20..32", 20)):
            sel = [x for x in srows if lo_bits <= x["bits"] <= 32]
            xs = [x["log2N"] for x in sel]
            ys = [math.log2(x["ratio"]) for x in sel]
            gs = [x["bits"] for x in sel]
            frozen = stats.bootstrap_slope(xs, ys, groups=gs, reps=2000, level=0.95, seed=0)
            order = sorted(range(len(sel)), key=lambda i: (sel[i]["bits"], sel[i]["curve"]))
            frozen_sorted = stats.bootstrap_slope([xs[i] for i in order], [ys[i] for i in order],
                                                  groups=[gs[i] for i in order], reps=2000,
                                                  level=0.95, seed=0)
            hand = own_ols(xs, ys)
            # own bootstrap: 50 seeds x 2000 reps, and one 200000-rep reference
            lo_s, hi_s, lo_l, hi_l = [], [], [], []
            for s in range(50):
                b = np.sort(own_boot_slopes(xs, ys, gs, 2000, 1_000_003 + s))
                a1, a2 = pct_statspy(b)
                c1, c2 = pct_linear(b)
                lo_s.append(a1); hi_s.append(a2); lo_l.append(c1); hi_l.append(c2)
            big = np.sort(own_boot_slopes(xs, ys, gs, 200_000, 7_777_777))
            ref = pct_linear(big)
            lo_mean, lo_sd = float(np.mean(lo_s)), float(np.std(lo_s, ddof=1))
            hi_mean, hi_sd = float(np.mean(hi_s)), float(np.std(hi_s, ddof=1))
            z_lo = (frozen["lo"] - lo_mean) / lo_sd
            z_hi = (frozen["hi"] - hi_mean) / hi_sd
            model = MODEL[m]
            # residuals of the primary OLS fit (tail check)
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            icpt = my - hand * mx
            res = [(abs(yv - (icpt + hand * xv)), sel[i]) for i, (xv, yv) in enumerate(zip(xs, ys))]
            worst = max(res, key=lambda t: t[0])
            fits[name][rng_name] = {
                "n": len(sel),
                "frozen_file_order": frozen,
                "frozen_sorted_bits_curve_order": frozen_sorted,
                "hand_ols_slope": hand,
                "abs_diff_frozen_vs_hand_slope": abs(frozen["slope"] - hand),
                "own_bootstrap_statspy_convention": {"lo_mean": lo_mean, "lo_sd": lo_sd,
                                                     "hi_mean": hi_mean, "hi_sd": hi_sd,
                                                     "z_frozen_lo": z_lo, "z_frozen_hi": z_hi},
                "own_bootstrap_linear_quantile": {"lo_mean": float(np.mean(lo_l)),
                                                  "hi_mean": float(np.mean(hi_l))},
                "own_bootstrap_200k_reference_linear": {"lo": ref[0], "hi": ref[1]},
                "model_value": model,
                "frozen_excludes_model": excludes(frozen["lo"], frozen["hi"], model),
                "sorted_order_excludes_model": excludes(frozen_sorted["lo"], frozen_sorted["hi"], model),
                "own_200k_excludes_model": excludes(ref[0], ref[1], model),
                "own_mean_statspy_excludes_model": excludes(lo_mean, hi_mean, model),
                "largest_abs_residual": {"abs_residual": worst[0], "bits": worst[1]["bits"],
                                         "curve": worst[1]["curve"]},
                "agreement_within_3sd": abs(z_lo) <= 3 and abs(z_hi) <= 3
                                        and abs(frozen["slope"] - hand) <= 1e-12,
            }
        smallest = min(srows, key=lambda x: x["ratio"])
        fits[name]["smallest_ratio_row"] = {"ratio": smallest["ratio"], "bits": smallest["bits"],
                                            "curve": smallest["curve"], "fb": smallest["fb"]}
    out["P4_fits"] = fits

    # Monte Carlo stability scan of the frozen function (seeds 0..K-1): how often
    # does each interval exclude its model value? Descriptive; the outcome id is
    # defined on seed 0 only.
    scan = {}
    for name, f, m, fb in SERIES:
        srows = [x for x in ic if x["file"] == f and x["m"] == m and x["fb"] == fb and x["engine"] == "mitm"]
        scan[name] = {}
        for rng_name, lo_bits in (("12..32", 12), ("20..32", 20)):
            sel = [x for x in srows if lo_bits <= x["bits"] <= 32]
            xs = [x["log2N"] for x in sel]
            ys = [math.log2(x["ratio"]) for x in sel]
            gs = [x["bits"] for x in sel]
            los, his, exc = [], [], 0
            for s in range(args.seed_scan):
                o = stats.bootstrap_slope(xs, ys, groups=gs, reps=2000, level=0.95, seed=s)
                los.append(o["lo"]); his.append(o["hi"])
                exc += excludes(o["lo"], o["hi"], MODEL[m])
            scan[name][rng_name] = {"seeds": args.seed_scan, "fraction_excluding_model": exc / args.seed_scan,
                                    "lo_min": min(los), "lo_max": max(los),
                                    "hi_min": min(his), "hi_max": max(his)}
    out["mc_seed_scan_frozen_function"] = scan

    # ------------------------------------------------------------------ P5
    mn = min(ic, key=lambda x: x["ratio"])
    out["P5"] = {
        "n_ic_rows": len(ic),
        "min_ratio": mn["ratio"],
        "min_row": {k: mn[k] for k in ("file", "bits", "curve", "method", "fb", "engine", "S", "r", "N")},
        "rows_below_1": [{k: x[k] for k in ("file", "bits", "curve", "method", "fb", "engine", "S", "r", "N", "ratio")}
                         for x in ic if x["ratio"] < 1.0],
        "rows_below_0.9": sum(1 for x in ic if x["ratio"] < 0.9),
        "min_ratio_by_file_engine": {f"{f}|{e}": min(x["ratio"] for x in ic if x["file"] == f and x["engine"] == e)
                                     for f, e in sorted({(x["file"], x["engine"]) for x in ic})},
    }

    # ------------------------------------------------------------------ P6
    p6 = {}
    for fb in ("small_x", "random", "subgroup"):
        sel = [x for x in ic if x["file"] == "sweep-minfill-20260926" and x["m"] == 3 and x["fb"] == fb
               and x["engine"] == "mitm" and 20 <= x["bits"] <= 32]
        lr = [math.log(x["ratio"]) for x in sel]
        gm = math.exp(sum(lr) / len(lr))
        strata = collections.defaultdict(list)
        for i, x in enumerate(sel):
            strata[x["bits"]].append(i)
        # (i) random.Random(0), stats.py-style strata and order statistics
        rng = random.Random(0)
        boots = []
        for _ in range(2000):
            idx = [rng.choice(mem) for mem in strata.values() for _ in mem]
            boots.append(math.exp(sum(lr[i] for i in idx) / len(idx)))
        boots.sort()
        ci_a = pct_statspy(boots)
        # (ii) numpy PCG64, 200000 reps, linear quantiles
        lr_np = np.asarray(lr)
        g = np.random.Generator(np.random.PCG64(4242))
        bb = []
        for _ in range(10):  # 10 x 20000 = 200000 reps, chunked (RV-7)
            cols = [np.asarray(strata[k])[g.integers(0, len(strata[k]), size=(20_000, len(strata[k])))]
                    for k in sorted(strata)]
            idx = np.concatenate(cols, axis=1)
            bb.append(np.exp(lr_np[idx].mean(axis=1)))
        ci_b = pct_linear(np.concatenate(bb))
        p6[fb] = {"n": len(sel), "geo_mean": gm, "ci_random0_statspy": ci_a, "ci_numpy200k": ci_b}
    pairs = {}
    for a, b in (("small_x", "random"), ("small_x", "subgroup"), ("random", "subgroup")):
        for key in ("ci_random0_statspy", "ci_numpy200k"):
            A, B = p6[a][key], p6[b][key]
            pairs.setdefault(f"{a}~{b}", {})[key] = not (A[1] < B[0] or B[1] < A[0])
    out["P6"] = {"bases": p6, "pairwise_overlap": pairs}

    # ------------------------------------------------------------------ outcomes
    prim = {name: fits[name]["12..32"]["frozen_file_order"] for name, *_ in SERIES}
    mm = {name: m for name, _, m, _ in SERIES}
    in_window = {n: WINDOW[mm[n]][0] <= prim[n]["slope"] <= WINDOW[mm[n]][1] for n in prim}
    f1 = out["P5"]["rows_below_0.9"] > 0
    f2 = [n for n in prim if mm[n] % 2 == 1 and excludes(prim[n]["lo"], prim[n]["hi"], 0.0)]
    f3 = [n for n in prim if mm[n] % 2 == 0 and excludes(prim[n]["lo"], prim[n]["hi"], 1 / (2 * mm[n]))]
    overlap_all = all(v["ci_random0_statspy"] for v in pairs.values())
    minr = out["P5"]["min_ratio"]
    cond = {
        "OUT-CONSISTENT": all(in_window.values()) and minr >= 1.0 and overlap_all and not (f1 or f2 or f3),
        "OUT-FLOOR-VIOLATION": f1,
        "OUT-SLOPE-INTERVAL": bool(f2 or f3),
        "OUT-PREDICTION-MISS": (not all(in_window.values())) or (not overlap_all) or (0.9 <= minr < 1.0),
        "OUT-INVALID": None,  # invalidation I-1..I-4 is established in J1/J3, not from the rows
    }
    first = next((k for k in ("OUT-CONSISTENT", "OUT-FLOOR-VIOLATION", "OUT-SLOPE-INTERVAL",
                              "OUT-PREDICTION-MISS") if cond[k]), None)
    out["outcomes"] = {"conditions": cond, "F-1": f1, "F-2_series": f2, "F-3_series": f3,
                       "point_estimates_in_window": in_window, "all_base_pairs_overlap": overlap_all,
                       "first_true_in_stated_order_excluding_OUT-INVALID": first}
    out["finished_unix"] = time.time()
    out["elapsed_s"] = out["finished_unix"] - t0
    out["peak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    out["sys_modules_crypto_autoresearcher"] = sorted(k for k in sys.modules if k.startswith("crypto_autoresearcher"))
    with open(f"{args.out}/j2-results.json", "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=float)


if __name__ == "__main__":
    main()
