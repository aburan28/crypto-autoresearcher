"""RED TEAM: (a) double degree drop on the p=1009 curve (which HAS rational
2-torsion, x=110 -- the very point in RUN-2's own recorded non-split example);
(b) item 4: does the Stage-1 'reconstruction' have power to reject a WRONG
implementation, or is 193/193 a foregone conclusion of the test setup?"""
import sys, random, importlib.util
import sympy
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher")
from harness.semaev import s3_expr, s4_expr, x1, x2, x3
from harness.toycurve import EllipticCurve
spec = importlib.util.spec_from_file_location(
    "exe", "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-805a02/implementation/run_experiment.py")
exe = importlib.util.module_from_spec(spec); spec.loader.exec_module(exe)
x4 = sympy.symbols("x4")

# ---------- (a) double degree drop, p=1009 (2-torsion present) --------------
p, a, b = 1009, 17, 19
E = EllipticCurve(p, a, b); pts = exe.on_curve_points(E)
tors = [q for q in pts if q[1] == 0]
print("p=1009 rational 2-torsion points:", tors)
S4 = s4_expr(a, b)
# reproduce RUN-2's own recorded non-split cell exactly
P1, P2, R = (110, 0), (435, 32), (637, 9)
expr = S4.subs({x1: P1[0], x2: P2[0], x4: R[0]})
deg, roots = exe.poly_roots_bruteforce(expr, x3, p)
gl = exe.group_law_root_set(E, [P1, P2, R])
P = sympy.Poly([c % p for c in [int(c) for c in sympy.Poly(sympy.expand(expr), x3).all_coeffs()]], x3, modulus=p)
print("  RUN-2 recorded cell P1=(110,0) P2=(435,32) R=(637,9):")
print("   deg =", deg, " distinct roots =", roots, " group-law set =", sorted(gl),
      " SET MATCH =", set(roots) == gl)
print("   factorisation mod p:", [(str(f.as_expr()), m) for f, m in P.factor_list()[1]])
print("   -> splits completely WITH MULTIPLICITY; the 'non-split' reading is the")
print("      2-torsion degeneracy (-P1 = P1 collapses 4 sign classes to 2).")

# forced DOUBLE drop: P3 2-torsion and P1+P2 = P3
P3t = tors[0]
for Q in pts:
    Pa = E.add(P3t, E.negate(Q))
    if Pa is None or Pa == Q or Pa[1] == 0 or Q[1] == 0: continue
    e2 = S4.subs({x1: Pa[0], x2: Q[0], x3: P3t[0]})
    d2, r2 = exe.poly_roots_bruteforce(e2, x4, p)
    g2 = exe.group_law_root_set(E, [Pa, Q, P3t])
    print(f"  forced double drop P1={Pa} P2={Q} P3={P3t}: deg={d2} roots={r2} "
          f"grouplaw={sorted(g2)} setmatch={set(r2)==g2} split(distinct)={len(r2)==d2}")
    break

# ---------- (b) item 4: power of the Stage-1 reconstruction -----------------
print("\n=== ITEM 4: deliberately WRONG reconstructions, 193 triples, p=211 ====")
pf, af, bf = 211, 37, 57
Ef = EllipticCurve(pf, af, bf); ptsf = exe.on_curve_points(Ef)

def census(S4expr, curve, points, label, n=193, seed=20260830):
    rng = random.Random(str((seed, "stage1")))   # SAME seeding as the Executor's stage1
    nm = ns = 0
    for _ in range(n):
        A, B, C = rng.sample(points, 3)
        e = S4expr.subs({x1: A[0], x2: B[0], x3: C[0]})
        d, r = exe.poly_roots_bruteforce(e, x4, curve.p)
        if set(r) == exe.group_law_root_set(curve, [A, B, C]): nm += 1
        if len(r) == d: ns += 1
    print(f"  {label:56s} setmatch={nm}/{n}  split={ns}/{n}")
    return nm

census(s4_expr(af, bf), Ef, ptsf, "CONTROL: correct s4_expr, correct curve")
census(s4_expr(af + 1, bf), Ef, ptsf, "MUTANT 1: S_4 built for a=38 (wrong curve)")
census(s4_expr(af, bf + 1), Ef, ptsf, "MUTANT 2: S_4 built for b=58 (wrong curve)")

def s3_bad_sign(a, b):   # sign flip on the 4b(x1+x2) term
    return ((x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3
            + ((x1*x2-a)**2 + 4*b*(x1+x2)))
def s4_from(s3f, a, b):
    t = sympy.symbols("t_")
    L = s3f(a, b).subs(x3, t)
    Rr = s3f(a, b).subs({x1: x3, x2: x4, x3: t}, simultaneous=True)
    return sympy.resultant(L, Rr, t)
census(s4_from(s3_bad_sign, af, bf), Ef, ptsf, "MUTANT 3: sign error in S_3 constant term")

def s3_bad_a(a, b):      # (x1*x2 + a)^2 instead of (x1*x2 - a)^2
    return ((x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3
            + ((x1*x2+a)**2 - 4*b*(x1+x2)))
census(s4_from(s3_bad_a, af, bf), Ef, ptsf, "MUTANT 4: (x1x2+a)^2 instead of (x1x2-a)^2")

# product instead of resultant
t_ = sympy.symbols("t_")
prod = sympy.expand(s3_expr(af,bf).subs(x3,t_) * s3_expr(af,bf).subs({x1:x3,x2:x4,x3:t_},simultaneous=True)).subs(t_, 0)
census(prod, Ef, ptsf, "MUTANT 5: product-at-t=0 instead of resultant")

# wrong group law: negate-free prediction (drop the +- signs, use only + )
def census_badgrouplaw(n=193, seed=20260830):
    rng = random.Random(str((seed, "stage1"))); nm = 0
    S = s4_expr(af, bf)
    for _ in range(n):
        A, B, C = rng.sample(ptsf, 3)
        e = S.subs({x1: A[0], x2: B[0], x3: C[0]})
        d, r = exe.poly_roots_bruteforce(e, x4, pf)
        acc = Ef.add(Ef.add(A, B), C)
        if set(r) == ({acc[0]} if acc else set()): nm += 1
    print(f"  {'MUTANT 6: prediction = {x(P1+P2+P3)} only (no sign orbit)':56s} setmatch={nm}/{n}")
census_badgrouplaw()
