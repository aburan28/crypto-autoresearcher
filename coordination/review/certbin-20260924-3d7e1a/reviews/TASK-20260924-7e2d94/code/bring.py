"""The Boolean ring B = F_2[v_0..v_17]/(v_i^2 + v_i) and three certificate checkers.

TASK-20260924-7e2d94. A monomial is an 18-bit mask; a polynomial is a set of
masks. The monomial product is bitwise OR (v_i^2 = v_i); addition is XOR
(symmetric difference).

The claim checked for a certificate C = [(mu, k), ...] on a system f_0..f_16:
    sum_{(mu,k) in C} mu * f_k == 1   in B.

Three checkers, required to agree:
  A  literal: pure-Python toggling of monomials in a set;
  B  numpy: parity of monomial counts via bincount over the 2^18 masks;
  C  function space: B is isomorphic to the ring of all functions
     F_2^18 -> F_2 (multilinear polynomials <-> truth tables), so the identity
     holds iff it holds at every one of the 2^18 Boolean points. Evaluated on
     bit-packed truth tables; independent of monomial arithmetic.
"""
import numpy as np

NV = 18
NPTS = 1 << NV


def popcount(m):
    return bin(m).count("1")


def mask_of(mu):
    """mu: iterable of variable indices. Returns (mask, problems list)."""
    problems = []
    m = 0
    seen = set()
    prev = -1
    for i in mu:
        if not isinstance(i, int) or i < 0 or i >= NV:
            problems.append("index_out_of_range")
            continue
        if i in seen:
            problems.append("repeated_index")
        if i <= prev:
            problems.append("not_strictly_ascending")
        seen.add(i)
        prev = i
        m |= 1 << i
    return m, problems


def mask_to_list(m):
    return [i for i in range(NV) if (m >> i) & 1]


# ------------------------------------------------------------------ ring operations
def badd(p, q):
    return set(p) ^ set(q)


def bmul(p, q):
    r = set()
    for a in p:
        for b in q:
            x = a | b
            if x in r:
                r.remove(x)
            else:
                r.add(x)
    return r


def beval(p, v):
    """Evaluate polynomial p at the Boolean point v (an 18-bit int)."""
    s = 0
    for m in p:
        if m & v == m:
            s ^= 1
    return s


# ------------------------------------------------------------------ checker A
def residual_A(C_masks, f):
    """C_masks: list of (mu_mask, k); f: list of 17 sets. Returns the sum as a set."""
    acc = set()
    for mu, k in C_masks:
        for t in f[k]:
            x = mu | t
            if x in acc:
                acc.remove(x)
            else:
                acc.add(x)
    return acc


# ------------------------------------------------------------------ checker B
def f_arrays(f):
    return [np.fromiter(sorted(e), dtype=np.int64, count=len(e)) for e in f]


def residual_B(C_masks, farr):
    parts = []
    for mu, k in C_masks:
        a = farr[k]
        if a.size:
            parts.append(a | mu)
    if not parts:
        return set()
    allm = np.concatenate(parts)
    cnt = np.bincount(allm, minlength=NPTS)
    return set(np.nonzero(cnt & 1)[0].tolist())


# ------------------------------------------------------------------ checker C
_V = np.arange(NPTS, dtype=np.uint32)
VAR = [np.packbits(((_V >> i) & 1).astype(bool)) for i in range(NV)]
ONES = np.full(NPTS // 8, 0xFF, dtype=np.uint8)
ZEROS = np.zeros(NPTS // 8, dtype=np.uint8)
_mono_cache = {}


def eval_mono(m):
    e = _mono_cache.get(m)
    if e is None:
        e = ONES.copy()
        for i in range(NV):
            if (m >> i) & 1:
                e &= VAR[i]
        if popcount(m) <= 3:                 # at most 988 cached masks (~32 MB)
            _mono_cache[m] = e
    return e


def eval_poly(p):
    acc = ZEROS.copy()
    for m in p:
        acc ^= eval_mono(m)
    return acc


def truth_tables(f):
    return [eval_poly(e) for e in f]


def truth_tables_from_values(vals, nbits=17):
    """Bit k of the direct F_2^17 evaluation, packed, for k = 0..nbits-1."""
    return [np.packbits(((vals >> np.uint64(k)) & np.uint64(1)).astype(bool)) for k in range(nbits)]


def check_C(C_masks, tt):
    acc = ZEROS.copy()
    for mu, k in C_masks:
        acc ^= eval_mono(mu) & tt[k]
    return bool(np.array_equal(acc, ONES)), acc


def count_solutions(tt):
    """Number of Boolean points where every f_k vanishes."""
    orv = ZEROS.copy()
    for t in tt:
        orv |= t
    nz = int(np.unpackbits(orv).sum())
    return NPTS - nz


def solutions(tt, limit=8):
    orv = ZEROS.copy()
    for t in tt:
        orv |= t
    bits = np.unpackbits(orv)
    idx = np.nonzero(bits == 0)[0][:limit]
    return [int(x) for x in idx]


def vanishes_identically(mu, tt_k):
    """True iff mu * f_k is the zero function (hence zero in B)."""
    return not bool(np.any(eval_mono(mu) & tt_k))
