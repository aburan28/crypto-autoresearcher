"""Exhaustive 2^18 evaluator for a 17 x 172 Boolean system (own code).

Assignment u in [0, 2^18): bit i of u = v_i. For each of the 172 layout
monomials m the truth table [(u & m) == m] is bit-packed (bit u of the packed
vector). Equation k's truth table is the XOR of its columns' tables; the
solution set is the complement of the OR over k. Also a naive per-assignment
evaluator for cross-checks. Imports nothing from this repository.
"""
import numpy as np

from layout import COL_MASKS, NCOL, NEQ, NV

NA = 1 << NV
NW = NA // 64


def _build_table():
    u = np.arange(NA, dtype=np.int64)
    tab = np.empty((NCOL, NW), dtype=np.uint64)
    for c, m in enumerate(COL_MASKS):
        bits = (u & m) == m
        tab[c] = np.packbits(bits, bitorder="little").view("<u8")
    return tab


TABLE = _build_table()


def row_truth(row):
    cols = [j for j in range(NCOL) if (row >> j) & 1]
    if not cols:
        return np.zeros(NW, dtype=np.uint64)
    return np.bitwise_xor.reduce(TABLE[cols], axis=0)


def solutions(rows):
    """Returns (s, sorted solution array)."""
    orv = np.zeros(NW, dtype=np.uint64)
    for r in rows:
        orv |= row_truth(r)
    sol = ~orv
    bits = np.unpackbits(sol.view(np.uint8), bitorder="little")
    idx = np.flatnonzero(bits)
    return int(idx.size), idx


def naive_eval(rows, u):
    """Vector of the 17 equation values at assignment u, per monomial."""
    out = []
    for r in rows:
        v = 0
        j = 0
        rr = r
        while rr:
            if rr & 1:
                m = COL_MASKS[j]
                if (u & m) == m:
                    v ^= 1
            rr >>= 1
            j += 1
        out.append(v)
    return out


def selftest(rng, n_systems=200, n_points=64):
    """Packed evaluator against naive per-assignment evaluation on random
    systems; includes systems with planted solutions."""
    fails = 0
    for t in range(n_systems):
        rows = [rng.getrandbits(NCOL) for _ in range(NEQ)]
        if t % 2 == 0:
            # plant a solution: fix constants so that u0 satisfies all rows
            u0 = rng.randrange(NA)
            vals = naive_eval(rows, u0)
            rows = [r ^ v for r, v in zip(rows, vals)]  # flip constant bit (col 0)
        s, idx = solutions(rows)
        idxset = set(idx.tolist())
        pts = [rng.randrange(NA) for _ in range(n_points)] + idx.tolist()[:16]
        if t % 2 == 0:
            pts.append(u0)
            if u0 not in idxset:
                fails += 1
        for u in pts:
            is_sol = not any(naive_eval(rows, u))
            if is_sol != (u in idxset):
                fails += 1
    return {"systems": n_systems, "failures": fails, "pass": fails == 0}
