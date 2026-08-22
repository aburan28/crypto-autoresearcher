#!/usr/bin/env python3
"""
Within-class independence check: Neron-Tate height regulator.

The Galois-eigenspace argument in verify_certificate.py is exact and needs no
numerics, but it can only certify ONE independent point per twist class d.
When a certificate uses several points on the same twist, those points must be
shown independent by a height argument.  This script computes the Neron-Tate
height pairing matrix of each multi-point class at high precision with PARI and
reports its determinant.

Epistemic status, stated plainly: this is a numerical computation, not exact
algebra.  A determinant many orders of magnitude above the working precision is
the standard certificate of independence used throughout the rank literature,
but it is a strictly weaker artifact than the eigenspace argument, and the
evidence record separates the two bounds accordingly.
"""
import json
import sys
import cypari

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)


def check(cert, precision=64):
    """Return per-class regulator data and the total independent-point count."""
    pari('default(realprecision,%d)' % precision)
    A = int(cert['base_curve']['A'])
    B = int(cert['base_curve']['B'])
    rows = []
    total = 0
    for e in cert['twists']:
        d = int(e['d'])
        pts = e['points']
        if not pts:
            continue
        if len(pts) == 1:
            rows.append({'d': d, 'n_points': 1, 'det': None,
                         'independent': True, 'basis': 'eigenspace'})
            total += 1
            continue
        E = pari('ellinit([0,0,0,%d,%d])' % (A * d * d, B * d * d * d))
        vec = '[' + ','.join('[%s,%s]' % (p[0], p[1]) for p in pts) + ']'
        det = pari('matdet(ellheightmatrix(%s,%s))' % (E, vec))
        detf = float(det)
        indep = abs(detf) > 1e-20
        rows.append({'d': d, 'n_points': len(pts), 'det': repr(det),
                     'det_float': detf, 'independent': bool(indep),
                     'basis': 'height_regulator'})
        total += len(pts) if indep else 1
    return rows, total


if __name__ == '__main__':
    cert = json.load(open(sys.argv[1]))
    rows, total = check(cert)
    bad = [r for r in rows if not r['independent']]
    multi = [r for r in rows if r['n_points'] > 1]
    print('classes with >1 point : %d' % len(multi))
    for r in multi[:12]:
        print('   d=%-8d m=%d  det=%.6g' % (r['d'], r['n_points'], r['det_float']))
    print('singular regulators   : %d' % len(bad))
    print('TOTAL independent points (eigenspace + regulator) = %d' % total)
    sys.exit(1 if bad else 0)
