"""Symbolic checks of the ordered-base derivation, generic (a, b) where feasible.

R1 m=3 root formula over Z[a,b][x1,x2,y1,y2]/(y_i^2 - f(x_i)):  S_3(x1, x2, x(P1 +- P2)) = 0.
   An identity over Z holds over every F_p: all curves, all odd p at once.
R2 m=4 root formula over F_p[a,b][x1,x2,x3,y1,y2,y3]/(...): S_4(x1,x2,x3, x(P1+P2+P3)) = 0,
   for p in {7, 11, 13, 101, 10007} with a, b symbolic (every curve over those primes), then over Z.
R3 m=4 Galois group over F_p(x1,x2,x3) by the resolvent cubic: F irreducible (checked in
   check_ordered.py) and the resolvent cubic of F splits into three linear factors over
   F_p(x1,x2,x3) => Gal = V_4 exactly.  Done per curve and for generic (a, b) at p = 101.
   Also disc_T F is a square in F_p(x) (Gal <= A_4) as a sub-check.
Usage: sage -python symbolic_checks.py OUTDIR
"""
import sys, json, time, os
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import S3_expr, symbolic_S

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'symbolic.log'), 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s); log.write(s + '\n'); log.flush()


summary = {}


def add_x(a, b, P, Q):
    """x, y of P + Q for P != +-Q, in a fraction field."""
    (x1, y1), (x2, y2) = P, Q
    lam = (y2 - y1) / (x2 - x1)
    x3 = lam ** 2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


# ------------------------------------------------------------------ R1
say('== R1 m=3 root formula over Z[a,b]')
t0 = time.time()
R = PolynomialRing(ZZ, ['a', 'b', 'x1', 'x2', 'y1', 'y2'])
a, b, x1, x2, y1, y2 = R.gens()
K = R.fraction_field()
I = R.ideal([y1 ** 2 - (x1 ** 3 + a * x1 + b), y2 ** 2 - (x2 ** 3 + a * x2 + b)])
ok3 = True
for sgn in (1, -1):
    xs, ys = add_x(K(a), K(b), (K(x1), K(y1)), (K(x2), sgn * K(y2)))
    val = S3_expr(K(a), K(b), K(x1), K(x2), xs)
    num = R(val.numerator())
    red = I.reduce(num)
    ok3 = ok3 and (red == 0)
summary['R1_m3_root_formula_over_Z[a,b]'] = {'ok': bool(ok3), 'seconds': round(time.time() - t0, 1)}
say('  ', summary['R1_m3_root_formula_over_Z[a,b]'])


# ------------------------------------------------------------------ R2
def m4_root_formula(base):
    R = PolynomialRing(base, ['a', 'b', 'x1', 'x2', 'x3', 'y1', 'y2', 'y3'])
    a, b, x1, x2, x3, y1, y2, y3 = R.gens()
    K = R.fraction_field()
    I = R.ideal([y1 ** 2 - (x1 ** 3 + a * x1 + b), y2 ** 2 - (x2 ** 3 + a * x2 + b), y3 ** 2 - (x3 ** 3 + a * x3 + b)])
    P12 = add_x(K(a), K(b), (K(x1), K(y1)), (K(x2), K(y2)))
    P123 = add_x(K(a), K(b), P12, (K(x3), K(y3)))
    r = P123[0]
    # S_4(x1, x2, x3, T) = Res_Z(S_3(x1, x2, Z), S_3(x3, T, Z)); evaluate at T = r via the symbolic S_4
    R4, S4 = symbolic_S(4, a, b, R)   # S_4 over the ring R (a, b symbolic), variables X1..X4, Z
    val = S4(K(x1), K(x2), K(x3), r, K(0))
    num = R(val.numerator())
    return I.reduce(num) == 0


say('== R2 m=4 root formula, a, b symbolic')
summary['R2_m4_root_formula'] = {}
for base in [GF(7), GF(11), GF(13), GF(101), GF(10007)]:
    t0 = time.time()
    ok = m4_root_formula(base)
    summary['R2_m4_root_formula'][str(base)] = {'ok': bool(ok), 'seconds': round(time.time() - t0, 1)}
    say('  ', base, summary['R2_m4_root_formula'][str(base)])
t0 = time.time()
try:
    alarm(900)
    okZ = m4_root_formula(ZZ)
    cancel_alarm()
    summary['R2_m4_root_formula']['ZZ'] = {'ok': bool(okZ), 'seconds': round(time.time() - t0, 1)}
except (AlarmInterrupt, KeyboardInterrupt):
    summary['R2_m4_root_formula']['ZZ'] = {'ok': 'timeout', 'seconds': round(time.time() - t0, 1)}
say('  ZZ', summary['R2_m4_root_formula']['ZZ'])


# ------------------------------------------------------------------ R3
def resolvent_check(base_ring_gens_ab):
    """base_ring_gens_ab: (p, a, b) with a, b either integers (specific curve) or None (generic)."""
    p, a, b = base_ring_gens_ab
    F = GF(p)
    if a is None:
        R = PolynomialRing(F, ['a', 'b', 'x1', 'x2', 'x3']); av, bv, x1, x2, x3 = R.gens()
    else:
        R = PolynomialRing(F, ['x1', 'x2', 'x3']); x1, x2, x3 = R.gens(); av, bv = F(a), F(b)
    K = R.fraction_field()
    PT = PolynomialRing(K, 'T'); T = PT.gen()
    PTX = PolynomialRing(PT, 'X'); X = PTX.gen()
    Fq = PTX(S3_expr(av, bv, K(x1), K(x2), X)).resultant(PTX(S3_expr(av, bv, K(x3), T, X)))
    Fq = PT(Fq)
    assert Fq.degree() == 4
    c = [Fq[i] / Fq[4] for i in range(5)]  # monic: T^4 + c3 T^3 + c2 T^2 + c1 T + c0
    b3, c2, d1, e0 = c[3], c[2], c[1], c[0]
    PZ = PolynomialRing(K, 'Z'); Z = PZ.gen()
    # resolvent cubic with roots r1 r2 + r3 r4, r1 r3 + r2 r4, r1 r4 + r2 r3
    res = Z ** 3 - c2 * Z ** 2 + (b3 * d1 - 4 * e0) * Z - (b3 ** 2 * e0 - 4 * c2 * e0 + d1 ** 2)
    # clear denominators and factor over R[Z]
    den = lcm([cf.denominator() for cf in res.list()])
    RZ = PolynomialRing(R, 'Zc'); Zc = RZ.gen()
    resR = sum(R((cf * den).numerator()) * Zc ** i for i, cf in enumerate(res.list()))
    fac = resR.factor()
    zdegs = sorted(int(g.degree()) for g, e in fac for _ in range(e) if g.degree() > 0)
    # discriminant square test: disc of monic quartic in K; is it a square in K?
    disc = Fq.discriminant()
    dn, dd = disc.numerator(), disc.denominator()
    def is_square_poly(P):
        return all(e % 2 == 0 for g, e in P.factor()) if P != 0 else True
    sq = is_square_poly(R(dn * dd))  # disc = dn/dd is a square iff dn*dd is a square polynomial (up to units: F_p^* squares?)
    # unit part: leading coefficient could be a non-square constant; check separately
    lc_sq = (R(dn * dd).lc()).is_square() if R(dn * dd) != 0 else True
    return {'resolvent_linear_factors_in_Z': zdegs, 'gal_in_V4': (zdegs == [1, 1, 1]), 'disc_square_in_Fp(x)': bool(sq and lc_sq)}


say('== R3 m=4 resolvent cubic over F_p(x1,x2,x3)')
summary['R3_m4_resolvent'] = {}
for spec in [(7, 1, 0), (7, 0, 1), (11, 0, 1), (11, 1, 0), (13, 2, 5), (101, 2, 3), (101, 0, 1), (1009, 5, 7), (10007, 1, 0), (101, None, None), (13, None, None)]:
    t0 = time.time()
    try:
        alarm(600)
        rec = resolvent_check(spec)
        cancel_alarm()
    except (AlarmInterrupt, KeyboardInterrupt):
        rec = {'timeout': True}
    rec['seconds'] = round(time.time() - t0, 1)
    summary['R3_m4_resolvent'][str(spec)] = rec
    say('  ', spec, rec)

with open(os.path.join(OUT, 'symbolic_summary.json'), 'w') as fh:
    json.dump(summary, fh, indent=1, default=str)
say('wrote', os.path.join(OUT, 'symbolic_summary.json'))
