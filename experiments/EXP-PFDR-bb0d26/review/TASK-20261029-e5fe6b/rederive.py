#!/usr/bin/env python3
"""Blind re-derivation of the EXP-PFDR-bb0d26 per-cell statistics (TASK-20261029-e5fe6b, joint J4).

Written from the text of experiments/EXP-PFDR-bb0d26/specification.yaml and
ledger/hypotheses/H-PFDR-727bfc.yaml only. It never imports, reads or mirrors the producer's
implementation/ or any analyze run directory. Inputs are the census job records and design.json.

Usage:
  python3 -I rederive.py <repo_root> <out_json> [--boot 2000] [--seed-tag TAG] [--quantile linear]

Choices where the specification text does not determine a quantity are marked CHOICE below
and listed in the YAML report.
"""
import argparse
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from fractions import Fraction

import numpy as np

EXP = "EXP-PFDR-bb0d26"
TASK = "TASK-20261029-e5fe6b"
NULL_REPS = 20
POWER_M = 2500
FLAG_DK, FLAG_Z = 0.10, 4.0
NULL_DK, NULL_LO, NULL_HI = 0.05, 0.90, 1.10
PLANT_K, PLANT_Z = 1.15, 4.0
CAL_SD_LO, CAL_SD_HI, CAL_MEAN = 0.75, 1.25, 0.35


def binom4(n):
    return n * (n - 1) * (n - 2) * (n - 3) // 24


def var_sum(rows, ddof):
    """Sum over curves of the per-curve variance of the listed counts (exact rational)."""
    tot = Fraction(0)
    for xs in rows:
        k = len(xs)
        s = sum(xs)
        ss = sum(x * x for x in xs)
        # sum (x - mean)^2 = ss - s^2/k
        tot += (Fraction(ss) - Fraction(s * s, k)) / (k - ddof)
    return tot


def cell_seed(tag, cell):
    h = hashlib.sha256(f"{TASK}|{tag}|{cell}".encode()).digest()
    return int.from_bytes(h[:8], "big")


def bootstrap_ratio(num, den, B, seed, method):
    """Curve-cluster percentile bootstrap of sum(num)/sum(den): resample curves with replacement."""
    num = np.asarray(num, dtype=np.float64)
    den = np.asarray(den, dtype=np.float64)
    k = len(num)
    rng = np.random.Generator(np.random.PCG64(seed))
    out = np.empty(B)
    chunk = max(1, min(B, 2_000_000 // max(k, 1)))
    i = 0
    while i < B:
        b = min(chunk, B - i)
        idx = rng.integers(0, k, size=(b, k))
        out[i:i + b] = num[idx].sum(axis=1) / den[idx].sum(axis=1)
        i += b
    lo, hi = np.percentile(out, [2.5, 97.5], method=method)
    return float(lo), float(hi)


def z_of(S, M, V, reps):
    if V <= 0:
        return None
    return float((Fraction(S) - M) / 1) / math.sqrt(float(V) * (1 + 1 / reps))


def classify(c):
    if c["curves_ok"] < c["n_curves"]:
        return "invalid"
    if not c["powered"]:
        return "inconclusive_underpowered"
    if not (c["plant_feasible_all"] and c["plant_kappa"] >= PLANT_K and c["plant_z"] is not None
            and c["plant_z"] > PLANT_Z):
        return "inconclusive_plant_not_recovered"
    if abs(c["kappa"] - 1) >= FLAG_DK and c["z"] is not None and abs(c["z"]) > FLAG_Z:
        return "flagged"
    lo, hi = c["ci95"]
    # CHOICE: "interval inside [0.90, 1.10]" read as closed: 0.90 <= lo and hi <= 1.10
    if abs(c["kappa"] - 1) < NULL_DK and NULL_LO <= lo and hi <= NULL_HI:
        return "null"
    return "intermediate"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("out")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed-tag", default="boot-v1")
    ap.add_argument("--quantile", default="linear")
    args = ap.parse_args()

    base = os.path.join(args.repo, "experiments", EXP, "runs")
    design = json.load(open(os.path.join(base, "RUN-PFDR-e44a19", "design.json")))
    jobs_path = os.path.join(base, "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")
    rep_path = os.path.join(base, "RUN-PFDR-cd03e2", "toy-rep-jobs.jsonl")

    recs = defaultdict(list)
    nonok = []
    seen = set()
    with open(jobs_path) as fh:
        for line in fh:
            if not line.strip():
                continue
            d = json.loads(line)
            key = (d["cell"], d["block"], d["c"])
            if key in seen:
                raise SystemExit(f"duplicate job key {key}")
            seen.add(key)
            if d["block"] != "main":
                raise SystemExit(f"non-main record in main census {key}")
            if d["status"] != "ok":
                nonok.append({"cell": d["cell"], "c": d["c"], "status": d["status"],
                              "T": d["gap_meta"].get("T"), "enumerated": d["gap_meta"].get("enumerated"),
                              "duplicate_skips": d["gap_meta"].get("duplicate_skips"),
                              "infinity_skips": d["gap_meta"].get("infinity_skips")})
                continue
            recs[d["cell"]].append(d)
    rep_bytes = os.path.getsize(rep_path)
    rep_records = sum(1 for line in open(rep_path) if line.strip())

    # Design re-derivation from the closed-form sizing rule (spec 'sizing').
    design_ok = True
    for t in design["toy_cells"]:
        mu = 3 * binom4(t["n"]) / (0.75 * 2 ** t["bits"])
        ncv = min(2000, max(50, math.ceil(1.5 * 2500 / mu)))
        if ncv != t["n_curves"] or abs(mu - t["mu_ref"]) > 1e-9 * mu:
            design_ok = False

    cells = []
    for t in design["toy_cells"]:
        cell = t["cell"]
        R = sorted(recs.get(cell, []), key=lambda d: d["c"])  # spec: records sorted by curve index first
        n = t["n"]
        ok_curves = len({d["c"] for d in R})
        out = {"cell": cell, "bits": t["bits"], "r": t["r"], "n": n, "n_curves": t["n_curves"],
               "curves_ok": ok_curves,
               "nonok_jobs": sum(1 for x in nonok if x["cell"] == cell)}
        if not R:
            out.update({"cls": "invalid"})
            cells.append(out)
            continue
        for d in R:
            assert len(d["null_C"]) == NULL_REPS and len(d["null_D"]) == NULL_REPS
            assert d["n"] == n and d["bits"] == t["bits"] and d["r"] == t["r"]
        S = sum(d["gap_C"] for d in R)
        Mq = sum(Fraction(sum(d["null_C"]), NULL_REPS) for d in R)          # exact
        V1 = var_sum([d["null_C"] for d in R], ddof=1)                        # CHOICE: sample variance ddof=1
        V0 = var_sum([d["null_C"] for d in R], ddof=0)                        # alternative, reported only
        M = float(Mq)
        kappa = float(Fraction(S) / Mq)
        z = z_of(S, Mq, V1, NULL_REPS)
        z_v0 = z_of(S, Mq, V0, NULL_REPS)
        # Calibration: replicate 0 against replicates 1..19 (variance factor 1 + 1/19).
        S0 = sum(d["null_C"][0] for d in R)
        M19 = sum(Fraction(sum(d["null_C"][1:]), NULL_REPS - 1) for d in R)
        V19 = var_sum([d["null_C"][1:] for d in R], ddof=1)
        z_cal = z_of(S0, M19, V19, NULL_REPS - 1)
        z_cal_v0 = z_of(S0, M19, var_sum([d["null_C"][1:] for d in R], ddof=0), NULL_REPS - 1)
        # Plant arm: same statistics with the planted counts.
        feas_all = all(d["plant_feasible"] is True for d in R)
        Sp = sum(d["plant_C"] for d in R if d["plant_C"] is not None)
        plant_kappa = float(Fraction(Sp) / Mq)
        plant_z = z_of(Sp, Mq, V1, NULL_REPS)
        # Bootstrap (curve clusters).
        seed = cell_seed(args.seed_tag, cell)
        gap = [d["gap_C"] for d in R]
        mc = [sum(d["null_C"]) / NULL_REPS for d in R]
        ci = bootstrap_ratio(gap, mc, args.boot, seed, args.quantile)
        pci = bootstrap_ratio([d["plant_C"] for d in R], mc, args.boot, seed ^ 1, args.quantile)
        # Secondary: D ratio, even/odd kappa, formula ratio.
        SD = sum(d["gap_D"] for d in R)
        MD = sum(Fraction(sum(d["null_D"]), NULL_REPS) for d in R)
        ev = [d for d in R if d["c"] % 2 == 0]
        od = [d for d in R if d["c"] % 2 == 1]
        k_even = float(Fraction(sum(d["gap_C"] for d in ev)) / sum(Fraction(sum(d["null_C"]), NULL_REPS) for d in ev))
        k_odd = float(Fraction(sum(d["gap_C"] for d in od)) / sum(Fraction(sum(d["null_C"]), NULL_REPS) for d in od))
        F = sum(Fraction(3 * binom4(n), d["p"]) for d in R)                   # sum of 3 binom(n,4)/p_c
        per_curve_ratio = [(sum(d["null_C"]) / NULL_REPS) / (3 * binom4(n) / d["p"]) for d in R]
        dup = [d["gap_meta"].get("duplicate_skips", 0) for d in R]
        out.update({
            "S": S, "M": round(M, 4), "V": round(float(V1), 4), "V_ddof0": round(float(V0), 4),
            "kappa": kappa, "ci95": [ci[0], ci[1]], "z": z, "z_Vddof0": z_v0,
            "z_cal": z_cal, "z_cal_Vddof0": z_cal_v0,
            "plant_S": Sp, "plant_kappa": plant_kappa, "plant_z": plant_z, "plant_ci95": [pci[0], pci[1]],
            "plant_feasible_all": feas_all,
            "plant_m_min": min(d["plant_m"] for d in R), "plant_m_max": max(d["plant_m"] for d in R),
            "powered": M >= POWER_M,
            "d_ratio": float(Fraction(SD) / MD),
            "kappa_even": k_even, "kappa_odd": k_odd,
            "formula_sum": float(F), "null_mean_over_formula": float(Mq / F),
            "per_curve_ratio_mean": float(np.mean(per_curve_ratio)),
            "per_curve_ratio_min": float(np.min(per_curve_ratio)),
            "per_curve_ratio_max": float(np.max(per_curve_ratio)),
            "V_over_M": float(V1 / Mq),
            "dup_skips_max": max(dup), "dup_skips_total": sum(dup),
            "boot_seed": seed,
        })
        out["cls"] = classify(out)
        cells.append(out)

    classes = defaultdict(list)
    for c in cells:
        classes[c["cls"]].append(c["cell"])
    valid = [c for c in cells if c["cls"] in ("null", "flagged", "intermediate")]
    fraction_valid = len(valid) / 45

    def gate(sel, key="z_cal"):
        zs = [c[key] for c in sel]
        if not zs:
            return {"n": 0, "mean": None, "sd": None, "pass": False}
        m = float(np.mean(zs))
        sd = float(np.std(zs, ddof=0))                      # spec: population sd
        return {"n": len(zs), "mean": m, "sd": sd,
                "pass": bool(CAL_SD_LO <= sd <= CAL_SD_HI and abs(m) <= CAL_MEAN)}

    # CHOICE (primary): powered cells = cells not invalid with measured M >= 2500.
    powered_primary = [c for c in cells if c["cls"] != "invalid" and c.get("powered")]
    # Alternative: every cell with M >= 2500 computed over its ok records, the invalid cell included.
    powered_all = [c for c in cells if c.get("powered")]
    cal = gate(powered_primary)
    cal_alt = gate(powered_all)
    cal_v0 = gate(powered_primary, "z_cal_Vddof0")
    cal_alt_v0 = gate(powered_all, "z_cal_Vddof0")

    flagged = classes.get("flagged", [])
    # Replication: survives iff same sign, |z|>3, |kappa-1|>=0.05 on the replication block.
    replication = {}
    for f in flagged:
        replication[f] = {"records": 0, "complete": False, "survives": False}

    if not cal["pass"] or fraction_valid < 0.5:
        outcome = "O-INVALID"
    elif any(v["survives"] for v in replication.values()):
        outcome = "O-STRUCT"
    elif any(not v["complete"] for v in replication.values()):
        outcome = "O-PENDING-REPLICATION"
    elif all(c["cls"] == "null" for c in valid) and fraction_valid >= 0.8:
        outcome = "O-NULL"
    else:
        outcome = "O-MIXED"
    headline = {"O-STRUCT": "FALSIFY_SCOPED", "O-INVALID": "NOT_EVIDENCE",
                "O-NULL": "SUPPORT_SCOPED"}.get(outcome, "INCONCLUSIVE")

    pw = [c for c in cells if c["cls"] != "invalid" and c.get("powered")]
    maxdk = max(pw, key=lambda c: abs(c["kappa"] - 1))
    maxz = max(pw, key=lambda c: abs(c["z"]))
    maxzc = max(pw, key=lambda c: abs(c["z_cal"]))
    min_pk = min(pw, key=lambda c: c["plant_kappa"])
    min_pz = min(pw, key=lambda c: c["plant_z"])
    widest = max(pw, key=lambda c: max(c["kappa"] - c["ci95"][0], c["ci95"][1] - c["kappa"]) / c["kappa"])
    ci_margin = min(pw, key=lambda c: min(c["ci95"][0] - NULL_LO, NULL_HI - c["ci95"][1]))

    # Secondary slope of ln kappa on log2 n per (bits, r) over valid cells with kappa > 0, >= 3 cells.
    slopes = {}
    for b in (20, 24, 28):
        for r in (1, 2, 3):
            pts = [(math.log2(c["n"]), math.log(c["kappa"])) for c in valid
                   if c["bits"] == b and c["r"] == r and c["kappa"] > 0]
            if len(pts) >= 3:
                xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
                slopes[f"b{b}-r{r}"] = float(np.polyfit(xs, ys, 1)[0])
            else:
                slopes[f"b{b}-r{r}"] = None

    result = {
        "experiment": EXP, "task": TASK, "script": "rederive.py",
        "python": sys.version.split()[0], "numpy": np.__version__,
        "bootstrap": {"resamples": args.boot, "seed_rule": f"int(sha256('{TASK}|{args.seed_tag}|<cell>')[:8], big); plant arm seed ^ 1",
                      "rng": "numpy PCG64", "percentile_method": args.quantile,
                      "unit": "curve record (gap_C, per-curve mean null_C) resampled with replacement; kappa* = sum gap*/sum mean null*"},
        "design_rederives": design_ok,
        "jobs": {"total": sum(len(v) for v in recs.values()) + len(nonok), "ok": sum(len(v) for v in recs.values()),
                 "non_ok": nonok},
        "replication_file": {"bytes": rep_bytes, "records": rep_records},
        "calibration": cal, "calibration_alt_including_invalid_cell": cal_alt,
        "calibration_Vddof0": cal_v0, "calibration_alt_Vddof0": cal_alt_v0,
        "class_counts": {k: len(v) for k, v in classes.items()},
        "classes": {k: v for k, v in classes.items() if k != "null"},
        "fraction_valid": fraction_valid, "flagged_cells": flagged, "replication": replication,
        "outcome": outcome, "headline": headline,
        "extremes_over_powered_valid": {
            "max_abs_kappa_minus_1": [maxdk["cell"], maxdk["kappa"]],
            "max_abs_z": [maxz["cell"], maxz["z"]],
            "max_abs_z_cal": [maxzc["cell"], maxzc["z_cal"]],
            "min_plant_kappa": [min_pk["cell"], min_pk["plant_kappa"]],
            "min_plant_z": [min_pz["cell"], min_pz["plant_z"]],
            "widest_rel_ci_halfwidth": [widest["cell"], widest["ci95"]],
            "smallest_ci_margin_to_band": [ci_margin["cell"], ci_margin["ci95"]],
            "count_abs_z_gt_3": sum(1 for c in pw if abs(c["z"]) > 3),
            "count_abs_z_gt_2": sum(1 for c in pw if abs(c["z"]) > 2),
        },
        "secondary_slope_ln_kappa_per_log2n": slopes,
        "cells": cells,
    }
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=0, sort_keys=False, separators=(",", ":"))
        fh.write("\n")
    print(json.dumps({k: result[k] for k in ("design_rederives", "calibration", "calibration_alt_including_invalid_cell",
                                             "calibration_Vddof0", "class_counts", "classes", "fraction_valid",
                                             "outcome", "headline", "extremes_over_powered_valid")}, indent=1))


if __name__ == "__main__":
    main()
