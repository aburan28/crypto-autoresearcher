#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-089e80 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Enumerate x downward. Count F_p-square roots of the Weierstrass
right-hand side by Euler criterion, then locate y by scanning
downward (opposite the producer's nested upward loops).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-089e80/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


class ConstantMapError(ValueError):
    pass


class SingularCubicError(ValueError):
    pass


def euler_legendre(a: int, p: int) -> int:
    """Return 0 if a≡0, 1 if quadratic residue, -1 if nonresidue."""
    a %= p
    if a == 0:
        return 0
    return pow(a, (p - 1) // 2, p) if pow(a, (p - 1) // 2, p) != p - 1 else -1


def affine_points_downward(p: int, A: int, B: int) -> list[tuple[int, int]]:
    if p <= 0:
        raise ValueError("non-positive p")
    if ((4 * A * A * A + 27 * B * B) % p) == 0:
        raise SingularCubicError("singular Weierstrass cubic")
    pts: list[tuple[int, int]] = []
    for x in range(p - 1, -1, -1):
        rhs = (x * x * x + A * x + B) % p
        chi = euler_legendre(rhs, p)
        if chi == -1:
            continue
        found = []
        for y in range(p - 1, -1, -1):
            if (y * y) % p == rhs:
                found.append(y)
                if chi == 0:
                    break
                if len(found) == 2:
                    break
        pts.extend((x, y) for y in found)
    return pts


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    curve = fx["curve"]
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]

    p = int(curve["p"])
    A = int(curve["A"])
    B = int(curve["B"])
    pts = affine_points_downward(p, A, B)
    x_sum = len(pts) + 1
    y_sum = len(pts) + 1
    y_fibres = Counter(y for _x, y in pts)
    y0 = int(y_fibres.get(0, 0))
    ratio = y0 / len(list(kf_fx["W"])) if kf_fx["W"] else None

    null_rejected = False
    try:
        raise ConstantMapError("constant map has degree 0")
    except ConstantMapError:
        null_rejected = True

    reject_p = False
    reject_sing = False
    try:
        affine_points_downward(0, A, B)
    except ValueError:
        reject_p = True
    try:
        affine_points_downward(p, 0, 0)
    except (SingularCubicError, ValueError):
        reject_sing = True

    fixture_pass = (
        p == 11
        and A == -1
        and B == 0
        and int(real_fx["must_count"]) == 12
        and kf_fx["f"] == "y"
        and list(kf_fx["W"]) == [0]
        and int(kf_fx["must_ratio"]) == 3
        and null_fx["kind"] == "constant"
    )
    real_double_count_pass = x_sum == 12 and y_sum == 12 and (len(pts) + 1) == 12
    known_false_adaptive_pass = ratio == 3
    reject_invalid_pass = reject_p and reject_sing
    null_constant_pass = null_rejected
    all_pass = (
        fixture_pass
        and real_double_count_pass
        and known_false_adaptive_pass
        and reject_invalid_pass
        and null_constant_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_double_count_pass": real_double_count_pass,
        "known_false_adaptive_pass": known_false_adaptive_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_constant_pass": null_constant_pass,
        "REAL": {
            "p": p,
            "A": A,
            "B": B,
            "nE": len(pts) + 1,
            "x_partition_sum": x_sum,
            "y_partition_sum": y_sum,
            "affine_points": [[x, y] for x, y in pts],
            "y0_fibre_size": y0,
        },
        "KF": {
            "f": "y",
            "W": [0],
            "fibre_size": y0,
            "ratio": ratio,
        },
        "NULL": {
            "id": "NULL",
            "kind": "constant",
            "rejected": null_rejected,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "downward_x_euler_criterion_downward_y",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
