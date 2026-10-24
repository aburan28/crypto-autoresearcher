#!/usr/bin/env python3
"""J2 recomputation for TASK-20261022-3aca4b, written from the specification's metric
definitions BEFORE reading implementation/check.py or implementation/run.py.

Reads only raw-result.json and manifest.yaml of the two runs (by key). Every metric is
recomputed from row-level fields; first-principles quantities (discriminant, N_p, the
uniform model, sample points on the curve) are recomputed from the a-invariants alone.

Usage: python3 -I j2_recompute.py <repo-root>  > j2_recompute_output.json
"""
import json
import math
import statistics
import sys

ROOT = sys.argv[1]
EXP = ROOT + "/experiments/EXP-CZLIFT-a255fc"
RUNS = {"RUN-CZLIFT-74f172": 100000, "RUN-CZLIFT-490b33": 300000}


def load_manifest_metrics(path):
    # tiny YAML subset reader is risky; use PyYAML if present, else skip
    try:
        import yaml  # noqa
    except Exception:
        return None
    return yaml.safe_load(open(path))["run"]["result"]["metrics"]


def binv(a1, a2, a3, a4, a6):
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return b2, b4, b6, b8


def disc(ainv):
    b2, b4, b6, b8 = binv(*ainv)
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def count_Fp(ainv, p):
    b2, b4, b6, _ = binv(*ainv)
    n = 1
    for x in range(p):
        f = (4 * x * x * x + b2 * x * x + 2 * b4 * x + b6) % p
        if f == 0:
            n += 1
        elif pow(f, (p - 1) // 2, p) == 1:
            n += 2
    return n


def model(N, Np):
    return Np * (1.0 - (1.0 - 1.0 / Np) ** N)


def ols_slope(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def is_prime(n):
    if n < 2:
        return False
    for q in range(2, math.isqrt(n) + 1):
        if n % q == 0:
            return False
    return True


def main():
    out = {}
    Np_cache = {}
    for run, hmax in RUNS.items():
        raw = json.load(open(f"{EXP}/runs/{run}/raw-result.json"))
        recm = raw["metrics"]
        manm = load_manifest_metrics(f"{EXP}/runs/{run}/manifest.yaml")
        R = {"recorded_metrics_equal_manifest": (manm == recm) if manm is not None else "pyyaml-missing"}
        curves = raw["raw"]["curves"]
        # ---------- first-principles per curve ----------
        fp = {}
        for c in curves:
            ainv = c["ainvs"]
            D = disc(ainv)
            bad_listed = [p for p in c["primes"] if D % p == 0]
            nonprime = [p for p in c["primes"] if not is_prime(p)]
            out_of_range = [p for p in c["primes"] if not (101 <= p <= 20000)]
            np_mis = []
            for row in c["coverage"]:
                key = (tuple(ainv), row["p"])
                if key not in Np_cache:
                    Np_cache[key] = count_Fp(ainv, row["p"])
                if Np_cache[key] != row["N_p"]:
                    np_mis.append((row["p"], row["N_p"], Np_cache[key]))
            # sample points [a, d, s]: s^2 = 4a^3 + b2 a^2 d^2 + 2 b4 a d^4 + b6 d^6
            b2, b4, b6, _ = binv(*ainv)
            sp_bad = []
            for (a, d, s) in c["points_sample"]:
                R6 = 4 * a ** 3 + b2 * a * a * d * d + 2 * b4 * a * d ** 4 + b6 * d ** 6
                if s * s != R6 or math.gcd(a, d) != 1 or max(abs(a), d * d) > hmax:
                    sp_bad.append([a, d, s])
            fp[c["label"]] = {
                "disc_recomputed": D, "disc_recorded": c["discriminant"],
                "disc_match": D == c["discriminant"],
                "listed_primes_dividing_disc": bad_listed,
                "listed_nonprimes": nonprime,
                "listed_primes_outside_101_20000": out_of_range,
                "n_primes": len(c["primes"]),
                "N_p_mismatches": sorted(set(map(tuple, np_mis))),
                "points_sample_n": len(c["points_sample"]),
                "points_sample_failures": sp_bad,
            }
        R["first_principles"] = fp

        # ---------- row-level consistency ----------
        row_issues = []
        all_rows = []
        for c in curves:
            for row in c["coverage"]:
                N, Np, dist = row["n_points"], row["N_p"], row["distinct"]
                if N != c["counts"][str(row["H"])]:
                    row_issues.append(("n_points!=counts", c["label"], row["p"], row["H"]))
                m = model(N, Np)
                if abs(m - row["model_distinct"]) > 1e-9 * max(1, m):
                    row_issues.append(("model", c["label"], row["p"], row["H"], m, row["model_distinct"]))
                if abs(dist / m - row["ratio_to_model"]) > 1e-12:
                    row_issues.append(("ratio", c["label"], row["p"], row["H"]))
                if abs(dist / Np - row["coverage"]) > 1e-12:
                    row_issues.append(("coverage", c["label"], row["p"], row["H"]))
                if dist > min(N, Np):
                    row_issues.append(("distinct>min(N,Np)", c["label"], row["p"], row["H"]))
                all_rows.append((c["label"], c["rank_recalled"], row))
            # distinct must be non-decreasing in H at fixed p
            byp = {}
            for row in c["coverage"]:
                byp.setdefault(row["p"], []).append(row)
            for p, rows in byp.items():
                rows.sort(key=lambda r: r["H"])
                for r0, r1 in zip(rows, rows[1:]):
                    if r1["distinct"] < r0["distinct"]:
                        row_issues.append(("distinct decreasing", c["label"], p, r0["H"], r1["H"]))
            grid = sorted(int(h) for h in c["counts"])
            for h0, h1 in zip(grid, grid[1:]):
                if c["counts"][str(h1)] < c["counts"][str(h0)]:
                    row_issues.append(("count decreasing", c["label"], h0, h1))
            if len(c["coverage"]) != len(c["primes"]) * len(grid):
                row_issues.append(("coverage rows != primes x grid", c["label"], len(c["coverage"])))
        R["row_issues"] = row_issues
        R["grid"] = sorted(int(h) for h in curves[0]["counts"])

        # ---------- primary coverage metrics ----------
        def cov_metrics(rows):
            ratios = [r["distinct"] / model(r["n_points"], r["N_p"]) for (_, _, r) in rows]
            n = len(ratios)
            return {
                "cells": n,
                "median": statistics.median(ratios) if n else None,
                "frac_above_1p5_strict": sum(x > 1.5 for x in ratios) / n if n else None,
                "frac_above_1p5_ge": sum(x >= 1.5 for x in ratios) / n if n else None,
                "frac_below_0p5_strict": sum(x < 0.5 for x in ratios) / n if n else None,
                "min": min(ratios) if n else None, "max": max(ratios) if n else None,
            }

        def filt(rows, nmin=30, covmax=0.9, ge=True, le=True, pmax=None):
            keep = []
            for t in rows:
                r = t[2]
                mc = model(r["n_points"], r["N_p"]) / r["N_p"]
                okN = r["n_points"] >= nmin if ge else r["n_points"] > nmin
                okc = mc <= covmax if le else mc < covmax
                okp = True if pmax is None else r["p"] <= pmax
                if okN and okc and okp:
                    keep.append(t)
            return keep

        frozen = filt(all_rows)
        R["coverage_frozen_filter"] = cov_metrics(frozen)
        R["coverage_recorded"] = {k: recm[k] for k in (
            "coverage_cells", "coverage_ratio_median", "coverage_ratio_frac_above_1p5",
            "coverage_ratio_frac_below_0p5")}
        R["coverage_exact_match"] = (
            R["coverage_frozen_filter"]["cells"] == recm["coverage_cells"]
            and R["coverage_frozen_filter"]["median"] == recm["coverage_ratio_median"]
            and R["coverage_frozen_filter"]["frac_above_1p5_strict"] == recm["coverage_ratio_frac_above_1p5"]
            and R["coverage_frozen_filter"]["frac_below_0p5_strict"] == recm["coverage_ratio_frac_below_0p5"])
        # borderline probes: boundary equalities and filter variants
        R["coverage_boundary_probe"] = {
            "cells_with_N_eq_30": sum(1 for t in all_rows if t[2]["n_points"] == 30),
            "cells_with_modelcov_within_1e-9_of_0p9": sum(
                1 for t in all_rows
                if abs(model(t[2]["n_points"], t[2]["N_p"]) / t[2]["N_p"] - 0.9) < 1e-9),
            "variant_N_gt_30": cov_metrics(filt(all_rows, ge=False)),
            "variant_cov_lt_0p9": cov_metrics(filt(all_rows, le=False)),
            "variant_drop_p_gt_20000": cov_metrics(filt(all_rows, pmax=20000)),
            "variant_no_filter": cov_metrics(all_rows),
            "cells_at_p_20011_in_frozen_filter": sum(1 for t in frozen if t[2]["p"] == 20011),
        }
        # per-curve and per-N/N_p breakdown of the frozen cells
        per_curve = {}
        for lab in [c["label"] for c in curves]:
            rr = [t for t in frozen if t[0] == lab]
            per_curve[lab] = cov_metrics(rr)
        R["coverage_per_curve"] = per_curve
        xs = [t[2]["n_points"] / t[2]["N_p"] for t in frozen]
        R["coverage_N_over_Np_distribution"] = {
            "min": min(xs), "median": statistics.median(xs), "max": max(xs),
            "frac_cells_N_over_Np_lt_0p375": sum(x < 0.375 for x in xs) / len(xs),
            "frac_cells_N_over_Np_lt_0p874": sum(x < 0.874 for x in xs) / len(xs),
        }

        # ---------- growth slopes ----------
        gs = {}
        for c in curves:
            r = c["rank_recalled"]
            grid = sorted(int(h) for h in c["counts"])
            variants = {}
            for lo in (10, 30, 100):
                hs = [h for h in grid if lo <= h <= hmax]
                xs_ = [math.log(math.log(h)) for h in hs]
                ys_ = [math.log(c["counts"][str(h)]) for h in hs]
                variants["H_in_[%d,%d]" % (lo, hmax)] = ols_slope(xs_, ys_)
            rec = recm["growth_slopes"][c["label"]]["measured"]
            match = [k for k, v in variants.items() if v is not None and abs(v - rec) < 1e-12]
            Nmax = c["counts"][str(hmax)]
            s100 = variants["H_in_[100,%d]" % hmax]
            gs[c["label"]] = {
                "rank_recalled": r, "N_E_hmax": Nmax, "slope_variants": variants,
                "recorded": rec, "recorded_matches_variant": match,
                "predicted": r / 2, "abs_dev_H100": abs(s100 - r / 2),
                "in_scope_N_ge_20": Nmax >= 20,
                "passes_within_1": (abs(s100 - r / 2) <= 1) if Nmax >= 20 else "exempt",
            }
        R["growth_slopes"] = gs

        # ---------- h_half and its scaling ----------
        hh = {}
        for c in curves:
            byp = {}
            for row in c["coverage"]:
                byp.setdefault(row["p"], []).append(row)
            mine_ge, mine_gt = {}, {}
            for p, rows in byp.items():
                rows.sort(key=lambda t: t["H"])
                for row in rows:
                    if 2 * row["distinct"] >= row["N_p"]:
                        mine_ge.setdefault(str(p), row["H"])
                    if 2 * row["distinct"] > row["N_p"]:
                        mine_gt.setdefault(str(p), row["H"])
            exact_half = [(row["p"], row["H"]) for row in c["coverage"] if 2 * row["distinct"] == row["N_p"]]
            rec = c["h_half"]
            ent = {"recorded": rec, "recomputed_ge_half": mine_ge, "recomputed_gt_half": mine_gt,
                   "match_ge": mine_ge == rec, "match_gt": mine_gt == rec,
                   "rows_with_distinct_exactly_half": exact_half}
            if len(rec) >= 3:
                ps = sorted(rec, key=int)
                xs_ = [math.log(int(p)) for p in ps]
                ys_ = [math.log(math.log(rec[p])) for p in ps]
                ent["scaling_slope_recomputed"] = ols_slope(xs_, ys_)
                rs = recm["h_half_scaling"].get(c["label"])
                ent["scaling_recorded"] = rs
                ent["scaling_match"] = rs is not None and abs(ent["scaling_slope_recomputed"] - rs["slope"]) < 1e-12 \
                    and rs["resolved_primes"] == len(rec)
                r = c["rank_recalled"]
                ent["within_0p5_to_2_times_2_over_r"] = 0.5 * 2 / r <= ent["scaling_slope_recomputed"] <= 2 * 2 / r
            else:
                ent["scaling_recorded"] = recm["h_half_scaling"].get(c["label"])
                ent["scaling_expected_absent"] = ent["scaling_recorded"] is None
            hh[c["label"]] = ent
        R["h_half"] = hh

        # ---------- twists ----------
        trows = []
        for c in curves:
            for t in (c.get("twists") or []):
                trows.append((c["label"], t))
        tw = {"rows": len(trows)}
        if trows:
            issues = []
            for lab, t in trows:
                Nu = t["n_base_points"] + t["n_twist_points"]
                m = model(Nu, t["N_p"])
                if abs(m - t["model_union"]) > 1e-9 * max(1, m):
                    issues.append(("model_union", lab, t["D"], t["p"], m, t["model_union"]))
                if abs(t["distinct_union"] / m - t["ratio_union_to_model"]) > 1e-12:
                    issues.append(("ratio", lab, t["D"], t["p"]))
                if pow(t["D"] % t["p"], (t["p"] - 1) // 2, t["p"]) != 1:
                    issues.append(("D not a nonzero square mod p", lab, t["D"], t["p"]))
                if t["distinct_union"] > t["distinct_base"] + t["distinct_twist"] or \
                        t["distinct_union"] < max(t["distinct_base"], t["distinct_twist"]):
                    issues.append(("union bounds", lab, t["D"], t["p"]))
                if abs(t["gain_over_base"] - t["distinct_union"] / t["distinct_base"]) > 1e-12:
                    issues.append(("gain", lab, t["D"], t["p"]))
                ctr = [cc for cc in curves if cc["label"] == lab][0]
                if t["n_base_points"] != ctr["counts"].get(str(t["H"])):
                    issues.append(("n_base!=counts[H]", lab, t["D"], t["p"], t["n_base_points"]))
                cov = [r for r in ctr["coverage"] if r["p"] == t["p"] and r["H"] == t["H"]]
                if cov and cov[0]["distinct"] != t["distinct_base"]:
                    issues.append(("distinct_base!=coverage.distinct", lab, t["D"], t["p"]))
                if cov and cov[0]["N_p"] != t["N_p"]:
                    issues.append(("N_p differs", lab, t["D"], t["p"]))
            tw["row_issues"] = issues
            # completeness: for each twist curve, D, prime: D square mod p should appear
            expected = 0
            missing = []
            for c in curves:
                if not c.get("twists"):
                    continue
                for D in (-1, 2, -3, 5, -7, 13):
                    for p in c["primes"]:
                        if pow(D % p, (p - 1) // 2, p) == 1:
                            expected += 1
                            if not any(t["D"] == D and t["p"] == p for t in c["twists"]):
                                missing.append((c["label"], D, p))
            tw["expected_rows_D_square_mod_p"] = expected
            tw["missing_rows"] = missing

            def tmetrics(rows):
                ratios = [t["distinct_union"] / model(t["n_base_points"] + t["n_twist_points"], t["N_p"])
                          for _, t in rows]
                n = len(ratios)
                return {"cells": n, "median": statistics.median(ratios) if n else None,
                        "frac_above_1p5_strict": sum(x > 1.5 for x in ratios) / n if n else None}

            def tf(rows, nmin=None, covmax=None, oneO=False):
                keep = []
                for lab, t in rows:
                    Nu = t["n_base_points"] + t["n_twist_points"] - (1 if oneO else 0)
                    mc = model(Nu, t["N_p"]) / t["N_p"]
                    if nmin is not None and Nu < nmin:
                        continue
                    if covmax is not None and mc > covmax:
                        continue
                    keep.append((lab, t))
                return keep
            tw["variant_no_filter"] = tmetrics(trows)
            tw["variant_N_ge_30_cov_le_0p9"] = tmetrics(tf(trows, 30, 0.9))
            tw["variant_N_ge_30"] = tmetrics(tf(trows, 30, None))
            tw["variant_cov_le_0p9"] = tmetrics(tf(trows, None, 0.9))
            tw["recorded"] = {k: recm[k] for k in ("twist_cells", "twist_union_ratio_median",
                                                   "twist_union_ratio_frac_above_1p5")}
            tw["matching_variants"] = [k for k in ("variant_no_filter", "variant_N_ge_30_cov_le_0p9",
                                                   "variant_N_ge_30", "variant_cov_le_0p9")
                                       if tw[k]["cells"] == recm["twist_cells"]
                                       and tw[k]["median"] == recm["twist_union_ratio_median"]
                                       and tw[k]["frac_above_1p5_strict"] == recm["twist_union_ratio_frac_above_1p5"]]
            # point-at-infinity double count probe: union model with N_base + N_twist - 1
            sel = tf(trows, 30, 0.9)
            r_oneO = []
            for lab, t in sel:
                Nu = t["n_base_points"] + t["n_twist_points"] - 1
                r_oneO.append(t["distinct_union"] / model(Nu, t["N_p"]))
            tw["probe_O_counted_once_median_same_cells"] = statistics.median(r_oneO) if r_oneO else None
            tw["per_curve_rows_in_frozen_filter"] = {
                lab: sum(1 for l, _ in sel if l == lab) for lab in {l for l, _ in trows}}
            tw["n_twist_points_min"] = min(t["n_twist_points"] for _, t in trows)
        else:
            tw["recorded"] = {k: recm[k] for k in ("twist_cells", "twist_union_ratio_median",
                                                   "twist_union_ratio_frac_above_1p5")}
        R["twists"] = tw

        # ---------- frozen criteria evaluated on my numbers ----------
        cf = R["coverage_frozen_filter"]
        crit = {
            "coverage_median_in_[0.8,1.2]": 0.8 <= cf["median"] <= 1.2,
            "coverage_frac_above_1p5_lt_0.05": cf["frac_above_1p5_strict"] < 0.05,
            "every_slope_within_1_for_N_ge_20": all(v["passes_within_1"] in (True, "exempt") for v in gs.values()),
        }
        if trows:
            tm = tw.get("variant_N_ge_30_cov_le_0p9")
            crit["twist_median_in_[0.8,1.2]_(N>=30,cov<=0.9 cells)"] = 0.8 <= tm["median"] <= 1.2
            crit["twist_median_in_[0.8,1.2]_(all rows)"] = 0.8 <= tw["variant_no_filter"]["median"] <= 1.2
        R["frozen_criteria_on_recomputed_values"] = crit

        # ---------- controls ----------
        c11 = [c for c in curves if c["label"] == "11a1"][0]
        R["control_11a1_constant_5_every_H"] = {
            "counts": c11["counts"],
            "literal_holds": all(v == 5 for v in c11["counts"].values()),
            "holds_for_H_ge_16": all(v == 5 for h, v in c11["counts"].items() if int(h) >= 16),
            "explanation": "points (5,5),(5,-6) have height 5 and (16,60),(16,-61) height 16, so N_E(10) = 3 is "
                           "the correct value; the frozen wording 'at every H' cannot hold on a grid starting at 10",
        }
        out[run] = R
    json.dump(out, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
