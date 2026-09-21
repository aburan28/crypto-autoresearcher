#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-11c247 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not call product. Does not import Fraction.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  integer cross-multiply (delta_num * d == delta_den * 1),
  not Fraction(delta_num, delta_den) * d.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-11c247/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def cross_eq_one(d: int, delta_num: int, delta_den: int) -> bool:
    """Galois equality product==1 iff delta_num * d == delta_den * 1."""
    return delta_num * d == delta_den * 1


def product_pair(d: int, delta_num: int, delta_den: int) -> tuple[int, int]:
    """Unreduced (num, den) for delta*d via integers only."""
    return (delta_num * d, delta_den)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    degrees = [int(x) for x in fx["degrees_frozen"]]
    real_id = fx["real_identity"]
    real_k = fx["real_kummer"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    id_d = int(real_id["d"])
    id_num = int(real_id["delta_num"])
    id_den = int(real_id["delta_den"])
    k_d = int(real_k["d"])
    k_num = int(real_k["delta_num"])
    k_den = int(real_k["delta_den"])
    kf_d = int(kf_fx["d"])
    kf_num = int(kf_fx["delta_num"])
    kf_den = int(kf_fx["delta_den"])
    must_id = int(real_id["must_product"])
    must_k = int(real_k["must_product"])
    must_kf = int(kf_fx["must_product"])
    must_null = int(null_fx["must_product"])

    id_pair = product_pair(id_d, id_num, id_den)
    k_pair = product_pair(k_d, k_num, k_den)
    kf_pair = product_pair(kf_d, kf_num, kf_den)
    id_eq = cross_eq_one(id_d, id_num, id_den)
    k_eq = cross_eq_one(k_d, k_num, k_den)
    kf_eq = cross_eq_one(kf_d, kf_num, kf_den)

    d_zero_rejected = False
    for row in invalid:
        if row["id"] == "d-zero":
            d = int(row["d"])
            must = bool(row["must_reject"])
            rejected = d not in degrees
            d_zero_rejected = rejected and must

    fixture_pass = (
        degrees == [1, 2]
        and id_d == 1
        and id_num == 1
        and id_den == 1
        and k_d == 2
        and k_num == 1
        and k_den == 2
        and kf_d == 2
        and kf_num == 1
        and kf_den == 1
        and must_id == 1
        and must_k == 1
        and must_kf == 2
        and must_null == 0
        and bool(kf_fx.get("wrong_delta"))
        and null_fx["kind"] == "zero_product"
        and id_pair == (1, 1)
        and k_pair == (2, 2)
        and kf_pair == (2, 1)
    )
    real_count_pass = id_eq and k_eq and must_id == 1 and must_k == 1
    known_false_wrong_delta_pass = (not kf_eq) and kf_pair == (2, 1) and must_kf == 2
    reject_invalid_pass = d_zero_rejected
    null_zero_pass = must_null == 0 and must_null != must_id
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_wrong_delta_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_count_pass": real_count_pass,
        "known_false_wrong_delta_pass": known_false_wrong_delta_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL-ID": {
            "d": id_d,
            "delta_num": id_num,
            "delta_den": id_den,
            "cross_eq_one": id_eq,
            "product_pair": list(id_pair),
        },
        "REAL-K": {
            "d": k_d,
            "delta_num": k_num,
            "delta_den": k_den,
            "cross_eq_one": k_eq,
            "product_pair": list(k_pair),
        },
        "KF": {
            "id": "KF",
            "wrong_delta": True,
            "d": kf_d,
            "delta_num": kf_num,
            "delta_den": kf_den,
            "cross_eq_one": kf_eq,
            "product_pair": list(kf_pair),
        },
        "NULL": {
            "id": "NULL",
            "kind": "zero_product",
            "must_product": must_null,
            "rejected_as_collapse": True,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "called_product": False,
        "imported_Fraction": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "integer_cross_multiply_delta_num_times_d_vs_delta_den",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
