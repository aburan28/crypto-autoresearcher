"""
Exact group-order computation #E(F_p) via baby-step-giant-step within the
Hasse interval, using the classical "random point(s), intersect candidate
sets" method (see e.g. Washington, "Elliptic Curves: Number Theory and
Cryptography", ch. 4). No Schoof/SEA algorithm is used; this is the direct
BSGS-on-a-point method, which is O(p^{1/4}) time and exact -- not a
probabilistic estimate -- because the true group order N always satisfies
N*P = O for every P on the curve (Lagrange), so N is always a member of
every point's candidate set, and the intersection over enough independent
random points collapses to {N} except with negligible probability, which is
mitigated further by an explicit primality check + independent order
verification (see verify_group_order below).
"""
from __future__ import annotations
import math
import random
from .ecc import scalar_mult, point_add, point_neg, random_point, OpCounter


def _isqrt(n: int) -> int:
    return math.isqrt(n)


def bsgs_order_candidates(P, a: int, p: int, ctr: OpCounter = None):
    """Return the set of all N in the Hasse interval [p+1-t, p+1+t]
    (t = ceil(2*sqrt(p))) with N*P = O, via baby-step-giant-step.
    """
    if ctr is None:
        ctr = OpCounter()
    if P is None:
        return set(range(p + 1 - 0, p + 1 + 1))  # degenerate, unused in practice
    t_bound = _isqrt(4 * p) + 1
    L = p + 1
    m = _isqrt(2 * t_bound) + 1

    # baby steps: b*P for b in [0, m-1]. If P has order < m (never true of
    # a curve this driver ultimately accepts, since acceptance requires
    # prime N and every nonzero point then has order N; but arbitrary test
    # curves and rejected composite-order candidates can have small-order
    # points), R returns to the identity before the table fills, which
    # would silently collide dict keys and corrupt the match below. Detect
    # that directly: the first return to O reveals ord(P) exactly (the
    # smallest positive b with b*P = O), and every multiple of ord(P) in
    # the Hasse interval is then an exhaustively listed, exact candidate
    # set -- baby/giant matching is neither needed nor well-defined here.
    baby = {}
    R = None
    for b in range(m):
        if b > 0 and R is None:
            ord_P = b
            candidates = set()
            n = ((p + 1 - t_bound + ord_P - 1) // ord_P) * ord_P
            while n <= p + 1 + t_bound:
                if n > 0:
                    candidates.add(n)
                n += ord_P
            return candidates
        baby[R] = b
        R = point_add(R, P, a, p, ctr)

    negQ_base = point_neg(scalar_mult(L, P, a, p, ctr), p)  # -(L*P)

    candidates = set()
    # search a in range so that a*m covers [-t_bound - m, t_bound + m]
    a_min = -(t_bound // m) - 1
    a_max = (t_bound // m) + 1
    for aa in range(a_min, a_max + 1):
        shift = None if aa == 0 else point_neg(scalar_mult(aa * m, P, a, p, ctr), p)
        target = point_add(negQ_base, shift, a, p, ctr)
        if target in baby:
            b = baby[target]
            k = aa * m + b
            N = L + k
            if p + 1 - t_bound <= N <= p + 1 + t_bound and N > 0:
                # verify exactly (candidate set from baby/giant match can be a
                # false positive only if two matches collide by chance)
                if scalar_mult(N, P, a, p, ctr) is None:
                    candidates.add(N)
    return candidates


def compute_group_order(a: int, b: int, p: int, rng: random.Random, max_points: int = 6):
    """Compute #E(F_p) exactly by intersecting BSGS candidate sets from
    independent random points until exactly one candidate survives.
    Returns (N, ctr, points_used)."""
    ctr = OpCounter()
    candidate_set = None
    points_used = 0
    for _ in range(max_points):
        P = random_point(a, b, p, rng)
        points_used += 1
        cands = bsgs_order_candidates(P, a, p, ctr)
        if candidate_set is None:
            candidate_set = cands
        else:
            candidate_set &= cands
        if len(candidate_set) == 1:
            break
    if candidate_set is None or len(candidate_set) != 1:
        raise RuntimeError(
            f"group order did not converge to a unique candidate after {points_used} points: {candidate_set}"
        )
    N = next(iter(candidate_set))
    return N, ctr, points_used


def verify_group_order(N: int, a: int, b: int, p: int, rng: random.Random, trials: int = 3) -> bool:
    """Independent re-verification: for `trials` fresh random points,
    confirm N*P = O. Does not by itself prove minimality of N (that is
    established by the intersection procedure above / by N's primality --
    if N is prime and any point P != O satisfies N*P=O, ord(P) in {1,N},
    and ord(P)=1 only if P=O, which random_point excludes by construction
    since it always returns an affine point)."""
    ctr = OpCounter()
    for _ in range(trials):
        P = random_point(a, b, p, rng)
        if scalar_mult(N, P, a, p, ctr) is not None:
            return False
    return True
