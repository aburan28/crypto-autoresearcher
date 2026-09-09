"""Pollard rho for ECDLP -- the matched generic baseline (KN-TECH-001).

Solves Q = k*P using only the public instance data (never the oracle secret),
in expected ~sqrt(n) group operations. On success it returns k together with a
count of group operations, so experiments can report cost without conflating it
with the solver's wall time. Correctness of k is certified downstream by
recomputing k*P (docs/claims-and-verification.md).

`solve` here uses Floyd cycle detection: constant memory, one walk, and the
trajectory is discarded. The distinguished-point variant that real campaigns
run -- many independent short walks, only DPs stored, collision found in the DP
table -- lives in `walk.py` and is re-exported as `rho.solve_dp`; it keeps the
walks, so they can be measured and drawn (`walkviz.py`). Kangaroo, the same
walk restricted to an interval, is in `kangaroo.py`.
"""
from __future__ import annotations

from dataclasses import dataclass

from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int
from .walk import solve_dp  # noqa: F401  (re-exported; see module docstring)


@dataclass(frozen=True)
class RhoResult:
    solved: bool
    k: int | None
    group_operations: int          # walk-phase only (for backward compat)
    total_group_operations: int    # all group ops: precompute + walk + verify
    iterations: int
    reason: str = ""


def solve(inst: ECDLPInstance, max_iterations: int | None = None,
          branches: int = 32) -> RhoResult:
    """Recover k with a Teske r-adding Pollard-rho walk. Public data only.

    Uses `branches` precomputed steps T_s = c_s*P + d_s*Q chosen deterministically
    from the instance seed; this mixes far better than the classic 3-partition
    walk and stays correct for small toy subgroups. Floyd cycle detection.
    """
    E = inst.curve()
    P, Q, n = inst.P, inst.Q, inst.n
    if max_iterations is None:
        max_iterations = max(2000, 200 * int(n ** 0.5) + 200)

    ops = 0
    total_ops = 0  # counts ALL group operations: precompute, walk, verify

    def _count_mul(k_val: int, pt: Point) -> Point:
        nonlocal total_ops
        if k_val < 0:
            raise ValueError("nonnegative scalar required")
        if k_val == 0:
            return None
        result_pt = pt
        for digit in bin(k_val)[3:]:
            result_pt = E.add(result_pt, result_pt)
            total_ops += 1
            if digit == "1":
                result_pt = E.add(result_pt, pt)
                total_ops += 1
        return result_pt

    # Precompute the r branch steps (deterministic in the seed).
    steps = []
    for s in range(branches):
        c = _seed_int(inst.seed, f"rho_c{s}") % n
        d = _seed_int(inst.seed, f"rho_d{s}") % n
        cP = _count_mul(c, P)
        dQ = _count_mul(d, Q)
        step_pt = E.add(cP, dQ)
        total_ops += 1
        steps.append((step_pt, c, d))

    def walk(R: Point, a: int, b: int) -> tuple[Point, int, int]:
        nonlocal ops, total_ops
        s = (R[0] if R is not None else 0) % branches
        Ts, c, d = steps[s]
        ops += 1
        total_ops += 1
        return E.add(R, Ts), (a + c) % n, (b + d) % n

    # A few deterministic restarts guard against a rare degenerate collision.
    for offset in range(0, 12):
        a0 = _seed_int(inst.seed, f"rho_a0_{offset}") % n
        b0 = (_seed_int(inst.seed, f"rho_b0_{offset}") % (n - 1)) + 1
        T = E.add(_count_mul(a0, P), _count_mul(b0, Q))
        total_ops += 1
        aT, bT = a0, b0
        H, aH, bH = T, aT, bT
        for it in range(1, max_iterations + 1):
            T, aT, bT = walk(T, aT, bT)               # tortoise
            H, aH, bH = walk(*walk(H, aH, bH))        # hare (two steps)
            if T == H:
                db = (bT - bH) % n
                if db == 0:
                    break                              # degenerate; restart
                k = (aH - aT) * pow(db, -1, n) % n
                # Verification: count the scalar mult
                verify_pt = _count_mul(int(k), P)
                if verify_pt == Q:
                    return RhoResult(True, int(k), ops, total_ops, it)
                break
    return RhoResult(False, None, ops, total_ops, max_iterations,
                     reason="no collision yielded an invertible relation "
                            "within the iteration budget")
