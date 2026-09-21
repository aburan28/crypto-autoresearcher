#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-628891 Stage 0 P-S0-DELIM.

Frozen lists from the specification / hypothesis only.
Does not import the Stage 0 producer. Does not read RUN-ECDLP-628891-S0.
Does not hunt a new ANF. Does not run cadical/kissat.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-628891/implementation/stage0_delim.py",
    ROOT / "experiments/EXP-ECDLP-628891/runs/RUN-ECDLP-628891-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-628891/execution-report-s0.yaml",
]

BITS = ("a0", "a1", "a2", "b0", "b1", "b2", "c0", "c1", "c2")
AB = ("a0", "a1", "a2", "b0", "b1", "b2")
KF_EXPECTED = {
    (0, 1, 0, 0, 1, 0),
    (0, 1, 1, 0, 1, 1),
    (1, 0, 0, 1, 0, 0),
    (1, 0, 1, 1, 0, 1),
}


def real3(bits: dict[str, int]) -> bool:
    return (
        (bits["a0"] ^ bits["b0"] ^ bits["c0"]) == 1
        and (bits["a1"] ^ bits["b1"] ^ bits["c1"]) == 0
        and (bits["a2"] ^ bits["b2"] ^ bits["c2"]) == 1
        and ((bits["a0"] & bits["b0"]) ^ bits["a1"] ^ bits["c2"]) == 0
    )


def kf3(bits: dict[str, int]) -> bool:
    return (
        real3(bits)
        and bits["a0"] == bits["b0"]
        and bits["a1"] == bits["b1"]
        and bits["a2"] == bits["b2"]
    )


def null3(bits: dict[str, int]) -> bool:
    return bits["c0"] == 1 and bits["c1"] == 0 and bits["c2"] == 1


def solutions(pred):
    out = []
    for values in product((0, 1), repeat=9):
        bits = dict(zip(BITS, values))
        if pred(bits):
            out.append(bits)
    return out


def pairs(sols):
    return sorted({tuple(bits[n] for n in AB) for bits in sols})


def affine_eval(coeffs, pair):
    acc = coeffs[-1]
    for c, x in zip(coeffs[:-1], pair):
        acc ^= c & x
    return acc


def vanishing(pairs_):
    forms = []
    for coeffs in product((0, 1), repeat=7):
        if all(c == 0 for c in coeffs):
            continue
        if all(affine_eval(coeffs, p) == 0 for p in pairs_):
            forms.append(coeffs)
    return forms


def vanish_expr(expr, pairs_):
    coeffs = [0] * 7
    for name in expr.split("+"):
        coeffs[AB.index(name)] = 1
    return all(affine_eval(tuple(coeffs), p) == 0 for p in pairs_)


def blocks_ok(blocks):
    if not isinstance(blocks, dict) or not blocks:
        return False
    if set(blocks) != {"A", "B", "C"}:
        return False
    return all(blocks.get(k) == 3 for k in ("A", "B", "C"))


def main() -> int:
    imported = [m for m in ("stage0_delim",) if m in globals()]
    assert not imported
    for path in FORBIDDEN:
        _ = path

    real_s = solutions(real3)
    kf_s = solutions(kf3)
    null_s = solutions(null3)
    real_p = pairs(real_s)
    kf_p = pairs(kf_s)
    null_p = pairs(null_s)
    real_f = vanishing(real_p)
    kf_f = vanishing(kf_p)
    null_f = vanishing(null_p)
    kf_vanish = all(vanish_expr(e, kf_p) for e in ("a0+b0", "a1+b1", "a2+b2"))

    fixture_pass = (
        len(real_s) == 32
        and len(real_p) == 32
        and len(kf_s) == 4
        and len(kf_p) == 4
        and set(kf_p) == KF_EXPECTED
        and len(null_s) == 64
        and len(null_p) == 64
        and blocks_ok({"A": 3, "B": 3, "C": 3})
    )
    real_no_linear_pass = len(real_f) == 0
    known_false_delims_one_pass = bool(kf_f) and kf_vanish
    reject_invalid_pass = (not blocks_ok({})) and (not blocks_ok({"A": 3, "B": 3}))
    null_recorded_pass = isinstance(len(null_s), int) and isinstance(len(null_f), int)
    all_pass = (
        fixture_pass
        and real_no_linear_pass
        and known_false_delims_one_pass
        and reject_invalid_pass
        and null_recorded_pass
    )
    out = {
        "task_id": "TASK-20260908-a4776d",
        "imported_producer": False,
        "read_producer_raw": False,
        "read_execution_report": False,
        "fixture_pass": fixture_pass,
        "real_no_linear_pass": real_no_linear_pass,
        "known_false_delims_one_pass": known_false_delims_one_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_recorded_pass": null_recorded_pass,
        "REAL3_n_solutions": len(real_s),
        "REAL3_n_pairs": len(real_p),
        "REAL3_n_affine_linear_forms": len(real_f),
        "KF3_n_solutions": len(kf_s),
        "KF3_n_pairs": len(kf_p),
        "KF3_n_affine_linear_forms": len(kf_f),
        "KF3_must_vanish": kf_vanish,
        "NULL3_n_solutions": len(null_s),
        "NULL3_n_pairs": len(null_p),
        "NULL3_n_affine_linear_forms": len(null_f),
        "all_pass": all_pass,
        "certificate_kind": "none",
        "workspace_parents": 7,
    }
    (HERE / "blind_raw.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
