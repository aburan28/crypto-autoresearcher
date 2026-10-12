#!/usr/bin/env python3
"""Structure of the twelve systems: degrees, bipartition x1/x2, term counts, constants."""
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from msparse import *
root = '..'
files = sorted(glob.glob(root + '/experiments/**/*.ms', recursive=True), key=lambda f: (parse_ms(f)[0], f))
for f in files:
    N, B, R, info = parse_ms(f)
    names = info['names']
    k = N // 2
    h1 = (1 << k) - 1
    ok_names = all(n.startswith('x1_') for n in names[:k]) and all(n.startswith('x2_') for n in names[k:])
    degs = collections.Counter(deg(p) for p in B)
    szs = collections.Counter(bin(m).count('1') for p in B for m in p)
    bil = all((bin(m & h1).count('1') <= 1 and bin(m >> k).count('1') <= 1) for p in B for m in p)
    pure = sum(1 for p in B for m in p if bin(m).count('1') == 2 and (bin(m & h1).count('1') != 1))
    consts = sum(1 for p in B if 0 in p)
    print(os.path.basename(f), 'N=%d k=%d M=%d(nonfield) fieldlines=%d' % (N, k, len(B), info['n_field_lines']),
          'names x1|x2 ok' if ok_names else 'NAMES UNEXPECTED', 'degs', dict(degs), 'monomial sizes', dict(szs),
          'bilinear-in-halves' if bil else 'NOT-BILINEAR', 'sq-in-same-half', pure, 'with-const', consts, 'terms/poly avg %.0f' % (sum(len(p) for p in B)/len(B)))
