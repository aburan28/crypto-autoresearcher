"""Excluded engineering probe; never used as a scientific sample."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, '/workspace/solinas-run/experiments/EXP-ECDLP-5184f7/implementation')
from common import Stream, gp_file, write

out = Path('/workspace/solinas-runtime/nist-comparison/instrument-01')
out.mkdir(parents=True, exist_ok=False)
moduli = [('P192', 2**192-2**64-1), ('P224', 2**224-2**96+1)]
results=[]
for name,p in moduli:
    rng=Stream('EXCLUDED-NIST-ENGINEERING-PROBE/'+name)
    rows=[[rng.below(p),rng.below(p)] for _ in range(4)]
    src=out/(name+'.gp')
    src.write_text(f'p={p};setrand(2026101180);v={rows};\n'+
       'for(i=1,#v,gettime();E=ellinit(v[i],p);N=ellcard(E);ms=gettime();F=factor(N,2^20);fm=gettime();print([i,N,lift(E.j),ms,fm,Vec(F[,1]),Vec(F[,2])]));\nquit;\n')
    raw,timing=gp_file(src,out/name,timeout=600)
    parsed=[json.loads(s) for s in raw.splitlines() if s.strip()]
    results.append({'name':name,'p':p,'rows':rows,'outputs':parsed,'process':timing,'excluded_from_scientific_sample':True})
    print(name,'order seconds', [r[3]/1000 for r in parsed], 'factor seconds',[r[4]/1000 for r in parsed],flush=True)
write(out/'results.json',results)
