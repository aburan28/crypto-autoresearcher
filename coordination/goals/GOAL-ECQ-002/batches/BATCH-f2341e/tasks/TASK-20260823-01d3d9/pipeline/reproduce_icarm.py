#!/usr/bin/env python3
"""
CHECK 1 (gates everything): reproduce the ICARM board's own numbers.

For curves ALREADY on the frozen snapshot, recompute from the a-invariants
alone -- rank (exactly certified from the curve's exhibited points, by
exact_certify), naive height, Faltings height, conductor, discriminant and
curve_key -- and compare with the board's recorded values.  If our height
definition were wrong, every later comparison against the frontier would be
meaningless, so this runs BEFORE any search.

The board's rank is a lower bound backed by its points; ours is recomputed
independently, in exact arithmetic, from those same points.  Agreement means
"our certifier reproduces their bound", not "their bound is optimal".

usage: python3 reproduce_icarm.py SNAPSHOT.json OUT.json [--ids 42,244,276] [--limit N]
"""
import argparse
import json
import sys
import time

import exact_certify
import icarm_invariants as inv

REL_TOL = 1e-9


def compare_curve(c, conductor_time_limit=20):
    ai = [int(a) for a in c['ainvs']]
    row = {'id': c.get('id'), 'submitter': c.get('submitter'),
           'board_rank': c['rank_lower_bound']}
    t0 = time.time()
    try:
        m = inv.invariants(ai, time_limit=conductor_time_limit)
    except inv.InvariantTimeout as e:
        row['status'] = 'infrastructure_timeout'
        row['note'] = str(e)
        return row
    cert = exact_certify.certify(ai, c['points'])
    escalated = False
    if cert['certified_rank_lower_bound'] < c['rank_lower_bound']:
        # more primes / larger l: the first pass ran out of F_l coordinates,
        # which is a search-bound limitation of the certifier, not a fact
        # about the curve.  Recorded either way.
        cert2 = exact_certify.certify(ai, c['points'], max_prime=8000,
                                      max_good_primes=250,
                                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
        escalated = True
        if cert2['certified_rank_lower_bound'] > cert['certified_rank_lower_bound']:
            cert = cert2
    row.update({
        'status': 'compared',
        'n_board_points': len(c['points']),
        'our_certified_rank': cert['certified_rank_lower_bound'],
        'rank_agrees': cert['certified_rank_lower_bound'] == c['rank_lower_bound'],
        'certifier_escalated': escalated,
        'certifier_l': cert.get('independence', {}).get('l'),
        'certifier_n_primes': len(cert.get('independence', {}).get('primes_used', [])),
        'on_curve_failures': cert['on_curve_failures'],
        'board_naive_height': c['naive_height'],
        'our_naive_height': m['naive_height'],
        'naive_height_abs_diff': abs(m['naive_height'] - c['naive_height']),
        'board_faltings_height': c['faltings_height'],
        'our_faltings_height': m['faltings_height'],
        'faltings_height_abs_diff': abs(m['faltings_height'] - c['faltings_height']),
        'board_conductor': c['conductor'],
        'our_conductor': m['conductor'],
        'conductor_agrees': (m['conductor'] == c['conductor']
                             if m['conductor'] is not None else None),
        'conductor_timed_out': m['conductor_timed_out'],
        'discriminant_agrees': m['discriminant'] == c['discriminant'],
        'curve_key_agrees': m['curve_key'] == c['curve_key'],
        'seconds': time.time() - t0,
    })
    for k in ('naive', 'faltings'):
        d = row['%s_height_abs_diff' % k]
        b = abs(c['%s_height' % k]) or 1.0
        row['%s_height_agrees' % k] = (d / b) < REL_TOL
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('out')
    ap.add_argument('--ids', default='')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--conductor-time-limit', type=int, default=20)
    a = ap.parse_args(argv)

    snap = json.load(open(a.snapshot))
    curves = snap['curves']
    if a.ids:
        want = {int(x) for x in a.ids.split(',')}
        sel = [c for c in curves if c.get('id') in want]
    else:
        sel = curves
    if a.limit:
        sel = sel[:a.limit]

    rows = [compare_curve(c, a.conductor_time_limit) for c in sel]
    done = [r for r in rows if r['status'] == 'compared']

    def frac(key):
        vals = [r[key] for r in done if r.get(key) is not None]
        return {'agree': sum(1 for v in vals if v), 'checked': len(vals)}

    summary = {
        'n_selected': len(sel),
        'n_compared': len(done),
        'n_infrastructure_timeouts': len(rows) - len(done),
        'rank': frac('rank_agrees'),
        'naive_height': frac('naive_height_agrees'),
        'faltings_height': frac('faltings_height_agrees'),
        'conductor': frac('conductor_agrees'),
        'discriminant': frac('discriminant_agrees'),
        'curve_key': frac('curve_key_agrees'),
        'max_naive_height_abs_diff': max((r['naive_height_abs_diff'] for r in done),
                                         default=None),
        'max_faltings_height_abs_diff': max((r['faltings_height_abs_diff'] for r in done),
                                            default=None),
        'rank_disagreements': [r['id'] for r in done if not r['rank_agrees']],
        'conductor_disagreements': [r['id'] for r in done
                                    if r['conductor_agrees'] is False],
    }
    out = {'snapshot': a.snapshot,
           'snapshot_sha256_declared': snap.get('sha256_of_snapshot'),
           'definitions': {
               'naive_height': 'log(max(|c4|^3, c6^2)) of the minimal model',
               'faltings_height': '-1/2 log(covolume of the period lattice of '
                                  'the minimal model)',
               'conductor': 'PARI ellglobalred(E)[1]',
               'rank': 'exact_certify.py lower bound from the board\'s own points',
           },
           'summary': summary, 'rows': rows}
    json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps(summary, indent=1))
    return out


if __name__ == '__main__':
    main()
