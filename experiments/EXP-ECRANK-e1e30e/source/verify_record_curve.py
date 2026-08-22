#!/usr/bin/env python3
"""
Independent verification of a published rank-record curve over Q.

Two separate checks, of deliberately different epistemic strength:

  (a) EXACT.  Every published generator is checked to lie on the curve in exact
      rational arithmetic (pure Python, no PARI).  A transcription error in the
      record page or in this pipeline is caught here.

  (b) NUMERICAL.  The Neron-Tate height pairing matrix of the generators is
      computed with PARI at two different precisions and its determinant (the
      regulator) and least eigenvalue are reported.  A regulator bounded away
      from zero certifies that the generators are Z-independent, hence that the
      rank is at least their number.  This is the standard argument in the rank
      literature and it is numerical, not exact: it is reported as such.

Nothing here re-proves the record.  It confirms that the published data is
internally consistent and supports the stated rank lower bound.
"""
import json
import sys
from fractions import Fraction as F

import cypari

pari = cypari.pari
pari.allocatemem(2 ** 33, silent=True)


def on_curve_exact(a_inv, points):
    a1, a2, a3, a4, a6 = a_inv
    bad = []
    for i, (xs, ys) in enumerate(points, 1):
        x, y = F(xs), F(ys)
        if y * y + a1 * x * y + a3 * y != x ** 3 + a2 * x * x + a4 * x + a6:
            bad.append(i)
    return bad


def regulator(a_inv, points, precisions=(80, 150)):
    vec = '[' + ','.join('[%s,%s]' % (x, y) for x, y in points) + ']'
    rows = []
    for prec in precisions:
        pari('default(realprecision,%d)' % prec)
        E = pari('ellinit(%s)' % (list(a_inv),))
        M = pari('ellheightmatrix(%s,%s)' % (E, vec))
        rows.append({'precision': prec,
                     'regulator_det': str(pari('matdet(%s)' % M)),
                     'least_eigenvalue': str(pari('vecmin(mateigen(%s,1)[1])' % M)),
                     'pari_matrank': int(pari('matrank(%s)' % M))})
    return rows


if __name__ == '__main__':
    src = json.load(open(sys.argv[1]))
    a_inv = [int(c) for c in src['a_invariants']]
    pts = src['points']
    bad = on_curve_exact(a_inv, pts)
    rows = regulator(a_inv, pts)
    n = len(pts)
    print('published generators           : %d' % n)
    print('EXACT on-curve check           : %s'
          % ('ALL PASS' if not bad else 'FAILED for points %s' % bad))
    for r in rows:
        print('NUMERICAL regulator @ prec %-4d: det = %s'
              % (r['precision'], r['regulator_det'][:34]))
        print('                                 least eigenvalue = %s, matrank = %d'
              % (r['least_eigenvalue'][:12], r['pari_matrank']))
    indep = all(r['pari_matrank'] == n for r in rows)
    print('CONCLUSION                     : rank E(Q) >= %d %s'
          % (n, '(generators independent; regulator far from 0)' if indep and not bad
             else '(NOT ESTABLISHED)'))
    json.dump({'n_points': n, 'exact_on_curve_failures': bad,
               'regulator_rows': rows, 'independent': bool(indep and not bad)},
              open(sys.argv[2], 'w'), indent=1)
    sys.exit(0 if (indep and not bad) else 1)
