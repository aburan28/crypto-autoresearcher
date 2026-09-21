#!/usr/bin/env python3
"""TASK-20260905-cfce83 INPUT PREPARATION ONLY.

Reads the archived, unedited fetched/icarm_curve302.json (ICARM leaderboard
curve #302) and prepares a k = 0 certificate in the exact input format of the
committed verifiers experiments/EXP-ECRANK-e1e30e/source/verify_certificate.py
and regulator_check.py (base_curve {A,B} integers, short Weierstrass
y^2 = x^3 + A x + B; field {V_classes:[1], k:0}; twists [{d:1, points:[...]}]).

The published curve is in GENERAL Weierstrass form
    E : y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6,  (a1,a2,a3) = (1,1,1).
The committed verifiers accept only the short integer model, so an EXACT
birational change of variables over Q is applied (input preparation; the
committed verifier independently re-checks every transformed point against the
transformed curve):

    b2 = a1^2 + 4 a2 ; b4 = a1 a3 + 2 a4 ; b6 = a3^2 + 4 a6
    W  = (2y + a1 x + a3)/2                       (complete the square)
    x  = X - b2/12                                (kill the X^2 term)
    X  = Xs / 144 , W = Ws / 1728                 (scale, u = 1/12, rational)

giving  Ws^2 = Xs^3 + A' Xs + B'  with integers
    A' = 20736 a4 - 432
    B' = 3456 (1728 a6 - 720 a4 + 322)
and the point map
    (x, y) |-> (Xs, Ws) = (144 x + 60, 864 (2y + x + 1)).

Group structure, non-torsion and independence are preserved by an isomorphism
over Q, and the Neron-Tate height pairing is isomorphism-invariant, so the
verifier outputs on the transformed certificate concern exactly the published
points on the published curve.

This script FABRICATES NOTHING: every coordinate is read from the archived
JSON bytes; the transformation is exact rational arithmetic; every step is
checked exactly (Fraction / integer equality) and the checks are printed.
"""
import json
from fractions import Fraction as Fr

SRC = 'fetched/icarm_curve302.json'
OUT = 'certificate_k0_icarm302.json'

j = json.load(open(SRC))
a1, a2, a3, a4, a6 = (int(v) for v in j['ainvs'])
print('source: %s' % SRC)
print('ainvs (verbatim from fetched bytes): [%d, %d, %d, a4=%d, a6=%d]'
      % (a1, a2, a3, a4, a6))
pts_raw = j['points']
print('number of points in fetched bytes: %d' % len(pts_raw))

# ---- exact check: raw points on the published GENERAL model ----
bad = 0
for xs, ys in pts_raw:
    x, y = Fr(xs), Fr(ys)
    lhs = y*y + a1*x*y + a3*y
    rhs = x**3 + a2*x*x + a4*x + a6
    if lhs != rhs:
        bad += 1
        print('  ! raw point NOT on general model: (%s, %s)' % (xs, ys))
print('raw points exactly on general model: %d/%d (failures %d)'
      % (len(pts_raw) - bad, len(pts_raw), bad))

# ---- transformation to integer short model ----
b2 = a1*a1 + 4*a2
b4 = a1*a3 + 2*a4
b6 = a3*a3 + 4*a6
A_frac = Fr(b4, 2) - Fr(b2*b2, 48)
B_frac = Fr(b6, 4) - Fr(b2*b4, 24) + Fr(b2**3, 864)
print('short model before scaling: A = %s, B = %s' % (A_frac, B_frac))
u4, u6 = 12**4, 12**6          # u = 1/12
A = A_frac * u4
B = B_frac * u6
assert A.denominator == 1 and B.denominator == 1, 'scaling failed to clear denominators'
A, B = int(A), int(B)
print("A' = %d" % A)
print("B' = %d" % B)

pts_t = []
bad2 = 0
for xs, ys in pts_raw:
    x, y = Fr(xs), Fr(ys)
    Xs = 144*x + 60
    Ws = 864*(2*y + x + 1)
    if Ws*Ws != Xs**3 + A*Xs + B:
        bad2 += 1
        print('  ! transformed point NOT on short model: from (%s, %s)' % (xs, ys))
    pts_t.append([str(Xs.numerator) if Xs.denominator == 1
                  else '%d/%d' % (Xs.numerator, Xs.denominator),
                  str(Ws.numerator) if Ws.denominator == 1
                  else '%d/%d' % (Ws.numerator, Ws.denominator)])
print('transformed points exactly on short model: %d/%d (failures %d)'
      % (len(pts_t) - bad2, len(pts_t), bad2))

# ---- invariant cross-checks (isomorphism consistency) ----
c4_gen = b2*b2 - 24*b4
c6_gen = -b2**3 + 36*b2*b4 - 216*b6
print('c4 check (general*12^4 == -48*A\'): %s'
      % (c4_gen * u4 == -48 * A))
print('c6 check (general*12^6 == -864*B\'): %s'
      % (c6_gen * u6 == -864 * B))
b8 = (a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4)
disc_gen = -b2*b2*b8 - 8*b4**3 - 27*b6*b6 + 9*b2*b4*b6
disc_short = -16*(4*A**3 + 27*B*B)
print('discriminant scaling check (general*12^12 == short): %s'
      % (disc_gen * 12**12 == disc_short))
page_disc = int(j['discriminant'])
print('page discriminant == general-model discriminant: %s'
      % (page_disc == disc_gen))
print('page regulator (verbatim): %s' % j['regulator'])

cert = {'base_curve': {'A': A, 'B': B},
        'field': {'V_classes': [1], 'k': 0},
        'twists': [{'d': 1, 'points': pts_t}]}
json.dump(cert, open(OUT, 'w'), indent=1)
print('wrote %s : k=0, |V|=1, twist d=1, %d points' % (OUT, len(pts_t)))
print('STATUS: %s' % ('ALL CHECKS PASSED' if (bad == 0 and bad2 == 0)
                      else 'CHECK FAILURES PRESENT'))
