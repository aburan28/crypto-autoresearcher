#!/usr/bin/env python3
"""Separate emitted-artifact verifier using baseline affine arithmetic and GF rank."""
import hashlib,json,sys
from pathlib import Path
import sympy as S
from sympy.polys.matrices import DomainMatrix
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent.parent/'baseline'))
from curve_arithmetic import Curve
d=json.loads((H/'orbit_certificate.json').read_text());c=d['curve']
p,r=c['p'],c['r'];E=Curve(p,0,7);beta=d['beta'];lam=d['lambda']
points=[tuple(P) for P in d['points']];reps=[tuple(P) for P in d['representatives']]
R=[];RC=[]
for file in sorted(H.glob('matrix_block_*.json')):
    for obj in json.loads(file.read_text()):
        row,small=obj['full'],obj['compressed']; assert len(row)==48 and len(small)==8
        total=None
        for n,P in zip(row,points):total=E.add(total,E.mul(n,P))
        assert total is None
        expected=[0]*8
        for j,n in enumerate(row):
            i=d['representative_index'][j]
            expected[i]=(expected[i]+n*d['compression_factor'][j])%r
        assert expected==small;R.append(row);RC.append(small)
constraints=json.loads((H/'symmetry_constraints.json').read_text())
def rank(A):return int(DomainMatrix.from_Matrix(S.Matrix(A)).convert_to(S.GF(r)).rank())
ranks=[rank(R),rank(constraints),rank(R+constraints),rank(RC)]
assert ranks==[42,40,47,7]
assert E.mul(lam,tuple(d['generator']))==(beta*d['generator'][0]%p,d['generator'][1])
assert (beta**3-1)%p==0 and beta!=1
assert (lam**3-1)%r==0 and lam!=1
out={'completion_sentinel':True,'artifact_point_sums':len(R),'ranks_GF_r':ranks,
     'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'orbit_matrix.py',Path(__file__)]},
     'verification_scope':'Separate implementation over emitted artifacts; same session, not independent review'}
(H/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
