"""Independent P-256 Jacobian label checks and exhaustive m=4 oracle.

Imports no producer module. Definitions alone perform no mathematical panel.
"""
from collections import Counter
from hashlib import sha256
from itertools import product

P = int('ffffffff00000001000000000000000000000000ffffffffffffffffffffffff', 16)
A = P - 3
B = int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b', 16)
R = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551', 16)
G = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296', 16),
     int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5', 16))
ZERO = (0, 1, 0)


class Jacobian:
    def __init__(self):
        self.counts = Counter()

    def double(self, q):
        self.counts['jacobian_doublings'] += 1
        x, y, z = q
        if not z or not y:
            return ZERO
        yy = y*y % P
        s = 4*x*yy % P
        z2 = z*z % P
        m = (3*x*x + A*z2*z2) % P
        nx = (m*m - 2*s) % P
        return nx, (m*(s-nx)-8*yy*yy) % P, 2*y*z % P

    def add(self, q, v):
        self.counts['jacobian_additions'] += 1
        x, y, z = q
        u, w, t = v
        if not z:
            return v
        if not t:
            return q
        z2, t2 = z*z % P, t*t % P
        ux, vx = x*t2 % P, u*z2 % P
        uy, vy = y*t*t2 % P, w*z*z2 % P
        if ux == vx:
            return self.double(q) if uy == vy else ZERO
        h, dy = (vx-ux) % P, (vy-uy) % P
        h2 = h*h % P
        h3 = h*h2 % P
        nx = (dy*dy - h3 - 2*ux*h2) % P
        return nx, (dy*(ux*h2-nx)-uy*h3) % P, h*z*t % P

    def multiply(self, n, q):
        self.counts['jacobian_scalar_multiplications'] += 1
        if n < 0:
            return self.multiply(-n, (q[0], -q[1] % P, q[2]))
        out = ZERO
        for bit in bin(n)[2:]:
            out = self.double(out)
            if bit == '1':
                out = self.add(out, q)
        return out

    @staticmethod
    def affine_matches(q, affine):
        if affine is None:
            return q[2] == 0
        if not q[2]:
            return False
        x, y, z = q
        u, v = affine
        z2 = z*z % P
        return x == u*z2 % P and y == v*z2*z % P


def check_labels(base, target):
    j = Jacobian()
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    check('generator_equation', (G[1]*G[1]-G[0]**3-A*G[0]-B) % P == 0)
    check('generator_order', j.multiply(R, (*G, 1))[2] == 0)
    check('target_equation', (target[1]*target[1]-target[0]**3-A*target[0]-B) % P == 0)
    check('target_order', j.multiply(R, (*target, 1))[2] == 0)
    for index, record in enumerate(base):
        point = record['point']
        check(f'point_equation_{index}',
              (point[1]*point[1]-point[0]**3-A*point[0]-B) % P == 0)
        represented = j.add(j.multiply(record['a'], (*G, 1)),
                            j.multiply(record['b'], (*target, 1)))
        check(f'label_{index}', j.affine_matches(represented, point))
    return {'checks': checks, 'passed': len(checks), 'counters': dict(j.counts)}


def exhaustive(points, partitions):
    """Visit every signed quadruple; no x-coordinate hashing or producer calls."""
    if len(partitions) != 4:
        raise ValueError('four partitions required by oracle')
    j = Jacobian()
    signed = {(i, sign): (q[0], sign*q[1] % P, 1)
              for i, q in enumerate(points) for sign in (1, -1)}
    # Reuse the left sum arithmetically, without testing membership in a table.
    left = {(i, k, sign): j.add(signed[i, 1], signed[k, sign])
            for i in partitions[0] for k in partitions[1] for sign in (1, -1)}
    relations = []
    visited = 0
    trace = sha256()
    for i, k, l, m in product(*partitions):
        for s2, s3, s4 in product((1, -1), repeat=3):
            result = j.add(j.add(left[i, k, s2], signed[l, s3]), signed[m, s4])
            zero = result[2] == 0
            trace.update(f'{i},{k},{l},{m}:{s2},{s3},{s4}:{int(zero)}\n'.encode())
            visited += 1
            if zero:
                relations.append({'indices': [i, k, l, m], 'signs': [1, s2, s3, s4]})
    relations.sort(key=lambda row: (row['indices'], row['signs']))
    return {'signed_quadruples_visited': visited, 'relations': relations,
            'enumeration_trace_sha256': trace.hexdigest(), 'counters': dict(j.counts),
            'independence': 'separate exhaustive enumeration and Jacobian arithmetic; no producer import'}


def check_assessments(base, target, relations, assessments):
    j = Jacobian()
    checked = 0
    if len(relations) != len(assessments):
        raise AssertionError('assessment count differs from relation count')
    for relation, assessment in zip(relations, assessments):
        alpha = sum(sign*base[index]['a'] for index, sign in
                    zip(relation['indices'], relation['signs'])) % R
        beta = sum(sign*base[index]['b'] for index, sign in
                   zip(relation['indices'], relation['signs'])) % R
        if alpha != assessment['A'] or beta != assessment['B']:
            raise AssertionError('independent aggregate coefficient check failed')
        if j.add(j.multiply(alpha, (*G, 1)), j.multiply(beta, (*target, 1)))[2] != 0:
            raise AssertionError('independent labelled group relation check failed')
        if beta:
            scalar = -alpha*pow(beta, -1, R) % R
            if scalar != assessment['recovered'] or not j.affine_matches(j.multiply(scalar, (*G, 1)), target):
                raise AssertionError('independent recovered scalar verification failed')
        elif alpha or assessment['recovered'] is not None:
            raise AssertionError('independent zero-Q classification failed')
        checked += 1
    return {'relations_checked': checked, 'counters': dict(j.counts)}
