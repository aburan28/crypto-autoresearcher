"""Satisfiability oracles (never use either solver), witness re-verification
and PS0 checks.

Copied from EXP-CERTBIN-4e92d7/impl/oracles.py and generalized to (n, l)
(see impl-provenance.json); oracle C is new (spec object.satisfiability).

Oracle A: O(2^l) root finding over V (curve-algebra families only).
Oracle B: exhaustive bit-sliced evaluation of the n descended equations over
          all 2^{2l} assignments (regime A; every regime-A family).
Oracle C: direct evaluation of g_0 (S_3, or a null family's g_0) on all of
          V x V with vectorized table arithmetic (regime B; every family).
An assignment u encodes v_i = bit i of u; x_1 = u & (2^l - 1), x_2 = u >> l.
"""
import numpy as np

from curve import s3_eval_school


class OracleB:
    def __init__(self, desc):
        self.desc = desc
        self.nassign = 1 << desc.nv
        self.nwords = max(1, self.nassign // 64)
        u = np.arange(self.nassign, dtype=np.int64)
        vecs = np.zeros((len(desc.eq_mons), self.nwords), dtype=np.uint64)
        for j, m in enumerate(desc.eq_mons):
            bits = np.ones(self.nassign, dtype=np.uint8)
            for i in m:
                bits &= ((u >> i) & 1).astype(np.uint8)
            vecs[j] = np.packbits(bits, bitorder="little").view(np.uint64)
        self.mv = vecs

    def __call__(self, E):
        """Sorted list of satisfying assignments u."""
        anyfail = np.zeros(self.nwords, dtype=np.uint64)
        for k in range(self.desc.neq):
            supp = np.flatnonzero(E[k])
            if supp.size == 0:
                continue
            anyfail |= np.bitwise_xor.reduce(self.mv[supp], axis=0)
        ok = ~anyfail
        bits = np.unpackbits(ok.view(np.uint8), bitorder="little")[:self.nassign]
        return [int(x) for x in np.flatnonzero(bits)]


def solve_quadratic(F, a, b, c):
    """All roots X in F_{2^n} of a X^2 + b X + c = 0 (n odd). Returns
    ("all", None) if the polynomial is identically zero, else ("roots", list)."""
    if a == 0 and b == 0:
        return ("all", None) if c == 0 else ("roots", [])
    if a == 0:
        return ("roots", [F.div(c, b)])
    if b == 0:
        return ("roots", [F.sqrt(F.div(c, a))])
    d = F.div(F.mul(a, c), F.mul(b, b))
    if F.trace(d) != 0:
        return ("roots", [])
    z = F.half_trace(d)
    s = F.div(b, a)
    return ("roots", [F.mul(s, z), F.mul(s, z ^ 1)])


def oracle_A(F, B, xR, l):
    """Root finding: for each x_1 in V solve a X^2 + b X + c = 0 with
    a = x_1^2 + x_R^2, b = x_1 x_R, c = x_1^2 x_R^2 + B; keep roots in V.
    Returns sorted list of assignments u = x_1 | (x_2 << l)."""
    sols = []
    xR2 = F.mul(xR, xR)
    for x1 in range(1 << l):
        x12 = F.mul(x1, x1)
        a = x12 ^ xR2
        b = F.mul(x1, xR)
        c = F.mul(x12, xR2) ^ B
        kind, roots = solve_quadratic(F, a, b, c)
        if kind == "all":
            roots = list(range(1 << l))
        for x2 in roots:
            if x2 >> l == 0:
                sols.append(x1 | (x2 << l))
    return sorted(sols)


class OracleC:
    """Direct evaluation of g_0(x_1, x_2) = c1 x1^2 x2^2 + c2 x1^2 + c3 x2^2
    + c4 x1 x2 + c5 on all of V x V (V enumerated in increasing integer
    order). For S_3: (c1..c5) = (1, x_R^2, x_R^2, x_R, B)."""

    def __init__(self, F, l):
        self.F, self.l = F, l
        v = np.arange(1 << l, dtype=np.int64)
        self.x1 = np.repeat(v, 1 << l)
        self.x2 = np.tile(v, 1 << l)
        self.x1s = F.vmul(self.x1, self.x1)
        self.x2s = F.vmul(self.x2, self.x2)
        self.x1x2 = F.vmul(self.x1, self.x2)
        self.x1sx2s = F.vmul(self.x1s, self.x2s)

    def values(self, coeffs):
        F = self.F
        c1, c2, c3, c4, c5 = [np.int64(c) for c in coeffs]
        val = (F.vmul(self.x1sx2s, np.full_like(self.x1, c1)) ^ F.vmul(self.x1s, np.full_like(self.x1, c2))
               ^ F.vmul(self.x2s, np.full_like(self.x1, c3)) ^ F.vmul(self.x1x2, np.full_like(self.x1, c4)) ^ c5)
        return val

    def __call__(self, coeffs):
        val = self.values(coeffs)
        z = np.flatnonzero(val == 0)
        l = self.l
        return sorted(int(self.x1[i]) | (int(self.x2[i]) << l) for i in z)


def s3_coeffs(F, B, xR):
    xR2 = F.mul(xR, xR)
    return (1, xR2, xR2, xR, B)


def g0_eval_school(F, coeffs, x1, x2):
    m = F.mul_school
    c1, c2, c3, c4, c5 = coeffs
    x1s, x2s = m(x1, x1), m(x2, x2)
    return m(c1, m(x1s, x2s)) ^ m(c2, x1s) ^ m(c3, x2s) ^ m(c4, m(x1, x2)) ^ c5


def verify_witnesses(F, B, xR, E, sols, l, desc=None, curve_algebra=True, coeffs=None):
    """C-WIT: every solution re-verified (i) by direct S_3 evaluation in
    F_{2^n} with schoolbook arithmetic (curve-algebra families), or of the null
    g_0 (regime-B nulls, schoolbook); (ii) by evaluating all n Boolean
    equations with scalar code when a descended E is given. Returns failures."""
    fails = []
    vm = (1 << l) - 1
    for u in sols:
        x1, x2 = u & vm, u >> l
        if curve_algebra:
            if s3_eval_school(F, B, x1, x2, xR) != 0:
                fails.append({"u": u, "check": "S3_direct"})
        elif coeffs is not None:
            if g0_eval_school(F, coeffs, x1, x2) != 0:
                fails.append({"u": u, "check": "g0_direct"})
        if E is not None and desc is not None:
            vals = desc.eval_equations_scalar(E, u)
            if any(vals):
                fails.append({"u": u, "check": "boolean_equations"})
    return fails


def rational_flag(curve, xR, sols, l):
    """# of solutions whose x_1, x_2 are both abscissae of F_{2^n} points and
    for which some sign choice gives +-P_1 +- P_2 = +-R."""
    cnt = 0
    vm = (1 << l) - 1
    for u in sols:
        x1, x2 = u & vm, u >> l
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
    """Regime-A PS0: every row of M_D vanishes at every Boolean solution."""
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
