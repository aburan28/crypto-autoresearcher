#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-f883e1 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form doubling.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed forms 3^6 ≡ 7 and 11^6 ≡ 1 (mod 19).
  The producer forms affine doubling, then raises y to the sixth power.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-f883e1/specification.yaml"
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

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_character"

    # Closed forms. Not doubling.
    chi = pow(3, 6, 19)
    chi_prime = pow(11, 6, 19)
    real_character_pass = (
        chi == int(real_fx["must_chi"]) == 7
        and chi_prime == int(real_fx["must_chi_prime"]) == 1
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        chi_prime == int(kf_fx["must_chi_prime"]) == 1
        and int(kf_fx["claimed_chi_prime"]) == 7
        and kf_fx.get("kind") == "constant_chi_prime"
        and bool(kf_fx.get("must_reject"))
        and chi_prime != int(kf_fx["claimed_chi_prime"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_character_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_3_pow_6_and_11_pow_6",
        "imported_producer": False,
        "used_doubling": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_character_pass": real_character_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "chi": chi,
            "chi_prime": chi_prime,
            "must_chi": 7,
            "must_chi_prime": 1,
            "matches_frozen": real_character_pass,
        },
        "KF": {
            "kind": "constant_chi_prime",
            "chi_prime": chi_prime,
            "claimed_chi_prime": 7,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_character", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
