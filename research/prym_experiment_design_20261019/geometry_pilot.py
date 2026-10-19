#!/usr/bin/env python3
"""Prospective exact arithmetic pilot. Execution requires native run admission.

Uses a table of square multiplicities, rather than a point-counting oracle.
The check mode verifies artifact structure and algebraic consistency; it is
not an independent recount or an independent scientific review.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import resource
import time

import sympy as sp


def read_config(path):
    data = path.read_bytes()
    cfg = json.loads(data)
    if (cfg['schema'] != 'prym-geometry-input/v1'
            or cfg['experiment_id'] != 'EXP-ECDLP-da4ba3'
            or cfg['primes'] != [11, 13, 17, 19, 23, 31, 43, 59]
            or cfg['f_coefficients_descending'] != [1, 0, 0, 7]
            or cfg['covers_per_prime'] != 8
            or cfg['extension_degrees'] != [1, 2]):
        raise ValueError('unsupported frozen input parameters')
    return cfg, sha256(data).hexdigest()


def cover_pairs(p):
    return [pair for pair in combinations(range(p), 2)
            if all((x**3 + 7) % p for x in pair)][:8]


def counts(p, a, b, degree):
    """Count affine solutions plus the smooth-model points at infinity."""
    if degree == 1:
        elems = list(range(p))
        add = lambda x, y: (x + y) % p
        mul = lambda x, y: x * y % p
        const = lambda x: x % p
        nonresidue = None
    elif degree == 2:
        nonresidue = next(d for d in range(2, p)
                          if pow(d, (p - 1) // 2, p) == p - 1)
        elems = [(x, y) for x in range(p) for y in range(p)]
        add = lambda x, y: ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
        mul = lambda x, y: ((x[0]*y[0]+nonresidue*x[1]*y[1]) % p,
                            (x[0]*y[1]+x[1]*y[0]) % p)
        const = lambda x: (x % p, 0)
    else:
        raise ValueError('only degrees 1 and 2 are specified')
    squares = Counter(mul(y, y) for y in elems)
    ne, nh, nd = 1, 1, 2
    for x in elems:
        fx = add(mul(mul(x, x), x), const(7))
        hx = mul(add(x, const(-a)), add(x, const(-b)))
        ne += squares[fx]
        nh += squares[mul(fx, hx)]
        nd += squares[fx] * squares[hx]
    return {'degree': degree, 'q': p**degree, 'nonresidue': nonresidue,
            'N_E': ne, 'N_H': nh, 'N_D': nd}


def screen(p, n1, n2):
    t = p + 1 - n1['N_E']
    s1 = p + 1 - n1['N_H']
    s2 = p*p + 1 - n2['N_H']
    if (s1*s1-s2) % 2:
        raise ValueError('nonintegral genus-two coefficient')
    c2 = (s1*s1-s2) // 2
    fe = [1, -t, p]
    fa = [1, -s1, c2, -p*s1, p*p]
    T = sp.Symbol('T')
    e = sp.Poly.from_list(fe, T, domain=sp.QQ)
    aux = sp.Poly.from_list(fa, T, domain=sp.QQ)
    factors = sp.factor_list(aux)[1]
    odd = [int(r) for r in sp.factorint(n1['N_E']) if r > 2]
    r = max(odd) if odd else None
    return {'F_E': fe, 'F_A': fa,
            'F_A_irreducible_factors': [
                {'coefficients': [int(c) for c in f.all_coeffs()], 'multiplicity': m}
                for f, m in factors],
            'gcd_over_Q_degree': int(sp.gcd(e, aux).degree()),
            'E_order': n1['N_E'], 'A_order': int(aux.eval(1)),
            'largest_odd_prime_divisor_r': r,
            'r_divides_A_order': bool(aux.eval(1) % r == 0) if r else None,
            'source_type': 'supersingular_control' if t % p == 0 else 'ordinary_toy',
            'synthetic_screen_controls': {
                'shared_F_E_squared_gcd_degree': int(sp.gcd(e, e*e).degree()),
                'coprime_T_gcd_degree': int(sp.gcd(e, sp.Poly(T, T)).degree())}}


def verify(result, cfg, config_sha):
    if result.get('experiment_id') != cfg['experiment_id']:
        raise ValueError('experiment identity mismatch')
    if result.get('config_sha256') != config_sha:
        raise ValueError('input hash mismatch')
    expected = [(p, a, b) for p in cfg['primes'] for a, b in cover_pairs(p)]
    actual = [(row['p'], row['a'], row['b']) for row in result['rows']]
    if actual != expected or len(set(actual)) != 64:
        raise ValueError('incomplete, reordered or duplicated cover catalogue')
    for row in result['rows']:
        p = row['p']
        if [c['degree'] for c in row['counts']] != [1, 2]:
            raise ValueError('extension field coverage mismatch')
        for c in row['counts']:
            if c['q'] != p**c['degree']:
                raise ValueError('incorrect field size')
            if c['N_D'] != c['N_E'] + c['N_H'] - c['q'] - 1:
                raise ValueError('fiber-product point-count identity failed')
        n1, n2 = row['counts']
        if n2['N_E'] != p*p + 1 - ((p+1-n1['N_E'])**2 - 2*p):
            raise ValueError('elliptic trace recurrence failed')
        if row['screen'] != screen(p, n1, n2):
            raise ValueError('polynomial or subgroup screen mismatch')
        controls = row['screen']['synthetic_screen_controls']
        if controls != {'shared_F_E_squared_gcd_degree': 2, 'coprime_T_gcd_degree': 0}:
            raise ValueError('polynomial instrument control failed')
    if result.get('measurement_scope') != 'point_counts_Fp_Fp2_only':
        raise ValueError('scope mismatch')
    return {'artifact_checks': 'passed', 'rows_checked': len(actual),
            'independent_recount': False, 'execution_authority_granted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--output', type=Path)
    action.add_argument('--check', type=Path)
    args = parser.parse_args()
    cfg, digest = read_config(args.config)
    if args.check:
        print(json.dumps(verify(json.loads(args.check.read_text()), cfg, digest), sort_keys=True))
        return
    start = time.perf_counter()
    rows = []
    for p in cfg['primes']:
        for a, b in cover_pairs(p):
            observed = [counts(p, a, b, d) for d in cfg['extension_degrees']]
            rows.append({'p': p, 'a': a, 'b': b, 'counts': observed,
                         'screen': screen(p, *observed)})
    result = {'schema': 'prym-geometry-result/v1', 'experiment_id': cfg['experiment_id'],
              'config_sha256': digest, 'measurement_scope': 'point_counts_Fp_Fp2_only',
              'jacobian_maps_checked': False, 'full_genus3_frobenius_independent_check': False,
              'rows': rows, 'wall_seconds': time.perf_counter()-start,
              'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
              'environment': {'python': platform.python_version(), 'sympy': sp.__version__,
                              'platform': platform.platform()},
              'execution_authority_granted': False}
    verify(result, cfg, digest)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'raw-result.json').open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({'artifact': str(args.output/'raw-result.json'), 'rows': len(rows)}))


if __name__ == '__main__':
    main()
