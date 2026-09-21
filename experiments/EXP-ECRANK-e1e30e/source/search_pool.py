"""Stage 1: enumerate small-coefficient curves of rank >= 3 over Q, dedupe by j-invariant.

Produces the base-curve pool consumed by scan_pool.py.  ellrank supplies both the
rank lower bound and the points; a curve enters the pool on its rank lower bound
alone, so a descent timeout drops a curve rather than admitting it.
"""
import os
import sys, json, time
sys.path.insert(0,'/home/user/crypto-autoresearcher/scratch_rank')
import cypari
p = cypari.pari; p.allocatemem(2**31, silent=True)

seen_j = {}
t0=time.time(); n=0
for a1 in (0,1):
  for a2 in (-1,0,1):
    for a3 in (0,1):
      for a4 in range(-20,21):
        for a6 in range(-50,51):
          ai=[a1,a2,a3,a4,a6]; n+=1
          try:
            E = p('iferr(ellinit(%s),E,0)'%(ai,))
            if str(E)=='0': continue
            r = p('iferr(alarm(3,ellrank(%s)),E,[-1,-1,0,[]])'%E)
            rl=int(r[0])
            if rl < 3: continue
            j = str(p('%s.j'%E))
            if j not in seen_j or rl > seen_j[j][1]:
                seen_j[j]=(ai,rl)
          except Exception: continue
print('scanned',n,'curves in %.0fs'%(time.time()-t0),'-> distinct j with rank>=3:',len(seen_j))
res=[{'ai':v[0],'rank':v[1],'j':k} for k,v in seen_j.items()]
res.sort(key=lambda z:-z['rank'])
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'runs', 'RUN-ECRANK-e1e30e-001', 'pool.json'), 'w'))
from collections import Counter
print('rank histogram:', Counter(x['rank'] for x in res))
