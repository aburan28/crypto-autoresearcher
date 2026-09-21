#!/usr/bin/env python3
"""Validator's own POSITIVE and NEGATIVE controls for J2."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validator_independent_check import Curve, x_coords_distinct, torsion_criterion_violations
from itertools import combinations, product

print("### CONTROL 0: arithmetic self-tests (group axioms + Hasse)")
for (p, A, B) in [(101, 2, 3), (211, 5, 7), (1009, 3, 8)]:
    E = Curve(p, A, B)
    pts = E.points(); N = len(pts)
    assert abs(N - (p + 1)) <= 2 * math.isqrt(p), "Hasse violated"
    rnd = random.Random(20260904)
    for _ in range(300):
        P, Q, R = rnd.choice(pts), rnd.choice(pts), rnd.choice(pts)
        assert E.on_curve(E.add(P, Q))
        assert E.add(P, Q) == E.add(Q, P)                       # commutative
        assert E.add(E.add(P, Q), R) == E.add(P, E.add(Q, R))   # associative
        assert E.add(P, E.neg(P)) is None                       # inverse
        assert E.add(P, None) == P                              # identity
        assert E.mul(N, P) is None                              # Lagrange
    print(f"  p={p} A={A} B={B}: #E={N}, Hasse ok, 300 random triples pass "
          f"commutativity/associativity/inverse/identity/Lagrange")

print()
print("### CONTROL 1 (NEGATIVE, m=4): P_1 = P_2  =>  collision MUST occur")
E = Curve(101, 2, 3)
P = (3, 6)
ok, xs, coll, inf = x_coords_distinct(E, [P, P, (9, 12)])
print(f"  pts=[P,P,(9,12)]  distinct={ok}  collisions={coll}")
assert ok is False, "negative control FAILED to fire"
print("  -> detector fires. (Note: this collision is x(P_3) at eps=+-+ vs +--;")
print("     my J1 criterion flags it via S={1,2}, signs (+,-): P_1-P_2 = O in E[2].)")
bad = torsion_criterion_violations(E, [P, P, (9, 12)])
print(f"  torsion-criterion violations: {[(S, s) for S, s, Q in bad]}")

print()
print("### CONTROL 2 (NEGATIVE, m=4): P_1 in E[2]  =>  collision MUST occur")
T = (100, 0)                    # the rational 2-torsion point on y^2=x^3+2x+3 /F_101
assert E.on_curve(T) and E.is_two_torsion(T)
ok, xs, coll, inf = x_coords_distinct(E, [T, (5, 21), (9, 12)])
print(f"  pts=[(100,0),(5,21),(9,12)]  distinct={ok}  collisions={coll}")
assert ok is False, "negative control FAILED to fire"
bad = torsion_criterion_violations(E, [T, (5, 21), (9, 12)])
print(f"  torsion-criterion violations: {[(S, s) for S, s, Q in bad]}")

print()
print("### CONTROL 3 (NEGATIVE, m=4): P_1+P_2 in E[2] by construction")
# pick P_1 arbitrary, set P_2 = T - P_1 so that P_1+P_2 = T in E[2]
P1 = (5, 21); P2 = E.add(T, E.neg(P1))
print(f"  P_1={P1}  P_2={P2}  P_1+P_2={E.add(P1,P2)} in E[2]={E.is_two_torsion(E.add(P1,P2))}")
ok, xs, coll, inf = x_coords_distinct(E, [P1, P2, (9, 12)])
print(f"  distinct={ok}  collisions={coll}")
assert ok is False, "negative control FAILED to fire"
print("  -> confirms the |S|=2 branch of the criterion is exactly what collides.")

print()
print("### CONTROL 4 (POSITIVE): agreement of the two routes over many random inputs")
for (p, A, B, n) in [(101, 2, 3, 3), (211, 5, 7, 3), (101, 2, 3, 4), (1009, 3, 8, 3), (1009, 3, 8, 4)]:
    E = Curve(p, A, B); pts_all = [q for q in E.points() if q is not None]
    rnd = random.Random(917)
    agree = clean = 0
    for _ in range(400):
        sel = [rnd.choice(pts_all) for _ in range(n)]
        ok, xs, coll, inf = x_coords_distinct(E, sel)
        bad = torsion_criterion_violations(E, sel)
        if ok == (not bad and not inf):
            agree += 1
        clean += ok
    print(f"  p={p} m-1={n}: routes agree on {agree}/400 random tuples; "
          f"{clean}/400 tuples clean ({100*clean/400:.1f}%)")
    assert agree == 400

print()
print("### CONTROL 5: does a clean witness exist at all for a curve where it should NOT?")
# E over F_5 with very few points: at m=5 we need 8 distinct x-coords but only
# <= p distinct x-values exist, so cleanliness is IMPOSSIBLE by pigeonhole for p<8.
E5 = Curve(5, 1, 1); pts5 = [q for q in E5.points() if q is not None]
found = False
for sel in product(pts5, repeat=4):
    ok, xs, coll, inf = x_coords_distinct(E5, list(sel))
    if ok:
        found = True; break
print(f"  p=5, m=5 (needs 8 distinct x in a set of size 5): clean witness found = {found}")
assert found is False
print("  -> cleanliness is a genuinely falsifiable property of the (curve,points) pair,")
print("     not a tautology of the checker.")
