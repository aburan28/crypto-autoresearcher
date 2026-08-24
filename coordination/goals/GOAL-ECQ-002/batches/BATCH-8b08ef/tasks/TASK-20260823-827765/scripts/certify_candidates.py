#!/usr/bin/env python3
"""
Certify rank LOWER BOUNDS by exhibited points in exact arithmetic, for the
families the envelope scan ranks best.

Every rank reported anywhere in this task comes from here.  The certifier is
`exact_certify.py`, taken UNCHANGED from the BATCH-f2341e pipeline: stdlib
only, no floating point, no PARI, no analytic rank, no Selmer bound.  It is
independent of the code that produced the points (this file), which is the
point of using it.

Two controls are run alongside:
  * LOW-CEILING CONTROL.  The families with the very lowest measured envelopes
    have low Shioda-Tate ceilings.  They are certified too, so that "a small
    curve with no rank" is visible in the record rather than inferred.
  * The minimal model is recomputed by PARI and the points are transported to
    it; each transported point is re-checked on the minimal model in exact
    rational arithmetic before it is written out.

usage: certify_candidates.py SCAN.json OUT.json [--min-ceiling 12]
       [--max-families 60] [--height-cap 95] [--time-budget 600]
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

pari = cypari.pari


def to_minimal(ai, pts):
    """Transport (ai, pts) to the PARI-minimal model; verify exactly."""
    r = pari('my(v); E=ellminimalmodel(ellinit(%s),&v); [E[1..5], v]'
             % ([int(x) for x in ai],))
    mai = [int(x) for x in r[0]]
    u, rr, s, t = [F(str(x)) for x in r[1]]
    out = []
    for x, y in pts:
        x, y = F(x), F(y)
        X = (x - rr) / u ** 2
        Y = (y - s * (x - rr) - t) / u ** 3
        if not ec.on_curve(ec.Qfield(), [F(a) for a in mai], (X, Y)):
            return None
        out.append((X, Y))
    return mai, out, [str(u), str(rr), str(s), str(t)]


def naive_height(mai):
    E = pari('ellinit(%s)' % (mai,))
    c4 = int(pari('%s.c4' % E))
    c6 = int(pari('%s.c6' % E))
    return math.log(max(abs(c4) ** 3, c6 * c6)), c4, c6


def certify_fibre(fam, t0, max_prime=6000, max_good_primes=150):
    quart = fam.quartic_at(t0)
    secs = fam.sections_at(t0)
    mp = measure.measure_points(t0, quart, secs)
    if mp is None:
        return None
    ai, pts = mp
    cert = ec.certify(ai, [[str(x), str(y)] for x, y in pts],
                      max_prime=max_prime, max_good_primes=max_good_primes,
                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
    tm = to_minimal(ai, pts)
    if tm is None:
        return None
    mai, mpts, chg = tm
    h, c4, c6 = naive_height(mai)
    return {
        't': str(t0),
        'n_points_exhibited': len(pts),
        'certified_rank_lower_bound': cert['certified_rank_lower_bound'],
        'torsion_bound': cert.get('torsion_bound'),
        'independence_l': (cert.get('independence') or {}).get('l'),
        'independence_primes_used': (cert.get('independence') or {}).get('primes_used'),
        'on_curve_failures': cert.get('on_curve_failures'),
        'minimal_a_invariants': mai,
        'change_of_variable_u_r_s_t': chg,
        'c4': str(c4), 'c6': str(c6),
        'curve_key': '%d:%d' % (c4, c6),
        'naive_height': h,
        'points_on_minimal_model': [[str(x), str(y)] for x, y in mpts],
        'independent_point_indices': (cert.get('independence') or {}).get(
            'independent_point_indices'),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('scan')
    ap.add_argument('out')
    ap.add_argument('--min-ceiling', type=int, default=12)
    ap.add_argument('--max-families', type=int, default=60)
    ap.add_argument('--height-cap', type=float, default=95.0)
    ap.add_argument('--max-t-per-family', type=int, default=20)
    ap.add_argument('--time-budget', type=float, default=600.0)
    a = ap.parse_args(argv)

    scan = json.load(open(a.scan))
    fams = scan['families']
    hi = [f for f in fams
          if (f.get('surface') or {}).get('shioda_tate_ceiling') is not None
          and f['surface']['shioda_tate_ceiling'] >= a.min_ceiling]
    hi.sort(key=lambda f: f['measured_envelope_min_naive_height'])
    hi = hi[:a.max_families]
    lowctl = [f for f in fams
              if (f.get('surface') or {}).get('shioda_tate_ceiling') is not None
              and f['surface']['shioda_tate_ceiling'] < a.min_ceiling]
    lowctl.sort(key=lambda f: f['measured_envelope_min_naive_height'])
    lowctl = lowctl[:12]

    t0 = time.time()
    results = []
    budget_hit = False
    for group, fl in (('candidate', hi), ('low_ceiling_control', lowctl)):
        for f in fl:
            if time.time() - t0 > a.time_budget:
                budget_hit = True
                break
            fam = measure.family_from_tuple(f['tuple'], name=f['family'])
            rows = sorted((r for r in f['lower_envelope_points']),
                          key=lambda r: r['naive_height'])
            rows = [r for r in rows if r['naive_height'] <= a.height_cap]
            rows = rows[:a.max_t_per_family]
            per = []
            for r in rows:
                if time.time() - t0 > a.time_budget:
                    budget_hit = True
                    break
                try:
                    c = certify_fibre(fam, F(r['t']))
                except BaseException as e:
                    per.append({'t': r['t'], 'error': '%s: %s'
                                % (type(e).__name__, e)})
                    continue
                if c:
                    per.append(c)
            if not per:
                continue
            good = [c for c in per if 'certified_rank_lower_bound' in c]
            best_rank = max((c['certified_rank_lower_bound'] for c in good),
                            default=0)
            results.append({
                'family': f['family'],
                'group': group,
                'tuple': f['tuple'],
                'stratum': f.get('stratum'),
                'content_P2': f['content_P2'],
                'shioda_tate_ceiling': f['surface']['shioda_tate_ceiling'],
                'surface_degree_d': f['surface']['surface_degree_d'],
                'measured_envelope_min_naive_height':
                    f['measured_envelope_min_naive_height'],
                'max_certified_rank_over_tested_t': best_rank,
                'best_height_at_certified_rank': {
                    str(k): min((c['naive_height'] for c in good
                                 if c['certified_rank_lower_bound'] >= k),
                                default=None)
                    for k in range(8, 14)},
                'fibres': per,
            })

    out = {
        'what': 'certified rank lower bounds from exhibited sections, exact '
                'arithmetic, for the best-envelope families and a '
                'low-ceiling control',
        'task_id': 'TASK-20260823-416e78',
        'certifier': 'exact_certify.py from the BATCH-f2341e pipeline, unchanged',
        'scan_source': a.scan,
        'min_ceiling': a.min_ceiling,
        'height_cap': a.height_cap,
        'time_budget_seconds': a.time_budget,
        'time_budget_reached': budget_hit,
        'wall_clock_seconds': time.time() - t0,
        'families': results,
    }
    json.dump(out, open(a.out, 'w'), indent=1)
    print('certified %d families in %.1fs (budget hit %s)'
          % (len(results), out['wall_clock_seconds'], budget_hit))
    for r in sorted(results, key=lambda r: -r['max_certified_rank_over_tested_t']):
        b = r['best_height_at_certified_rank']
        print('%-36s %-20s ST<=%2s env=%8.3f maxcert=%2d  h@r>=11=%s h@r>=12=%s'
              % (r['family'], r['group'], r['shioda_tate_ceiling'],
                 r['measured_envelope_min_naive_height'],
                 r['max_certified_rank_over_tested_t'],
                 ('%.3f' % b['11']) if b['11'] else '-',
                 ('%.3f' % b['12']) if b['12'] else '-'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
