"""Boolean ring B = F_2[v_0..v_17]/(v_i^2 + v_i), own arithmetic.

A polynomial is a sorted numpy int64 array of distinct monomial masks (the
monomials with coefficient 1). Product of monomials = bitwise OR (v^2 = v).
Sum = symmetric difference (parity of multiplicities).
Imports nothing from this repository.
"""
import numpy as np

NV = 18
NA = 1 << NV
POP = np.array([bin(i).count("1") for i in range(NA)], dtype=np.int64)
EMPTY = np.zeros(0, dtype=np.int64)
ONE = np.zeros(1, dtype=np.int64)  # the constant monomial 1 (mask 0)


def parity_reduce(arr):
    """Multiset of monomials -> set of monomials with odd multiplicity."""
    arr = np.asarray(arr, dtype=np.int64)
    if arr.size == 0:
        return EMPTY
    if arr.size > 4096:
        c = np.bincount(arr, minlength=NA)
        return np.flatnonzero(c & 1).astype(np.int64)
    u, c = np.unique(arr, return_counts=True)
    return u[(c & 1) == 1].astype(np.int64)


def add(*polys):
    polys = [p for p in polys if p.size]
    if not polys:
        return EMPTY
    return parity_reduce(np.concatenate(polys))


def times_monomial(P, m):
    if P.size == 0:
        return EMPTY
    return parity_reduce(P | np.int64(m))


def times(P, Q):
    if P.size == 0 or Q.size == 0:
        return EMPTY
    return parity_reduce((P[:, None] | Q[None, :]).ravel())


def degree(P):
    if P.size == 0:
        return -1
    return int(POP[P].max())


def is_one(P):
    return P.size == 1 and int(P[0]) == 0


def from_list(monos):
    return parity_reduce(np.array(list(monos), dtype=np.int64))


def evaluate(P, u):
    """Value of P at assignment u (bit i of u = v_i)."""
    return int(np.count_nonzero((P & u) == P) & 1)


def selftest(rng, n=200):
    """Ring laws on random sparse polynomials, and evaluation is a ring map."""
    fails = 0
    for _ in range(n):
        def rp():
            return from_list(rng.randrange(NA) & rng.randrange(NA) & rng.randrange(NA)
                             for _ in range(rng.randrange(1, 12)))
        P, Q, R = rp(), rp(), rp()
        if not np.array_equal(times(P, Q), times(Q, P)):
            fails += 1
        if not np.array_equal(times(times(P, Q), R), times(P, times(Q, R))):
            fails += 1
        if not np.array_equal(times(P, add(Q, R)), add(times(P, Q), times(P, R))):
            fails += 1
        if not np.array_equal(times(P, P), P):  # idempotent ring: P^2 = P
            fails += 1
        j = rng.randrange(NV)
        if not np.array_equal(times_monomial(P, 1 << j), times(P, np.array([1 << j], dtype=np.int64))):
            fails += 1
        for _ in range(4):
            u = rng.randrange(NA)
            if evaluate(times(P, Q), u) != (evaluate(P, u) & evaluate(Q, u)):
                fails += 1
            if evaluate(add(P, Q), u) != (evaluate(P, u) ^ evaluate(Q, u)):
                fails += 1
    return {"cases": n, "failures": fails, "pass": fails == 0}
