"""Pollard rho with distinguished points and a Teske r-adding walk.

The baseline index calculus is measured against.  Cost is reported in two
columns that are never mixed:

* ``walk_ops`` -- one group addition per step of the walk.  This is the
  quantity that grows like sqrt(pi N / 2) and the one exponent fits use;
* ``setup_ops`` -- the fixed scalar multiplications: 2 r for the step table
  M_j = c_j P + d_j Q and 2 per walk for its starting point.  At toy sizes
  this O(r log N) term rivals the walk itself and flattens a fitted slope.

A point is distinguished when bits of its x-coordinate above the partition
index vanish, with probability theta = 2^-dp_bits.  The default theta ~
32 / sqrt(N) keeps the table at a few dozen points while overshooting the
collision by only about 1/theta ~ sqrt(N)/32 steps.  Every walk keeps going
after storing a point (van Oorschot-Wiener), a walk that runs 20/theta steps
without one is abandoned, and a new walk joins the same table.
"""

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
    group_ops: int  # setup_ops + walk_ops
    walk_ops: int
    setup_ops: int
    walks: int
    distinguished: int
    dp_bits: int
    seconds: float

    @property
    def restarts(self) -> int:
        return self.walks - 1


def default_dp_bits(N: int) -> int:
    return max(0, N.bit_length() // 2 - 5)


def pollard_rho(E: Curve, P: Point, Q: Point, seed: int = 0, r: int = R_ADDING,
                dp_bits: int | None = None, max_walks: int = 1000) -> RhoResult:
    """Solve Q = kP in the prime-order group <P>; counts every group op."""
    N = E.order
    if N is None:
        raise ValueError("curve order must be known")
    rng = random.Random(f"rho|{E.p}|{E.a}|{E.b}|{seed}")
    dp_bits = default_dp_bits(N) if dp_bits is None else dp_bits
    mask = (1 << dp_bits) - 1
    max_len = 20 << dp_bits
    t0 = time.perf_counter()
    ops0 = E.ops.group_ops
    walk_ops = 0

    steps = []
    for _ in range(r):
        c, d = rng.randrange(N), rng.randrange(N)
        steps.append((E.add(E.mul(c, P), E.mul(d, Q)), c, d))
    table: dict[Point, tuple[int, int]] = {}

    def done(k: int | None, walks: int) -> RhoResult:
        total = E.ops.group_ops - ops0
        ok = k is not None and E.mul(k, P) == Q
        return RhoResult(k, ok, total, walk_ops, total - walk_ops, walks, len(table),
                         dp_bits, time.perf_counter() - t0)

    for walk in range(1, max_walks + 1):
        a, b = rng.randrange(N), rng.randrange(N)
        X = E.add(E.mul(a, P), E.mul(b, Q))
        for _ in range(max_len):
            if X is None:
                break
            x = X[0]
            if (x // r) & mask == 0:
                prev = table.get(X)
                if prev is not None:
                    a2, b2 = prev
                    if (b - b2) % N:
                        return done((a2 - a) * pow(b - b2, -1, N) % N, walk)
                    break  # the walk merged into a stored path; start afresh
                table[X] = (a, b)
            M, c, d = steps[x % r]
            X = E.add(X, M)
            a, b = (a + c) % N, (b + d) % N
            walk_ops += 1
    return done(None, max_walks)
