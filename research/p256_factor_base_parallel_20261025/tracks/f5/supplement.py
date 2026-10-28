"""Replay exact Hasse interval and kernel extension-degree consequences."""
import json,math
from pathlib import Path
p=2**256-2**224+2**192+2**96-1
r=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
rad=math.isqrt(4*p);lo=p+1-rad;hi=p+1+rad
assert (lo+r-1)//r==hi//r==1
f=json.loads(Path('attempt02-frobenius.json').read_text())
rows=[]
for row in f['screen']:
 ell=row['ell']
 if ell not in [3,5,11]:continue
 for root in row['Frobenius_roots']:
  full=next(k for k in range(1,ell) if pow(root,k,ell)==1)
  xd=next(k for k in range(1,ell) if pow(root,k,ell) in [1,ell-1])
  rows.append({'ell':ell,'Frobenius_eigenvalue':root,'full_point_field_degree':full,'x_field_degree':xd,'minimality_checked_by_exhaustion':True})
out={'Hasse':{'radius_floor_2sqrtp':str(rad),'lo':str(lo),'hi':str(hi),'unique_multiple_is_r':True},'kernel_extension_degrees':rows,'nontrivial_rational_kernel_points':False,'rational_kernel_reason':'#E(Fp)=prime r, and ell=3,5,11 are coprime to r; Frobenius-stable kernels need not have rational nonidentity points.'}
Path('supplement-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
