#!/usr/bin/env python3
"""Independent builder for the EXP-PFDR-20ee58 chained digit twin and for the
red team's planted-syzygy / nearby objects (TASK-20260904-0d66e3).

Written from the definition in the handoff's review_plan.blind_rederivation and
H-PFDR-9aadc0 (S1)-(S4); NOT imported from experiments/EXP-PFDR-20ee58/run_experiment.py.
Uses harness/macaulay_fp only as the linear-algebra / ring layer (meter snapshot
commit 2d2083e5; per-file sha256 recorded in the report).

Ring: mixed, n_sq = 3*s squarefree digit variables a_{k,i} (index (k-1)*s + i),
one free variable u.  Leaves x_k = sum_i 2^i a_{k,i}.
  E1 = S_3(x_1, x_2, u)      E2 = S_3(u, x_3, x_R)
"""
from __future__ import annotations

import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher")

from harness.macaulay_fp import Ring  # noqa: E402


def s3(ring: Ring, X1, X2, X3, A: int, B: int):
    """S_3(X1,X2,X3) = (X1-X2)^2 X3^2 - 2((X1+X2)(X1 X2 + A) + 2B) X3
                       + (X1 X2 - A)^2 - 4B (X1 + X2)   (harness/semaev.py::s3_expr)."""
    d = ring.sub(X1, X2)
    t1 = ring.mul(ring.mul(d, d), ring.mul(X3, X3))
    sm = ring.add(X1, X2)
    pr = ring.mul(X1, X2)
    inner = ring.add(ring.mul(sm, ring.add(pr, ring.constant(A))), ring.constant(2 * B))
    t2 = ring.scale(ring.mul(inner, X3), -2)
    r = ring.sub(pr, ring.constant(A))
    t3 = ring.mul(r, r)
    t4 = ring.scale(sm, -4 * B)
    return ring.add(ring.add(t1, t2), ring.add(t3, t4))


def leaf(ring: Ring, k: int, s: int):
    """x_k = sum_{i<s} 2^i a_{k,i}; k in {1,2,3}; digit index (k-1)*s + i."""
    out = {}
    for i in range(s):
        out = ring.add(out, {ring.sq_var((k - 1) * s + i): pow(2, i, ring.p)})
    return out


def twin_generators(p: int, s: int, A: int, B: int, x_R: int):
    ring = Ring(p, 3 * s, 1)
    u = {ring.free_var(0): 1}
    x1, x2, x3 = (leaf(ring, k, s) for k in (1, 2, 3))
    E1 = s3(ring, x1, x2, u, A, B)
    E2 = s3(ring, u, x3, ring.constant(x_R), A, B)
    return ring, [E1, E2]
