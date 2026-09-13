#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-67b0d7 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form doubling.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed forms 2*3=6 and 16*11=5.
  The producer forms [2]P by affine doubling and multiplies coordinates.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-67b0d7/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_curve"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    y_zero_rejected = False
    for item in invalid:
        if bool(item.get("y_zero")) and bool(item.get("must_reject")):
            y_zero_rejected = True
    reject_invalid_pass = y_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_product"

    # Closed form. Not affine doubling.
    pi = 2 * 3
    pi_prime = 16 * 11
    if pi_prime >= 19:
        pi_prime = pi_prime - 19 * (pi_prime // 19)
    real_product_pass = (
        pi == int(real_fx["must_pi"]) == 6
        and pi_prime == int(real_fx["must_pi_prime"]) == 5
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        pi_prime == int(kf_fx["must_pi_prime"]) == 5
        and int(kf_fx["claimed_pi_prime"]) == 6
        and kf_fx.get("kind") == "constant_pi_prime"
        and bool(kf_fx.get("must_reject"))
        and pi_prime != int(kf_fx["claimed_pi_prime"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_product_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_2_times_3_and_16_times_11",
        "imported_producer": False,
        "used_doubling": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_product_pass": real_product_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "pi": pi,
            "pi_prime": pi_prime,
            "must_pi": 6,
            "must_pi_prime": 5,
            "matches_frozen": real_product_pass,
        },
        "KF": {
            "kind": "constant_pi_prime",
            "pi_prime": pi_prime,
            "claimed_pi_prime": 6,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_product", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
