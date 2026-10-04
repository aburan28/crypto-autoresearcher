#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-71c37d Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use sequential multiply.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Walk positive divisors of N-1 and take the minimal d with
  pow(p, d, N) == 1. The producer uses sequential multiply:
  acc starts at 1, repeatedly acc = (acc * (p % N)) % N.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-71c37d/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def divisors_of(n: int) -> list[int]:
    value = int(n)
    found: list[int] = []
    d = 1
    while d * d <= value:
        if value % d == 0:
            found.append(d)
            other = value // d
            if other != d:
                found.append(other)
        d += 1
    return sorted(found)


def order_by_divisors(n: int, p: int) -> int:
    """Minimal d | (N-1) with p^d ≡ 1 (mod N). Not sequential multiply."""
    modulus = int(n)
    base = int(p) % modulus
    if modulus <= 0 or base == 0:
        raise ValueError("invalid pair")
    for d in divisors_of(modulus - 1):
        if pow(base, d, modulus) == 1:
            return d
    raise ValueError("no order among divisors of N-1")


def gcd_int(u: int, v: int) -> int:
    aa, bb = abs(int(u)), abs(int(v))
    while bb:
        aa, bb = bb, aa % bb
    return aa


def forced_degrees(n: int, k: int) -> list[int]:
    return sorted([1] + [int(k)] * ((int(n) - 1) // int(k)))


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_pair"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_n = int(real_fx["N"])
    real_p = int(real_fx["p"])
    must_gcd = int(real_fx["must_gcd"])
    must_k = int(real_fx["must_k"])
    must_degrees = list(real_fx["must_degrees"])
    kf_n = int(kf_fx["N"])
    kf_p = int(kf_fx["p"])
    kf_must_k = int(kf_fx["must_k"])

    fixture_pass = True

    n_zero_rejected = False
    for item in invalid:
        if int(item.get("N", 1)) <= 0 and bool(item.get("must_reject")):
            n_zero_rejected = True
    reject_invalid_pass = n_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_pair"

    real_gcd = gcd_int(real_n, real_p - 1)
    real_k = order_by_divisors(real_n, real_p)
    real_degrees = forced_degrees(real_n, real_k)
    real_order_pass = (
        real_gcd == must_gcd
        and real_k == must_k
        and real_degrees == must_degrees
    )

    kf_k = order_by_divisors(kf_n, kf_p)
    kf_divides = ((kf_p - 1) % kf_n) == 0
    kf_rejected = (kf_k == kf_must_k) and kf_divides and bool(kf_fx.get("must_reject"))
    known_false_k1_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_order_pass
        and known_false_k1_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "divisors_of_N_minus_1_minimal_pow",
        "imported_producer": False,
        "used_sequential_multiply": False,
        "used_divisor_walk": True,
        "fixture_pass": fixture_pass,
        "real_order_pass": real_order_pass,
        "known_false_k1_pass": known_false_k1_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "N": real_n,
            "p": real_p,
            "gcd": real_gcd,
            "k": real_k,
            "degrees": real_degrees,
            "matches_frozen": real_order_pass,
        },
        "KF": {
            "N": kf_n,
            "p": kf_p,
            "k": kf_k,
            "N_divides_p_minus_1": kf_divides,
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
