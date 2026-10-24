#!/usr/bin/env python3
"""Phase-2 recomputation for TASK-20261022-38e8d2 (EXP-CZLIFT-8c50ea), joint J2.

Written before check.py was read.  Part 1 recomputes every frozen metric and
control from raw-result.json alone.  Part 2 re-enumerates all six curves with
the sealed blind square test (blind/blind_points.py, imported read-only, no
bytecode written) under two definitions of the box:

  spec      : alpha in Z[theta], |coords(alpha)| <= H, 1 <= d <= dmax
              (specification.yaml objective; distinct K-points, +-y, plus O)
  inferred  : the definition that the recorded counts imply, tested here as a
              hypothesis: gcd(a0, a1, a2, d) = 1 and max(|coords(alpha)|, d^2) <= H

and recomputes N_p = #E(F_p) and the distinct-residue counts of every coverage
cell from its own points under each of the three cube roots of 2 mod p.

Usage: python3 j2_recompute.py RUN_DIR_MAIN RUN_DIR_REPL OUT.json
"""
import json
import math
import os
import random
import statistics
import sys
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "blind"))
import blind_points as bp  # noqa: E402  (sealed blind code; reused, not modified)

RECALLED_AINVS = {  # general knowledge (Cremona tables), cross-check of raw ainvs
    "11a1": [0, -1, 1, -10, -20], "37a1": [0, 0, 1, -1, 0], "389a1": [0, 1, 1, -2, 0],
    "5077a1": [0, 0, 1, -7, 6], "234446a1": [1, -1, 0, -79, 289],
    "19047851a1": [0, 0, 1, -79, 342],
}


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def split_primes(lo, hi):
    return [p for p in range(lo, hi + 1) if is_prime(p) and p % 3 == 1 and pow(2, (p - 1) // 3, p) == 1]


def model_distinct(n, N):
    return N * (1 - (1 - 1 / N) ** n)


_NP = {}


def count_Fp(ai, p):
    if (tuple(ai), p) in _NP:
        return _NP[(tuple(ai), p)]
    a1, a2, a3, a4, a6 = ai
    n = 1
    for x in range(p):
        rhs = (x ** 3 + a2 * x * x + a4 * x + a6) % p
        disc = ((a1 * x + a3) ** 2 + 4 * rhs) % p
        if disc == 0:
            n += 1
        elif pow(disc, (p - 1) // 2, p) == 1:
            n += 2
    _NP[(tuple(ai), p)] = n
    return n


def slope(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else None


# ---------------- Part 1: from raw-result.json only ----------------
def part1(raw, manifest_metrics):
    out = {}
    curves = raw["raw"]["curves"]
    hmax = raw["metrics"]["hmax"]
    gains = {}
    for c in curves:
        K = {int(h): v for h, v in c["counts_K"].items()}
        Q = {int(h): v for h, v in c["counts_Q"].items()}
        gains[c["label"]] = {"N_K": K[hmax], "N_Q": Q[hmax], "gain": K[hmax] / Q[hmax]}
    elig = [g["gain"] for g in gains.values() if g["N_Q"] >= 10]
    out["gain_per_curve"] = gains
    out["cubic_gain_median_NQ_ge_10"] = statistics.median(elig)
    out["cubic_gain_median_all_curves"] = statistics.median([g["gain"] for g in gains.values()])
    out["cubic_gain_max_NQ_ge_10"] = max(elig)
    out["hypothesis_bound_violations"] = [k for k, g in gains.items() if g["N_Q"] >= 10 and not (g["N_Q"] <= g["N_K"] <= 4 * g["N_Q"])]
    # coverage
    cells, bad_arith = [], []
    for c in curves:
        for x in c["coverage"]:
            md = model_distinct(x["n_points"], x["N_p"])
            if abs(md - x["model_distinct"]) > 1e-9 or abs(x["distinct"] / md - x["ratio_to_model"]) > 1e-12:
                bad_arith.append((c["label"], x))
            cells.append((c["label"], x))
    out["coverage_cells_total"] = len(cells)
    out["coverage_arithmetic_mismatches"] = len(bad_arith)
    for thr in (1, 2, 10, 20):
        sel = [x["ratio_to_model"] for _, x in cells if x["n_points"] >= thr]
        out[f"coverage_n_ge_{thr}"] = {
            "cells": len(sel), "median": statistics.median(sel),
            "frac_above_1p5": sum(r > 1.5 for r in sel) / len(sel),
            "frac_below_0p5": sum(r < 0.5 for r in sel) / len(sel),
            "frac_in_0p8_1p2": sum(0.8 <= r <= 1.2 for r in sel) / len(sel),
        }
    # structural ceiling: distinct <= n_points, so ratio <= n / model(n, N_p)
    ceil = [x["n_points"] / model_distinct(x["n_points"], x["N_p"]) for _, x in cells if x["n_points"] >= 20]
    out["coverage_ratio_structural_ceiling_max_over_counted_cells"] = max(ceil)
    out["coverage_cells_with_collision"] = sum(1 for _, x in cells if x["distinct"] < x["n_points"])
    # primes
    sp = split_primes(101, 5000)
    pr = curves[0]["primes"]
    out["primes"] = {
        "recorded": pr, "all_curves_same_primes": all(c["primes"] == pr for c in curves),
        "all_split_and_in_range": all(p in sp for p in pr), "n_eligible_split_primes_101_5000": len(sp),
        "first_12_eligible": sp[:12], "recorded_equals_first_12": pr == sp[:12],
        "recorded_index_in_eligible_list": [sp.index(p) for p in pr if p in sp],
    }
    # controls
    ctrl_nk_ge_nq = []
    for c in curves:
        for h in c["counts_K"]:
            if c["counts_K"][h] < c["counts_Q"][h]:
                ctrl_nk_ge_nq.append((c["label"], h))
    out["control_NK_ge_NQ_violations"] = ctrl_nk_ge_nq
    sample_checks = []
    for c in curves:
        b2, b4, b6 = bp.bcoef(c["ainvs"])
        for alpha, d, beta in c["points_sample"]:
            G = bp.G_exact(tuple(alpha), d, b2, b4, b6)
            ok = bp.mul(tuple(beta), tuple(beta)) == G
            sample_checks.append({"curve": c["label"], "alpha": alpha, "d": d, "beta": beta, "exact_square": ok,
                                  "gcd_content_d": math.gcd(*alpha, d)})
    out["points_sample_checks"] = {"n": len(sample_checks), "all_exact": all(s["exact_square"] for s in sample_checks)}
    out["points_sample_rows"] = sample_checks
    c11 = [c for c in curves if c["label"] == "11a1"][0]
    out["control_11a1_counts_K_by_H"] = {int(h): v for h, v in sorted(c11["counts_K"].items(), key=lambda kv: int(kv[0]))}
    out["control_11a1_K_equals_Q_all_H"] = c11["counts_K"] == c11["counts_Q"]
    # growth slope: try readings
    sl = {}
    for c in curves:
        Hs = sorted(int(h) for h in c["counts_K"])
        NK = [c["counts_K"][str(h)] for h in Hs]
        cand = {
            "lnN_vs_lnlnH": slope([math.log(math.log(h)) for h in Hs], [math.log(n) for n in NK]),
            "lnN_vs_lnH": slope([math.log(h) for h in Hs], [math.log(n) for n in NK]),
            "lnN_vs_lnlnH_H>=4": slope([math.log(math.log(h)) for h in Hs if h >= 4], [math.log(n) for h, n in zip(Hs, NK) if h >= 4]),
            "N_vs_lnH": slope([math.log(h) for h in Hs], NK),
        }
        sl[c["label"]] = {"recorded": c["growth_slope_K"],
                          "manifest": manifest_metrics["growth"][c["label"]]["slope_K"],
                          **{k: v for k, v in cand.items()}}
    out["growth_slope_readings"] = sl
    # metric agreement with manifest
    mm = manifest_metrics
    out["manifest_agreement"] = {
        "cubic_gain_median": (mm["cubic_gain_median"], out["cubic_gain_median_NQ_ge_10"], mm["cubic_gain_median"] == out["cubic_gain_median_NQ_ge_10"]),
        "coverage_cells": (mm["coverage_cells"], out["coverage_n_ge_20"]["cells"], mm["coverage_cells"] == out["coverage_n_ge_20"]["cells"]),
        "coverage_ratio_median": (mm["coverage_ratio_median"], out["coverage_n_ge_20"]["median"], mm["coverage_ratio_median"] == out["coverage_n_ge_20"]["median"]),
        "coverage_ratio_frac_above_1p5": (mm["coverage_ratio_frac_above_1p5"], out["coverage_n_ge_20"]["frac_above_1p5"], mm["coverage_ratio_frac_above_1p5"] == out["coverage_n_ge_20"]["frac_above_1p5"]),
        "coverage_ratio_frac_below_0p5": (mm["coverage_ratio_frac_below_0p5"], out["coverage_n_ge_20"]["frac_below_0p5"], mm["coverage_ratio_frac_below_0p5"] == out["coverage_n_ge_20"]["frac_below_0p5"]),
        "growth_N_at_hmax": all(mm["growth"][k]["N_K_at_hmax"] == gains[k]["N_K"] and mm["growth"][k]["N_Q_at_hmax"] == gains[k]["N_Q"] for k in gains),
        "raw_metrics_equal_manifest_metrics": raw["metrics"] == mm,
    }
    return out


# ---------------- Part 2: independent enumeration ----------------
def enumerate_hits(ai, hmax, dmax):
    """All (alpha, d) in the spec box with G square (method A, exact verify) -> beta."""
    return bp.run_A(ai, hmax, dmax)


def points_by_def(ai, hits, H, dmax, definition):
    """Set of distinct x (as Fraction triples) with a representation admissible at height H."""
    xs = {}
    for (a0, a1, a2, d), beta in hits.items():
        if d > dmax:
            continue
        hc = max(abs(a0), abs(a1), abs(a2))
        if definition == "spec":
            if hc > H:
                continue
        elif definition == "inferred":
            if math.gcd(math.gcd(math.gcd(a0, a1), a2), d) != 1 or max(hc, d * d) > H:
                continue
        elif definition == "spec_height_d2":
            if max(hc, d * d) > H:
                continue
        elif definition == "spec_primitive":
            if math.gcd(math.gcd(math.gcd(a0, a1), a2), d) != 1 or hc > H:
                continue
        x = tuple(Fraction(c, d * d) for c in (a0, a1, a2))
        w = tuple(Fraction(c, d ** 3) for c in beta)
        xs[x] = w
    return xs


def npts(ai, xs):
    """Distinct affine points (+-y) plus O."""
    a1, a2, a3, a4, a6 = ai
    n = 1
    for x, w in xs.items():
        n += 1 if all(c == 0 for c in w) else 2
    return n


def reduce_points(ai, xs, p, r):
    a1, a2, a3, a4, a6 = ai
    red = {("O",)}
    for x, w in xs.items():
        def ev(z):
            num = Fraction(z[0]) + z[1] * r + z[2] * r * r
            return (num.numerator * pow(num.denominator, -1, p)) % p
        X = ev(x)
        for s in ((1,) if all(c == 0 for c in w) else (1, -1)):
            yK = tuple((s * w[i] - a1 * x[i] - (a3 if i == 0 else 0)) / 2 for i in range(3))
            red.add((X, ev(yK)))
    return red


def part2(raws):
    out = {}
    cache = {}
    for tag, raw in raws.items():
        curves = raw["raw"]["curves"]
        hmax, dmax = raw["metrics"]["hmax"], raw["metrics"]["dmax"]
        res = {}
        for c in curves:
            ai = c["ainvs"]
            key = (tuple(ai), hmax, dmax)
            if key not in cache:
                hA = enumerate_hits(ai, hmax, dmax)
                hB, _ = bp.run_B(ai, hmax, dmax)
                cache[key] = (hA, set(hA) == set(hB) and all(bp.mul(hA[k], hA[k]) == bp.mul(hB[k], hB[k]) for k in hA))
            hits, ab_agree = cache[key]
            Hs = sorted(int(h) for h in c["counts_K"])
            row = {"ainvs_match_recalled": ai == RECALLED_AINVS[c["label"]], "methods_A_B_agree": ab_agree,
                   "spec_box_alpha_d_hits": len(hits), "by_H": {}}
            for H in Hs:
                ent = {"recorded": [c["counts_K"][str(H)], c["counts_Q"][str(H)]]}
                for dfn in ("spec", "inferred", "spec_height_d2", "spec_primitive"):
                    xs = points_by_def(ai, hits, H, dmax, dfn)
                    xq = {x: w for x, w in xs.items() if x[1] == 0 and x[2] == 0}
                    ent[dfn] = [npts(ai, xs), npts(ai, xq)]
                row["by_H"][H] = ent
            row["inferred_matches_recorded_all_H"] = all(e["inferred"] == e["recorded"] for e in row["by_H"].values())
            row["spec_matches_recorded_all_H"] = all(e["spec"] == e["recorded"] for e in row["by_H"].values())
            # points the spec box has at hmax that the recorded/inferred count lacks
            xs_spec = points_by_def(ai, hits, hmax, dmax, "spec")
            xs_inf = points_by_def(ai, hits, hmax, dmax, "inferred")
            row["x_in_spec_not_inferred_at_hmax"] = [
                {"x": [str(v) for v in x], "rational": x[1] == 0 and x[2] == 0,
                 "min_d": bp.min_rep(x)[0], "min_alpha": list(bp.min_rep(x)[2])}
                for x in xs_spec if x not in xs_inf]
            row["gain_spec_at_hmax"] = npts(ai, xs_spec) / npts(ai, {x: w for x, w in xs_spec.items() if x[1] == 0 and x[2] == 0})
            row["NK_NQ_spec_at_hmax"] = [npts(ai, xs_spec), npts(ai, {x: w for x, w in xs_spec.items() if x[1] == 0 and x[2] == 0})]
            # coverage cells: recompute N_p and distinct under each root, inferred and spec point sets
            cov = []
            for cell in c["coverage"]:
                p, H = cell["p"], cell["H"]
                Np = count_Fp(ai, p)
                roots = sorted(t for t in range(p) if (t ** 3 - 2) % p == 0)
                xs_i = points_by_def(ai, hits, H, dmax, "inferred")
                xs_s = points_by_def(ai, hits, H, dmax, "spec")
                d_inf = [len(reduce_points(ai, xs_i, p, r)) for r in roots]
                d_spec = [len(reduce_points(ai, xs_s, p, r)) for r in roots]
                cov.append({"p": p, "H": H, "recorded": [cell["N_p"], cell["n_points"], cell["distinct"]],
                            "N_p_own": Np, "roots": roots, "n_inferred": npts(ai, xs_i), "distinct_inferred_by_root": d_inf,
                            "n_spec": npts(ai, xs_s), "distinct_spec_by_root": d_spec})
            row["coverage_cells"] = cov
            row["N_p_all_match"] = all(x["N_p_own"] == x["recorded"][0] for x in cov)
            row["n_points_match_inferred"] = all(x["n_inferred"] == x["recorded"][1] for x in cov)
            for i in range(3):
                row[f"distinct_match_inferred_root{i}"] = all(x["distinct_inferred_by_root"][i] == x["recorded"][2] for x in cov)
            res[c["label"]] = row
        # spec-definition metrics, same cell rule (n >= 20), all three roots
        spec_gains = {k: v["NK_NQ_spec_at_hmax"] for k, v in res.items()}
        elig = [k_[0] / k_[1] for k_ in spec_gains.values() if k_[1] >= 10]
        cov_spec = {}
        for i in range(3):
            rat = []
            for v in res.values():
                for x in v["coverage_cells"]:
                    if x["n_spec"] >= 20:
                        rat.append(x["distinct_spec_by_root"][i] / model_distinct(x["n_spec"], x["N_p_own"]))
            cov_spec[f"root{i}"] = {"cells": len(rat), "median": statistics.median(rat),
                                    "frac_above_1p5": sum(r > 1.5 for r in rat) / len(rat),
                                    "frac_below_0p5": sum(r < 0.5 for r in rat) / len(rat)}
        out[tag] = {"hmax": hmax, "dmax": dmax, "curves": res,
                    "spec_definition_metrics": {"N_K_N_Q_at_hmax": spec_gains,
                                                "cubic_gain_median_NQ_ge_10": statistics.median(elig),
                                                "coverage_by_root": cov_spec}}
    return out


# ---------------- same-shape null for the coverage ratio ----------------
def null_coverage(raw, trials=1000, seed=20261022):
    """n uniform draws from a set of size N_p per counted cell; ratio = distinct / model."""
    rng = random.Random(seed)
    cells = [x for c in raw["raw"]["curves"] for x in c["coverage"] if x["n_points"] >= 20]
    medians, fr15, fr05 = [], [], []
    for _ in range(trials):
        rats = []
        for x in cells:
            n, N = x["n_points"], x["N_p"]
            dist = len({rng.randrange(N) for _ in range(n)})
            rats.append(dist / model_distinct(n, N))
        medians.append(statistics.median(rats))
        fr15.append(sum(r > 1.5 for r in rats) / len(rats))
        fr05.append(sum(r < 0.5 for r in rats) / len(rats))
    medians.sort()
    return {"trials": trials, "seed": seed, "cells": len(cells),
            "median_of_medians": statistics.median(medians),
            "median_2p5_97p5": [medians[int(0.025 * trials)], medians[int(0.975 * trials) - 1]],
            "max_frac_above_1p5": max(fr15), "max_frac_below_0p5": max(fr05)}


def main():
    run_main, run_repl, outpath = sys.argv[1:4]
    raws, p1 = {}, {}
    for tag, rd in (("main", run_main), ("replication", run_repl)):
        raw = json.load(open(os.path.join(rd, "raw-result.json")))
        import yaml  # noqa: E402
        man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))
        raws[tag] = raw
        p1[tag] = part1(raw, man["run"]["result"]["metrics"])
        p1[tag]["null_coverage"] = null_coverage(raw)
    p2 = part2(raws)
    # cross-run: are the replication counts a restriction of the main counts?
    nested = {}
    for c_m, c_r in zip(raws["main"]["raw"]["curves"], raws["replication"]["raw"]["curves"]):
        nested[c_m["label"]] = all(c_m["counts_K"][h] == c_r["counts_K"][h] and c_m["counts_Q"][h] == c_r["counts_Q"][h]
                                   for h in c_r["counts_K"])
        cm = {(x["p"], x["H"]): x for x in c_m["coverage"]}
        nested[c_m["label"] + "_coverage_cells_identical"] = all(cm[(x["p"], x["H"])] == x for x in c_r["coverage"])
    out = {"part1_raw_only": p1, "part2_enumeration": p2, "replication_counts_equal_main_counts_at_shared_H": nested}
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)


if __name__ == "__main__":
    main()
