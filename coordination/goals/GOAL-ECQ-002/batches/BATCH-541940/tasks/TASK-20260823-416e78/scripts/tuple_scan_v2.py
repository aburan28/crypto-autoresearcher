#!/usr/bin/env python3
"""
TUPLE-SPACE scan, corrected version.  Supersedes tuple_scan.py, which
RUN-ECQTUP-416e78-002 used and which silently truncated the 99% of tuples
whose r is a QUINTIC (genus 2) to a quartic.  That run is superseded as
invalid_measurement; this one refuses any family with deg_x r != 4.

Two exact symmetries are quotiented out before enumeration (translation
a_i -> a_i + c, and simultaneous scaling a_i -> L a_i, T -> L T), and
reflection a_i -> M - a_i is normalised lexicographically.

Families are ranked by MEASURED ENVELOPE, never by generic rank.  The null
ladder is produced by null_ladder.py and merged by build_deliverables.py.

usage: tuple_scan_v2.py OUT.json [--exhaustive-max 56] [--large-lo 57]
       [--large-hi 400] [--n-large-tested 400000] [--time-budget 900]
"""
import argparse
import itertools
import json
import math
import random
import sys
import time

import measure
from admissible import phi_int

PUBLISHED = {
    'MESTRE-PUBLISHED-A': (-17, -16, 10, 11, 14, 17),
    'MESTRE-PUBLISHED-B': (399, 380, 352, 47, 4, 0),
}


def canonical(tup):
    e = sorted(tup)
    e = [x - e[0] for x in e]
    g = 0
    for x in e:
        g = math.gcd(g, x)
    if g > 1:
        e = [x // g for x in e]
    m = e[-1]
    return tuple(min(e, sorted(m - x for x in e)))


def enumerate_admissible(mmax, mmin=5):
    seen = set()
    out = []
    tested = 0
    for m in range(mmin, mmax + 1):
        for mid in itertools.combinations(range(1, m), 4):
            tested += 1
            t = (0,) + mid + (m,)
            if math.gcd(math.gcd(math.gcd(math.gcd(mid[0], mid[1]), mid[2]),
                                 mid[3]), m) != 1:
                continue
            if phi_int(t):
                continue
            c = canonical(t)
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
    return out, tested, seen


def sample_admissible(lo, hi, n_tested, rng, seen):
    out = []
    for _ in range(n_tested):
        m = rng.randint(lo, hi)
        mid = tuple(sorted(rng.sample(range(1, m), 4)))
        t = (0,) + mid + (m,)
        if phi_int(t):
            continue
        c = canonical(t)
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--exhaustive-max', type=int, default=56)
    ap.add_argument('--exhaustive-min', type=int, default=5)
    ap.add_argument('--large-lo', type=int, default=57)
    ap.add_argument('--large-hi', type=int, default=400)
    ap.add_argument('--n-large-tested', type=int, default=400000)
    ap.add_argument('--seed', type=int, default=20260823)
    ap.add_argument('--time-budget', type=float, default=900.0)
    a = ap.parse_args(argv)
    rng = random.Random(a.seed)

    t_enum = time.time()
    ex, tested, seen = enumerate_admissible(a.exhaustive_max, a.exhaustive_min)
    lg = sample_admissible(a.large_lo, a.large_hi, a.n_large_tested, rng, seen)
    t_enum = time.time() - t_enum

    work = ([('published', tuple(sorted(t)), nm) for nm, t in PUBLISHED.items()]
            + [('admissible_exhaustive_spread_%d_%d' % (a.exhaustive_min, a.exhaustive_max), t, None)
               for t in ex]
            + [('admissible_sampled_spread_%d_%d' % (a.large_lo, a.large_hi), t, None)
               for t in lg])

    t0 = time.time()
    rows, failures, refused = [], [], []
    budget_hit = False
    for stratum, t, nm in work:
        if time.time() - t0 > a.time_budget:
            budget_hit = True
            break
        try:
            fam = measure.family_from_tuple(t, name=nm)
            if fam.deg_x_r != 4:
                refused.append({'tuple': list(t), 'stratum': stratum,
                                'deg_x_r': fam.deg_x_r,
                                'reason': 'not a genus-1 quartic family'})
                continue
            r = measure.measure(fam)
            r['stratum'] = stratum
            r['canonical_tuple'] = list(canonical(t))
            rows.append(r)
        except BaseException as e:
            failures.append({'tuple': list(t), 'stratum': stratum,
                             'error': '%s: %s' % (type(e).__name__, e)})

    ok = [r for r in rows if r.get('status') == 'measured']
    ok.sort(key=lambda r: r['measured_envelope_min_naive_height'])
    out = {
        'what': 'tuple-space scan of ADMISSIBLE Mestre families (deg_x r = 4), '
                'ranked by MEASURED ENVELOPE over the declared T-box',
        'task_id': 'TASK-20260823-416e78',
        'hypothesis_id': 'H-ECQ-8b600d',
        'supersedes_run': 'RUN-ECQTUP-416e78-002 (invalid_measurement: quintic '
                          'families were silently truncated to quartics)',
        't_box': measure.T_BOX_DESC,
        'n_t_values': len(measure.T_BOX),
        'seed': a.seed,
        'admissibility': {
            'condition': 'deg_x r = 4, equivalently 12*sum(c^5) = '
                         '5*sum(c^2)*sum(c^3) with c_i = 6 a_i - sum(a)',
            'checked_symbolically_per_family': True,
            'n_tuples_tested_exhaustive': tested,
            'n_admissible_exhaustive': len(ex),
            'admissible_fraction_exhaustive': len(ex) / tested if tested else None,
            'n_tuples_tested_large_sample': a.n_large_tested,
            'n_admissible_large_sample': len(lg),
            'enumeration_seconds': t_enum,
        },
        'n_families_attempted': len(rows) + len(failures) + len(refused),
        'n_families_measured': len(ok),
        'n_refused_not_quartic': len(refused),
        'n_family_failures': len(failures),
        'time_budget_seconds': a.time_budget,
        'time_budget_reached_before_full_enumeration': budget_hit,
        'wall_clock_seconds': time.time() - t0,
        'failures': failures,
        'refused': refused[:50],
        'families': ok,
    }
    json.dump(out, open(a.out, 'w'), indent=1)
    print('enumerated %d admissible (exhaustive, %d tested) + %d (sampled) in %.1fs'
          % (len(ex), tested, len(lg), t_enum))
    print('measured %d families in %.1fs (refused %d, failures %d, budget hit %s)'
          % (len(ok), out['wall_clock_seconds'], len(refused), len(failures),
             budget_hit))
    for r in ok[:30]:
        f = r.get('two_arm_fit') or {}
        print('%-40s env=%9.4f flat a=%8.3f b=%6.2f steep b=%6.2f d=%s ST<=%s'
              % (r['family'], r['measured_envelope_min_naive_height'],
                 f.get('flat_arm', {}).get('intercept', float('nan')),
                 f.get('flat_arm', {}).get('slope', float('nan')),
                 f.get('steep_arm', {}).get('slope', float('nan')),
                 (r.get('surface') or {}).get('surface_degree_d'),
                 (r.get('surface') or {}).get('shioda_tate_ceiling')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
