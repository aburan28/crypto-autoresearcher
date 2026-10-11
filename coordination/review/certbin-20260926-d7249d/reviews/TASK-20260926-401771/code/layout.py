"""Monomial orders and the E_layout codec, rebuilt from the text.

Monomials of B = F_2[v_0..v_19]/(v_i^2 + v_i) are encoded as 20-bit masks,
bit i set iff v_i divides the monomial.

* mu_order(d, nv): "degree ascending, then ascending sorted index tuple"
  (EXP-CERTBIN-060020 object.E_layout; EXP-CERTBIN-4e92d7 macaulay_matrix).
* E_layout: a system is a 19 x 211 F_2 matrix; column j is the j-th monomial
  of mu_order(2, 20); E_hex is a list of 19 hex integers, bit j (LSB first) =
  column j.
* ann_order(4, 20): "all multilinear monomials of degree <= 4 in v_0..v_19
  sorted by (-degree, bitmask ascending)" (FORMAT ann-v1), 6196 coordinates,
  constant last.
"""
from itertools import combinations

import numpy as np

NV = 20
NEQ = 19


def popcount(m):
    return bin(m).count("1")


def mask_of(idx):
    m = 0
    for i in idx:
        m |= 1 << i
    return m


def mu_order(d, nv=NV):
    """List of sorted index tuples, degree ascending then lexicographic."""
    out = []
    for deg in range(d + 1):
        out.extend(combinations(range(nv), deg))  # itertools yields lexicographic order
    return out


def ann_order(d=4, nv=NV):
    masks = [mask_of(t) for t in mu_order(d, nv)]
    return sorted(masks, key=lambda m: (-popcount(m), m))


# E_layout columns
E_COLS = mu_order(2, NV)               # 211 tuples
E_MASKS = [mask_of(t) for t in E_COLS]  # 211 masks
assert len(E_COLS) == 211 and E_COLS[0] == () and E_COLS[1] == (0,) and E_COLS[20] == (19,)
assert E_COLS[21] == (0, 1) and E_COLS[210] == (18, 19)
E_COL_OF_MASK = {m: j for j, m in enumerate(E_MASKS)}

# ann-v1 coordinates
ANN_MASKS = ann_order(4, NV)
NCOL4 = len(ANN_MASKS)  # 6196
assert NCOL4 == 6196
ANN_COL_OF_MASK = np.full(1 << NV, -1, dtype=np.int32)
ANN_COL_OF_MASK[np.array(ANN_MASKS, dtype=np.int64)] = np.arange(NCOL4, dtype=np.int32)
ANN_MASK_OF_COL = np.array(ANN_MASKS, dtype=np.int32)
ANN_DEG_OF_COL = np.array([popcount(m) for m in ANN_MASKS], dtype=np.int32)
CONST_COL = NCOL4 - 1
assert ANN_MASKS[CONST_COL] == 0
# first coordinate is v_0v_1v_2v_3 (mask 15), degree-3 block starts at 4845
DEG3_START = int(np.flatnonzero(ANN_DEG_OF_COL <= 3)[0])
assert ANN_MASKS[0] == 15 and DEG3_START == 4845 and NCOL4 - DEG3_START == 1351
WORDS4 = (NCOL4 + 63) // 64  # 97

def popcount_table(nv=NV):
    x = np.arange(1 << nv, dtype=np.uint32)
    c = np.zeros(1 << nv, dtype=np.uint8)
    for i in range(nv):
        c += ((x >> i) & 1).astype(np.uint8)
    return c


POP = popcount_table(NV)


def decode_E(E_hex):
    """E_hex (19 hex strings) -> 19 x 211 uint8 matrix. Raises if a row has a
    bit at a column >= 211 or the row count is not 19."""
    if len(E_hex) != NEQ:
        raise ValueError("E_hex must have 19 rows")
    E = np.zeros((NEQ, 211), dtype=np.uint8)
    for k, h in enumerate(E_hex):
        v = int(h, 16)
        if v >> 211:
            raise ValueError("row %d has a bit beyond column 210" % k)
        for j in range(211):
            if (v >> j) & 1:
                E[k, j] = 1
    return E


def encode_E(E):
    out = []
    for k in range(E.shape[0]):
        v = 0
        for j in range(E.shape[1]):
            if E[k, j]:
                v |= 1 << j
        out.append(format(v, "x"))
    return out


def rows_as_masks(E):
    """List (per equation k) of numpy int64 arrays of monomial masks of f_k."""
    em = np.array(E_MASKS, dtype=np.int64)
    return [em[np.flatnonzero(E[k])] for k in range(E.shape[0])]


def anf_u32(E):
    """Packed ANF: a[m] bit k = coefficient of monomial m in f_k."""
    a = np.zeros(1 << NV, dtype=np.uint32)
    em = np.array(E_MASKS, dtype=np.int64)
    for k in range(E.shape[0]):
        for m in em[np.flatnonzero(E[k])]:
            a[m] ^= np.uint32(1 << k)
    return a
