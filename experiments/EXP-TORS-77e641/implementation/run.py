"""Frozen measurement for EXP-TORS-77e641.

Writes manifest.yaml, raw-result.json, and reading.yaml. Does not edit
the ledger. A crash is an infrastructure failure, not a factor-count gap.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import yaml

from ntheory import (
    discriminant,
    factor_count_with_multiplicity,
    is_square,
    monic_psi7,
    smallest_nonsquare,
    trace,
    twist_coeffs,
)

P = 23
A = 1
B = 1
P_SECONDARY = 29
NULL_SEED = 20261006
NULL_COUNT = 30


def _pair(a, b, p):
    poly, degree, lead = monic_psi7(a, b, p)
    again, degree2, lead2 = monic_psi7(a, b, p)
    return {
        "degree": degree,
        "leading_coefficient_before_monic": lead,
        "monic_leading": poly[-1] if poly else None,
        "rebuild_matches": poly == again and degree == degree2 and lead == lead2,
        "factor_count": factor_count_with_multiplicity(poly, p),
        "discriminant": discriminant(a, b, p),
        "trace": trace(a, b, p),
    }


def build_report():
    c = smallest_nonsquare(P)
    twist_a, twist_b = twist_coeffs(A, B, c, P)
    c1_a, c1_b = twist_coeffs(A, B, 1, P)
    base = _pair(A, B, P)
    twist = _pair(twist_a, twist_b, P)
    control = _pair(c1_a, c1_b, P)
    gap = abs(base["factor_count"] - twist["factor_count"])
    checks = {
        "discriminant_E_nonzero": base["discriminant"] != 0,
        "discriminant_twist_nonzero": twist["discriminant"] != 0,
        "degree_E_is_24": base["degree"] == 24,
        "degree_twist_is_24": twist["degree"] == 24,
        "degree_c1_is_24": control["degree"] == 24,
        "monic": base["monic_leading"] == 1 and twist["monic_leading"] == 1 and control["monic_leading"] == 1,
        "c_is_nonsquare": not is_square(c, P),
        "c_is_smallest_nonsquare": c == smallest_nonsquare(P),
        "c1_count_equals_I_E": control["factor_count"] == base["factor_count"],
        "trace_negates": twist["trace"] == -base["trace"],
        "rebuild_matches": base["rebuild_matches"] and twist["rebuild_matches"] and control["rebuild_matches"],
    }
    if all(checks.values()) and gap == 0:
        row = "counts_agree"
    elif all(checks.values()) and gap >= 1:
        row = "counts_differ"
    else:
        row = "instrument_failure"
    secondary = _secondary(base["factor_count"], twist["factor_count"])
    return {
        "schema": "tors-77e641-factor-count-v1",
        "experiment_id": "EXP-TORS-77e641",
        "p": P,
        "A": A,
        "B": B,
        "c": c,
        "twist_A": twist_a,
        "twist_B": twist_b,
        "I_E": base["factor_count"],
        "I_twist": twist["factor_count"],
        "I_c1": control["factor_count"],
        "degree_E": base["degree"],
        "degree_twist": twist["degree"],
        "degree_c1": control["degree"],
        "discriminant_E": base["discriminant"],
        "discriminant_twist": twist["discriminant"],
        "trace_E": base["trace"],
        "trace_twist": twist["trace"],
        "gap": gap,
        "checks": checks,
        "reading_row": row,
        "attack_claimed": False,
        "secondary_does_not_choose_row": True,
        "secondary": secondary,
    }


def _secondary(i_e, i_twist):
    c = smallest_nonsquare(P_SECONDARY)
    ta, tb = twist_coeffs(A, B, c, P_SECONDARY)
    try:
        base = _pair(A, B, P_SECONDARY)
        twist = _pair(ta, tb, P_SECONDARY)
        p29 = {
            "available": True,
            "c": c,
            "gap": abs(base["factor_count"] - twist["factor_count"]),
            "degree_E": base["degree"],
            "degree_twist": twist["degree"],
            "trace_negates": twist["trace"] == -base["trace"],
        }
    except (ValueError, RuntimeError, ZeroDivisionError) as error:
        p29 = {"available": False, "reason": str(error)}
    rng = random.Random(NULL_SEED)
    counts = []
    for _ in range(NULL_COUNT):
        coeffs = [rng.randrange(P) for _ in range(24)] + [1]
        counts.append(factor_count_with_multiplicity(coeffs, P))
    return {
        "p29": p29,
        "null_seed": NULL_SEED,
        "null_count": NULL_COUNT,
        "null_min": min(counts),
        "null_max": max(counts),
        "I_E_inside_null_range": min(counts) <= i_e <= max(counts),
        "I_twist_inside_null_range": min(counts) <= i_twist <= max(counts),
    }


def write_run(run_dir: Path, report: dict) -> None:
    # The trial harness creates the run directory before launch and writes
    # its own launch files there. This driver only adds the declared artifacts.
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = run_dir / "raw-result.json"
    reading = run_dir / "reading.yaml"
    manifest = run_dir / "manifest.yaml"
    raw.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading.write_text(
        yaml.safe_dump(
            {
                "reading_row": report["reading_row"],
                "gap": report["gap"],
                "attack_claimed": False,
                "secondary_does_not_choose_row": True,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    manifest.write_text(
        yaml.safe_dump(
            {
                "experiment_id": "EXP-TORS-77e641",
                "command": [
                    "python3",
                    "experiments/EXP-TORS-77e641/implementation/run.py",
                    "--run-dir",
                    str(run_dir),
                ],
                "p": P,
                "curve": "y^2 = x^3 + x + 1",
                "ell": 7,
                "null_seed": NULL_SEED,
                "null_count": NULL_COUNT,
                "secondary_prime": P_SECONDARY,
                "attack_claimed": False,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    write_run(Path(args.run_dir), build_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
