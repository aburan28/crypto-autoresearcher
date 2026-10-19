"""Sign-pattern split of the last remainder (mult arm, X^(2^k) = c factor base).

On each root x of q, R = X^(2^(k-1)) mod q takes a value with R(x)^2 = c, so R(x) = +s or -s with
s = x0^(2^(k-1)) a fixed square root of c. Up to the order of the roots, a sign pattern is the number
m of '+' roots, so q = q_plus * q_minus with deg q_plus = m and
    q_plus  | X^(2^(k-1)) - s,      q_minus | X^(2^(k-1)) + s,
each a squaring chain of depth k - 1 modulo a factor of degree m or 6 - m.

Variables: u (5 unknowns of f = A + yC), s0..s5 (coefficients of q), p0..p{m-1} (q_plus, monic),
n0..n{5-m} (q_minus, monic), and per factor and squaring step a quotient and a remainder.
Equations: s_j = q_j(u); q_plus * q_minus = q; the two chains. All have degree <= 2.

Usage (sage-python): split_build.py K P INST SEED M OUT
Writes OUT.ms (msolve input) and OUT.json (metadata; for planted instances the true m and a checked witness).
"""
import json, sys
from sage.all__sagemath_schemes import *
from sage.all__sagemath_singular import *
import build_systems as B


def chain_layout(k, d):
    """Steps of x -> x^2 for depth k modulo a monic degree-d factor.

    ('plain', None): no reduction, no new variables; ('reduce', e): quotient of degree e and a new remainder;
    ('const', None): the remainder is a constant (d = 1), so the step only squares it into a new variable.
    """
    deg, out = 1, []
    for _ in range(k):
        dout = 2 * deg
        if dout >= d:
            out.append(('reduce', dout - d)); deg = d - 1
        elif deg == 0:
            out.append(('const', None))
        else:
            out.append(('plain', None)); deg = dout
    return out


def main():
    k, p, inst, seed, m, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    assert 2 ** (k - 1) >= 6, 'need k >= 4 so every factor chain reaches its modulus degree'
    d = B.build('mult', k, p, inst, seed, 'circuit')  # same instance, curve, T and planted witness as the other sweeps
    F = GF(p)
    a, b, c = F(d['a']), F(d['b']), F(d['c'])
    xT, yT = F(d['T'][0]), F(d['T'][1])
    # s: a square root of c in the factor-base sense, s = x0^(2^(k-1)) for an element x0 with x0^(2^k) = c
    s = c.sqrt()
    names = ['u%d' % i for i in range(5)]
    Ru = PolynomialRing(F, names)
    RuX = PolynomialRing(Ru, 'x'); x = RuX.gen(); u = Ru.gens()
    Cpol = x**2 + u[4] * x + u[3]
    a0 = yT * (xT**2 + u[4] * xT + u[3]) - (u[0] * xT + u[1] * xT**2 + u[2] * xT**3)
    Apol = a0 + u[0] * x + u[1] * x**2 + u[2] * x**3
    qq, rr = ((x**3 + a * x + b) * Cpol**2 - Apol**2).quo_rem(x - xT)
    assert rr == 0 and qq.degree() == 6 and qq.leading_coefficient() == 1
    qcoef = [qq[i] for i in range(6)]

    dp, dm = m, 6 - m
    lay = {'P': chain_layout(k - 1, dp) if dp else [], 'N': chain_layout(k - 1, dm) if dm else []}
    varnames = names + ['s%d' % j for j in range(6)] + ['p%d' % j for j in range(dp)] + ['n%d' % j for j in range(dm)]
    for tag, dd in (('P', dp), ('N', dm)):
        for i, (kind, qd) in enumerate(lay[tag]):
            if kind == 'reduce':
                varnames += ['%sq%d_%d' % (tag, i, j) for j in range(qd + 1)]
            if kind in ('reduce', 'const'):
                if i < k - 2:
                    varnames += ['%sr%d_%d' % (tag, i, j) for j in range(dd)]
    R = PolynomialRing(F, varnames + ['X'], order='degrevlex')
    V = dict(zip(varnames, R.gens()[:-1])); X = R.gens()[-1]
    eqs = [V['s%d' % j] - R(str(qcoef[j])) for j in range(6)]
    qX = sum(V['s%d' % j] * X**j for j in range(6)) + X**6
    fac = {'P': sum(V['p%d' % j] * X**j for j in range(dp)) + X**dp,
           'N': sum(V['n%d' % j] * X**j for j in range(dm)) + X**dm}
    diff = fac['P'] * fac['N'] - qX
    eqs += [diff.coefficient({X: j}) for j in range(6)]
    target = {'P': s, 'N': -s}
    for tag, dd in (('P', dp), ('N', dm)):
        if dd == 0:
            continue
        cur = X
        for i, (kind, qd) in enumerate(lay[tag]):
            sq = cur * cur
            if kind == 'plain':
                cur = sq; continue
            Q = sum(V['%sq%d_%d' % (tag, i, j)] * X**j for j in range(qd + 1)) if kind == 'reduce' else R(0)
            Rn = sum(V['%sr%d_%d' % (tag, i, j)] * X**j for j in range(dd)) if i < k - 2 else R(target[tag])
            dd_ = sq - Q * fac[tag] - Rn
            for j in range(dd_.degree(X) + 1):
                co = dd_.coefficient({X: j})
                if co != 0:
                    eqs.append(co)
            cur = Rn
    Rout = PolynomialRing(F, varnames, order='degrevlex')
    eqs = [Rout(e) if e.degree(X) <= 0 else None for e in eqs]
    assert all(e is not None for e in eqs)
    eqs = [e for e in eqs if e != 0]

    meta = dict(k=k, p=int(p), inst=inst, seed=seed, m=m, s=int(s), c=int(c), nvars=len(varnames), neqs=len(eqs),
                maxdeg=max(e.degree() for e in eqs), varnames=varnames, true_m=None, witness_checked=False)
    if d['planted_x'] is not None:
        xs = [F(t) for t in d['planted_x']]
        signs = [x_**(2**(k - 1)) for x_ in xs]
        assert all(t in (s, -s) for t in signs), 'planted roots not in the factor base'
        plus = [x_ for x_, t in zip(xs, signs) if t == s]
        minus = [x_ for x_, t in zip(xs, signs) if t == -s]
        meta['true_m'] = len(plus)
        if len(plus) == m:
            # numeric witness
            RF = PolynomialRing(F, 'Y'); Y = RF.gen()
            ustar = [F(t) for t in d['ustar']]
            w = dict(zip(names, ustar))
            qn = RF([Ru(qcoef[j])(*ustar) for j in range(6)] + [1])
            fp, fm = prod([Y - t for t in plus], RF(1)), prod([Y - t for t in minus], RF(1))
            assert fp * fm == qn, 'planted roots do not factor q(u*)'
            w.update({'s%d' % j: qn[j] for j in range(6)})
            w.update({'p%d' % j: fp[j] for j in range(dp)}); w.update({'n%d' % j: fm[j] for j in range(dm)})
            for tag, f_ in (('P', fp), ('N', fm)):
                cur = Y
                for i, (kind, qd) in enumerate(lay[tag]):
                    sq = cur * cur
                    if kind == 'plain':
                        cur = sq; continue
                    Qn, Rn = sq.quo_rem(f_)
                    if kind == 'reduce':
                        for j in range(qd + 1):
                            w['%sq%d_%d' % (tag, i, j)] = Qn[j]
                    if i < k - 2:
                        for j in range(f_.degree()):
                            w['%sr%d_%d' % (tag, i, j)] = Rn[j]
                    cur = Rn
                if f_.degree():
                    assert cur == target[tag], 'planted chain does not end at +-s'
            pt = [w[n_] for n_ in varnames]
            assert all(e(*pt) == 0 for e in eqs), 'witness does not satisfy split system'
            meta['witness_checked'] = True
    with open(out + '.ms', 'w') as fh:
        fh.write(','.join(varnames) + '\n' + str(p) + '\n' + ',\n'.join(str(e).replace(' ', '') for e in eqs) + '\n')
    json.dump(meta, open(out + '.json', 'w'), default=int)
    print(json.dumps({x_: meta[x_] for x_ in ['k', 'inst', 'm', 'true_m', 'nvars', 'neqs', 'maxdeg', 'witness_checked']}, default=int))


if __name__ == '__main__':
    main()
