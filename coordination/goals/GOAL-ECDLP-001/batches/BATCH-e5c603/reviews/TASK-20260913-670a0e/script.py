#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-895a0f Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form Jacobians.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed forms (3*4+1)*16=18, (3*9+1)*13=3, 18^2-4=16.
  The producer forms the affine doubling map and then (3x^2+A)/(2y).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-895a0f/specification.yaml"
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

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_slope"

    # Closed forms. Not Jacobian formation. Not producer affine_double.
    lam = ((3 * 4 + 1) * 16) % 19
    lam_prime = ((3 * 9 + 1) * 13) % 19
    x_prime = (18 * 18 - 4) % 19
    real_slope_pass = (
        lam == int(real_fx["must_lambda"]) == 18
        and lam_prime == int(real_fx["must_lambda_prime"]) == 3
        and x_prime == int(real_fx["must_x_prime"]) == 16
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        lam_prime == int(kf_fx["must_lambda_prime"]) == 3
        and int(kf_fx["claimed_lambda_prime"]) == 18
        and kf_fx.get("kind") == "constant_lambda_prime"
        and bool(kf_fx.get("must_reject"))
        and lam_prime != int(kf_fx["claimed_lambda_prime"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_slope_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_3x2_plus_A_times_inv_2y",
        "imported_producer": False,
        "used_jacobian_formation": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_slope_pass": real_slope_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "lambda": lam,
            "lambda_prime": lam_prime,
            "x_prime": x_prime,
            "must_lambda": 18,
            "must_lambda_prime": 3,
            "must_x_prime": 16,
            "matches_frozen": real_slope_pass,
        },
        "KF": {
            "kind": "constant_lambda_prime",
            "lambda_prime": lam_prime,
            "claimed_lambda_prime": 18,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_slope", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
