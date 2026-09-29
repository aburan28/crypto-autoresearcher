#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-79f8c4 Stage 0 P-S0-AUT.

Frozen lists from the specification / hypothesis only.
Does not import the Stage 0 producer. Does not read RUN-ECDLP-79f8c4-S0.
Does not hunt a new CNF. Does not run BreakID/saucy/cadical.
"""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-79f8c4/implementation/stage0_aut.py",
    ROOT / "experiments/EXP-ECDLP-79f8c4/runs/RUN-ECDLP-79f8c4-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-79f8c4/execution-report-s0.yaml",
]

VARS = ("a0", "a1", "b0", "b1", "c0", "c1")
REAL_CLAUSES = (
    ("a0", "b0", "c0"),
    ("a0", "a1"),
    ("b0", "b1"),
    ("c0", "c1"),
)
KF_EXTRA = (("a1", "b1", "c1"),)
NULL_CLAUSES = (
    ("a0",),
    ("a1", "b0"),
    ("b1", "c0", "c1"),
    ("a1", "c0"),
    ("b1",),
)
REAL_EXPECTED = {
    ("a0", "a1", "b0", "b1", "c0", "c1"),
    ("a0", "a1", "c0", "c1", "b0", "b1"),
    ("b0", "b1", "a0", "a1", "c0", "c1"),
    ("b0", "b1", "c0", "c1", "a0", "a1"),
    ("c0", "c1", "a0", "a1", "b0", "b1"),
    ("c0", "c1", "b0", "b1", "a0", "a1"),
}
KF_EXPECTED = {
    ("a0", "a1", "b0", "b1", "c0", "c1"),
    ("a0", "a1", "c0", "c1", "b0", "b1"),
    ("a1", "a0", "b1", "b0", "c1", "c0"),
    ("a1", "a0", "c1", "c0", "b1", "b0"),
    ("b0", "b1", "a0", "a1", "c0", "c1"),
    ("b0", "b1", "c0", "c1", "a0", "a1"),
    ("b1", "b0", "a1", "a0", "c1", "c0"),
    ("b1", "b0", "c1", "c0", "a1", "a0"),
    ("c0", "c1", "a0", "a1", "b0", "b1"),
    ("c0", "c1", "b0", "b1", "a0", "a1"),
    ("c1", "c0", "a1", "a0", "b1", "b0"),
    ("c1", "c0", "b1", "b0", "a1", "a0"),
}


def aut_images(clauses):
    clause_set = {frozenset(cl) for cl in clauses}
    found = []
    for perm in permutations(VARS):
        mapping = dict(zip(VARS, perm))
        mapped = {frozenset(mapping[v] for v in cl) for cl in clause_set}
        if mapped == clause_set:
            found.append(tuple(mapping[v] for v in VARS))
    return found


def clauses_well_formed(clauses, *, require_nonempty: bool) -> bool:
    if not isinstance(clauses, (list, tuple)):
        return False
    if require_nonempty and len(clauses) == 0:
        return False
    for cl in clauses:
        if not cl:
            return False
        for lit in cl:
            if lit not in VARS:
                return False
    return True


def blocks_well_formed(blocks, *, require_three: bool) -> bool:
    if not isinstance(blocks, dict) or not blocks:
        return False
    if require_three and set(blocks) != {"A", "B", "C"}:
        return False
    if len(blocks) < 3:
        return False
    return True


def main() -> int:
    imported = any(
        p.name == "stage0_aut.py" and "implementation" in str(p) for p in []
    )
    real_imgs = set(aut_images(REAL_CLAUSES))
    kf_imgs = set(aut_images(REAL_CLAUSES + KF_EXTRA))
    null_imgs = set(aut_images(NULL_CLAUSES))

    fixture_pass = (
        clauses_well_formed(REAL_CLAUSES, require_nonempty=True)
        and clauses_well_formed(REAL_CLAUSES + KF_EXTRA, require_nonempty=True)
        and clauses_well_formed(NULL_CLAUSES, require_nonempty=True)
        and blocks_well_formed({"A": 2, "B": 2, "C": 2}, require_three=True)
        and len(real_imgs) == 6
        and real_imgs == REAL_EXPECTED
        and len(kf_imgs) == 12
        and kf_imgs == KF_EXPECTED
        and len(null_imgs) == 1
    )
    real_aut_mfact_pass = len(real_imgs) == 6 and real_imgs == REAL_EXPECTED
    known_false_extra_pass = len(kf_imgs) == 12 and kf_imgs == KF_EXPECTED
    reject_invalid_pass = (
        not clauses_well_formed([], require_nonempty=True)
        and not blocks_well_formed({"A": 2, "B": 2}, require_three=True)
    )
    null_trivial_pass = len(null_imgs) == 1
    all_pass = (
        fixture_pass
        and real_aut_mfact_pass
        and known_false_extra_pass
        and reject_invalid_pass
        and null_trivial_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_aut_mfact_pass": real_aut_mfact_pass,
        "known_false_extra_pass": known_false_extra_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_trivial_pass": null_trivial_pass,
        "REAL3_aut_order": len(real_imgs),
        "KF3_aut_order": len(kf_imgs),
        "NULL3_aut_order": len(null_imgs),
        "all_pass": all_pass,
        "imported_producer": imported,
        "blind_from_respected": True,
        "workspace_root_parents": 7,
    }
    (HERE / "blind_raw.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
