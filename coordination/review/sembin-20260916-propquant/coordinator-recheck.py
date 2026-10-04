"""Coordinator's independent recheck of the three hand-algebra claims in report.md.

Written and run by the top-level Coordinator on 2026-09-16, AFTER reading the blind
reader's report, to avoid propagating a claim it had not checked. This is not an
independent re-derivation in the review-architecture sense -- the claims and their
witnesses were read from the report -- but the arithmetic is redone from scratch and
the degree-2 search in claim 2 is EXHAUSTIVE rather than a witness check.

F_2 coefficients; exponents PRESERVED, because the whole point of Nagao's true-vs-fake
distinction is that degrees are taken in the polynomial ring before reduction modulo
the field equations. sympy is unavailable in this environment, so the arithmetic is
implemented directly: a polynomial is a set of monomials (present = coefficient 1,
symmetric difference = addition over F_2) and a monomial is a 5-tuple of exponents.
"""
N = 5

def mono_mul(a, b):
    return tuple(x + y for x, y in zip(a, b))

def mul(p, q):
    out = set()
    for a in p:
        for b in q:
            out ^= {mono_mul(a, b)}
    return out

def add(*ps):
    out = set()
    for p in ps:
        out ^= p
    return out

def deg(p):
    return max((sum(m) for m in p), default=-1)

def red2(p):
    """Reduce modulo the field equations Xi^2 - Xi: clamp every exponent to <= 1."""
    out = set()
    for m in p:
        out ^= {tuple(min(e, 1) for e in m)}
    return out

def V(i, e=1):
    m = [0] * N
    m[i] = e
    return {tuple(m)}

ONE = {tuple([0] * N)}
X1, X2, X3, X4, X5 = [V(i) for i in range(N)]

def sq(i):
    return V(i, 2)

def show(p):
    if not p:
        return "0"
    names = ["X1", "X2", "X3", "X4", "X5"]
    terms = []
    for m in sorted(p, key=lambda m: (-sum(m), m)):
        if sum(m) == 0:
            terms.append("1")
            continue
        terms.append("".join(names[i] + ("^%d" % e if e > 1 else "")
                             for i, e in enumerate(m) if e))
    return " + ".join(terms)

print("=== claim 2: Lemma 4's LITERAL form, field equations OUTSIDE the system ===")
f1 = add(mul(X1, X2), X3)
f2 = add(X1, X2)
fake = red2(add(f1, mul(X2, f2)))
print("  fake: f1 + X2*f2 mod S_fe =", show(fake), "| deg", deg(fake))
print("  reduced product degrees:", deg(red2(f1)), deg(red2(mul(X2, f2))), "=> d'_F = 2")

falls = []
for c in (0, 1):
    for a in (0, 1):
        for b1 in (0, 1):
            for b2 in (0, 1):
                for b3 in (0, 1):
                    if not any((c, a, b1, b2, b3)):
                        continue
                    t1 = f1 if c else set()
                    parts = ([ONE] if a else []) + ([X1] if b1 else []) \
                            + ([X2] if b2 else []) + ([X3] if b3 else [])
                    mult = add(*parts) if parts else set()
                    t2 = mul(mult, f2) if mult else set()
                    comb = add(t1, t2)
                    if not comb:
                        continue
                    if max(deg(t1), deg(t2)) == 2 and deg(comb) < 2:
                        falls.append((c, a, b1, b2, b3, show(comb)))
print("  EXHAUSTIVE degree-2 true falls, field eqs OUTSIDE:", falls or "NONE")

witness = add(mul(add(X1, X2), f1), mul(mul(X1, X2), f2))
print("  degree-3 true fall (X1+X2)f1 + X1X2*f2 =", show(witness), "| deg", deg(witness),
      "from products of deg", deg(mul(add(X1, X2), f1)))
print("  => d_F = 3 > 2 = d'_F: LEMMA 4 AS LITERALLY WRITTEN IS FALSE")

inside = add(f1, mul(X2, f2), add(sq(1), X2))
print("  field eqs INSIDE: f1 + X2*f2 + (X2^2+X2) =", show(inside), "| deg", deg(inside),
      "from deg-2 products => true fall at 2, inequality HOLDS")

print()
print("=== claim 1: a TRUE fall the FAKE quantity cannot see ===")
f = add(mul(mul(X1, X2), X3), mul(mul(X1, X4), X5), X2)
g_f = mul(X1, f)
h = mul(add(mul(X2, X3), mul(X4, X5)), add(sq(0), X1))
s = add(g_f, h)
print("  X1*f + (X2X3+X4X5)(X1^2+X1) =", show(s), "| deg", deg(s),
      "from products of deg", deg(g_f), deg(h))
print("  same multipliers, Boolean ring: X1*f mod S_fe =", show(red2(g_f)),
      "| deg", deg(red2(g_f)), "(no drop => NOT a fake fall)")

print()
print("=== claim 3: the trivial Koszul ceiling at p = 2 ===")
fi = mul(mul(X1, X2), X3)
fe = add(sq(3), X4)
k = add(mul(fe, fi), mul(add(fi, ONE), fe))
print("  (X4^2+X4)f + (f+1)(X4^2+X4) =", show(k), "| deg", deg(k),
      "from products of deg", deg(mul(fe, fi)))
print("  => literal true d_F of ANY cubic system union S_fe at p=2 is <= 5;")
print("     Proposition 5's bound of 4 sits ONE degree below a trivial ceiling.")
