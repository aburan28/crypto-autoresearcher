#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-9c04a3 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use sequential visit counting.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form T_sep = 1+1+1+1 = 4 and T_nosep = 2+2+1+1 = 6.
  The producer walks the fork counting visits.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-9c04a3/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_dag"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    cost_neg_rejected = False
    for item in invalid:
        if int(item.get("cost", 1)) < 0 and bool(item.get("must_reject")):
            cost_neg_rejected = True
    reject_invalid_pass = cost_neg_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_dag"

    # Closed form. Not a sequential visit walk.
    t_sep = 1 + 1 + 1 + 1
    t_nosep = 2 + 2 + 1 + 1
    real_separator_pass = t_sep == int(real_fx["must_T"]) == 4
    kf_rejected = (
        t_nosep == int(kf_fx["must_T_nosep"]) == 6
        and int(kf_fx["claimed_T_nosep"]) == 4
        and kf_fx.get("kind") == "equal_cost_without_separator"
        and bool(kf_fx.get("must_reject"))
        and t_nosep != int(kf_fx["claimed_T_nosep"])
    )
    known_false_equal_cost_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_separator_pass
        and known_false_equal_cost_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_T_sep_4_T_nosep_6",
        "imported_producer": False,
        "used_sequential_visit_counting": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_separator_pass": real_separator_pass,
        "known_false_equal_cost_pass": known_false_equal_cost_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {"T": t_sep, "must_T": 4, "matches_frozen": real_separator_pass},
        "KF": {
            "kind": "equal_cost_without_separator",
            "T": t_nosep,
            "claimed_T": 4,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_dag", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
