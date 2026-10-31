#!/usr/bin/env python3
"""Hand-selected software-conformance fixture. This is not a scientific cohort."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent/'fixed-case';root.mkdir(exist_ok=True)
p,a,b,P,r,N=383,261,146,(196,297),181,362
scalars=[0,1,2,7,180]
def add(q,s):
 if q is None:return s
 if s is None:return q
 if q[0]==s[0] and (q[1]+s[1])%p==0:return None
 m=((3*q[0]*q[0]+a)*pow(2*q[1],-1,p) if q==s else (s[1]-q[1])*pow(s[0]-q[0],-1,p))%p
 x=(m*m-q[0]-s[0])%p;return x,(m*(q[0]-x)-q[1])%p
def mul(k):
 q=None;s=P
 while k:
  if k&1:q=add(q,s)
  k>>=1
  if k:s=add(s,s)
 return q
(root/'fixtures.tsv').write_text('fixture_id\tstratum\tp\ta\tb\tgx\tgy\tr\tN\tseed\nfixed-dev\tordinary\t383\t261\t146\t196\t297\t181\t362\t4420\n')
rows=['fixture_id\treplicate\ttarget_id\ttarget_ordinal\tqx\tqy\tinfinity']
for ordinal,k in enumerate(scalars):
 q=mul(k);rows.append(f'fixed-dev\t0\tfixed-Q-{ordinal}\t{ordinal}\t{q[0] if q else 0}\t{q[1] if q else 0}\t{0 if q else 1}')
(root/'targets.tsv').write_text('\n'.join(rows)+'\n')
(root/'settings.tsv').write_text('cell_id\tfixture_id\treplicate\tdp_bits\tinitial_chains\tendpoint_cap\tmax_precomp_ops\tmax_online_ops\tseed\nfixed-cell\tfixed-dev\t0\t2\t11\t44\t0\t0\t1267058\n')
(root/'expected.json').write_text(json.dumps({'context':'development_software_conformance','scientific_cohort_run':False,'hand_selected_scalars':scalars,'p':p,'a':a,'b':b,'P':P,'r':r,'N':N},indent=2)+'\n')
print(root)
