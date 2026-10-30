#!/usr/bin/env python3
"""Construct and verify signed secp256k1 orbit compression; no timings."""
import hashlib, json, platform, sys
from pathlib import Path
import sympy as S
from sympy.polys.matrices import DomainMatrix
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'baseline'))
from parameters import CURVES
from curve_arithmetic import Curve, sqrt_mod
C=next(c for c in CURVES if c['name']=='secp256k1')
p,r=C['p'],C['r']; E=Curve(p,0,7)

def rank_mod(A):
    A=[[v%r for v in row] for row in A]; i=0
    for j in range(len(A[0])):
        k=next((k for k in range(i,len(A)) if A[k][j]),None)
        if k is None: continue
        A[i],A[k]=A[k],A[i]
        inv=pow(A[i][j],-1,r); A[i]=[a*inv%r for a in A[i]]
        for k in range(i+1,len(A)):
            u=A[k][j]
            if u:A[k]=[(a-u*b)%r for a,b in zip(A[k],A[i])]
        i+=1
        if i==len(A):break
    return i

def rank_independent(A):
    # Different matrix package, modular-domain row reduction.
    return int(DomainMatrix.from_Matrix(S.Matrix(A)).convert_to(S.GF(r)).rank())

def jdouble(P):
    X,Y,Z=P
    if not Z or not Y:return (0,1,0)
    yy=Y*Y%p; s=4*X*yy%p; m=3*X*X%p
    x=(m*m-2*s)%p
    return x,(m*(s-x)-8*yy*yy)%p,2*Y*Z%p

def jadd(P,Q):
    X,Y,Z=P; U,V,W=Q
    if not Z:return Q
    if not W:return P
    z2,w2=Z*Z%p,W*W%p
    a,b=X*w2%p,U*z2%p
    c,d=Y*W*w2%p,V*Z*z2%p
    if a==b:return jdouble(P) if c==d else (0,1,0)
    h=(b-a)%p; rr=(d-c)%p; h2=h*h%p; h3=h*h2%p
    x=(rr*rr-h3-2*a*h2)%p
    return x,(rr*(a*h2-x)-c*h3)%p,h*Z*W%p

def independent_mul(k,P):
    A=(0,1,0); B=(P[0],P[1],1)
    for bit in bin(k)[2:]:
        A=jdouble(A)
        if bit=='1':A=jadd(A,B)
    X,Y,Z=A
    if not Z:return None
    iz=pow(Z,-1,p); return X*iz*iz%p,Y*iz**3%p

def main():
    G=(int('79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',16),
       int('483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8',16))
    assert E.rhs(G[0])==G[1]**2%p
    assert E.mul(r,G) is None and independent_mul(r,G) is None
    beta=pow(2,(p-1)//3,p)
    assert beta!=1 and (beta*beta+beta+1)%p==0
    psi=lambda P:None if P is None else (beta*P[0]%p,P[1])
    root=sqrt_mod(-3,r)
    candidates=[(-1+root)*pow(2,-1,r)%r,(-1-root)*pow(2,-1,r)%r]
    lam=next(k for k in candidates if E.mul(k,G)==psi(G))
    assert independent_mul(lam,G)==psi(G)
    assert lam!=1 and (lam*lam+lam+1)%r==0 and pow(lam,3,r)==1
    assert psi(psi(psi(G)))==G and psi(None) is None
    reps=[E.mul(i,G) for i in range(1,9)]
    points=[]; factors=[]; mapping=[]
    for j in range(3):
        for sign in [1,-1]:
            for i,P in enumerate(reps):
                point=P
                for _ in range(j):point=psi(point)
                if sign<0:point=E.neg(point)
                factor=sign*pow(lam,j,r)%r
                assert point==E.mul(factor,P)==independent_mul(factor,P)
                points.append(point);factors.append(factor);mapping.append(i)
    assert len(set(points))==48
    assert all(E.rhs(P[0])==P[1]*P[1]%p for P in points)
    R=[]; RC=[]; group_checks=0
    pairs=[(a,b) for a in range(1,9) for b in range(a,9) if a+b<=8]
    for block in range(6):
        blockrows=[]
        for a,b in pairs:
            row=[0]*48
            for i,c in [(a-1,1),(b-1,1),(a+b-1,-1)]:row[block*8+i]+=c
            total=None
            for c,P in zip(row,points):total=E.add(total,E.mul(c,P))
            assert total is None; group_checks+=1
            small=[0]*8
            for i,c in enumerate(row):small[mapping[i]]=(small[mapping[i]]+c*factors[i])%r
            assert sum(c*(i+1) for i,c in enumerate(small))%r==0
            R.append(row);RC.append(small);blockrows.append({'full':row,'compressed':small})
        (HERE/f'matrix_block_{block}.json').write_text(json.dumps(blockrows,indent=2)+'\n')
    constraints=[]
    for j in range(8,48):
        row=[0]*48;row[j]=1;row[mapping[j]]=-factors[j]%r;constraints.append(row)
    ranks={}
    for name,A in [('relations_full',R),('symmetry_constraints',constraints),
                   ('relations_plus_symmetry',R+constraints),('compressed',RC)]:
        a,b=rank_mod(A),rank_independent(A)
        assert a==b;ranks[name]=dict(custom_elimination=a,sympy_GF_rank=b)
    assert ranks['compressed']['custom_elimination']==7
    assert ranks['relations_plus_symmetry']['custom_elimination']==47
    # Negative controls exercise map choice and eigenvalue identification.
    assert E.mul(candidates[1-candidates.index(lam)],G)!=psi(G)
    assert (2**3-1)%p!=0
    assert any(((2*P[0])**3+7-P[1]**2)%p!=0 for P in reps)
    assert rank_mod(RC+[[1]+[0]*7])==8
    data={'curve':C,'generator':G,'beta':beta,'lambda':lam,
          'other_lambda':next(k for k in candidates if k!=lam),
          'representatives':reps,'points':points,'compression_factor':factors,
          'representative_index':mapping}
    (HERE/'orbit_certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    (HERE/'symmetry_constraints.json').write_text(json.dumps(constraints,separators=(',',':'))+'\n')
    receipt={'schema':'f8-orbit-validation-v1','task':'TASK-20261025-f439ca',
        'software':{'python':platform.python_version(),'sympy':S.__version__},
        'curve_name':C['name'],'order_assumption':'Published p,r prime and h=1; no primality certificate regenerated',
        'orbits':8,'signed_orbit_size':6,'full_columns':48,'compressed_columns':8,
        'constructed_relation_rows':len(R),'point_sum_checks':group_checks,
        'affine_jacobian_action_agreements':48,'ranks':ranks,
        'controls':{'conjugate_eigenvalue_rejected':True,'nonroot_beta_2_rejected':True,
                    'false_relation_increases_rank_to_8':True},
        'unknown_target_solved':False,'performance_trial':False,'completion_sentinel':True}
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
