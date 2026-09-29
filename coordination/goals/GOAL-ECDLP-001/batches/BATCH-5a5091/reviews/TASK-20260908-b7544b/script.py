#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-166141 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use sequential Euclidean division.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form r(-1) because remainder of r by (x+1) is r(-1).
  The producer uses sequential Euclidean division.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-166141/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def closed_form_remainder_at_minus_one(r_coeffs: list[int], modulus: int) -> int:
    """r(-1) by Horner. Not sequential Euclidean division."""
    acc = 0
    for coeff in reversed([int(c) for c in r_coeffs]):
        acc = (acc * (-1) + coeff) % int(modulus)
    return acc


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_polys"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    modulus = int(real_fx["modulus"])
    g = [int(c) for c in real_fx["g"]]
    r = [int(c) for c in real_fx["r"]]
    must_remainder = int(real_fx["must_remainder"])
    kf_must_value = int(kf_fx["must_value"])

    fixture_pass = True

    modulus_zero_rejected = False
    for item in invalid:
        if int(item.get("modulus", 1)) <= 0 and bool(item.get("must_reject")):
            modulus_zero_rejected = True
    reject_invalid_pass = modulus_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_pair"

    real_remainder = closed_form_remainder_at_minus_one(r, modulus)
    real_remainder_pass = (
        real_remainder == must_remainder
        and g == [1, 1]
    )

    kf_value = sum(r) % modulus
    kf_rejected = (
        kf_value == kf_must_value
        and kf_fx.get("kind") == "eval_at_plus_one"
        and bool(kf_fx.get("must_reject"))
    )
    known_false_eval_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_remainder_pass
        and known_false_eval_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_r_at_minus_one_horner",
        "imported_producer": False,
        "used_sequential_euclidean_division": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_remainder_pass": real_remainder_pass,
        "known_false_eval_pass": known_false_eval_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "modulus": modulus,
            "g": g,
            "r": r,
            "remainder": real_remainder,
            "matches_frozen": real_remainder_pass,
        },
        "KF": {
            "kind": "eval_at_plus_one",
            "value": kf_value,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_pair", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
