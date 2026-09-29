#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recheck.py  --  executable hand-check for TASK-20260916-64a93b
                Validator blind read, joint J-4 (a/b/c) and the J-5 proves-too-much control.
                Subject: Igor Semaev, ePrint 2015/310 (revised 2015-04-10),
                frozen at inputs/SEMAEV-2015-310/eprint-2015-310.pdf
                sha256 d6636436e2e9254d07e2270f61e6d1892de8d0d5f350a1c5232f60cafe39a7db

WHAT THIS IS AND IS NOT
-----------------------
This is a LABELLED HAND-CHECK of symbolic identities that the paper itself states,
computed from scratch in plain Python 3 with no third-party dependencies.

It is NOT a measurement.  It runs no Groebner basis, no F4, no solver, and it
computes NO value of d_F4 (the regularity degree) for anything.  It computes only
BOOLEAN COORDINATE DEGREES of explicitly written polynomials -- that is, the
quantity Semaev writes `deg_{F2}` on p.10 of the frozen PDF.  Every number it
prints is a degree of a polynomial the paper prints, or of a polynomial this file
constructs from the paper's own formula (14).

`maximum_runs` for this task is 0 and this file does not consume it.

THE CLAIM IT CHECKS (the heaviest claim in report.md)
-----------------------------------------------------
Semaev's justification for Assumption 1 has exactly one algebraic input: the
degree fall exhibited on p.10,

      deg_{F2} S_3(x1,x2,x3)      = 3
      deg_{F2} x1*S_3(x1,x2,x3)   = 3     <  deg_{F2} x1 + deg_{F2} S_3 = 4

Assumption 1 is stated under the hypothesis `k = ceil(n/m)` and `V a subspace of
dimension k`.  On p.13 the same paper reports that its CONCLUSION is false one
parameter-step away:

      "the maximal degree(regularity degree) generally exceeds 4 when
       k > ceil(n/m) though the first fall degree is still 4."

So the J-5 question is mechanical: DOES THE ARGUMENT'S ONLY ALGEBRAIC INPUT
DEPEND ON k AT ALL?  If it does not, the argument runs unchanged in a regime
where the author reports its conclusion false, which is the proves-too-much
signature.  RC-2 below answers that by recomputing the fall for every
k = 1..n, for two different fields, and for a random (non-polynomial) subspace.

CHECKS
------
  RC-0  field construction is a field (irreducibility by trial division)
  RC-1  the p.10 argument, verbatim: the four degrees and the printed expansion
  RC-2  *** J-5 CONTROL ***  the same fall, swept over dim V = k = 1..n
  RC-3  the terminal equation S_3(x,u,z): which degree-2 field multipliers fall
  RC-4  independent cross-check of every degree by the Hamming-weight rule
  RC-5  coverage bookkeeping for "at least t-2 of the equations" at t = 2
  RC-6  Table 3 rho-crossover re-derived from the paper's own stated formula
        (NOT blind -- see the note printed at RC-6)

Author: validator subagent, TASK-20260916-64a93b, 2026-09-21.
"""

import re
import sys
import math
import random
import os

FAILURES = []
CHECKS = 0


def check(label, got, want, note=""):
    global CHECKS
    CHECKS += 1
    ok = (got == want)
    if not ok:
        FAILURES.append((label, got, want))
    print("  [%s] %-58s got=%-22s want=%-22s %s"
          % ("PASS" if ok else "FAIL", label, repr(got), repr(want), note))
    return ok


def report(label, value, note=""):
    print("  [ -- ] %-58s %s  %s" % (label, repr(value), note))


# ===========================================================================
# GF(2)[x] and GF(2^n)
# ===========================================================================

def gf2_polymod(a, m):
    """a mod m in GF(2)[x], both as integer bitmasks (bit i = coeff of x^i)."""
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def is_irreducible(m):
    """Trial division over GF(2)[x] by every polynomial of degree 1..deg(m)//2."""
    n = m.bit_length() - 1
    if n < 1:
        return False
    for d in range(1, n // 2 + 1):
        for c in range(1 << d, 1 << (d + 1)):
            if gf2_polymod(m, c) == 0:
                return False
    return True


def alpha_powers(n, modulus):
    """alpha^i reduced mod f(alpha), i = 0..2n-2, as bitmasks on the basis
    1, alpha, ..., alpha^{n-1}."""
    pw = [1]
    for _ in range(1, 2 * n):
        v = pw[-1] << 1
        if v & (1 << n):
            v ^= modulus
        pw.append(v & ((1 << n) - 1))
    return pw


# ===========================================================================
# Multilinear (Boolean) polynomials over GF(2).
#   a polynomial is a frozenset of monomials; a monomial is a frozenset of
#   variable ids.  Addition is symmetric difference (char 2); multiplication
#   is union of index sets, i.e. the ring GF(2)[X]/(X_i^2 - X_i).
# ===========================================================================

BZERO = frozenset()
BONE = frozenset({frozenset()})


def bmul(p, q):
    out = set()
    for a in p:
        for b in q:
            m = a | b
            if m in out:
                out.discard(m)
            else:
                out.add(m)
    return frozenset(out)


def bdeg(p):
    """-1 for the zero polynomial; 0 for a nonzero constant."""
    return max((len(m) for m in p), default=-1)


# ===========================================================================
# Symbolic elements of F_{2^n}: an n-tuple of Boolean coordinate polynomials.
# ===========================================================================

class Field(object):
    def __init__(self, n, modulus, name):
        self.n = n
        self.modulus = modulus
        self.name = name
        self.pw = alpha_powers(n, modulus)

    def zero(self):
        return tuple(BZERO for _ in range(self.n))

    def const(self, bits):
        return tuple(BONE if (bits >> c) & 1 else BZERO for c in range(self.n))

    def add(self, A, B):
        return tuple(a ^ b for a, b in zip(A, B))

    def mul(self, A, B):
        n = self.n
        res = [BZERO] * n
        for i in range(n):
            if not A[i]:
                continue
            for j in range(n):
                if not B[j]:
                    continue
                pr = bmul(A[i], B[j])
                if not pr:
                    continue
                mask = self.pw[i + j]
                for c in range(n):
                    if (mask >> c) & 1:
                        res[c] = res[c] ^ pr
        return tuple(res)

    def pow(self, A, e):
        if e == 0:
            return self.const(1)
        r = None
        base = A
        while e:
            if e & 1:
                r = base if r is None else self.mul(r, base)
            e >>= 1
            if e:
                base = self.mul(base, base)
        return r

    def deg(self, A):
        """deg_{F2} in Semaev's sense: total degree of the coordinate Boolean
        functions, i.e. the max multilinear degree over the n coordinates."""
        return max((bdeg(p) for p in A), default=-1)

    def var(self, basis, vids):
        """The generic element sum_j X_{vid_j} * basis_j of the subspace spanned
        by `basis` (a list of field elements as bitmasks)."""
        res = [set() for _ in range(self.n)]
        for b, v in zip(basis, vids):
            mono = frozenset({v})
            for c in range(self.n):
                if (b >> c) & 1:
                    s = res[c]
                    if mono in s:
                        s.discard(mono)
                    else:
                        s.add(mono)
        return tuple(frozenset(s) for s in res)


def S3(F, x1, x2, x3, B):
    """Semaev's third summation polynomial in characteristic 2, eq. (14) of the
    frozen PDF p.9:  S3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B."""
    t = F.add(F.add(F.mul(x1, x2), F.mul(x1, x3)), F.mul(x2, x3))
    return F.add(F.add(F.mul(t, t), F.mul(F.mul(x1, x2), x3)), B)


def poly_basis(F, k):
    """V = {polynomials in alpha of degree < k}, the paper's own choice (p.9)."""
    return [1 << j for j in range(k)]


def random_basis(F, k, rng):
    """V = a random subspace of dimension k.  Assumption 1 quantifies over
    'any subspace V of dimension k' (p.10), so this case is in its scope; the
    paper's Table 1 rows marked 6* use exactly such a V."""
    basis = []
    span = {0}
    while len(basis) < k:
        c = rng.randrange(1, 1 << F.n)
        if c in span:
            continue
        basis.append(c)
        span = {s ^ (c * 0) for s in span} | {s ^ c for s in span}
    return basis


# ===========================================================================
print("=" * 78)
print("recheck.py -- TASK-20260916-64a93b, validator blind read of Semaev 2015/310")
print("ZERO RUNS, ZERO MEASUREMENTS.  Symbolic degree arithmetic only.")
print("=" * 78)

F7 = Field(7, (1 << 7) | (1 << 1) | 1, "F_{2^7}, f = x^7 + x + 1")
F5 = Field(5, (1 << 5) | (1 << 2) | 1, "F_{2^5}, f = x^5 + x^2 + 1")
F9 = Field(9, (1 << 9) | (1 << 1) | 1, "F_{2^9}, f = x^9 + x + 1")

# ---------------------------------------------------------------- RC-0 -----
print("\nRC-0  the constructed rings are fields (trial division over GF(2)[x])")
for Fq in (F5, F7, F9):
    check("irreducible: " + Fq.name, is_irreducible(Fq.modulus), True)
    check("reduction table covers alpha^0 .. alpha^(2n-2) (" + Fq.name + ")",
          len(Fq.pw) >= 2 * Fq.n - 1, True)

# ---------------------------------------------------------------- RC-1 -----
print("\nRC-1  the argument of Semaev p.10, verbatim")
print("      frozen text inputs/SEMAEV-2015-310/paper_fulltext.md :561-600")
print("      PDF p.10 y=577 / y=581 / y=602 / y=605 / y=606 / y=608")

for Fq in (F5, F7, F9):
    n = Fq.n
    k = n  # variables range over all of F_{2^n}: the paper says "in V or F_{2^n}"
    bas = poly_basis(Fq, k)
    x1 = Fq.var(bas, [0 * n + j for j in range(k)])
    x2 = Fq.var(bas, [1 * n + j for j in range(k)])
    x3 = Fq.var(bas, [2 * n + j for j in range(k)])
    Bc = Fq.const(1)  # B = 1, the curve parameter of the paper's Table 1

    s = S3(Fq, x1, x2, x3, Bc)
    x1s = Fq.mul(x1, s)

    # (a) "degF2 S3(x1, x2, x3) = 3."                       PDF p.10 y=577
    check("RC-1a deg_F2 S3(x1,x2,x3)          [%s]" % Fq.name, Fq.deg(s), 3)
    # (b) "degF2 x1S3(x1, x2, x3) = 3"                      PDF p.10 y=581
    check("RC-1b deg_F2 x1*S3(x1,x2,x3)       [%s]" % Fq.name, Fq.deg(x1s), 3)
    # "despite degF2 x1 + degF2 S3(x1,x2,x3) = 4"           PDF p.10 y=602
    check("RC-1c deg_F2 x1 + deg_F2 S3        [%s]" % Fq.name,
          Fq.deg(x1) + Fq.deg(s), 4, "=> A FALL AT DEGREE 4 EXISTS")
    check("RC-1d the fall is non-trivial (sum != 0) [%s]" % Fq.name,
          any(p for p in x1s), True)

    # (d) the printed expansion, PDF p.10 y=443.5, reassembled from glyph
    #     coordinates in reextract.md:
    #        x1*S3 = x1^3 x2^2 + x1^3 x3^2 + x1 x2^2 x3^2 + x1^2 x2 x3 + B x1
    rhs = Fq.zero()
    for term in (
        Fq.mul(Fq.pow(x1, 3), Fq.pow(x2, 2)),
        Fq.mul(Fq.pow(x1, 3), Fq.pow(x3, 2)),
        Fq.mul(Fq.mul(x1, Fq.pow(x2, 2)), Fq.pow(x3, 2)),
        Fq.mul(Fq.mul(Fq.pow(x1, 2), x2), x3),
        Fq.mul(Bc, x1),
    ):
        rhs = Fq.add(rhs, term)
    check("RC-1e printed expansion is an identity [%s]" % Fq.name, x1s == rhs, True)

    # (i) is the fall degree EXACTLY 4, or only <= 4?  A fall at degree 3 would
    #     need max_i(deg g_i + deg f_i) = 3 with deg f_i = 3, i.e. CONSTANT
    #     multipliers: a nonzero F_2-combination of the n coordinates of S_3
    #     whose degree-3 part vanishes.  Rank of the degree-3 parts settles it.
    monos3 = sorted({m for p in s for m in p if len(m) == 3}, key=sorted)
    idx = {m: i for i, m in enumerate(monos3)}
    rows = []
    for p in s:
        r = 0
        for m in p:
            if len(m) == 3:
                r |= 1 << idx[m]
        rows.append(r)
    rank, piv = 0, []
    for r in rows:
        for q in piv:
            r = min(r, r ^ q)
        if r:
            piv.append(r)
            piv.sort(reverse=True)
            rank += 1
    check("RC-1i deg-3 parts of the n coordinates are F_2-independent [%s]"
          % Fq.name, rank, n,
          "=> no fall at 3 from constants, so d_ff = 4 exactly here")

# the terminal equation: z a constant of F_{2^n}, not a variable
print("\n      the terminal equation S_3(x1,x2,z), z constant  (PDF p.10 y=602-608)")
rng = random.Random(20260921)
for Fq in (F5, F7, F9):
    n = Fq.n
    bas = poly_basis(Fq, n)
    x1 = Fq.var(bas, [0 * n + j for j in range(n)])
    x2 = Fq.var(bas, [1 * n + j for j in range(n)])
    Bc = Fq.const(1)
    degs_s, degs_x1s, degs_sum = set(), set(), set()
    for _ in range(8):
        z = Fq.const(rng.randrange(1, 1 << n))
        sz = S3(Fq, x1, x2, z, Bc)
        degs_s.add(Fq.deg(sz))
        degs_x1s.add(Fq.deg(Fq.mul(x1, sz)))
        degs_sum.add(Fq.deg(x1) + Fq.deg(sz))
    # "degF2 S3(x1, x2, z) = 2,"                             PDF p.10 y=605
    check("RC-1f deg_F2 S3(x1,x2,z)           [%s]" % Fq.name, sorted(degs_s), [2])
    # "degF2 x1S3(x1, x2, z) = 3,"                           PDF p.10 y=606
    check("RC-1g deg_F2 x1*S3(x1,x2,z)        [%s]" % Fq.name, sorted(degs_x1s), [3])
    # "and degF2 x1 + degF2 S3(x1, x2, z) = 3."              PDF p.10 y=608
    check("RC-1h deg_F2 x1 + deg_F2 S3(..,z)  [%s]" % Fq.name, sorted(degs_sum), [3],
          "=> NO FALL: the paper says 'This argument does not work'")

# ---------------------------------------------------------------- RC-2 -----
print("\nRC-2  *** J-5 PROVES-TOO-MUCH CONTROL ***")
print("      Assumption 1 (PDF p.10 y=276-249) is stated under k = ceil(n/m).")
print("      PDF p.13 y=670/656: the regularity degree 'generally exceeds 4 when")
print("      k > ceil(n/m) though the first fall degree is still 4'.")
print("      QUESTION: does the fall exhibition depend on k at all?")
print("      sweep over k = 1..n, V = {polys in alpha of degree < k}:")

sweep_rows = []
for Fq in (F5, F7):
    n = Fq.n
    Bc = Fq.const(1)
    for k in range(1, n + 1):
        bas = poly_basis(Fq, k)
        x1 = Fq.var(bas, [0 * n + j for j in range(k)])
        x2 = Fq.var(bas, [1 * n + j for j in range(k)])
        x3 = Fq.var(bas, [2 * n + j for j in range(k)])
        s = S3(Fq, x1, x2, x3, Bc)
        x1s = Fq.mul(x1, s)
        d_s, d_x1, d_prod = Fq.deg(s), Fq.deg(x1), Fq.deg(x1s)
        falls = (d_prod < d_x1 + d_s) and any(p for p in x1s)
        sweep_rows.append((Fq.name, k, d_s, d_x1 + d_s, d_prod, falls))
        print("      %-24s k=%-2d  deg S3=%d  deg x1+deg S3=%d  deg(x1*S3)=%d  fall=%s"
              % (Fq.name, k, d_s, d_x1 + d_s, d_prod, falls))

check("RC-2a a fall exists at EVERY k = 1..n, in every field swept",
      sorted({r[5] for r in sweep_rows}), [True])
check("RC-2b for k >= 2 the fall is exactly the p.10 one (bound 4 -> deg 3)",
      sorted({(r[3], r[4]) for r in sweep_rows if r[1] >= 2}), [(4, 3)])
check("RC-2b' at the degenerate k = 1 the fall is DEEPER (4 -> 2), not absent",
      sorted({(r[3], r[4]) for r in sweep_rows if r[1] == 1}), [(4, 2)],
      "k=1 puts x_i in F_2, so more collapses; still no k kills the fall")
check("RC-2c the fall is present at k = n, the largest possible subspace",
      all(r[5] for r in sweep_rows if r[1] == (5 if "2^5" in r[0] else 7)), True)
check("RC-2d the sweep really covered k > ceil(n/m) for realistic m",
      sorted({r[1] for r in sweep_rows if "2^7" in r[0] and r[1] > -(-7 // 3)}),
      [4, 5, 6, 7], "ceil(7/3) = 3, so k = 4..7 is the exceeded regime")

print("\n      and for a RANDOM subspace V of dimension k (Assumption 1 says")
print("      'any subspace V of dimension k'; Table 1's 6* rows use one):")
rng2 = random.Random(4223)
rand_ok = True
for Fq in (F5, F7):
    n = Fq.n
    Bc = Fq.const(1)
    for k in (2, 3, n - 1, n):
        bas = random_basis(Fq, k, rng2)
        x1 = Fq.var(bas, [0 * n + j for j in range(k)])
        x2 = Fq.var(bas, [1 * n + j for j in range(k)])
        x3 = Fq.var(bas, [2 * n + j for j in range(k)])
        s = S3(Fq, x1, x2, x3, Bc)
        x1s = Fq.mul(x1, s)
        f = (Fq.deg(x1s) < Fq.deg(x1) + Fq.deg(s)) and any(p for p in x1s)
        rand_ok = rand_ok and (f or Fq.deg(s) < 3)
        print("      %-24s random V, k=%-2d  deg S3=%d  bound=%d  deg(x1*S3)=%d  fall=%s"
              % (Fq.name, k, Fq.deg(s), Fq.deg(x1) + Fq.deg(s), Fq.deg(x1s), f))
check("RC-2e the fall survives a random subspace too", rand_ok, True)

print("\n      and for the MIXED shape of system (5), where u_i range over the")
print("      whole field and x_i over V (PDF p.4 eq. (5)):")
mixed_ok = True
for Fq in (F7,):
    n = Fq.n
    Bc = Fq.const(1)
    for k in (2, 3, 4, n):
        basV = poly_basis(Fq, k)
        basF = poly_basis(Fq, n)
        u1 = Fq.var(basF, [0 * n + j for j in range(n)])
        u2 = Fq.var(basF, [1 * n + j for j in range(n)])
        xv = Fq.var(basV, [2 * n + j for j in range(k)])
        s = S3(Fq, u1, u2, xv, Bc)
        u1s = Fq.mul(u1, s)
        f = (Fq.deg(u1s) < Fq.deg(u1) + Fq.deg(s)) and any(p for p in u1s)
        mixed_ok = mixed_ok and f
        print("      %-24s S3(u1,u2,x in V_%d)  deg S3=%d  bound=%d  deg=%d  fall=%s"
              % (Fq.name, k, Fq.deg(s), Fq.deg(u1) + Fq.deg(s), Fq.deg(u1s), f))
check("RC-2f the fall survives the mixed field/subspace shape", mixed_ok, True)

print("""
      RC-2g  REACH OF THE SAME ARGUMENT UNDER AN AFFINE (COSET) SHIFT.
      Semaev's descent is linear: x_i = sum_j X_ij alpha_j.  The neighbouring
      literature (Nagao 2015/984 Def. 7/8, :692-713) descends the same S_3 with
      x_i = v_i + sum_j X_ij alpha_j for nonzero coset shifts v_i.  Semaev's
      exhibition uses ONLY deg_F2(x^2) = deg_F2(x), and squaring is F_2-AFFINE,
      not merely F_2-linear -- so the question is whether the fall survives.
      This is a statement about the reach of SEMAEV's argument.  It is computed
      here for the FAKE (multilinear) degree only and says nothing about any
      true-degree claim.  Multipliers are field variables, exactly as on p.10.""")

shift_rows = []
rng3 = random.Random(310310)
Fq = F7
n = Fq.n
basF = poly_basis(Fq, n)
Bc = Fq.const(1)
for k in (2, 3, 4):
    basV = poly_basis(Fq, k)
    for trial in range(3):
        v1 = rng3.randrange(1, 1 << n)
        v2 = rng3.randrange(1, 1 << n)
        v3 = rng3.randrange(1, 1 << n)
        # three shifted subspace variables (EQS4-style X_i in V + v_i)
        X1 = Fq.add(Fq.const(v1), Fq.var(basV, [0 * n + j for j in range(k)]))
        X2 = Fq.add(Fq.const(v2), Fq.var(basV, [1 * n + j for j in range(k)]))
        X3 = Fq.add(Fq.const(v3), Fq.var(basV, [2 * n + j for j in range(k)]))
        s = S3(Fq, X1, X2, X3, Bc)
        p = Fq.mul(X1, s)
        shift_rows.append(("3 shifted V-vars", k, Fq.deg(X1) + Fq.deg(s),
                           Fq.deg(p),
                           Fq.deg(p) < Fq.deg(X1) + Fq.deg(s) and any(q for q in p)))
        # the EQS3 link shape: two full-field U's and one shifted V variable
        U1 = Fq.var(basF, [0 * n + j for j in range(n)])
        U2 = Fq.var(basF, [1 * n + j for j in range(n)])
        s2 = S3(Fq, U1, U2, X3, Bc)
        p2 = Fq.mul(U1, s2)
        shift_rows.append(("U,U,shifted X", k, Fq.deg(U1) + Fq.deg(s2),
                           Fq.deg(p2),
                           Fq.deg(p2) < Fq.deg(U1) + Fq.deg(s2)
                           and any(q for q in p2)))
for shape in ("3 shifted V-vars", "U,U,shifted X"):
    rs = [r for r in shift_rows if r[0] == shape]
    print("      %-18s  bounds=%s  degs=%s  falls=%s"
          % (shape, sorted({r[2] for r in rs}), sorted({r[3] for r in rs}),
             sorted({r[4] for r in rs})))
check("RC-2g the p.10 fall survives nonzero coset shifts too",
      sorted({r[4] for r in shift_rows}), [True],
      "FAKE degree only; asserts nothing about the true degree")

print("""
      CONCLUSION OF RC-2.  The exhibition depends on the Frobenius collapse
      deg_F2(x^2) = deg_F2(x) and on nothing else.  dim V enters the degrees
      nowhere.  So the premise of Semaev's justification holds unchanged at
      k > ceil(n/m), where the paper itself reports the conclusion d_F4 <= 4
      is FALSE.  The argument survives its own known-false object.""")

# ---------------------------------------------------------------- RC-3 -----
print("\nRC-3  the terminal equation: which degree-2 field multipliers DO fall?")
print("      Semaev gives none ('This argument does not work', p.10 y=602) and")
print("      falls back on experiments.  Nagao 2015/984 :452-459 attributes the")
print("      multiplier x*u to Semaev.  Enumerate m = x^a u^b, deg_F2(m) <= 2.")

Fq = F7
n = Fq.n
bas = poly_basis(Fq, n)
X = Fq.var(bas, [0 * n + j for j in range(n)])
U = Fq.var(bas, [1 * n + j for j in range(n)])
Bc = Fq.const(1)
Z = Fq.const(0b1011011)
Szt = S3(Fq, X, U, Z, Bc)
d_S = Fq.deg(Szt)
report("RC-3  deg_F2 S3(x,u,z)", d_S)

fall_table = []
for a in range(0, 9):
    for b in range(0, 9):
        if a == 0 and b == 0:
            continue
        mono = Fq.mul(Fq.pow(X, a), Fq.pow(U, b)) if a and b else (
            Fq.pow(X, a) if a else Fq.pow(U, b))
        dm = Fq.deg(mono)
        if dm != 2:
            continue
        prod = Fq.mul(mono, Szt)
        bound = dm + d_S
        dp = Fq.deg(prod)
        fell = (dp < bound) and any(p for p in prod)
        fall_table.append((a, b, dm, bound, dp, fell))

for (a, b, dm, bound, dp, fell) in sorted(fall_table)[:14]:
    print("      m = x^%d u^%d   deg_F2 m=%d  bound=%d  deg_F2(m*S3)=%d  FALL=%s"
          % (a, b, dm, bound, dp, fell))

xu = [r for r in fall_table if (r[0], r[1]) == (1, 1)]
xu2 = [r for r in fall_table if (r[0], r[1]) == (1, 2)]
x2u = [r for r in fall_table if (r[0], r[1]) == (2, 1)]
check("RC-3a m = x*u   (the multiplier Nagao attributes to Semaev) falls?",
      xu[0][5], False, "deg(m*S3)=%d = bound %d" % (xu[0][4], xu[0][3]))
check("RC-3b m = x*u^2 falls?", xu2[0][5], True,
      "deg(m*S3)=%d < bound %d" % (xu2[0][4], xu2[0][3]))
check("RC-3c m = x^2*u falls?", x2u[0][5], True,
      "deg(m*S3)=%d < bound %d" % (x2u[0][4], x2u[0][3]))
check("RC-3d at least one degree-2 multiplier gives a fall at degree 4",
      any(r[5] for r in fall_table), True)
report("RC-3e degree-2 multipliers (a,b) that DO fall",
       [(r[0], r[1]) for r in sorted(fall_table) if r[5]])

# could the terminal equation fall BELOW 4?  that needs deg_F2(m) = 1, so
# max = 1 + 2 = 3, and deg(m*S3) <= 2.  Enumerate every such monomial.
low = []
for a in range(0, 17):
    for b in range(0, 17):
        if a == 0 and b == 0:
            continue
        mono = Fq.mul(Fq.pow(X, a), Fq.pow(U, b)) if a and b else (
            Fq.pow(X, a) if a else Fq.pow(U, b))
        if Fq.deg(mono) != 1:
            continue
        prod = Fq.mul(mono, Szt)
        low.append((a, b, Fq.deg(prod), Fq.deg(prod) < 1 + d_S))
report("RC-3f degree-1 multipliers tried on S3(x,u,z)", len(low))
check("RC-3g none of them falls below degree 4 (so d_ff of the terminal "
      "equation is not driven under 4 by a monomial multiplier)",
      any(r[3] for r in low), False)

# ---------------------------------------------------------------- RC-4 -----
print("\nRC-4  independent cross-check: deg_F2(x^a) should equal popcount(a),")
print("      because x^(2^i) is F_2-linear in the coordinates of x (Frobenius).")
Fq = F7
n = Fq.n
bas = poly_basis(Fq, n)
X = Fq.var(bas, [j for j in range(n)])
agree = []
for a in range(1, 40):
    agree.append((a, Fq.deg(Fq.pow(X, a)), bin(a).count("1")))
bad = [t for t in agree if t[1] != t[2]]
check("RC-4a deg_F2(x^a) == popcount(a) for a = 1..39", bad, [])
print("      (this is the whole mechanism: it is a fact about squaring in")
print("       characteristic 2 and says nothing whatever about dim V.)")

# ---------------------------------------------------------------- RC-5 -----
print("\nRC-5  coverage bookkeeping for 'at least t-2 of the equations in (5)")
print("      have the first fall degree 4' (PDF p.10 y=609) against Assumption 1's")
print("      range '2 <= t <= m' (PDF p.10 y=249).")

for t in (2, 3, 4, 5, 6):
    n_eqs = t - 1          # PDF p.4 eq. (5): t-1 equations
    n_proved = max(t - 2, 0)
    print("      t=%d : system (5) has %d equation(s); the sentence covers %d of them"
          % (t, n_eqs, n_proved))
check("RC-5a at t = 2 the sentence covers ZERO of the equations", max(2 - 2, 0), 0)
check("RC-5b at t = 2 system (5) is nonetheless one equation", 2 - 1, 1)
check("RC-5c Assumption 1's range includes t = 2", 2 >= 2, True)

TABLES = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    *([".."] * 6 + ["inputs", "SEMAEV-2015-310", "tables.yaml"])))
if os.path.exists(TABLES):
    txt = open(TABLES, encoding="utf-8").read()
    rows_t2 = re.findall(r"\{n: (\d+), m: (\d+), t: 2,", txt)
    report("RC-5d Table 2 rows with t = 2 (n, m)", rows_t2,
           "experimental cover for the case the argument does not reach")
    check("RC-5e Table 2 does contain t = 2 rows", len(rows_t2) > 0, True)

    # "To fill the tables 2300 Boolean systems ... where t = m, were solved"
    # (PDF p.11 y=453.5) at "100 random z" per row (PDF p.10-11).
    t1 = len(re.findall(r"\{n: \d+, n_random_f:", txt))
    t2_all = re.findall(r"\{n: (\d+), m: (\d+), t: (\d+),", txt)
    t2_tm = [r for r in t2_all if r[1] == r[2]]
    report("RC-5f Table 1 rows (all t = m)", t1)
    report("RC-5f Table 2 rows, of which t = m", (len(t2_all), len(t2_tm)))
    report("RC-5f t = m rows x 100 z", (t1 + len(t2_tm)) * 100,
           "vs the paper's stated 2300 -- a one-row (100-system) gap")
    check("RC-5g the stated 2300 is within one table row of the row count",
          abs((t1 + len(t2_tm)) * 100 - 2300) <= 100, True,
          "NOT RESOLVED: which row is not counted is not determinable here")
else:
    report("RC-5d tables.yaml not found at", TABLES, "(skipped)")

# ---------------------------------------------------------------- RC-6 -----
print("\nRC-6  Table 3 crossover, re-derived from the paper's own stated formulas")
print("      stage 1 = m! * 2^(n/m) * n^12   (eq. 15 at omega = 3)")
print("      Pollard rho = 2^(n/2).  Paper states 'better than Pollard's for n > 310'.")
print("      NOT BLIND: inputs/SEMAEV-2015-310/tables.yaml derived_checks already")
print("      states n = 302, and this reader read that file before writing this.")


def stage1(n_, m_):
    return math.lgamma(m_ + 1) / math.log(2) + n_ / m_ + 12 * math.log2(n_)


cross = None
for nn in range(50, 601):
    best = min(stage1(nn, mm) for mm in range(2, 40))
    if best < nn / 2.0:
        cross = nn
        break
report("RC-6a smallest n at which min_m stage1 < 2^(n/2)", cross)
check("RC-6b the paper's stated threshold n > 310 is conservative "
      "w.r.t. its own formula", cross is not None and cross <= 310, True)
for nn in (310, 409, 571):
    bm = min(range(2, 40), key=lambda mm: stage1(nn, mm))
    report("RC-6c n=%d optimal m, log2(stage1), log2(rho)" % nn,
           (bm, round(stage1(nn, bm), 1), nn / 2.0))

# ===========================================================================
print("\n" + "=" * 78)
print("SUMMARY: %d checks, %d failure(s)" % (CHECKS, len(FAILURES)))
for f in FAILURES:
    print("  FAILED:", f)
print("=" * 78)
print("""
WHAT THIS DOES NOT SHOW.
  * Nothing here measures d_F4.  The regularity degree is what Assumption 1 is
    about and it is not computed anywhere in this file.  RC-2 shows only that
    the ARGUMENT for Assumption 1 has no k-dependence; the falsity of the
    conclusion at k > ceil(n/m) is the PAPER'S OWN report (p.13), not a
    measurement by this program.
  * A fall exhibition gives d_ff <= 4, never d_ff = 4, and the paper argues
    only the <= direction.  RC-1i supplies the one lower bound in this file,
    and its scope is narrow: it rules out a fall at 3 for the n coordinates of
    a SINGLE non-terminal S_3 link, where deg f_i = 3 forces any degree-3 fall
    to use constant multipliers, so the rank of the degree-3 parts settles it.
    It says nothing about the whole system (5), where coordinates of different
    links could in principle combine, and that case is not checked here.
  * RC-3's multipliers are checked over F_{2^7} at one z and one B.  A fall
    found at one instance is an upper bound at that instance; it is evidence
    that the terminal-equation gap is fillable, not a proof that it is filled.
  * All degrees are computed in the multilinear (Boolean) ring, i.e. the FAKE
    quantity in the taxonomy of Nagao 2015/984 Definition 6.  This file says
    nothing about the TRUE first fall degree of Nagao's Definition 5.
""")
sys.exit(1 if FAILURES else 0)
