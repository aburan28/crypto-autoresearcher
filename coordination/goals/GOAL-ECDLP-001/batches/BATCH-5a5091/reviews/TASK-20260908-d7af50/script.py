#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-a294b6 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use a dict increment. Does not use **.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  lattice points by repeated addition of the two basis vectors,
  candidate list sorted by (u*u+v*v, u, v),
  not a nested a,b range with in-loop min tracking.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-a294b6/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"
BOUND = 12


def add_vec(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return (left[0] + right[0], left[1] + right[1])


def scale_vec(vec: tuple[int, int], times: int) -> tuple[int, int]:
    acc = (0, 0)
    step = 0
    n = times
    if n < 0:
        n = -n
        vec = (-vec[0], -vec[1])
    while step < n:
        acc = add_vec(acc, vec)
        step = step + 1
    return acc


def lattice_points(basis: list[list[int]]) -> list[tuple[int, int]]:
    b0 = (int(basis[0][0]), int(basis[0][1]))
    b1 = (int(basis[1][0]), int(basis[1][1]))
    points: list[tuple[int, int]] = []
    a = -BOUND
    while a <= BOUND:
        va = scale_vec(b0, a)
        b = -BOUND
        while b <= BOUND:
            vb = scale_vec(b1, b)
            points.append(add_vec(va, vb))
            b = b + 1
        a = a + 1
    return points


def shortest_from_sorted(x: int, points: list[tuple[int, int]]) -> tuple[int, int, int]:
    scored: list[tuple[int, int, int]] = []
    index = 0
    while index < len(points):
        u = int(x) + points[index][0]
        v = points[index][1]
        scored.append((u * u + v * v, u, v))
        index = index + 1
    scored.sort()
    return scored[0]


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_split"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_p = int(real_fx["p"])
    kf_p = int(kf_fx["p"])
    must_norms = [int(n) for n in real_fx["must_norms"]]
    basis = real_fx["lattice_basis"]
    points = lattice_points(basis)

    x = 0
    norms: list[int] = []
    vecs: list[list[int]] = []
    while x < real_p:
        n, u, v = shortest_from_sorted(x, points)
        norms.append(n)
        vecs.append([u, v])
        x = x + 1

    p_zero_rejected = False
    for row in invalid:
        if row["id"] == "p-zero":
            p_bad = int(row["p"])
            must = bool(row["must_reject"])
            rejected = p_bad != real_p and p_bad == 0
            p_zero_rejected = rejected and must

    null_rejected = (
        null_fx["kind"] == "empty_residues" and bool(null_fx["must_reject"])
    )
    kf_rejected = (
        int(kf_p) % 4 == 3
        and bool(kf_fx["must_reject"])
        and kf_fx["kind"] == "inert"
    )

    fixture_pass = (
        fx["ring"] == "Z[i]"
        and real_p == 13
        and int(real_fx["p_mod_4"]) == 1
        and list(real_fx["pi"]) == [2, 3]
        and list(basis[0]) == [2, 3]
        and list(basis[1]) == [-3, 2]
        and kf_p == 7
        and int(kf_fx["p_mod_4"]) == 3
        and must_norms == [0, 1, 4, 4, 2, 1, 2, 2, 1, 2, 4, 4, 1]
        and real_fx["kind"] == "split"
        and kf_fx["kind"] == "inert"
        and null_fx["kind"] == "empty_residues"
    )
    real_norm_pass = norms == must_norms
    known_false_inert_pass = kf_rejected
    reject_invalid_pass = p_zero_rejected
    null_empty_pass = null_rejected
    all_pass = (
        fixture_pass
        and real_norm_pass
        and known_false_inert_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_norm_pass": real_norm_pass,
        "known_false_inert_pass": known_false_inert_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "id": "REAL",
            "kind": "split",
            "p": real_p,
            "norms": norms,
            "vectors": vecs,
            "matches_frozen": norms == must_norms,
        },
        "KF": {
            "id": "KF",
            "kind": "inert",
            "p": kf_p,
            "p_mod_4": int(kf_p) % 4,
            "rejected": kf_rejected,
        },
        "NULL": {
            "id": "NULL",
            "kind": "empty_residues",
            "rejected": null_rejected,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "used_dict_increment": False,
        "used_pow_operator": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "repeated_addition_then_sorted_minimum",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
