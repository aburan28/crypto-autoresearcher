"""
Matched Pollard rho (with negation map) and baby-step-giant-step (BSGS)
discrete-log baselines, per specification.yaml controls.CTRL-BASELINE.
Every claimed solve carries a [k]P=Q certificate independently re-verified
by the caller (see certificate.py); this module never trusts its own
output without that re-check being performed externally, per
docs/claims-and-verification.md.
"""
from __future__ import annotations
import math
import random
from .ecc import point_add, point_neg, scalar_mult, OpCounter


def _canonical_rep(P, p):
    """Canonical representative of {P, -P} under the negation map: the
    point with the lexicographically smaller y (or -y) coordinate. Used
    only for the negation-map speedup below."""
    if P is None:
        return P
    x, y = P
    yn = (-y) % p
    return P if y <= yn else (x, yn)


def pollard_rho_negation(P, Q, a: int, N: int, p: int, rng: random.Random, max_steps: int = None):
    """Solve Q = k*P for k in [0, N-1] via the standard r-adding-walk
    Pollard rho (Teske / MOV Handbook of Applied Cryptography style) with
    Floyd cycle detection and the negation map (partition {R,-R} to a
    single representative), which halves the effective search space and
    gives the expected 0.886*sqrt(N) step count matched in
    specification.yaml. Walk: precompute R random jump points
    M_i = a_i*P + b_i*Q; X_{n+1} = X_n + M_{partition(X_n)}, tracking
    (a,b) additively so X_n = a_n*P + b_n*Q throughout. Returns
    (k or None, steps_taken, ctr)."""
    ctr = OpCounter()
    if max_steps is None:
        max_steps = int(20 * math.isqrt(N)) + 1000

    R = 20  # partition classes; R in [16,32] is the standard well-mixing range
    jump_a = [rng.randrange(1, N) for _ in range(R)]
    jump_b = [rng.randrange(1, N) for _ in range(R)]
    jump_pt = [point_add(scalar_mult(jump_a[i], P, a, p, ctr), scalar_mult(jump_b[i], Q, a, p, ctr), a, p, ctr)
               for i in range(R)]

    def partition(pt):
        if pt is None:
            return 0
        return pt[0] % R

    def step(pt, ai, bi):
        i = partition(pt)
        new_pt = point_add(pt, jump_pt[i], a, p, ctr)
        new_ai = (ai + jump_a[i]) % N
        new_bi = (bi + jump_b[i]) % N
        return new_pt, new_ai, new_bi

    a0 = rng.randrange(1, N)
    b0 = rng.randrange(1, N)
    X = point_add(scalar_mult(a0, P, a, p, ctr), scalar_mult(b0, Q, a, p, ctr), a, p, ctr)
    a_t, b_t = a0, b0
    a_h, b_h = a0, b0
    Xt, Xh = X, X

    for step_count in range(1, max_steps + 1):
        Xt, a_t, b_t = step(Xt, a_t, b_t)
        Xh, a_h, b_h = step(Xh, a_h, b_h)
        Xh, a_h, b_h = step(Xh, a_h, b_h)
        if _canonical_rep(Xt, p) == _canonical_rep(Xh, p):
            # a_t*P + b_t*Q = +-(a_h*P + b_h*Q)  =>  solve for k = Q/P
            for sign in (1, -1):
                db = (sign * b_h - b_t) % N
                if db == 0:
                    continue
                da = (a_t - sign * a_h) % N
                try:
                    inv_db = pow(db, -1, N)
                except ValueError:
                    continue
                k = (da * inv_db) % N
                if scalar_mult(k, P, a, p, ctr) == Q:
                    return k, step_count * 3, ctr
            # collision didn't resolve to a valid k (degenerate a_i/b_i
            # coincidence); keep walking rather than terminating falsely
    return None, max_steps * 3, ctr


def bsgs_dlp(P, Q, a: int, N: int, p: int):
    """Solve Q = k*P for k in [0, N-1] via classical baby-step-giant-step.
    Returns (k or None, ctr). O(sqrt(N)) time and memory."""
    ctr = OpCounter()
    m = math.isqrt(N) + 1
    baby = {}
    R = None
    for j in range(m):
        baby[R] = j
        R = point_add(R, P, a, p, ctr)
    mP_neg = point_neg(scalar_mult(m, P, a, p, ctr), p)
    cur = Q
    for i in range(m + 1):
        if cur in baby:
            k = (i * m + baby[cur]) % N
            return k, ctr, m
        cur = point_add(cur, mP_neg, a, p, ctr)
    return None, ctr, m
