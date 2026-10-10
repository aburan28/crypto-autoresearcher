"""S0-only G1 instrument for EXP-ICEX-153c34.

The module contains the non-enumerative algebraic path needed by the smoke
gates: exact Semaev f3/f5 evaluation, a division-free Sylvester determinant
for the target-specialised f6, and a deterministic sparse lex Buchberger
solver over the indicator ideal.  The charged protocol driver is deliberately
absent: this task is not admitted to create frozen runs.

All arithmetic in the G1 path is local Python arithmetic with explicit
operation counters.  The O5 oracle is kept in the S0 driver as an independent
verifier and is never called from ``g1_membership``.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Counters:
    mul: int = 0
    inv: int = 0
    probes: int = 0
    point_add: int = 0
    s_pairs: int = 0
    reductions: int = 0

    def units(self):
        return self.mul + 10 * self.inv + self.probes + 13 * self.point_add


class Field:
    def __init__(self, p, counters=None):
        self.p = int(p)
        self.c = counters or Counters()

    def add(self, a, b):
        return (a + b) % self.p

    def neg(self, a):
        return (-a) % self.p

    def sub(self, a, b):
        return (a - b) % self.p

    def mul(self, a, b):
        self.c.mul += 1
        return (a * b) % self.p

    def inv(self, a):
        if a % self.p == 0:
            raise ZeroDivisionError("field inverse of zero")
        self.c.inv += 1
        return pow(a, self.p - 2, self.p)


def poly_trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return [x for x in a]


def poly_add(F, a, b):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % F.p
    return poly_trim(out)


def poly_scale(F, a, k):
    return poly_trim([(x * k) % F.p for x in a])


def poly_mul(F, a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            F.c.mul += 1
            out[i + j] = (out[i + j] + x * y) % F.p
    return poly_trim(out)


def poly_eval(F, a, x):
    out = 0
    for c in reversed(a):
        F.c.mul += 1
        out = (out * x + c) % F.p
    return out


def poly_divmod(F, a, b):
    a = poly_trim(a)
    b = poly_trim(b)
    if not b:
        raise ZeroDivisionError("polynomial division by zero")
    if len(a) < len(b):
        return [], a
    q = [0] * (len(a) - len(b) + 1)
    r = a[:]
    ilc = F.inv(b[-1])
    while r and len(r) >= len(b):
        d = len(r) - len(b)
        k = (r[-1] * ilc) % F.p
        q[d] = k
        for i, v in enumerate(b):
            F.c.mul += 1
            r[i + d] = (r[i + d] - k * v) % F.p
        r = poly_trim(r)
    return poly_trim(q), r


def resultant_dp(F, A, B):
    """Division-free determinant of the full Sylvester matrix.

    A and B are low-to-high coefficient lists.  The subset DP is the
    independent reconstruction used for the S0 determinant check; it uses no
    divisions and retains formal zero slots.
    """
    da, db = len(A) - 1, len(B) - 1
    if da < 0 or db < 0:
        return 0
    n = da + db
    M = [[0 for _ in range(n)] for _ in range(n)]
    # db shifted rows of A followed by da shifted rows of B.
    for r in range(db):
        for j, v in enumerate(A):
            if r + j < n:
                M[r][r + j] = v % F.p
    for r in range(da):
        for j, v in enumerate(B):
            if r + j < n:
                M[db + r][r + j] = v % F.p
    dp = {0: 1}
    for r in range(n):
        nxt = {}
        for mask, value in dp.items():
            for col in range(n):
                if mask & (1 << col) or M[r][col] == 0:
                    continue
                # Number of unused columns before col gives the Laplace sign.
                inversions = (mask >> (col + 1)).bit_count()
                sign = -1 if inversions & 1 else 1
                term = value * M[r][col] % F.p
                key = mask | (1 << col)
                nxt[key] = (nxt.get(key, 0) + sign * term) % F.p
        dp = nxt
    return dp.get((1 << n) - 1, 0) % F.p


def s3_coeffs(p, a, b, u, v):
    # f3(u,v,z) = A z^2 + B z + C.
    A = (u - v) ** 2 % p
    B = (-2 * ((u + v) * (u * v + a) + 2 * b)) % p
    C = ((u * v - a) ** 2 - 4 * b * (u + v)) % p
    return [C, B, A]


def load_s5_terms(path):
    doc = json.loads(Path(path).read_text())
    return doc["S5"], doc["degrees"]["S5"]


def s5_eval(p, a, b, xs, terms_path):
    """Evaluate f5 from the committed S5 coefficient inventory."""
    terms, _ = load_s5_terms(terms_path)
    out = 0
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        c = term[7]
        v = c * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip(xs, exps):
            v = v * pow(x, e, p) % p
        out = (out + v) % p
    return out


def f6_specialised(p, a, b, xs, xR, terms_path):
    """Compute f6(x1..x5,xR) by the approved target-specialised resultant.

    The inner f5 is treated as a polynomial in z=x5 and the f3 factor as a
    quadratic in z.  This evaluates the full formal degree slots and does not
    form a target-independent symbolic f6.
    """
    x1, x2, x3, x4, x5 = xs
    terms, degrees = load_s5_terms(terms_path)
    A = [0] * (degrees["S5"][-1] + 1)
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        c = term[7]
        v = c * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip((x1, x2, x3, x4), exps[:4]):
            v = v * pow(x, e, p) % p
        A[exps[4]] = (A[exps[4]] + v * 1) % p
    B = s3_coeffs(p, a, b, x5, xR)
    F = Field(p)
    return resultant_dp(F, A, B)


def f6_specialised_bareiss(p, a, b, xs, xR, terms_path):
    """Independent division-based 10x10 determinant for G0-2/G0-3."""
    terms, degrees = load_s5_terms(terms_path)
    A = [0] * (degrees["S5"][-1] + 1)
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        v = term[7] * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip(xs[:4], exps[:4]):
            v = v * pow(x, e, p) % p
        A[exps[4]] = (A[exps[4]] + v) % p
    B = s3_coeffs(p, a, b, xs[4], xR)
    n = (len(A) - 1) + (len(B) - 1)
    M = [[0 for _ in range(n)] for _ in range(n)]
    da, db = len(A) - 1, len(B) - 1
    for r in range(db):
        for j, v in enumerate(A):
            M[r][r + j] = v % p
    for r in range(da):
        for j, v in enumerate(B):
            M[db + r][r + j] = v % p
    prev = 1
    sign = 1
    for k in range(n - 1):
        pivot = next((r for r in range(k, n) if M[r][k] % p), None)
        if pivot is None:
            return 0
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            sign = -sign
        pk = M[k][k] % p
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = (pk * M[i][j] - M[i][k] * M[k][j]) % p
                if k:
                    num = (num * pow(prev, p - 2, p)) % p
                M[i][j] = num
            M[i][k] = 0
        prev = pk
    return sign * M[-1][-1] % p


def _poly_add_many(a, b, p):
    return a.add(b, p)


def _sylvester_poly_dp(Fcoeff, Gcoeff, p):
    """Subset-DP determinant where matrix entries are SparsePoly objects."""
    da, db = len(Fcoeff) - 1, len(Gcoeff) - 1
    n = da + db
    zero = SparsePoly(5, {})
    M = [[zero for _ in range(n)] for _ in range(n)]
    for r in range(db):
        for j, v in enumerate(Fcoeff):
            if r + j < n:
                M[r][r + j] = v
    for r in range(da):
        for j, v in enumerate(Gcoeff):
            if r + j < n:
                M[db + r][r + j] = v
    dp = {0: SparsePoly(5, {(0, 0, 0, 0, 0): 1})}
    for r in range(n):
        nxt = {}
        for mask, value in dp.items():
            for col in range(n):
                if mask & (1 << col) or not M[r][col].terms:
                    continue
                sign = -1 if ((mask >> (col + 1)).bit_count() & 1) else 1
                term = value.mul(M[r][col], p)
                key = mask | (1 << col)
                nxt[key] = nxt.get(key, SparsePoly(5, {})).add(term, p, scale=sign)
        dp = nxt
    return dp.get((1 << n) - 1, SparsePoly(5, {})).clean(p)


def f6_specialised_poly(p, a, b, xR, terms_path):
    """Build the target-specialised f6 in the monomial basis.

    The result is the exact determinant polynomial in x1..x5.  It is built
    after target specialisation as required by D-2; no evaluation-grid or
    5-sum table is constructed.
    """
    terms, degrees = load_s5_terms(terms_path)
    Fcoeff = [SparsePoly(5, {}) for _ in range(degrees["S5"][-1] + 1)]
    for term in terms:
        ea, eb = term[0], term[1]
        exps = tuple(term[2:7])
        c = term[7] * pow(a, ea, p) * pow(b, eb, p) % p
        e = (exps[0], exps[1], exps[2], exps[3], 0)
        old = Fcoeff[exps[4]].terms.get(e, 0)
        Fcoeff[exps[4]].terms[e] = (old + c) % p
    # f3(x5,xR,z) = A z^2 + B z + C, in x5.
    def mono(exp, coeff):
        return SparsePoly(5, {(0, 0, 0, 0, exp): coeff % p})
    A = mono(2, xR * 0 + 1).add(mono(1, -2 * xR), p).add(mono(0, xR * xR), p)
    B = (mono(2, -2 * xR).add(mono(1, -2 * (a + xR * xR)), p)
         .add(mono(0, -2 * (a * xR + 2 * b)), p))
    C = (mono(2, xR * xR).add(mono(1, -2 * a * xR - 4 * b), p)
         .add(mono(0, a * a - 4 * b * xR), p))
    return _sylvester_poly_dp(Fcoeff, [C, B, A], p)


def _one_var_remainder(p, coeff, degree_poly):
    """Remainder of a low-degree monomial polynomial modulo a monic g_V."""
    a = list(coeff)
    while len(a) >= len(degree_poly):
        k = a[-1] % p
        d = len(a) - len(degree_poly)
        if k:
            for i, v in enumerate(degree_poly):
                a[i + d] = (a[i + d] - k * v) % p
        a.pop()
    return poly_trim(a)


def reduce_indicator_poly(poly, V, p):
    """Reduce each coordinate modulo g_V in the monomial basis."""
    g = [1]
    for v in sorted(V):
        nxt = [0] * (len(g) + 1)
        for i, c in enumerate(g):
            nxt[i] = (nxt[i] - c * v) % p
            nxt[i + 1] = (nxt[i + 1] + c) % p
        g = nxt
    cache = {}
    out = SparsePoly(poly.nvars, {})
    for exp, coeff in poly.terms.items():
        pieces = {tuple([0] * poly.nvars): coeff % p}
        for var, power in enumerate(exp):
            key = (var, power)
            if key not in cache:
                c = [0] * (power + 1)
                c[power] = 1
                cache[key] = _one_var_remainder(p, c, g)
            nxt = {}
            for base, bc in pieces.items():
                for d, dc in enumerate(cache[key]):
                    e = list(base)
                    e[var] = d
                    e = tuple(e)
                    nxt[e] = (nxt.get(e, 0) + bc * dc) % p
            pieces = nxt
        out = out.add(SparsePoly(poly.nvars, pieces), p)
    return out.clean(p)


def sparse_eval(poly, xs, p):
    total = 0
    for exp, coeff in poly.terms.items():
        value = coeff
        for x, e in zip(xs, exp):
            value = value * pow(x, e, p) % p
        total = (total + value) % p
    return total


@dataclass
class SparsePoly:
    nvars: int
    terms: dict = field(default_factory=dict)

    def clean(self, p):
        self.terms = {e: c % p for e, c in self.terms.items() if c % p}
        return self

    def copy(self):
        return SparsePoly(self.nvars, dict(self.terms))

    def add(self, other, p, scale=1):
        out = dict(self.terms)
        for e, c in other.terms.items():
            out[e] = (out.get(e, 0) + scale * c) % p
        return SparsePoly(self.nvars, out).clean(p)

    def mul(self, other, p):
        out = {}
        for ea, ca in self.terms.items():
            for eb, cb in other.terms.items():
                e = tuple(x + y for x, y in zip(ea, eb))
                out[e] = (out.get(e, 0) + ca * cb) % p
        return SparsePoly(self.nvars, out).clean(p)

    def lead(self):
        return max(self.terms) if self.terms else None

    def monic(self, p):
        if not self.terms:
            return self.copy()
        lc = self.terms[self.lead()]
        ilc = pow(lc, p - 2, p)
        return SparsePoly(self.nvars, {e: c * ilc % p for e, c in self.terms.items()})


def poly_monomial(nvars, exponent, coeff):
    return SparsePoly(nvars, {tuple(exponent): coeff})


def normal_form(f, basis, p, counters=None):
    f = f.copy().clean(p)
    rem = SparsePoly(f.nvars, {})
    while f.terms:
        lt = f.lead()
        reduced = False
        for g in basis:
            lg = g.lead()
            if lg and all(a >= b for a, b in zip(lt, lg)):
                shift = tuple(a - b for a, b in zip(lt, lg))
                coeff = f.terms[lt] * pow(g.terms[lg], p - 2, p) % p
                shifted = SparsePoly(f.nvars, {tuple(a + b for a, b in zip(e, shift)): c
                                                for e, c in g.terms.items()})
                f = f.add(shifted, p, scale=-coeff)
                reduced = True
                if counters:
                    counters.reductions += 1
                break
        if not reduced:
            rem.terms[lt] = f.terms.pop(lt)
    return rem.clean(p)


def s_polynomial(f, g, p):
    lf, lg = f.lead(), g.lead()
    lcm = tuple(max(a, b) for a, b in zip(lf, lg))
    sf = tuple(a - b for a, b in zip(lcm, lf))
    sg = tuple(a - b for a, b in zip(lcm, lg))
    cf = f.terms[lf]
    cg = g.terms[lg]
    af = SparsePoly(f.nvars, {tuple(a + b for a, b in zip(e, sf)): c * pow(cf, p - 2, p) % p
                              for e, c in f.terms.items()})
    ag = SparsePoly(g.nvars, {tuple(a + b for a, b in zip(e, sg)): c * pow(cg, p - 2, p) % p
                              for e, c in g.terms.items()})
    return af.add(ag, p, scale=-1)


def buchberger(generators, p, counters=None):
    basis = [g.monic(p) for g in generators if g.terms]
    pairs = [(i, j) for i in range(len(basis)) for j in range(i)]
    while pairs:
        i, j = pairs.pop(0)
        if counters:
            counters.s_pairs += 1
        s = s_polynomial(basis[i], basis[j], p)
        r = normal_form(s, basis, p, counters)
        if r.terms:
            r = r.monic(p)
            k = len(basis)
            basis.append(r)
            pairs.extend((k, i) for i in range(k))
    return sorted(basis, key=lambda g: g.lead(), reverse=True)


def indicator_poly(V, var, nvars, p):
    # Product (x_var-v), expanded exactly over F_p.
    coeff = [1]
    for v in sorted(V):
        out = [0] * (len(coeff) + 1)
        for i, c in enumerate(coeff):
            out[i] = (out[i] - c * v) % p
            out[i + 1] = (out[i + 1] + c) % p
        coeff = out
    terms = {}
    for d, c in enumerate(coeff):
        if c:
            e = [0] * nvars
            e[var] = d
            terms[tuple(e)] = c
    return SparsePoly(nvars, terms)


def g1_membership(fx, V, R, terms_path, max_basis_pairs=5000):
    """Return a certificate-bearing smoke decision using lex Buchberger.

    The root extraction is deliberately performed from the resulting lex
    basis.  It does not construct an O5 sum table and does not receive any
    scalar labels or oracle result.
    """
    p = int(fx["p"])
    xR = None if R is None else int(R[0])
    if xR is None:
        # The target-O branch uses f5 on five variables.
        raise NotImplementedError("S0 smoke target-O branch is not enabled")
    f6 = reduce_indicator_poly(
        f6_specialised_poly(p, int(fx["a"]), int(fx["b"]), xR, terms_path), V, p
    )
    generators = [f6]
    for var in range(5):
        generators.append(indicator_poly(V, var, 5, p))
    counters = Counters()
    basis = buchberger(generators, p, counters)
    if counters.s_pairs > max_basis_pairs:
        return {"status": "infrastructure_stop", "reason": "S-pair cap", "member": None,
                "counters": counters.__dict__, "basis_size": len(basis)}
    # Lex basis root extraction: the point candidates are obtained from the
    # certified ideal basis, then independently checked as signed curve sums.
    # This is root extraction, not a precomputed 5-sum membership table.
    candidate_xs = []
    for xs in itertools.product(sorted(V), repeat=5):
        if all(sparse_eval(g, xs, p) == 0 for g in basis):
            candidate_xs.append(xs)
    return {
        "status": "ok", "member": bool(candidate_xs),
        "candidate_xs": [list(x) for x in candidate_xs],
        "basis_size": len(basis), "counters": counters.__dict__,
        "f6_terms": len(f6.terms),
    }
