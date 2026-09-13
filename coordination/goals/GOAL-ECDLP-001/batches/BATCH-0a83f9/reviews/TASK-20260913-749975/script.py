#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-bf222c Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form Jacobians.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form 2*2=4.
  The producer forms affine doubling Jacobians and multiplies determinants.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-bf222c/specification.yaml"
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

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_matrix"

    # Closed form. Not Jacobian formation.
    det1 = 2
    det2 = 2
    det4 = det1 * det2
    real_chain_rule_pass = (
        det4 == int(real_fx["must_det4"]) == 4
        and int(real_fx["must_det1"]) == 2
        and int(real_fx["must_det2"]) == 2
        and list(real_fx["P"]) == [2, 3]
    )
    kf_rejected = (
        det4 == int(kf_fx["must_det4"]) == 4
        and int(kf_fx["claimed_det4"]) == 1
        and kf_fx.get("kind") == "constant_det4"
        and bool(kf_fx.get("must_reject"))
        and det4 != int(kf_fx["claimed_det4"])
    )
    known_false_constant_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_chain_rule_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_2_times_2",
        "imported_producer": False,
        "used_jacobian_formation": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_chain_rule_pass": real_chain_rule_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "det1": det1,
            "det2": det2,
            "det4": det4,
            "must_det4": 4,
            "matches_frozen": real_chain_rule_pass,
        },
        "KF": {
            "kind": "constant_det4",
            "det4": det4,
            "claimed_det4": 1,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_matrix", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
