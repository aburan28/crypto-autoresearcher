"""Satisfiability oracles (never use the solver), witness re-verification and
Proposition S instrument checks.

Oracle A: O(2^l) root finding over V (curve-algebra families only).
Oracle B: exhaustive bit-sliced evaluation of the 17 descended equations over
all 2^18 assignments (every family).
An assignment u encodes v_i = bit i of u; x_1 = u & 511, x_2 = u >> 9.
"""
import numpy as np

from macaulay import EQ_MONS, NV, NEQ, L, eval_equations_scalar
from curve import s3_eval_school

NASSIGN = 1 << NV
NWORDS = NASSIGN // 64
VMASK = (1 << L) - 1


def _build_monomial_vectors():
    u = np.arange(NASSIGN, dtype=np.int64)
    vecs = np.zeros((len(EQ_MONS), NWORDS), dtype=np.uint64)
    for j, m in enumerate(EQ_MONS):
        bits = np.ones(NASSIGN, dtype=np.uint8)
        for i in m:
            bits &= ((u >> i) & 1).astype(np.uint8)
        vecs[j] = np.packbits(bits, bitorder="little").view(np.uint64)
    return vecs


_MONVECS = None


def monvecs():
    global _MONVECS
    if _MONVECS is None:
        _MONVECS = _build_monomial_vectors()
    return _MONVECS


def oracle_B(E):
    """Returns sorted list of satisfying assignments u."""
    mv = monvecs()
    anyfail = np.zeros(NWORDS, dtype=np.uint64)
    for k in range(NEQ):
        supp = np.flatnonzero(E[k])
        if supp.size == 0:
            continue
        anyfail |= np.bitwise_xor.reduce(mv[supp], axis=0)
    ok = ~anyfail
    bits = np.unpackbits(ok.view(np.uint8), bitorder="little")
    return [int(x) for x in np.flatnonzero(bits)]


def solve_quadratic(F, a, b, c):
    """All roots X in F_{2^17} of a X^2 + b X + c = 0 (n odd). Returns
    ("all", None) if the polynomial is identically zero, else ("roots", list)."""
    if a == 0 and b == 0:
        return ("all", None) if c == 0 else ("roots", [])
    if a == 0:
        return ("roots", [F.div(c, b)])
    if b == 0:
        return ("roots", [F.sqrt(F.div(c, a))])
    # X = (b/a) Z with Z^2 + Z = ac/b^2; solvable iff Tr(ac/b^2) = 0
    d = F.div(F.mul(a, c), F.mul(b, b))
    if F.trace(d) != 0:
        return ("roots", [])
    z = F.half_trace(d)
    s = F.div(b, a)
    return ("roots", [F.mul(s, z), F.mul(s, z ^ 1)])


def oracle_A(F, B, xR, V):
    """Root finding: for each x_1 in V solve a X^2 + b X + c = 0 with
    a = x_1^2 + x_R^2, b = x_1 x_R, c = x_1^2 x_R^2 + B; keep roots in V.
    Returns sorted list of assignments u = u_1 | (u_2 << 9), u_i the
    coordinates of x_i in the cell's basis of V (EXP-CERTBIN-3f06d1: V is a
    VBasis; membership of a root is V.coord, the linear-algebra test)."""
    sols = []
    xR2 = F.mul(xR, xR)
    for u1 in range(1 << L):
        x1 = V.comb(u1)
        x12 = F.mul(x1, x1)
        a = x12 ^ xR2
        b = F.mul(x1, xR)
        c = F.mul(x12, xR2) ^ B
        kind, roots = solve_quadratic(F, a, b, c)
        if kind == "all":
            roots = [V.comb(u) for u in range(1 << L)]
        for x2 in roots:
            u2 = V.coord(x2)
            if u2 is not None:
                sols.append(u1 | (u2 << L))
    return sorted(sols)


def verify_witnesses(F, B, xR, E, sols, curve_algebra, V=None):
    """C-WIT: every Boolean solution re-verified (i) by direct S_3 evaluation in
    F_{2^17} with schoolbook arithmetic (curve-algebra families) and (ii) by
    evaluating all 17 Boolean equations with scalar code. Returns list of
    failures. (x_i = V.comb(u_i), the cell's basis.)"""
    fails = []
    for u in sols:
        if curve_algebra:
            x1, x2 = V.comb(u & VMASK), V.comb(u >> L)
            if s3_eval_school(F, B, x1, x2, xR) != 0:
                fails.append({"u": u, "check": "S3_direct"})
        vals = eval_equations_scalar(E, u)
        if any(vals):
            fails.append({"u": u, "check": "boolean_equations"})
    return fails


def rational_flag(curve, xR, sols, V):
    """# of Boolean solutions whose x_1, x_2 are both abscissae of F_{2^17}
    points and for which some sign choice gives +-P_1 +- P_2 = +-R."""
    cnt = 0
    for u in sols:
        x1, x2 = V.comb(u & VMASK), V.comb(u >> L)
        P1 = curve.lift_x(x1)
        P2 = curve.lift_x(x2)
        if P1 is None or P2 is None:
            continue
        S = curve.add(P1, P2)
        Dd = curve.sub(P1, P2)
        if (S is not None and S[0] == xR) or (Dd is not None and Dd[0] == xR):
            cnt += 1
    return cnt


def ps0_check(shape, M_orig, sols):
    """PS0: every row of M_D vanishes at every Boolean solution. Returns list of
    (u, number of non-vanishing rows)."""
    bad = []
    evs = []
    for u in sols:
        ev = shape.eval_vector(u)
        evs.append(ev)
        par = np.bitwise_count(M_orig & ev[None, :]).sum(axis=1) & 1
        n = int(par.sum())
        if n:
            bad.append({"u": u, "nonvanishing_rows": n})
    return bad, evs
