#!/usr/bin/env python3
"""Per-solve cost of m = 2 orbit-union point decomposition, up the n ladder to
the real ECC2K-130 parameters.

Extends the toy measurement in ../frobenius-orbit-union/frob_union_m2.py
(EV-FROB-b6e1e9 / KN-FIND-47da4e, n <= 23) toward n = 131.  It is an
INSTRUMENT MEASUREMENT of the cost of one decomposition solve; it is not an
attack, it makes no progress on any discrete logarithm, and it is not a
harness run (no RUN-* manifest exists and none is invented).

Two arms, exactly as the prior instrument defines them:

  baseline : n separate gauge-fixed Semaev systems, x1 in V', x2 in sigma^j(V'),
             j = 0..n-1, conflicts summed over all n.
  onehot   : one system with n shift bits s_j, exactly one true,
             x2 = sum_j s_j sigma^j(u), u in V'.

Two CNF encodings of the Weil descent:

  direct : the prior instrument's encoding -- S3(X1, X2, c) expanded
           symbolically over F_{2^n} and descended, so the one-hot arm carries
           l'^2 * n cubic monomials.  Infeasible at n = 131.
  staged : intermediate F_2 variable vectors w = x2 and p = x1*x2, so every
           block is at most quadratic and the monomial count is O(l' n).
           This is what makes n = 131 buildable at all.

S3 is DERIVED here (coefficient fit against real curve triples with
P1+P2+P3 = O) and verified before use; nothing about it is recalled.  The
Weil descent is verified against field arithmetic on random assignments.
Every SAT model is re-decoded and re-checked in the field.

Budgets: per-solve conflict budget and per-cell wall clock.  A censored solve
is a RESOURCE outcome, never negative mathematical evidence (AGENTS.md rule 3);
it is reported with the conflicts observed at the cutoff.
"""
import argparse, json, math, os, random, resource, sys, threading, time

from pysat.solvers import Cadical153

# --------------------------------------------------------------- GF(2^n)
PINNED_MOD = {131: (131, 13, 2, 1, 0)}   # ECC2K-130's field polynomial


class GF:
    def __init__(self, n, exps=None):
        self.n = n
        self.hi = 1 << n
        if exps is None:
            exps = PINNED_MOD.get(n) or self._find_modulus()
        self.exps = tuple(exps)
        self.mod = sum(1 << e for e in exps)
        assert self.irreducible(), f"modulus {exps} not irreducible over F_2"

    def _find_modulus(self):
        n = self.n
        for k in range(1, n):                       # trinomials
            cand = (n, k, 0)
            self.exps = cand
            self.mod = sum(1 << e for e in cand)
            if self.irreducible():
                return cand
        for k1 in range(1, n):                      # pentanomials
            for k2 in range(1, k1):
                for k3 in range(1, k2):
                    cand = (n, k1, k2, k3, 0)
                    self.exps = cand
                    self.mod = sum(1 << e for e in cand)
                    if self.irreducible():
                        return cand
        raise RuntimeError("no sparse irreducible modulus found")

    def irreducible(self):
        """Valid for PRIME n: f | x^(2^n) - x  <=>  f irreducible (deg f = n >= 3)."""
        assert self.n >= 3
        t = 2
        for _ in range(self.n):
            t = self.mul(t, t)
        return t == 2

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & self.hi:
                a ^= self.mod
        return r

    def sqr(self, a):
        return self.mul(a, a)

    def pow(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a):
        assert a != 0
        return self.pow(a, (1 << self.n) - 2)

    def frob(self, a, j):
        for _ in range(j % self.n):
            a = self.mul(a, a)
        return a

    def trace(self, a):
        t, s = 0, a
        for _ in range(self.n):
            t ^= s
            s = self.mul(s, s)
        return t

    def half_trace(self, a):      # n odd: z with z^2 + z = a when Tr(a) = 0
        z, s = 0, a
        for _ in range((self.n + 1) // 2):
            z ^= s
            s = self.mul(self.mul(s, s), 1)
            s = self.mul(s, s)
        return z

    def solve_quadratic(self, A, B, C):
        """Roots z of A z^2 + B z + C = 0 in F_{2^n}."""
        if A == 0:
            if B == 0:
                return []
            return [self.mul(C, self.inv(B))]
        if B == 0:
            v = self.mul(C, self.inv(A))
            return [self.pow(v, 1 << (self.n - 1))]
        lam = self.mul(B, self.inv(A))
        d = self.mul(self.mul(C, A), self.inv(self.sqr(B)))
        if self.trace(d) != 0:
            return []
        w = self.half_trace(d)
        assert self.sqr(w) ^ w == d
        return [self.mul(lam, w), self.mul(lam, w ^ 1)]


# --------------------------------------------------------------- curve
class Koblitz:
    """K_a : y^2 + x y = x^3 + a x^2 + 1 over F_{2^n}."""

    def __init__(self, F, a, r=None, h=None):
        self.F, self.a = F, a
        n = F.n
        t = [2, 1 if a == 1 else -1]
        for k in range(2, n + 1):
            t.append(t[1] * t[k - 1] - 2 * t[k - 2])
        self.order = (1 << n) + 1 - t[n]
        if r is not None:
            assert self.order % r == 0
            self.r, self.h = r, self.order // r
        else:
            import sympy
            fac = sympy.factorint(self.order)
            self.r = max(fac)
            self.h = self.order // self.r

    def on_curve_x(self, x):
        F = self.F
        if x == 0:
            return True
        return F.trace(x ^ self.a ^ F.inv(F.sqr(x))) == 0

    def lift(self, x):
        F = self.F
        if x == 0:
            return (0, 1)
        w = x ^ self.a ^ F.inv(F.sqr(x))
        assert F.trace(w) == 0
        return (x, F.mul(x, F.half_trace(w)))

    def is_point(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        return F.sqr(y) ^ F.mul(x, y) == F.mul(F.sqr(x), x) ^ (F.sqr(x) if self.a else 0) ^ 1

    def neg(self, P):
        return None if P is None else (P[0], P[0] ^ P[1])

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0]:
            if P[1] != Q[1] or P[0] == 0:
                return None
            lam = P[0] ^ F.mul(P[1], F.inv(P[0]))
            x3 = F.sqr(lam) ^ lam ^ self.a
            return (x3, F.sqr(P[0]) ^ F.mul(lam ^ 1, x3))
        lam = F.mul(P[1] ^ Q[1], F.inv(P[0] ^ Q[0]))
        x3 = F.sqr(lam) ^ lam ^ P[0] ^ Q[0] ^ self.a
        return (x3, F.mul(lam, P[0] ^ x3) ^ x3 ^ P[1])

    def smul(self, k, P):
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def random_point(self, rng):
        F = self.F
        while True:
            x = rng.randrange(1, F.hi)
            if self.on_curve_x(x):
                return self.lift(x)


# --------------------------------------------------------------- S3, DERIVED
def derive_s3(F, E, rng, nsamples=80, nverify=200):
    """Fit S3 from real curve triples with P1 + P2 + P3 = O; no recalled formula.

    Ansatz: sum_{i,j,k <= 2} c_{ijk} x1^i x2^j x3^k, symmetric by construction of
    the sample set.  Returns (coeffs dict keyed (i,j,k), report dict).
    """
    mons = [(i, j, k) for i in range(3) for j in range(3) for k in range(3)]

    def triple():
        while True:
            P1 = E.random_point(rng)
            P2 = E.random_point(rng)
            P3 = E.neg(E.add(P1, P2))
            if P3 is None or P1[0] == 0 or P2[0] == 0 or P3[0] == 0:
                continue
            assert E.add(E.add(P1, P2), P3) is None
            return (P1[0], P2[0], P3[0])

    rows = []
    for _ in range(nsamples):
        x1, x2, x3 = triple()
        pw = lambda v, e: (1 if e == 0 else (v if e == 1 else F.sqr(v)))
        rows.append([F.mul(F.mul(pw(x1, i), pw(x2, j)), pw(x3, k)) for (i, j, k) in mons])

    # kernel of the sample matrix over F_{2^n}
    ncol = len(mons)
    mat = [r[:] for r in rows]
    pivots = {}
    rr = 0
    for c in range(ncol):
        piv = None
        for r in range(rr, len(mat)):
            if mat[r][c]:
                piv = r
                break
        if piv is None:
            continue
        mat[rr], mat[piv] = mat[piv], mat[rr]
        iv = F.inv(mat[rr][c])
        mat[rr] = [F.mul(v, iv) for v in mat[rr]]
        for r in range(len(mat)):
            if r != rr and mat[r][c]:
                f = mat[r][c]
                mat[r] = [mat[r][q] ^ F.mul(f, mat[rr][q]) for q in range(ncol)]
        pivots[c] = rr
        rr += 1
    free = [c for c in range(ncol) if c not in pivots]
    kernel = []
    for fc in free:
        vec = [0] * ncol
        vec[fc] = 1
        for c, r in pivots.items():
            vec[c] = mat[r][fc]
        kernel.append(vec)

    report = dict(samples=nsamples, monomials=ncol, kernel_dim=len(kernel))
    if len(kernel) != 1:
        report['status'] = 'FAILED: kernel not 1-dimensional'
        return None, report
    vec = kernel[0]
    # normalise so the constant term is 1 (it is b = 1 for these curves)
    c000 = vec[mons.index((0, 0, 0))]
    assert c000 != 0, "constant term vanished; cannot normalise"
    iv = F.inv(c000)
    vec = [F.mul(v, iv) for v in vec]
    coeffs = {m: v for m, v in zip(mons, vec) if v}

    def ev(x1, x2, x3):
        pw = lambda v, e: (1 if e == 0 else (v if e == 1 else F.sqr(v)))
        acc = 0
        for (i, j, k), c in coeffs.items():
            acc ^= F.mul(c, F.mul(F.mul(pw(x1, i), pw(x2, j)), pw(x3, k)))
        return acc

    ok_real = sum(1 for _ in range(nverify) if ev(*triple()) == 0)
    ok_rand = 0
    for _ in range(nverify):
        x1, x2, x3 = (rng.randrange(1, F.hi) for _ in range(3))
        if ev(x1, x2, x3) != 0:
            ok_rand += 1
    report.update(
        support=sorted(coeffs), coeffs_hex={str(m): hex(c) for m, c in coeffs.items()},
        verify_real_triples=nverify, verify_real_vanishing=ok_real,
        verify_random_triples=nverify, verify_random_nonvanishing=ok_rand,
        status='ok' if (ok_real == nverify and ok_rand >= nverify - 2) else 'FAILED')
    report['ev'] = None
    return coeffs, report


# --------------------------------------------------------------- symbolic ANF over F_{2^n}
def sym_add(A, B):
    C = dict(A)
    for m, c in B.items():
        v = C.get(m, 0) ^ c
        if v:
            C[m] = v
        else:
            C.pop(m, None)
    return C


def sym_mul(F, A, B):
    C = {}
    for ma, ca in A.items():
        for mb, cb in B.items():
            m = ma | mb
            v = C.get(m, 0) ^ F.mul(ca, cb)
            if v:
                C[m] = v
            else:
                C.pop(m, None)
    return C


def sym_sqr(F, A):
    return {m: F.sqr(c) for m, c in A.items()}


def sym_scale(F, A, c):
    out = {}
    for m, v in A.items():
        w = F.mul(v, c)
        if w:
            out[m] = w
    return out


def s3_sym(F, coeffs, X1, X2, c):
    """S3(X1, X2, c) as symbolic ANF, using the DERIVED coefficients."""
    ONE = {frozenset(): 1}
    P1 = [ONE, X1, sym_sqr(F, X1)]
    P2 = [ONE, X2, sym_sqr(F, X2)]
    cp = [1, c, F.sqr(c)]
    out = {}
    for (i, j, k), co in coeffs.items():
        term = sym_mul(F, P1[i], P2[j]) if (i and j) else (P1[i] if i else P2[j])
        if not i and not j:
            term = ONE
        out = sym_add(out, sym_scale(F, term, F.mul(co, cp[k])))
    return out


def weil_descent(n, S):
    """-> list of (list_of_monomials, rhs_bit): XOR of monomials = rhs."""
    eqs = []
    const = S.get(frozenset(), 0)
    for i in range(n):
        mons = [m for m, c in S.items() if m and (c >> i) & 1]
        eqs.append((mons, (const >> i) & 1))
    return eqs


def verify_descent(F, rng, S, eqs, trials=8):
    """Check the descended F_2 system agrees with field evaluation of S."""
    allvars = sorted({v for m in S for v in m})
    bad = 0
    for _ in range(trials):
        asg = {v: rng.randrange(2) for v in allvars}
        val = 0
        for m, c in S.items():
            if all(asg[v] for v in m):
                val ^= c
        for i, (mons, rhs) in enumerate(eqs):
            lhs = 0
            for m in mons:
                if all(asg[v] for v in m):
                    lhs ^= 1
            if lhs ^ rhs != (val >> i) & 1:
                bad += 1
    return dict(trials=trials, vars=len(allvars), mismatches=bad)


# --------------------------------------------------------------- CNF, streamed
class CNFSink:
    """Tseitin sink that streams clauses straight into the solver."""

    def __init__(self, nvars, solver):
        self.nv = nvars
        self.solver = solver
        self.nclauses = 0
        self.mon_aux = {}

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, cl):
        self.nclauses += 1
        self.solver.add_clause(cl)

    def monomial(self, m):
        if len(m) == 1:
            return next(iter(m))
        a = self.mon_aux.get(m)
        if a is not None:
            return a
        a = self.new()
        vs = sorted(m)
        for v in vs:
            self.add([-a, v])
        self.add([a] + [-v for v in vs])
        self.mon_aux[m] = a
        return a

    def xor(self, lits, rhs):
        lits = list(lits)
        if not lits:
            if rhs:
                self.add([])
            return
        if len(lits) == 1:
            self.add([lits[0]] if rhs else [-lits[0]])
            return
        cur = lits[0]
        for x in lits[1:-1]:
            y = self.new()
            self.add([-y, cur, x]); self.add([-y, -cur, -x])
            self.add([y, -cur, x]); self.add([y, cur, -x])
            cur = y
        z = lits[-1]
        if rhs:
            self.add([cur, z]); self.add([-cur, -z])
        else:
            self.add([-cur, z]); self.add([cur, -z])

    def add_system(self, eqs):
        for mons, rhs in eqs:
            self.xor([self.monomial(m) for m in mons], rhs)


# --------------------------------------------------------------- subspaces
def random_subspace(F, dim, rng):
    while True:
        basis = [rng.randrange(1, F.hi) for _ in range(dim)]
        piv = []
        for r in basis:
            for p in piv:
                r = min(r, r ^ p)
            if r:
                piv.append(r)
        if len(piv) == dim:
            return basis


def echelon(basis):
    piv = []
    for b in basis:
        r = b
        for p in piv:
            r = min(r, r ^ p)
        if r:
            piv.append(r)
            piv.sort(reverse=True)
    return piv


def in_span(piv, x):
    for p in piv:
        x = min(x, x ^ p)
    return x == 0


# --------------------------------------------------------------- one cell
def build_and_solve(F, coeffs, basis, lprime, n, c, arm, encoding, order,
                    j=None, conf_budget=None, solve_wall=None, verbose=False):
    """Build one CNF and solve it.  Returns a record dict."""
    solver = Cadical153()
    l = lprime
    # ---- variable layout
    nsh = n if arm == 'onehot' else 0
    if order == 'shift_first' and nsh:
        vs = list(range(1, n + 1))
        vt = list(range(n + 1, n + l + 1))
        vu = list(range(n + l + 1, n + 2 * l + 1))
        base = n + 2 * l
    else:
        vt = list(range(1, l + 1))
        vu = list(range(l + 1, 2 * l + 1))
        vs = list(range(2 * l + 1, 2 * l + n + 1)) if nsh else []
        base = 2 * l + nsh
    X1 = {frozenset([vt[k]]): basis[k] for k in range(l)}
    if arm == 'onehot':
        X2 = {}
        for jj in range(n):
            for k in range(l):
                X2[frozenset([vs[jj], vu[k]])] = F.frob(basis[k], jj)
    else:
        X2 = {frozenset([vu[k]]): F.frob(basis[k], j) for k in range(l)}

    t_build = time.perf_counter()
    if encoding == 'direct':
        cnf = CNFSink(base, solver)
        S = s3_sym(F, coeffs, X1, X2, c)
        eqs = weil_descent(n, S)
        cnf.add_system(eqs)
        n_main_mon = len(S)
        stage_info = dict(main_monomials=n_main_mon)
        decode_X2 = X2
        vw = vp = None
    elif encoding == 'stagew':
        # stage ONLY w = x2 (n free F_2 bits); the product x1*x2 stays a direct
        # quadratic ANF in {t_a, w_i}, so the main block never exceeds degree 2
        # and carries l' * n monomials instead of the direct arm's l'^2 * n.
        vw = list(range(base + 1, base + n + 1))
        vp = None
        cnf = CNFSink(base + n, solver)
        W_as_field = {frozenset([vw[i]]): 1 << i for i in range(n)}
        cnf.add_system(weil_descent(n, sym_add(X2, W_as_field)))
        S = s3_sym(F, coeffs, X1, W_as_field, c)
        cnf.add_system(weil_descent(n, S))
        stage_info = dict(w_monomials=len(X2), main_monomials=len(S))
        decode_X2 = X2
    else:
        vw = list(range(base + 1, base + n + 1))
        vp = list(range(base + n + 1, base + 2 * n + 1))
        cnf = CNFSink(base + 2 * n, solver)
        # W block:  w = X2
        W_as_field = {frozenset([vw[i]]): 1 << i for i in range(n)}
        eqs_w = weil_descent(n, sym_add(X2, W_as_field))
        cnf.add_system(eqs_w)
        # P block:  p = X1 * W
        PROD = sym_mul(F, X1, W_as_field)
        P_as_field = {frozenset([vp[i]]): 1 << i for i in range(n)}
        eqs_p = weil_descent(n, sym_add(PROD, P_as_field))
        cnf.add_system(eqs_p)
        # main block: S3 with X2 -> W and X1*X2 -> P.  Requires support in
        # {(0,0),(2,0),(0,2),(1,1),(2,2)} x {k}, which is checked by the caller.
        ONE = {frozenset(): 1}
        Wsym = W_as_field
        Psym = P_as_field
        cp = [1, c, F.sqr(c)]
        main = {}
        for (i, jj, k), co in coeffs.items():
            sc = F.mul(co, cp[k])
            if (i, jj) == (0, 0):
                term = ONE
            elif (i, jj) == (2, 0):
                term = sym_sqr(F, X1)
            elif (i, jj) == (0, 2):
                term = sym_sqr(F, Wsym)
            elif (i, jj) == (1, 1):
                term = Psym
            elif (i, jj) == (2, 2):
                term = sym_sqr(F, Psym)
            elif (i, jj) == (1, 0):
                term = X1
            elif (i, jj) == (0, 1):
                term = Wsym
            else:
                raise RuntimeError(f"staged encoding cannot express S3 term {(i, jj)}")
            main = sym_add(main, sym_scale(F, term, sc))
        cnf.add_system(weil_descent(n, main))
        stage_info = dict(w_monomials=len(X2), p_monomials=len(PROD))
        decode_X2 = X2
    if arm == 'onehot':
        cnf.xor(vs, 1)
        for i in range(n):
            for jj in range(i + 1, n):
                cnf.add([-vs[i], -vs[jj]])
    t_build = time.perf_counter() - t_build

    if conf_budget:
        solver.conf_budget(int(conf_budget))
    # NOTE: python-sat 1.9.dev15 raises NotImplementedError from
    # Cadical153.interrupt(), so a hard per-solve WALL CLOCK is not available on
    # this solver.  Censoring is therefore by CONFLICT BUDGET only, and
    # --solve-wall is refused rather than silently ignored.
    if solve_wall:
        raise RuntimeError('per-solve wall clock unsupported: Cadical153.interrupt() '
                           'raises NotImplementedError in python-sat 1.9.dev15')
    t0 = time.perf_counter()
    ok = solver.solve_limited() if conf_budget else solver.solve()
    dt = time.perf_counter() - t0
    st = solver.accum_stats()
    model = solver.get_model() if ok else None
    rec = dict(arm=arm, encoding=encoding, order=order, j=j, sat=ok,
               censored=(ok is None), censor_reason=(
                   None if ok is not None else
                   'conflict_budget'),
               t_solve=dt, t_build=t_build, solve_wall=solve_wall,
               cnf_vars=cnf.nv, cnf_clauses=cnf.nclauses,
               conflicts=st.get('conflicts'), decisions=st.get('decisions'),
               propagations=st.get('propagations'), **stage_info)
    if ok:
        mset = {v for v in model if v > 0}

        def dec(X):
            val = 0
            for m, cc in X.items():
                if all(v in mset for v in m):
                    val ^= cc
            return val
        x1 = dec(X1)
        x2 = dec(decode_X2)
        rec['model_x1'] = hex(x1)
        rec['model_x2'] = hex(x2)
        if vw is not None:
            wval = sum(1 << i for i in range(n) if vw[i] in mset)
            rec['stage_w_ok'] = (wval == x2)
            if vp is not None:
                pval = sum(1 << i for i in range(n) if vp[i] in mset)
                rec['stage_p_ok'] = (pval == F.mul(x1, x2))
    solver.delete()
    return rec


def eval_s3(F, coeffs, x1, x2, x3):
    pw = lambda v, e: (1 if e == 0 else (v if e == 1 else F.sqr(v)))
    acc = 0
    for (i, j, k), c in coeffs.items():
        acc ^= F.mul(c, F.mul(F.mul(pw(x1, i), pw(x2, j)), pw(x3, k)))
    return acc


def run_cell(n, a, lprime, ntargets, seed, encoding, order, conf_budget,
             cell_wall, ground_truth_cap, planted, r_known=None, baseline_encoding=None,
             baseline_sample=0, solve_wall=0.0, onehot_solve_wall=0.0):
    t_cell0 = time.perf_counter()
    rng = random.Random(seed)
    F = GF(n)
    E = Koblitz(F, a, r=r_known)
    coeffs, s3rep = derive_s3(F, E, rng)
    if coeffs is None or s3rep['status'] != 'ok':
        return dict(n=n, status='S3_DERIVATION_FAILED', s3=s3rep)
    s3rep.pop('ev', None)
    bad_support = [m for m in coeffs if (m[0], m[1]) not in
                   {(0, 0), (2, 0), (0, 2), (1, 1), (2, 2), (1, 0), (0, 1)}]
    basis = random_subspace(F, lprime, rng)
    piv = echelon(basis)
    baseline_encoding = baseline_encoding or encoding

    def in_S(x):
        for j in range(n):
            if in_span(piv, F.frob(x, -j % n)):
                return True
        return False

    # descent self-check on a small symbolic instance of this cell
    vt = list(range(1, lprime + 1))
    vu = list(range(lprime + 1, 2 * lprime + 1))
    X1 = {frozenset([vt[k]]): basis[k] for k in range(lprime)}
    X2 = {frozenset([vu[k]]): basis[k] for k in range(lprime)}
    ctest = E.random_point(rng)[0]
    Stest = s3_sym(F, coeffs, X1, X2, ctest)
    dv = verify_descent(F, rng, Stest, weil_descent(n, Stest))

    do_gt = lprime <= ground_truth_cap
    cell = dict(n=n, a=a, lprime=lprime, log2_S=round(math.log2(n) + lprime, 3),
                encoding=encoding, baseline_encoding=baseline_encoding, order=order,
                conf_budget=conf_budget, cell_wall=cell_wall, seed=seed,
                baseline_sample=baseline_sample, solve_wall=solve_wall,
                onehot_solve_wall=onehot_solve_wall,
                modulus_exponents=list(F.exps), curve_order=E.order, r=E.r, h=E.h,
                s3=s3rep, s3_support_outside_staged_set=bad_support,
                descent_check=dv, ground_truth=do_gt, planted=planted,
                targets=[], status='running')

    G = None
    if not planted:
        while True:
            P = E.random_point(rng)
            G = E.smul(E.h, P)
            if G is not None and E.smul(E.r, G) is None:
                break

    for tix in range(ntargets):
        if time.perf_counter() - t_cell0 > cell_wall:
            cell['status'] = 'wall_clock_censored'
            break
        # ---- target
        if planted:
            while True:
                x1p = 0
                while x1p == 0:
                    x1p = 0
                    for k in range(lprime):
                        if rng.randrange(2):
                            x1p ^= basis[k]
                up = 0
                while up == 0:
                    up = 0
                    for k in range(lprime):
                        if rng.randrange(2):
                            up ^= basis[k]
                jp = rng.randrange(n)
                x2p = F.frob(up, jp)
                # solve S3(x1p, x2p, X) = 0 for X  (quadratic in X)
                A = B = C = 0
                for (i, j, k), co in coeffs.items():
                    v = F.mul(co, F.mul(1 if i == 0 else (x1p if i == 1 else F.sqr(x1p)),
                                        1 if j == 0 else (x2p if j == 1 else F.sqr(x2p))))
                    if k == 0:
                        C ^= v
                    elif k == 1:
                        B ^= v
                    else:
                        A ^= v
                roots = [z for z in F.solve_quadratic(A, B, C) if z and E.on_curve_x(z)]
                if roots:
                    c = roots[rng.randrange(len(roots))]
                    assert eval_s3(F, coeffs, x1p, x2p, c) == 0
                    break
        else:
            k = rng.randrange(1, E.r)
            R = E.smul(k, G)
            if R is None or R[0] == 0:
                continue
            c = R[0]

        row = dict(target=tix, xR=hex(c), planted=planted)
        if planted:
            row['plant_x1'] = hex(x1p)
            row['plant_x2'] = hex(x2p)
            row['plant_j'] = jp
        # ---- ground truth (exhaustive over V'), toy cells only
        if do_gt:
            sols = []
            for mask in range(1 << lprime):
                x1 = 0
                mm = mask
                kk = 0
                while mm:
                    if mm & 1:
                        x1 ^= basis[kk]
                    mm >>= 1
                    kk += 1
                A = B = C = 0
                for (i, j, kx) in coeffs:
                    co = coeffs[(i, j, kx)]
                    v = F.mul(co, F.mul(1 if i == 0 else (x1 if i == 1 else F.sqr(x1)),
                                        1 if kx == 0 else (c if kx == 1 else F.sqr(c))))
                    if j == 0:
                        C ^= v
                    elif j == 1:
                        B ^= v
                    else:
                        A ^= v
                for x2 in F.solve_quadratic(A, B, C):
                    if in_S(x2):
                        assert eval_s3(F, coeffs, x1, x2, c) == 0
                        sols.append((hex(x1), hex(x2)))
            row['gt_sat'] = bool(sols)
            row['gt_nsol'] = len(sols)
        # ---- baseline arm
        base_recs = []
        js = list(range(n))
        if baseline_sample and baseline_sample < n:
            js = sorted(rng.sample(js, baseline_sample))
        for j in js:
            rec = build_and_solve(F, coeffs, basis, lprime, n, c, 'baseline',
                                  baseline_encoding, order, j=j, conf_budget=conf_budget,
                                  solve_wall=solve_wall)
            if rec['sat']:
                x1 = int(rec['model_x1'], 16)
                x2 = int(rec['model_x2'], 16)
                rec['verified'] = (eval_s3(F, coeffs, x1, x2, c) == 0
                                   and in_span(piv, x1) and in_S(x2))
            base_recs.append(rec)
            if time.perf_counter() - t_cell0 > cell_wall:
                rec['cell_wall_hit'] = True
                break
        row['baseline_systems_run'] = len(base_recs)
        row['baseline_systems_total'] = n
        row['baseline_sampled'] = bool(baseline_sample and baseline_sample < n)
        row['baseline_censored'] = (any(r['censored'] for r in base_recs)
                                    or (len(base_recs) < n and not row['baseline_sampled']))
        row['baseline_conflicts'] = sum(r['conflicts'] for r in base_recs)
        row['baseline_conflicts_per_system_measured'] = (
            sum(r['conflicts'] for r in base_recs) / len(base_recs)) if base_recs else None
        if row['baseline_sampled'] and base_recs:
            # MODELLED, not measured: mean over the sampled j scaled to all n systems.
            row['baseline_conflicts_modelled_sum'] = (
                n * row['baseline_conflicts_per_system_measured'])
            row['baseline_t_modelled_sum'] = n * sum(r['t_solve'] for r in base_recs) / len(base_recs)
        row['baseline_j_sampled'] = [r['j'] for r in base_recs]
        row['baseline_censor_reasons'] = [r.get('censor_reason') for r in base_recs]
        row['baseline_decisions'] = sum(r['decisions'] for r in base_recs)
        row['baseline_propagations'] = sum(r['propagations'] for r in base_recs)
        row['baseline_t'] = sum(r['t_solve'] for r in base_recs)
        row['baseline_build_t'] = sum(r['t_build'] for r in base_recs)
        row['baseline_sat'] = any(r['sat'] for r in base_recs)
        row['baseline_verified'] = [r.get('verified') for r in base_recs if r['sat']]
        row['baseline_cnf_vars'] = base_recs[0]['cnf_vars'] if base_recs else None
        row['baseline_cnf_clauses'] = base_recs[0]['cnf_clauses'] if base_recs else None
        # ---- one-hot arm
        oh = build_and_solve(F, coeffs, basis, lprime, n, c, 'onehot',
                             encoding, order, conf_budget=conf_budget,
                             solve_wall=onehot_solve_wall or solve_wall)
        if oh['sat']:
            x1 = int(oh['model_x1'], 16)
            x2 = int(oh['model_x2'], 16)
            oh['verified'] = (eval_s3(F, coeffs, x1, x2, c) == 0
                              and in_span(piv, x1) and in_S(x2))
        for k2 in ('sat', 'censored', 'censor_reason', 'conflicts', 'decisions', 'propagations',
                   'cnf_vars', 'cnf_clauses', 'verified', 'stage_w_ok', 'stage_p_ok'):
            if k2 in oh:
                row['onehot_' + k2] = oh[k2]
        row['onehot_t'] = oh['t_solve']
        row['onehot_build_t'] = oh['t_build']
        if row['baseline_conflicts'] and not row['baseline_censored'] and not oh['censored']:
            denom = (row.get('baseline_conflicts_modelled_sum')
                     if row['baseline_sampled'] else row['baseline_conflicts'])
            row['ratio'] = row['onehot_conflicts'] / denom
            row['ratio_denominator'] = 'modelled' if row['baseline_sampled'] else 'measured'
        if do_gt:
            row['baseline_matches_gt'] = (row['baseline_sat'] == row['gt_sat']
                                          if not row['baseline_censored'] else None)
            row['onehot_matches_gt'] = (oh['sat'] == row['gt_sat']
                                        if not oh['censored'] else None)
        row['maxrss_kb'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        cell['targets'].append(row)
        print(json.dumps(row), flush=True)

    if cell['status'] == 'running':
        cell['status'] = 'complete'
    cell['wall_seconds'] = time.perf_counter() - t_cell0
    cell['maxrss_kb'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # summary
    rows = cell['targets']

    def mean(key, flt):
        v = [r[key] for r in rows if flt(r) and r.get(key) is not None]
        return (sum(v) / len(v)) if v else None
    for label, flt in (('all', lambda r: True),
                       ('uncensored', lambda r: not r['baseline_censored'] and not r.get('onehot_censored')),
                       ('UNSAT', lambda r: not r['baseline_sat'] and not r['baseline_censored'] and not r.get('onehot_censored'))):
        cnt = sum(1 for r in rows if flt(r))
        if not cnt:
            continue
        b = mean('baseline_conflicts', flt)
        o = mean('onehot_conflicts', flt)
        cell.setdefault('summary', []).append(dict(
            subset=label, targets=cnt,
            baseline_conflicts=b, onehot_conflicts=o,
            ratio_of_means=(o / b if b else None),
            mean_of_ratios=mean('ratio', flt),
            baseline_t=mean('baseline_t', flt), onehot_t=mean('onehot_t', flt)))
    return cell


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--a', type=int, default=None)
    ap.add_argument('--lprime', type=int, default=None)
    ap.add_argument('--targets', type=int, default=8)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--encoding', choices=('direct', 'stagew', 'staged'), default='stagew')
    ap.add_argument('--baseline-encoding', choices=('direct', 'stagew', 'staged'), default=None)
    ap.add_argument('--order', choices=('default', 'shift_first'), default='shift_first')
    ap.add_argument('--conf-budget', type=int, default=0, help='0 = unlimited')
    ap.add_argument('--cell-wall', type=float, default=3600.0)
    ap.add_argument('--gt-cap', type=int, default=16, help='max l\' for exhaustive ground truth')
    ap.add_argument('--planted', action='store_true')
    ap.add_argument('--solve-wall', type=float, default=0.0,
                    help='hard wall clock (s) per individual solve; 0 = none')
    ap.add_argument('--onehot-solve-wall', type=float, default=0.0,
                    help='separate wall clock for the one-hot solve; 0 = use --solve-wall')
    ap.add_argument('--baseline-sample', type=int, default=0,
                    help='measure only K of the n gauge-fixed baseline systems; '
                         'the full-n sum is then MODELLED, never reported as measured')
    ap.add_argument('--mem-gib', type=float, default=7.0)
    ap.add_argument('--out', type=str, default=None)
    args = ap.parse_args()

    resource.setrlimit(resource.RLIMIT_AS,
                       (int(args.mem_gib * (1 << 30)), int(args.mem_gib * (1 << 30))))
    n = args.n
    r_known = None
    if n == 131:
        a = 0 if args.a is None else args.a
        r_known = 680564733841876926932320129493409985129
    else:
        if args.a is None:
            F = GF(n)
            a = max((Koblitz(F, aa).r, aa) for aa in (0, 1))[1]
        else:
            a = args.a
    if args.lprime is None:
        args.lprime = max(1, math.ceil(n / 2) - math.ceil(math.log2(n)))
    cell = run_cell(n, a, args.lprime, args.targets, args.seed, args.encoding,
                    args.order, args.conf_budget, args.cell_wall, args.gt_cap,
                    args.planted, r_known=r_known,
                    baseline_encoding=args.baseline_encoding,
                    baseline_sample=args.baseline_sample,
                    solve_wall=args.solve_wall,
                    onehot_solve_wall=args.onehot_solve_wall)
    cell['argv'] = sys.argv
    cell['pysat_version'] = __import__('pysat').__version__ if hasattr(__import__('pysat'), '__version__') else '1.9.dev15'
    cell['solver'] = 'Cadical153 (CaDiCaL 1.5.3) via python-sat 1.9.dev15'
    for s in cell.get('summary', []):
        print('SUMMARY', json.dumps(s), flush=True)
    if args.out:
        with open(args.out, 'w') as f:
            json.dump(cell, f, indent=1)


if __name__ == '__main__':
    main()
