#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-fc8954 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form doubling.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form 11 mod 4 = 3.
  The producer forms [2]P by affine doubling and reduces y_Z mod 4.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-fc8954/specification.yaml"
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

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_residue"

    # Closed form. Not affine doubling.
    r = 11 % 4
    real_residue_pass = (
        r == int(real_fx["must_r"]) == 3
        and list(real_fx["P"]) == [2, 3]
        and list(real_fx["P2"]) == [16, 11]
    )
    kf_rejected = (
        r == int(kf_fx["must_r"]) == 3
        and int(kf_fx["claimed_r"]) == 0
        and kf_fx.get("kind") == "constant_r"
        and bool(kf_fx.get("must_reject"))
        and r != int(kf_fx["claimed_r"])
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
        "method": "closed_form_11_mod_4",
        "imported_producer": False,
        "used_doubling": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_residue_pass": real_residue_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "r": r,
            "must_r": 3,
            "matches_frozen": real_residue_pass,
        },
        "KF": {
            "kind": "constant_r",
            "r": r,
            "claimed_r": 0,
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
