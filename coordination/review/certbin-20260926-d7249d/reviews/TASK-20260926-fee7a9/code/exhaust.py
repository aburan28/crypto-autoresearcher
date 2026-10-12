"""Own exhaustive 2^20 evaluator of a 19 x 211 E_layout system (numpy bit-sliced).
Assignment u: bit i = v_i. Returns s and the solution list. No crypto_autoresearcher import."""
import numpy as np
from itertools import combinations
NV = 20
_u = np.arange(1 << NV, dtype=np.uint32)
_var = [np.packbits(((_u >> i) & 1).astype(np.uint8), bitorder='little').view(np.uint64) for i in range(NV)]
_ones = np.full(_var[0].shape, np.uint64(0xFFFFFFFFFFFFFFFF))
COLS = [_ones] + _var + [(_var[i] & _var[j]) for i, j in combinations(range(NV), 2)]
assert len(COLS) == 211
def solve(E_rows_int):
    """E_rows_int: 19 ints (bit j = column j). Returns (s, solutions)."""
    zero = _ones.copy()
    for x in E_rows_int:
        acc = np.zeros_like(_ones)
        j = 0
        while x:
            if x & 1:
                acc ^= COLS[j]
            x >>= 1
            j += 1
        zero &= ~acc
    s = int(np.bitwise_count(zero).sum())
    sols = []
    if s:
        bits = np.unpackbits(zero.view(np.uint8), bitorder='little')
        sols = np.flatnonzero(bits).tolist()
    return s, sols
