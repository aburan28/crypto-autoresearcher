#!/usr/bin/env python3
"""V6 steps (3)-(4): score the correction factor against the claim the V6
addendum QUOTES from IDEA-20260915-8fe0ef, and state what the run reports.

I did not open ledger/proposals/IDEA-20260915-8fe0ef.yaml. The claim scored
here is the one written out inside review-plan-addendum-V6.yaml
(`what_I_do_NOT_claim`), which is a committed plan document:

  "the correction is sqrt(2n) = 5.5x, 5.8x, 6.2x at n = 15, 17, 19, obtained
   as 0.886*sqrt(r) divided by sqrt(pi*r/(4n))"

Two separate things are scored: the FORMULA and the NUMBER.
"""
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
K = json.load(open(HERE / "v6_koblitz.json"))

rows = []
for key in ("n15", "n17", "n19"):
    n = K["curves"][key]["n"]
    r = K["curves"][key]["largest_prime_factor_r"]
    b = K["baseline_group_operations"][key]

    # the quoted formula, evaluated literally
    numerator = 0.886 * math.sqrt(r)               # negation-only baseline
    denominator = math.sqrt(math.pi * r / (4 * n))  # <tau,-1> baseline
    quoted_formula_value = numerator / denominator

    rows.append(
        {
            "cell": key,
            "n": n,
            "r": r,
            # my own derivation, from VOW's sqrt(pi/2) constant
            "mine_none_k1": b["none"]["expected_group_operations"],
            "mine_negation_k2": b["negation_only"]["expected_group_operations"],
            "mine_tau_neg_k2n": b["tau_and_negation"]["expected_group_operations"],
            "mine_factor_vs_none": b["speedup_tau_over_none"],
            "mine_factor_vs_negation": b["speedup_tau_over_negation"],
            "sqrt_2n": round(math.sqrt(2 * n), 4),
            "sqrt_n": round(math.sqrt(n), 4),
            # the quoted claim, scored
            "quoted_numerator_0886_sqrt_r": round(numerator, 2),
            "quoted_denominator_sqrt_pi_r_over_4n": round(denominator, 2),
            "quoted_formula_evaluates_to": round(quoted_formula_value, 4),
            "quoted_number_asserted": {"n15": 5.5, "n17": 5.8, "n19": 6.2}[key],
            "formula_equals_sqrt_n": abs(quoted_formula_value - math.sqrt(n)) < 1e-6,
            "asserted_number_equals_sqrt_2n": abs(
                {"n15": 5.5, "n17": 5.8, "n19": 6.2}[key] - math.sqrt(2 * n)
            ) < 0.05,
            "formula_and_number_disagree_by": round(
                {"n15": 5.5, "n17": 5.8, "n19": 6.2}[key] / quoted_formula_value, 4
            ),
            # my numerator/denominator vs the quoted ones
            "my_negation_matches_quoted_numerator": abs(
                b["negation_only"]["expected_group_operations"] - numerator
            ) < 0.5,
            "my_tau_matches_quoted_denominator": abs(
                b["tau_and_negation"]["expected_group_operations"] - denominator
            ) < 0.5,
            # the Pohlig-Hellman correction, which is a different axis entirely
            "whole_group_order": K["curves"][key]["order_from_recursion"],
            "cofactor_h": K["curves"][key]["cofactor_h"],
            "naive_sqrt_whole_group_negation_only": b[
                "naive_whole_group_negation_only"
            ]["expected_group_operations"],
            "correct_sqrt_r_negation_only": b["negation_only"][
                "expected_group_operations"
            ],
            "overstatement_from_using_E_instead_of_r": round(
                b["naive_whole_group_negation_only"]["expected_group_operations"]
                / b["negation_only"]["expected_group_operations"],
                3,
            ),
        }
    )

out = {
    "scored_rows": rows,
    "what_the_run_reports_as_a_baseline": {
        "searched": [
            "experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/manifest.yaml",
            "experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/summary.json",
            "experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/task-report.md",
            "experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/command.txt",
            "experiments/EXP-ICPERF-66fd51/specification.yaml",
        ],
        "terms": "rho, baseline, generic, pollard, vow, oorschot, koblitz, frobenius",
        "hits": (
            "manifest.yaml:93 `cnf_generic: 300` -- a timeout budget key, not a "
            "baseline; specification.yaml:151 interpretation_limits -- 'No "
            "relation-yield, linear-algebra or rho column exists in this row.'"
        ),
        "conclusion": (
            "RUN-ICPERF-305ca3 reports NO generic baseline of any kind. The "
            "frozen contract excludes a rho column explicitly. So there is no "
            "ratio between a reported baseline and a corrected one, and no "
            "comparison, ratio or verdict in the run or its summary changes "
            "when the Koblitz correction is applied: every number the run "
            "reports is a solver wall time or conflict count, or a ratio "
            "between two of them."
        ),
    },
}
json.dump(out, open(HERE / "v6_score.json", "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
