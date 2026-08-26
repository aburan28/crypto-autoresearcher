"""Parse the published rank-record curve page and check every listed generator
lies on the curve, in exact rational arithmetic.

Input is the saved HTML of the record page; output is the JSON consumed by
quadratic_lift.py.  This script verifies ON-CURVE membership only -- independence
of the published generators is checked separately by the height regulator.
"""
import os
import re, json
from fractions import Fraction as F
txt = open('rk30.html').read()
txt = re.sub(r'<[^>]*>','',txt).replace('&ge;','>=').replace('&ouml;','o')
# curve coefficients
m = re.search(r'y2\s*\+\s*xy\s*=\s*x3\s*-\s*(\d+)x\s*\+\s*(\d+)', txt.replace('\n',' ').replace('\t',' '))
a4 = -int(m.group(1)); a6 = int(m.group(2))
pts=[]
for mm in re.finditer(r'P(\d+)\s*=\s*\[([^,]+),\s*([^\]]+)\]', txt):
    i=int(mm.group(1)); xs=mm.group(2).strip(); ys=mm.group(3).strip()
    pts.append((i, xs, ys))
pts.sort()
print('a4 digits',len(str(abs(a4))),'a6 digits',len(str(a6)),'points',len(pts))
def frac(s):
    if '/' in s:
        n,d=s.split('/'); return F(int(n),int(d))
    return F(int(s))
# exact on-curve check for y^2 + xy = x^3 + a4 x + a6
bad=[]
for i,xs,ys in pts:
    x=frac(xs); y=frac(ys)
    if y*y + x*y != x**3 + a4*x + a6: bad.append(i)
print('points OFF the curve:', bad if bad else 'none - all %d verified exactly'%len(pts))
json.dump({'a_invariants':[1,0,0,a4,a6],
           'points':[[p[1],p[2]] for p in pts]},
          open('rk30.json','w'))
print('a4 =',a4); print('a6 =',a6)
