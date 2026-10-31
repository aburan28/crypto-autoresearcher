# PROBE ONLY: preimage-count histogram excluding O and 2-torsion traces
import sys
src=open('probe_legendre.py').read().split('for p in map(int,sys.argv[1:])')[0]
src=src.replace("out.append((t0,N,M,dist,len(cc),len(cg)))","out.append((t0,Counter(tr),pts))")
exec(src)
from collections import Counter
for p in (23,29,31):
    r=run(p); h=Counter()
    for t0,c,pts in r:
        for i,m in c.items():
            P=pts[i]
            if P is None or P[1][0]==0: continue
            h[m]+=1
    print("p",p,"preimage-count histogram (non-2-torsion traces):",sorted(h.items()))
