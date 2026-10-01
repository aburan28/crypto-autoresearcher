#!/usr/bin/env python3
"""RECHECK (not a measurement) for TASK-20260916-9da6e0, joints J-1/J-2/J-3/J-5.

This file is a hand-check of algebraic steps, mechanised so it survives the
session that produced it.  It performs NO experiment, samples nothing, and
measures no property of any research object.  Every number it prints is an
exact finite computation in F_p[X_1..X_N] that a reader could do by hand.

Plain Python 3, standard library only, deterministic, no randomness.

Four checks:

  CHECK 1  Example 1 of Nagao 2015/984 (PDF page 5) is internally inconsistent:
           the polynomial it defines is not the polynomial it prints as its
           expansion, and not the one its final line produces.  A one-character
           reconstruction repairs it.

  CHECK 2  The inductive step of Nagao 2013/549's Lemma 2 -- the statement
           2015/984 quotes as its Lemma 3 -- is executed on concrete tuples:
           identity (3) of the proof, membership of G^new in the solution set,
           strict descent of psi, and the degree bound at termination.

  CHECK 3  A counterexample to Lemma 4 of 2015/984 AS PRINTED, over F_2[X,Y]:
              f_1 = X^2 Y ,  f_2 = XY + X .
           Exhaustive over every admissible multiplier at every degree tested.

  CHECK 4  The J-5 proves-too-much control: the J-3 derivation is run against
           the object where Lemma 4's conclusion is known false, to see whether
           it goes through there too.

Conventions declared before any output:
  * deg(0) := -1.
  * "reduced mod S_fe" means the normal form modulo {X_i^p - X_i}: every
    exponent e >= 1 is replaced by ((e-1) mod (p-1)) + 1, i.e. X^e -> X for
    p = 2.  Reduction is F_p-linear and never raises total degree.
  * Monomial order for leading terms: graded reverse lexicographic (total
    degree first).  Nagao's proof fixes only "prod X^e_i > prod X^f_i when
    sum e_i > sum f_i", i.e. ANY graded order; grevlex is one.
  * Two readings of condition (1) of a first-fall definition are computed
    separately and never mixed:
      "EQ"  max_s deg(g_s s) == d      (Nagao 2013/549 Definition 1)
      "GE"  max_s deg(g_s s) >= d      (Nagao 2015/984 Definitions 5 and 6,
                                        confirmed in the PDF, not an
                                        extraction artifact)
    2013/549's Definition 1 additionally carries condition 4, deg(s) <= d;
    2015/984's Definitions 5 and 6 do not.  Both are reported.
"""

from itertools import product

NEG = -1  # deg of the zero polynomial


# --------------------------------------------------------------------------
# sparse polynomials over F_p, exponent tuples of fixed length
# --------------------------------------------------------------------------

class Poly:
    __slots__ = ("p", "n", "c")

    def __init__(self, p, n, c=None):
        self.p, self.n = p, n
        self.c = {}
        if c:
            for m, v in c.items():
                v %= p
                if v:
                    self.c[m] = v

    def __eq__(self, o):
        return self.c == o.c

    def __hash__(self):
        return hash(frozenset(self.c.items()))

    def is_zero(self):
        return not self.c

    def deg(self):
        return max((sum(m) for m in self.c), default=NEG)

    def __add__(self, o):
        r = dict(self.c)
        for m, v in o.c.items():
            w = (r.get(m, 0) + v) % self.p
            if w:
                r[m] = w
            else:
                r.pop(m, None)
        return Poly(self.p, self.n, r)

    def neg(self):
        return Poly(self.p, self.n, {m: (-v) % self.p for m, v in self.c.items()})

    def __mul__(self, o):
        r = {}
        for m1, v1 in self.c.items():
            for m2, v2 in o.c.items():
                m = tuple(a + b for a, b in zip(m1, m2))
                w = (r.get(m, 0) + v1 * v2) % self.p
                if w:
                    r[m] = w
                else:
                    r.pop(m, None)
        return Poly(self.p, self.n, r)

    def scal(self, k):
        return Poly(self.p, self.n, {m: v * k for m, v in self.c.items()})

    def reduce_fe(self):
        """normal form modulo {X_i^p - X_i}"""
        r = {}
        for m, v in self.c.items():
            mm = tuple(e if e < self.p else ((e - 1) % (self.p - 1)) + 1 for e in m)
            w = (r.get(mm, 0) + v) % self.p
            if w:
                r[mm] = w
            else:
                r.pop(mm, None)
        return Poly(self.p, self.n, r)

    def divides_by_mono(self, mono):
        """exact division by a monomial, or None"""
        r = {}
        for m, v in self.c.items():
            if any(a < b for a, b in zip(m, mono)):
                return None
            r[tuple(a - b for a, b in zip(m, mono))] = v
        return Poly(self.p, self.n, r)

    def subst_const(self, idx, val):
        """substitute X_idx := val (an element of F_p), keeping the variable
        slot so that printed names stay aligned with the original ring."""
        r = {}
        for m, v in self.c.items():
            w = (v * pow(val, m[idx], self.p)) % self.p
            mm = m[:idx] + (0,) + m[idx + 1:]
            t = (r.get(mm, 0) + w) % self.p
            if t:
                r[mm] = t
            else:
                r.pop(mm, None)
        return Poly(self.p, self.n, r)

    def __repr__(self):
        if not self.c:
            return "0"
        names = "XYZUVW"[: self.n]
        out = []
        for m in sorted(self.c, key=lambda m: (-sum(m), m), reverse=True):
            v = self.c[m]
            s = "" if (v == 1 and any(m)) else str(v)
            for nm, e in zip(names, m):
                if e == 1:
                    s += nm
                elif e > 1:
                    s += "%s^%d" % (nm, e)
            out.append(s or "1")
        return " + ".join(out)


Poly.__sub__ = lambda self, o: self + o.neg()


def grevlex_key(m):
    """graded reverse lex: total degree first, then reverse lex."""
    return (sum(m),) + tuple(-e for e in reversed(m))


def lm(f):
    """leading monomial (exponent tuple) or None for 0"""
    if f.is_zero():
        return None
    return max(f.c, key=grevlex_key)


def lt(f):
    m = lm(f)
    return None if m is None else Poly(f.p, f.n, {m: f.c[m]})


def mono(p, n, expo, coeff=1):
    return Poly(p, n, {tuple(expo): coeff})


def const(p, n, v):
    return Poly(p, n, {(0,) * n: v})


def fieldeq(p, n, i):
    """X_i^p - X_i"""
    e = [0] * n
    e[i] = p
    f = mono(p, n, e)
    e2 = [0] * n
    e2[i] = 1
    return f - mono(p, n, e2)


def polys_up_to_degree(p, n, d):
    """every polynomial of total degree <= d (d < 0 yields only 0)"""
    if d < 0:
        return [Poly(p, n)]
    monos = [m for m in product(range(d + 1), repeat=n) if sum(m) <= d]
    out = []
    for coeffs in product(range(p), repeat=len(monos)):
        out.append(Poly(p, n, dict(zip(monos, coeffs))))
    return out


def banner(t):
    print()
    print("=" * 74)
    print(t)
    print("=" * 74)


# ==========================================================================
# CHECK 1 -- Example 1 of Nagao 2015/984, PDF page 5
# ==========================================================================

def check1():
    banner("CHECK 1  Example 1 of Nagao 2015/984 (PDF p.5) -- internal consistency")
    p, n = 2, 3  # X, Y, Z
    X = mono(p, n, (1, 0, 0))
    Y = mono(p, n, (0, 1, 0))
    Z = mono(p, n, (0, 0, 1))
    X2, Y2, Z2 = X * X, Y * Y, Z * Z
    feX, feY = X2 + X, Y2 + Y          # X^2+X and Y^2+Y  (char 2: + == -)

    # the four printed lines, transcribed verbatim from the PDF spans
    L1 = (X2 + X) * (Y2 + Y) + (X2 + X) * (Y2 + Z)
    Lexp = (mono(p, n, (2, 1, 0)) + mono(p, n, (0, 2, 1)) + mono(p, n, (0, 1, 1))
            + mono(p, n, (2, 0, 1)) + mono(p, n, (1, 2, 0)) + mono(p, n, (1, 0, 1)))
    Lmid = ((X2 + X) * (Y2 + Y) + (X2 + X) * (Y2 + Y)
            + (X2 + X) * (Y2 + Y) + (X2 + X) * (Y2 + Z))
    Lfin = (X + Z) * (Y2 + Y) + (X2 + X) * (Y + Z)

    print("printed line 1  F := (X^2+X)(Y^2+Y) + (X^2+X)(Y^2+Z)   = %s   deg %d"
          % (L1, L1.deg()))
    print("printed expansion  X^2Y+Y^2Z+YZ+X^2Z+XY^2+XZ           = %s   deg %d"
          % (Lexp, Lexp.deg()))
    print("printed middle line (three copies of (X^2+X)(Y^2+Y))   = %s   deg %d"
          % (Lmid, Lmid.deg()))
    print("printed final line (X+Z)(Y^2+Y) + (X^2+X)(Y+Z)         = %s   deg %d"
          % (Lfin, Lfin.deg()))
    print()
    print("line1 == printed expansion ? %s" % (L1 == Lexp))
    print("line1 == middle line       ? %s" % (L1 == Lmid))
    print("line1 == final line        ? %s" % (L1 == Lfin))
    print("printed expansion == final ? %s" % (Lexp == Lfin))
    print("=> the printed chain is INTERNALLY INCONSISTENT: its first line and")
    print("   its last line are different polynomials, differing by %s"
          % (L1 + Lfin))

    # one-character reconstruction: first factor (X^2+X) -> (X^2+Z)
    R1 = (X2 + Z) * (Y2 + Y) + (X2 + X) * (Y2 + Z)
    print()
    print("reconstruction  F := (X^2+Z)(Y^2+Y) + (X^2+X)(Y^2+Z)   = %s   deg %d"
          % (R1, R1.deg()))
    print("reconstruction == printed expansion ? %s" % (R1 == Lexp))
    print("reconstruction == printed final     ? %s" % (R1 == Lfin))
    print("reconstruction ==  0 mod S_fe       ? %s" % R1.reduce_fe().is_zero())
    print("printed line 1 ==  0 mod S_fe       ? %s" % L1.reduce_fe().is_zero())
    print()
    print("why it matters for the lemma being illustrated:")
    print("  the reconstruction's multipliers are (X^2+Z) on (Y^2+Y) and")
    print("  (Y^2+Z) on (X^2+X), both of degree 2 > deg F - p = 1, so it IS an")
    print("  instance the lemma has to repair; the final line's multipliers")
    print("  (X+Z) and (Y+Z) have degree 1 = deg F - p, which is the lemma's")
    print("  conclusion.  Line 1 AS PRINTED collapses to (X^2+X)(Y+Z), whose")
    print("  multiplier already has degree 1, so as printed the example")
    print("  illustrates nothing.")
    print("  line1 as printed == (X^2+X)(Y+Z) ? %s" % (L1 == (X2 + X) * (Y + Z)))
    assert L1 != Lexp and R1 == Lexp and R1 == Lfin


# ==========================================================================
# CHECK 2 -- the inductive step of Nagao 2013/549 Lemma 2
# ==========================================================================

def psi_and_ind(p, n, G):
    """psi(G) = max monomial among LM(G_i X_i^p); IND = argmax set."""
    best, ind = None, []
    for i, g in enumerate(G):
        if g.is_zero():
            continue
        e = [0] * n
        e[i] = p
        m = lm(g * mono(p, n, e))
        if best is None or grevlex_key(m) > grevlex_key(best):
            best, ind = m, [i]
        elif m == best:
            ind.append(i)
    return best, ind


def combine(p, n, G):
    F = Poly(p, n)
    for i, g in enumerate(G):
        F = F + g * fieldeq(p, n, i)
    return F


def nagao_step(p, n, G):
    """one application of the construction in the proof of Lemma 2."""
    psi, ind = psi_and_ind(p, n, G)
    I1, rest = ind[0], ind[1:]
    e1p = [0] * n
    e1p[I1] = p
    e1pm1 = [0] * n
    e1pm1[I1] = p - 1
    new = list(G)
    acc = Poly(p, n)
    for i in rest:
        L = lt(G[i])
        q = L.divides_by_mono(tuple(e1p))      # LT(G_Ii) / X_I1^p
        assert q is not None, "X_I1^p does not divide LT(G_Ii) -- claim 1) fails"
        acc = acc + q * fieldeq(p, n, i)
        qq = L.divides_by_mono(tuple(e1pm1))   # LT(G_Ii) / X_I1^{p-1}
        new[i] = G[i] - L + qq
    new[I1] = G[I1] + acc
    return new


def check2():
    banner("CHECK 2  inductive step of Nagao 2013/549 Lemma 2 "
           "(= Lemma 3 of 2015/984)")

    # -- 2a: identity (3) of the proof, for p = 2 and p = 3 --------------
    print("2a. identity (3):  (B^p-B)G == (B^p-B)(G - LT(G) + LT(G)/A^{p-1})")
    print("                              + (LT(G)/A^p)(A^p-A)(B^p-B)")
    for p in (2, 3):
        n = 2
        A, B = 0, 1
        eA = [0] * n
        eA[A] = p
        # a G whose leading term is divisible by A^p, as claim 1) guarantees
        G = mono(p, n, (p, 1)) + mono(p, n, (0, 1)) + const(p, n, 1)
        L = lt(G)
        assert L.divides_by_mono(tuple(eA)) is not None
        eAm = [0] * n
        eAm[A] = p - 1
        lhs = fieldeq(p, n, B) * G
        rhs = (fieldeq(p, n, B) * (G - L + L.divides_by_mono(tuple(eAm)))
               + L.divides_by_mono(tuple(eA)) * fieldeq(p, n, A) * fieldeq(p, n, B))
        print("   p=%d  G = %-22s  LT(G) = %-10s  identity holds ? %s"
              % (p, G, L, lhs == rhs))
        assert lhs == rhs

    # -- 2b: run the whole induction on concrete tuples -------------------
    print()
    print("2b. full descent, checking at every step: G^new gives the same F,")
    print("    psi strictly decreases, and the terminal tuple meets the bound")
    print("    deg G'_i <= deg F - p.")
    cases = []
    p, n = 2, 2
    cases.append((p, n, [mono(p, n, (0, 2)), mono(p, n, (2, 0))]))
    cases.append((p, n, [mono(p, n, (0, 2)) + mono(p, n, (1, 0)),
                         mono(p, n, (2, 0)) + mono(p, n, (0, 1))]))
    p, n = 3, 2
    cases.append((p, n, [mono(p, n, (0, 3)), mono(p, n, (3, 0))]))
    p, n = 2, 3
    cases.append((p, n, [mono(p, n, (0, 2, 2)), mono(p, n, (2, 0, 2)),
                         mono(p, n, (2, 2, 0))]))
    for p, n, G0 in cases:
        F = combine(p, n, G0)
        D = F.deg()
        G = list(G0)
        steps = 0
        trail = []
        while True:
            psi, ind = psi_and_ind(p, n, G)
            trail.append((psi, len(ind)))
            if psi is None:
                why = "all multipliers zero"
                break
            if len(ind) == 1:
                why = "NUM(G) = 1        [the paper's first branch]"
                break
            if sum(psi) <= D:
                why = ("NUM(G) = %d and deg psi(G) = %d = D   "
                       "[THE CASE THE PAPER'S WRITE-UP OMITS]" % (len(ind), sum(psi)))
                break
            Gn = nagao_step(p, n, G)
            assert combine(p, n, Gn) == F, "G^new left the solution set"
            psin, _ = psi_and_ind(p, n, Gn)
            assert psin is None or grevlex_key(psin) < grevlex_key(psi), \
                "psi did not strictly decrease"
            G, steps = Gn, steps + 1
            assert steps < 50
        bound = D - p
        ok = all(g.deg() <= bound for g in G)
        print("   p=%d N=%d  F = %-28s deg F = %d  steps = %d" % (p, n, F, D, steps))
        print("            start  %s" % [str(g) for g in G0])
        print("            end    %s   max deg = %d   bound deg F - p = %d   OK ? %s"
              % ([str(g) for g in G], max(g.deg() for g in G), bound, ok))
        print("            terminated because %s" % why)
        assert ok and combine(p, n, G) == F

    print()
    print("2d. claim 1) of the proof is printed as  X_{I_1}^p | G_{I_i}  (the whole")
    print("    multiplier).  What the argument establishes, and all identity (3)")
    print("    needs, is  X_{I_1}^p | LT(G_{I_i}).  Witness that the printed form")
    print("    is strictly stronger and FALSE:")
    p, n = 2, 2
    G = [mono(p, n, (1, 0)) + mono(p, n, (0, 2)), mono(p, n, (0, 1)) + mono(p, n, (2, 0))]
    psi, ind = psi_and_ind(p, n, G)
    e1p = [0] * n
    e1p[ind[0]] = p
    whole = G[ind[1]].divides_by_mono(tuple(e1p))
    head = lt(G[ind[1]]).divides_by_mono(tuple(e1p))
    print("    p=2 N=2, G = (%s, %s);  psi = %s, IND = %s"
          % (G[0], G[1], psi, ind))
    print("    X_{I_1}^p = X^2 divides the whole G_{I_2} = %s ? %s"
          % (G[ind[1]], whole is not None))
    print("    X_{I_1}^p = X^2 divides LT(G_{I_2}) = %s ? %s"
          % (lt(G[ind[1]]), head is not None))
    print("    -> printed claim 1) fails on this tuple; the LT form holds, and")
    print("       the step goes through on the LT form (2b ran this tuple).")
    assert whole is None and head is not None

    print()
    print("2c. where the GRADED order is load-bearing (errata-extraction-20260921):")
    print("    the NUM(G)=1 branch concludes D = deg F = deg psi(G).  That step")
    print("    needs deg psi(G) >= deg G_i + p for every i, which is what a")
    print("    graded order gives and a merely lexicographic one does not.")
    p, n = 2, 2
    G = [mono(p, n, (0, 5)), Poly(p, n)]
    F = combine(p, n, G)
    psi, ind = psi_and_ind(p, n, G)
    print("    witness p=2 N=2, G=(Y^5, 0): psi = %s, total degree %d, deg F = %d,"
          % (psi, sum(psi), F.deg()))
    print("    NUM = %d, so deg G_1 = %d <= deg F - p = %d ? %s"
          % (len(ind), G[0].deg(), F.deg() - p, G[0].deg() <= F.deg() - p))


# ==========================================================================
# CHECK 3 -- counterexample to Lemma 4 of 2015/984 as printed
# ==========================================================================

def enumerate_witnesses(p, n, members, d):
    """every multiplier tuple with deg(g_s * s) <= d, as a generator."""
    pools = []
    for s in members:
        ds = s.deg()
        pools.append(polys_up_to_degree(p, n, NEG if ds < 0 else d - ds))
    return product(*pools)


def ffd_eq(p, n, members, dmax, condition4):
    """true first fall degree, EQUALITY reading. Exhaustive for d <= dmax."""
    for d in range(0, dmax + 1):
        if condition4 and any(s.deg() > d for s in members):
            continue
        for G in enumerate_witnesses(p, n, members, d):
            prods = [g * s for g, s in zip(G, members)]
            mx = max((q.deg() for q in prods), default=NEG)
            if mx != d:
                continue
            tot = Poly(p, n)
            for q in prods:
                tot = tot + q
            if not tot.is_zero() and tot.deg() < d:
                return d, [str(g) for g in G], str(tot)
    return None, None, None


def ffd_ge(p, n, members, bound):
    """true first fall degree, '>=' reading, over multipliers of degree
    <= bound - deg(s).  An UPPER bound only; the matching lower bound is
    supplied by the ideal-membership certificates below."""
    best = None
    for G in enumerate_witnesses(p, n, members, bound):
        prods = [g * s for g, s in zip(G, members)]
        mx = max((q.deg() for q in prods), default=NEG)
        tot = Poly(p, n)
        for q in prods:
            tot = tot + q
        if tot.is_zero():
            continue
        d = tot.deg() + 1
        if mx >= d and (best is None or d < best[0]):
            best = (d, [str(g) for g in G], str(tot))
    return best


def fake_ffd(p, n, fs, dmax, reading):
    """fake first fall degree of {f_1..f_M} (union S_fe), Definition 6.

    Multipliers may be taken reduced mod S_fe without loss: every condition
    of Definition 6 is stated modulo S_fe, so replacing g_i by its normal
    form changes none of them.  The search over reduced multipliers is
    therefore EXHAUSTIVE, not truncated."""
    red = [g for g in polys_up_to_degree(p, n, n * (p - 1)) if g.reduce_fe() == g]
    best = None
    for G in product(red, repeat=len(fs)):
        prods = [(g * f).reduce_fe() for g, f in zip(G, fs)]
        mx = max((q.deg() for q in prods), default=NEG)
        tot = Poly(p, n)
        for q in prods:
            tot = tot + q
        if tot.is_zero():
            continue
        if reading == "EQ":
            d = mx
            if not (tot.deg() < d):
                continue
        else:
            d = tot.deg() + 1
            if not (mx >= d):
                continue
        if best is None or d < best[0]:
            best = (d, [str(g) for g in G], str(tot))
    return best


def check3():
    banner("CHECK 3  counterexample to Lemma 4 of Nagao 2015/984 AS PRINTED")
    p, n = 2, 2
    X = mono(p, n, (1, 0))
    Y = mono(p, n, (0, 1))
    f1 = mono(p, n, (2, 1))            # X^2 Y
    f2 = mono(p, n, (1, 1)) + X        # XY + X
    feX, feY = fieldeq(p, n, 0), fieldeq(p, n, 1)
    print("p = 2,  F_2[X,Y],  S_fe = {X^2+X, Y^2+Y}")
    print("f_1 = %s   (deg %d, NOT reduced mod S_fe)" % (f1, f1.deg()))
    print("f_2 = %s   (deg %d, reduced)" % (f2, f2.deg()))
    print("Lemma 4 as printed: d_F of {f_1,f_2}  <=  d'_F of {f_1,f_2} u S_fe.")
    print()

    for reading in ("EQ", "GE"):
        fk = fake_ffd(p, n, [f1, f2], 4, reading)
        print("fake d'_F  [%s reading] = %d   witness g = %s   sum mod S_fe = %s"
              % (reading, fk[0], fk[1], fk[2]))
    print("   (exhaustive over all %d reduced multiplier pairs)"
          % (16 * 16))
    print()
    print("does putting S_fe INSIDE the FAKE system change d'_F?  Definition 6")
    print("gives multipliers only to f_1..f_M; the question is what happens if")
    print("the field equations are given their own multipliers h_j too.")
    for j, fe in ((0, feX), (1, feY)):
        for h in (const(p, n, 1), Y, mono(p, n, (1, 1)), Y * Y * Y):
            assert (h * fe).reduce_fe().is_zero()
    print("   every product h_j * (X_j^p - X_j) reduces to 0 mod S_fe, so such a")
    print("   member contributes deg = -inf to condition (1) and 0 to conditions")
    print("   (2) and (3).  ALL THREE CONDITIONS ARE UNCHANGED.")
    for reading in ("EQ", "GE"):
        a = fake_ffd(p, n, [f1, f2], 4, reading)[0]
        b = fake_ffd(p, n, [f1, f2, feX, feY], 4, reading)[0]
        print("   [%s reading]  d'_F({f_1,f_2}) = %d ,  d'_F({f_1,f_2} u S_fe) = %d"
              "   same ? %s" % (reading, a, b, a == b))
        assert a == b
    print("   => 'field equations inside vs outside the FAKE system' is a")
    print("      DISTINCTION WITHOUT A DIFFERENCE under Definition 6.  The")
    print("      placement that does change the statement is on the TRUE side.")
    print()

    for c4 in (False, True):
        tag = "with condition 4" if c4 else "no condition 4"
        d_out, w_out, s_out = ffd_eq(p, n, [f1, f2], 4, c4)
        d_in, w_in, s_in = ffd_eq(p, n, [f1, f2, feX, feY], 4, c4)
        print("true d_F   [EQ reading, %s]" % tag)
        print("   S_fe OUTSIDE the true system: d_F = %s   witness %s -> %s"
              % (d_out, w_out, s_out))
        print("   S_fe INSIDE  the true system: d_F = %s   witness %s -> %s"
              % (d_in, w_in, s_in))
    print("   (exhaustive at every d = 0..4 over every multiplier with")
    print("    deg(g_s * s) <= d, so the minima above are certified, not sampled)")
    print()

    out_ge = ffd_ge(p, n, [f1, f2], 3)
    in_ge = ffd_ge(p, n, [f1, f2, feX, feY], 3)
    print("true d_F   [GE reading, multipliers bounded by deg(g s) <= 3]")
    print("   S_fe OUTSIDE: d_F <= %d   witness %s -> %s" % out_ge)
    print("   S_fe INSIDE : d_F <= %d   witness %s -> %s" % in_ge)

    # certificates for the GE lower bounds
    print()
    print("   lower-bound certificates (a bounded search cannot supply these):")
    phi = lambda f: f.subst_const(0, 0)        # X := 0
    psi_ = lambda f: f.subst_const(1, 1)       # Y := 1
    print("   phi: X:=0 sends f_1,f_2 -> %s, %s   (and X^2+X -> %s, Y^2+Y -> %s)"
          % (phi(f1), phi(f2), phi(feX), phi(feY)))
    print("   psi: Y:=1 sends f_1,f_2 -> %s, %s" % (psi_(f1), psi_(f2)))
    assert phi(f1).is_zero() and phi(f2).is_zero() and phi(feX).is_zero()
    # OUTSIDE: any h in <f_1,f_2> has h(0,Y)=0 and h(X,1) in <X^2>
    bad = []
    for h in polys_up_to_degree(p, n, 1):
        if h.is_zero():
            continue
        h0 = phi(h)
        h1 = psi_(h)
        in_X2 = all(sum(m) >= 2 for m in h1.c)
        if h0.is_zero() and in_X2:
            bad.append(str(h))
    print("   OUTSIDE: nonzero h of deg <= 1 surviving both necessary")
    print("            conditions for h in <f_1,f_2>: %s" % (bad or "NONE"))
    print("            => min degree of a nonzero element is >= 2,")
    print("               so d_F(outside)[GE] >= 3.  Matches the witness: = 3.")
    assert not bad
    # INSIDE: phi image lies in <Y^2+Y>, which contains no nonzero constant
    one = const(p, n, 1)
    print("   INSIDE : phi(I) <= <Y^2+Y> in F_2[Y]; every element of <Y^2+Y>")
    print("            vanishes at Y=0, and phi(1)=1 does not, so 1 is not in I")
    print("            => no degree-0 fall, d_F(inside)[GE] >= 2.  Witness: = 2.")
    assert phi(one).subst_const(1, 0) == one  # 1 survives X:=0 and Y:=0

    print()
    print("SUMMARY of CHECK 3")
    print("   d'_F = 2 under both readings.")
    print("   S_fe OUTSIDE the true system: d_F = 3 > 2 under BOTH readings")
    print("        -> Lemma 4 as printed is FALSE.")
    print("   S_fe INSIDE  the true system: d_F = 3 > 2 under the EQ reading")
    print("        (with or without condition 4) -> the inside form is FALSE too")
    print("        for this f_1, which is not reduced mod S_fe;")
    print("        d_F = 2 = d'_F under the GE reading -> holds there, and")
    print("        holds there WITHOUT Lemma 3 (see CHECK 4).")


# ==========================================================================
# CHECK 4 -- J-5 proves-too-much control
# ==========================================================================

def check4():
    banner("CHECK 4  J-5 control: run the J-3 derivation on the object where "
           "Lemma 4's conclusion is known false")
    p, n = 2, 2
    X = mono(p, n, (1, 0))
    f1 = mono(p, n, (2, 1))
    f2 = mono(p, n, (1, 1)) + X
    feX, feY = fieldeq(p, n, 0), fieldeq(p, n, 1)
    Y = mono(p, n, (0, 1))

    print("the derivation, step by step, on the fake witness g = (1,1):")
    P = f1 + f2
    Pbar = P.reduce_fe()
    R = P - Pbar
    print("   P    = g_1 f_1 + g_2 f_2               = %s   deg %d" % (P, P.deg()))
    print("   Pbar = P mod S_fe                      = %s   deg %d"
          % (Pbar, Pbar.deg()))
    print("   R    = P - Pbar  (lies in <S_fe>)      = %s   deg %d" % (R, R.deg()))
    print("   max_i deg(g_i f_i) UNREDUCED           = %d"
          % max(f1.deg(), f2.deg()))
    print("   max_i deg(g_i f_i mod S_fe)            = %d"
          % max(f1.reduce_fe().deg(), f2.reduce_fe().deg()))
    Gp = [Y, Poly(p, n)]
    print("   Lemma 2 applied to R gives G' with deg G'_j <= deg R - p = %d:"
          % (R.deg() - p))
    print("       G'_X = %s (deg %d), G'_Y = %s   and sum G'_j (X_j^p - X_j) = %s"
          % (Gp[0], Gp[0].deg(), Gp[1], Gp[0] * feX + Gp[1] * feY))
    assert Gp[0] * feX + Gp[1] * feY == R and Gp[0].deg() <= R.deg() - p

    print()
    print("   WITH S_fe INSIDE the true system the constructed combination is")
    print("   admissible:  1*f_1 + 1*f_2 + Y*(X^2+X) = %s" % (f1 + f2 + Y * feX))
    inside_sum = f1 + f2 + Y * feX
    inside_max = max(f1.deg(), f2.deg(), (Y * feX).deg())
    print("   products of degrees %s, max %d, sum of degree %d  -> a fall at %d,"
          % ([f1.deg(), f2.deg(), (Y * feX).deg()], inside_max,
             inside_sum.deg(), inside_max))
    print("   i.e. the derivation yields  d_F(inside) <= max_i deg(g_i f_i) = %d,"
          % inside_max)
    print("   NOT  d_F(inside) <= d'_F = 2.  The derivation is LOSSY by exactly")
    print("   the gap between reduced and unreduced product degree.")
    assert inside_sum == Pbar and inside_sum.deg() < inside_max

    print()
    print("   WITH S_fe OUTSIDE the true system the term Y*(X^2+X) is not a")
    print("   member of the system, so the only admissible combination from the")
    print("   same witness is P itself:")
    print("       products of degrees %s, max %d, sum = %s of degree %d"
          % ([f1.deg(), f2.deg()], max(f1.deg(), f2.deg()), P, P.deg()))
    print("   no drop (%d < %d is %s) -> THE DERIVATION DOES NOT GO THROUGH."
          % (P.deg(), max(f1.deg(), f2.deg()),
             P.deg() < max(f1.deg(), f2.deg())))
    assert not (P.deg() < max(f1.deg(), f2.deg()))
    print()
    print("   CONTROL OUTCOME: PASS.  The derivation fails on the object where")
    print("   the conclusion is false, and it fails at the one step that uses")
    print("   the field equations as members -- the same step whose absence")
    print("   makes the outside form false.  It does not prove too much.")

    print()
    print("   second half of the control: under the GE reading the inside form")
    print("   holds WITHOUT Lemma 3 at all.  Any representation of R will do,")
    print("   because GE's condition (1) only needs SOME product of degree >= d")
    print("   and a large product helps rather than hurts.  Witness with a")
    print("   deliberately BAD (high-degree) field-equation multiplier:")
    bad = Y * Y * Y * Y  # Y^4, far above Lemma 2's bound
    alt = f1 + f2 + Y * feX + bad * feY + bad * feY  # + 0, keeps the sum
    print("       1*f_1 + 1*f_2 + Y*(X^2+X) + Y^4*(Y^2+Y) + Y^4*(Y^2+Y) = %s" % alt)
    print("       products up to degree %d, sum still %s of degree %d,"
          % (max(f1.deg(), f2.deg(), (Y * feX).deg(), (bad * feY).deg()),
             alt, alt.deg()))
    print("       so GE still reports a fall at %d.  A statement Lemma 3 is"
          % (alt.deg() + 1))
    print("       not needed for is not a statement Lemma 3 supports.")
    assert alt == Pbar


def main():
    print("RECHECK for TASK-20260916-9da6e0 -- hand-check, NOT a measurement.")
    print("Exact arithmetic in F_p[X_1..X_N]; no sampling, no timing, no runs.")
    check1()
    check2()
    check3()
    check4()
    banner("ALL ASSERTIONS PASSED")


if __name__ == "__main__":
    main()
