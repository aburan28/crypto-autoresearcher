"""
EXP-MONO-815525 Stage 0, part 1: DERIVE the m=3 and m=4 Semaev summation
polynomials from the elliptic-curve group law by resultant elimination, and
descend S_4 to the symmetric base.

Nothing here is copied from an external source: S_3 is obtained by eliminating
y1 then y2 from the addition-law relation against y_i^2 = f(x_i), and S_4 is
obtained by eliminating the intermediate point's x-coordinate U between two
copies of S_3.  Both eliminations are ordinary Sylvester resultants.

Outputs (consumed by run_census.py, which itself uses NO CAS):
  s4_monomials.json          ordered-base S_4 as a monomial table in
                             (x1,x2,x3,x4,A,B)
  s4_symmetric_coeffs.json   symmetric-base Q_e(T) = sum_k c_k(e1,e2,e3,A,B) T^k
  s3_monomials.json          S_3 as a monomial table in (x1,x2,x3,A,B)
  derivation_checks.json     pass/fail record of every symbolic check
"""
import json
import os
import sys

import sympy as sp
from sympy.polys.polyfuncs import symmetrize

HERE = os.path.dirname(os.path.abspath(__file__))

x1, x2, x3, x4, U, A, B, y1, y2 = sp.symbols("x1 x2 x3 x4 U A B y1 y2")
e1, e2, e3 = sp.symbols("e1 e2 e3")

checks = {}


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- S_3
# x(P1+P2) = x3 with P_i = (x_i, y_i) on y^2 = x^3 + A x + B is, after
# clearing the denominator of lambda = (y2-y1)/(x2-x1),
#     (y2 - y1)^2 = (x1 + x2 + x3) (x2 - x1)^2.
# Eliminate y1 against y1^2 - f(x1), then y2 against y2^2 - f(x2).
log("[S_3] eliminating y1, y2 from the addition-law relation ...")
rel = sp.expand((y2 - y1) ** 2 - (x1 + x2 + x3) * (x2 - x1) ** 2)
f1 = y1 ** 2 - (x1 ** 3 + A * x1 + B)
f2 = y2 ** 2 - (x2 ** 3 + A * x2 + B)
r1 = sp.expand(sp.resultant(sp.Poly(rel, y1), sp.Poly(f1, y1)))
r2 = sp.expand(sp.resultant(sp.Poly(r1, y2), sp.Poly(f2, y2)))
r2f = sp.factor(r2)
log("[S_3] factored elimination result: %s" % r2f)

S3 = sp.expand(
    A ** 2
    - 2 * A * (x1 * x2 + x1 * x3 + x2 * x3)
    - 4 * B * (x1 + x2 + x3)
    + x1 ** 2 * x2 ** 2
    - 2 * x1 ** 2 * x2 * x3
    + x1 ** 2 * x3 ** 2
    - 2 * x1 * x2 ** 2 * x3
    - 2 * x1 * x2 * x3 ** 2
    + x2 ** 2 * x3 ** 2
)
# the elimination result is exactly (x1-x2)^4 * S3^2 : the (x1-x2)^4 is the
# extraneous factor introduced by clearing lambda's denominator, and the
# square arises because the resultant in y_i sees both signs of each y_i.
checks["s3_elimination_matches_squared_form"] = bool(
    sp.expand(r2 - (x1 - x2) ** 4 * S3 ** 2) == 0
)
log("[S_3] check: elimination == (x1-x2)^4 * S_3^2 -> %s"
    % checks["s3_elimination_matches_squared_form"])
checks["s3_symmetric"] = all(
    sp.expand(S3.subs({x1: a, x2: b, x3: c}, simultaneous=True) - S3) == 0
    for a, b, c in sp.utilities.iterables.permutations([x1, x2, x3])
)
checks["s3_degree_in_each_var"] = [sp.Poly(S3, v).degree() for v in (x1, x2, x3)]
log("[S_3] symmetric=%s degrees=%s" % (checks["s3_symmetric"],
                                       checks["s3_degree_in_each_var"]))


# ---------------------------------------------------------------- S_4
# P1+P2+P3+P4 = O  <=>  there is a point R with P1+P2 = -R and P3+P4 = R,
# i.e. S_3(x1,x2,U) and S_3(x3,x4,U) share the root U = x(R).  Eliminating U
# is exactly a Sylvester resultant of two U-quadratics.
log("[S_4] eliminating the intermediate point's x-coordinate U ...")
S3a = S3.subs({x3: U}, simultaneous=True)
S3b = S3.subs({x1: x3, x2: x4, x3: U}, simultaneous=True)
S4 = sp.expand(sp.resultant(sp.Poly(S3a, U), sp.Poly(S3b, U)))

checks["s4_degree_in_each_var"] = [sp.Poly(S4, v).degree() for v in (x1, x2, x3, x4)]
log("[S_4] degrees in x1..x4: %s" % checks["s4_degree_in_each_var"])
checks["s4_degree_4_in_each_var"] = checks["s4_degree_in_each_var"] == [4, 4, 4, 4]

fac = sp.factor(S4)
checks["s4_irreducible_no_extraneous_factor"] = not fac.is_Mul
log("[S_4] elimination result carries no extraneous factor: %s"
    % checks["s4_irreducible_no_extraneous_factor"])

V = (x1, x2, x3, x4)
Z = sp.symbols("z0 z1 z2 z3")
sym_ok = True
for perm in sp.utilities.iterables.permutations(range(4)):
    Sp = S4.subs({V[i]: Z[i] for i in range(4)}, simultaneous=True)
    Sp = Sp.subs({Z[i]: V[perm[i]] for i in range(4)}, simultaneous=True)
    if sp.expand(Sp - S4) != 0:
        sym_ok = False
        log("[S_4] SYMMETRY FAILURE at permutation %s" % (perm,))
checks["s4_fully_symmetric_in_x1_x4"] = sym_ok
log("[S_4] fully symmetric under all 24 permutations of x1..x4: %s" % sym_ok)
checks["s4_n_terms"] = len(S4.args)


# --------------------------------------------- descend to the symmetric base
log("[Q_e] symmetrizing the T-coefficients in x1,x2,x3 ...")
P = sp.Poly(S4, x4)
cks = {}
for k in range(5):
    c = sp.expand(P.nth(k))
    sym, rem, _ = symmetrize(c, [x1, x2, x3], formal=True)
    if rem != 0:
        raise SystemExit("symmetrization left a remainder at k=%d" % k)
    cks[k] = sp.expand(sym.subs({sp.Symbol("s1"): e1,
                                 sp.Symbol("s2"): e2,
                                 sp.Symbol("s3"): e3}))
    log("[Q_e] c_%d = %s" % (k, sp.factor(cks[k])))
checks["s4_symmetric_descent_exact"] = True


def table(expr, gens):
    poly = sp.Poly(expr, *gens)
    return {",".join(str(i) for i in mon): int(co)
            for mon, co in zip(poly.monoms(), poly.coeffs())}


json.dump({"gens": ["x1", "x2", "x3", "x4", "A", "B"],
           "terms": table(S4, (x1, x2, x3, x4, A, B))},
          open(os.path.join(HERE, "s4_monomials.json"), "w"), indent=0)
json.dump({"gens": ["x1", "x2", "x3", "A", "B"],
           "terms": table(S3, (x1, x2, x3, A, B))},
          open(os.path.join(HERE, "s3_monomials.json"), "w"), indent=0)
json.dump({"gens": ["e1", "e2", "e3", "A", "B"],
           "coeffs": {str(k): table(cks[k], (e1, e2, e3, A, B)) for k in range(5)}},
          open(os.path.join(HERE, "s4_symmetric_coeffs.json"), "w"), indent=0)
json.dump(checks, open(os.path.join(HERE, "derivation_checks.json"), "w"), indent=2)

open(os.path.join(HERE, "S4_expanded.txt"), "w").write(str(S4))
for k, v in cks.items():
    open(os.path.join(HERE, "Qe_coeff_c%d.txt" % k), "w").write(str(v))

bad = [k for k, v in checks.items()
       if isinstance(v, bool) and not v]
log("\n[derive_s4] FAILED CHECKS: %s" % (bad if bad else "none"))
sys.exit(1 if bad else 0)
