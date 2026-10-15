"""Build six-point Riemann-Roch decomposition systems with a 2-adic chain factor base.

f = A(x) + y C(x), deg A <= 3, C monic of degree 2, f(-T) = 0.
q = (E C^2 - A^2)/(x - x_T), monic of degree 6.
Factor-base membership of all six roots of q:
  arm 'mult'   (p-1 smooth, P-224 shape): X^(2^k)   == c   (mod q)
  arm 'dickson'(p+1 smooth, P-192 shape): D_(2^k)(X) == c  (mod q), D_2(x)=x^2-2
Encodings:
  'circuit': variables u (5 coefficients), s (6 coefficients of q), and per
             squaring step the remainder R_{i+1} (6) and quotient Q_i;
             every equation has degree <= 2.
  'direct' : the remainder of the k-fold map modulo q, expanded in u only.
Instances:
  'planted': T is the sum of six factor-base points (positive control).
  'random' : T is a uniformly random point (expected #relations ~ |F|^6/(720 p)).
Run with sage-python. Writes msolve input files and a JSON manifest.
"""
import json, sys, os
from sage.all__sagemath_schemes import *
from sage.all__sagemath_singular import *

def chain_map(arm, z):
    return z * z if arm == 'mult' else z * z - 2

def factor_base(arm, F, k, seed):
    """Return (c, S): S = all roots in F of the k-fold chain map minus c."""
    set_random_seed(seed)
    R = PolynomialRing(F, 'X'); X = R.gen()
    while True:
        x0 = F.random_element()
        if arm == 'mult' and x0 == 0:
            continue
        if arm == 'dickson' and (x0**2 - 4).is_square():
            continue  # need x0 = z + 1/z with z in the norm-1 torus
        c = x0
        for _ in range(k):
            c = chain_map(arm, c)
        g = X
        for _ in range(k):
            g = chain_map(arm, g)
        S = [r for r, _ in (g - c).roots()]
        return c, S

def build(arm, k, p, inst, seed, enc):
    F = GF(p)
    c, S = factor_base(arm, F, k, seed + 1)
    set_random_seed(seed)
    while True:  # resample the curve until >= 6 factor-base x-coordinates lie on it
        a, b = F.random_element(), F.random_element()
        if 4 * a**3 + 27 * b**2 == 0:
            continue
        E = EllipticCurve(F, [a, b])
        fb_points = []
        for x in S:
            rhs = x**3 + a * x + b
            if rhs.is_square() and rhs != 0:
                y = rhs.sqrt(); fb_points += [E(x, y), E(x, -y)]
        if len(fb_points) >= 12:
            break
    set_random_seed(seed + 2)
    planted = None
    if inst == 'planted':
        while True:
            pts = [fb_points[randint(0, len(fb_points) - 1)] for _ in range(6)]
            if len({P[0] for P in pts}) == 6:
                T = sum(pts, E(0))
                if T != E(0) and T[0] not in {P[0] for P in pts}:
                    planted = pts; break
    else:
        T = E.random_point()
    xT, yT = T[0], T[1]
    ustar = None
    if planted:
        # f = a0 + a1 x + a2 x^2 + a3 x^3 + y (c0 + c1 x + c2 x^2) vanishing at P1..P6 and -T
        rows = [[1, P[0], P[0]**2, P[0]**3, P[1], P[1] * P[0], P[1] * P[0]**2] for P in planted + [-T]]
        from sage.all__sagemath_modules import matrix
        K = matrix(F, rows).right_kernel()
        assert K.dimension() == 1, 'nondegeneracy: kernel dimension %d' % K.dimension()
        v = K.basis()[0]
        assert v[6] != 0, 'nondegeneracy: C not of degree 2'
        v = v / v[6]
        ustar = [v[1], v[2], v[3], v[4], v[5]]
    # Unknowns u = (a1, a2, a3, c0, c1); a0 fixed by f(-T) = 0.
    names = ['u%d' % i for i in range(5)]
    sn = ['s%d' % i for i in range(6)]
    if enc == 'circuit':
        nsteps = k
        rn, qn = [], []
        # remainder variables for steps whose input degree reaches 6
        allnames = names + sn
    Rx = PolynomialRing(F, names + ['x']); gens = Rx.gens(); u = gens[:5]; x = gens[5]
    Cpol = x**2 + u[4] * x + u[3]
    a0 = yT * (xT**2 + u[4] * xT + u[3]) - (u[0] * xT + u[1] * xT**2 + u[2] * xT**3)
    Apol = a0 + u[0] * x + u[1] * x**2 + u[2] * x**3
    N = (x**3 + a * x + b) * Cpol**2 - Apol**2
    # exact division by (x - xT)
    Rq = PolynomialRing(PolynomialRing(F, names), 'x')
    Nq = Rq(N.polynomial(x).change_ring(PolynomialRing(F, names)))
    qq, rr = Nq.quo_rem(Rq([-xT, 1]))
    assert rr == 0 and qq.degree() == 6 and qq.leading_coefficient() == 1
    qcoef = [qq[i] for i in range(6)]
    if enc == 'direct':
        Ru = PolynomialRing(F, names, order='degrevlex')
        RX = PolynomialRing(Ru, 'X'); X = RX.gen()
        qX = RX([Ru(t) for t in qcoef] + [1])
        r = X
        for _ in range(k):
            r = chain_map(arm, r) % qX
        eqs = [Ru(r[i]) for i in range(6)]
        eqs[0] -= c
        varnames = names
    else:
        # circuit: s_j = q_j(u); chain of squarings with quotient variables
        steps = []  # (deg_in) we track numeric polynomial degrees in X
        varnames = names + sn
        eq_specs = []
        # Determine variable layout
        deg = 1; r_index = 0; cur = None  # cur: list of coefficient expressions as strings later
        layout = []
        for i in range(k):
            dout = 2 * deg if arm == 'mult' else 2 * deg
            if dout >= 6:
                layout.append(('reduce', dout - 6))  # quotient degree
                deg = 5
            else:
                layout.append(('plain', None)); deg = dout
        for i, (kind, qd) in enumerate(layout):
            if kind == 'reduce':
                varnames += ['q%d_%d' % (i, j) for j in range(qd + 1)]
                if i < k - 1:
                    varnames += ['r%d_%d' % (i, j) for j in range(6)]
        Rv = PolynomialRing(F, varnames + ['X'], order='degrevlex')
        V = dict(zip(varnames, Rv.gens()[:-1])); X = Rv.gens()[-1]
        uu = [V[n] for n in names]; ss = [V[n] for n in sn]
        Ru = PolynomialRing(F, names)
        sub = {Ru.gen(i): uu[i] for i in range(5)}
        eqs = [ss[j] - Ru(qcoef[j]).subs(sub) if False else ss[j] - Rv(str(Ru(qcoef[j]))) for j in range(6)]
        qX = sum(ss[j] * X**j for j in range(6)) + X**6
        cur = X
        for i, (kind, qd) in enumerate(layout):
            sq = chain_map(arm, cur)
            if kind == 'plain':
                cur = sq; continue
            Q = sum(V['q%d_%d' % (i, j)] * X**j for j in range(qd + 1))
            if i < k - 1:
                Rn = sum(V['r%d_%d' % (i, j)] * X**j for j in range(6))
            else:
                Rn = Rv(c)
            diff = sq - Q * qX - Rn
            for j in range(diff.degree(X) + 1):
                co = diff.coefficient({X: j})
                if co != 0:
                    eqs.append(co)
            cur = Rn
        Rout = PolynomialRing(F, varnames, order='degrevlex')
        eqs = [Rout(e.subs({X: 0}) if e.degree(X) == 0 else e) for e in eqs]
        if ustar is not None:
            # numeric witness for the auxiliary variables
            RF = PolynomialRing(F, 'X'); Xn = RF.gen()
            qs = [Ru(qcoef[j])(*ustar) for j in range(6)]
            qn_ = RF(qs + [1])
            w = dict(zip(names, ustar)); w.update(dict(zip(sn, qs)))
            cur = Xn
            for i, (kind, qd) in enumerate(layout):
                sq = chain_map(arm, cur)
                if kind == 'plain':
                    cur = sq; continue
                Qn, Rn = sq.quo_rem(qn_)
                for j in range(qd + 1):
                    w['q%d_%d' % (i, j)] = Qn[j]
                if i < k - 1:
                    for j in range(6):
                        w['r%d_%d' % (i, j)] = Rn[j]
                cur = Rn
            assert cur == c, 'planted chain does not end at c'
            pt = [w[n] for n in varnames]
            assert all(e(*pt) == 0 for e in eqs), 'witness does not satisfy circuit system'
    if enc == 'direct' and ustar is not None:
        assert all(e(*ustar) == 0 for e in eqs), 'witness does not satisfy direct system'
    return dict(p=int(p), a=int(a), b=int(b), c=int(c), fb_size_x=len(S), fb_points=len(fb_points),
                T=[int(xT), int(yT)], planted_x=[int(P[0]) for P in planted] if planted else None,
                varnames=varnames, eqs=[str(e) for e in eqs], maxdeg=max(e.degree() for e in eqs if e != 0), witness_checked=ustar is not None)

if __name__ == '__main__':
    arm, k, p, inst, seed, enc, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6], sys.argv[7]
    d = build(arm, k, p, inst, seed, enc)
    with open(out + '.ms', 'w') as fh:
        fh.write(','.join(d['varnames']) + '\n' + str(p) + '\n' + ',\n'.join(e.replace(' ', '') for e in d['eqs']) + '\n')
    meta = {k2: v for k2, v in d.items() if k2 != 'eqs'}
    meta.update(arm=arm, k=k, inst=inst, seed=seed, enc=enc, nvars=len(d['varnames']), neqs=len(d['eqs']))
    json.dump(meta, open(out + '.json', 'w'), default=int)
    print(json.dumps({x: meta[x] for x in ['arm', 'k', 'enc', 'inst', 'nvars', 'neqs', 'maxdeg', 'fb_size_x', 'fb_points']}, default=int))
