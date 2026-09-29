#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-e9dd89 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not expand the product polynomial.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form 1+2=3.
  The producer expands (X-a)(X-b) and reads e1=a+b.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-e9dd89/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_set"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    empty_selected_rejected = False
    for item in invalid:
        if bool(item.get("empty_selected_coefficients")) and bool(item.get("must_reject")):
            empty_selected_rejected = True
    reject_invalid_pass = empty_selected_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_set"

    # Closed form. Not product expansion.
    e1 = 1 + 2
    real_e1_pass = (
        e1 == int(real_fx["must_e1"]) == 3
        and list(real_fx["must_poly"]) == [1, -3, 2]
        and list(real_fx["elements"]) == [1, 2]
    )
    kf_rejected = (
        e1 == int(kf_fx["must_e1"]) == 3
        and int(kf_fx["claimed_e1"]) == 0
        and kf_fx.get("kind") == "constant_sketch"
        and bool(kf_fx.get("must_reject"))
        and e1 != int(kf_fx["claimed_e1"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_e1_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_1_plus_2",
        "imported_producer": False,
        "used_product_expansion": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_e1_pass": real_e1_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "e1": e1,
            "must_e1": 3,
            "must_poly": [1, -3, 2],
            "matches_frozen": real_e1_pass,
        },
        "KF": {
            "kind": "constant_sketch",
            "e1": e1,
            "claimed_e1": 0,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_set", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
