"""
GOAL-MONO-001 direction-swap successor's cheapest falsification check (D-5,
DEC-20260810-2f86db), settled 2026-09-04 (DEC-20260904-8c2580).

Question: does OBS-1's identity disc_T S_3(x1,x2,T) = 16 f(x1) f(x2) transport,
under S_3's own full symmetry in its three variables, to
disc_{x2} S_3(x1,x2,T0) = 16 f(x1) f(T0)?

S_3 is derived here from scratch via the group law (elimination of y1, y2 via
resultants from the point-addition relation x(P1+P2) = x3), not copied from a
reference formula, so this check does not depend on any external source being
correct.
"""
import sympy as sp

x1, x2, x3, y1, y2, A, B, T, T0 = sp.symbols('x1 x2 x3 y1 y2 A B T T0')


def f(x):
    return x**3 + A * x + B


# x(P1+P2) = x3  <=>  ((y2-y1)/(x2-x1))**2 - x1 - x2 = x3, cleared of denominators.
rel = (y2 - y1)**2 - (x1 + x2 + x3) * (x2 - x1)**2

r1 = sp.expand(sp.resultant(rel, y1**2 - f(x1), y1))
S3_raw = sp.expand(sp.resultant(r1, y2**2 - f(x2), y2))

# The raw resultant carries an extraneous (x1-x2)^4 factor from the two
# eliminations; the genuine S_3 is the remaining degree-2-in-each-variable
# factor. Verified below to be exactly this by direct symmetry/degree checks.
S3 = (A**2 - 2 * A * (x1 * x2 + x1 * x3 + x2 * x3) - 4 * B * (x1 + x2 + x3)
      + x1**2 * x2**2 - 2 * x1**2 * x2 * x3 + x1**2 * x3**2
      - 2 * x1 * x2**2 * x3 - 2 * x1 * x2 * x3**2 + x2**2 * x3**2)

assert sp.expand(S3_raw - (x1 - x2)**4 * S3**2) == 0, "S3 does not match the raw resultant up to the extraneous factor"

for perm in [(x1, x3, x2), (x2, x1, x3), (x2, x3, x1), (x3, x1, x2), (x3, x2, x1)]:
    assert sp.expand(S3.subs({x1: perm[0], x2: perm[1], x3: perm[2]}, simultaneous=True) - S3) == 0
assert sp.degree(S3, x1) == 2 and sp.degree(S3, x2) == 2 and sp.degree(S3, x3) == 2

disc_T = sp.discriminant(sp.Poly(S3.subs(x3, T), T))
obs1_holds = sp.expand(disc_T - 16 * f(x1) * f(x2)) == 0

disc_x2 = sp.discriminant(sp.Poly(S3.subs(x3, T0), x2))
d5_transport_holds = sp.expand(disc_x2 - 16 * f(x1) * f(T0)) == 0

if __name__ == "__main__":
    print("S3 symmetric and degree-2 in each variable: confirmed")
    print("OBS-1 (disc_T S3(x1,x2,T) = 16 f(x1) f(x2)):", obs1_holds)
    print("D-5 transport (disc_x2 S3(x1,x2,T0) = 16 f(x1) f(T0)):", d5_transport_holds)
    assert obs1_holds and d5_transport_holds
