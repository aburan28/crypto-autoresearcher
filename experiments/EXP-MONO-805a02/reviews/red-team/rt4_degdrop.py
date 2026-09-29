"""RED TEAM item 5: adversarially force degree drop at m=4 and m=5 and test the
FIXED code (imported from the Executor's own module) on those cases.

Degree drop in the free variable happens exactly when one signed combination
+-P_1 +- ... +- P_{k} equals the point at infinity, i.e. the leading coefficient
of S_m in the free variable vanishes mod p.  So P3 = P1 + P2 forces it at m=4.
"""
import sys, importlib.util
import sympy
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher")
from harness.semaev import s3_expr, s4_expr, x1, x2, x3
from harness.toycurve import EllipticCurve

spec = importlib.util.spec_from_file_location(
    "exe", "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-805a02/implementation/run_experiment.py")
exe = importlib.util.module_from_spec(spec); spec.loader.exec_module(exe)

x4, U, T = sympy.symbols("x4 U T")
p, a, b = 211, 37, 57
E = EllipticCurve(p, a, b)
pts = exe.on_curve_points(E)

# ---------- leading coefficient of S_4 in x4, as a polynomial in x1,x2,x3 ----
S4 = s4_expr(a, b)
L = sympy.Poly(sympy.expand(S4), x4).all_coeffs()[0]
print("lc_{x4} S_4 is a polynomial in x1,x2,x3 of total degree",
      sympy.Poly(L, x1, x2, x3).total_degree())

def report(tag, deg, roots, expected):
    print(f"  {tag:52s} deg={deg} #roots={len(roots)} roots={roots} "
          f"| grouplaw={sorted(expected)} | setmatch={set(roots)==expected} "
          f"| split(distinct)={len(roots)==deg}")

print("\n=== CASE 1 (m=4, Stage-1 path): P3 = P1+P2  -> one combination at infinity")
P1, P2 = pts[3], pts[7]
P3 = E.add(P1, P2)
print("   lc_{x4}S_4(u1,u2,u3) mod p =", int(L.subs({x1:P1[0],x2:P2[0],x3:P3[0]})) % p)
expr = S4.subs({x1:P1[0], x2:P2[0], x3:P3[0]})
deg, roots = exe.poly_roots_bruteforce(expr, x4, p)
report("FIXED poly_roots_bruteforce", deg, roots, exe.group_law_root_set(E,[P1,P2,P3]))
# what the UNFIXED code would have said
polyZ = sympy.Poly(sympy.expand(expr), x4)
print("   over-Z degree (pre-fix reading) =", polyZ.degree(), "-> pre-fix would call this NON-SPLIT")

print("\n=== CASE 2 (m=4): P3 2-torsion AND P1+P2 = P3 -> DOUBLE degree drop")
tors = [q for q in pts if q[1] == 0]
done = False
if tors:
    P3t = tors[0]
    for Q in pts:
        Pa = E.add(P3t, E.negate(Q))          # Pa + Q = P3t
        if Pa is None or Pa == Q: continue
        expr = S4.subs({x1:Pa[0], x2:Q[0], x3:P3t[0]})
        deg, roots = exe.poly_roots_bruteforce(expr, x4, p)
        report(f"P1={Pa} P2={Q} P3={P3t}(2-torsion)", deg, roots,
               exe.group_law_root_set(E,[Pa,Q,P3t]))
        done = True; break
if not done: print("   (no rational 2-torsion on this curve; skipped)")

print("\n=== CASE 3 (m=5, Stage-2 path): P3 = P1+P2 -> lc_U(S_4) == 0 mod p")
print("    HAZARD: Res_Z(f,g) mod p = lc(g_bar)^(deg f - deg f_bar) * Res(f_bar,g_bar).")
print("    Here lc_U(g) = (x(P4) - T)^2, so a SPURIOUS root at T = x(P4) is injected.")
P4 = pts[11]
deg, roots = exe.build_s5_root_set_and_deg(E, a, b, P1, P2, P3, P4)
expected = exe.group_law_root_set(E, [P1, P2, P3, P4])
report("Executor build_s5_root_set_and_deg (Stage 2)", deg, roots, expected)
print("    x(P4) =", P4[0], " in measured roots?", P4[0] in roots,
      " in group-law set?", P4[0] in expected)

print("\n=== CASE 3b (m=5): control, generic P1..P4 (no degree drop)")
Pg = [pts[3], pts[7], pts[13], pts[17]]
deg, roots = exe.build_s5_root_set_and_deg(E, a, b, *Pg)
report("Executor build_s5 (generic control)", deg, roots, exe.group_law_root_set(E, Pg))

print("\n=== CASE 4 (Stage-5 m=5 inline path): same forced drop, T fixed on-curve")
Rt = pts[11]
S4n = s4_expr(a,b).subs({x1:P1[0], x2:P2[0], x3:P3[0]}).subs(x4, U)
S3p = s3_expr(a,b).subs({x1:x4, x2:T, x3:U}, simultaneous=True).subs(T, Rt[0])
S5 = sympy.resultant(sympy.expand(S4n), sympy.expand(S3p), U)
deg, roots = exe.poly_roots_bruteforce(S5, x4, p)
report("Stage5-m5 inline construction", deg, roots, exe.group_law_root_set(E,[P1,P2,P3,Rt]))
print("    NOTE: here lc_U(g)=(x4 - x(R))^2 is a polynomial in the FREE variable x4,")
print("    so the spurious factor lands at x4 = x(R) =", Rt[0])
