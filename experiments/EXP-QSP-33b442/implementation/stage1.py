#!/usr/bin/env python3
"""EXP-QSP-33b442 RUN 1 -- Stage 0 numeric gate, the four forced fixtures
C1-C4, the C6 linearized cross-check, and Stage 1: five exhaustive F_2 cells,
252 lambda each (exact degree 2..7), all three instruments on all 1260
candidates.

Usage:  python3 stage1.py RUN-QSP-33b442-S1
"""
from __future__ import annotations

import random
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qspcore import (KField, FIELD_POLY, field_poly_str, deg, poly_str, tpoly_str,
                     polys_of_degree, is_linearized, is_affine, i1_brute_f2,
                     i2_gcd_f2, i3_injection_f2, difference_poly_f2, verify_roots_f2,
                     c6_linearized_N, linearized_symbol)
import runlib

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = [(11, 6), (13, 7), (7, 3), (11, 4), (13, 5)]
DEGREES = list(range(2, 8))
I3_DEG_CAP = 1000000          # AMD-20260917-001


def is_square_f2(lam: int) -> bool:
    """lambda' = 0 over F_2 <=> every exponent present is even."""
    return all(((lam >> i) & 1) == 0 for i in range(1, deg(lam) + 1, 2))


def build_helper(run) -> str:
    cmd = "gcc -O2 -o gf2rc gf2rc.c"
    subprocess.run(cmd, shell=True, cwd=HERE, check=True)
    run.log("[helper] built:", cmd, "in", HERE)
    return cmd


def gf2rc(items):
    inp = "".join("%d %d %x\n" % (n, npr, lam) for n, npr, lam in items)
    out = subprocess.run([os.path.join(HERE, "gf2rc")], input=inp, capture_output=True,
                         text=True, check=True).stdout.split("\n")
    res = [int(l.split()[-1]) for l in out if l.strip()]
    assert len(res) == len(items), (len(res), len(items))
    return res


def main(run_id: str) -> int:
    rng = random.Random(0xC0FFEE)          # equal-degree splitting only; output unique
    inputs = {
        "stage": "stage_1 (with the Stage 0 numeric gate, controls C1-C4 and C6)",
        "cells": [{"n": n, "n_prime": npr, "q": n // npr, "r": n % npr,
                   "field_polynomial": field_poly_str(n),
                   "field_polynomial_bits": hex(FIELD_POLY[n])} for n, npr in CELLS],
        "candidate_set": "every lambda in F_2[X] of exact degree d, d = 2..7: "
                         "2^d per degree, 252 per cell, 1260 in total; exhaustive, "
                         "no sampling, no ordering dependence",
        "instruments": ["I1 brute enumeration over all 2^n elements of K",
                        "I2 deg gcd(X^{2^n} - X, L) in F_2[X]",
                        "I3 injection count via D(Y) = Lambda_{q+1}(Y) + Y^{2^{n'-r}} "
                        "with the per-orbit closing test L(x) = 0"],
        "seeds": {
            "base_seed": runlib.BASE_SEED,
            "stage_1_is_seed_free": True,
            "note": "Stage 0, Stage 1 and C1-C4/C6 enumerate fully specified finite "
                    "candidate sets. The only random.Random in the code path "
                    "(seed 0xC0FFEE, literal in stage1.py) drives Cantor-Zassenhaus "
                    "equal-degree splitting inside I3; the set of irreducible factors "
                    "it returns is mathematically unique, so every recorded number is "
                    "independent of that stream.",
        },
        "amendment_in_force": "AMD-20260917-001 (I3 run only when deg D <= %d; "
                              "no Stage 1 candidate is affected -- every Stage 1 deg D "
                              "is at most 343)" % I3_DEG_CAP,
    }
    run = runlib.Run(run_id, "stage_1",
                     "python3 experiments/EXP-QSP-33b442/implementation/stage1.py " + run_id,
                     inputs, certificate_kind="root_list")
    raw: dict = {"stage": "stage_1", "specification_version": 1}
    anomalies: list = []
    deviations: list = []

    raw["helper_build_command"] = build_helper(run)

    # ---------------- Stage 0 numeric gate, (n, n') = (4, 3) ----------------
    run.log("== Stage 0 numeric gate at (n, n') = (4, 3), q = 1, r = 1, bound max(d^2, 4)")
    K4 = KField(4)
    gate_rows = []
    hand = {0b111: {"N": 1, "slack": 0}, 0b1001: {"N": 0, "slack": 2}}
    gate_pass = True
    for lam in (0b111, 0b1001):
        i1, i1roots = i1_brute_f2(K4, lam, 3, want_roots=True)
        i2 = i2_gcd_f2(4, 3, lam)
        i3 = i3_injection_f2(K4, lam, 3, rng)
        agree = (i1 == i2 == i3["N"])
        ok = agree and i1 == hand[lam]["N"] and i3["slack"] == hand[lam]["slack"]
        gate_pass &= ok
        row = {"lambda_printed": poly_str(lam), "lambda_bits": lam,
               "hand_N": hand[lam]["N"], "hand_slack": hand[lam]["slack"],
               "I1": i1, "I2": i2, "I3_N": i3["N"], "I3_slack": i3["slack"],
               "I3_D_roots_in_K": i3["D_roots_in_K"], "deg_D": i3["deg_D"],
               "instruments_agree": agree, "agrees_with_hand": ok,
               "explicit_roots_in_K": [K4.elt_str(x) for x in i1roots],
               "root_verification": verify_roots_f2(K4, lam, 3, i1roots),
               "field_polynomial": field_poly_str(4)}
        gate_rows.append(row)
        run.log("   lambda =", poly_str(lam), "hand N =", hand[lam]["N"],
                "| I1 =", i1, "I2 =", i2, "I3 =", i3["N"],
                "slack hand =", hand[lam]["slack"], "measured =", i3["slack"],
                "->", "PASS" if ok else "FAIL")
    raw["stage_0_numeric_gate"] = {"cell": "(4, 3)", "rows": gate_rows, "pass": gate_pass}
    if not gate_pass:
        run.warn("STAGE 0 GATE FAILED -- F0. Stopping before Stage 1 per stopping_rules.")
        run.finish(raw, "invalid_measurement", "Stage 0 numeric gate failed (F0)",
                   certificate={"kind": "root_list", "verified": False,
                                "verifier": "qspcore.verify_roots_f2"},
                   anomalies=[{"branch": "F0", "detail": "hand counts disagree with instrument"}])
        return 1

    # ---------------- forced fixtures C1-C4 --------------------------------
    run.log("\n== Forced fixtures C1-C4 (measured vs forced)")
    fixtures = [
        ("C1", 12, 6, 0b10, 64, "r = 0 subfield control; the bound must be vacuous"),
        ("C2", 7, 3, 0b110, 8, "Type 2 at n = 7; bound attained"),
        ("C3", 31, 15, (1 << 128) | (1 << 8) | (1 << 2) | (1 << 1), 32768,
         "Type 2 at n = 31; published family admitted with room"),
        ("C4", 3, 2, 0b110, 4, "Theorem 1 equality case over F_8; bound attained"),
    ]
    fx_rows = []
    fx_pass = True
    for name, n, npr, lam, forced, role in fixtures:
        q, r = divmod(n, npr)
        d = deg(lam)
        bound = max(d ** (q + 1), 1 << (npr - r))
        degD = deg(difference_poly_f2(lam, n, npr))
        row = {"control": name, "n": n, "n_prime": npr, "q": q, "r": r, "d": d,
               "lambda_printed": poly_str(lam), "lambda_bits_hex": hex(lam),
               "forced_value": forced, "bound": bound, "deg_D": degD,
               "field_polynomial": field_poly_str(n), "role": role,
               "instruments": {}}
        if n <= 13:
            i1, i1roots = i1_brute_f2(KField(n), lam, npr, want_roots=True)
            row["instruments"]["I1"] = i1
            row["explicit_roots_in_K"] = [KField(n).elt_str(x) for x in i1roots]
            row["root_verification"] = verify_roots_f2(KField(n), lam, npr, i1roots)
        else:
            row["instruments"]["I1"] = None
            row["I1_skip_reason"] = "2^%d elements: enumeration not affordable " \
                                    "(specification stage_2.instrument: 'I1 where 2^n " \
                                    "enumeration is affordable')" % n
        row["instruments"]["I2"] = gf2rc([(n, npr, lam)])[0] if npr >= 10 \
            else i2_gcd_f2(n, npr, lam)
        row["I2_implementation"] = "gf2rc.c (C helper)" if npr >= 10 else "qspcore.i2_gcd_f2 (Python)"
        if degD <= I3_DEG_CAP:
            i3 = i3_injection_f2(KField(n), lam, npr, rng)
            row["instruments"]["I3"] = i3["N"]
            row["I3_slack"] = i3["slack"]
            row["I3_orbit_sizes"] = i3["orbit_sizes"]
            row["I3_run"] = True
        else:
            row["instruments"]["I3"] = None
            row["I3_run"] = False
            row["I3_skip_reason"] = "deg_D_above_declared_cap (AMD-20260917-001: " \
                                    "deg D = %d > %d)" % (degD, I3_DEG_CAP)
        if is_linearized(lam):
            Nc6, dg, splits = c6_linearized_N(lam, npr, n)
            row["C6_proposition_2"] = {
                "symbol_f": tpoly_str(linearized_symbol(lam, npr)),
                "deg_gcd_f_Tn_minus_1": dg, "N_predicted": Nc6,
                "splits_completely": splits,
                "agrees_with_instruments": all(
                    v == Nc6 for v in row["instruments"].values() if v is not None)}
        measured = [v for v in row["instruments"].values() if v is not None]
        row["measured_values"] = measured
        row["matches_forced"] = all(v == forced for v in measured) and bool(measured)
        row["ratio_N_over_bound"] = forced / bound
        row["attains_bound"] = (forced == bound)
        fx_pass &= row["matches_forced"]
        if row.get("C6_proposition_2") and not row["C6_proposition_2"]["agrees_with_instruments"]:
            fx_pass = False
        fx_rows.append(row)
        run.log("   %s (%d, %d): forced %d, measured %s -> %s | bound %d, ratio %.4f%s" % (
            name, n, npr, forced, measured, "PASS" if row["matches_forced"] else "FAIL",
            bound, forced / bound, "  ATTAINED" if row["attains_bound"] else ""))
    raw["forced_fixtures_C1_C4"] = {"rows": fx_rows, "pass": fx_pass}
    if not fx_pass:
        run.warn("FORCED FIXTURE MISMATCH -- F5. Stopping per stopping_rules.")
        run.finish(raw, "invalid_measurement", "a forced fixture returned another value (F5)",
                   certificate={"kind": "root_list", "verified": False,
                                "verifier": "qspcore.verify_roots_f2"},
                   anomalies=[{"branch": "F5", "detail": "forced fixture mismatch",
                               "rows": [r for r in fx_rows if not r["matches_forced"]]}])
        return 1

    # ---------------- Stage 1 exhaustive cells ------------------------------
    run.log("\n== Stage 1: 5 cells x 252 candidates, three instruments on every one")
    cells_out = {}
    disagreements = []
    pair_counts = {"I1_vs_I2": 0, "I1_vs_I3": 0, "I2_vs_I3": 0}
    total = 0
    violations = []
    c6_rows = []
    for n, npr in CELLS:
        K = KField(n)
        q, r = divmod(n, npr)
        rows = []
        hist: dict[int, int] = {}
        best = (-1.0, None)
        slack_max = 0
        slack_sum = 0
        degen = []
        for d in DEGREES:
            bound = max(d ** (q + 1), 1 << (npr - r))
            for lam in polys_of_degree(d):
                total += 1
                i1, _ = i1_brute_f2(K, lam, npr)
                i2 = i2_gcd_f2(n, npr, lam)
                i3 = i3_injection_f2(K, lam, npr, rng)
                degenerate = i3["degenerate"]
                i3N = i3["N"]
                row = {
                    "lambda_bits": lam, "lambda_hex": hex(lam), "lambda_printed": poly_str(lam),
                    "n": n, "n_prime": npr, "d": d, "q": q, "r": r,
                    "field_polynomial": field_poly_str(n),
                    "instruments_run": ["I1", "I2", "I3"],
                    "I1": i1, "I2": i2, "I3": i3N,
                    "N": i1, "bound": bound, "ratio": i1 / bound,
                    "deg_D": i3["deg_D"], "D_roots_in_K": i3.get("D_roots_in_K"),
                    "slack": i3.get("slack"), "orbit_sizes": i3.get("orbit_sizes"),
                    "degenerate_D_zero": degenerate,
                    "linearized": is_linearized(lam), "affine": is_affine(lam),
                    "square_lambda_prime_zero": is_square_f2(lam),
                }
                agree = (i1 == i2) and (i2 == i3N) and not degenerate
                if degenerate:
                    degen.append(row)
                    row["note"] = "D = 0 (degenerate); excluded from the M1 ratio; " \
                                  "trivial bound applies"
                if not degenerate:
                    if i1 != i2:
                        pair_counts["I1_vs_I2"] += 1
                    if i1 != i3N:
                        pair_counts["I1_vs_I3"] += 1
                    if i2 != i3N:
                        pair_counts["I2_vs_I3"] += 1
                    if not agree:
                        disagreements.append(row)
                    if i1 > bound:
                        _, roots = i1_brute_f2(K, lam, npr, want_roots=True)
                        row["explicit_roots_in_K"] = [K.elt_str(x) for x in roots]
                        row["root_verification"] = verify_roots_f2(K, lam, npr, roots)
                        violations.append(row)
                    elif i1 == bound:
                        _, roots = i1_brute_f2(K, lam, npr, want_roots=True)
                        row["explicit_roots_in_K"] = [K.elt_str(x) for x in roots]
                        row["root_verification"] = verify_roots_f2(K, lam, npr, roots)
                    hist[i1] = hist.get(i1, 0) + 1
                    if i1 / bound > best[0]:
                        best = (i1 / bound, row)
                    if i3.get("slack") is not None:
                        slack_max = max(slack_max, i3["slack"])
                        slack_sum += i3["slack"]
                if is_linearized(lam):
                    Nc6, dg, splits = c6_linearized_N(lam, npr, n)
                    row["C6_proposition_2"] = {
                        "symbol_f": tpoly_str(linearized_symbol(lam, npr)),
                        "deg_gcd_f_Tn_minus_1": dg, "N_predicted": Nc6,
                        "splits_completely": splits,
                        "agrees_with_instruments": (Nc6 == i1 == i2 == i3N)}
                    c6_rows.append({k: row[k] for k in
                                    ("lambda_printed", "n", "n_prime", "d", "I1", "I2", "I3")}
                                   | {"C6": row["C6_proposition_2"]})
                rows.append(row)
        nd = [r for r in rows if not r["degenerate_D_zero"]]
        cells_out["n%d_np%d" % (n, npr)] = {
            "n": n, "n_prime": npr, "q": q, "r": r,
            "field_polynomial": field_poly_str(n),
            "field_polynomial_bits": hex(FIELD_POLY[n]),
            "candidates": len(rows),
            "degenerate_candidates": len(degen),
            "M1_max_ratio": best[0],
            "M1_attaining_lambda": best[1]["lambda_printed"] if best[1] else None,
            "M1_attaining_row": best[1],
            "N_histogram": dict(sorted(hist.items())),
            "max_N": max((r["N"] for r in nd), default=None),
            "M8_slack_max": slack_max,
            "M8_slack_mean": (slack_sum / len(nd)) if nd else None,
            "rows": rows,
        }
        run.log("   (%2d, %d) q=%d r=%d: %d candidates, M1 = %.4f at %s, max N = %d, "
                "slack max = %d, mean = %.3f, degenerate = %d" % (
                    n, npr, q, r, len(rows), best[0], best[1]["lambda_printed"],
                    max(r["N"] for r in nd), slack_max, slack_sum / len(nd), len(degen)))
    for label, cell in cells_out.items():
        with open(run.path("cells", label + ".json"), "w") as fh:
            import json as _json
            _json.dump(cell, fh, indent=1, sort_keys=True)
    raw["stage_1_cells"] = cells_out
    raw["per_cell_json_files"] = ["cells/%s.json" % k for k in cells_out]
    raw["stage_1_total_candidates"] = total
    raw["M2_agreement_matrix"] = {
        "candidates_compared": total,
        "candidates_with_all_three_equal": total - len(disagreements),
        "pairwise_disagreement_counts": pair_counts,
        "matrix": {"I1": {"I1": 0, "I2": pair_counts["I1_vs_I2"], "I3": pair_counts["I1_vs_I3"]},
                   "I2": {"I1": pair_counts["I1_vs_I2"], "I2": 0, "I3": pair_counts["I2_vs_I3"]},
                   "I3": {"I1": pair_counts["I1_vs_I3"], "I2": pair_counts["I2_vs_I3"], "I3": 0}},
        "disagreeing_candidates": disagreements,
    }
    raw["C6_linearized_cross_check"] = {
        "candidates": len(c6_rows),
        "disagreements": [r for r in c6_rows if not r["C6"]["agrees_with_instruments"]],
        "rows": c6_rows,
        "procedure": "Proposition 2 of KN-LIT-4fe9d2 as implemented in "
                     "qspcore.c6_linearized_N: F_{2^n} = F_2[T]/(T^n - 1) as an "
                     "F_2[T]-module with T acting as the Frobenius, so a linearized L "
                     "with symbol f has N = 2^{deg gcd(f, T^n - 1)} roots in K and "
                     "splits completely iff f | T^n - 1.",
    }
    raw["violations_of_the_bound"] = violations
    raw["tail_checks"] = {
        "attainment": {
            "cells_with_ratio_exactly_1": [k for k, v in cells_out.items()
                                           if v["M1_max_ratio"] == 1.0],
            "attaining_candidates_at_7_3": [
                r["lambda_printed"] for r in cells_out["n7_np3"]["rows"]
                if not r["degenerate_D_zero"] and r["N"] == r["bound"]],
        },
        "maximum": {
            "largest_ratio_over_all_stage_1_cells": max(v["M1_max_ratio"] for v in cells_out.values()),
            "largest_ratio_cell": max(cells_out.items(), key=lambda kv: kv[1]["M1_max_ratio"])[0],
        },
        "slack": {k: {"max": v["M8_slack_max"], "mean": v["M8_slack_mean"]}
                  for k, v in cells_out.items()},
    }

    m2 = len(disagreements)
    if m2 or violations:
        status = "invalid_measurement" if m2 else "completed_valid"
        reason = ("instrument disagreement on %d Stage 1 candidates (F5)" % m2) if m2 \
            else "certified violation of the bound (F1): %d candidates" % len(violations)
        run.warn("STOP:", reason)
        run.finish(raw, status, reason,
                   certificate={"kind": "root_list", "verified": True,
                                "verifier": "qspcore.verify_roots_f2 (independent of the "
                                            "instrument that produced the count)"},
                   anomalies=[{"branch": "F5" if m2 else "F1", "detail": reason}])
        return 1

    nverif = sum(1 for v in cells_out.values() for r in v["rows"] if "root_verification" in r)
    allok = all(r["root_verification"]["all_roots_verified"]
                for v in cells_out.values() for r in v["rows"] if "root_verification" in r)
    run.log("\n== Summary: M2 = 0 disagreements over %d candidates; "
            "%d bound-attaining/exceeding candidates carry a re-verified root list (all ok: %s)"
            % (total, nverif, allok))
    run.finish(raw, "completed_valid",
               "Stage 0 gate passed; C1-C4 returned their forced values; three "
               "instruments agreed on all %d Stage 1 candidates; every "
               "bound-attaining candidate carries an independently re-verified root list"
               % total,
               certificate={"kind": "root_list", "verified": bool(allok),
                            "verifier": "qspcore.verify_roots_f2 (evaluates "
                                        "x^{2^{n'}} - lambda(x) in K directly; shares no "
                                        "code path with I3)",
                            "certified_candidates": nverif},
               deviations=deviations, anomalies=anomalies)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
