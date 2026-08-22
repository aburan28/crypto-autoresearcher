"""Stage 2: rank-profile every pool curve over the twist support, then optimise
over every affine k-subspace (coset) of the support group, for k = 3..6.

Scoring is vectorised over subspaces; the two objectives are the exact
distinct-class count and the multiplicity sum.  See twist_family.py for the
mathematics.
"""
import os
import sys, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twist_family import (profile, affine_subspaces, DEFAULT_SUPPORT)

NS = len(DEFAULT_SUPPORT)

IDX = {}
for k in (3,4,5,6):
    AS = affine_subspaces(NS, k)
    IDX[k] = np.array([[m0^v for v in V] for m0,V in AS], dtype=np.int32)
    print('k=%d affine subspaces: %d'%(k, len(AS)), flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, 'runs')
pool = json.load(open(os.path.join(OUT, 'RUN-ECRANK-e1e30e-001', 'pool.json')))
seeds = [{'ai':[1,-1,1,0,0],'rank':1},{'ai':[0,0,1,-7,6],'rank':3},
         {'ai':[0,1,1,-2,0],'rank':2},{'ai':[1,-1,0,-79,289],'rank':4},
         {'ai':[1,1,1,-2,0],'rank':3}]
allc = seeds + pool
best = {k:(-1,None) for k in (3,4,5,6)}
bestc= {k:(-1,None) for k in (3,4,5,6)}
res=[]
t0=time.time()
for i,c in enumerate(allc):
    ai=c['ai']
    try:
        (A,B), prof = profile(ai, DEFAULT_SUPPORT, 3)
    except Exception as e:
        continue
    cert = np.array([e['certified'] for e in prof], dtype=np.int32)
    has  = (cert>=1).astype(np.int32)
    row={'ai':ai,'A':A,'B':B}
    for k in (3,4,5,6):
        sm = cert[IDX[k]].sum(axis=1); sc = has[IDX[k]].sum(axis=1)
        m1=int(sm.max()); m2=int(sc.max())
        row['k%d_mult'%k]=m1; row['k%d_cls'%k]=m2
        if m1>best[k][0]: best[k]=(m1,ai)
        if m2>bestc[k][0]: bestc[k]=(m2,ai)
    res.append(row)
    if i%25==0:
        print('[%4d/%d %.0fs] best mult k3/k4/k5/k6 = %d/%d/%d/%d  best cls = %d/%d/%d/%d'
              %(i,len(allc),time.time()-t0,best[3][0],best[4][0],best[5][0],best[6][0],
                bestc[3][0],bestc[4][0],bestc[5][0],bestc[6][0]), flush=True)
json.dump(res, open(os.path.join(OUT, 'RUN-ECRANK-e1e30e-001', 'subspace_scan.json'), 'w'))
print('DONE %.0fs'%(time.time()-t0))
for k in (3,4,5,6):
    print('k=%d [K:Q]=%-3d  best sum-mult=%d %s | best #classes=%d %s'
          %(k,2**k,best[k][0],best[k][1],bestc[k][0],bestc[k][1]))
