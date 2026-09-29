#!/usr/bin/env python3
"""
RUN 1 -- controls before anything is believed.

Everything downstream rests on four things being true.  Each is checked here,
exactly, before a single tuple is scanned:

 C1  the construction is reproduced as the BATCH-da59ec validator re-derived it:
     p = g^2 - r IDENTICALLY in (x,T), deg_x r = 4, deg_x g = 6, and all twelve
     sections on y^2 = r IDENTICALLY in T (not at sampled T);
 C2  the quartic -> Weierstrass map is right: every mapped section satisfies the
     Weierstrass equation in exact rational arithmetic;
 C3  the model carrying the points and the Jacobian Y^2 = X^3 - 27IX - 27J have
     the SAME minimal model (same c4:c6).  This licenses measuring the height on
     the Jacobian -- which needs no rational point -- so that the null families
     with NO rational section are measured on exactly the same object as the
     Mestre families;
 C4  the height measurement reproduces an independent prior measurement: the
     BATCH-f2341e validator measured h = 79.6 for Mestre tuple A.

 C5  negative control on the certifier's inputs: a deliberately wrong section
     (y shifted by 1) must FAIL the on-curve test.

usage: selftest_construction.py OUT.json
"""
import json
import sys
from fractions import Fraction as F

import measure
from mestre import (quartic_IJ, quartic_to_weierstrass, on_weierstrass,
                    integral_model)

TUPLE_A = (-17, -16, 10, 11, 14, 17)
TUPLE_B = (399, 380, 352, 47, 4, 0)


def main(out_path):
    res = {'task_id': 'TASK-20260823-416e78', 'checks': []}
    ok_all = True
    for name, tup in (('MESTRE-PUBLISHED-A', TUPLE_A), ('MESTRE-PUBLISHED-B', TUPLE_B)):
        fam = measure.family_from_tuple(tup, name=name)
        c1 = fam.identity_checks()
        c1['tuple'] = list(tup)
        c1['check'] = 'C1 construction identities in Q(T)'
        c1['passed'] = (c1['p_equals_g2_minus_r_identically']
                        and c1['deg_x_r'] == 4 and c1['deg_x_g'] == 6
                        and c1['n_sections'] == 12
                        and c1['sections_on_curve_identically_in_T'])
        res['checks'].append(c1)
        ok_all &= c1['passed']

        c2 = {'check': 'C2 quartic->Weierstrass map, exact', 'family': name,
              'per_t': []}
        c3 = {'check': 'C3 point-carrying model vs Jacobian minimal model',
              'family': name, 'per_t': []}
        for t0 in (F(1), F(2), F(3), F(4), F(5), F(1, 2), F(2, 3), F(7)):
            quart = fam.quartic_at(t0)
            secs = fam.sections_at(t0)
            mp_out = measure.measure_points(t0, quart, secs)
            if mp_out is None:
                c2['per_t'].append({'t': str(t0), 'status': 'skipped'})
                continue
            aint, ipts = mp_out
            allon = all(on_weierstrass(aint, P) for P in ipts)
            c2['per_t'].append({'t': str(t0), 'n_points': len(ipts),
                                'all_points_exactly_on_curve': allon})
            _, _, h1, _ = measure.minimal_invariants(aint)
            c41, c61, _, _ = measure.minimal_invariants(aint)
            jai = measure._jacobian_ai(quart)
            c42, c62, h2, _ = measure.minimal_invariants(jai)
            c3['per_t'].append({'t': str(t0),
                                'point_model_key': '%d:%d' % (c41, c61),
                                'jacobian_key': '%d:%d' % (c42, c62),
                                'same_minimal_model': (c41, c61) == (c42, c62),
                                'naive_height': h1,
                                'naive_height_jacobian': h2})
        c2['passed'] = all(r.get('all_points_exactly_on_curve', True)
                           for r in c2['per_t'])
        c3['passed'] = all(r['same_minimal_model'] for r in c3['per_t'])
        res['checks'].append(c2)
        res['checks'].append(c3)
        ok_all &= c2['passed'] and c3['passed']

    # C4 -- reproduce the independent prior measurement
    fam = measure.family_from_tuple(TUPLE_A, name='MESTRE-PUBLISHED-A')
    m = measure.measure(fam)
    c4 = {
        'check': 'C4 reproduction of an independent prior measurement',
        'prior': 'BATCH-f2341e validator (TASK-20260823-6040d1) measured naive '
                 'height 79.6 for Mestre tuple (-17,-16,10,11,14,17) at '
                 'certified rank >= 11',
        'measured_envelope_min_naive_height': m['measured_envelope_min_naive_height'],
        'argmin_t': m['envelope_argmin_t'],
        'agrees_to_1_decimal': abs(m['measured_envelope_min_naive_height'] - 79.6) < 0.05,
    }
    c4['passed'] = c4['agrees_to_1_decimal']
    res['checks'].append(c4)
    ok_all &= c4['passed']

    # C5 -- negative control
    quart = fam.quartic_at(F(4))
    secs = fam.sections_at(F(4))
    aint, ipts = measure.measure_points(F(4), quart, secs)
    bad = [(ipts[0][0], ipts[0][1] + 1)]
    c5 = {'check': 'C5 negative control: a corrupted point must fail on-curve',
          'corrupted_point_on_curve': on_weierstrass(aint, bad[0]),
          'genuine_point_on_curve': on_weierstrass(aint, ipts[0])}
    c5['passed'] = (not c5['corrupted_point_on_curve']) and c5['genuine_point_on_curve']
    res['checks'].append(c5)
    ok_all &= c5['passed']

    res['all_checks_passed'] = bool(ok_all)
    json.dump(res, open(out_path, 'w'), indent=1)
    for c in res['checks']:
        print('%-60s %s' % (c['check'], 'PASS' if c['passed'] else 'FAIL'))
    print('ALL:', res['all_checks_passed'])
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
