# PROBE ONLY: max number of torus elements u (not pairs) with the same trace, per fibre
import sys
sys.argv=['x']
src=open('probe_legendre.py').read().split('for p in map(int,sys.argv[1:])')[0]
exec(src.replace("tr.append(idx[T])","tr.append(idx[T])"))
from collections import Counter
import re
# re-run run() but need tr; patch run to return tr lists
src2=src.replace("out.append((t0,N,M,dist,len(cc),len(cg)))","out.append((t0,N,M,dist,len(cc),len(cg),max(Counter(tr).values())))")
exec(src2)
for p in (11,13,17,19,23,29):
    r=run(p)
    print("p",p,"max u-preimages of one trace over fibres",max(x[6] for x in r),"median-of-max",sorted(x[6] for x in r)[len(r)//2])
