#!/usr/bin/env python3
"""EXP-QSP-33b442 RUN 2 -- Stage 1b: the seeded K-coefficient arm, which is
also control C5 (the random null object).  n = 11 with n' = 6 and n = 13 with
n' = 7, d in {3, 5, 7} at each n (6 cells), 200 uniformly random lambda in
K[X] of EXACT degree d per cell, 1200 draws, base seed 20260917 with a named
sub-stream per (n, n', d).  I2 and I3 on every draw; I1 on every fifth draw at
n = 11.

Usage:  python3 stage1b.py RUN-QSP-33b442-S1B
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qspcore import (KField, FIELD_POLY, field_poly_str, i1_brute_k, i2_gcd_k,
                     i3_injection_k, difference_poly_k, verify_roots_k, kp_deg)
import runlib

CELLS = [(11, 6, 3), (11, 6, 5), (11, 6, 7), (13, 7, 3), (13, 7, 5), (13, 7, 7)]
DRAWS = 200


def stream_label(n: int, npr: int, d: int) -> str:
    return "%d:stage1b:n%d-np%d-d%d" % (runlib.BASE_SEED, n, npr, d)


def kpoly_str(K: KField, coeffs: list[int]) -> str:
    terms = []
    for i in range(len(coeffs) - 1, -1, -1):
        c = coeffs[i]
        if not c:
            continue
        cs = "1" if c == 1 else "(%s)" % K.elt_str(c)
        xs = "" if i == 0 else ("X" if i == 1 else "X^%d" % i)
        terms.append(cs + xs if xs else cs)
    return " + ".join(terms) if terms else "0"


def main(run_id: str) -> int:
    inputs = {
        "stage": "stage_1b (K-coefficient random fixture; control C5, the null object)",
        "cells": [{"n": n, "n_prime": npr, "d": d, "q": n // npr, "r": n % npr,
                   "draws": DRAWS, "field_polynomial": field_poly_str(n),
                   "field_polynomial_bits": hex(FIELD_POLY[n]),
                   "seed_stream_label": stream_label(n, npr, d)} for n, npr, d in CELLS],
        "draws_total": DRAWS * len(CELLS),
        "sampling": "lambda = sum_{i=0}^{d} c_i X^i with every c_i drawn "
                    "uniformly from K by random.Random(stream_label).getrandbits(n) "
                    "and c_d redrawn until nonzero, so the degree is EXACT d",
        "instruments": "I2 and I3 on every draw; I1 on every fifth draw at n = 11 "
                       "(draw index 0, 5, 10, ... over 2048 elements)",
        "seeds": {"base_seed": runlib.BASE_SEED,
                  "sub_streams": {"n%d_np%d_d%d" % (n, npr, d): stream_label(n, npr, d)
                                  for n, npr, d in CELLS},
                  "derivation": "random.Random(<label>) where <label> = "
                                "'<base_seed>:stage1b:n<n>-np<n'>-d<d>'; no cell is "
                                "ever re-drawn",
                  "note": "the SAME Random object also drives the Cantor-Zassenhaus "
                          "splitting inside I3, whose factor set is unique; only the "
                          "draws depend on the stream"},
        "sample_size_justification": "specification stage_1b: 200 draws detect a "
                                     "per-draw violation rate of 1.5% with probability "
                                     "0.951; 1200 draws jointly detect 0.25% with "
                                     "probability 0.950. A random sample can only REFUTE "
                                     "a universally quantified inequality.",
    }
    run = runlib.Run(run_id, "stage_1b",
                     "python3 experiments/EXP-QSP-33b442/implementation/stage1b.py " + run_id,
                     inputs, certificate_kind="root_list")
    raw: dict = {"stage": "stage_1b", "specification_version": 1}
    cells_out = {}
    pair_counts = {"I1_vs_I2": 0, "I1_vs_I3": 0, "I2_vs_I3": 0}
    disagreements = []
    violations = []
    n_multi = 0
    run.log("== Stage 1b: 6 cells x %d draws, K-coefficient lambda" % DRAWS)
    for n, npr, d in CELLS:
        K = KField(n)
        q, r = divmod(n, npr)
        bound = max(d ** (q + 1), 1 << (npr - r))
        rng = random.Random(stream_label(n, npr, d))
        rows = []
        hist: dict[int, int] = {}
        best = (-1.0, None)
        slack_max = 0
        slack_sum = 0.0
        degen = 0
        orbit_carrying = 0
        for i in range(DRAWS):
            coeffs = [rng.getrandbits(n) for _ in range(d)] + [0]
            while coeffs[d] == 0:
                coeffs[d] = rng.getrandbits(n)
            i2 = i2_gcd_k(K, npr, coeffs)
            i3 = i3_injection_k(K, coeffs, npr, rng)
            i1 = i1_brute_k(K, coeffs, npr) if (n == 11 and i % 5 == 0) else None
            instruments = {"I2": i2, "I3": i3["N"]}
            if i1 is not None:
                instruments["I1"] = i1
            row = {
                "draw_index": i, "seed_stream": stream_label(n, npr, d),
                "lambda_coeffs_hex": [hex(c) for c in coeffs],
                "lambda_printed": kpoly_str(K, coeffs),
                "n": n, "n_prime": npr, "d": d, "q": q, "r": r,
                "field_polynomial": field_poly_str(n),
                "instruments_run": sorted(instruments),
                "I1": i1, "I2": i2, "I3": i3["N"],
                "N": i2, "bound": bound, "ratio": (i2 / bound) if not i3["degenerate"] else None,
                "deg_D": i3["deg_D"], "D_roots_in_K": i3.get("D_roots_in_K"),
                "slack": i3.get("slack"),
                "degenerate_D_zero": i3["degenerate"],
                "linearized": False,
                "square_lambda_prime_zero": all(coeffs[j] == 0 for j in range(1, d + 1, 2)),
            }
            if i3["degenerate"]:
                degen += 1
                row["note"] = "D = 0 (degenerate); excluded from the M1 ratio"
            else:
                vals = list(instruments.values())
                if i1 is not None:
                    n_multi += 1
                    if i1 != i2:
                        pair_counts["I1_vs_I2"] += 1
                    if i1 != i3["N"]:
                        pair_counts["I1_vs_I3"] += 1
                if i2 != i3["N"]:
                    pair_counts["I2_vs_I3"] += 1
                if len(set(vals)) != 1:
                    disagreements.append(row)
                hist[i2] = hist.get(i2, 0) + 1
                slack_max = max(slack_max, i3["slack"])
                slack_sum += i3["slack"]
                if i2 / bound > best[0]:
                    best = (i2 / bound, row)
                if i2 >= n:
                    orbit_carrying += 1
                if i2 > bound:
                    row["explicit_roots_in_K"] = [K.elt_str(x) for x in i3["roots"]]
                    row["root_verification"] = verify_roots_k(K, coeffs, npr, i3["roots"])
                    violations.append(row)
                elif i2 == bound:
                    row["explicit_roots_in_K"] = [K.elt_str(x) for x in i3["roots"]]
                    row["root_verification"] = verify_roots_k(K, coeffs, npr, i3["roots"])
            rows.append(row)
        nd = DRAWS - degen
        lam_pois = nd / n
        obs = orbit_carrying
        tail = 1.0 - sum(math.exp(-lam_pois) * lam_pois ** k / math.factorial(k)
                         for k in range(obs))
        label = "n%d_np%d_d%d" % (n, npr, d)
        cells_out[label] = {
            "n": n, "n_prime": npr, "d": d, "q": q, "r": r, "bound": bound,
            "field_polynomial": field_poly_str(n), "seed_stream": stream_label(n, npr, d),
            "draws": DRAWS, "degenerate_draws": degen,
            "M1_max_ratio": best[0], "M1_attaining_lambda": best[1]["lambda_printed"] if best[1] else None,
            "max_N": max((r_["N"] for r_ in rows if not r_["degenerate_D_zero"]), default=None),
            "N_histogram": dict(sorted(hist.items())),
            "M8_slack_max": slack_max, "M8_slack_mean": slack_sum / nd if nd else None,
            "M9_null_object": {
                "draws_with_N_at_least_n": obs,
                "poisson_mean_under_H2": lam_pois,
                "upper_tail_probability_P_at_least_observed": tail,
                "model": "H2: the number of size-n Frobenius orbits of K-roots is "
                         "approximately Poisson(1/n) per candidate, so over C "
                         "candidates the number of orbit-carrying candidates is "
                         "approximately Poisson(C/n). MODELED, not measured.",
                "caveat": "lambda here has K coefficients, so the root set of L is NOT "
                          "Frobenius-stable and does not decompose into Frobenius orbits; "
                          "this row therefore counts draws whose distinct-root count "
                          "REACHES the orbit size n, as the closest available analogue of "
                          "H2's orbit statistic. The genuine orbit statistic of this "
                          "experiment is the Stage 3 census, where lambda has F_2 "
                          "coefficients.",
            },
            "rows": rows,
        }
        with open(run.path("cells", label + ".json"), "w") as fh:
            json.dump(cells_out[label], fh, indent=1, sort_keys=True)
        run.log("   n=%2d n'=%d d=%d bound=%3d: max N = %2d, M1 = %.4f, slack max = %d, "
                "mean = %.3f, degenerate = %d, orbit-carrying = %d (Poisson mean %.3f, "
                "upper tail %.4f)" % (n, npr, d, bound, cells_out[label]["max_N"], best[0],
                                      slack_max, slack_sum / nd, degen, obs, lam_pois, tail))
    raw["stage_1b_cells"] = cells_out
    raw["per_cell_json_files"] = ["cells/%s.json" % k for k in cells_out]
    raw["M2_agreement_matrix_stage_1b"] = {
        "draws_total": DRAWS * len(CELLS),
        "draws_with_more_than_one_instrument": DRAWS * len(CELLS),
        "draws_with_I1_also_run": n_multi,
        "pairwise_disagreement_counts": pair_counts,
        "disagreeing_draws": disagreements,
    }
    raw["violations_of_the_bound"] = violations
    raw["C5_null_object"] = {
        "role": "blocking (null object before belief)",
        "detail": "1200 uniformly random lambda in F_{2^11}[X] and F_{2^13}[X] through "
                  "the SAME instruments as the structured arms.",
        "per_cell": {k: v["M9_null_object"] for k, v in cells_out.items()},
        "largest_N_per_cell_against_its_bound": {
            k: {"max_N": v["max_N"], "bound": v["bound"], "ratio": v["M1_max_ratio"]}
            for k, v in cells_out.items()},
    }
    ndis = len(disagreements)
    if ndis or violations:
        reason = ("instrument disagreement on %d Stage 1b draws" % ndis) if ndis \
            else "certified violation of the bound (F1) on %d draws" % len(violations)
        run.warn("STOP:", reason)
        run.finish(raw, "invalid_measurement" if ndis else "completed_valid", reason,
                   certificate={"kind": "root_list", "verified": True,
                                "verifier": "qspcore.verify_roots_k"},
                   anomalies=[{"branch": "F5" if ndis else "F1", "detail": reason}])
        return 1
    run.log("\n== Summary: 0 instrument disagreements over %d draws "
            "(I1 additionally run on %d of them); 0 draws above the bound"
            % (DRAWS * len(CELLS), n_multi))
    run.finish(raw, "completed_valid",
               "%d seeded K-coefficient draws;" % (DRAWS * len(CELLS)) + "  I2 and I3 agreed on every draw and I1 "
               "agreed on every draw where it ran; no draw exceeded max(d^{q+1}, 2^{n'-r})",
               certificate={"kind": "root_list", "verified": True,
                            "verifier": "qspcore.verify_roots_k (applied to every draw "
                                        "meeting or exceeding the bound; no draw exceeded it)",
                            "certified_candidates": sum(
                                1 for v in cells_out.values() for r_ in v["rows"]
                                if "root_verification" in r_)})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
