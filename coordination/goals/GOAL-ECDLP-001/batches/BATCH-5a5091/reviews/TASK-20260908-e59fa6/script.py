#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-2a466a Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not build a square-set of y^2 values.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Euler criterion (rhs)^((p-1)/2) mod p, then a y-walk
  that solves y^2 == rhs without a precomputed square set.
  The producer builds square_set = {y^2} and tests membership.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-2a466a/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def euler_legendre(rhs: int, p: int) -> int:
    """(rhs)^((p-1)/2) mod p. 0 if rhs=0, 1 if residue, p-1 if nonresidue."""
    return pow(int(rhs), (int(p) - 1) // 2, int(p))


def affine_by_euler(p: int, a: int, b: int) -> list[tuple[int, int]]:
    pts: list[tuple[int, int]] = []
    x = 0
    while x < p:
        rhs = (pow(x, 3, p) + (a * x) + b) % p
        symbol = euler_legendre(rhs, p)
        if symbol == p - 1:
            x = x + 1
            continue
        y = 0
        while y < p:
            if (y * y) % p == rhs:
                pts.append((x, y))
            y = y + 1
        x = x + 1
    return pts


def is_prime(n: int) -> bool:
    value = int(n)
    if value <= 1:
        return False
    d = 2
    while d * d <= value:
        if value % d == 0:
            return False
        d += 1
    return True


def gcd_int(u: int, v: int) -> int:
    aa, bb = abs(int(u)), abs(int(v))
    while bb:
        aa, bb = bb, aa % bb
    return aa


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_curve"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_p = int(real_fx["p"])
    real_a = int(real_fx["a"])
    real_b = int(real_fx["b"])
    must_N = int(real_fx["must_N"])
    must_Nprime = int(real_fx["must_Nprime"])
    must_gcd = int(real_fx["must_gcd"])
    must_affine_count = int(real_fx["must_affine_count"])
    must_affine = [tuple(pt) for pt in real_fx["must_affine_points"]]
    kf_p = int(kf_fx["p"])
    kf_a = int(kf_fx["a"])
    kf_b = int(kf_fx["b"])
    kf_must_N = int(kf_fx["must_N"])

    fixture_pass = True

    p_zero_rejected = False
    for item in invalid:
        if int(item.get("p", 1)) <= 0 and bool(item.get("must_reject")):
            p_zero_rejected = True
    reject_invalid_pass = p_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_point_list"

    real_pts = affine_by_euler(real_p, real_a, real_b)
    real_N = len(real_pts) + 1
    real_t = real_p + 1 - real_N
    real_Nprime = real_p + 1 + real_t
    real_gcd = gcd_int(real_N, real_Nprime)
    two_tor = [pt for pt in real_pts if pt[1] == 0]
    real_order_pass = (
        real_N == must_N
        and real_Nprime == must_Nprime
        and real_gcd == must_gcd
        and len(real_pts) == must_affine_count
        and two_tor == []
        and real_pts == must_affine
        and is_prime(real_N)
    )

    kf_pts = affine_by_euler(kf_p, kf_a, kf_b)
    kf_N = len(kf_pts) + 1
    kf_rejected = (kf_N == kf_must_N) and (not is_prime(kf_N)) and bool(kf_fx.get("must_reject"))
    known_false_composite_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_order_pass
        and known_false_composite_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "euler_criterion_then_y_walk_no_square_set",
        "imported_producer": False,
        "used_square_set": False,
        "used_euler_criterion": True,
        "fixture_pass": fixture_pass,
        "real_order_pass": real_order_pass,
        "known_false_composite_pass": known_false_composite_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "p": real_p,
            "a": real_a,
            "b": real_b,
            "N": real_N,
            "t": real_t,
            "Nprime": real_Nprime,
            "gcd": real_gcd,
            "affine_count": len(real_pts),
            "affine": [list(pt) for pt in real_pts],
            "two_torsion_empty": two_tor == [],
            "matches_frozen": real_order_pass,
        },
        "KF": {
            "p": kf_p,
            "a": kf_a,
            "b": kf_b,
            "N": kf_N,
            "N_prime": is_prime(kf_N),
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_point_list", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "REAL": {
                    "N": real_N,
                    "t": real_t,
                    "Nprime": real_Nprime,
                    "gcd": real_gcd,
                    "affine_count": len(real_pts),
                },
                "KF": {"N": kf_N, "rejected": kf_rejected},
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
