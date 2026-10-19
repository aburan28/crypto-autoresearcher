"""Prospective PO003 companion filter components; not an experiment launcher.

Coordinates are public field elements. Training acceptance labels must come
from the baseline divisor/FB checker, never from discrete-log ground truth.
The integrating executor must meter all calls and enforce split separation.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json


def companion_point(p, curve_a, curve_b, x, y):
    """C:y²=x6+A*x²+B -> E2:V²=W³+A*W²+B², for x != 0."""
    x, y = x % p, y % p
    if not x:
        raise ValueError('x=0 requires the excluded exceptional-point path')
    if not curve_b % p or (y*y-x**6-curve_a*x*x-curve_b) % p:
        raise ValueError('invalid affine curve input')
    inv_x = pow(x, -1, p)
    return curve_b * inv_x**2 % p, curve_b * y * inv_x**3 % p


def add_companion(p, curve_a, curve_b, left, right):
    """Elliptic addition, infinity=None, in the fixed E2 coordinates."""
    for point in (left, right):
        if point is not None:
            u, v = point
            if not (0 <= u < p and 0 <= v < p):
                raise ValueError('noncanonical field coordinates')
            if (v*v-u**3-curve_a*u*u-curve_b**2) % p:
                raise ValueError('point is not on E2')
    if left is None:
        return right
    if right is None:
        return left
    u, v = left
    s, t = right
    if u == s and (v+t) % p == 0:
        return None
    if u == s:
        slope = (3*u*u+2*curve_a*u) * pow(2*v, -1, p) % p
    else:
        slope = (t-v) * pow(s-u, -1, p) % p
    w = (slope*slope-curve_a-u-s) % p
    return w, (slope*(u-w)-v) % p


def public_bucket(p, point):
    if point is None:
        return 'infinity'
    w, _ = point
    if not 0 <= w < p:
        raise ValueError('noncanonical bucket input')
    symbol = pow(w, (p-1)//2, p)
    symbol = -1 if symbol == p-1 else symbol
    return f'{symbol:+d}:{16*w//p:02d}'


def candidate_digest(identity):
    """The caller supplies the complete identity required by the protocol."""
    expected = {'curve_uid', 'source_scalar', 'lambda', 'signed_fb_lift_ids'}
    if set(identity) != expected:
        raise ValueError('candidate identity fields differ from frozen interface')
    encoded = json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()
    return sha256(encoded).hexdigest()


def split(candidate_id):
    if len(candidate_id) != 64 or any(c not in '0123456789abcdef' for c in candidate_id):
        raise ValueError('expected canonical SHA-256 candidate identity')
    return 'train' if int(candidate_id[-1], 16) % 2 == 0 else 'holdout'


def fit(training):
    """Retain ceil(nonempty bins/4), ranked by Beta(1,1) posterior mean."""
    seen = set()
    attempts, hits = Counter(), Counter()
    for row in training:
        if set(row) != {'candidate_id', 'bucket', 'accepted'}:
            raise ValueError('training record fields differ from frozen interface')
        ident = row['candidate_id']
        if ident in seen or split(ident) != 'train':
            raise ValueError('duplicate or holdout candidate in training data')
        if type(row['accepted']) is not bool:
            raise ValueError('acceptance is an exact baseline-checker boolean')
        seen.add(ident)
        attempts[row['bucket']] += 1
        hits[row['bucket']] += row['accepted']
    if not attempts:
        raise ValueError('no calibration data')
    ordered = sorted(attempts, key=lambda b: (
        -Fraction(hits[b]+1, attempts[b]+2), b))
    return {'schema': 'prym-companion-selector/v1',
            'retained_buckets': sorted(ordered[:(len(ordered)+3)//4]),
            'training_candidates': len(seen),
            'training_ids_sha256': sha256('\n'.join(sorted(seen)).encode()).hexdigest(),
            'unseen_bucket_policy': 'reject',
            'bins': {b: {'attempts': attempts[b], 'accepted': hits[b]}
                     for b in sorted(attempts)}}


def accepts(model, bucket):
    if model['schema'] != 'prym-companion-selector/v1':
        raise ValueError('unknown model schema')
    return bucket in model['retained_buckets']
