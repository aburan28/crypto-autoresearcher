#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-6a97f4 Stage 0 scaling invariance.

Frozen fixture numbers only. Does not import the Stage 0 producer.
Does not read RUN-ECDLP-6a97f4-S0. Does not inspect first-lift digits.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-6a97f4/implementation/stage0_scaling_invariance.py",
    ROOT / "experiments/EXP-ECDLP-6a97f4/runs/RUN-ECDLP-6a97f4-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-6a97f4/execution-report-s0.yaml",
]

CELLS = [
    {"id": "S0-C13", "p": 13, "A": 1, "B": 5, "n": 9, "P": (3, 3)},
    {"id": "S0-C17", "p": 17, "A": 1, "B": 5, "n": 15, "P": (2, 7)},
    {"id": "S0-C19", "p": 19, "A": 1, "B": 1, "n": 21, "P": (0, 1)},
    {"id": "S0-C37", "p": 37, "A": 1, "B": 3, "n": 39, "P": (0, 15)},
]
SCALINGS = [2, 3]


def add(mod: int, a: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % mod == 0:
        return None
    if P == Q:
        if y1 % mod == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, mod) % mod
    else:
        lam = (y2 - y1) * pow((x2 - x1) % mod, -1, mod) % mod
    x3 = (lam * lam - x1 - x2) % mod
    y3 = (lam * (x1 - x3) - y1) % mod
    return (x3, y3)


def scal(mod: int, a: int, k: int, P):
    R = None
    Q = P
    while k:
        if k & 1:
            R = add(mod, a, R, Q)
        Q = add(mod, a, Q, Q)
        k >>= 1
    return R


def hensel_y(p: int, A: int, B: int, P):
    x0, y0 = P
    mod = p * p
    fx = (pow(x0, 3, mod) + A * x0 + B) % mod
    rhs = (fx - (y0 * y0) % mod) % mod
    if rhs % p != 0:
        raise RuntimeError("not a point")
    if (2 * y0) % p == 0:
        raise RuntimeError("y=0")
    dy = ((rhs // p) * pow(2 * y0, -1, p)) % p
    return (x0 % mod, (y0 + p * dy) % mod)


def F_of(x: int, A: int, mod: int) -> int:
    return (x * x) % mod * pow(A, -1, mod) % mod


def algebraic_rewrite_pass(p: int) -> bool:
    mod = p * p
    for A in range(1, min(p, 12)):
        if A % p == 0:
            continue
        for u in SCALINGS:
            if u % p == 0:
                return False
            for x in range(0, p):
                left = F_of((u * u * x) % mod, (pow(u, 4, mod) * A) % mod, mod)
                right = F_of(x, A, mod)
                if left != right:
                    return False
    return True


def run_cell(cell: dict) -> dict:
    p = cell["p"]
    A = cell["A"]
    B = cell["B"]
    n = cell["n"]
    P = cell["P"]
    mod = p * p
    if scal(p, A, n, P) is not None:
        raise RuntimeError(f"{cell['id']}: nP is not O")
    n_changed = 0
    n_sections = 0
    for k in range(1, n):
        R = scal(p, A, k, P)
        if R is None:
            raise RuntimeError(f"{cell['id']}: [{k}]P = O")
        if R[1] % p == 0:
            raise RuntimeError(f"{cell['id']}: y=0 at k={k}")
        x0, _y0 = hensel_y(p, A, B, R)
        F0 = F_of(x0, A, mod)
        n_sections += 1
        for u in SCALINGS:
            Fu = F_of(pow(u, 2, mod) * x0 % mod, pow(u, 4, mod) * A % mod, mod)
            if Fu != F0:
                n_changed += 1
    return {
        "id": cell["id"],
        "p": p,
        "n": n,
        "n_sections": n_sections,
        "expected_sections": n - 1,
        "n_changed_F": n_changed,
        "algebraic_rewrite_pass": algebraic_rewrite_pass(p),
    }


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            # Presence on disk is allowed; reading is not. Do not open.
            pass
    cells = [run_cell(c) for c in CELLS]
    n_changed = sum(c["n_changed_F"] for c in cells)
    sections_ok = all(c["n_sections"] == c["expected_sections"] for c in cells)
    rewrite_ok = all(c["algebraic_rewrite_pass"] for c in cells)
    result = {
        "task_id": "TASK-20260908-76ebf5",
        "quantity": "n_changed_F and per-cell n_sections of F=x^2/A under u=2,3",
        "n_changed_F": n_changed,
        "scaling_invariance_pass": n_changed == 0 and sections_ok and rewrite_ok,
        "sections_ok": sections_ok,
        "algebraic_rewrite_pass": rewrite_ok,
        "cells": cells,
        "scalings": SCALINGS,
        "producer_imported": False,
        "stage0_run_read": False,
        "first_lift_digits_inspected": False,
        "certificate_kind": "none",
    }
    (HERE / "blind_raw.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "n_changed_F": n_changed,
        "scaling_invariance_pass": result["scaling_invariance_pass"],
        "sections_ok": sections_ok,
        "algebraic_rewrite_pass": rewrite_ok,
    }))
    return 0 if result["scaling_invariance_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
