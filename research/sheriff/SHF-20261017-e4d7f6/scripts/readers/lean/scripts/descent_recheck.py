#!/usr/bin/env python3
"""Re-audit of THM_QUOTIENT_DESCENT1 (SHF-20261016-3caa6f, L1/L2). Written from the
statement in formal/CryptoResearch/Quotient/TranslationDescent.lean:31-32 and the
prose in research/THM_QUOTIENT_DESCENT1.md; shares no code with the producer.

Part A  statement truth: exhaustive over finite abelian groups Z/a x Z/b, all S,T.
Part B  proves-too-much: mutated statements must be FALSE somewhere (witness printed).
Part C  the proof's two `abel` steps as identities in the free abelian group on P,S,T
        (coefficient vectors); mutated keys must fail, so abel could not close them.
Part D  elliptic-curve check of the corrected Setting (.md:16-21) and the Lemma (.md:36-37)
        with S = 2R not 2-torsion: fibres of phi(P) = x(P+R) are {P, -(P+2R)}, and
        tau_T maps fibres to fibres  <=>  2T = O, for every T in E(F_p).
"""
import itertools
import sys

# ---------------- Part A / B ----------------
SHAPES = [(1, 1), (2, 1), (3, 1), (4, 1), (2, 2), (4, 2), (6, 1), (6, 4), (8, 2), (12, 1), (3, 5), (8, 8), (9, 3)]


def group(a, b):
    elts = [(i, j) for i in range(a) for j in range(b)]
    add = lambda x, y: ((x[0] + y[0]) % a, (x[1] + y[1]) % b)
    neg = lambda x: ((-x[0]) % a, (-x[1]) % b)
    smul = lambda n, x: ((n * x[0]) % a, (n * x[1]) % b)
    return elts, add, neg, smul, (0, 0)


def lean_stmt(elts, add, neg, smul, zero, S, T):
    lhs = all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in elts)
    rhs = smul(2, T) == zero
    return lhs == rhs


MUTANTS = {
    "rhs 3*T=0": lambda e, add, neg, sm, z, S, T: all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in e) == (sm(3, T) == z),
    "rhs 4*T=0": lambda e, add, neg, sm, z, S, T: all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in e) == (sm(4, T) == z),
    "rhs T=0": lambda e, add, neg, sm, z, S, T: all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in e) == (T == z),
    "lhs no outer neg (P+S)+T=(P+T+S)": lambda e, add, neg, sm, z, S, T: all(add(add(P, S), T) == add(add(P, T), S) for P in e) == (sm(2, T) == z),
    "rhs 2*S=0 (wrong variable)": lambda e, add, neg, sm, z, S, T: all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in e) == (sm(2, S) == z),
    "lhs iota_S vs iota_{S+T}": lambda e, add, neg, sm, z, S, T: all(add(neg(add(P, S)), T) == neg(add(add(P, T), add(S, T))) for P in e) == (sm(2, T) == z),
}

print("== Part A: Lean statement, exhaustive over Z/a x Z/b, all S, T ==")
fails = checked = 0
for a, b in SHAPES:
    e, add, neg, sm, z = group(a, b)
    for S in e:
        for T in e:
            checked += 1
            if not lean_stmt(e, add, neg, sm, z, S, T):
                fails += 1
print(f"(S,T) pairs checked: {checked}; counterexamples: {fails}")
# hS no longer present: show the theorem is exercised with S of every order, incl. non-2-torsion
e, add, neg, sm, z = group(12, 1)
nontors = [S for S in e if sm(2, S) != z]
print(f"Z/12: {len(nontors)} S with 2S != 0 all satisfy the statement for every T:",
      all(lean_stmt(e, add, neg, sm, z, S, T) for S in nontors for T in e))
# non-vacuity: both truth values of each side occur
lhs_vals = set()
for T in e:
    lhs_vals.add(all(add(neg(add(P, (1, 0))), T) == neg(add(add(P, T), (1, 0))) for P in e))
print("non-vacuity: both sides of the iff take both truth values on Z/12:", lhs_vals == {True, False})

print("\n== Part B: proves-too-much (each mutant must be false somewhere) ==")
for name, f in MUTANTS.items():
    wit = None
    for a, b in SHAPES:
        e, add, neg, sm, z = group(a, b)
        for S, T in itertools.product(e, e):
            if not f(e, add, neg, sm, z, S, T):
                wit = (f"Z/{a}xZ/{b}", S, T)
                break
        if wit:
            break
    print(f"mutant '{name}': {'FALSE, witness ' + str(wit) if wit else 'TRUE on all tested groups (control FAILED)'}")

print("\n== Part C: the proof's `abel` identities in the free abelian group on (P, S, T) ==")
V = lambda p, s, t: (p, s, t)
vadd = lambda x, y: tuple(i + j for i, j in zip(x, y))
vneg = lambda x: tuple(-i for i in x)
vsub = lambda x, y: vadd(x, vneg(y))
P, S, T, O = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1), V(0, 0, 0)
two_T = V(0, 0, 2)
# key (forward, L36): 2*T = (-(0+S)+T) - -(0+T+S)
k1 = two_T == vsub(vadd(vneg(vadd(O, S)), T), vneg(vadd(vadd(O, T), S)))
# key (backward, L41): -(P+S)+T = -(P+T+S) + 2*T
k2 = vadd(vneg(vadd(P, S)), T) == vadd(vneg(vadd(vadd(P, T), S)), two_T)
print("forward key holds:", k1, "| backward key holds:", k2)
three_T = V(0, 0, 3)
print("mutant forward key with 3*T holds:", three_T == vsub(vadd(vneg(vadd(O, S)), T), vneg(vadd(vadd(O, T), S))), "(expected False)")
print("mutant backward key with 3*T holds:", vadd(vneg(vadd(P, S)), T) == vadd(vneg(vadd(vadd(P, T), S)), three_T), "(expected False)")
# after rw [key, h 0] the forward goal is  a - a = 0 for a = -(0+T+S): sub_self closes it
print("forward goal after rewrites is x - x with x = -(0+T+S):", vsub(vneg(vadd(vadd(O, T), S)), vneg(vadd(vadd(O, T), S))) == O)

# ---------------- Part D ----------------
print("\n== Part D: elliptic curve, phi(P) = x(P+R), S = 2R not 2-torsion ==")


def ec_points(p, a, b):
    sq = {}
    for y in range(p):
        sq.setdefault(y * y % p, []).append(y)
    pts = [None]
    for x in range(p):
        for y in sq.get((x * x * x + a * x + b) % p, []):
            pts.append((x, y))
    return pts


def ec_add(p, a, P1, P2):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P1 == P2:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_neg(p, P1):
    return None if P1 is None else (P1[0], (-P1[1]) % p)


def ec_mul(p, a, n, P1):
    R = None
    for _ in range(n):
        R = ec_add(p, a, R, P1)
    return R


def order(p, a, P1):
    n, Q = 1, P1
    while Q is not None:
        Q = ec_add(p, a, Q, P1)
        n += 1
    return n


def xcoord(P1):
    return "inf" if P1 is None else P1[0]


def run_curve(p, a, b, rorder):
    pts = ec_points(p, a, b)
    N = len(pts)
    Rs = [Q for Q in pts if Q is not None and order(p, a, Q) == rorder]
    if not Rs:
        return None
    R = Rs[0]
    S2 = ec_mul(p, a, 2, R)  # S = 2R
    phi = lambda Q: xcoord(ec_add(p, a, Q, R))
    iota = lambda Q: ec_neg(p, ec_add(p, a, Q, S2))  # iota_S(P) = -(P+S)
    # fibres of phi are exactly {P, iota(P)}
    fib = {}
    for Q in pts:
        fib.setdefault(phi(Q), set()).add(Q)
    fibres_ok = all(fib[phi(Q)] == {Q, iota(Q)} for Q in pts)
    s_is_2tors = ec_mul(p, a, 2, S2) is None
    # descent of tau_T through phi  <=>  2T = O, for every T
    agree = 0
    desc_count = 0
    two_tors_count = 0
    for T in pts:
        desc = all(phi(ec_add(p, a, iota(Q), T)) == phi(ec_add(p, a, Q, T)) for Q in pts)
        two = ec_mul(p, a, 2, T) is None
        desc_count += desc
        two_tors_count += two
        agree += (desc == two)
    return dict(p=p, a=a, b=b, N=N, R=R, ordR=rorder, S=S2, S_is_2torsion=s_is_2tors,
                fibres_are_P_and_iota=fibres_ok, T_checked=N, lemma_agree=agree,
                descending_T=desc_count, two_torsion_T=two_tors_count)


found = 0
for p in (1009, 211):
    for a, b in itertools.product(range(1, 40), range(1, 40)):
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        pts = ec_points(p, a, b)
        N = len(pts)
        if N % 6 != 0:
            continue
        res = run_curve(p, a, b, 3)
        if res is None:
            continue
        print(res)
        found += 1
        if N % 5 == 0:
            res5 = run_curve(p, a, b, 5)
            if res5:
                print(res5)
        break
print("curves checked:", found)
sys.exit(0 if fails == 0 else 1)
