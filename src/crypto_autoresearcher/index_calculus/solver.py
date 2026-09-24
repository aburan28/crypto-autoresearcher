"""End-to-end index calculus for Q = kP on a prime-order curve E(F_p).

1. Build a factor base F (one point per +/- pair).
2. Relation collection: draw R = aP + bQ for random a, b and decompose
   R = sum s_i F_i, giving  sum s_i L_i - b k = a  (mod N).
3. Feed each relation straight into incremental elimination; stop at the
   first relation that determines k.
4. Verify kP = Q.

Every stage is charged in its own column: group operations (scalar
multiplications for the targets included), S_3 root solves (one modular
square root each), membership tests, and modular multiply-adds in the linear
algebra.  Wall time is reported per phase.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import asdict, dataclass

from .curve import Curve, Point
from .decompose import DecompStats, decompose
from .factor_base import FactorBase
from .linalg import EliminationState

FACTOR_BASES = ("small_x", "subgroup", "random")


@dataclass
class ICResult:
    k: int | None
    verified: bool
    m: int
    factor_base: dict
    relations: int
    rank: int
    attempts: int
    s3_solves: int
    membership_tests: int
    group_ops: int
    la_ops: int
    seconds_factor_base: float
    seconds_relations: float
    seconds_linalg: float
    seconds_total: float

    def to_dict(self) -> dict:
        return asdict(self)


def default_fb_size(N: int, m: int) -> int:
    """|F| giving about one decomposition per two attempts.

    A random target is a sum of m signed factor-base points with probability
    about (2|F|)^m / (m! N), so |F| = ((m! N) / 2)^(1/m) / 2.
    """
    return max(4, math.ceil((math.factorial(m) * N / 2) ** (1 / m) / 2))


def build_factor_base(E: Curve, kind: str, size: int, seed: int = 0) -> FactorBase:
    if kind == "small_x":
        return FactorBase.small_x(E, size)
    if kind == "subgroup":
        return FactorBase.subgroup(E, size, seed)
    if kind == "random":
        return FactorBase.random(E, size, seed)
    raise ValueError(f"unknown factor base {kind!r}; choose from {FACTOR_BASES}")


def solve_index_calculus(E: Curve, P: Point, Q: Point, m: int = 2,
                         fb_kind: str = "small_x", fb_size: int | None = None,
                         seed: int = 0, max_attempts: int | None = None) -> ICResult:
    N = E.order
    if N is None:
        raise ValueError("curve order must be known")
    if m < 2:
        raise ValueError("m must be >= 2")
    rng = random.Random(f"ic|{E.p}|{E.a}|{E.b}|{m}|{fb_kind}|{seed}")
    ops0 = E.ops.group_ops
    t0 = time.perf_counter()

    fb = build_factor_base(E, fb_kind, fb_size or default_fb_size(N, m), seed)
    t1 = time.perf_counter()

    stats = DecompStats()
    la = EliminationState(N)
    relations = 0
    k: int | None = None
    t_la = 0.0
    limit = max_attempts if max_attempts is not None else 50 * N
    while k is None and stats.attempts < limit:
        a, b = rng.randrange(N), rng.randrange(1, N)
        R = E.add(E.mul(a, P), E.mul(b, Q))
        rel = decompose(E, fb, R, m, stats)
        if rel is None:
            continue
        relations += 1
        coeffs: dict[int, int] = {}
        for i, s in rel:
            coeffs[i] = coeffs.get(i, 0) + s
        ta = time.perf_counter()
        k = la.add_row(coeffs, -b, a)
        t_la += time.perf_counter() - ta
    t2 = time.perf_counter()

    group_ops = E.ops.group_ops - ops0
    verified = k is not None and E.mul(k, P) == Q
    return ICResult(
        k=k, verified=verified, m=m, factor_base=fb.describe(),
        relations=relations, rank=la.rank, attempts=stats.attempts,
        s3_solves=stats.s3_solves, membership_tests=stats.membership_tests,
        group_ops=group_ops, la_ops=la.ops,
        seconds_factor_base=t1 - t0, seconds_relations=t2 - t1 - t_la,
        seconds_linalg=t_la, seconds_total=t2 - t0,
    )
