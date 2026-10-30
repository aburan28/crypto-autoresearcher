#!/usr/bin/env python3
"""Re-derivation of the primary metrics of EXP-PFDR-bb0d26 from specification.yaml definitions.

Imports nothing from the producer (no run.py, check.py, curve.py). Standard library only.
Arithmetic: exact rationals (fractions.Fraction) for S, M, V and every ratio; Decimal at 60 digits
for square roots; one rounding to float at the end. So the values printed here are the
mathematically exact statistics (to ~1e-50), against which both the recorded (CPython 3.11) and
the replayed (CPython 3.13) floats can be measured.

Definitions used (specification.yaml /experiment/inputs):
  sizing (l.120): n_curves = clamp(ceil(1.5*2500/mu_ref), 50, 2000), mu_ref = 3 C(n,4) / (0.75 * 2^bits)
  statistics.per_cell (l.128): S = sum_curves C(gap); M = sum of per-curve null means (20 reps);
      V = sum of per-curve null sample variances; kappa = S/M; z = (S-M)/sqrt(V(1+1/20));
      plant_kappa, plant_z the same way with the planted counts;
      z_cal = replicate 0 as pseudo-structured vs replicates 1..19, variance factor 1+1/19
  powered (l.135): M >= 2500
  cell_classes (l.137): first match of invalid, inconclusive_underpowered, inconclusive_plant_not_recovered,
      flagged, null, intermediate
  calibration_gate (l.146): over powered cells, population sd of z_cal in [0.75, 1.25], |mean| <= 0.35
  toy_reading_rules (l.150) and headline (l.160)
The bootstrap interval (l.130: 2000 resamples, seeded per cell, percentiles 2.5/97.5) is not
bit-reproducible from the specification (the per-cell seed derivation is not stated there), so this
script draws its OWN curve-cluster bootstrap with an auditor seed and reports whether the null-class
condition holds under it, and separately whether the recorded interval satisfies the condition.

Usage: blind_rederive.py EXP_DIR AUDIT_DIR    (prints JSON; writes nothing)
"""
import hashlib
import json
import math
import os
import random
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60
BITS, RANKS, NS = (20, 24, 28), (1, 2, 3), (256, 512, 1024, 2048, 4096)
REPS = 20


def dec(q: Fraction) -> Decimal:
    return Decimal(q.numerator) / Decimal(q.denominator)


def n_curves(bits, n):
    mu_ref = Fraction(3 * math.comb(n, 4)) / (Fraction(3, 4) * 2 ** bits)
    return max(50, min(2000, math.ceil(Fraction(3, 2) * 2500 / mu_ref)))


def mean_q(xs):
    return Fraction(sum(xs), len(xs))


def svar_q(xs):
    m = mean_q(xs)
    return sum((Fraction(x) - m) ** 2 for x in xs) / (len(xs) - 1)


def zstat(S, M, V, factor):
    if V <= 0:
        return None
    return (dec(Fraction(S) - M)) / (dec(V * factor)).sqrt()


def boot_ci(gC, means, cell):
    rng = random.Random(int.from_bytes(hashlib.sha256(f"auditor-blind-boot|{cell}".encode()).digest(), "big"))
    n, out = len(gC), []
    for _ in range(2000):
        idx = [rng.randrange(n) for _ in range(n)]
        m = sum(means[i] for i in idx)
        if m > 0:
            out.append(Fraction(sum(gC[i] for i in idx)) / m)
    out.sort()
    lo = out[math.floor(0.025 * len(out))]
    hi = out[math.ceil(0.975 * len(out)) - 1]
    return float(lo), float(hi)


def main():
    exp, aud = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in open(os.path.join(exp, "runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")) if l.strip()]
    design = json.load(open(os.path.join(exp, "runs/RUN-PFDR-e44a19/design.json")))["toy_cells"]
    design_nc = {c["cell"]: c["n_curves"] for c in design}
    rec_an = json.load(open(os.path.join(exp, "runs/RUN-PFDR-089edc/analysis.json")))
    rpl_an = json.load(open(os.path.join(aud, "replay/RUN-PFDR-089edc/analysis.json")))
    rec_cells = {c["cell"]: c for c in rec_an["cells"]}
    rpl_cells = {c["cell"]: c for c in rpl_an["cells"]}

    by_cell = {}
    for r in recs:
        by_cell.setdefault(r["cell"], []).append(r)

    rows, design_mismatch = [], []
    for bits in BITS:
        for rk in RANKS:
            for n in NS:
                cell = f"b{bits}-r{rk}-n{n}"
                nc = n_curves(bits, n)
                if design_nc.get(cell) != nc:
                    design_mismatch.append([cell, nc, design_nc.get(cell)])
                ok = {}
                for r in by_cell.get(cell, []):
                    if r["status"] == "ok" and 0 <= r["c"] < nc and r["c"] not in ok:
                        ok[r["c"]] = r
                row = {"cell": cell, "bits": bits, "r": rk, "n": n, "n_curves": nc, "curves": len(ok)}
                if len(ok) < nc:
                    row["cls"] = "invalid"
                    rows.append(row)
                    continue
                rs = [ok[c] for c in sorted(ok)]
                means = [mean_q(r["null_C"]) for r in rs]
                S = sum(r["gap_C"] for r in rs)
                M = sum(means)
                V = sum(svar_q(r["null_C"]) for r in rs)
                Pl = sum(r["plant_C"] for r in rs)
                kappa = Fraction(S) / M
                z = zstat(S, M, V, Fraction(21, 20))
                pk = Fraction(Pl) / M
                pz = zstat(Pl, M, V, Fraction(21, 20))
                S0 = sum(r["null_C"][0] for r in rs)
                M0 = sum(mean_q(r["null_C"][1:]) for r in rs)
                V0 = sum(svar_q(r["null_C"][1:]) for r in rs)
                zc = zstat(S0, M0, V0, Fraction(20, 19))
                feas = all(r["plant_feasible"] for r in rs)
                powered = M >= 2500
                ci = boot_ci([r["gap_C"] for r in rs], means, cell)
                planted = feas and pk >= Fraction(115, 100) and pz is not None and pz > 4
                dev = abs(kappa - 1)
                if not powered:
                    cls = "inconclusive_underpowered"
                elif not planted:
                    cls = "inconclusive_plant_not_recovered"
                elif dev >= Fraction(1, 10) and z is not None and abs(z) > 4:
                    cls = "flagged"
                elif dev < Fraction(5, 100) and 0.90 <= ci[0] and ci[1] <= 1.10:
                    cls = "null"
                else:
                    cls = "intermediate"
                rc = rec_cells[cell]
                rec_ci_null = rc["ci95"] is not None and 0.90 <= rc["ci95"][0] and rc["ci95"][1] <= 1.10
                row.update(cls=cls, S=S, M=float(M), V=float(V), kappa=float(kappa), z=float(z),
                           z_cal=zc, plant_kappa=float(pk), plant_z=float(pz), powered=powered,
                           plant_feasible_all=feas, auditor_ci95=ci, recorded_ci95=rc["ci95"],
                           recorded_ci_satisfies_null=rec_ci_null,
                           margins={"kappa_dev_to_0.05": float(Fraction(5, 100) - dev),
                                    "auditor_ci_lo_minus_0.90": ci[0] - 0.90,
                                    "1.10_minus_auditor_ci_hi": 1.10 - ci[1],
                                    "M_minus_2500": float(M - 2500),
                                    "plant_kappa_minus_1.15": float(pk - Fraction(115, 100)),
                                    "plant_z_minus_4": float(pz - 4),
                                    "4_minus_abs_z": float(4 - abs(z))})
                rows.append(row)

    zs = [r["z_cal"] for r in rows if r.get("powered") and r.get("z_cal") is not None]
    nz = len(zs)
    mean = sum(zs) / nz
    psd = (sum((x - mean) ** 2 for x in zs) / nz).sqrt()
    cal_pass = Decimal("0.75") <= psd <= Decimal("1.25") and abs(mean) <= Decimal("0.35")
    valid = [r for r in rows if r["cls"] in ("null", "flagged", "intermediate")]
    frac = Fraction(len(valid), 45)
    flagged = [r["cell"] for r in rows if r["cls"] == "flagged"]
    if not cal_pass or frac < Fraction(1, 2):
        outcome = "O-INVALID"
    elif flagged:
        outcome = "O-PENDING-REPLICATION"  # no replication records exist (toy-rep-jobs.jsonl is empty)
    elif valid and all(r["cls"] == "null" for r in valid) and frac >= Fraction(4, 5):
        outcome = "O-NULL"
    else:
        outcome = "O-MIXED"
    headline = {"O-STRUCT": "FALSIFY_SCOPED", "O-INVALID": "NOT_EVIDENCE", "O-NULL": "SUPPORT_SCOPED"}.get(
        outcome, "INCONCLUSIVE")

    # comparison against recorded (3.11) and replayed (3.13) analysis.json
    def worst(key):
        wr = wp = 0.0
        for r in rows:
            if r["cls"] == "invalid":
                continue
            exact = float(r[key]) if not isinstance(r[key], Decimal) else float(r[key])
            wr = max(wr, abs(rec_cells[r["cell"]][key] - exact))
            wp = max(wp, abs(rpl_cells[r["cell"]][key] - exact))
        return {"max_abs_err_recorded": wr, "max_abs_err_replay": wp}

    cls_mismatch = [[r["cell"], r["cls"], rec_cells[r["cell"]]["cls"]] for r in rows
                    if r["cls"] != rec_cells[r["cell"]]["cls"]]
    S_mismatch = [r["cell"] for r in rows if r["cls"] != "invalid" and r["S"] != rec_cells[r["cell"]]["S"]]
    exact_mean, exact_sd = float(mean), float(psd)
    cal_rec, cal_rpl = rec_an["calibration"], rpl_an["calibration"]
    margin_keys = rows[0]["margins"].keys() if "margins" in rows[0] else []
    min_margins = {k: min(r["margins"][k] for r in rows if "margins" in r) for k in margin_keys}
    out = {
        "design_n_curves_mismatches": design_mismatch,
        "cells": len(rows),
        "class_counts": {c: sum(r["cls"] == c for r in rows) for c in sorted({r["cls"] for r in rows})},
        "invalid_cells": [[r["cell"], r["curves"], r["n_curves"]] for r in rows if r["cls"] == "invalid"],
        "class_mismatches_vs_recorded": cls_mismatch,
        "S_integer_mismatches_vs_recorded": S_mismatch,
        "recorded_ci_fails_null_condition_in": [r["cell"] for r in rows if r["cls"] == "null"
                                                and not r["recorded_ci_satisfies_null"]],
        "calibration": {
            "n": nz, "exact_mean": exact_mean, "exact_pop_sd": exact_sd, "pass": bool(cal_pass),
            "recorded_mean": cal_rec["mean"], "replay_mean": cal_rpl["mean"],
            "recorded_mean_minus_exact": cal_rec["mean"] - exact_mean,
            "replay_mean_minus_exact": cal_rpl["mean"] - exact_mean,
            "recorded_sd": cal_rec["sd"], "replay_sd": cal_rpl["sd"],
            "recorded_sd_minus_exact": cal_rec["sd"] - exact_sd,
            "replay_sd_minus_exact": cal_rpl["sd"] - exact_sd,
            "margin_to_mean_gate_0.35": 0.35 - abs(exact_mean),
            "margin_to_sd_band": min(exact_sd - 0.75, 1.25 - exact_sd),
        },
        "fraction_valid": [frac.numerator, frac.denominator, float(frac)],
        "flagged_cells": flagged,
        "outcome": outcome,
        "headline": headline,
        "errors_vs_exact": {k: worst(k) for k in ("kappa", "z", "z_cal", "M", "V", "plant_kappa", "plant_z")},
        "min_margins_over_valid_cells": min_margins,
        "largest_abs_z": max(((r["cell"], r["z"]) for r in rows if r.get("powered")), key=lambda t: abs(t[1])),
    }
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
