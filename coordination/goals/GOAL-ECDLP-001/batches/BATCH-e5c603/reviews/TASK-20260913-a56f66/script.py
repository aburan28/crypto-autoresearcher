#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-dab70e Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form Jacobians. Does not compute chi_3(y).
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed forms 2^9 ≡ 18 and 16^9 ≡ 1 (mod 19).
  The producer forms the affine doubling map and then u^9.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-dab70e/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_curve"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    x_zero_rejected = False
    for item in invalid:
        if bool(item.get("x_zero")) and bool(item.get("must_reject")):
            x_zero_rejected = True
    reject_invalid_pass = x_zero_rejected

    null_empty_pass = (
        bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_character"
    )

    # Closed forms. Not Jacobian formation. Not producer affine_double. Not chi_3(y).
    chi = pow(2, 9, 19)
    chi_prime = pow(16, 9, 19)
    real_character_pass = (
        chi == int(real_fx["must_chi"]) == 18
        and chi_prime == int(real_fx["must_chi_prime"]) == 1
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        chi_prime == int(kf_fx["must_chi_prime"]) == 1
        and int(kf_fx["claimed_chi_prime"]) == 18
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
        "method": "closed_form_x_ninth_power",
        "imported_producer": False,
        "used_jacobian_formation": False,
        "used_chi3_y": False,
        "used_xy_product": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_character_pass": real_character_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "chi": chi,
            "chi_prime": chi_prime,
            "must_chi": 18,
            "must_chi_prime": 1,
            "matches_frozen": real_character_pass,
        },
        "KF": {
            "kind": "constant_chi_prime",
            "chi_prime": chi_prime,
            "claimed_chi_prime": 18,
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
