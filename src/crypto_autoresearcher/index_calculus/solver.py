"""End-to-end index calculus for Q = kP on a prime-order curve E(F_p).

1. Build a factor base F (one point per +/- pair).
2. Relation collection: draw R = aP + bQ for random a, b and decompose
   R = sum s_i F_i, giving  sum s_i L_i - b k = a  (mod N).
3. Feed each relation straight into incremental elimination; stop at the
   first relation that determines k.
4. Verify kP = Q.

Decomposition runs on one of two engines: ``enumerate`` (exhaustive S_3
search, decompose.py) or ``msolve`` (Groebner bases, msolve.py).  Every stage
is charged in its own column: S_3 root solves, membership tests, group
operations split into target generation (the scalar multiplications for
aP + bQ) and decomposition, modular multiply-adds in the linear algebra, and
for msolve the solver's wall time.  Wall time is reported per phase.
"""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass

from .curve import Curve, Point
from .decompose import DecompStats, decompose, use_acceleration
from .factor_base import FACTOR_BASES, FactorBase, build_factor_base, default_fb_size
from .linalg import EliminationState

ENGINES = ("enumerate", "msolve")
__all__ = ["ENGINES", "FACTOR_BASES", "ICResult", "build_factor_base",
           "default_fb_size", "solve_index_calculus"]


@dataclass
class ICResult:
    k: int | None
    verified: bool
    m: int
    engine: str
    accelerated: bool
    factor_base: dict
    relations: int
    rank: int
    attempts: int
    s3_solves: int
    membership_tests: int
    group_ops: int
    target_ops: int
    la_ops: int
    msolve_calls: int
    msolve_seconds: float
    censored_attempts: int
    seconds_factor_base: float
    seconds_relations: float
    seconds_linalg: float
    seconds_total: float

    def to_dict(self) -> dict:
        return asdict(self)


def solve_index_calculus(E: Curve, P: Point, Q: Point, m: int = 2,
                         fb_kind: str = "small_x", fb_size: int | None = None,
                         seed: int = 0, max_attempts: int | None = None,
                         engine: str = "enumerate", accelerate: bool | None = None,
                         factor_base: FactorBase | None = None,
                         msolve_timeout: float | None = 600.0) -> ICResult:
    N = E.order
    if N is None:
        raise ValueError("curve order must be known")
    if m < 2:
        raise ValueError("m must be >= 2")
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}; choose from {ENGINES}")
    rng = random.Random(f"ic|{E.p}|{E.a}|{E.b}|{m}|{fb_kind}|{seed}")
    ops0 = E.ops.group_ops
    t0 = time.perf_counter()

    fb = factor_base
    if fb is None:
        fb = build_factor_base(E, fb_kind, fb_size or default_fb_size(N, m), seed)
    accel = engine == "enumerate" and use_acceleration(fb, accelerate)
    t1 = time.perf_counter()

    stats = DecompStats()
    la = EliminationState(N)
    relations = target_ops = msolve_calls = censored = 0
    msolve_seconds = 0.0
    k: int | None = None
    t_la = 0.0
    limit = max_attempts if max_attempts is not None else 50 * N
    while k is None and stats.attempts < limit:
        a, b = rng.randrange(N), rng.randrange(1, N)
        before = E.ops.group_ops
        R = E.add(E.mul(a, P), E.mul(b, Q))
        target_ops += E.ops.group_ops - before
        if engine == "enumerate":
            rel = decompose(E, fb, R, m, stats, accelerate=accel)
        else:
            rel = _msolve_attempt(E, fb, R, m, seed, stats, msolve_timeout)
            msolve_calls += rel[1]
            msolve_seconds += rel[2]
            censored += rel[3]
            rel = rel[0]
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
        k=k, verified=verified, m=m, engine=engine, accelerated=accel,
        factor_base=fb.describe(), relations=relations, rank=la.rank,
        attempts=stats.attempts, s3_solves=stats.s3_solves,
        membership_tests=stats.membership_tests, group_ops=group_ops,
        target_ops=target_ops, la_ops=la.ops, msolve_calls=msolve_calls,
        msolve_seconds=msolve_seconds, censored_attempts=censored,
        seconds_factor_base=t1 - t0, seconds_relations=t2 - t1 - t_la,
        seconds_linalg=t_la, seconds_total=t2 - t0,
    )


def _msolve_attempt(E, fb, R, m, seed, stats, timeout):
    """One msolve decomposition attempt: (relation | None, runs, seconds, censored)."""
    from .msolve import decompose_msolve

    stats.attempts += 1
    if R is None:
        return None, 0, 0.0, 0
    out = decompose_msolve(E, fb, R, m, seed=seed, timeout=timeout)
    if out.status not in ("ok", "no_solution"):
        # Timeouts and solver failures are censored, never read as "no relation".
        return None, out.runs, out.seconds, 1
    if not out.relations:
        return None, out.runs, out.seconds, 0
    stats.successes += 1
    return list(out.relations[0]), out.runs, out.seconds, 0
