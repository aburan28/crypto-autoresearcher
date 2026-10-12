"""Independent deterministic arithmetic for TASK-20260930-1f6124.

Uses only Python's standard library. No ECDLP, curve, or relation experiments.
The parameters are transcribed from the assigned handoff, not producer code.
"""

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import platform
import sys


R = 680564733841876926932320129493409985129
INPUTS = (
    "AGENTS.md",
    "coordination/review/icperf-orbit-scope-20260930/handoffs/TASK-20260930-1f6124.yaml",
)


def arctan_inverse(q, precision):
    """Alternating series, with omitted term smaller than 10^(-precision-5)."""
    x = Decimal(1) / Decimal(q)
    square = x * x
    term = x
    total = Decimal(0)
    j = 0
    tolerance = Decimal(10) ** (-precision - 5)
    while abs(term / Decimal(2 * j + 1)) > tolerance:
        total += term / Decimal(2 * j + 1)
        term = -term * square
        j += 1
    return total, j


def solve(precision):
    with localcontext() as context:
        context.prec = precision + 20
        one, two, three, six = map(Decimal, (1, 2, 3, 6))
        r = Decimal(R)
        a5, terms5 = arctan_inverse(5, context.prec)
        a239, terms239 = arctan_inverse(239, context.prec)
        pi = Decimal(16) * a5 - Decimal(4) * a239
        log_two = two.ln()
        reference = (pi * r / (Decimal(4) * Decimal(131))).sqrt()
        reference_log2 = reference.ln() / log_two
        cases = []
        for label, multiplier, k_integer in (
            ("N=4r,k=1", 4, 1),
            ("N=r,k=1", 1, 1),
            ("N=4r,k=131", 4, 131),
        ):
            n = Decimal(multiplier) * r
            k = Decimal(k_integer)

            def stationary(b):
                d = (b - one) * (b - two)
                return b * d * d - n * k * (two * b - three)

            def objective(b):
                return six * n / (k * (b - one) * (b - two)) + three * b * b / (k * k)

            asymptotic_b = (two * n * k).sqrt().sqrt()
            lo = three
            hi = two * asymptotic_b + three
            assert stationary(lo) < 0
            assert stationary(hi) > 0
            iterations = 0
            relative_target = Decimal(10) ** (-precision - 5)
            while hi - lo > lo * relative_target:
                mid = (lo + hi) / two
                assert lo < mid < hi
                if stationary(mid) < 0:
                    lo = mid
                else:
                    hi = mid
                iterations += 1
            assert stationary(lo) < 0 < stationary(hi)
            b = (lo + hi) / two
            cost = objective(b)
            binomial = b * (b - one) * (b - two) / six
            original_cost = (b / k) * n / binomial + three * (b / k) ** 2
            original_agreement = abs(original_cost / cost - one)
            assert original_agreement < Decimal(10) ** (-precision)
            approximate_cost = six * (two * n).sqrt() / (k * k.sqrt())
            ratio = cost / reference
            log2_cost = cost.ln() / log_two
            normalized_residual = stationary(b) / (n * k * (two * b - three))
            row = {
                "label": label,
                "N": str(int(n)),
                "k": k_integer,
                "B_min": str(b),
                "B_min_bracket_lower": str(lo),
                "B_min_bracket_upper": str(hi),
                "B_min_bracket_relative_width": str((hi - lo) / b),
                "bisection_iterations": iterations,
                "normalized_stationarity_residual": str(normalized_residual),
                "cost_min": str(cost),
                "log2_cost_min": str(log2_cost),
                "cost_over_reference": str(ratio),
                "log2_cost_minus_reference": str(log2_cost - reference_log2),
                "asymptotic_B_min": str(asymptotic_b),
                "asymptotic_cost_min": str(approximate_cost),
                "asymptotic_log2_cost_min": str(approximate_cost.ln() / log_two),
                "exact_minus_asymptotic_bits": str((cost / approximate_cost).ln() / log_two),
                "cost_at_B_3": str(objective(three)),
                "original_and_simplified_cost_relative_difference": str(original_agreement),
            }
            cases.append(row)
        return {
            "working_decimal_digits": context.prec,
            "requested_decimal_digits": precision,
            "pi": str(pi),
            "pi_arctan_terms": {"inverse_5": terms5, "inverse_239": terms239},
            "reference": str(reference),
            "log2_reference": str(reference_log2),
            "cases": cases,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    low = solve(80)
    high = solve(120)
    with localcontext() as context:
        context.prec = 140
        differences = []
        for a, b in zip(low["cases"], high["cases"]):
            log_difference = abs(Decimal(a["log2_cost_min"]) - Decimal(b["log2_cost_min"]))
            b_relative_difference = abs(Decimal(a["B_min"]) / Decimal(b["B_min"]) - Decimal(1))
            assert log_difference < Decimal("1e-79")
            assert b_relative_difference < Decimal("1e-79")
            differences.append({
                "label": a["label"],
                "log2_cost_absolute_difference": str(log_difference),
                "B_min_relative_difference": str(b_relative_difference),
            })
    output = {
        "task_id": "TASK-20260930-1f6124",
        "input_snapshot": "0e1804b1ec8e0f128684de4d0b876ed2a667d11b",
        "python_version": platform.python_version(),
        "interpreter": sys.executable,
        "dependencies": "Python standard library only",
        "scientific_experiments": 0,
        "source_sha256": {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in INPUTS},
        "precision_comparison": differences,
        "result": high,
    }
    with Path(args.output).open("x", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print("Python:", platform.python_version())
    print("log2 reference:", high["log2_reference"])
    for row in high["cases"]:
        print(row["label"])
        for key in ("B_min", "cost_min", "log2_cost_min", "cost_over_reference", "log2_cost_minus_reference", "exact_minus_asymptotic_bits"):
            print(" ", key + ":", row[key])
    print("Precision comparison:", json.dumps(differences))
    print("Output:", args.output)


if __name__ == "__main__":
    main()
