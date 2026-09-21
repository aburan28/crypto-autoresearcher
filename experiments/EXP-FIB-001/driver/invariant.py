"""The n_R fiber invariant: number of unordered factor-base 3-subsets whose
canonical-sign sum equals R, from a per-curve enumeration table of C(B,3)
tuple sums. Public data only (curve, factor base, tuple sums) -- no secret
scalar is used anywhere in this module.
"""
from __future__ import annotations

import itertools
import time
from collections import Counter

from .common import seeded_rng
from .instances import CurveContext


def build_table_exact(ctx: CurveContext) -> tuple[Counter, int]:
    """Exact C(B,3) enumeration table: point -> count. Returns (table, n_evals)."""
    E = ctx.E
    table: Counter = Counter()
    n = 0
    for i, j, k in itertools.combinations(range(ctx.B), 3):
        p1, p2, p3 = ctx.V_canon[i], ctx.V_canon[j], ctx.V_canon[k]
        s = E.add(E.add(p1, p2), p3)
        table[s] += 1
        n += 1
    return table, n


def build_table_sampled(ctx: CurveContext, max_evals: int, time_budget_s: float,
                         seed_tag: str = "invariant_sample") -> dict:
    """Sampled enumeration: uniform random unordered index-triples, i.i.d.,
    up to max_evals or time_budget_s (whichever first). Returns a dict with
    the table, n_evals actually performed, and the stop reason.
    """
    E = ctx.E
    rng = seeded_rng(ctx.spec["seed"], f"{ctx.spec['id']}:{seed_tag}")
    table: Counter = Counter()
    n = 0
    t0 = time.perf_counter()
    stop_reason = "max_evals"
    B = ctx.B
    idx_range = range(B)
    while n < max_evals:
        if n % 200000 == 0 and (time.perf_counter() - t0) >= time_budget_s:
            stop_reason = "time_budget"
            break
        i, j, k = rng.sample(idx_range, 3)
        p1, p2, p3 = ctx.V_canon[i], ctx.V_canon[j], ctx.V_canon[k]
        s = E.add(E.add(p1, p2), p3)
        table[s] += 1
        n += 1
    wall = time.perf_counter() - t0
    return {"table": table, "n_evals": n, "stop_reason": stop_reason, "wall_seconds": wall}


def n_R_exact(table: Counter, R) -> int:
    return table.get(R, 0)


def independent_exact_count(ctx: CurveContext, R) -> int:
    """CTRL-EXHAUSTIVE-TRUTH: an independently-coded exact count of 3-subsets
    summing to R, deliberately not reusing the shared table (fresh canonical
    lift, direct comparison per triple) so the audit is a genuine cross-check
    of the n_R instrument, not a tautology.
    """
    E = ctx.E
    count = 0
    V = ctx.V
    pts = [None] * len(V)
    for idx, x in enumerate(V):
        pt = E.lift_x(x)
        if pt is None:
            continue
        y = pt[1]
        pts[idx] = (x, min(y, (-y) % E.p))
    for i, j, k in itertools.combinations(range(len(V)), 3):
        p1, p2, p3 = pts[i], pts[j], pts[k]
        if p1 is None or p2 is None or p3 is None:
            continue
        s = E.add(E.add(p1, p2), p3)
        if s == R:
            count += 1
    return count


def n_R_sampled_estimate(sample_table: dict, R, B: int) -> dict:
    """Estimate n_R from a sampled table: rate = hits/n_evals scaled by C(B,3);
    a 95% CI via the normal approximation to a Poisson-thinned binomial count
    of hits (honest: attenuates toward the null, per the frozen sample-size
    justification, never toward the claim).
    """
    from math import comb, sqrt
    n_evals = sample_table["n_evals"]
    hits = sample_table["table"].get(R, 0)
    CB3 = comb(B, 3)
    if n_evals == 0:
        return {"estimate": 0.0, "ci_low": 0.0, "ci_high": 0.0, "hits": 0, "n_evals": 0}
    rate = hits / n_evals
    est = rate * CB3
    # Poisson approx on the count of hits itself, scaled.
    se_hits = sqrt(max(hits, 1))
    se_est = se_hits * (CB3 / n_evals)
    return {"estimate": est, "ci_low": max(0.0, est - 1.96 * se_est),
            "ci_high": est + 1.96 * se_est, "hits": hits, "n_evals": n_evals}
