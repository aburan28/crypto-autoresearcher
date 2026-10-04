"""RC-B: the ell-substituted system (specification object.rc_b (1)-(4)).

(1) left kernel of the 17 x 153 quadratic-column submatrix (own elimination);
(2) ell = sum_k c_k f_k;
(3) zero linear part -> REFUTED-AT-DEGREE-2 / ELL-TRIVIAL (not substituted);
(4) j* = least index in ell's linear support; pi sets v_{j*} := ell + v_{j*};
    the remaining 17 variables are relabelled 0..16 in ascending order;
    pi(f_k) is reduced multilinearly (degree <= 2).
The substituted equations are returned as engine eqs (lists of 17-variable
monomial masks) for Closure(17, D, 17).
"""
from __future__ import annotations

from common import COLS, NEQ, NV, QUAD_MASK


def left_kernel(rows, colmask=QUAD_MASK):
    """Basis of {c in F_2^17 : sum_k c_k (row_k & colmask) = 0}, as 17-bit ints."""
    piv = []  # list of (vec, comb) in echelon by highest bit
    kern = []
    for k, r in enumerate(rows):
        v = r & colmask
        comb = 1 << k
        for pv, pc in piv:
            if v >> (pv.bit_length() - 1) & 1:
                v ^= pv
                comb ^= pc
        if v == 0:
            kern.append(comb)
        else:
            piv.append((v, comb))
            piv.sort(key=lambda t: -t[0].bit_length())
    return kern


def combine(rows, c):
    e = 0
    for k in range(NEQ):
        if (c >> k) & 1:
            e ^= rows[k]
    return e


def ell_info(rows):
    """-> dict with kernel_dim, c (17-bit int or None), ell (172-bit int or
    None), label, j_star, ell_linear_support (list of var indices), ell_const."""
    kern = left_kernel(rows)
    info = {"kernel_dim": len(kern)}
    if len(kern) != 1:
        info.update(label=f"not applicable (kernel dim {len(kern)})", c=None, ell=None,
                    j_star=None, ell_linear_support=None, ell_const=None, substituted=False)
        return info
    c = kern[0]
    ell = combine(rows, c)
    assert ell & QUAD_MASK == 0
    lin = [i for i in range(NV) if (ell >> (1 + i)) & 1]
    const = ell & 1
    info.update(c=c, ell=ell, ell_linear_support=lin, ell_const=const)
    if not lin:
        info.update(label="REFUTED-AT-DEGREE-2" if const else "ELL-TRIVIAL", j_star=None,
                    substituted=False)
    else:
        info.update(label="SUBSTITUTED", j_star=lin[0], substituted=True)
    return info


def substitute(rows, info):
    """pi(f_k) for k = 0..16 -> eqs over 17 variables (masks), plus the list of
    per-equation monomial sets in the ORIGINAL 18-variable masks (for checks)."""
    js = info["j_star"]
    ell = info["ell"]
    # L = ell + v_{j*}: terms as 18-var masks (0 = constant)
    Lterms = []
    if ell & 1:
        Lterms.append(0)
    for i in info["ell_linear_support"]:
        if i != js:
            Lterms.append(1 << i)
    bj = 1 << js
    out18 = []
    for r in rows:
        acc = {}
        x = r
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            m = 0
            for i in COLS[b]:
                m |= 1 << i
            if m & bj:
                rest = m & ~bj
                for t in Lterms:
                    mm = rest | t
                    acc[mm] = acc.get(mm, 0) ^ 1
            else:
                acc[m] = acc.get(m, 0) ^ 1
        out18.append(sorted(m for m, p in acc.items() if p))
    # relabel
    keep = [i for i in range(NV) if i != js]
    newidx = {i: n for n, i in enumerate(keep)}

    def relabel(m):
        s = 0
        for i in keep:
            if (m >> i) & 1:
                s |= 1 << newidx[i]
        return s

    eqs17 = [[relabel(m) for m in f] for f in out18]
    for f in eqs17:
        for m in f:
            assert bin(m).count("1") <= 2
    return eqs17, out18
