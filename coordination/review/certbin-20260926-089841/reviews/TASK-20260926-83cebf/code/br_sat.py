"""Exact satisfiability counts s (BR-4).

Route 1 (every system): exhaustive evaluation of the 17 descended equations
at all 2^18 assignments v (bit i of the assignment index u is v_i), with
bit-sliced monomial tables.
Route 1' (self-test only): a second exhaustive implementation with unpacked
integer matrices.
Route 2 (S_3 descents only): for each x_1 in V, solve S_3(x_1, x_2, x_R) = 0
for x_2 in F_2^17 by the quadratic formula / half-trace and count solutions
in V. It never touches the descended equations.
Route 3 (S_3 descents, extra): vectorized direct evaluation of S_3 over V x V.
"""
import numpy as np

import br_field as F
from br_system import E_MASKS, NV

_NU = 1 << NV
_MON = None


def _mon_table():
    global _MON
    if _MON is None:
        u = np.arange(_NU, dtype=np.uint64)
        var = []
        for i in range(NV):
            b = ((u >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
            var.append(np.packbits(b, bitorder="little").view(np.uint64).copy())
        allones = np.full(_NU // 64, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
        mon = np.empty((len(E_MASKS), _NU // 64), dtype=np.uint64)
        for c, m in enumerate(E_MASKS):
            acc = allones.copy()
            i = 0
            mm = m
            while mm:
                if mm & 1:
                    acc &= var[i]
                mm >>= 1
                i += 1
            mon[c] = acc
        _MON = mon
    return _MON


def zero_set(E):
    """Packed indicator of the common zeros of the rows of E (17 x 172)."""
    mon = _mon_table()
    z = np.full(_NU // 64, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
    for k in range(E.shape[0]):
        supp = np.flatnonzero(E[k])
        if supp.size == 0:
            continue
        eq = np.bitwise_xor.reduce(mon[supp], axis=0)
        z &= ~eq
    return z


def count_s(E, want_solutions=False):
    z = zero_set(E)
    s = int(np.bitwise_count(z).sum())
    if not want_solutions:
        return s, None
    bits = np.unpackbits(z.view(np.uint8), bitorder="little")
    sols = [int(x) for x in np.flatnonzero(bits)]
    return s, sols


def count_s_unpacked(E):
    """Second, independent exhaustive route (self-test)."""
    u = np.arange(_NU, dtype=np.int64)
    X = ((u[:, None] >> np.arange(NV)[None, :]) & 1).astype(np.int32)
    vals = np.empty((_NU, len(E_MASKS)), dtype=np.int32)
    for c, m in enumerate(E_MASKS):
        idx = [i for i in range(NV) if (m >> i) & 1]
        if not idx:
            vals[:, c] = 1
        else:
            vals[:, c] = np.prod(X[:, idx], axis=1)
    ev = (vals @ E.astype(np.int32).T) & 1
    return int(np.count_nonzero(~ev.any(axis=1)))


def oracle_A(xR, B, l=9):
    """Route 2: number of (x1, x2) in V x V with S_3(x1, x2, xR) = 0."""
    V = 1 << l
    count = 0
    xR2 = F.sqr(xR)
    for x1 in range(V):
        a = F.sqr(x1) ^ xR2
        b = F.mul(x1, xR)
        c = F.mul(F.sqr(x1), xR2) ^ B
        if a == 0 and b == 0:
            if c == 0:
                count += V
            continue
        if a == 0:
            x2 = F.div(c, b)
            if x2 < V:
                count += 1
            continue
        if b == 0:
            x2 = F.div(c, a)
            for _ in range(F.N - 1):
                x2 = F.sqr(x2)          # square root: (c/a)^{2^{16}}
            if x2 < V:
                count += 1
            continue
        cc = F.div(F.mul(a, c), F.sqr(b))
        roots = F.solve_quadratic_z(cc)
        ba = F.div(b, a)
        for z in roots:
            x2 = F.mul(ba, z)
            if x2 < V:
                count += 1
    return count


def direct_count_VxV(xR, B, l=9):
    """Route 3: vectorized direct evaluation of S_3 over V x V."""
    V = 1 << l
    x1 = np.repeat(np.arange(V, dtype=np.uint64), V)
    x2 = np.tile(np.arange(V, dtype=np.uint64), V)
    xr = np.uint64(xR)
    s = F.vmul(x1, x2) ^ F.vmul(x1, xr) ^ F.vmul(x2, xr)
    val = F.vmul(s, s) ^ F.vmul(F.vmul(x1, x2), xr) ^ np.uint64(B)
    return int(np.count_nonzero(val == 0))
