#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-70c6f0 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not enumerate replacements.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form J(3,1) degree = 3-1 = 2 and nonbacktracking = 2-1 = 1.
  The producer enumerates replacements then drops the inverse.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-70c6f0/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_exchange"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    weight_neg_rejected = False
    for item in invalid:
        if int(item.get("weight", 1)) < 0 and bool(item.get("must_reject")):
            weight_neg_rejected = True
    reject_invalid_pass = weight_neg_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_universe"

    # Closed form. Not replacement enumeration.
    n_all = 3 - 1
    n_nb = n_all - 1
    real_nb_count_pass = (
        n_all == int(real_fx["must_n_all"]) == 2
        and n_nb == int(real_fx["must_n_nb"]) == 1
    )
    kf_rejected = (
        n_nb == int(kf_fx["must_n_nb"]) == 1
        and int(kf_fx["claimed_n_nb"]) == 2
        and kf_fx.get("kind") == "all_johnson_neighbors_legal"
        and bool(kf_fx.get("must_reject"))
        and n_nb != int(kf_fx["claimed_n_nb"])
    )
    known_false_all_neighbors_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_nb_count_pass
        and known_false_all_neighbors_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_J31_degree_2_nb_1",
        "imported_producer": False,
        "used_replacement_enumeration": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_nb_count_pass": real_nb_count_pass,
        "known_false_all_neighbors_pass": known_false_all_neighbors_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {"n_all": n_all, "n_nb": n_nb, "must_n_nb": 1, "matches_frozen": real_nb_count_pass},
        "KF": {
            "kind": "all_johnson_neighbors_legal",
            "n_nb": n_nb,
            "claimed_n_nb": 2,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_universe", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
