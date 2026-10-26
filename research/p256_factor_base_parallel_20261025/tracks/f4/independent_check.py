"""Separate certificate consumer: no imports from divisor.py or validate.py.

Python-domain SymPy checks polynomial certificates; Jacobian arithmetic checks
point sums. Row ranks use fraction-free cross elimination, with no RREF helper
or producer-generated pivots imported.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import sympy as s


def check(directory):
    receipt = json.loads((directory/'receipt.json').read_text())
    p, a, b, r = (receipt[k] for k in ['p','a','b','r'])
    x, t = s.symbols('x t')
    g = s.Poly(x**3+a*x+b, x, modulus=p)
    def poly(v, z=x):
        return s.Poly.from_list(list(reversed(v)), z, modulus=p)
    def same(u,v):
        return (u-v).is_zero
    def rank(M):
        if not M:
            return 0
        A = [[v % r for v in row] for row in M]
        h=0
        for j in range(len(A[0])):
            at=next((i for i in range(h,len(A)) if A[i][j]),None)
            if at is None:
                continue
            A[at],A[h]=A[h],A[at]
            pivot=A[h][j]
            for i in range(h+1,len(A)):
                c=A[i][j]
                if c:
                    A[i]=[(pivot*u-c*v)%r for u,v in zip(A[i],A[h])]
            h+=1
            if h == len(A):
                break
        return h
    # Jacobian Z=0 is infinity. Independent from producer affine formulas.
    O=(1,1,0)
    def double(P):
        X,Y,Z=P
        if not Z or not Y:
            return O
        XX=X*X%p; YY=Y*Y%p; YYYY=YY*YY%p; ZZ=Z*Z%p
        S=2*((X+YY)**2-XX-YYYY)%p
        M=(3*XX+a*ZZ*ZZ)%p
        U=(M*M-2*S)%p
        return U,(M*(S-U)-8*YYYY)%p,((Y+Z)**2-YY-ZZ)%p
    def plus(P,Q):
        X1,Y1,Z1=P; X2,Y2,Z2=Q
        if not Z1:return Q
        if not Z2:return P
        U1=X1*Z2**2%p; U2=X2*Z1**2%p
        S1=Y1*Z2**3%p; S2=Y2*Z1**3%p
        if U1==U2:
            return double(P) if S1==S2 else O
        H=(U2-U1)%p; I=(2*H)**2%p; J=H*I%p
        V=U1*I%p; rr=2*(S2-S1)%p
        X3=(rr*rr-J-2*V)%p
        return X3,(rr*(V-X3)-2*S1*J)%p,((Z1+Z2)**2-Z1**2-Z2**2)*H%p
    def multiply(n,P):
        Q=O
        for bit in bin(n)[2:]:
            Q=double(Q)
            if bit=='1':Q=plus(Q,P)
        return Q
    def check_sum(row, pointmap):
        total=O
        for key,c in row.items():
            X,Y=pointmap[key]
            total=plus(total,multiply(c%r,(X,Y,1)))
        assert total[2]==0
    def valuation(A,B,X,Y,bound):
        # Hensel/Newton doubling for y^2=g(X+t), distinct from coefficient recurrence.
        mod=s.Poly(t**(bound+1),t,modulus=p)
        rhs=s.Poly((X+t)**3+a*(X+t)+b,t,modulus=p).rem(mod)
        y=s.Poly(Y,t,modulus=p)
        for _ in range((bound+1).bit_length()+1):
            y=((y+rhs*s.invert(y,mod))*pow(2,-1,p)).rem(mod)
        assert same((y*y).rem(mod),rhs)
        Aat=s.Poly(A.as_expr().subs(x,X+t),t,modulus=p)
        Bat=s.Poly(B.as_expr().subs(x,X+t),t,modulus=p)
        f=(Aat+y*Bat).rem(mod)
        for k in range(bound+1):
            if f.nth(k)%p:return k
        raise AssertionError('zero jet exceeds certified norm multiplicity')
    cases={}
    pointmap={}
    factor_checks=0
    multiplicity_checks=0
    for path in sorted(directory.glob('*.json')):
        c=json.loads(path.read_text())
        if not isinstance(c,dict) or 'norm' not in c:
            continue
        A,B,N=(poly(c[key]) for key in ['A','B','norm'])
        assert same(A*A-g*B*B,N)
        m=max(2*A.degree() if not A.is_zero else -1, 3+2*B.degree() if not B.is_zero else -1)
        assert m==c['pole_order'] and N.degree()==m
        product=poly([c['norm_unit']])
        norm_roots={}
        for f in c['norm_factors']:
            q=poly(f['coefficients'])
            assert q.degree()==f['degree'] and q.is_irreducible
            factor_checks+=1
            product*=q**f['multiplicity']
            if q.degree()==1:
                X=-int(q.nth(0))*pow(int(q.nth(1)),-1,p)%p
                norm_roots[X]=f['multiplicity']
        assert same(product,N)
        expected_zeros=[]
        nonrational_degree=0
        for f in c['norm_factors']:
            if f['degree']>1:
                nonrational_degree+=f['degree']*f['multiplicity']
                continue
            q=poly(f['coefficients'])
            X=-int(q.nth(0))*pow(int(q.nth(1)),-1,p)%p
            rhs=int(g.eval(X))%p
            assert rhs != 0
            if pow(rhs,(p-1)//2,p)!=1:
                nonrational_degree+=f['multiplicity']
                continue
            Y=pow(rhs,(p+1)//4,p)
            for Yv in sorted([Y,p-Y]):
                e=valuation(A,B,X,Yv,f['multiplicity'])
                if e:expected_zeros.append((X,Yv,e))
                multiplicity_checks+=1
        assert sorted(expected_zeros)==sorted((z['point'][0],z['point'][1],z['multiplicity']) for z in c['zeros'])
        assert sum(e for X,Y,e in expected_zeros)+nonrational_degree==m
        row={}; signed={}
        for X,Y,e in expected_zeros:
            assert (Y*Y-X**3-a*X-b)%p==0
            assert multiply(r,(X,Y,1))[2]==0
            key=str(X); sg=1 if Y<p-Y else -1
            row[key]=row.get(key,0)+sg*e
            pointmap[key]=(X,min(Y,p-Y))
            signed.setdefault(key,[0,0])[sg<0]+=e
        row={k:v for k,v in row.items() if v}
        assert row==c['row']
        assert sum(min(v) for v in signed.values())==c['inverse_pairs']
        assert (nonrational_degree==0)==c['fully_rational']
        if c['fully_rational']:
            check_sum(row,pointmap)
        for X,Y in c['declared_anchors']:
            assert (int(A.eval(X))+Y*int(B.eval(X)))%p==0
        anchor_counts=Counter(tuple(P) for P in c['declared_anchors'])
        zeros_counts={(X,Y):e for X,Y,e in expected_zeros}
        assert all(zeros_counts.get(P,0)>=count for P,count in anchor_counts.items())
        cases[c['id']]=c
    graphs={}
    checked_sums=0
    for path in sorted(directory.glob('graph_*.json')):
        c=json.loads(path.read_text())
        rows=[cases[k]['row'] for k in c['case_ids']]
        allcols=c['all_columns']; base=c['base_columns']; outside=c['outside_columns']
        D=[[row.get(k,0) for k in allcols] for row in rows]
        A=[[row.get(k,0) for row in rows] for k in outside]
        B=[[row.get(k,0) for k in base] for row in rows]
        assert rank(D)==c['rank_before_all_columns']
        assert rank(A)==c['outside_incidence_rank']
        assert rank(B)==c['rank_projected_base_before_cancellation']
        vectors=[]
        for output in c['cancelled_rows']:
            coeff=output['combination']
            assert len(coeff)==len(rows)
            value={k:sum(v*row.get(k,0) for v,row in zip(coeff,rows))%r for k in allcols}
            assert all(value[k]==0 for k in outside)
            assert {k:value[k] for k in base if value[k]}==output['row']
            check_sum(output['row'],pointmap)
            checked_sums+=1
            vectors.append(coeff)
        assert rank(vectors)==c['kernel_dimension']==len(rows)-rank(A)
        finalrank=rank([[out['row'].get(k,0) for k in base] for out in c['cancelled_rows']])
        assert finalrank==c['rank_after_cancellation']==rank(D)-rank(A)
        graphs[path.stem]={'all_rank':rank(D),'outside_rank':rank(A),'after_rank':finalrank,
                           'coefficient_witnesses':len(vectors),'independently_checked':True}
    # Mutation control: a wrong final coefficient must fail the group identity.
    tamper_detected=False
    key=next(iter(pointmap))
    try:check_sum({key:1},pointmap)
    except AssertionError:tamper_detected=True
    assert tamper_detected
    return {'status':'passed','divisor_cases':len(cases),'irreducible_factor_checks':factor_checks,
            'local_branch_multiplicity_checks':multiplicity_checks,'stitched_group_sums':checked_sums,
            'graphs':graphs,'tampered_singleton_detected':tamper_detected,
            'independence':'separate code paths and arithmetic; same author/session, not independent scientific review',
            'producer_receipt_sha256':hashlib.sha256((directory/'receipt.json').read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    started=time.perf_counter()
    result=check(args.directory)
    result.update(command=[sys.executable]+sys.argv,python=sys.version,sympy=s.__version__,
                  completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-started,
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))
