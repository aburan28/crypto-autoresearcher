#!/usr/bin/env python3
"""
CHECK 2 (cheap falsifier of the mechanism in H-ECQ-d60d07).

H-ECQ-d60d07 says: a base family of high generic rank can be specialised at
SMALL rational parameters, and that keeps the minimal model -- hence the naive
height -- SMALL.  The falsification criterion it declares is:

    "FALSIFIED for the mechanism if specialising at small parameters does NOT
     keep the height low -- i.e. if minimal models of small-parameter
     specialisations are not small."

Operationalisation, fixed here before the numbers are read:

  For each family and each parameter point t of a box, measure
      X(t) = log H(t),  H(t) = max(|num(t)|, den(t))   ("parameter size")
      Y(t) = naive height of the MINIMAL model of the specialisation.
  Fit Y = a + b X by least squares and report (a, b, R^2), plus min/median Y.

  MECHANISM SURVIVES the check if Y grows at most linearly in X (i.e. only
  LOGARITHMICALLY in the parameter itself) with a finite slope, so that
  shrinking the parameter is an effective lever on the height.
  MECHANISM IS FALSIFIED if Y is essentially independent of X (the family's own
  constants dominate and the lever does nothing) or grows faster than linearly
  in X.

  Separately -- and this is a LEVEL question, not a MECHANISM question -- the
  measured (a, b) give the parameter budget available under a target height
  h_max:   X <= (h_max - a) / b.  Reported for h_max = 118.770, the frozen
  minimum naive height over rank >= 15 curves on the ICARM snapshot.

usage: python3 falsifier_height.py OUT.json FAMILY.json [FAMILY.json ...]
       [--num-max 40] [--den-max 3] [--target-height 118.770]
"""
import argparse
import json
import math
import statistics
import sys

import exact_certify
import icarm_invariants as inv
from families import Family, parameter_box


def fit(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    b = sxy / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return {'intercept': a, 'slope': b,
            'r_squared': (1 - ss_res / ss_tot) if ss_tot else None,
            'n': n}


def measure_family(path, num_max, den_max, target_height, time_limit=20):
    fam = Family.load(path)
    box = {fam.params[0]: {'num_min': -num_max, 'num_max': num_max,
                           'den_max': den_max}}
    for p in fam.params[1:]:
        box[p] = {'num_min': -3, 'num_max': 3, 'den_max': 1}
    pts = parameter_box(box)
    rows = []
    for v in pts:
        sp = fam.specialise(v)
        if sp is None or exact_certify.discriminant(sp['a_invariants']) == 0:
            continue
        try:
            m = inv.invariants(sp['a_invariants'], time_limit=time_limit,
                               want_conductor=False)
        except inv.InvariantTimeout as e:
            rows.append({'params': {k: str(x) for k, x in v.items()},
                         'status': 'infrastructure_timeout', 'note': str(e)})
            continue
        H = max(max(abs(x.numerator), x.denominator) for x in v.values())
        rows.append({'params': {k: str(x) for k, x in v.items()},
                     'status': 'measured',
                     'param_size_H': H,
                     'log_param_size': math.log(H),
                     'naive_height': m['naive_height'],
                     'faltings_height': m['faltings_height'],
                     'n_digits_a4': len(str(abs(sp['a_invariants'][3]))),
                     'n_digits_a6': len(str(abs(sp['a_invariants'][4])))})
    ok = [r for r in rows if r['status'] == 'measured']
    xs = [r['log_param_size'] for r in ok]
    ys = [r['naive_height'] for r in ok]
    f = fit(xs, ys)
    out = {
        'family': fam.name,
        'family_source': fam.source,
        'claimed_generic_rank': fam.claimed_generic_rank,
        'box': box,
        'n_points_measured': len(ok),
        'n_infrastructure_timeouts': len(rows) - len(ok),
        'min_naive_height': min(ys) if ys else None,
        'median_naive_height': statistics.median(ys) if ys else None,
        'max_naive_height': max(ys) if ys else None,
        'naive_height_at_smallest_params': [
            {'param_size_H': r['param_size_H'], 'naive_height': r['naive_height'],
             'params': r['params']}
            for r in sorted(ok, key=lambda r: (r['param_size_H'],
                                               r['naive_height']))[:5]],
        'fit_naive_height_vs_log_param_size': f,
        'rows': rows,
    }
    if f and f['slope'] > 0:
        budget = (target_height - f['intercept']) / f['slope']
        out['parameter_budget_under_target'] = {
            'target_naive_height': target_height,
            'max_log_param_size': budget,
            'max_param_size': math.exp(budget) if budget < 700 else float('inf'),
        }
    out['height_lever_effective'] = bool(
        f and f['slope'] > 0.5 and (f['r_squared'] or 0) > 0.5)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('families', nargs='+')
    ap.add_argument('--num-max', type=int, default=40)
    ap.add_argument('--den-max', type=int, default=3)
    ap.add_argument('--target-height', type=float, default=118.770)
    a = ap.parse_args(argv)
    res = [measure_family(p, a.num_max, a.den_max, a.target_height)
           for p in a.families]
    out = {'target_naive_height': a.target_height,
           'target_source': 'frontier_20260823.json, min naive height over '
                            'rank >= 15 curves (pre-registered)',
           'families': res}
    json.dump(out, open(a.out, 'w'), indent=1)
    for r in res:
        f = r['fit_naive_height_vs_log_param_size'] or {}
        print('%-22s n=%3d  min h=%8.3f  median h=%8.3f  '
              'fit h = %.3f + %.3f*log H  (R^2=%.4f)  lever_effective=%s'
              % (r['family'], r['n_points_measured'], r['min_naive_height'] or -1,
                 r['median_naive_height'] or -1, f.get('intercept', float('nan')),
                 f.get('slope', float('nan')), f.get('r_squared') or float('nan'),
                 r['height_lever_effective']))
    return out


if __name__ == '__main__':
    main()
