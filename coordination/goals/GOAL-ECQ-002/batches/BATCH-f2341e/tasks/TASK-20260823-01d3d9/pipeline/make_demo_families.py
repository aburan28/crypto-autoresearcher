#!/usr/bin/env python3
"""
Build INTERNAL demo families for the height-vs-parameter-size falsifier and for
the pipeline's own smoke tests.  These are NOT the campaign's base family: the
base family is chosen in TASK-20260823-d1cb76 and is read from a JSON spec.
They exist so the pipeline can be exercised and the mechanism of H-ECQ-d60d07
tested before that family lands.

Construction (self-contained, no citation needed): prescribe n sections
(x_i(t), y_i(t)) with rational-function coordinates and solve the LINEAR system

    a1 x_i y_i - a2 x_i^2 + a3 y_i - a4 x_i - a6 = x_i^3 - y_i^2

for the a-invariants over Q(t).  With n = 5 all five a-invariants are
determined; with n = 3 only (a2, a4, a6) are solved for and a1 = a3 = 0.  The
resulting family has Mordell-Weil rank over Q(t) AT MOST n and at least the
number of independent sections; the actual generic rank is a CLAIM TO CHECK,
which is exactly what the pipeline does by certifying specialisations.

usage: python3 make_demo_families.py OUTDIR
"""
import json
import os
import sys

import cypari

pari = cypari.pari


def solve_family(xs, ys, unknowns):
    """unknowns: 'all5' or 'a2a4a6'."""
    if unknowns == 'all5':
        rows = ['(%s)*(%s), -(%s)^2, (%s), -(%s), -1' % (x, y, x, y, x)
                for x, y in zip(xs, ys)]
    else:
        rows = ['-(%s)^2, -(%s), -1' % (x, x) for x in xs]
    M = '[%s]' % (';'.join(rows))
    v = '[%s]~' % (','.join('(%s)^3-(%s)^2' % (x, y) for x, y in zip(xs, ys)))
    sol = pari('matsolve(%s,%s)' % (M, v))
    vals = [str(sol[i]) for i in range(len(rows))]
    if unknowns == 'all5':
        return vals
    return ['0', vals[0], '0', vals[1], vals[2]]


FAMILIES = [
    # null object: no prescribed section at all (generic rank 0 expected)
    dict(name='DEMO-NULL-r0', sections=([], []), unknowns=None,
         a_invariants=['0', '0', '0', '0', 't'],
         claimed_generic_rank=0,
         notes='y^2 = x^3 + t.  Null-object control required by '
               'H-ECQ-d60d07.nearby_object_control: generic rank 0, no sections.'),
    dict(name='DEMO-SEC1-r1', sections=(['t'], ['t']), unknowns='a2a4a6',
         claimed_generic_rank=1, notes='one prescribed section (t,t)'),
    dict(name='DEMO-SEC3-r3', sections=(['0', 't', '1'], ['t', 't^2', 't+1']),
         unknowns='a2a4a6', claimed_generic_rank=3,
         notes='three prescribed sections, a1=a3=0'),
    dict(name='DEMO-SEC5-r5',
         sections=(['0', 't', '1', '-t', 't^2'], ['t', 't^2', 't+1', '1', 't^3+1']),
         unknowns='all5', claimed_generic_rank=5,
         notes='five prescribed sections, all five a-invariants solved'),
    dict(name='DEMO-SEC5-BIGCOEFF',
         sections=(['0', '10007*t', '1', '-t', '99991*t^2'],
                   ['t', 't^2', 't+1', '1', 't^3+1']),
         unknowns='all5', claimed_generic_rank=5,
         notes='same shape as DEMO-SEC5-r5 but with large constants inside the '
               'section coordinates: isolates the family-constant contribution '
               'to the height from the parameter contribution'),
]


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    written = []
    for f in FAMILIES:
        if f.get('unknowns') is None:
            ai = f['a_invariants']
            secs = []
        else:
            xs, ys = f['sections']
            if f['unknowns'] == 'a2a4a6' and len(xs) < 3:
                # under-determined: pad by fixing a2 = a4 = 0 and solving a6
                ai = ['0', '0', '0', '0',
                      str(pari('-((%s)^3-(%s)^2)' % (xs[0], ys[0])))]
            else:
                ai = solve_family(xs, ys, f['unknowns'])
            secs = [[x, y] for x, y in zip(xs, ys)]
        spec = {'name': f['name'], 'params': ['t'], 'a_invariants': ai,
                'sections': secs,
                'claimed_generic_rank': f['claimed_generic_rank'],
                'source': 'internal (constructed in make_demo_families.py)',
                'notes': f['notes']}
        p = os.path.join(outdir, f['name'] + '.json')
        json.dump(spec, open(p, 'w'), indent=1)
        written.append(p)
        print('wrote', p)
    return written


if __name__ == '__main__':
    main(sys.argv[1])
