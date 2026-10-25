"""R3 (fast form): Galois group of F = S_4(x1,x2,x3,T) over F_p(x1,x2,x3) by the resolvent cubic,
with POLYNOMIAL coefficients (no fraction-field arithmetic).

For a4 T^4 + a3 T^3 + a2 T^2 + a1 T + a0 with roots r_i, the cubic with roots
w_k = a4 (r_i r_j + r_k r_l) is
   W(w) = w^3 - a2 w^2 + (a1 a3 - 4 a0 a4) w - (a3^2 a0 - 4 a2 a0 a4 + a1^2 a4).
Gal(F) <= V_4 iff W splits into three linear factors over F_p(x) (equivalently over F_p[x], Gauss).
With F irreducible over F_p(x) (checked in check_ordered.py: S_4 irreducible), Gal = V_4 exactly.
Also: disc_T(F) is a square in F_p(x) iff Gal <= A_4 (consistency).
Run per curve, and with a, b symbolic at p in {7, 11, 13, 101, 10007} (every curve over those primes).
Usage: sage -python resolvent_fast.py OUTDIR
"""
import sys, json, time, os
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import S3_expr

OUT = sys.argv[1]
res = {}


def check(p, a, b):
    F = GF(p)
    if a is None:
        R = PolynomialRing(F, ['a', 'b', 'x1', 'x2', 'x3']); av, bv, x1, x2, x3 = R.gens()
    else:
        R = PolynomialRing(F, ['x1', 'x2', 'x3']); x1, x2, x3 = R.gens(); av, bv = F(a), F(b)
    PT = PolynomialRing(R, 'T'); T = PT.gen()
    PTX = PolynomialRing(PT, 'X'); X = PTX.gen()
    Fq = PT(PTX(S3_expr(av, bv, x1, x2, X)).resultant(PTX(S3_expr(av, bv, x3, T, X))))
    assert Fq.degree() == 4
    a4, a3, a2, a1, a0 = [Fq[i] for i in (4, 3, 2, 1, 0)]
    PW = PolynomialRing(R, 'w'); w = PW.gen()
    W = w ** 3 - a2 * w ** 2 + (a1 * a3 - 4 * a0 * a4) * w - (a3 ** 2 * a0 - 4 * a2 * a0 * a4 + a1 ** 2 * a4)
    # factor over R[w] via the multivariate ring
    RW = PolynomialRing(F, list(R.variable_names()) + ['w'])
    Wm = RW(sum(RW(c) * RW.gen(RW.ngens() - 1) ** i for i, c in enumerate(W.list())))
    fac = Wm.factor()
    wdeg = sorted(int(g.degree(RW.gen(RW.ngens() - 1))) for g, e in fac for _ in range(e) if g.degree(RW.gen(RW.ngens() - 1)) > 0)
    disc = Fq.discriminant()
    dfac = disc.factor()
    disc_square = all(e % 2 == 0 for g, e in dfac) and (dfac.unit().is_square() if hasattr(dfac.unit(), 'is_square') else True)
    return {'resolvent_w_degrees': wdeg, 'gal_in_V4': wdeg == [1, 1, 1], 'disc_square_in_Fp(x)': bool(disc_square),
            'resolvent_roots_are_polynomials': [str(g)[:80] for g, e in fac if g.degree(RW.gen(RW.ngens() - 1)) == 1]}


for spec in [(7, 1, 0), (7, 0, 1), (11, 0, 1), (11, 1, 0), (13, 2, 5), (13, 1, 4), (101, 2, 3), (101, 0, 1), (101, 1, 0), (1009, 5, 7), (1013, 0, 1), (10007, 1, 0), (10007, 2, 3),
             (7, None, None), (11, None, None), (13, None, None), (101, None, None), (10007, None, None)]:
    t0 = time.time()
    try:
        alarm(300)
        r = check(*spec)
        cancel_alarm()
    except (AlarmInterrupt, KeyboardInterrupt):
        r = {'timeout': True}
    r['seconds'] = round(time.time() - t0, 1)
    res[str(spec)] = r
    print(spec, r, flush=True)
json.dump(res, open(os.path.join(OUT, 'resolvent_summary.json'), 'w'), indent=1, default=str)
