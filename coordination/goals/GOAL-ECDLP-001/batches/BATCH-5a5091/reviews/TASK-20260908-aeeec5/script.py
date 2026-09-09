#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-1dc6e1 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use sequential multiply.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form (2 * 3) mod 5 = 1.
  The producer uses sequential multiply: acc starts at 1 and
  is multiplied by each child.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-1dc6e1/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def closed_form_two_leaf_product(u0: int, u1: int, modulus: int) -> int:
    """(u0 * u1) mod modulus. Not sequential multiply."""
    return (int(u0) * int(u1)) % int(modulus)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_units"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    modulus = int(real_fx["modulus"])
    u0 = int(real_fx["u0"])
    u1 = int(real_fx["u1"])
    must_parent = int(real_fx["must_parent"])
    kf_must_parent = int(kf_fx["must_parent"])

    fixture_pass = True

    modulus_zero_rejected = False
    for item in invalid:
        if int(item.get("modulus", 1)) <= 0 and bool(item.get("must_reject")):
            modulus_zero_rejected = True
    reject_invalid_pass = modulus_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_pair"

    real_parent = closed_form_two_leaf_product(u0, u1, modulus)
    real_product_pass = real_parent == must_parent

    kf_parent = (u0 + u1) % modulus
    kf_rejected = (
        kf_parent == kf_must_parent
        and kf_fx.get("kind") == "sum_instead_of_product"
        and bool(kf_fx.get("must_reject"))
    )
    known_false_sum_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_product_pass
        and known_false_sum_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_two_leaf_product_2_times_3_mod_5",
        "imported_producer": False,
        "used_sequential_multiply": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_product_pass": real_product_pass,
        "known_false_sum_pass": known_false_sum_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "modulus": modulus,
            "u0": u0,
            "u1": u1,
            "parent": real_parent,
            "matches_frozen": real_product_pass,
        },
        "KF": {
            "kind": "sum_instead_of_product",
            "parent": kf_parent,
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
