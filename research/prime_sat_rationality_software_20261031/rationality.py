"""Reviewed rationality blocks and supplied-witness construction, without relation search."""
from pathlib import Path
import sys
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'prime_sat_shared_signed_chart_20261030'))
import quotient as q
import charts, projectors, signed_recovery
import circuits as ir

EVENTS = {}


def event(name):
    EVENTS[name] = EVENTS.get(name, 0)+1


def curve_parameters(p, a, b):
    q.require(type(p) is int and p > 3, 'prime p>3 premise')
    q.curve_data({'p': p, 'a': a, 'b': b})


def pad(poly, length, p):
    q.require(type(poly) is list and len(poly) <= length, 'bounded coefficient vector')
    for c in poly:
        q.scalar(c, p)
    return poly+[0]*(length-len(poly))


def modular_product(builder, U, L, R, label, final_zero=False):
    """Expose all bounded remainder/quotient coefficients, even when they are zero."""
    p = builder.p
    k = len(U)-1
    q.require(k >= 1 and len(L) == len(R) == k, 'modular product arity')
    uv = [builder.value(x) for x in U]
    lv = [builder.value(x) for x in L]
    rv = [builder.value(x) for x in R]
    quotient, remainder = q.divrem(q.mul(lv, rv, p), uv, p)
    # k=1 has no quotient variables; the numerical quotient is the zero polynomial.
    qv = pad([] if k == 1 else quotient, k-1, p)
    pv = pad(remainder, k, p)
    P = [{} for _ in range(k)] if final_zero else [builder.aux(label+'.P'+str(i), pv[i]) for i in range(k)]
    Q = [builder.aux(label+'.Q'+str(i), qv[i]) for i in range(k-1)]
    LR = ir.polynomial_product(L, R, p)
    UQ = ir.polynomial_product(U, Q, p) if Q else [{} for _ in range(2*k-1)]
    for i in range(2*k-1):
        builder.eq(label+'.coefficient'+str(i), ir.sub(ir.sub(LR[i], P[i] if i < k else {}, p), UQ[i], p))
    event('modular_product_certificate')
    return P


def nilpotent_square_block(k, p, a, b, U=None, C=None):
    """Return explicit IR plus a supplied-C assignment (not necessarily satisfying)."""
    curve_parameters(p, a, b)
    q.require(type(k) is int and 0 <= k <= 5, 'supported degree k0..5')
    U = [0]*k+[1] if U is None else U
    q.require(type(U) is list and len(U) == k+1 and U[-1] == 1, 'monic degree-k input')
    for x in U:
        q.scalar(x, p)
    C = pad([] if C is None else C, k, p)
    B = ir.Builder(p, a, b, 'nilpotent', k)
    u = [B.input('u'+str(i), U[i]) for i in range(k)]+[ir.constant(1, p)]
    if not k:
        return B.export()
    c = [B.aux('C'+str(i), C[i]) for i in range(k)]
    if k == 1:
        v = B.aux('v', U[0]*U[0] % p)
        F = B.aux('F', (-U[0]**3-a*U[0]+b) % p)
        B.eq('evaluation.square', ir.sub(v, ir.mul(u[0], u[0], p), p))
        B.eq('evaluation.cubic', ir.add(p, F, ir.mul(u[0], v, p), ir.scale(u[0], a, p), ir.constant(-b, p)))
        B.eq('ordinate.square', ir.sub(ir.mul(c[0], c[0], p), F, p))
        return B.export()
    if k == 2:
        qvalue = -U[1] % p
        qq = B.aux('f.q', qvalue)
        F1 = B.aux('f.F1', (a-U[0]-U[1]*qvalue) % p)
        F0 = B.aux('f.F0', (b-U[0]*qvalue) % p)
        B.eq('f.degree2', ir.add(p, qq, u[1]))
        B.eq('f.degree1', ir.add(p, F1, u[0], ir.mul(u[1], qq, p), ir.constant(-a, p)))
        B.eq('f.degree0', ir.add(p, F0, ir.mul(u[0], qq, p), ir.constant(-b, p)))
        F = [F0, F1]
    elif k == 3:
        F = [ir.sub(ir.constant(b, p), u[0], p), ir.sub(ir.constant(a, p), u[1], p), ir.scale(u[2], -1, p)]
    else:
        F = [ir.constant(x, p) for x in [b, a, 0, 1]+[0]*(k-4)]
    W = modular_product(B, u, c, c, 'C2')
    D = [ir.sub(x, y, p) for x, y in zip(W, F)]
    if k == 2:
        modular_product(B, u, D, D, 'D2zero', True)
    else:
        S = modular_product(B, u, D, D, 'D2')
        if k == 3:
            modular_product(B, u, S, D, 'D3zero', True)
        elif k == 4:
            modular_product(B, u, S, S, 'D4zero', True)
        else:
            T = modular_product(B, u, S, S, 'D4')
            modular_product(B, u, T, D, 'D5zero', True)
    return B.export()


def linear_B_square_block(p, a, b, mode, A=None, B=None, beta=0):
    curve_parameters(p, a, b)
    q.require(mode in ('guard', 'slack'), 'guard or slack mode')
    aa = pad([0] if A is None else A, 4, p)
    bb = pad([0, 1] if B is None else B, 2, p)
    q.require(bb[1] != 0, 'linear B stratum')
    q.scalar(beta, p)
    zval = q.inv(bb[1], p)
    alpha = -bb[0]*zval % p
    q1v = (aa[3]*alpha+aa[2]) % p
    q2v = (q1v*alpha+aa[1]) % p
    cv = (q2v*alpha+aa[0]) % p
    fv = (alpha**3+a*alpha+b) % p
    E = ir.Builder(p, a, b, mode, None)
    av = [E.input('A'+str(i), v) for i, v in enumerate(aa)]
    bv = [E.input('b'+str(i), v) for i, v in enumerate(bb)]
    z = E.aux('z', zval); x = E.aux('alpha', alpha)
    q1 = E.aux('q1', q1v); q2 = E.aux('q2', q2v)
    c = E.aux('c', cv); v = E.aux('v', alpha*alpha % p); F = E.aux('F', fv)
    E.eq('linear.inverse', ir.add(p, ir.mul(bv[1], z, p), ir.constant(-1, p)))
    E.eq('linear.root', ir.add(p, ir.mul(bv[1], x, p), bv[0]))
    E.eq('A.horner1', ir.sub(ir.sub(q1, ir.mul(av[3], x, p), p), av[2], p))
    E.eq('A.horner2', ir.sub(ir.sub(q2, ir.mul(q1, x, p), p), av[1], p))
    E.eq('A.value', ir.sub(ir.sub(c, ir.mul(q2, x, p), p), av[0], p))
    E.eq('f.square', ir.sub(v, ir.mul(x, x, p), p))
    E.eq('f.value', ir.sub(ir.sub(ir.sub(F, ir.mul(x, v, p), p), ir.scale(x, a, p), p), ir.constant(b, p), p))
    if mode == 'guard':
        e = E.aux('e', int(cv == 0))
        u = E.aux('u', q.inv(cv, p) if cv else 0)
        y = E.aux('beta', 0 if cv else beta)
        E.eq('guard.inverse', ir.add(p, ir.mul(c, u, p), e, ir.constant(-1, p)))
        E.eq('guard.c', ir.mul(c, e, p))
        E.eq('guard.u', ir.mul(u, e, p))
        E.eq('guard.beta', ir.sub(y, ir.mul(e, y, p), p))
        E.eq('guard.square', ir.sub(ir.mul(y, y, p), ir.mul(e, F, p), p))
    else:
        y = E.aux('beta', beta)
        u = E.aux('u', (beta*beta-fv)*q.inv(cv, p) % p if cv else 0)
        E.eq('slack.square', ir.sub(ir.sub(ir.mul(y, y, p), F, p), ir.mul(c, u, p), p))
    return E.export()


def constant_B_block(curve, B):
    p = curve['p'];curve_parameters(p, curve['a'], curve['b'])
    q.require(type(B) is list and len(B) == 1, 'constant B representation')
    q.scalar(B[0], p);q.require(B[0] != 0, 'constant nonzero B stratum')
    E = ir.Builder(p, curve['a'], curve['b'], 'constant', None)
    c = E.input('b0', B[0]);z = E.aux('z', q.inv(B[0], p))
    E.eq('constant.inverse', ir.add(p, ir.mul(c, z, p), ir.constant(-1, p)))
    return E.export()


def interpolate_known_roots(U, points):
    p, u = q.modulus(U)
    by_x = defaultdict(set)
    for P in points:
        if P is not None:
            q.require(type(P) is list and len(P) == 2, 'supplied point pair')
            x, y = P;q.scalar(x, p);q.scalar(y, p)
            by_x[x].add(min(y, -y % p))
    q.require(all(len(ys) == 1 for ys in by_x.values()), 'consistent supplied ordinate roots')
    result = [0]
    for x, ys in sorted(by_x.items()):
        basis = [1];denominator = 1
        for xx in sorted(by_x):
            if xx != x:
                basis = q.mul(basis, [-xx % p, 1], p)
                denominator = denominator*(x-xx) % p
        result = q.add(result, q.scale(basis, next(iter(ys))*q.inv(denominator, p) % p, p), p)
        event('interpolation_distinct_root')
    return [] if len(u) == 1 else pad(result, len(u)-1, p)


def chart_identity(w):
    return {key: w[key] for key in ('curve', 'interval', 'target', 'k', 'A', 'B', 'U')}


def construct_auxiliaries_from_checked_chart(w, recovered_points, arm, beta_override=None):
    """Use supplied checked data only. Candidate block does not invoke Euler acceptance."""
    curve = w['curve'];p = curve['p'];a = curve['a'];b = curve['b']
    signed_recovery.validate_shape(curve, w['target'], w['A'], w['B'], w['U'])
    factors = projectors.recover_interval_factors(w['U'], w['interval']['t'], w['interval']['s'], w['e'])
    q.require(recovered_points == signed_recovery.recover_signed_divisor(curve, w['target'], w['A'], w['B'], w['U'], factors, w['root_lifts']), 'checked supplied signed points')
    q.require(arm in ('uniform_nilpotent_square', 'stratified_slack_with_nilpotent_zero_B', 'stratified_guard_with_nilpotent_zero_B'), 'candidate arm')
    B = w['B'];stratum = 'zero' if B == [0] else 'constant' if len(B) == 1 else 'linear'
    roots = []
    if arm == 'uniform_nilpotent_square' or stratum == 'zero':
        C = interpolate_known_roots(w['U'], recovered_points)
        block = nilpotent_square_block(w['k'], p, a, b, w['U']['coeffs'], C)
        roots = [[x, q.evaluate(C or [0], x, p)] for x, m in factors['factors']]
    elif stratum == 'constant':
        block = constant_B_block(curve, B)
    else:
        alpha = -B[0]*q.inv(B[1], p) % p
        c = q.evaluate(w['A'], alpha, p)
        beta = 0
        if not c:
            supplied = [y for x, y in w['root_lifts'] if x == alpha]
            q.require(bool(supplied), 'supplied common-root ordinate')
            beta = min(min(y, -y % p) for y in supplied)
            if beta_override is not None:
                q.scalar(beta_override, p);beta = beta_override
            roots = [[alpha, beta]]
        mode = 'guard' if 'guard' in arm else 'slack'
        block = linear_B_square_block(p, a, b, mode, w['A'], B, beta)
    recovered = signed_recovery.recover_signed_divisor(curve, w['target'], w['A'], B, w['U'], factors, roots)
    event('candidate_chart_assignment')
    return {'arm': arm, 'stratum': stratum, 'chart': chart_identity(w), 'block': block,
            'root_lifts': roots, 'recovered': recovered}
