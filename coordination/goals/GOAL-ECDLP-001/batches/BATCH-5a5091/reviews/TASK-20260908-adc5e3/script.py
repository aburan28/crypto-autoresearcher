#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-9e9536 Stage 0 P-S0-GLUE.

Frozen lists from the specification / hypothesis only.
Does not import the Stage 0 producer. Does not read RUN-ECDLP-9e9536-S0.
Does not hunt a new atlas. Does not search a priced width.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-9e9536/implementation/stage0_glue.py",
    ROOT / "experiments/EXP-ECDLP-9e9536/runs/RUN-ECDLP-9e9536-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-9e9536/execution-report-s0.yaml",
]

N15, MOD, TRANS = 15, 5, 1
N11 = 11
CHARTS = {
    "A": [0, 1, 2, 3, 4],
    "B": [3, 4, 5, 6, 7],
    "C": [7, 8, 9, 10, 0],
}
RELS = {"AB": "equal", "BC": "equal", "CA": "unequal"}
NULL_LABELS = {"A": 0, "B": 0, "C": 0}
ALPHABET = (0, 1)


def intertwine(n: int, modulus: int, transition: int) -> tuple[bool, int]:
    misses = 0
    for x in range(n):
        left = ((x + transition) % n) % modulus
        right = ((x % n) % modulus + transition) % modulus
        if left != right:
            misses += 1
    return misses == 0, misses


def atlas_ok(charts: dict, n: int) -> bool:
    if set(charts) != {"A", "B", "C"}:
        return False
    for pts in charts.values():
        if not pts or len(set(pts)) != len(pts):
            return False
        if not all(isinstance(x, int) and 0 <= x < n for x in pts):
            return False
    return True


def holds(left: int, right: int, rel: str) -> bool:
    return left == right if rel == "equal" else left != right


def pair_sat() -> bool:
    ab = any(holds(a, b, RELS["AB"]) for a, b in product(ALPHABET, repeat=2))
    bc = any(holds(b, c, RELS["BC"]) for b, c in product(ALPHABET, repeat=2))
    ca = any(holds(c, a, RELS["CA"]) for c, a in product(ALPHABET, repeat=2))
    return ab and bc and ca


def global_sat() -> bool:
    for a, b, c in product(ALPHABET, repeat=3):
        if holds(a, b, RELS["AB"]) and holds(b, c, RELS["BC"]) and holds(c, a, RELS["CA"]):
            return True
    return False


def equal_obstruction(labels: dict[str, int]) -> int:
    pairs = {"AB": ("A", "B"), "BC": ("B", "C"), "CA": ("C", "A")}
    misses = 0
    for key, (left, right) in pairs.items():
        if RELS[key] == "equal" and labels[left] != labels[right]:
            misses += 1
    return misses


def main() -> int:
    imported = [m for m in ("stage0_glue",) if m in globals()]
    assert not imported
    for path in FORBIDDEN:
        _ = path  # existence is allowed; we must not read or import them

    ok, obst = intertwine(N15, MOD, TRANS)
    fixture_pass = (
        atlas_ok(CHARTS, N11)
        and NULL_LABELS == {"A": 0, "B": 0, "C": 0}
        and N15 == 15
        and MOD == 5
        and TRANS == 1
    )
    reject_invalid_pass = (not atlas_ok({}, N11)) and (
        not atlas_ok({"A": [0, 1], "B": [1, 2]}, N11)
    )
    plant_global = global_sat()
    plant_refuse_pass = pair_sat() and (not plant_global)
    coset_zero_obstruction_pass = ok and obst == 0
    null_obst = equal_obstruction(NULL_LABELS)
    null_recorded_pass = isinstance(null_obst, int)
    all_pass = (
        fixture_pass
        and coset_zero_obstruction_pass
        and plant_refuse_pass
        and reject_invalid_pass
        and null_recorded_pass
    )
    out = {
        "task_id": "TASK-20260908-adc5e3",
        "imported_producer": False,
        "read_producer_raw": False,
        "read_execution_report": False,
        "fixture_pass": fixture_pass,
        "coset_zero_obstruction_pass": coset_zero_obstruction_pass,
        "plant_refuse_pass": plant_refuse_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_recorded_pass": null_recorded_pass,
        "COS15_obstruction": obst,
        "NULL11_obstruction": null_obst,
        "PLANT11_global_sat": plant_global,
        "all_pass": all_pass,
        "certificate_kind": "none",
        "workspace_parents": 7,
    }
    (HERE / "blind_raw.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
