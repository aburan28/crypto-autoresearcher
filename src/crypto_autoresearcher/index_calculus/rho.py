"""Pollard rho with a Teske r-adding walk, the baseline for index calculus."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .curve import Curve, Point

R_ADDING = 20


@dataclass
class RhoResult:
    k: int | None
    verified: bool
    group_ops: int
    restarts: int
    seconds: float


def pollard_rho(E: Curve, P: Point, Q: Point, seed: int = 0,
                max_restarts: int = 20) -> RhoResult:
    """Solve Q = kP in the prime-order group <P>; counts every group op."""
    N = E.order
    if N is None:
        raise ValueError("curve order must be known")
    rng = random.Random(f"rho|{E.p}|{E.a}|{E.b}|{seed}")
    start_ops = E.ops.group_ops
    t0 = time.perf_counter()
    for restart in range(max_restarts):
        steps = []
        for _ in range(R_ADDING):
            c, d = rng.randrange(N), rng.randrange(N)
            steps.append((E.add(E.mul(c, P), E.mul(d, Q)), c, d))

        def step(X: Point, a: int, b: int):
            j = 0 if X is None else X[0] % R_ADDING
            M, c, d = steps[j]
            return E.add(X, M), (a + c) % N, (b + d) % N

        a0, b0 = rng.randrange(N), rng.randrange(N)
        X0 = E.add(E.mul(a0, P), E.mul(b0, Q))
        tort = hare = (X0, a0, b0)
        while True:
            tort = step(*tort)
            hare = step(*step(*hare))
            if tort[0] == hare[0]:
                break
        _, a1, b1 = tort
        _, a2, b2 = hare
        if (b2 - b1) % N == 0:
            continue
        k = (a1 - a2) * pow(b2 - b1, -1, N) % N
        ops = E.ops.group_ops - start_ops
        ok = E.mul(k, P) == Q
        return RhoResult(k, ok, ops, restart, time.perf_counter() - t0)
    return RhoResult(None, False, E.ops.group_ops - start_ops, max_restarts,
                     time.perf_counter() - t0)
