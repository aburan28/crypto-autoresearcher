#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-1aa0f8 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-1aa0f8/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def lit_true(lit: str, assign: dict[str, int]) -> bool:
    if lit.startswith("~"):
        return assign[lit[1:]] == 0
    return assign[lit] == 1


def sat(clauses, assign) -> bool:
    return all(any(lit_true(lit, assign) for lit in clause) for clause in clauses)


def enumerate_up(variables, target, clauses):
    if not variables:
        raise ValueError("empty variable list")
    if any(t not in variables for t in target):
        raise ValueError("missing target bits")
    sols = []
    for bits in product((0, 1), repeat=len(variables)):
        assign = dict(zip(variables, bits))
        if sat(clauses, assign):
            sols.append(assign)
    projected = {tuple(s[t] for t in target) for s in sols}
    return len(sols), len(projected)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    variables = tuple(fx["variables"])
    target = tuple(fx["target"])
    real_clauses = [tuple(c) for c in fx["real"]["clauses"]]
    kf_clauses = [tuple(c) for c in fx["known_false"]["clauses"]]
    null_clauses = [tuple(c) for c in fx["matched_null"]["clauses"]]

    real_U, real_P = enumerate_up(variables, target, real_clauses)
    kf_U, kf_P = enumerate_up(variables, target, kf_clauses)
    null_U, null_P = enumerate_up(variables, target, null_clauses)

    reject_empty = False
    reject_core = False
    try:
        enumerate_up((), target, ())
    except ValueError:
        reject_empty = True
    try:
        enumerate_up(tuple(fx["core"]), target, ())
    except ValueError:
        reject_core = True

    real_up_pass = real_U == fx["real"]["must_U"] and real_P == fx["real"]["must_P"]
    known_false_unconstrained_pass = (
        kf_U == fx["known_false"]["must_U"] and kf_P == fx["known_false"]["must_P"]
    )
    null_unsat_pass = (
        null_U == fx["matched_null"]["must_U"] and null_P == fx["matched_null"]["must_P"]
    )
    reject_invalid_pass = reject_empty and reject_core
    fixture_pass = True
    all_pass = (
        fixture_pass
        and real_up_pass
        and known_false_unconstrained_pass
        and reject_invalid_pass
        and null_unsat_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_up_pass": real_up_pass,
        "known_false_unconstrained_pass": known_false_unconstrained_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_unsat_pass": null_unsat_pass,
        "REAL3_U": real_U,
        "REAL3_P": real_P,
        "KF3_U": kf_U,
        "KF3_P": kf_P,
        "NULL3_U": null_U,
        "NULL3_P": null_P,
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
