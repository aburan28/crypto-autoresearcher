#!/usr/bin/env python3
"""EXP-QSP-33b442 Stage 5 helper: extract every reported metric MECHANICALLY
from the raw-result.json files of RUN-QSP-33b442-S1/-S1B/-S2/-S3/-S4, and
compute the M7 arithmetic table in closed form.

This script does no measurement and adds no number of its own except the M7
rows, which are closed-form evaluations of the corollary and of Proposition 8
of KN-LIT-4fe9d2 and are emitted in a SEPARATE section labelled as arithmetic.
It reads nothing from analysis/qsp-ecc2k130/.

Usage:  python3 make_report.py            # writes runs/RUN-QSP-33b442-S5/metrics.json
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "..", "runs")
OUT = os.path.join(RUNS, "RUN-QSP-33b442-S5")
KAPPA = 4.876          # Rojas solver exponent, KN-LIT-4fe9d2 Remark 1
RHO_BITS = 60.9        # rho on ECC2K-130, KN-LIT-096
N131 = 131


def load(run_id: str):
    p = os.path.join(RUNS, run_id, "raw-result.json")
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def m7_table() -> dict:
    """ARITHMETIC ON (B), NOT MEASURED. beta >= n/(n + n' - r) is the exact
    corollary; alpha_beta = 1/(2 kappa beta) and the m >> 1 exponent
    1 - alpha_beta/2 are Proposition 8 of KN-LIT-4fe9d2."""
    rows = []
    for npr in range(2, N131):
        r = N131 % npr
        beta = N131 / (N131 + npr - r)
        ab = 1.0 / (2 * KAPPA * beta)
        exp_m_large = 1.0 - ab / 2.0
        rows.append({"n_prime": npr, "r": r, "beta_lower_bound": beta,
                     "alpha_beta": ab, "prop8_exponent_m_large": exp_m_large,
                     "bits": exp_m_large * N131})
    smallest = min(rows, key=lambda t: t["beta_lower_bound"])
    minexp = min(rows, key=lambda t: t["prop8_exponent_m_large"])
    minus_one = [t for t in rows if t["r"] == t["n_prime"] - 1]
    return {
        "label": "M7 -- ARITHMETIC, NOT MEASURED",
        "definition": {
            "beta_lower_bound": "n / (n + n' - r) with n = 131, r = 131 mod n' "
                                "(the EXACT corollary (B) of H-QSP-5540d7)",
            "alpha_beta": "1 / (2 kappa beta), Proposition 8 of KN-LIT-4fe9d2",
            "kappa": KAPPA,
            "kappa_source": "Rojas' solver exponent as used in Remark 1 of KN-LIT-4fe9d2",
            "prop8_exponent_m_large": "1 - alpha_beta/2, the m >> 1 form of "
                                      "Proposition 8's max(2 alpha_beta/m, "
                                      "1 - alpha_beta(1/2 - 1/m))",
            "caveat": "Proposition 8's asymptotics assume m >> 1 with m fixed, a "
                      "regime that does not exist at a concrete n where m is an "
                      "integer near n/n' (KN-LIT-4fe9d2, 'Limits of applicability'). "
                      "Every row here is a closed-form evaluation, NOT a measurement, "
                      "and none of it is evidence about (A) or (B).",
        },
        "smallest_beta_admitted_over_n_prime_2_to_130": smallest,
        "smallest_prop8_exponent": minexp,
        "ten_n_prime_with_131_equiv_minus_1": minus_one,
        "rho_comparison": {"rho_iterations_bits": RHO_BITS,
                           "rho_source": "KN-LIT-096",
                           "smallest_prop8_bits": minexp["bits"],
                           "gap_bits": minexp["bits"] - RHO_BITS},
        "all_rows": rows,
    }


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    s1, s1b, s2, s3, s4 = (load(r) for r in ("RUN-QSP-33b442-S1", "RUN-QSP-33b442-S1B",
                                             "RUN-QSP-33b442-S2B", "RUN-QSP-33b442-S3",
                                             "RUN-QSP-33b442-S4"))
    missing = [r for r, v in zip(("S1", "S1B", "S2B", "S3", "S4"), (s1, s1b, s2, s3, s4))
               if v is None]
    m: dict = {"experiment_id": "EXP-QSP-33b442", "stage": "stage_5",
               "runs_read": {"RUN-QSP-33b442-S1": s1 is not None,
                             "RUN-QSP-33b442-S1B": s1b is not None,
                             "RUN-QSP-33b442-S2B": s2 is not None,
                             "RUN-QSP-33b442-S3": s3 is not None,
                             "RUN-QSP-33b442-S4": s4 is not None},
               "runs_missing": missing,
               "extraction_note": "every value below is copied out of the named run's "
                                  "raw-result.json; nothing is recomputed and nothing "
                                  "is read from analysis/qsp-ecc2k130/."}

    if s1:
        m["M1_stage_1"] = {k: {"n": v["n"], "n_prime": v["n_prime"], "q": v["q"], "r": v["r"],
                               "max_ratio": v["M1_max_ratio"],
                               "attaining_lambda": v["M1_attaining_lambda"],
                               "max_N": v["max_N"],
                               "bound_at_attaining": v["M1_attaining_row"]["bound"],
                               "degenerate": v["degenerate_candidates"]}
                           for k, v in s1["stage_1_cells"].items()}
        m["M2"] = s1["M2_agreement_matrix"]
        m["M6_forced_fixtures"] = [
            {"control": r["control"], "n": r["n"], "n_prime": r["n_prime"],
             "lambda": r["lambda_printed"], "forced": r["forced_value"],
             "measured": r["measured_values"], "instruments": r["instruments"],
             "matches": r["matches_forced"], "bound": r["bound"],
             "attains_bound": r["attains_bound"],
             "C6": r.get("C6_proposition_2")}
            for r in s1["forced_fixtures_C1_C4"]["rows"]]
        m["stage_0_gate"] = s1["stage_0_numeric_gate"]
        m["C6_stage_1"] = {"candidates": s1["C6_linearized_cross_check"]["candidates"],
                           "disagreements": len(s1["C6_linearized_cross_check"]["disagreements"])}
        m["M8_stage_1"] = s1["tail_checks"]["slack"]
        m["tail_checks_stage_1"] = s1["tail_checks"]
    if s1b:
        m["M1_stage_1b"] = {k: {"n": v["n"], "n_prime": v["n_prime"], "d": v["d"],
                                "bound": v["bound"], "max_ratio": v["M1_max_ratio"],
                                "attaining_lambda": v["M1_attaining_lambda"],
                                "max_N": v["max_N"], "histogram": v["N_histogram"],
                                "degenerate": v["degenerate_draws"],
                                "seed_stream": v["seed_stream"]}
                            for k, v in s1b["stage_1b_cells"].items()}
        m["M2_stage_1b"] = s1b["M2_agreement_matrix_stage_1b"]
        m["M8_stage_1b"] = {k: {"max": v["M8_slack_max"], "mean": v["M8_slack_mean"]}
                            for k, v in s1b["stage_1b_cells"].items()}
        m["M9_C5"] = s1b["C5_null_object"]
    if s2:
        m["M3"] = {"totals": s2["stage_2_totals"],
                   "complete_splitter_cells": s2["M3_complete_splitter_cells"],
                   "complete_splitters": s2["M3_complete_splitters"],
                   "near_complete_count": len(s2["M3_near_complete"]),
                   "below_exact_corollary": s2["M3_below_exact_corollary"],
                   "below_conservative_corollary": s2["M3_below_conservative_corollary"],
                   "min_beta_minus_exact":
                       s2["tail_checks"]["minimum_beta_minus_exact_over_complete_splitters"],
                   "min_beta_minus_conservative":
                       s2["tail_checks"]["minimum_beta_minus_conservative_over_complete_splitters"]}
        m["M3_near_complete_rows"] = s2["M3_near_complete"]
        m["stage_2_agreement"] = s2["agreement"]
        m["stage_2_i3_skipped"] = s2["I3_skipped_above_cap"]
        m["C6_stage_2"] = {"candidates": s2["C6_linearized_cross_check"]["candidates"],
                           "disagreements": len(s2["C6_linearized_cross_check"]["disagreements"])}
        m["helper_self_test"] = s2["helper_self_test"]
        m["tail_checks_stage_2"] = s2["tail_checks"]
    if s3:
        m["M4"] = {k: {"n_prime": v["n_prime"], "q": v["q"], "r": v["r"],
                       "candidates": v["candidates"], "max_N": v["max_N"],
                       "max_ratio": v["M1_max_ratio"],
                       "attaining_lambda": v["M1_attaining_lambda"],
                       "histogram": v["N_histogram"],
                       "candidates_with_N_gt_0": v["candidates_with_N_gt_0"],
                       "certificates": v["certificates"],
                       "orbit_carrying": v["orbit_carrying_candidates"],
                       "orbit_carrying_lambdas": v["orbit_carrying_lambdas"],
                       "slack_max": v["M8_slack_max"], "slack_mean": v["M8_slack_mean"],
                       "orbit_tail": v["M9_orbit_tail"]}
                   for k, v in s3["stage_3_cells"].items()}
        m["M4_certificates_written"] = s3["certificates_written"]
        m["M4_certificate_failures"] = len(s3["certificate_reverification_failures"])
        m["tail_checks_stage_3"] = s3["tail_checks"]
    if s4:
        m["M5"] = s4["M5"]
        m["M5_above_bound"] = s4["draws_above_conjectured_bound"]
        m["M5_brute_disagreements"] = len(s4["brute_cross_check_disagreements"])

    m["M10_resources"] = {}
    for rid in ("RUN-QSP-33b442-S1", "RUN-QSP-33b442-S1B", "RUN-QSP-33b442-S2B",
                "RUN-QSP-33b442-S3", "RUN-QSP-33b442-S4"):
        mf = os.path.join(RUNS, rid, "manifest.yaml")
        if not os.path.exists(mf):
            continue
        txt = open(mf).read()
        def grab(key):
            for line in txt.splitlines():
                if line.strip().startswith(key + ":"):
                    return line.split(":", 1)[1].strip()
            return None
        m["M10_resources"][rid] = {
            "wall_seconds": grab("wall_seconds"), "cpu_seconds": grab("cpu_seconds"),
            "peak_rss_bytes": grab("peak_rss_bytes"), "workers": grab("workers"),
            "status": grab("status")}

    m["M7_arithmetic_not_measured"] = m7_table()
    m["violations_anywhere"] = {
        "stage_1": len(s1["violations_of_the_bound"]) if s1 else None,
        "stage_1b": len(s1b["violations_of_the_bound"]) if s1b else None,
        "stage_2": len(s2["violations_of_the_bound"]) if s2 else None,
        "stage_3": len(s3["violations_of_the_bound"]) if s3 else None,
    }
    with open(os.path.join(OUT, "metrics.json"), "w") as fh:
        json.dump(m, fh, indent=1, sort_keys=False)
    print("wrote", os.path.join(OUT, "metrics.json"))
    print("runs missing:", missing or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
