"""Signed multiplicity recovery by valuations and norm units; no field scan."""
from collections import Counter
import quotient as q
import charts
from projectors import check_factor_certificate


def validate_shape(curve,target,A,B,U):
    p,f=q.curve_data(curve);up,u=q.modulus(U);q.require(p==up,'curve quotient field match')
    A=q.canonical(A,p);B=q.canonical(B,p);k=len(u)-1;target=charts.point(curve,target)
    spec=charts.chart_spec(curve,k,target);q.require(spec['possible'],'possible pole chart')
    if not k:
        q.require(A==[1] and B==[0],'identity chart constants');return p,f,u,spec,target
    d=spec['d']
    degA=-1 if A==[0] else len(A)-1;degB=-1 if B==[0] else len(B)-1
    if d%2==0:q.require(degA==d//2 and A[-1]==1 and (B==[0] or 2*degB+3<d),'even pole normalization')
    else:q.require(degB==(d-3)//2 and B[-1]==1 and (A==[0] or 2*degA<d),'odd pole normalization')
    N=q.sub(q.mul(A,A,p),q.mul(f,q.mul(B,B,p),p),p)
    expected=q.mul([(-target[0])%p,1],u,p) if target else u
    q.require(q.scale(N,spec['c'],p)==expected,'norm coefficient identity')
    if target:q.require((q.evaluate(A,target[0],p)-target[1]*q.evaluate(B,target[0],p))%p==0,'actual negative target zero')
    return p,f,u,spec,target


def norm_support(factors,target):
    support=dict(factors['factors'])
    if target:support[target[0]]=support.get(target[0],0)+1
    return sorted(support.items())


def recover_signed_divisor(curve,target,A,B,U,factors,root_lifts):
    q.event('signed_divisor_recovery');p,f,u,spec,target=validate_shape(curve,target,A,B,U)
    check_factor_certificate(U,factors);q.require(type(root_lifts) is list,'root lift list')
    lifts=[charts.point(curve,P,False) for P in root_lifts]
    q.require(len(set(lifts))==len(lifts),'distinct root lift records')
    if len(u)==1:return [None]*5
    divisor=Counter()
    for x,m in norm_support(factors,target):
        av,ar=q.valuation(A,x,p);bv,br=q.valuation(B,x,p);fx=q.evaluate(f,x,p)
        if fx==0:
            order=min(2*av,2*bv+1);q.require(order==m,'branch local order');divisor[(x,0)]+=m
        else:
            g=min(av,bv);q.require(type(g) is int,'finite common valuation');residual=m-2*g
            q.require(residual>=0,'nonnegative residual norm order')
            if residual:
                common=q.power([(-x)%p,1],g,p);a0=q.exact(A,common,p);b0=q.exact(B,common,p)
                bval=q.evaluate(b0,x,p);q.require(bval!=0,'nonzero sign denominator')
                beta=-q.evaluate(a0,x,p)*q.inv(bval,p)%p
                q.require(beta!=0 and beta*beta%p==fx,'ratio ordinate')
            else:
                q.require(g>0,'balanced norm root')
                beta=target[1] if target and target[0]==x else next((y for xx,y in lifts if xx==x),None)
                q.require(beta is not None,'supplied balanced square root')
                q.require(beta!=0 and beta*beta%p==fx,'balanced square root check');q.event('supplied_square_root_check')
            if g+residual:divisor[(x,beta)]+=g+residual
            if g:divisor[(x,(-beta)%p)]+=g
    q.require(sum(divisor.values())==spec['d'],'complete signed degree')
    if target:
        negative=(target[0],(-target[1])%p);q.require(divisor[negative]>=1,'signed target subtraction');divisor[negative]-=1
    points=[P for P,m in sorted(divisor.items()) for _ in range(m)]
    q.require(len(points)==len(u)-1,'residual affine degree')
    q.require(Counter(x for x,y in points)==Counter(dict(factors['factors'])),'residual coordinate multiplicities')
    q.require(charts.sum_points(curve,points)==target,'recovered group sum')
    return [list(P) for P in points]+[None]*(5-len(points))
