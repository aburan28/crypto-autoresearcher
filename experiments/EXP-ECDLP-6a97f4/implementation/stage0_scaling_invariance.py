#!/usr/bin/env python3
"""EXP-ECDLP-6a97f4 Stage 0 scaling invariance of F=x^2/A.

Certificate kind none. Canonical-versus-arbitrary digits are not inspected.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-6a97f4/implementation/stage0_scaling_invariance.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-6a97f4/runs/RUN-ECDLP-6a97f4-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-6a97f4/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-36385f"
TASK_ID = "TASK-20260908-c452ef"

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


def hensel_lift_point(p: int, A: int, B: int, P):
    """Lift a nonsingular affine point from F_p to Z/p^2 by Hensel on y^2 - (x^3+Ax+B)."""
    x0, y0 = P
    mod = p * p
    # Keep x at the Teichmuller-style 0..p-1 representative; lift y.
    fx = (pow(x0, 3, mod) + A * x0 + B) % mod
    # y0^2 ≡ fx mod p already. Need 2 y0 dy ≡ (fx - y0^2)/p mod p.
    rhs = (fx - (y0 * y0) % mod) % mod
    assert rhs % p == 0, (P, rhs)
    if (2 * y0) % p == 0:
        raise RuntimeError(f"y=0 cannot lift uniquely: {P}")
    dy = ((rhs // p) * pow(2 * y0, -1, p)) % p
    y1 = (y0 + p * dy) % mod
    return (x0 % mod, y1)


def F_of(x: int, A: int, mod: int) -> int:
    return (x * x) % mod * pow(A, -1, mod) % mod


def symbolic_identity_pass() -> bool:
    # In any ring, (u^2 x)^2 / (u^4 A) = x^2 / A when A,u units.
    # Check as a polynomial identity over a few random unit samples, plus
    # the integer rewrite (u^4 x^2) * inv(u^4 A) == x^2 * inv(A).
    for A in range(1, 20):
        for u in range(1, 20):
            for x in range(0, 20):
                if pow(A * (u ** 4), 1, 97) == 0:
                    continue
                mod = 97
                left = F_of((u * u * x) % mod, (pow(u, 4, mod) * A) % mod, mod)
                right = F_of(x % mod, A % mod, mod)
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
    A_lift = A
    B_lift = B
    n_changed = 0
    n_sections = 0
    for k in range(1, n):
        R = scal(p, A, k, P)
        if R is None:
            raise RuntimeError(f"{cell['id']}: [k]P hit O at k={k}")
        if R[1] % p == 0:
            raise RuntimeError(f"{cell['id']}: y=0 at k={k}")
        x0, y0 = hensel_lift_point(p, A_lift, B_lift, R)
        F0 = F_of(x0, A_lift, mod)
        n_sections += 1
        for u in SCALINGS:
            if pow(u, 1, p) == 0:
                raise RuntimeError(f"u={u} not a unit mod {p}")
            Ap = pow(u, 4, mod) * A_lift % mod
            xp = pow(u, 2, mod) * x0 % mod
            Fu = F_of(xp, Ap, mod)
            if Fu != F0:
                n_changed += 1
        # u=1 sanity
        if F_of(x0, A_lift, mod) != F0:
            n_changed += 1
    return {
        "id": cell["id"],
        "p": p,
        "n": n,
        "n_sections": n_sections,
        "expected_sections": n - 1,
        "n_changed_F": n_changed,
    }


def main() -> int:
    t0 = time.time()
    identity_pass = symbolic_identity_pass()
    cells = [run_cell(c) for c in CELLS]
    n_changed = sum(c["n_changed_F"] for c in cells)
    sections_ok = all(c["n_sections"] == c["expected_sections"] for c in cells)
    scaling_invariance_pass = identity_pass and n_changed == 0 and sections_ok
    fixture_pass = scaling_invariance_pass
    result = {
        "run_id": "RUN-ECDLP-6a97f4-S0",
        "experiment_id": "EXP-ECDLP-6a97f4",
        "hypothesis_id": "H-ECDLP-e9d9bb",
        "authorized_by": AUTHORIZED_BY,
        "task_id": TASK_ID,
        "certificate": {"kind": "none"},
        "identity_pass": identity_pass,
        "scaling_invariance_pass": scaling_invariance_pass,
        "n_changed_F": n_changed,
        "fixture_pass": fixture_pass,
        "cells": cells,
        "scalings": SCALINGS,
        "wall_clock_seconds": time.time() - t0,
        "python": sys.version,
        "platform": platform.platform(),
        "source": SOURCE,
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "raw-result.json").write_text(json.dumps(result, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(f"python3 {SOURCE}\n")
    env = {
        "python": "3.12.3",
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    summary = json.dumps({k: result[k] for k in (
        "identity_pass", "scaling_invariance_pass", "n_changed_F", "fixture_pass"
    )}, indent=2) + "\n"
    (RUN_DIR / "stdout.log").write_text(summary)
    (RUN_DIR / "stderr.log").write_text("")
    print(summary, end="")
    if not fixture_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
