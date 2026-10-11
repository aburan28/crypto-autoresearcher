"""Exhaustive satisfiability over all 2^18 assignments (bit i of u = v_i).

Bit-sliced: every one of the 172 monomials is a packed truth table of 2^18
bits (4096 uint64 words); a row's value table is the XOR of the tables of its
monomials; the solution set is the complement of the OR over rows.
"""
from __future__ import annotations

import numpy as np

from common import COLS, NCOL, NV

NA = 1 << NV
NW = NA // 64


def _var_tables():
    u = np.arange(NA, dtype=np.uint64)
    V = np.empty((NV, NW), dtype=np.uint64)
    for i in range(NV):
        bits = ((u >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
        V[i] = np.packbits(bits, bitorder="little").view(np.uint64)
    return V


_V = _var_tables()
MT = np.empty((NCOL, NW), dtype=np.uint64)
for _j, _m in enumerate(COLS):
    if len(_m) == 0:
        MT[_j] = np.uint64(0xFFFFFFFFFFFFFFFF)
    elif len(_m) == 1:
        MT[_j] = _V[_m[0]]
    else:
        MT[_j] = _V[_m[0]] & _V[_m[1]]


def _bits(r):
    out = []
    while r:
        b = (r & -r).bit_length() - 1
        out.append(b)
        r &= r - 1
    return out


def bad_table(rows):
    bad = np.zeros(NW, dtype=np.uint64)
    for r in rows:
        idx = _bits(r)
        if not idx:
            continue
        bad |= np.bitwise_xor.reduce(MT[idx], axis=0)
    return bad


def count_solutions(rows, want_solutions=True):
    """-> (s, sorted list of solutions as 18-bit ints or None)."""
    good = ~bad_table(rows)
    s = int(np.bitwise_count(good).sum())
    sols = None
    if want_solutions:
        bits = np.unpackbits(good.view(np.uint8), bitorder="little")
        sols = np.flatnonzero(bits).tolist()
    return s, sols
