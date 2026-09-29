#!/usr/bin/env python3
"""
Rank SEARCH over the scanned fibres, followed by EXACT certification.

PARI `ellrank` is used here ONLY as a search for points (and, when it returns
r_low = r_high, as an independent upper bound worth recording).  It never
supplies a rank this task reports: every rank reported is re-derived by
`exact_certify.py` from the exhibited points, in exact arithmetic, with no
PARI in the loop.  A PARI alarm is an INFRASTRUCTURE outcome and is recorded
as one.

usage: search_rank.py SCAN.json OUT.json [--max-families 400]
       [--t-per-family 12] [--height-cap 100] [--alarm 20] [--time-budget 600]
"""
import argparse
import json
import math
import sys
import time
from fractions import Fraction as F

import cypari

import measure
import exact_certify as ec
from certify_candidates import to_minimal, naive_height

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)   # 2 GB, inside the 4 GB task cap


def search_fibre(fam, t0, alarm):
    quart = fam.quartic_at(t0)
    secs = fam.sections_at(t0)
    mp = measure.measure_points(t0, quart, secs)
    if mp is None:
        return None
    ai, pts = mp
    tm = to_minimal(ai, pts)
    if tm is None:
        return None
    mai, mpts, chg = tm
    h, c4, c6 = naive_height(mai)
    row = {'t': str(t0), 'minimal_a_invariants': mai, 'naive_height': h,
           'curve_key': '%d:%d' % (c4, c6),
           'n_section_points': len(mpts)}
    extra = []
    try:
        res = pari('alarm(%d, ellrank(ellinit(%s)))' % (alarm, mai))
        row['pari_ellrank_r_low'] = int(res[0])
        row['pari_ellrank_r_high'] = int(res[1])
        row['pari_ellrank_status'] = 'ok'
        for P in res[3]:
            try:
                x = F(str(pari('%s[1]' % P)))
                y = F(str(pari('%s[2]' % P)))
            except BaseException:
                continue
            extra.append((x, y))
    except BaseException as e:
        row['pari_ellrank_status'] = ('infrastructure_outcome: %s'
                                      % type(e).__name__)
    allpts = list(mpts) + [p for p in extra if p not in mpts]
    allpts = [p for p in allpts
              if ec.on_curve(ec.Qfield(), [F(a) for a in mai], p)]
    cert = ec.certify(mai, [[str(x), str(y)] for x, y in allpts],
                      max_prime=6000, max_good_primes=150,
                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
    row['n_points_submitted_to_certifier'] = len(allpts)
    row['certified_rank_lower_bound'] = cert['certified_rank_lower_bound']
    row['torsion_bound'] = cert.get('torsion_bound')
    row['independence'] = {k: v for k, v in (cert.get('independence') or {}).items()
                           if k in ('l', 'primes_used', 'stacked_matrix_Fl_rank')}
    row['points'] = [[str(x), str(y)] for x, y in allpts]
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('scan')
    ap.add_argument('out')
    ap.add_argument('--max-families', type=int, default=400)
    ap.add_argument('--only-min-ceiling', type=int, default=None,
                    help='restrict to families whose OWN Shioda-Tate '
                         'ceiling is at least this')
    ap.add_argument('--t-per-family', type=int, default=12)
    ap.add_argument('--height-cap', type=float, default=100.0)
    ap.add_argument('--alarm', type=int, default=20)
    ap.add_argument('--time-budget', type=float, default=600.0)
    a = ap.parse_args(argv)

    scan = json.load(open(a.scan))
    fams = sorted(scan['families'],
                  key=lambda f: f['measured_envelope_min_naive_height'])
    if a.only_min_ceiling is not None:
        fams = [f for f in fams
                if (f.get('surface') or {}).get('shioda_tate_ceiling') is not None
                and f['surface']['shioda_tate_ceiling'] >= a.only_min_ceiling]
    sel = fams[:a.max_families]
    have = {f['family'] for f in sel}
    # every family whose OWN ceiling admits rank >= 12 is searched, whatever its
    # envelope rank: the cell claim needs rank, and the low-envelope families
    # are exactly the ones whose ceilings forbid it
    for f in fams:
        c = (f.get('surface') or {}).get('shioda_tate_ceiling')
        if c is not None and c >= 12 and f['family'] not in have:
            sel.append(f)
            have.add(f['family'])
    fams = sel
    t0 = time.time()
    rows = []
    budget_hit = False
    n_alarm = 0
    for f in fams:
        if time.time() - t0 > a.time_budget:
            budget_hit = True
            break
        fam = measure.family_from_tuple(f['tuple'], name=f['family'])
        ts = sorted(f['lower_envelope_points'], key=lambda r: r['naive_height'])
        ts = [r for r in ts if r['naive_height'] <= a.height_cap][:a.t_per_family]
        for r in ts:
            if time.time() - t0 > a.time_budget:
                budget_hit = True
                break
            try:
                row = search_fibre(fam, F(r['t']), a.alarm)
            except BaseException as e:
                rows.append({'family': f['family'], 't': r['t'],
                             'error': '%s: %s' % (type(e).__name__, e)})
                continue
            if row is None:
                continue
            row['family'] = f['family']
            row['tuple'] = f['tuple']
            row['shioda_tate_ceiling'] = f['surface']['shioda_tate_ceiling']
            row['content_P2'] = f['content_P2']
            if row.get('pari_ellrank_status', '').startswith('infrastructure'):
                n_alarm += 1
            rows.append(row)

    good = [r for r in rows if 'certified_rank_lower_bound' in r]
    pareto = {}
    for k in range(1, 16):
        c = [r for r in good if r['certified_rank_lower_bound'] >= k]
        if c:
            b = min(c, key=lambda r: r['naive_height'])
            pareto[str(k)] = {'min_naive_height': b['naive_height'],
                              'family': b['family'], 't': b['t'],
                              'curve_key': b['curve_key'],
                              'n_curves_at_or_above': len(c)}
    out = {
        'what': 'PARI ellrank used as a point SEARCH; every reported rank '
                're-derived by exact_certify.py from the exhibited points',
        'task_id': 'TASK-20260823-416e78',
        'n_fibres_searched': len(rows),
        'n_fibres_certified': len(good),
        'n_pari_alarms_infrastructure': n_alarm,
        'time_budget_reached': budget_hit,
        'wall_clock_seconds': time.time() - t0,
        'certified_rank_vs_height_pareto': pareto,
        'fibres': rows,
    }
    json.dump(out, open(a.out, 'w'), indent=1)
    print('searched %d fibres in %.1fs (alarms %d, budget hit %s)'
          % (len(rows), out['wall_clock_seconds'], n_alarm, budget_hit))
    for k in sorted(pareto, key=int):
        p = pareto[k]
        print('certified rank >= %2s : min naive height %9.4f  (%s, t=%s, n=%d)'
              % (k, p['min_naive_height'], p['family'], p['t'],
                 p['n_curves_at_or_above']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
