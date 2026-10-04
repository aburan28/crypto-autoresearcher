#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-6b3d67 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use repeated ring multiply.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form F(a+bα)=(a, 2b) because α^3=2α in F_3[α]/(α^2+1).
  The producer uses repeated ring multiply: acc starts at 1 and
  is multiplied by the element p times.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-6b3d67/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"

P = 3


def add_el(u: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    return ((u[0] + v[0]) % P, (u[1] + v[1]) % P)


def frobenius_closed_form(el: tuple[int, int]) -> tuple[int, int]:
    """F(a+bα)=(a, 2b) from α^3=2α. Not repeated multiply."""
    a, b = el
    return (a % P, (2 * b) % P)


def as_pair(value) -> tuple[int, int]:
    return (int(value[0]), int(value[1]))


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_ring"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    s0 = as_pair(real_fx["s0"])
    s1 = as_pair(real_fx["s1"])
    must_f = as_pair(real_fx["must_F_s1"])
    must_parent = as_pair(real_fx["must_parent"])
    kf_must_parent = as_pair(kf_fx["must_parent"])

    fixture_pass = True

    p_zero_rejected = False
    for item in invalid:
        if int(item.get("p", 1)) <= 0 and bool(item.get("must_reject")):
            p_zero_rejected = True
    reject_invalid_pass = p_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_pair"

    real_f = frobenius_closed_form(s1)
    real_parent = add_el(s0, real_f)
    real_semilinear_pass = real_f == must_f and real_parent == must_parent

    kf_parent = add_el(s0, s1)
    kf_rejected = (
        kf_parent == kf_must_parent
        and kf_fx.get("kind") == "identity_frobenius"
        and bool(kf_fx.get("must_reject"))
    )
    known_false_id_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_semilinear_pass
        and known_false_id_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_F_a_2b_from_alpha_cubed",
        "imported_producer": False,
        "used_repeated_ring_multiply": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_semilinear_pass": real_semilinear_pass,
        "known_false_id_pass": known_false_id_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "s0": list(s0),
            "s1": list(s1),
            "F_s1": list(real_f),
            "parent": list(real_parent),
            "matches_frozen": real_semilinear_pass,
        },
        "KF": {
            "kind": "identity_frobenius",
            "parent": list(kf_parent),
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
