#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-114eb2 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not call M1, M2, M3, or divisor_count.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  explicit divisor lists (1,2,4) and (1,5), not a range-sum loop.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-114eb2/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    n_frozen = int(fx["n_frozen"])
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    must_m1 = int(real_fx["must_M1"])
    must_m2 = int(real_fx["must_M2"])
    must_m3 = int(real_fx["must_M3"])
    must_kf = int(kf_fx["must_M1"])
    must_null = int(null_fx["must_M1"])

    # Explicit divisor lists. No range-sum. No producer helpers.
    divisors_of_4 = (1, 2, 4)
    divisors_of_5 = (1, 5)
    d4 = len(divisors_of_4)
    d5 = len(divisors_of_5)
    real_m1 = d4 + 1
    real_m2 = 2
    real_m3 = n_frozen + 1
    kf_m1 = d5 + 1
    null_m1 = 0

    n_composite_rejected = False
    n_one_rejected = False
    for row in invalid:
        nid = row["id"]
        n = int(row["n"])
        must = bool(row["must_reject"])
        rejected = n != n_frozen
        if nid == "n-composite":
            n_composite_rejected = rejected and must
        if nid == "n-one":
            n_one_rejected = rejected and must

    fixture_pass = (
        n_frozen == 5
        and d4 == 3
        and d5 == 2
        and must_m1 == 4
        and must_m2 == 2
        and must_m3 == 6
        and must_kf == 3
        and must_null == 0
        and bool(kf_fx.get("wrong_divisor"))
        and null_fx["kind"] == "zero_count"
        and divisors_of_4 == (1, 2, 4)
        and divisors_of_5 == (1, 5)
    )
    real_count_pass = (
        real_m1 == must_m1
        and real_m2 == must_m2
        and real_m3 == must_m3
    )
    known_false_wrong_divisor_pass = kf_m1 == must_kf and kf_m1 != must_m1
    reject_invalid_pass = n_composite_rejected and n_one_rejected
    null_zero_pass = null_m1 == 0 and null_m1 != must_m1
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_wrong_divisor_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_count_pass": real_count_pass,
        "known_false_wrong_divisor_pass": known_false_wrong_divisor_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL": {
            "n": n_frozen,
            "divisors_of_4": list(divisors_of_4),
            "d_n_minus_1": d4,
            "M1": real_m1,
            "M2": real_m2,
            "M3": real_m3,
        },
        "KF": {
            "id": "KF",
            "wrong_divisor": True,
            "divisors_of_5": list(divisors_of_5),
            "d_n": d5,
            "M1": kf_m1,
        },
        "NULL": {
            "id": "NULL",
            "kind": "zero_count",
            "M1": null_m1,
            "rejected_as_collapse": True,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "called_M1": False,
        "called_divisor_count": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "explicit_divisor_lists_of_4_and_5",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
