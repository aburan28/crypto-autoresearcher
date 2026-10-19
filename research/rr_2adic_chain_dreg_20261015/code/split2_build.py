"""Two-level sign-pattern split: guess the signs of the last two remainders (mult arm, X^(2^k) = c).

On each root x of q, X^(2^(k-2)) takes one of the four fourth roots y0, y1, y2 = -y0, y3 = -y1 of c
(y0^2 = y2^2 = s, y1^2 = y3^2 = -s). A guess is a composition (m0, m1, m2, m3) of 6 (the number of roots
on each y_j), and
    q = q_plus * q_minus,  q_plus = f0 * f2,  q_minus = f1 * f3,  deg f_j = m_j,  f_j | X^(2^(k-2)) - y_j,
each f_j checked by a squaring chain of depth k - 2. q_plus and q_minus are the one-level split of
split_build.py (m = m0 + m2); the nesting keeps every equation of degree <= 2.

Usage (sage-python): split2_build.py K P INST SEED M0,M1,M2,M3 OUT
"""
import json, sys
from sage.all__sagemath_schemes import *
from sage.all__sagemath_singular import *
import build_systems as B
from split_build import chain_layout


def main():
    k, p, inst, seed, comp, out = (int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]),
                                   [int(t) for t in sys.argv[5].split(',')], sys.argv[6])
    assert len(comp) == 4 and sum(comp) == 6 and min(comp) >= 0
    depth = k - 2
    assert all(mj <= 2 ** depth for mj in comp), 'a factor of degree > 2^(k-2) cannot divide X^(2^(k-2)) - y'
    d = B.build('mult', k, p, inst, seed, 'circuit')
    F = GF(p)
    a, b, c = F(d['a']), F(d['b']), F(d['c'])
    xT, yT = F(d['T'][0]), F(d['T'][1])
    r4 = sorted(F(c).nth_root(4, all=True))
    assert len(r4) == 4
    y0 = r4[0]
    y1 = [t for t in r4 if t not in (y0, -y0)][0]
    ys = [y0, y1, -y0, -y1]

    names = ['u%d' % i for i in range(5)]
    Ru = PolynomialRing(F, names)
    RuX = PolynomialRing(Ru, 'x'); x = RuX.gen(); u = Ru.gens()
    Cpol = x**2 + u[4] * x + u[3]
    a0 = yT * (xT**2 + u[4] * xT + u[3]) - (u[0] * xT + u[1] * xT**2 + u[2] * xT**3)
    Apol = a0 + u[0] * x + u[1] * x**2 + u[2] * x**3
    qq, rr = ((x**3 + a * x + b) * Cpol**2 - Apol**2).quo_rem(x - xT)
    assert rr == 0 and qq.degree() == 6 and qq.leading_coefficient() == 1
    qcoef = [qq[i] for i in range(6)]

    dP, dN = comp[0] + comp[2], comp[1] + comp[3]
    lay = {j: chain_layout(depth, comp[j]) if comp[j] else [] for j in range(4)}
    varnames = names + ['s%d' % i for i in range(6)]
    varnames += ['P%d' % i for i in range(dP)] + ['N%d' % i for i in range(dN)]
    for j in range(4):
        varnames += ['f%d_%d' % (j, i) for i in range(comp[j])]
    for j in range(4):
        for i, (kind, qd) in enumerate(lay[j]):
            if kind == 'reduce':
                varnames += ['f%dq%d_%d' % (j, i, t) for t in range(qd + 1)]
            if kind in ('reduce', 'const') and i < depth - 1:
                varnames += ['f%dr%d_%d' % (j, i, t) for t in range(comp[j])]
    R = PolynomialRing(F, varnames + ['X'], order='degrevlex')
    V = dict(zip(varnames, R.gens()[:-1])); X = R.gens()[-1]

    def monic(prefix, deg):
        return sum(V['%s%d' % (prefix, i)] * X**i for i in range(deg)) + X**deg

    def coeff_eqs(poly):
        return [poly.coefficient({X: i}) for i in range(poly.degree(X) + 1) if poly.coefficient({X: i}) != 0]

    eqs = [V['s%d' % i] - R(str(qcoef[i])) for i in range(6)]
    qX = monic('s', 6)
    Pp, Np = monic('P', dP), monic('N', dN)
    fs = [monic('f%d_' % j, comp[j]) for j in range(4)]
    eqs += coeff_eqs(Pp * Np - qX)
    eqs += coeff_eqs(fs[0] * fs[2] - Pp)
    eqs += coeff_eqs(fs[1] * fs[3] - Np)
    for j in range(4):
        if comp[j] == 0:
            continue
        cur = X
        for i, (kind, qd) in enumerate(lay[j]):
            sq = cur * cur
            if kind == 'plain':
                cur = sq; continue
            Q = sum(V['f%dq%d_%d' % (j, i, t)] * X**t for t in range(qd + 1)) if kind == 'reduce' else R(0)
            Rn = (sum(V['f%dr%d_%d' % (j, i, t)] * X**t for t in range(comp[j])) if i < depth - 1 else R(ys[j]))
            eqs += coeff_eqs(sq - Q * fs[j] - Rn)
            cur = Rn
    Rout = PolynomialRing(F, varnames, order='degrevlex')
    eqs = [Rout(e) for e in eqs]
    eqs = [e for e in eqs if e != 0]

    meta = dict(k=k, p=int(p), inst=inst, seed=seed, comp=comp, ys=[int(t) for t in ys], c=int(c),
                nvars=len(varnames), neqs=len(eqs), maxdeg=max(e.degree() for e in eqs), varnames=varnames,
                true_comp=None, witness_checked=False)
    if d['planted_x'] is not None:
        xs = [F(t) for t in d['planted_x']]
        vals = [x_**(2**depth) for x_ in xs]
        assert all(v in ys for v in vals), 'planted roots not in the factor base'
        groups = [[x_ for x_, v in zip(xs, vals) if v == ys[j]] for j in range(4)]
        meta['true_comp'] = [len(g) for g in groups]
        if meta['true_comp'] == comp:
            RF = PolynomialRing(F, 'Y'); Y = RF.gen()
            ustar = [F(t) for t in d['ustar']]
            w = dict(zip(names, ustar))
            qn = RF([Ru(qcoef[i])(*ustar) for i in range(6)] + [1])
            fn = [prod([Y - t for t in g], RF(1)) for g in groups]
            Pn, Nn = fn[0] * fn[2], fn[1] * fn[3]
            assert Pn * Nn == qn, 'planted roots do not factor q(u*)'
            w.update({'s%d' % i: qn[i] for i in range(6)})
            w.update({'P%d' % i: Pn[i] for i in range(dP)}); w.update({'N%d' % i: Nn[i] for i in range(dN)})
            for j in range(4):
                w.update({'f%d_%d' % (j, i): fn[j][i] for i in range(comp[j])})
                if comp[j] == 0:
                    continue
                cur = Y
                for i, (kind, qd) in enumerate(lay[j]):
                    sq = cur * cur
                    if kind == 'plain':
                        cur = sq; continue
                    Qn, Rn = sq.quo_rem(fn[j])
                    if kind == 'reduce':
                        for t in range(qd + 1):
                            w['f%dq%d_%d' % (j, i, t)] = Qn[t]
                    if i < depth - 1:
                        for t in range(comp[j]):
                            w['f%dr%d_%d' % (j, i, t)] = Rn[t]
                    cur = Rn
                assert cur == ys[j], 'planted chain does not end at y_j'
            pt = [w[n_] for n_ in varnames]
            assert all(e(*pt) == 0 for e in eqs), 'witness does not satisfy the two-level split system'
            meta['witness_checked'] = True
    with open(out + '.ms', 'w') as fh:
        fh.write(','.join(varnames) + '\n' + str(p) + '\n' + ',\n'.join(str(e).replace(' ', '') for e in eqs) + '\n')
    json.dump(meta, open(out + '.json', 'w'), default=int)
    print(json.dumps({x_: meta[x_] for x_ in ['k', 'inst', 'comp', 'true_comp', 'nvars', 'neqs', 'maxdeg', 'witness_checked']},
                     default=int))


if __name__ == '__main__':
    main()
