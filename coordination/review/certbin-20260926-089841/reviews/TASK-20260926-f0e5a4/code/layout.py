"""E_layout (EXP-CERTBIN-ddfe75 object.E_layout), written from the text.

A system is a 17 x 172 F_2 matrix E. Row k is f_k. Column j is the j-th
monomial of mu_order(2, 18): degree ascending, then ascending sorted index
tuple. Column 0 = constant, 1..18 = v_0..v_17, 19..171 = the 153 pairs.
E_hex is a list of 17 hex integers, bit j (LSB first) = column j.

Monomials are represented as 18-bit masks, bit i <-> v_i.
Imports nothing from this repository.
"""
from itertools import combinations

NV = 18
NEQ = 17


def mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        for tup in combinations(range(nv), d):  # ascending sorted tuples, lexicographic
            out.append(tup)
    return out


COL_TUPLES = mu_order(2, NV)
NCOL = len(COL_TUPLES)
assert NCOL == 172


def tup_to_mask(t):
    m = 0
    for i in t:
        m |= 1 << i
    return m


COL_MASKS = [tup_to_mask(t) for t in COL_TUPLES]
MASK_TO_COL = {m: j for j, m in enumerate(COL_MASKS)}

CONST_COLS = [0]
LINEAR_COLS = list(range(1, 19))
QUAD_COLS = list(range(19, 172))
BILINEAR_COLS = [MASK_TO_COL[(1 << i) | (1 << (9 + j))] for i in range(9) for j in range(9)]


def colset_mask(cols):
    m = 0
    for j in cols:
        m |= 1 << j
    return m


CONST_MASK = colset_mask(CONST_COLS)
LINEAR_MASK = colset_mask(LINEAR_COLS)
LOW_MASK = CONST_MASK | LINEAR_MASK          # columns 0..18
QUAD_MASK = colset_mask(QUAD_COLS)           # columns 19..171
BILINEAR_MASK = colset_mask(BILINEAR_COLS)
ALL_MASK = (1 << NCOL) - 1


def decode_rows(E_hex):
    """17 hex strings -> 17 row ints (bit j = column j)."""
    if len(E_hex) != NEQ:
        raise ValueError("E_hex has %d rows, expected 17" % len(E_hex))
    rows = [int(h, 16) for h in E_hex]
    for r in rows:
        if r >> NCOL:
            raise ValueError("E_hex row has a bit beyond column 171")
    return rows


def row_monomials(row):
    """Row int -> list of monomial masks (the Boolean polynomial f_k)."""
    out = []
    j = 0
    r = row
    while r:
        if r & 1:
            out.append(COL_MASKS[j])
        r >>= 1
        j += 1
    return out


def monomials_to_row(monos):
    r = 0
    for m in monos:
        r ^= 1 << MASK_TO_COL[m]
    return r


def encode_hex(row):
    return format(row, "x")


def mask_to_idx(m):
    return [i for i in range(NV) if (m >> i) & 1]
