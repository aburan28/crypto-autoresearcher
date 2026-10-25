"""Pollard rho with distinguished points and a Teske r-adding walk.

The baseline index calculus is measured against.  Cost is reported in two
columns that are never mixed:

* ``walk_ops`` -- one group addition per step of the walk.  This is the
  quantity that grows like sqrt(pi N / 4) (sqrt(pi N / 2) without the
  negation map) and the one exponent fits use;
* ``setup_ops`` -- the fixed scalar multiplications: 2 r for the step table
  M_j = c_j P + d_j Q and 2 per walk for its starting point.  At toy sizes
  this O(r log N) term rivals the walk itself and flattens a fitted slope.

A point is distinguished when bits of its x-coordinate above the partition
index vanish, with probability theta = 2^-dp_bits.  The default theta ~
32 / sqrt(N) keeps the table at a few dozen points while overshooting the
collision by only about 1/theta ~ sqrt(N)/32 steps.  Every walk keeps going
after storing a point (van Oorschot-Wiener), a walk that runs 20/theta steps
without one is abandoned, and a new walk joins the same table.

By default the walk runs on the classes {X, -X} (the negation map, A = 2):
each point is replaced by the one of X, -X with the smaller y, its
coefficients negated with it, so walk_ops grows like sqrt(pi N / 4).  The
partition index and the distinguished-point test read only x, which the
two share.  Two guards keep the fruitless cycles the map creates rare and
short, as in crypto's matched reference (ic_boundary::RhoWalk::negation):

* the Wiener-Zuccherato look-ahead: a step whose result was flipped and
  would take the same jump again (the fruitless 2-cycle) is replaced by the
  next jump; the discarded addition is counted in walk_ops;
* a window of the last CYCLE_WINDOW abscissae: a repeat is a short cycle,
  left by doubling its member of smallest x (counted in walk_ops); a walk
  that meets the same cycle twice is abandoned.

``negation=False`` is the earlier walk on points, unchanged (A = 1,
sqrt(pi N / 2)).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .curve import Curve, Point

R_ADDING = 20
CYCLE_WINDOW = 16


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
    negation: bool = False
    look_ahead_adds: int = 0   # discarded look-ahead additions (in walk_ops)
    escapes: int = 0           # cycle escapes by doubling (in walk_ops)
    canonicalisations: int = 0 # sign choices: one field negation and compare each

    @property
    def walk(self) -> str:
        return "negation" if self.negation else "plain"

    @property
    def restarts(self) -> int:
        return self.walks - 1


def default_dp_bits(N: int) -> int:
    return max(0, N.bit_length() // 2 - 5)


def pollard_rho(E: Curve, P: Point, Q: Point, seed: int = 0, r: int = R_ADDING,
                dp_bits: int | None = None, max_walks: int = 1000,
                negation: bool = True) -> RhoResult:
    """Solve Q = kP in the prime-order group <P>; counts every group op.

    ``negation`` walks on {X, -X} (A = 2, the default); ``False`` walks on
    points, the earlier baseline, unchanged.
    """
    N = E.order
    if N is None:
        raise ValueError("curve order must be known")
    if not negation:
        return _plain(E, P, Q, seed, r, dp_bits, max_walks)
    p = E.p
    half = (p - 1) // 2
    rng = random.Random(f"rho|{E.p}|{E.a}|{E.b}|{seed}")
    dp_bits = default_dp_bits(N) if dp_bits is None else dp_bits
    mask = (1 << dp_bits) - 1
    max_len = 20 << dp_bits
    t0 = time.perf_counter()
    ops0 = E.ops.group_ops
    walk_ops = look_ahead = escapes = canon = 0

    steps = []
    for _ in range(r):
        c, d = rng.randrange(N), rng.randrange(N)
        steps.append((E.add(E.mul(c, P), E.mul(d, Q)), c, d))
    table: dict[Point, tuple[int, int]] = {}

    def done(k: int | None, walks: int) -> RhoResult:
        total = E.ops.group_ops - ops0
        ok = k is not None and E.mul(k, P) == Q
        return RhoResult(k, ok, total, walk_ops, total - walk_ops, walks, len(table),
                         dp_bits, time.perf_counter() - t0, True, look_ahead, escapes, canon)

    for walk in range(1, max_walks + 1):
        a, b = rng.randrange(N), rng.randrange(N)
        X = E.add(E.mul(a, P), E.mul(b, Q))
        canon += 1
        if X is not None and X[1] > half:
            X, a, b = (X[0], p - X[1]), N - a, N - b
        recent_x: list[int] = []  # the last CYCLE_WINDOW abscissae, oldest first
        recent: list[tuple[Point, int, int]] = []
        last_escape: int | None = None
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
            j = x % r
            M, c, d = steps[j]
            Y = E.add(X, M)
            walk_ops += 1
            canon += 1
            a, b = a + c, b + d
            if Y is not None and Y[1] > half:
                Y, a, b = (Y[0], p - Y[1]), -a, -b
                # Look-ahead: the flipped sum would take jump j again and come
                # straight back (a fruitless 2-cycle); take the next jump instead.
                tried = 1
                while Y[0] % r == j and tried < r:
                    look_ahead += 1
                    a, b = -a - c, -b - d
                    j = (j + 1) % r
                    M, c, d = steps[j]
                    Y = E.add(X, M)
                    walk_ops += 1
                    canon += 1
                    tried += 1
                    a, b = a + c, b + d
                    if Y is None or Y[1] <= half:
                        break
                    Y, a, b = (Y[0], p - Y[1]), -a, -b
            X = Y
            a, b = a % N, b % N
            if X is None:
                break
            x = X[0]
            if x in recent_x:
                pos = recent_x.index(x)
                i = min(range(pos, len(recent_x)), key=recent_x.__getitem__)
                if last_escape == recent_x[i]:
                    break  # the same cycle twice: abandon the walk
                last_escape = recent_x[i]
                mp, ma, mb = recent[i]
                X = E.add(mp, mp)
                walk_ops += 1
                escapes += 1
                a, b = 2 * ma % N, 2 * mb % N
                canon += 1
                if X is not None and X[1] > half:
                    X, a, b = (X[0], p - X[1]), N - a, N - b
                recent_x.clear()
                recent.clear()
                if X is None:
                    break
                x = X[0]
            recent_x.append(x)
            recent.append((X, a, b))
            if len(recent_x) > CYCLE_WINDOW:
                del recent_x[0], recent[0]
    return done(None, max_walks)


def _plain(E: Curve, P: Point, Q: Point, seed: int, r: int, dp_bits: int | None,
           max_walks: int) -> RhoResult:
    """The walk on points (A = 1), exactly as before the negation map."""
    N = E.order
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
