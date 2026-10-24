#!/usr/bin/env python3
"""J2 recomputation for TASK-20261022-8ebef8, written before reading check.py.

Recomputes every manifest metric of EXP-CZLIFT-1a3453 from raw-result.json
rows, against the specification's metric definitions, and audits each curve
record independently:
  * threshold == ln((p-1) n) + 12  (sealed blind formula, blind/blind_summary.yaml);
  * #E(F_p) recounted by brute force from (A mod p, B mod p); n prime, n | N,
    n != p, N odd, n^2 not dividing N;
  * cm_canonical curves: j(A,B) equals the class-number-one CM j-invariant of
    the recorded discriminant label, and p splits (ordinary reduction);
  * random_naive curves: p set equals the spec's 12 primes;
  * each row: above > 0 iff max_power > threshold; spike counts even;
  * trivial bound max_power <= m = (n-1)/2 (and the same for controls), and the
    blind-zone flag m <= threshold.
Usage: python3 j2_recompute.py RUN_DIR [RUN_DIR ...] > j2_recompute_output.json
"""
from __future__ import annotations

import json
import math
import os
import sys

SPEC_RANDOM_PRIMES = [53, 71, 101, 131, 173, 211, 263, 307, 367, 421, 487, 557]
# Class-number-one CM j-invariants (standard table).
CM_J = {-3: 0, -4: 1728, -7: -3375, -8: 8000, -11: -32768, -12: 54000,
        -16: 287496, -19: -884736, -27: -12288000, -28: 16581375,
        -43: -884736000, -67: -147197952000, -163: -262537412640768000}


def is_prime(x: int) -> bool:
    if x < 2:
        return False
    i = 2
    while i * i <= x:
        if x % i == 0:
            return False
        i += 1
    return True


def count_points(a: int, b: int, p: int) -> int:
    sq = [0] * p
    for y in range(p):
        sq[y * y % p] += 1
    tot = 1
    for x in range(p):
        tot += sq[(x * x * x + a * x + b) % p]
    return tot


def kronecker_split(D: int, p: int) -> bool:
    # p odd prime not dividing D: split iff D is a nonzero square mod p
    return pow(D % p, (p - 1) // 2, p) == 1


def audit_run(run_dir: str) -> dict:
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    M = raw["metrics"]
    curves = raw["raw"]["curves"]
    issues = []
    recs = []
    for c in curves:
        p, n, N, A, B = c["p"], c["n"], c["N"], c["A"], c["B"]
        a, b = A % p, B % p
        disc = (4 * a ** 3 + 27 * b ** 2) % p
        Ncount = count_points(a, b, p)
        m = (n - 1) // 2
        if disc == 0:
            issues.append(("singular_mod_p", c["label"], p))
        if Ncount != N:
            issues.append(("point_count_mismatch", c["label"], p, N, Ncount))
        if not is_prime(n) or N % n or n == p:
            issues.append(("bad_subgroup", c["label"], p, n, N))
        if N % 2 == 0:
            issues.append(("N_even", c["label"], p, N))
        if N % (n * n) == 0:
            issues.append(("n_squared_divides_N", c["label"], p, n, N))
        if abs(N - (p + 1)) > 2 * math.sqrt(p):
            issues.append(("hasse", c["label"], p, N))
        cm = None
        if c["arm"] == "cm_canonical":
            D = int(c["label"].split("=")[1])
            jnum = 1728 * 4 * A ** 3
            jden = 4 * A ** 3 + 27 * B ** 2
            j_ok = D in CM_J and jden != 0 and jnum == CM_J[D] * jden
            split = kronecker_split(D, p) if p % abs(D) else False
            cm = {"D": D, "j_matches_cm_table": j_ok, "p_split": split}
            if not j_ok:
                issues.append(("cm_j_mismatch", c["label"], p))
            if not split:
                issues.append(("cm_p_not_split", c["label"], p))
        rows = c["rows"]
        keys = sorted((r["coord"], r["digit"]) for r in rows)
        if keys != sorted((cc, d) for cc in "xy" for d in range(5)):
            issues.append(("row_set", c["label"], p, keys))
        rowrec = []
        for r in rows:
            T = math.log((p - 1) * n) + 12.0
            if abs(T - r["threshold"]) > 1e-9:
                issues.append(("threshold_formula", c["label"], p, n, r["threshold"], T))
            for pre in ("", "shuffled_", "uniform_"):
                mp = r[pre + "max_power"]
                ab = r[pre + "above"]
                if (ab > 0) != (mp > r["threshold"]):
                    issues.append(("above_vs_max", pre, c["label"], p, r["coord"], r["digit"]))
                if ab % 2:
                    issues.append(("odd_spike_count", pre, c["label"], p, r["coord"], r["digit"], ab))
                if mp > m + 1e-9:
                    issues.append(("exceeds_trivial_bound", pre, c["label"], p, n, mp, m))
            rowrec.append({"coord": r["coord"], "digit": r["digit"],
                           "max_power": r["max_power"], "shuffled": r["shuffled_max_power"],
                           "uniform": r["uniform_max_power"], "T": r["threshold"],
                           "real_over_m": r["max_power"] / m,
                           "shuf_over_m": r["shuffled_max_power"] / m,
                           "unif_over_m": r["uniform_max_power"] / m})
        recs.append({"arm": c["arm"], "label": c["label"], "p": p, "n": n, "N": N,
                     "h": N // n, "m": m, "T": math.log((p - 1) * n) + 12.0,
                     "blind_zone_m_le_T": m <= math.log((p - 1) * n) + 12.0,
                     "cm": cm, "rows": rowrec})

    # ---- metric recomputation from rows (spec metric definitions) ----
    allrows = [(c, r) for c in curves for r in c["rows"]]
    by_digit = {}
    for cc in "xy":
        for d in range(5):
            rs = [r for c in curves for r in c["rows"] if r["coord"] == cc and r["digit"] == d]
            by_digit[f"{cc}{d}"] = {
                "n": len(rs),
                "above": sum(r["above"] for r in rs),
                "max_power_mean": sum(r["max_power"] for r in rs) / len(rs),
                "threshold_mean": sum(r["threshold"] for r in rs) / len(rs),
                "shuffled_above": sum(r["shuffled_above"] for r in rs),
                "uniform_above": sum(r["uniform_above"] for r in rs),
            }
    hi = [r for _, r in allrows if r["digit"] >= 1]
    mine = {
        "curves": len(curves),
        "curves_cm": sum(c["arm"] == "cm_canonical" for c in curves),
        "curves_random": sum(c["arm"] == "random_naive" for c in curves),
        "spikes_total": sum(r["above"] for _, r in allrows),
        "spikes_digit0": sum(r["above"] for _, r in allrows if r["digit"] == 0),
        "spikes_higher_digits": sum(r["above"] for r in hi),
        "shuffled_spikes_total": sum(r["shuffled_above"] for _, r in allrows),
        "uniform_spikes_total": sum(r["uniform_above"] for _, r in allrows),
        "max_excess_over_threshold_higher_digits": max(r["max_power"] - r["threshold"] for r in hi),
        "max_excess_shuffled__all_digits": max(r["shuffled_max_power"] - r["threshold"] for _, r in allrows),
        "max_excess_shuffled__higher_digits": max(r["shuffled_max_power"] - r["threshold"] for r in hi),
        "max_excess_uniform__all_digits": max(r["uniform_max_power"] - r["threshold"] for _, r in allrows),
        "max_excess_digit0": max(r["max_power"] - r["threshold"] for _, r in allrows if r["digit"] == 0),
        "by_digit": by_digit,
    }
    # ---- compare with recorded metrics ----
    cmp = {}
    for k in ["curves", "curves_cm", "curves_random", "spikes_total", "spikes_digit0",
              "spikes_higher_digits", "shuffled_spikes_total", "uniform_spikes_total",
              "max_excess_over_threshold_higher_digits"]:
        cmp[k] = {"recorded": M[k], "recomputed": mine[k], "equal": M[k] == mine[k]}
    cmp["max_excess_shuffled"] = {
        "recorded": M["max_excess_shuffled"],
        "equal_all_digits_def": M["max_excess_shuffled"] == mine["max_excess_shuffled__all_digits"],
        "equal_higher_digits_def": M["max_excess_shuffled"] == mine["max_excess_shuffled__higher_digits"]}
    bd_eq = all(M["by_digit"][k][f] == mine["by_digit"][k][f]
                for k in mine["by_digit"] for f in mine["by_digit"][k])
    bd_close = all(abs(M["by_digit"][k][f] - mine["by_digit"][k][f]) <= 1e-12 * max(1, abs(mine["by_digit"][k][f]))
                   for k in mine["by_digit"] for f in mine["by_digit"][k])
    cmp["by_digit_all_fields"] = {"bit_equal": bd_eq, "equal_within_1e-12": bd_close}
    cmp["random_arm_primes_equal_spec"] = sorted(c["p"] for c in curves if c["arm"] == "random_naive") == SPEC_RANDOM_PRIMES
    cmp["cm_arm_p_range_50_600"] = all(50 <= c["p"] <= 600 for c in curves if c["arm"] == "cm_canonical")
    cmp["min_n"] = min(c["n"] for c in curves)

    # success / falsification / invalidation, per this seed
    seed_eval = {
        "success_this_seed": mine["spikes_higher_digits"] == 0 and mine["shuffled_spikes_total"] == 0
                             and mine["uniform_spikes_total"] == 0,
        "falsifying_digits_this_seed": sorted({f"{r['coord']}{r['digit']}" for c in curves for r in c["rows"]
                                               if r["digit"] >= 1 and r["above"] > 0}),
        "invalid_uniform_spike": mine["uniform_spikes_total"] > 0,
        "invalid_arm_empty": mine["curves_cm"] == 0 or mine["curves_random"] == 0,
    }
    # near-miss rows, top 8 by (max - T) across real/shuffled/uniform
    near = []
    for c in curves:
        m = (c["n"] - 1) // 2
        for r in c["rows"]:
            for pre in ("", "shuffled_", "uniform_"):
                near.append((r[pre + "max_power"] - r["threshold"], pre or "real", c["arm"], c["label"],
                             c["p"], c["n"], m, r["coord"], r["digit"], r[pre + "max_power"], r["threshold"]))
    near.sort(reverse=True)
    blind = [(c["arm"], c["label"], c["p"], c["n"]) for c in curves
             if (c["n"] - 1) // 2 <= math.log((c["p"] - 1) * c["n"]) + 12.0]
    return {"run_dir": run_dir, "seed": M["seed"], "issues": issues, "comparison": cmp,
            "recomputed": mine, "seed_eval": seed_eval,
            "top_near_misses": [dict(zip(["excess", "series", "arm", "label", "p", "n", "m", "coord",
                                          "digit", "max_power", "T"], x)) for x in near[:12]],
            "curves_in_blind_zone_m_le_T": blind,
            "curves": recs}


def main(argv):
    out = [audit_run(d) for d in argv[1:]]
    # cross-seed: falsification needs the same digit spiking on both seeds
    if len(out) == 2:
        f0 = set(out[0]["seed_eval"]["falsifying_digits_this_seed"])
        f1 = set(out[1]["seed_eval"]["falsifying_digits_this_seed"])
        cross = {"success_both_seeds": all(o["seed_eval"]["success_this_seed"] for o in out),
                 "falsification_digits_on_both_seeds": sorted(f0 & f1),
                 "any_invalidation": any(o["seed_eval"]["invalid_uniform_spike"] or o["seed_eval"]["invalid_arm_empty"]
                                         for o in out)}
        out.append({"cross_seed": cross})
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv)
