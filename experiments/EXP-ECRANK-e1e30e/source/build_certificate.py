#!/usr/bin/env python3
"""
Build a rank certificate for a chosen (base curve, support, k, objective).

Emits the JSON consumed by verify_certificate.py (exact, PARI-free) and
regulator_check.py (numerical, for multi-point classes).

usage: build_certificate.py --ai 1,-1,1,0,0 --k 5 --objective classes --out cert.json
"""
import argparse
import json
import sys
import os
from fractions import Fraction
from math import isqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twist_family as tf
from twist_family import pari


def build(a_invariants, k, objective, support, time_limit=20, name=''):
    (A, B), prof = tf.profile(a_invariants, support, time_limit)
    best = tf.optimise(prof, support, k)[objective]
    score, m0, V = best
    d0 = tf.class_value(m0, support)
    Ap, Bp = A * d0 * d0, B * d0 * d0 * d0

    twists = []
    for v in V:
        d = tf.class_value(v, support)
        e = prof[m0 ^ v]
        # The scan computed points on the twist of the SEED curve by
        # class_value(m0^v).  The certificate's base curve is the seed twisted
        # by d0, so the class we need is d0*d -- and these differ by the square
        # of the primes shared by d0 and d, because XOR cancels them.  Transport
        # the points along (u,v) |-> (u t^2, v t^3), which is the isomorphism
        # E^(e) -> E^(e t^2).
        e_class = tf.class_value(m0 ^ v, support)
        square = (d0 * d) // e_class
        assert square * e_class == d0 * d and isqrt(square) ** 2 == square, \
            'coset transport factor is not a perfect square'
        t = isqrt(square)
        pts = [[str(Fraction(px) * t * t), str(Fraction(py) * t ** 3)]
               for px, py in e['points']]
        twists.append({'d': d, 'points': pts,
                       'transport_factor_t': t,
                       'pari_r_low': e['r_low'], 'pari_r_high': e['r_high']})
    E = pari('ellinit([0,0,0,%d,%d])' % (Ap, Bp))
    Emin = pari('ellminimalmodel(%s)' % E)
    return {
        'name': name,
        'objective': objective,
        'score': score,
        'base_curve': {
            'A': Ap, 'B': Bp,
            'minimal_model_a_invariants': str(pari('%s[1..5]' % Emin)),
            'conductor': str(pari('ellglobalred(%s)[1]' % Emin)),
            'j_invariant': str(pari('%s.j' % E)),
            'rank_over_Q_pari': prof[m0]['r_low'],
        },
        'field': {'k': k, 'degree': 2 ** k,
                  'V_classes': sorted(tf.class_value(v, support) for v in V)},
        'search': {'support': support, 'seed_a_invariants': list(a_invariants),
                   'twist_coset_representative': d0,
                   'timed_out_classes': sum(1 for e in prof if e['timed_out'])},
        'twists': twists,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ai', required=True, help='comma-separated a-invariants')
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--objective', choices=['classes', 'sum_mult'], default='classes')
    ap.add_argument('--support', default=','.join(map(str, tf.DEFAULT_SUPPORT)))
    ap.add_argument('--time-limit', type=int, default=20)
    ap.add_argument('--name', default='')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    obj = 'n_classes' if a.objective == 'classes' else 'sum_mult'
    cert = build([int(x) for x in a.ai.split(',')], a.k, obj,
                 [int(x) for x in a.support.split(',')], a.time_limit, a.name)
    json.dump(cert, open(a.out, 'w'), indent=1)
    print('score=%d  base A=%d B=%d  [K:Q]=%d'
          % (cert['score'], cert['base_curve']['A'], cert['base_curve']['B'],
             cert['field']['degree']))
