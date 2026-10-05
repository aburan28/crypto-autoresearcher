#!/usr/bin/env python3
"""Convert a .ms file (via msparse) to the plain mask-list format read by the C programs.
Line 1: 'N M'; then M lines 't m1 ... mt' (decimal monomial bitmasks, bit j-1 = x_j).
Field-equation lines (x^2+x) are the zero polynomial in B and are dropped; --keep-field keeps them as empty polys."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from msparse import *
src, dst = sys.argv[1], sys.argv[2]
keep = '--keep-field' in sys.argv
N, B, R, info = parse_ms(src, drop_field_lines=not keep)
with open(dst, 'w') as f:
    f.write('%d %d\n' % (N, len(B)))
    for p in B:
        ms = sorted(p)
        f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))
