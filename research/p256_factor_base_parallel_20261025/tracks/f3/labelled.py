"""Exact P-256 labelled-point and APS m=3 correctness controls.

The search functions accept points only. No target logarithm or labels enter
their interfaces. This code is implementation validation, not a performance trial.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util

BASELINE = Path(__file__).resolve().parents[2] / 'baseline' / 'parameters.py'
spec = importlib.util.spec_from_file_location('published_parameters', BASELINE)
parameters = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parameters)
C = next(c for c in parameters.CURVES if c['name'] == 'P-256')
p, a, b, r = (C[k] for k in ('p', 'a', 'b', 'r'))
# SEC 2 v2, section 2.4.2: published P-256 generator.
G = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16),
     int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16))

def neg(P):
    return None if P is None else (P[0], -P[1] % p)

def on_curve(P):
    return P is None or (0 <= P[0] < p and 0 <= P[1] < p
        and (P[1]**2 - P[0]**3 - a*P[0] - b) % p == 0)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x, y = P; u, v = Q
    if x == u:
        if (y + v) % p == 0: return None
        slope = (3*x*x + a) * pow(2*y, -1, p) % p
    else:
        slope = (v-y) * pow((u-x) % p, -1, p) % p
    z = (slope*slope-x-u) % p
    return z, (slope*(x-z)-y) % p

def mul(n, P):
    if n < 0: return mul(-n, neg(P))
    out = None
    while n:
        if n & 1: out = add(out, P)
        P = add(P, P); n >>= 1
    return out

def sum_points(points):
    out = None
    for P in points: out = add(out, P)
    return out

def scalar(tag):
    # Public deterministic fixture material, no security claim for its sampling.
    return int.from_bytes(sha256(tag.encode()).digest(), 'big') % r

def label_point(alpha, beta, Q):
    return add(mul(alpha % r, G), mul(beta % r, Q))

def record(alpha, beta, Q):
    alpha %= r; beta %= r
    return dict(a=alpha, b=beta, point=label_point(alpha, beta, Q))

def hash_point(tag):
    x = int.from_bytes(sha256(tag.encode()).digest(), 'big') % p
    increments = 0
    while True:
        f = (x*x*x + a*x + b) % p
        y = pow(f, (p+1)//4, p)
        if y*y % p == f: return (x, min(y, p-y)), increments
        x = (x+1) % p; increments += 1

def random_base(Q, size=24, tag='natural-20261025'):
    points = []; seen = set(); rejected = Counter()
    attempt = 0
    while len(points) < size:
        A, B = (scalar(f'{tag}:{attempt}:{k}') for k in ('a','b'))
        z = record(A, B, Q); attempt += 1
        P = z['point']
        if P is None: rejected['identity'] += 1; continue
        if P[0] in seen: rejected['repeated_x_including_inverse'] += 1; continue
        seen.add(P[0]); points.append(z)
    return points, dict(attempts=attempt, accepted=len(points), rejected=dict(rejected),
                        scalar_multiplications=2*attempt, point_addition_calls=attempt)

def s3(x, y, z):
    return ((x-y)**2*z*z - 2*((x+y)*(x*y+a)+2*b)*z
            +(x*y-a)**2-4*b*(x+y)) % p

def quadratic_roots(A, B, D):
    A %= p; B %= p; D %= p
    if A == 0:
        if B: return [(-D * pow(B, -1, p)) % p], 'linear'
        if D: return [], 'constant_nonzero'
        raise ValueError('identically_zero_polynomial_requires_full_domain')
    delta = (B*B - 4*A*D) % p
    root = pow(delta, (p+1)//4, p)
    if root*root % p != delta: return [], 'quadratic_nonsquare'
    inv = pow(2*A, -1, p)
    return sorted({(-B+root)*inv % p, (-B-root)*inv % p}), 'quadratic'

def aps3_search(points, parts):
    """Hybrid h=2: enumerate two domains, solve residual quadratic exactly.

    Complete for the specified three coordinate domains. Sign recovery fixes
    the first sign positive, quotienting simultaneous negation only.
    """
    if len(parts) != 3: raise ValueError('three partitions required')
    if any(P is None or not on_curve(P) for P in points):
        raise ValueError('finite on-curve points required')
    if len({P[0] for P in points}) != len(points):
        raise ValueError('duplicate x including inverse points rejected')
    flat = sum(parts, [])
    if len(set(flat)) != len(flat) or set(flat) != set(range(len(points))):
        raise ValueError('partitions must be a disjoint cover')
    third = {points[i][0]: i for i in parts[2]}
    counts = Counter(); roots_found = []; relations = []
    for i, j in product(parts[0], parts[1]):
        x, y = points[i][0], points[j][0]
        roots, kind = quadratic_roots((x-y)**2,
            -2*((x+y)*(x*y+a)+2*b), (x*y-a)**2-4*b*(x+y))
        counts['specializations'] += 1; counts[kind] += 1
        for z in roots:
            counts['membership_probes'] += 1
            if z not in third: continue
            k = third[z]; roots_found.append([i,j,k]); counts['coordinate_roots'] += 1
            assert s3(x, y, z) == 0
            for sj, sk in product((1,-1), repeat=2):
                counts['sign_checks'] += 1
                if sum_points([points[i], mul(sj, points[j]), mul(sk, points[k])]) is None:
                    relations.append(dict(indices=[i,j,k], signs=[1,sj,sk]))
    return dict(counts=dict(counts), coordinate_roots=roots_found, relations=relations,
                complete_for='ordered partition-coordinate triples; signs modulo global negation')

def exhaustive3(points, parts):
    """Separate point-sum enumeration control; does not call s3 or quadratic solver."""
    relations = []; checks = 0
    for i,j,k in product(*parts):
        for sj,sk in product((1,-1), repeat=2):
            checks += 1
            if sum_points([points[i], mul(sj,points[j]), mul(sk,points[k])]) is None:
                relations.append(dict(indices=[i,j,k], signs=[1,sj,sk]))
    return dict(point_sum_checks=checks, relations=relations)

def assess(base, Q, relation):
    inds, signs = relation['indices'], relation['signs']
    if len(inds) != len(signs) or not inds or any(s not in (-1,1) for s in signs):
        raise ValueError('invalid dependency encoding')
    if any(i < 0 or i >= len(base) for i in inds): raise ValueError('index out of range')
    if not on_curve(Q) or Q is None or mul(r,Q) is not None:
        raise ValueError('invalid target')
    for i in set(inds):
        z = base[i]; P = z['point']
        if not on_curve(P) or P != label_point(z['a'],z['b'],Q):
            raise ValueError('invalid point or label')
    A = sum(s*base[i]['a'] for i,s in zip(inds,signs)) % r
    B = sum(s*base[i]['b'] for i,s in zip(inds,signs)) % r
    point_sum = sum_points(mul(s,base[i]['point']) for i,s in zip(inds,signs))
    zero = point_sum is None
    answer = (-A*pow(B,-1,r)) % r if zero and B else None
    verified = answer is not None and mul(answer,G) == Q
    xs = [base[i]['point'][0] for i in inds if base[i]['point'] is not None]
    return dict(A=A, B=B, point_sum_zero=zero, useful=bool(verified), recovered=answer,
        recovered_point_verified=verified, repeated_index=len(set(inds)) != len(inds),
        repeated_x=len(set(xs)) != len(xs),
        classification=('useful' if verified else 'zero_Q_dependency' if zero else 'not_a_relation'))

def vanishing_poly(xs):
    coeff = [1]
    for x in xs:
        out = [0]*(len(coeff)+1)
        for i,c in enumerate(coeff):
            out[i] = (out[i]-x*c) % p; out[i+1] = (out[i+1]+c) % p
        coeff = out
    return coeff  # ascending coefficients, exact product of linear factors
