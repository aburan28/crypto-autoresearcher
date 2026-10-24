#!/usr/bin/env python3
"""J2: independent recomputation of every frozen metric of EXP-CZLIFT-14f6d5 (TASK-20261022-a846f4).

Written before check.py or the driver were opened.  Definitions are taken from
the specification and H-CZLIFT-27a184:
  * N_E(H): rational points of naive x-height <= H.  Producer counts include O
    (established in phase 2 by comparison with the sealed blind counts), so
    n_points = 1 + #affine points.
  * coverage cell (curve, p, H): distinct reductions mod p of the n_points points;
    uniform model E[distinct] = N_p (1 - (1 - 1/N_p)^n); ratio = distinct / model.
  * hypothesis cell set: "every coverage cell with N >= 30" -> n_points >= 30.
  * coverage_ratio_median / frac_above_1p5 / frac_below_0p5 over that set.
  * H_half(p): smallest grid H with distinct / N_p >= 1/2 (unresolved otherwise).
Two layers:
  A. arithmetic: every recorded cell field recomputed from the other raw fields.
  B. independent: N_p by the validator's own point count, points from the
     validator's own enumeration (blind lists + rank-7 enumeration), reductions
     computed here; compared cell by cell with the raw table.
Usage: j2_recompute.py RAW_1E5 RAW_3E5 BLIND_SIEVE_JSON RANK7_JSON OUT_JSON
"""
import json
import math
import statistics
import sys
from fractions import Fraction

import numpy as np

LABEL_MAP = {
    "382623908456a1": ("rank7", "382623908456a1_from_raw"),
    "grunewald-zimmert-1977-rank-ge-8": ("blind", "grunewald_zimmert_1977_rank_ge_8"),
    "brumer-kramer-1977-rank-ge-9": ("blind", "brumer_kramer_1977_rank_ge_9"),
}
REL = 1e-9


def b_inv(ai):
    a1, a2, a3, a4, a6 = ai
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def disc(ai):
    a1, a2, a3, a4, a6 = ai
    b2, b4, b6 = b_inv(ai)
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def count_Fp(ai, p):
    b2, b4, b6 = b_inv(ai)
    x = np.arange(p, dtype=np.int64)
    f = ((4 * x + b2 % p) % p * x + (2 * b4) % p) % p
    f = (f * x + b6 % p) % p
    sq = np.zeros(p, dtype=np.int64)
    sq[(x * x) % p] = 1
    # number of s in F_p with s^2 = f: 1 if f == 0, 2 if nonzero square, 0 otherwise
    nsol = np.where(f == 0, 1, 2 * sq[f])
    return 1 + int(nsol.sum())


def reduce_pt(ai, x, y, p):
    if x.denominator % p == 0:
        return "O"
    xr = x.numerator * pow(x.denominator, -1, p) % p
    yr = y.numerator * pow(y.denominator, -1, p) % p
    a1, a2, a3, a4, a6 = ai
    assert (yr * yr + a1 * xr * yr + a3 * yr - (xr ** 3 + a2 * xr * xr + a4 * xr + a6)) % p == 0
    return (xr, yr)


def model(Np, n):
    return Np * (1.0 - (1.0 - 1.0 / Np) ** n)


def close(a, b):
    return a == b or (a is not None and b is not None and abs(a - b) <= REL * max(1.0, abs(a), abs(b)))


def ols_slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def main():
    raw_paths = {"RUN-CZLIFT-ca7450": sys.argv[1], "RUN-CZLIFT-b1dce4": sys.argv[2]}
    blind = json.load(open(sys.argv[3]))["curves"]
    rank7 = json.load(open(sys.argv[4]))["curves"]
    out_path = sys.argv[5]
    pts_by_label = {}
    for label, (src, key) in LABEL_MAP.items():
        c = (rank7 if src == "rank7" else blind)[key]
        pts_by_label[label] = [(Fraction(p["x"]), Fraction(p["y"]), p["H_x"]) for p in c["points"]]
    report = {"runs": {}}
    np_cache = {}
    for rid, path in raw_paths.items():
        raw = json.load(open(path))
        met = raw["metrics"]
        R = {"curves": {}, "layerA_mismatches": [], "layerB_mismatches": [], "probes": {}}
        all_cells = []
        hmax = met["hmax"]
        counts_at_hmax = {}
        for c in raw["raw"]["curves"]:
            label, ai = c["label"], c["ainvs"]
            pts = pts_by_label[label]
            D = disc(ai)
            cv = {"discriminant_recomputed_equals_raw": D == c["discriminant"],
                  "primes_dividing_discriminant": [p for p in c["primes"] if D % p == 0]}
            # counts
            cnt = {}
            for hs, v in c["counts"].items():
                mine = 1 + sum(1 for (_, _, hx) in pts if hx <= int(hs))
                cnt[hs] = {"raw": v, "validator_incl_O": mine, "equal": v == mine}
                if v != mine:
                    R["layerB_mismatches"].append(("count", label, hs, v, mine))
            cv["counts"] = cnt
            counts_at_hmax[label] = c["counts"][str(hmax)]
            # 2-torsion / p | d probes
            cv["affine_points_total"] = len(pts)
            cv["points_with_den_divisible_by_a_prime"] = sorted({
                (str(x), p) for (x, _, _) in pts for p in c["primes"] if x.denominator % p == 0})
            # coverage cells
            cells = []
            for e in c["coverage"]:
                p, H = e["p"], e["H"]
                # Layer A: arithmetic consistency of the recorded cell
                a_cov = e["distinct"] / e["N_p"]
                a_mod = model(e["N_p"], e["n_points"])
                a_rat = e["distinct"] / a_mod
                for name, rec, mine in (("coverage", e["coverage"], a_cov), ("model_distinct", e["model_distinct"], a_mod),
                                        ("ratio_to_model", e["ratio_to_model"], a_rat)):
                    if not close(rec, mine):
                        R["layerA_mismatches"].append((label, p, H, name, rec, mine))
                if e["n_points"] != c["counts"][str(H)]:
                    R["layerA_mismatches"].append((label, p, H, "n_points!=counts[H]", e["n_points"], c["counts"][str(H)]))
                # Layer B: independent
                if (label, p) not in np_cache:
                    np_cache[(label, p)] = count_Fp(ai, p)
                Np = np_cache[(label, p)]
                sel = [(x, y) for (x, y, hx) in pts if hx <= H]
                red = {"O"} | {reduce_pt(ai, x, y, p) for (x, y) in sel}
                n = 1 + len(sel)
                b_mod = model(Np, n)
                b_rat = len(red) / b_mod
                for name, rec, mine in (("N_p", e["N_p"], Np), ("n_points", e["n_points"], n),
                                        ("distinct", e["distinct"], len(red)), ("ratio_to_model", e["ratio_to_model"], b_rat)):
                    if not close(rec, mine):
                        R["layerB_mismatches"].append((label, p, H, name, rec, mine))
                cells.append({"label": label, "p": p, "H": H, "N_p": Np, "n": n, "distinct": len(red),
                              "model": b_mod, "ratio": b_rat, "coverage": len(red) / Np})
            all_cells.extend(cells)
            # H_half by definition
            hh = {}
            for p in c["primes"]:
                cs = sorted((x for x in cells if x["p"] == p), key=lambda x: x["H"])
                hit = [x["H"] for x in cs if 2 * x["distinct"] >= x["N_p"]]
                if hit:
                    hh[str(p)] = hit[0]
            cv["h_half_validator"] = hh
            cv["h_half_raw"] = c["h_half"]
            cv["h_half_equal"] = {k: v for k, v in hh.items()} == {k: v for k, v in c["h_half"].items()}
            cv["h_half_p_ge_1000"] = sorted(int(p) for p in hh if int(p) >= 1000)
            cv["coverage_exactly_half_cells"] = [(x["p"], x["H"]) for x in cells if 2 * x["distinct"] == x["N_p"]]
            if not cv["h_half_equal"]:
                R["layerB_mismatches"].append(("h_half", label, hh, c["h_half"]))
            # h_half scaling: OLS of log H_half on log p over resolved primes
            if len(hh) >= 2:
                ps = sorted(int(k) for k in hh)
                cv["h_half_scaling_validator"] = {
                    "slope_loglog": ols_slope([math.log(p) for p in ps], [math.log(hh[str(p)]) for p in ps]),
                    "resolved_primes": len(ps)}
            # growth slope variants
            hs = sorted(int(h) for h in c["counts"])
            variants = {}
            for lo in (10, 30, 100, 300, 1000):
                sub = [h for h in hs if h >= lo]
                if len(sub) >= 2:
                    variants[f"ols_logN_vs_loglogH_H>={lo}"] = ols_slope(
                        [math.log(math.log(h)) for h in sub], [math.log(c["counts"][str(h)]) for h in sub])
                    variants[f"ols_logNaff_vs_loglogH_H>={lo}"] = (ols_slope(
                        [math.log(math.log(h)) for h in sub], [math.log(max(c["counts"][str(h)] - 1, 1)) for h in sub]))
            sub = [h for h in hs if c["counts"][str(h)] > 1]
            if len(sub) >= 2:
                variants["ols_logN_vs_loglogH_N>1"] = ols_slope(
                    [math.log(math.log(h)) for h in sub], [math.log(c["counts"][str(h)]) for h in sub])
            cv["growth_slope_raw"] = c["growth_slope"]
            cv["growth_slope_variants"] = variants
            cv["growth_slope_matching_variants"] = [k for k, v in variants.items() if v is not None and close(v, c["growth_slope"])]
            R["curves"][label] = cv
        # Metrics on the hypothesis-defined cell set
        hyp = [x for x in all_cells if x["n"] >= 30]
        ratios = [x["ratio"] for x in hyp]
        R["hypothesis_cell_set"] = {
            "definition": "n_points >= 30 (N in the hypothesis statement), all curves, all primes, all grid H",
            "cells": len(hyp),
            "median": statistics.median(ratios) if ratios else None,
            "frac_above_1p5": sum(r > 1.5 for r in ratios) / len(ratios) if ratios else None,
            "frac_below_0p5": sum(r < 0.5 for r in ratios) / len(ratios) if ratios else None,
            "min_ratio": min(ratios), "max_ratio": max(ratios),
            "cells_by_curve": {lab: sum(1 for x in hyp if x["label"] == lab) for lab in LABEL_MAP},
            "cells_n_eq_29_or_30": [(x["label"], x["p"], x["H"], x["n"]) for x in all_cells if x["n"] in (29, 30, 31)],
        }
        # Try to identify the producer's cell filter (borderline probe)
        cand = {
            "n>=30": lambda x: x["n"] >= 30,
            "n>=30 and coverage<0.5": lambda x: x["n"] >= 30 and 2 * x["distinct"] < x["N_p"],
            "n>=30 and n<N_p": lambda x: x["n"] >= 30 and x["n"] < x["N_p"],
            "n>=30 and n<=N_p": lambda x: x["n"] >= 30 and x["n"] <= x["N_p"],
            "n>=30 and model<N_p/2": lambda x: x["n"] >= 30 and 2 * x["model"] < x["N_p"],
            "n>=30 and distinct<N_p": lambda x: x["n"] >= 30 and x["distinct"] < x["N_p"],
            "n>=30 and n<=N_p/2": lambda x: x["n"] >= 30 and 2 * x["n"] <= x["N_p"],
            "n>=30 and coverage<0.9": lambda x: x["n"] >= 30 and x["distinct"] < 0.9 * x["N_p"],
            "n>=30 and n<2N_p": lambda x: x["n"] >= 30 and x["n"] < 2 * x["N_p"],
            "n>=30 and n<=2N_p": lambda x: x["n"] >= 30 and x["n"] <= 2 * x["N_p"],
            "n>=30 and n<3N_p": lambda x: x["n"] >= 30 and x["n"] < 3 * x["N_p"],
            "n>=30 and n<=3N_p": lambda x: x["n"] >= 30 and x["n"] <= 3 * x["N_p"],
            "n>30": lambda x: x["n"] > 30,
            "distinct>=30": lambda x: x["distinct"] >= 30,
        }
        fil = {}
        for k, f in cand.items():
            s = [x["ratio"] for x in all_cells if f(x)]
            fil[k] = {"cells": len(s), "median": statistics.median(s) if s else None,
                      "frac_above_1p5": (sum(r > 1.5 for r in s) / len(s)) if s else None,
                      "reproduces_manifest": len(s) == met["coverage_cells"] and s and close(statistics.median(s), met["coverage_ratio_median"])}
        R["producer_filter_search"] = fil
        R["manifest_metrics"] = {k: met[k] for k in ("coverage_cells", "coverage_ratio_median",
                                                     "coverage_ratio_frac_above_1p5", "coverage_ratio_frac_below_0p5")}
        # Criterion clauses (values only; no hypothesis verdict)
        r7 = counts_at_hmax["382623908456a1"]
        hy = R["hypothesis_cell_set"]
        R["criterion_clauses"] = {
            "counts_at_hmax": counts_at_hmax,
            "S1_both_record_curves_below_rank7": all(counts_at_hmax[l] < r7 for l in counts_at_hmax if l != "382623908456a1"),
            "S2_median_in_[0.8,1.2]_hypothesis_set": 0.8 <= hy["median"] <= 1.2,
            "S3_frac_above_1p5_lt_0.05_hypothesis_set": hy["frac_above_1p5"] < 0.05,
            "S4_no_h_half_p_ge_1000_record_curves": all(not R["curves"][l]["h_half_p_ge_1000"] for l in counts_at_hmax if l != "382623908456a1"),
            "hypothesis_every_cell_ratio_in_[0.5,1.5]": hy["min_ratio"] >= 0.5 and hy["max_ratio"] <= 1.5,
            "F1_record_curve_above_rank7": any(counts_at_hmax[l] > r7 for l in counts_at_hmax if l != "382623908456a1"),
            "F2_median_outside": not (0.8 <= hy["median"] <= 1.2),
            "F3_frac_above_ge_0.05": hy["frac_above_1p5"] >= 0.05,
        }
        R["n_cells_total"] = len(all_cells)
        report["runs"][rid] = R
    json.dump(report, open(out_path, "w"), indent=1, default=str)
    for rid, R in report["runs"].items():
        print("=====", rid)
        print(" layerA mismatches:", len(R["layerA_mismatches"]), R["layerA_mismatches"][:5])
        print(" layerB mismatches:", len(R["layerB_mismatches"]), R["layerB_mismatches"][:5])
        print(" manifest:", R["manifest_metrics"])
        print(" hypothesis set:", {k: v for k, v in R["hypothesis_cell_set"].items()})
        print(" filters reproducing manifest:", [k for k, v in R["producer_filter_search"].items() if v["reproduces_manifest"]])
        for k, v in R["producer_filter_search"].items():
            print("   ", k, v["cells"], v["median"], v["frac_above_1p5"])
        print(" clauses:", R["criterion_clauses"])
        for lab, cv in R["curves"].items():
            print(" ", lab, "disc_ok", cv["discriminant_recomputed_equals_raw"], "p|disc", cv["primes_dividing_discriminant"],
                  "counts_equal", all(v["equal"] for v in cv["counts"].values()),
                  "h_half_equal", cv["h_half_equal"], "h_half>=1000", cv["h_half_p_ge_1000"],
                  "exact_half", cv["coverage_exactly_half_cells"], "p|d", cv["points_with_den_divisible_by_a_prime"])
            print("    h_half_scaling:", cv.get("h_half_scaling_validator"), "growth raw", cv["growth_slope_raw"],
                  "match", cv["growth_slope_matching_variants"])


if __name__ == "__main__":
    main()
