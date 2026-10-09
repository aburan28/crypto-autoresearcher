#!/usr/bin/env python3
"""EXP-CSIDH-f3c102 driver: 30-term class-number truncation at -83.

Default mode (--run-dir): enumerate the reduced forms of discriminant -83
twice (E1 direct listing, E2 box plus Gauss reduction), score the form
count h only on agreement, compute the exact rational 30-term truncation
L30 of L(1, chi) at chi(n) = (-83/n), enclose S = (sqrt(83)/pi) * L30 in a
rational interval of length below 1/2, apply the interval gates, and name
exactly one reading row. --self-test validates the machinery at
discriminants -59 and -107 and checks the fundamental-discriminant
discriminator; it never touches the frozen cell (p=83, N=30). The driver
records observations only; it edits no ledger record.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qforms import (  # noqa: E402
    PI_HIGH,
    PI_LOW,
    PI_PROVENANCE,
    enumerate_orbits,
    enumerate_reduced,
    interval_mul,
    interval_scale,
    is_fundamental,
    kronecker,
    kronecker_euler,
    nearest_integer_gates,
    sqrt_rational_bounds,
)

EXPERIMENT_ID = "EXP-CSIDH-f3c102"
HYPOTHESIS_ID = "H-CSIDH-f83e20"
RUN_ID = "RUN-CSIDH-9d743d"
P = 83
DISC = -83
N_TERMS = 30
A_MAX = 40
C_MAX = 400
NONFUNDAMENTAL_CONTROL = -332
SQRT_DIGITS = 6


def truncated_sum(disc: int, terms: int) -> tuple[Fraction, list[int]]:
    """Exact rational partial sum of L(1, chi) and the chi values."""
    chi = [kronecker(disc, n) for n in range(1, terms + 1)]
    total = sum(Fraction(c, n) for c, n in zip(chi, range(1, terms + 1)))
    return total, chi


def s_interval(l30: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Rational enclosure of (sqrt(P)/pi) * L30."""
    lo_sqrt, hi_sqrt = sqrt_rational_bounds(P, SQRT_DIGITS)
    sqrt_over_pi = interval_mul((lo_sqrt, hi_sqrt), (1 / PI_HIGH, 1 / PI_LOW))
    scaled = interval_scale(sqrt_over_pi, l30)
    return scaled[0], scaled[1], lo_sqrt, hi_sqrt


def measure() -> dict:
    report: dict = {
        "schema": "csidh-f3c102-truncation-v1",
        "experiment_id": EXPERIMENT_ID,
        "p": P,
        "discriminant": DISC,
        "terms": N_TERMS,
        "attack_claimed": False,
    }
    # controls that gate everything
    fundamental_83 = is_fundamental(DISC)
    fundamental_332 = is_fundamental(NONFUNDAMENTAL_CONTROL)
    fundamental_84 = is_fundamental(-84)
    # two-enumeration certificate
    e1 = enumerate_reduced(DISC)
    e2 = enumerate_orbits(DISC, A_MAX, C_MAX)
    agree = sorted(e1) == sorted(e2)
    chi1 = kronecker(DISC, 1)
    # truncation and interval
    l30, chi_values = truncated_sum(DISC, N_TERMS)
    lo, hi, lo_sqrt, hi_sqrt = s_interval(l30)
    length = hi - lo
    gate_status, r = nearest_integer_gates(lo, hi)

    h = len(e1) if agree else None
    checks = {
        "minus83_fundamental": fundamental_83,
        "minus332_nonfundamental": not fundamental_332,
        "minus84_fundamental_selfcheck": fundamental_84,
        "enumerations_agree": agree,
        "chi1_equals_1": chi1 == 1,
        "l30_is_reduced_fraction": l30.denominator > 0 and Fraction(l30.numerator, l30.denominator) == l30,
        "kronecker_implementations_agree": all(
            kronecker(DISC, n) == kronecker_euler(DISC, n) for n in range(1, N_TERMS + 1)
        ),
    }
    report.update({
        "controls": checks,
        "e1_count": len(e1),
        "e2_count": len(e2),
        "e1_forms": [list(f) for f in e1],
        "h": h,
        "chi_values": chi_values,
        "L30": {"numerator": l30.numerator, "denominator": l30.denominator},
        "sqrt_bounds": {
            "lo": f"{lo_sqrt.numerator}/{lo_sqrt.denominator}",
            "hi": f"{hi_sqrt.numerator}/{hi_sqrt.denominator}",
            "digits": SQRT_DIGITS,
        },
        "pi_bounds": {"lo": "333/106", "hi": "355/113", "provenance": PI_PROVENANCE},
        "interval": {"lo": f"{lo.numerator}/{lo.denominator}",
                     "hi": f"{hi.numerator}/{hi.denominator}"},
        "interval_length": f"{length.numerator}/{length.denominator}",
        "interval_length_below_half": length < Fraction(1, 2),
        "gate_status": gate_status,
        "r": r,
    })
    diff = abs(r - h) if (r is not None and h is not None) else None
    report["absolute_difference"] = diff

    if not all(checks.values()) or gate_status != "ok":
        row = "instrument_failure"
    elif r == h:
        row = "match"
    else:
        row = "mismatch"
    report["reading_row"] = row
    return report


def self_test() -> bool:
    """Machinery validation at other discriminants; never touches (83, 30)."""
    ok = True
    for disc in (-59, -107):
        e1 = enumerate_reduced(disc)
        e2 = enumerate_orbits(disc, A_MAX, C_MAX)
        if sorted(e1) != sorted(e2):
            print(f"E1/E2 disagree at {disc}", file=sys.stderr)
            ok = False
        for n in range(1, 31):
            if kronecker(disc, n) != kronecker_euler(disc, n):
                print(f"kronecker implementations disagree at ({disc}/{n})", file=sys.stderr)
                ok = False
        l, _ = truncated_sum(disc, N_TERMS)
        lo, hi, _lo, _hi = s_interval(l)
        status, r = nearest_integer_gates(lo, hi)
        if status != "ok":
            print(f"interval gates unexpectedly fail at {disc}: {status}", file=sys.stderr)
            ok = False
        else:
            print(f"  {disc}: machinery ok (interval gates pass; value withheld)")
    for disc, want in ((-83, True), (-332, False), (-84, True), (-4, True), (-8, True), (-12, False)):
        got = is_fundamental(disc)
        if got != want:
            print(f"is_fundamental({disc}) = {got}, want {want}", file=sys.stderr)
            ok = False
    print("self-test", "PASS" if ok else "FAIL", "(discriminants -59 and -107, discriminator checks)")
    return ok


def write_run(run_dir: Path, report: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading = {
        "reading_row": report["reading_row"],
        "h": report["h"],
        "r": report["r"],
        "absolute_difference": report["absolute_difference"],
        "interval_length_below_half": report["interval_length_below_half"],
        "gate_status": report["gate_status"],
        "enumerations_agree": report["controls"]["enumerations_agree"],
        "minus332_nonfundamental": report["controls"]["minus332_nonfundamental"],
        "chi1_equals_1": report["controls"]["chi1_equals_1"],
        "attack_claimed": False,
    }
    (run_dir / "reading.yaml").write_text(
        yaml.safe_dump(reading, sort_keys=False), encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "run_id": RUN_ID,
        "command": ["python3", "experiments/EXP-CSIDH-f3c102/implementation/run.py",
                    "--run-dir", str(run_dir)],
        "discriminant": DISC,
        "terms": N_TERMS,
        "arithmetic": "exact rationals (fractions.Fraction); no floating point",
        "enumerations": ["E1 direct reduced listing", "E2 box + Gauss reduction"],
        "box_bounds": {"a_max": A_MAX, "c_max": C_MAX},
        "pi_bounds": "333/106 < pi < 355/113 (continued-fraction convergents)",
        "nonfundamental_control": NONFUNDAMENTAL_CONTROL,
        "attack_claimed": False,
    }
    (run_dir / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    if not args.run_dir:
        parser.error("--run-dir is required unless --self-test is given")
    write_run(Path(args.run_dir), measure())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
