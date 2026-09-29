#!/usr/bin/env python3
"""
TUPLE-SPACE scan for H-ECQ-8b600d.

Regenerates Mestre's construction over many integer 6-tuples and measures each
family's lower envelope of minimal-model naive height.  Families are ranked by
MEASURED ENVELOPE, never by generic rank.

Canonical form.  Two exact symmetries of the construction are quotiented out
before enumeration, so the scan does not spend its budget on relabelled copies:

  * TRANSLATION.  a_i -> a_i + c sends q(x) -> q(x-c), p -> p(x-c),
    g -> g(x-c), r -> r(x-c); the curve at every T is unchanged.  Normalised
    by min(a_i) = 0.
  * SCALING.  a_i -> L a_i together with T -> L T sends r(x,T) -> L^12 r(x/L,T),
    and (x,y) -> (L x, L^6 y) is an isomorphism.  So a non-primitive tuple is
    a primitive tuple at a rescaled parameter, already inside the T-box.
    Normalised by gcd(a_i) = 1.
  * REFLECTION.  a_i -> M - a_i is x -> -x.  Normalised lexicographically.

usage: tuple_scan.py OUT.json [--exhaustive-max 16] [--sampled-max 40]
                     [--n-sampled 6000] [--seed 20260823] [--time-budget 900]
"""
import argparse
import itertools
import json
import math
import os
import random
import sys
import time

import measure


def canonical(tup):
    e = sorted(tup)
    e = [x - e[0] for x in e]
    g = 0
    for x in e:
        g = math.gcd(g, x)
    if g > 1:
        e = [x // g for x in e]
    m = e[-1]
    refl = sorted(m - x for x in e)
    return tuple(min(e, refl))


def enumerate_exhaustive(mmax):
    out = set()
    for m in range(5, mmax + 1):
        for mid in itertools.combinations(range(1, m), 4):
            out.add(canonical((0,) + mid + (m,)))
    return out


def sample_large(mlo, mhi, n, rng, seen):
    out = set()
    tries = 0
    while len(out) < n and tries < 60 * n:
        tries += 1
        m = rng.randint(mlo, mhi)
        mid = rng.sample(range(1, m), 4)
        c = canonical((0,) + tuple(mid) + (m,))
        if c not in seen:
            out.add(c)
    return out


PUBLISHED = {
    'MESTRE-PUBLISHED-A': (-17, -16, 10, 11, 14, 17),
    'MESTRE-PUBLISHED-B': (399, 380, 352, 47, 4, 0),
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--exhaustive-max', type=int, default=16)
    ap.add_argument('--sampled-max', type=int, default=40)
    ap.add_argument('--n-sampled', type=int, default=6000)
    ap.add_argument('--extra-strata', default='41:120:1500,121:400:1000',
                    help='lo:hi:n, comma separated; wider-spread samples so '
                         'that the envelope-vs-tuple-size trend is measured '
                         'rather than assumed from the small-spread stratum')
    ap.add_argument('--seed', type=int, default=20260823)
    ap.add_argument('--time-budget', type=float, default=900.0)
    a = ap.parse_args(argv)

    rng = random.Random(a.seed)
    ex = enumerate_exhaustive(a.exhaustive_max)
    sm = sample_large(a.exhaustive_max + 1, a.sampled_max, a.n_sampled, rng, ex)
    strata = ([('exhaustive_spread_le_%d' % a.exhaustive_max, t) for t in sorted(ex)]
              + [('sampled_spread_%d_%d' % (a.exhaustive_max + 1, a.sampled_max), t)
                 for t in sorted(sm)])
    extra_desc = []
    seen = set(ex) | set(sm)
    for spec in [z for z in a.extra_strata.split(',') if z.strip()]:
        lo, hi, n = (int(z) for z in spec.split(':'))
        s2 = sample_large(lo, hi, n, rng, seen)
        seen |= s2
        nm = 'sampled_spread_%d_%d' % (lo, hi)
        extra_desc.append('%s: %d drawn' % (nm, len(s2)))
        strata += [(nm, t) for t in sorted(s2)]
    pub = []
    for name, t in PUBLISHED.items():
        pub.append(('published', tuple(sorted(t)), name))

    t0 = time.time()
    rows = []
    failures = []
    # published tuples are measured FIRST and in their published (uncanonicalised)
    # form, so that the reproduction of the BATCH-f2341e validator's ~79.6 for
    # tuple A is not conditioned on the canonicalisation being right
    for _, t, name in pub:
        try:
            fam = measure.family_from_tuple(t, name=name)
            r = measure.measure(fam)
            r['stratum'] = 'published'
            r['canonical_tuple'] = list(canonical(t))
            rows.append(r)
        except BaseException as e:
            failures.append({'tuple': list(t), 'stratum': 'published',
                             'error': '%s: %s' % (type(e).__name__, e)})

    budget_hit = False
    for stratum, t in strata:
        if time.time() - t0 > a.time_budget:
            budget_hit = True
            break
        try:
            fam = measure.family_from_tuple(t)
            r = measure.measure(fam)
            r['stratum'] = stratum
            rows.append(r)
        except BaseException as e:
            failures.append({'tuple': list(t), 'stratum': stratum,
                             'error': '%s: %s' % (type(e).__name__, e)})

    ok = [r for r in rows if r.get('status') == 'measured']
    ok.sort(key=lambda r: r['measured_envelope_min_naive_height'])
    out = {
        'what': 'tuple-space scan of Mestre families, ranked by MEASURED '
                'ENVELOPE (min minimal-model naive height over the declared '
                'T-box), never by generic rank',
        'task_id': 'TASK-20260823-416e78',
        'hypothesis_id': 'H-ECQ-8b600d',
        't_box': measure.T_BOX_DESC,
        'n_t_values': len(measure.T_BOX),
        'seed': a.seed,
        'strata': {
            'exhaustive': 'every canonical tuple with spread <= %d (%d tuples)'
                          % (a.exhaustive_max, len(ex)),
            'sampled': 'uniform sample of canonical tuples with spread in '
                       '[%d, %d] (%d drawn, seed %d)'
                       % (a.exhaustive_max + 1, a.sampled_max, len(sm), a.seed),
            'published': list(PUBLISHED),
            'extra_sampled': extra_desc,
        },
        'n_families_attempted': len(rows) + len(failures),
        'n_families_measured': len(ok),
        'n_family_failures': len(failures),
        'time_budget_seconds': a.time_budget,
        'time_budget_reached_before_full_enumeration': budget_hit,
        'wall_clock_seconds': time.time() - t0,
        'failures': failures,
        'families': ok,
    }
    json.dump(out, open(a.out, 'w'), indent=1)
    print('measured %d families in %.1fs (failures %d, budget hit %s)'
          % (len(ok), out['wall_clock_seconds'], len(failures), budget_hit))
    for r in ok[:25]:
        f = r.get('two_arm_fit') or {}
        fa = f.get('flat_arm', {})
        sa = f.get('steep_arm', {})
        print('%-46s env=%9.4f  flat a=%8.3f b=%6.3f  steep b=%6.3f  d=%s  ST<=%s'
              % (r['family'], r['measured_envelope_min_naive_height'],
                 fa.get('intercept', float('nan')), fa.get('slope', float('nan')),
                 sa.get('slope', float('nan')),
                 (r.get('surface') or {}).get('surface_degree_d'),
                 (r.get('surface') or {}).get('shioda_tate_ceiling')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
