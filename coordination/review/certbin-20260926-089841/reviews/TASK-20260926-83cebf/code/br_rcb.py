"""object.rc_b of EXP-CERTBIN-ddfe75, steps (1)-(5), from the text alone.

(1) left kernel of the 17 x 153 quadratic-column submatrix (own elimination);
    if its dimension is not 1: "not applicable (kernel dim d)".
(2) ell = sum_k c_k f_k.
(3) linear part of ell zero: constant 1 -> REFUTED-AT-DEGREE-2, constant 0 ->
    ELL-TRIVIAL; not substituted.
(4) otherwise j* = least index in ell's linear support; pi sets
    v_{j*} := ell + v_{j*} (an affine form in the other variables); the
    remaining 17 variables are relabelled in ascending order as 0..16; pi(f_k)
    is reduced multilinearly (degree <= 2).
(5) rank R'_3; rank, "1 in", dims_by_deg (d = 0..4) of R'_4.
"""
import numpy as np

import br_linalg as LA
import br_system as S


def left_kernel(Qm):
    """Basis of {c in F_2^r : c^T Qm = 0} for an r x n 0/1 matrix."""
    r, n = Qm.shape
    A = np.concatenate([Qm.astype(np.uint8), np.eye(r, dtype=np.uint8)], axis=1)
    P = LA.pack(A)
    rows, piv, _ = LA.rref(P, n, full=True)
    rank = len(piv)
    # rows beyond the rank: redo with all rows kept -> use forward elimination
    # on the augmented matrix and collect rows whose first n columns vanish.
    dense = A.copy()
    # plain Gauss elimination on dense rows (independent of the packed kernel)
    R = dense.copy()
    prow = 0
    for c in range(n):
        piv_r = None
        for i in range(prow, r):
            if R[i, c]:
                piv_r = i
                break
        if piv_r is None:
            continue
        if piv_r != prow:
            R[[prow, piv_r]] = R[[piv_r, prow]]
        for i in range(r):
            if i != prow and R[i, c]:
                R[i] ^= R[prow]
        prow += 1
    assert prow == rank
    ker = [R[i, n:].copy() for i in range(prow, r)]
    for v in ker:
        assert not ((v.astype(np.int64) @ Qm.astype(np.int64)) & 1).any()
    return ker


def substitute(E, jstar, lin_support, const):
    """pi(f_k) for all k. E: 17 x 172 (18 variables). Returns (E', relabel)
    with E' 17 x 154 in mu_order(2, 17)."""
    nv = S.NV
    others = [i for i in range(nv) if i != jstar]
    new = {old: n for n, old in enumerate(others)}
    aff = [i for i in lin_support if i != jstar]       # affine form: sum v_i + const
    monos17 = S.mu_order(2, nv - 1)
    col17 = {S.mask_of(m): j for j, m in enumerate(monos17)}
    Ep = np.zeros((E.shape[0], len(monos17)), dtype=np.uint8)

    def addmono(k, olds):
        # olds: set of OLD variable indices (none equal to jstar); multilinear
        m = 0
        for o in olds:
            m |= 1 << new[o]
        Ep[k, col17[m]] ^= 1

    for k in range(E.shape[0]):
        for j in np.flatnonzero(E[k]):
            mono = S.E_MONOS[j]
            if jstar not in mono:
                addmono(k, set(mono))
                continue
            rest = [i for i in mono if i != jstar]
            # v_{j*} -> sum_{i in aff} v_i + const
            for i in aff:
                addmono(k, set(rest) | {i})
            if const:
                addmono(k, set(rest))
    return Ep, others


def rc_b(E, sp3_17, sp4_17):
    """Returns the rc_b record for one system (17 x 172)."""
    Qm = E[:, S.QUAD_COLS]
    ker = left_kernel(Qm)
    rec = {"kernel_dim": len(ker)}
    if len(ker) != 1:
        rec["label"] = "not applicable (kernel dim %d)" % len(ker)
        return rec
    c = ker[0]
    rec["c"] = [int(x) for x in c]
    ell = np.zeros(S.NCOL_E, dtype=np.uint8)
    for k in np.flatnonzero(c):
        ell ^= E[k]
    assert not ell[S.QUAD_COLS].any()
    lin = [i for i in range(S.NV) if ell[S.E_COL[1 << i]]]
    const = int(ell[0])
    rec["ell_linear_support"] = lin
    rec["ell_constant"] = const
    if not lin:
        rec["label"] = "REFUTED-AT-DEGREE-2" if const == 1 else "ELL-TRIVIAL"
        return rec
    jstar = lin[0]
    rec["label"] = "SUBSTITUTED"
    rec["j_star"] = jstar
    Ep, others = substitute(E, jstar, lin, const)
    rec["_Ep"] = Ep
    M3 = sp3_17.build(Ep)
    M4 = sp4_17.build(Ep)
    rec["R3_shape"] = [int(M3.shape[0]), sp3_17.ncols]
    rec["R4_shape"] = [int(M4.shape[0]), sp4_17.ncols]
    _, p3, _ = LA.rref(M3, sp3_17.ncols, full=False)
    _, p4, _ = LA.rref(M4, sp4_17.ncols, full=False)
    rec["rank_R3"] = len(p3)
    rec["one_in_R3"] = sp3_17.const_col in p3
    rec["rank_R4"] = len(p4)
    rec["one_in_R4"] = sp4_17.const_col in p4
    rec["dims_by_deg_R4"] = sp4_17.dims_by_deg(p4)
    return rec
