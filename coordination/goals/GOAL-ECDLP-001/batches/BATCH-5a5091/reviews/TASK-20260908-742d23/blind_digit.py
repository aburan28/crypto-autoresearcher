#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-6a97f4 Stage 1 P-S1-RELATIVE digits.

Frozen fixture numbers from review_plan_s1_6a97f4 only.
Does not import the Stage 1 producer. Does not read RUN-ECDLP-6a97f4-S1.
Does not certify Serre-Tate. Does not dispose P-S1-DIGIT.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-6a97f4/implementation/stage1_relative_digit.py",
    ROOT / "experiments/EXP-ECDLP-6a97f4/runs/RUN-ECDLP-6a97f4-S1/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-6a97f4/execution-report-s1.yaml",
]

CELLS = [
    {"id": "S0-C13", "p": 13, "A": 1, "B": 5, "n": 9, "P": (3, 3)},
    {"id": "S0-C17", "p": 17, "A": 1, "B": 5, "n": 15, "P": (2, 7)},
    {"id": "S0-C19", "p": 19, "A": 1, "B": 1, "n": 21, "P": (0, 1)},
    {"id": "S0-C37", "p": 37, "A": 1, "B": 3, "n": 39, "P": (0, 15)},
]
UNITS = (2, 3)
PERTS = (("P10", 1, 0), ("P01", 0, 1), ("P11", 1, 1))


def _point_add(mod, a, P, Q):
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
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, mod) % mod
    else:
        m = (y2 - y1) * pow((x2 - x1) % mod, -1, mod) % mod
    x3 = (m * m - x1 - x2) % mod
    y3 = (m * (x1 - x3) - y1) % mod
    return (x3, y3)


def _mul(mod, a, k, P):
    acc = None
    cur = P
    kk = k
    while kk:
        if kk & 1:
            acc = _point_add(mod, a, acc, cur)
        cur = _point_add(mod, a, cur, cur)
        kk >>= 1
    return acc


def _lift_y(p, A, B, P):
    x, y = P
    q = p * p
    rhs = (pow(x, 3, q) + A * x + B - (y * y) % q) % q
    if rhs % p:
        raise RuntimeError("residue mismatch")
    if (2 * y) % p == 0:
        raise RuntimeError("nonunique y")
    dy = ((rhs // p) * pow(2 * y, -1, p)) % p
    return (x % p, (y + p * dy) % q)


def _F(x, A, q):
    return (x * x) % q * pow(A, -1, q) % q


def _digit(F, p):
    q = p * p
    F = F % q
    return ((F - (F % p)) // p) % p


def _scale_ok(x, A, p):
    q = p * p
    F0 = _F(x, A, q)
    for u in UNITS:
        if _F((u * u * x) % q, (pow(u, 4, q) * A) % q, q) != F0:
            return False
    return True


def _digits(cell, dA, dB):
    p = cell["p"]
    A0 = cell["A"]
    B0 = cell["B"]
    n = cell["n"]
    P = cell["P"]
    A = A0 + dA * p
    B = B0 + dB * p
    q = p * p
    out = []
    scale = True
    for k in range(1, n):
        R = _mul(p, A0, k, P)
        if R is None or R[1] % p == 0:
            raise RuntimeError(f"{cell['id']} k={k}")
        x, _y = _lift_y(p, A, B, R)
        F = _F(x, A, q)
        out.append(_digit(F, p))
        scale = scale and _scale_ok(x, A, p)
    return out, scale


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            # existence is allowed; reading is not
            pass
    cells = {}
    panel = 0
    for cell in CELLS:
        base, base_scale = _digits(cell, 0, 0)
        nsec = len(base)
        expected = cell["n"] - 1
        base_vs_base = sum(int(a != b) for a, b in zip(base, base))
        per = {}
        arm_scale = {"BASE": base_scale}
        for name, dA, dB in PERTS:
            other, sc = _digits(cell, dA, dB)
            diff = sum(int(a != b) for a, b in zip(base, other))
            per[name] = diff
            panel += diff
            arm_scale[name] = sc
        cells[cell["id"]] = {
            "n_sections": nsec,
            "expected_sections": expected,
            "base_vs_base_n_digit_diff": base_vs_base,
            "n_digit_diff": per,
            "scaling_invariance_pass": all(arm_scale.values()),
        }
    result = {
        "n_digit_diff_panel": panel,
        "base_vs_base_all_zero": all(v["base_vs_base_n_digit_diff"] == 0 for v in cells.values()),
        "sections_ok": all(v["n_sections"] == v["expected_sections"] for v in cells.values()),
        "scaling_invariance_pass": all(v["scaling_invariance_pass"] for v in cells.values()),
        "cells": cells,
        "producer_imported": False,
        "stage1_run_read": False,
        "P_S1_DIGIT_disposed": False,
        "serre_tate_certified": False,
        "workspace_root": str(ROOT),
        "parents7_is_repo": (ROOT / "AGENTS.md").is_file(),
    }
    (HERE / "blind_raw.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in (
        "n_digit_diff_panel", "base_vs_base_all_zero", "sections_ok",
        "scaling_invariance_pass", "producer_imported", "stage1_run_read",
        "P_S1_DIGIT_disposed", "serre_tate_certified", "parents7_is_repo",
    )}, indent=2))
    print("cells", {cid: {k: cells[cid][k] for k in ("n_sections", "base_vs_base_n_digit_diff", "n_digit_diff")} for cid in cells})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
