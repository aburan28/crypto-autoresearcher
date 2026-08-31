"""RED TEAM items 1b + 2: what actually governs complete splitting of the m=4
Semaev fibre, and a GENUINELY partial locus that avoids the alleged symmetry
loophole.

Independent re-derivation (not reusing the Executor's code):
  roots of S_4(u1,u2,u3,X) are x(e1 P1 + e2 P2 + e3 P3), e in {+-1}^3 mod global
  sign, where P_i is ANY point with x(P_i)=u_i -- over F_p if f(u_i) is a square,
  else over F_{p^2} with phi(P_i) = -P_i.
  => Frobenius acts on sign-vectors by flipping the signs at the "bad" (non-
  residue) coordinates.  A root is F_p-rational iff that flip is the identity
  (bad set empty) or the global negation (bad set = ALL coordinates).
PREDICTION: complete splitting iff j=0 or j=k (k = #fixed coords), NOT merely
"on the factor-base locus".
"""
import random, sys
import sympy
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher")
from harness.semaev import s4_expr, x1, x2, x3
from harness.toycurve import EllipticCurve

x4 = sympy.symbols("x4")

def legendre(v, p):
    v %= p
    if v == 0: return 0
    return 1 if pow(v, (p-1)//2, p) == 1 else -1

def modpoly_shape(expr, var, p):
    """(true mod-p degree, distinct roots, factor-degree multiset, splits_with_mult)."""
    poly = sympy.Poly(sympy.expand(expr), var)
    co = [int(c) % p for c in poly.all_coeffs()]
    while len(co) > 1 and co[0] == 0:
        co = co[1:]
    deg = len(co) - 1
    if deg <= 0:
        return deg, [], [], (deg == 0)
    def ev(v):
        r = 0
        for c in co: r = (r*v + c) % p
        return r
    roots = [v for v in range(p) if ev(v) == 0]
    P = sympy.Poly(co, var, modulus=p)
    fl = P.factor_list()
    shape = sorted([f.degree() for f, m in fl[1] for _ in range(m)])
    return deg, roots, shape, (max(shape) == 1 if shape else False)

def run(p, a, b, trials=200, seed=777):
    E = EllipticCurve(p, a, b)
    rng = random.Random(str((p, seed)))
    oncurve = [xv for xv in range(p) if legendre((xv**3 + a*xv + b) % p, p) == 1]
    offcurve = [xv for xv in range(p) if legendre((xv**3 + a*xv + b) % p, p) == -1]
    S4 = s4_expr(a, b)
    configs = {
        "A_j0_stage5_as_specified (u1,u2 on-curve, T on-curve)": ("on","on","on"),
        "B_T_uniform (u1,u2 on-curve, T ~ U(F_p))":              ("on","on","uni"),
        "C_T_forced_nonresidue (GENUINELY partial)":             ("on","on","off"),
        "D_all_three_uniform":                                   ("uni","uni","uni"),
        "E_j3_ALL_THREE_off_curve":                              ("off","off","off"),
        "F_j1 (one off-curve)":                                  ("on","off","on"),
        "G_j2 (two off-curve)":                                  ("off","off","on"),
    }
    print(f"### p={p} a={a} b={b}  (#on-curve x = {len(oncurve)}, #off = {len(offcurve)})")
    for name, spec in configs.items():
        n_split_mult = 0; n_split_distinct = 0; n = 0
        shapes = {}
        for _ in range(trials):
            u = []
            for s in spec:
                if s == "on":   u.append(rng.choice(oncurve))
                elif s == "off": u.append(rng.choice(offcurve))
                else:           u.append(rng.randrange(p))
            expr = S4.subs({x1: u[0], x2: u[1], x4: u[2]})
            deg, roots, shape, splits_mult = modpoly_shape(expr, x3, p)
            n += 1
            if splits_mult: n_split_mult += 1
            if len(roots) == deg and deg > 0: n_split_distinct += 1
            shapes[tuple(shape)] = shapes.get(tuple(shape), 0) + 1
        top = sorted(shapes.items(), key=lambda kv: -kv[1])[:4]
        print(f"  {name:52s} split(mult)={n_split_mult/n:.3f}  "
              f"split(distinct)={n_split_distinct/n:.3f}  shapes={top}")

run(211, 37, 57, trials=200)
run(1009, 17, 19, trials=200)
