"""Recompute signed orders by bounded local series, not producer valuations."""
from collections import Counter
import quotient as q
from projectors import check_factor_certificate


def _point(P,curve):
    p,f=q.curve_data(curve)
    q.require(type(P) is list and len(P)==2,'checker point representation')
    x,y=P;q.scalar(x,p);q.scalar(y,p)
    q.require(y*y%p==q.evaluate(f,x,p),'checker point on curve')
    return x,y


def _series_product(a,b,p,L):
    out=[0]*L
    for i,x in enumerate(a):
        for j,y in enumerate(b[:L-i]):out[i+j]=(out[i+j]+x*y)%p
    return out


def _series_eval(poly,x,p,L):
    out=[0]*L
    for c in reversed(poly):
        out=_series_product(out,x,p,L);out[0]=(out[0]+c)%p
    return out


def local_order(curve,P,A,B,d):
    """Hasse coefficient recurrence in x-alpha or y, through order d."""
    q.event('checker_local_series');p,f=q.curve_data(curve);alpha,beta=P;L=d+1
    if beta:
        x=[alpha,1]+[0]*(L-2);y=[beta]+[0]*(L-1);F=_series_eval(f,x,p,L)
        for j in range(1,L):
            known=sum(y[i]*y[j-i] for i in range(1,j))%p
            y[j]=(F[j]-known)*q.inv(2*beta,p)%p
    else:
        y=[0,1]+[0]*(L-2);x=[alpha]+[0]*(L-1)
        derivative=(3*alpha*alpha+curve['a'])%p
        for j in range(1,L):
            previous=_series_eval(f,x,p,L)[j]
            x[j]=(int(j==2)-previous)*q.inv(derivative,p)%p
    aa=_series_eval(A,x,p,L);bb=_series_product(_series_eval(B,x,p,L),y,p,L)
    coefficients=[(a+b)%p for a,b in zip(aa,bb)]
    order=next((i for i,c in enumerate(coefficients) if c),None)
    q.require(order is not None,'checker finite local order within pole bound')
    return order


def _sum(curve,points):
    """Checker's own affine accumulation, including identity/torsion branches."""
    p=curve['p'];total=None
    for P in points:
        q.event('checker_group_add')
        if total is None:total=P;continue
        x,y=total;u,v=P
        if x==u and (y+v)%p==0:total=None;continue
        numerator=(3*x*x+curve['a']) if total==P else (v-y)
        denominator=(2*y) if total==P else (u-x)
        slope=numerator*q.inv(denominator,p)%p
        xx=(slope*slope-x-u)%p;total=(xx,(slope*(x-xx)-y)%p)
    return total


def _verify(w,recovered):
    q.event('independent_chart_check')
    required={'curve','interval','k','target','A','B','U','e','root_lifts'}
    q.require(type(w) is dict and required<=set(w) and set(w)<=required|{'factors'},'witness shape')
    curve=w['curve'];p,f=q.curve_data(curve);up,u=q.modulus(w['U']);q.require(up==p,'checker field binding')
    q.require(type(w['interval']) is dict and set(w['interval'])=={'t','s'},'checker interval representation')
    t,s=w['interval']['t'],w['interval']['s'];q.interval(p,t,s)
    k=q.integer(w['k'],'checker affine arity');q.require(k<=5 and len(u)==k+1,'checker quotient degree')
    A=q.canonical(w['A'],p);B=q.canonical(w['B'],p)
    target=_point(w['target'],curve) if w['target'] is not None else None
    q.require(type(recovered) is list and len(recovered)==5,'five point output')
    pts=[_point(P,curve) for P in recovered if P is not None]
    q.require(len(pts)==k and recovered==[list(P) for P in sorted(pts)]+[None]*(5-k),'canonical multiset and padding')
    for x,y in pts:q.require((x-t)%p < 1<<s,'checker residual interval')
    cert={'p':p,'t':t,'s':s,'factors':[[x,m] for x,m in sorted(Counter(x for x,y in pts).items())]}
    check_factor_certificate(w['U'],cert)
    if 'factors' in w:
        check_factor_certificate(w['U'],w['factors']);q.require(w['factors']==cert,'factor output binding')
    q.verify_quotient_witness(w['U'],t,s,w['e'],curve)
    q.require(type(w['root_lifts']) is list,'checker lift list')
    for P in w['root_lifts']:_point(P,curve)
    if not k:
        q.require(target is None and A==[1] and B==[0],'all identity special chart');return
    d=k+int(target is not None);q.require(d>=2,'checker no pole one')
    da=-1 if A==[0] else len(A)-1;db=-1 if B==[0] else len(B)-1
    if d%2==0:q.require(2*da==d and A[-1]==1 and (B==[0] or 2*db+3<d),'checker even pole shape')
    else:q.require(2*db+3==d and B[-1]==1 and (A==[0] or 2*da<d),'checker odd pole shape')
    norm=q.sub(q.mul(A,A,p),q.mul(f,q.mul(B,B,p),p),p)
    lhs=q.scale(norm,1 if d%2==0 else -1,p)
    rhs=q.mul([(-target[0])%p,1],u,p) if target else u
    q.require(lhs==rhs,'checker norm identity')
    zeros=Counter(pts)
    if target:zeros[(target[0],(-target[1])%p)]+=1
    q.require(sum(zeros.values())==d,'checker signed degree')
    for P,m in zeros.items():q.require(local_order(curve,P,A,B,d)==m,'checker exact signed local order')
    q.require(_sum(curve,pts)==target,'checker group relation')


def check_chart(witness,recovered):
    try:
        _verify(witness,recovered)
        return {'status':'valid','obligation':None}
    except (q.ObligationError,KeyError,TypeError,IndexError) as error:
        return {'status':'invalid','obligation':str(error),'exception_type':type(error).__name__}
    except Exception as error:
        return {'status':'error','obligation':str(error),'exception_type':type(error).__name__}
