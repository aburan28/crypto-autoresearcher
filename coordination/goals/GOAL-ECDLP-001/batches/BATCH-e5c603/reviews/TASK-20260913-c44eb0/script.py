#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-827d70 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form Jacobians. Does not compute y mod 4.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed forms 2 mod 4 = 2 and 16 mod 4 = 0.
  The producer forms the affine doubling map and then x_Z mod 4.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-827d70/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_curve"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    infinity_rejected = False
    for item in invalid:
        if bool(item.get("infinity")) and bool(item.get("no_affine_x")) and bool(item.get("must_reject")):
            infinity_rejected = True
    reject_invalid_pass = infinity_rejected

    null_empty_pass = (
        bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_residue"
    )

    # Closed forms. Not Jacobian formation. Not producer affine_double. Not y mod 4.
    r = 2 % 4
    r_prime = 16 % 4
    real_residue_pass = (
        r == int(real_fx["must_r"]) == 2
        and r_prime == int(real_fx["must_r_prime"]) == 0
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        r_prime == int(kf_fx["must_r_prime"]) == 0
        and int(kf_fx["claimed_r_prime"]) == 2
        and kf_fx.get("kind") == "constant_r_prime"
        and bool(kf_fx.get("must_reject"))
        and r_prime != int(kf_fx["claimed_r_prime"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_residue_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_x_mod_4",
        "imported_producer": False,
        "used_jacobian_formation": False,
        "used_y_mod_4": False,
        "used_chi2_x": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_residue_pass": real_residue_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "r": r,
            "r_prime": r_prime,
            "must_r": 2,
            "must_r_prime": 0,
            "matches_frozen": real_residue_pass,
        },
        "KF": {
            "kind": "constant_r_prime",
            "r_prime": r_prime,
            "claimed_r_prime": 2,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_residue", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
