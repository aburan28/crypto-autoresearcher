#!/usr/bin/env python3
"""Shift-encoded orbit-union point decomposition at m = 2 on toy Koblitz curves.

Session-level exploration prototype (not a ledger run).  For a Koblitz curve
K_a : y^2 + xy = x^3 + a x^2 + 1 over F_{2^n}, a random F_2-subspace V' of
dimension l', and the Frobenius-stable union S = U_j sigma^j(V'), it prices the
m = 2 decomposition of a target x_R three ways:

  SINGLE : n separate Semaev systems, x1 in V', x2 in sigma^j(V'), j = 0..n-1
           (global Frobenius gauge j1 = 0); cost summed over all n, and with a
           random j order stopped at the first satisfiable system.
  ONEHOT : one system with n one-hot shift bits s_j,  x2 = sum_j s_j sigma^j(u).
  BINARY : one system with B = ceil(log2 n) shift bits, sigma^j as a product of
           selectors (I + b_i (sigma^{2^i} - I)).
  LINEAR : reference -- a random subspace V of dimension ceil(log2 |S|),
           x1, x2 in V, one system.

Ground truth per target by solving the quadratic S3(x1, x2, x_R) = 0 for x2
over every x1 in V' (cross-checked by brute force at small n).
Solver: CaDiCaL 1.5.3 via python-sat; XORs encoded as CNF chains; statistics
are the solver's own conflict / decision / propagation counters.
"""
import argparse, json, math, random, sys, time
from pysat.solvers import Cadical153

# ---------------------------------------------------------------- GF(2^n)
IRRED = {11: (11, 2, 0), 13: (13, 4, 3, 1, 0), 17: (17, 3, 0), 19: (19, 5, 2, 1, 0),
         23: (23, 5, 0), 29: (29, 2, 0), 31: (31, 3, 0), 37: (37, 6, 4, 1, 0),
         41: (41, 3, 0)}

class GF:
    def __init__(self, n):
        self.n = n
        self.mod = sum(1 << e for e in IRRED[n])
        self.hi = 1 << n
        assert self._irreducible(), "modulus not irreducible"
    def _irreducible(self):
        # x^(2^n) == x mod f and gcd(x^(2^(n/p)) - x, f) == 1 for prime p | n (n prime here)
        x = 2
        t = x
        for _ in range(self.n):
            t = self.mul(t, t)
        if t != x: return False
        return True
    def mul(self, a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            b >>= 1
            a <<= 1
            if a & self.hi: a ^= self.mod
        return r
    def sqr(self, a): return self.mul(a, a)
    def pow(self, a, e):
        r = 1
        while e:
            if e & 1: r = self.mul(r, a)
            a = self.mul(a, a); e >>= 1
        return r
    def inv(self, a):
        assert a != 0
        return self.pow(a, (1 << self.n) - 2)
    def frob(self, a, j):
        for _ in range(j % self.n): a = self.mul(a, a)
        return a
    def trace(self, a):
        t, s = 0, a
        for _ in range(self.n):
            t ^= s; s = self.mul(s, s)
        return t
    def half_trace(self, a):  # n odd: z with z^2 + z = a when Tr(a) = 0
        z, s = 0, a
        for _ in range((self.n + 1) // 2):
            z ^= s; s = self.mul(self.mul(s, s), 1); s = self.mul(s, s)
        return z
    def solve_quadratic(self, A, B, C):
        """Roots z in F_{2^n} of A z^2 + B z + C = 0 (list, possibly empty)."""
        if A == 0:
            if B == 0: return []            # C == 0 would be everything; ignore
            return [self.mul(C, self.inv(B))]
        if B == 0:
            # z^2 = C/A  -> unique root sqrt(C/A)
            v = self.mul(C, self.inv(A))
            return [self.pow(v, 1 << (self.n - 1))]
        # z = (B/A) w  ->  w^2 + w = C A / B^2
        lam = self.mul(B, self.inv(A))
        d = self.mul(self.mul(C, A), self.inv(self.sqr(B)))
        if self.trace(d) != 0: return []
        w = self.half_trace(d)
        assert self.sqr(w) ^ w == d
        return [self.mul(lam, w), self.mul(lam, w ^ 1)]

# ---------------------------------------------------------------- curve
class Koblitz:
    def __init__(self, F, a):
        self.F, self.a = F, a
        n = F.n
        t = [2, 1 if a == 1 else -1]
        for k in range(2, n + 1):
            t.append(t[1] * t[k - 1] - 2 * t[k - 2])
        self.order = (1 << n) + 1 - t[n]
        import sympy
        fac = sympy.factorint(self.order)
        self.r = max(fac)
        self.h = self.order // self.r
    def on_curve_x(self, x):
        F = self.F
        if x == 0: return True
        w = x ^ self.a ^ F.inv(F.sqr(x))
        return F.trace(w) == 0
    def lift(self, x):
        F = self.F
        if x == 0: return (0, 1)
        w = x ^ self.a ^ F.inv(F.sqr(x))
        assert F.trace(w) == 0
        z = F.half_trace(w)
        y = F.mul(x, z)
        assert self.is_point((x, y))
        return (x, y)
    def is_point(self, P):
        if P is None: return True
        F = self.F; x, y = P
        return F.sqr(y) ^ F.mul(x, y) == F.mul(F.sqr(x), x) ^ (F.sqr(x) if self.a else 0) ^ 1
    def neg(self, P):
        if P is None: return None
        return (P[0], P[0] ^ P[1])
    def add(self, P, Q):
        F = self.F
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0]:
            if P[1] != Q[1] or P[0] == 0: return None
            lam = P[0] ^ F.mul(P[1], F.inv(P[0]))
            x3 = F.sqr(lam) ^ lam ^ self.a
            y3 = F.sqr(P[0]) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(P[1] ^ Q[1], F.inv(P[0] ^ Q[0]))
        x3 = F.sqr(lam) ^ lam ^ P[0] ^ Q[0] ^ self.a
        y3 = F.mul(lam, P[0] ^ x3) ^ x3 ^ P[1]
        return (x3, y3)
    def smul(self, k, P):
        R = None
        while k:
            if k & 1: R = self.add(R, P)
            P = self.add(P, P); k >>= 1
        return R
    def s3(self, x1, x2, x3):
        F = self.F
        p = F.mul(x1, x2)
        return F.mul(F.sqr(x1 ^ x2), F.sqr(x3)) ^ F.mul(p, x3) ^ F.sqr(p) ^ 1

# ---------------------------------------------------------------- symbolic ANF over F_{2^n}
def sym_add(A, B):
    C = dict(A)
    for m, c in B.items():
        v = C.get(m, 0) ^ c
        if v: C[m] = v
        else: C.pop(m, None)
    return C

def sym_mul(F, A, B):
    C = {}
    for ma, ca in A.items():
        for mb, cb in B.items():
            m = ma | mb
            v = C.get(m, 0) ^ F.mul(ca, cb)
            if v: C[m] = v
            else: C.pop(m, None)
    return C

def sym_sqr(F, A): return {m: F.sqr(c) for m, c in A.items()}
def sym_scale(F, A, c):
    out = {}
    for m, v in A.items():
        w = F.mul(v, c)
        if w: out[m] = w
    return out

def semaev3_sym(F, X1, X2, c):
    T = sym_add(X1, X2)
    P = sym_mul(F, X1, X2)
    S = sym_scale(F, sym_sqr(F, T), F.sqr(c))
    S = sym_add(S, sym_scale(F, P, c))
    S = sym_add(S, sym_sqr(F, P))
    S = sym_add(S, {frozenset(): 1})
    return S

def weil_descent(n, S):
    """-> list of (monomial_set, rhs) : XOR_{m in set} m = rhs, m != {} ."""
    eqs = []
    for i in range(n):
        mons = [m for m, c in S.items() if (c >> i) & 1 and m]
        rhs = (S.get(frozenset(), 0) >> i) & 1
        eqs.append((mons, rhs))
    return eqs

# ---------------------------------------------------------------- CNF
class CNF:
    def __init__(self, nvars):
        self.nv = nvars; self.clauses = []; self.mon_aux = {}
    def new(self):
        self.nv += 1; return self.nv
    def monomial(self, m):
        if len(m) == 1: return next(iter(m))
        if m in self.mon_aux: return self.mon_aux[m]
        a = self.new(); vs = sorted(m)
        for v in vs: self.clauses.append([-a, v])
        self.clauses.append([a] + [-v for v in vs])
        self.mon_aux[m] = a
        return a
    def xor(self, lits, rhs):
        lits = list(lits)
        if not lits:
            if rhs: self.clauses.append([])
            return
        if len(lits) == 1:
            self.clauses.append([lits[0]] if rhs else [-lits[0]]); return
        cur = lits[0]
        for x in lits[1:-1]:
            y = self.new()
            self.clauses += [[-y, cur, x], [-y, -cur, -x], [y, -cur, x], [y, cur, -x]]
            cur = y
        z = lits[-1]
        if rhs: self.clauses += [[cur, z], [-cur, -z]]
        else:   self.clauses += [[-cur, z], [cur, -z]]
    def add_system(self, eqs):
        for mons, rhs in eqs:
            self.xor([self.monomial(m) for m in mons], rhs)

def solve(cnf):
    s = Cadical153(bootstrap_with=cnf.clauses)
    t0 = time.perf_counter(); ok = s.solve(); dt = time.perf_counter() - t0
    st = s.accum_stats(); model = s.get_model() if ok else None
    s.delete()
    return ok, dt, st, model

# ---------------------------------------------------------------- experiment
def random_subspace(F, dim, rng):
    while True:
        basis = [rng.randrange(1, F.hi) for _ in range(dim)]
        # rank check by elimination
        rows = list(basis); piv = []
        for r in rows:
            for p in piv:
                r = min(r, r ^ p)
            if r: piv.append(r)
        if len(piv) == dim: return basis

def span(basis):
    out = {0}
    for b in basis:
        out |= {v ^ b for v in out}
    return out

def run(n, a, lprime, ntargets, seed, do_linear=True, do_binary=True):
    rng = random.Random(seed)
    F = GF(n); E = Koblitz(F, a)
    basis = random_subspace(F, lprime, rng)
    Vp = span(basis)
    S = set()
    for j in range(n):
        S |= {F.frob(v, j) for v in Vp}
    lS = math.log2(len(S))
    llin = math.ceil(lS)
    lin_basis = random_subspace(F, llin, rng)
    Vlin = span(lin_basis)
    B = max(1, math.ceil(math.log2(n)))
    # generator of the prime-order subgroup
    while True:
        x = rng.randrange(1, F.hi)
        if not E.on_curve_x(x): continue
        P = E.lift(x); G = E.smul(E.h, P)
        if G is not None: break
    assert E.smul(E.r, G) is None
    # symbolic x1, x2 forms
    vt = list(range(1, lprime + 1)); vu = list(range(lprime + 1, 2 * lprime + 1))
    X1 = {frozenset([vt[k]]): basis[k] for k in range(lprime)}
    def X2_single(j): return {frozenset([vu[k]]): F.frob(basis[k], j) for k in range(lprime)}
    vs = list(range(2 * lprime + 1, 2 * lprime + n + 1))
    X2_onehot = {}
    for j in range(n):
        for k in range(lprime):
            X2_onehot[frozenset([vs[j], vu[k]])] = F.frob(basis[k], j)
    vb = list(range(2 * lprime + 1, 2 * lprime + B + 1))
    U = {frozenset([vu[k]]): basis[k] for k in range(lprime)}
    for i in range(B):
        add = {}
        for m, c in U.items():
            d = F.frob(c, 1 << i) ^ c
            if d: add[m | {vb[i]}] = d
        U = sym_add(U, add)
    X2_binary = U
    vl1 = list(range(1, llin + 1)); vl2 = list(range(llin + 1, 2 * llin + 1))
    XL1 = {frozenset([vl1[k]]): lin_basis[k] for k in range(llin)}
    XL2 = {frozenset([vl2[k]]): lin_basis[k] for k in range(llin)}

    def ground_truth(c, x1set, x2set):
        sols = []
        for x1 in x1set:
            A = F.sqr(x1) ^ F.sqr(c); Bq = F.mul(x1, c); C = F.mul(F.sqr(x1), F.sqr(c)) ^ 1
            for x2 in F.solve_quadratic(A, Bq, C):
                if x2 in x2set:
                    assert E.s3(x1, x2, c) == 0
                    sols.append((x1, x2))
        return sols

    def decode_x(model, X):
        val = 0
        mset = set(v for v in model if v > 0)
        for m, c in X.items():
            if all(v in mset for v in m): val ^= c
        return val

    rows = []
    for tix in range(ntargets):
        k = rng.randrange(1, E.r); R = E.smul(k, G); c = R[0]
        if c == 0: continue
        gt = ground_truth(c, Vp, S)
        gt_lin = ground_truth(c, Vlin, Vlin) if do_linear else None
        row = dict(n=n, a=a, lprime=lprime, S=len(S), llin=llin, target=tix, xR=c,
                   gt_sat=bool(gt), gt_nsol=len(gt), gt_lin_sat=(bool(gt_lin) if do_linear else None))
        # SINGLE
        single = []
        for j in range(n):
            cnf = CNF(2 * lprime); cnf.add_system(weil_descent(n, semaev3_sym(F, X1, X2_single(j), c)))
            ok, dt, st, model = solve(cnf)
            if ok:
                x1 = decode_x(model, X1); x2 = decode_x(model, X2_single(j))
                assert E.s3(x1, x2, c) == 0 and x1 in Vp and x2 in S
            single.append(dict(j=j, sat=ok, t=dt, **{k2: st[k2] for k2 in ('conflicts', 'decisions', 'propagations')}))
        row['single_sat'] = any(s['sat'] for s in single)
        assert row['single_sat'] == row['gt_sat'], (row, single)
        for key in ('conflicts', 'decisions', 'propagations', 't'):
            row['single_sum_' + key] = sum(s[key] for s in single)
        order = list(range(n)); rng.shuffle(order)
        acc = dict(conflicts=0, decisions=0, propagations=0, t=0.0)
        for j in order:
            for key in acc: acc[key] += single[j][key]
            if single[j]['sat']: break
        for key in acc: row['single_first_' + key] = acc[key]
        # ONEHOT
        cnf = CNF(2 * lprime + n); cnf.add_system(weil_descent(n, semaev3_sym(F, X1, X2_onehot, c)))
        cnf.xor(vs, 1)
        for i in range(n):
            for j in range(i + 1, n): cnf.clauses.append([-vs[i], -vs[j]])
        ok, dt, st, model = solve(cnf)
        if ok:
            x1 = decode_x(model, X1); x2 = decode_x(model, X2_onehot)
            assert E.s3(x1, x2, c) == 0 and x1 in Vp and x2 in S
        assert ok == row['gt_sat']
        row.update(onehot_sat=ok, onehot_t=dt, onehot_vars=cnf.nv, onehot_clauses=len(cnf.clauses),
                   **{'onehot_' + k2: st[k2] for k2 in ('conflicts', 'decisions', 'propagations')})
        # BINARY
        if do_binary:
            cnf = CNF(2 * lprime + B); cnf.add_system(weil_descent(n, semaev3_sym(F, X1, X2_binary, c)))
            for val in range(n, 1 << B):   # forbid shifts >= n
                cnf.clauses.append([(-vb[i] if (val >> i) & 1 else vb[i]) for i in range(B)])
            ok, dt, st, model = solve(cnf)
            if ok:
                x1 = decode_x(model, X1); x2 = decode_x(model, X2_binary)
                assert E.s3(x1, x2, c) == 0 and x1 in Vp and x2 in S
            assert ok == row['gt_sat']
            row.update(binary_sat=ok, binary_t=dt, binary_vars=cnf.nv, binary_clauses=len(cnf.clauses),
                       **{'binary_' + k2: st[k2] for k2 in ('conflicts', 'decisions', 'propagations')})
        # LINEAR reference
        if do_linear:
            cnf = CNF(2 * llin); cnf.add_system(weil_descent(n, semaev3_sym(F, XL1, XL2, c)))
            ok, dt, st, model = solve(cnf)
            if ok:
                x1 = decode_x(model, XL1); x2 = decode_x(model, XL2)
                assert E.s3(x1, x2, c) == 0 and x1 in Vlin and x2 in Vlin
            assert ok == row['gt_lin_sat']
            row.update(linear_sat=ok, linear_t=dt, linear_vars=cnf.nv, linear_clauses=len(cnf.clauses),
                       **{'linear_' + k2: st[k2] for k2 in ('conflicts', 'decisions', 'propagations')})
        rows.append(row)
        print(json.dumps(row), flush=True)
    return dict(n=n, a=a, r=E.r, h=E.h, lprime=lprime, S=len(S), llin=llin, B=B, rows=rows)

def summarize(res):
    rows = res['rows']
    def mean(key, flt=lambda r: True):
        v = [r[key] for r in rows if flt(r) and key in r]
        return sum(v) / len(v) if v else float('nan')
    out = []
    n = res['n']
    for label, flt in (('all', lambda r: True), ('UNSAT', lambda r: not r['gt_sat']), ('SAT', lambda r: r['gt_sat'])):
        cnt = sum(1 for r in rows if flt(r))
        if not cnt: continue
        line = dict(cell=f"n={n} a={res['a']} l'={res['lprime']} |S|={res['S']} l_lin={res['llin']}", subset=label, targets=cnt,
                    single_sum_conf=mean('single_sum_conflicts', flt), single_first_conf=mean('single_first_conflicts', flt),
                    onehot_conf=mean('onehot_conflicts', flt), binary_conf=mean('binary_conflicts', flt), linear_conf=mean('linear_conflicts', flt),
                    single_sum_dec=mean('single_sum_decisions', flt), onehot_dec=mean('onehot_decisions', flt), binary_dec=mean('binary_decisions', flt), linear_dec=mean('linear_decisions', flt),
                    single_sum_prop=mean('single_sum_propagations', flt), onehot_prop=mean('onehot_propagations', flt), binary_prop=mean('binary_propagations', flt), linear_prop=mean('linear_propagations', flt),
                    single_sum_t=mean('single_sum_t', flt), onehot_t=mean('onehot_t', flt), binary_t=mean('binary_t', flt), linear_t=mean('linear_t', flt))
        out.append(line)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--a', type=int, default=None)
    ap.add_argument('--lprime', type=int, default=None)
    ap.add_argument('--targets', type=int, default=24)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--no-binary', action='store_true')
    ap.add_argument('--no-linear', action='store_true')
    ap.add_argument('--out', type=str, default=None)
    args = ap.parse_args()
    n = args.n
    if args.a is None:
        F = GF(n); cands = [(Koblitz(F, a).r, a) for a in (0, 1)]
        args.a = max(cands)[1]
    if args.lprime is None:
        l = math.ceil(n / 2); args.lprime = max(1, l - math.ceil(math.log2(n)))
    res = run(n, args.a, args.lprime, args.targets, args.seed, do_linear=not args.no_linear, do_binary=not args.no_binary)
    summ = summarize(res)
    for line in summ: print("SUMMARY", json.dumps(line), flush=True)
    if args.out:
        with open(args.out, 'w') as f: json.dump(dict(meta={k: v for k, v in res.items() if k != 'rows'}, rows=res['rows'], summary=summ), f)
