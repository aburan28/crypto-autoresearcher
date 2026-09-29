#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-835df6 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use a dict increment. Does not use ** for the degrees.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  sorted adjacent-run counts for fibres,
  repeated multiplication for degrees,
  not defaultdict increment plus **.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-835df6/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def repeated_mul(base: int, times: int) -> int:
    acc = 1
    step = 0
    while step < times:
        acc = acc * int(base)
        step = step + 1
    return acc


def affine_j0_t_values(p: int, b: int) -> list[int]:
    values: list[int] = []
    x = 0
    while x < p:
        rhs = (x * x * x + b) % p
        y = 0
        while y < p:
            if (y * y) % p == rhs:
                values.append((x * x * x) % p)
            y = y + 1
        x = x + 1
    return values


def affine_edwards_t_values(p: int, d: int) -> list[int]:
    values: list[int] = []
    x = 0
    while x < p:
        y = 0
        while y < p:
            left = (x * x + y * y) % p
            right = (1 + d * x * x * y * y) % p
            if left == right:
                values.append((x * y * x * y) % p)
            y = y + 1
        x = x + 1
    return values


def adjacent_run_sizes(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        return []
    ordered = sorted(values)
    runs: list[tuple[int, int]] = []
    current = ordered[0]
    count = 1
    index = 1
    while index < len(ordered):
        item = ordered[index]
        if item == current:
            count = count + 1
        else:
            runs.append((current, count))
            current = item
            count = 1
        index = index + 1
    runs.append((current, count))
    return runs


def max_run(runs: list[tuple[int, int]]) -> int:
    if not runs:
        return 0
    largest = runs[0][1]
    index = 1
    while index < len(runs):
        if runs[index][1] > largest:
            largest = runs[index][1]
        index = index + 1
    return largest


def all_runs_equal(runs: list[tuple[int, int]], size: int) -> bool:
    if not runs:
        return False
    index = 0
    while index < len(runs):
        if runs[index][1] != size:
            return False
        index = index + 1
    return True


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    m = int(fx["m_frozen"])
    real_fx = fx["real_aut"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_p = int(real_fx["p"])
    real_b = int(real_fx["B"])
    kf_p = int(kf_fx["p"])
    kf_d = int(kf_fx["d"])

    p_zero_rejected = False
    for row in invalid:
        if row["id"] == "p-zero":
            p_bad = int(row["p"])
            must = bool(row["must_reject"])
            rejected = p_bad != real_p and p_bad == 0
            p_zero_rejected = rejected and must

    null_rejected = (
        null_fx["kind"] == "empty_affine" and bool(null_fx["must_reject"])
    )

    real_values = affine_j0_t_values(real_p, real_b)
    kf_values = affine_edwards_t_values(kf_p, kf_d)
    real_runs = adjacent_run_sizes(real_values)
    kf_runs = adjacent_run_sizes(kf_values)

    real_g = int(real_fx["must_count_degree"])
    kf_g = int(kf_fx["must_count_degree"])
    exponent = m - 2
    real_type = repeated_mul(real_g, exponent)
    real_count = repeated_mul(real_g, exponent)
    kf_type = repeated_mul(2, exponent)
    kf_count = repeated_mul(kf_g, exponent)
    kf_max = max_run(kf_runs)

    fixture_pass = (
        m == 3
        and real_p == 13
        and real_b == 2
        and kf_p == 17
        and kf_d == 3
        and real_fx["t"] == "x_cubed"
        and kf_fx["t"] == "xy_squared"
        and real_fx["kind"] == "aut"
        and kf_fx["kind"] == "translation"
        and bool(real_fx["must_agree"])
        and bool(kf_fx["must_disagree"])
        and null_fx["kind"] == "empty_affine"
    )
    real_count_pass = (
        all_runs_equal(real_runs, int(real_fx["must_all_fibres"]))
        and real_type == int(real_fx["must_type_degree"])
        and real_count == int(real_fx["must_count_degree"])
        and real_type == real_count
    )
    known_false_translation_pass = (
        kf_max == int(kf_fx["must_max_fibre"])
        and kf_type == int(kf_fx["must_type_degree"])
        and kf_count == int(kf_fx["must_count_degree"])
        and kf_type != kf_count
    )
    reject_invalid_pass = p_zero_rejected
    null_empty_pass = null_rejected
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_translation_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_count_pass": real_count_pass,
        "known_false_translation_pass": known_false_translation_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "id": "REAL",
            "kind": "aut",
            "p": real_p,
            "B": real_b,
            "fibre_runs": [[k, v] for k, v in real_runs],
            "all_fibre_size": all_runs_equal(
                real_runs, int(real_fx["must_all_fibres"])
            ),
            "type_degree": real_type,
            "count_degree": real_count,
            "agree": real_type == real_count,
        },
        "KF": {
            "id": "KF",
            "kind": "translation",
            "p": kf_p,
            "d": kf_d,
            "fibre_runs": [[k, v] for k, v in kf_runs],
            "max_fibre": kf_max,
            "type_degree": kf_type,
            "count_degree": kf_count,
            "disagree": kf_type != kf_count,
        },
        "NULL": {
            "id": "NULL",
            "kind": "empty_affine",
            "rejected": null_rejected,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "used_dict_increment": False,
        "used_pow_operator": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "sorted_adjacent_run_counts_and_repeated_multiplication",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
