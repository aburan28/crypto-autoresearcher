"""Complete pole strata and interpolation from a supplied signed relation."""
from collections import Counter
import quotient as q


def point(curve,P,allow_identity=True):
    p,f=q.curve_data(curve)
    if P is None:
        q.require(allow_identity,'affine summand required'); return None
    q.require(type(P) in (list,tuple) and len(P)==2,'point representation')
    x,y=P; q.scalar(x,p);q.scalar(y,p)
    q.require(y*y % p==q.evaluate(f,x,p),'point on curve')
    return (x,y)


def add_points(curve,P,Q):
    q.event('elliptic_group_add')
    p=curve['p']
    if P is None:return Q
    if Q is None:return P
    x,y=P;u,v=Q
    if x==u and (y+v)%p==0:return None
    if x==u:
        slope=(3*x*x+curve['a'])*q.inv(2*y,p)%p
    else:slope=(v-y)*q.inv(u-x,p)%p
    z=(slope*slope-x-u)%p
    return (z,(slope*(x-z)-y)%p)


def sum_points(curve,points):
    total=None
    for P in points:total=add_points(curve,total,P)
    return total


def basis(d):
    terms=[('A',i,2*i) for i in range(d//2+1)]
    terms += [('B',j,2*j+3) for j in range(max(0,(d-3)//2+1))]
    return sorted(terms,key=lambda t:t[2])


def chart_spec(curve,k,target):
    q.event('chart_specification'); q.curve_data(curve); q.integer(k,'affine arity')
    q.require(k<=5,'five summand scope');target=point(curve,target)
    if k==0:return {'possible':target is None,'d':0,'special':'all_identity' if target is None else 'finite_zero_impossible'}
    d=k+int(target is not None)
    if d==1:return {'possible':False,'d':1,'special':'no_pole_one'}
    return {'possible':True,'d':d,'c':1 if d%2==0 else -1,'basis':basis(d)}


def trunc(a,L):
    return (a+[0]*L)[:L]


def smul(a,b,p,L):
    return trunc(q.mul(a,b,p),L)


def compose(a,x,p,L):
    v=[0]*L
    for c in reversed(a):
        v=smul(v,x,p,L);v[0]=(v[0]+c)%p
    return v


def interpolation_series(curve,P,L):
    p,f=q.curve_data(curve);alpha,beta=P
    if beta:
        x=trunc([alpha,1],L); y=[beta]+[0]*(L-1);F=compose(f,x,p,L);den=q.inv(2*beta,p)
        for n in range(1,L):y[n]=(F[n]-sum(y[i]*y[n-i] for i in range(1,n)))*den%p
    else:
        x=[alpha]+[0]*(L-1);y=trunc([0,1],L);den=q.inv(3*alpha*alpha+curve['a'],p)
        for n in range(1,L):
            value=compose(f,x,p,L)[n];x[n]=((int(n==2)-value)*den)%p
    return x,y


def unique_linear_solution(rows,rhs,p,n):
    q.event('interpolation_gaussian_elimination')
    M=[a[:]+[b] for a,b in zip(rows,rhs)];row=0;pivots=[]
    for col in range(n):
        pivot=next((i for i in range(row,len(M)) if M[i][col]),None)
        if pivot is None:continue
        M[row],M[pivot]=M[pivot],M[row];den=q.inv(M[row][col],p)
        M[row]=[a*den%p for a in M[row]]
        for i in range(len(M)):
            if i!=row:
                c=M[i][col];M[i]=[(a-c*b)%p for a,b in zip(M[i],M[row])]
        pivots.append(col);row+=1
    q.require(all(any(a[:n]) or a[n]==0 for a in M),'consistent interpolation')
    q.require(len(pivots)==n,'unique normalized interpolation')
    out=[0]*n
    for i,col in enumerate(pivots):out[col]=M[i][-1]
    return out


def construct_from_signed_multiset(curve,interval,points,target):
    q.event('relation_witness_constructor');p,f=q.curve_data(curve)
    q.require(type(interval) is dict and set(interval)=={'t','s'},'interval representation')
    t,s=interval['t'],interval['s'];q.interval(p,t,s)
    q.require(type(points) is list,'signed point list')
    pts=[point(curve,P,False) for P in points];target=point(curve,target);k=len(pts)
    for x,y in pts:q.require((x-t)%p < 1<<s,'supplied point interval')
    spec=chart_spec(curve,k,target);q.require(spec['possible'],'possible pole chart')
    q.require(sum_points(curve,pts)==target,'supplied relation group sum')
    if not k:
        return {'curve':dict(curve),'interval':dict(interval),'k':0,'target':None,'A':[1],'B':[0],'U':{'p':p,'coeffs':[1]},'e':[],'root_lifts':[]}
    d=spec['d'];zeros=Counter(pts)
    if target is not None:zeros[(target[0],(-target[1])%p)]+=1
    rows=[];rhs=[];terms=spec['basis']
    for P,m in sorted(zeros.items()):
        x,y=interpolation_series(curve,P,d+1);values=[]
        for kind,i,_ in terms:
            v=[1]+[0]*d
            for _ in range(i):v=smul(v,x,p,d+1)
            if kind=='B':v=smul(v,y,p,d+1)
            values.append(v)
        for j in range(m):
            rows.append([v[j] for v in values[:-1]]);rhs.append(-values[-1][j]%p)
    coefs=unique_linear_solution(rows,rhs,p,len(terms)-1)+[1];A=[0]*(d//2+1);B=[0]*max(1,(d-3)//2+1)
    for (kind,i,_),c in zip(terms,coefs):(A if kind=='A' else B)[i]=c
    A=q.trim(A);B=q.trim(B);N=q.sub(q.mul(A,A,p),q.mul(f,q.mul(B,B,p),p),p);u=q.scale(N,spec['c'],p)
    if target is not None:u=q.exact(u,[(-target[0])%p,1],p)
    U={'p':p,'coeffs':u};q.require(len(u)==k+1 and u[-1]==1,'residual degree and normalization')
    support=Counter(P[0] for P in pts);e=[[0] for _ in range(s)]
    for x,m in sorted(support.items()):
        q.event('CRT_local_factor');local=q.power([(-x)%p,1],m,p);other=q.exact(u,local,p)
        projector=q.rem(q.mul(other,q.inverse_mod(other,local,p),p),u,p);label=(x-t)%p
        for j in range(s):
            if label>>j&1:e[j]=q.rem(q.add(e[j],projector,p),u,p)
    q.verify_quotient_witness(U,t,s,e,curve)
    roots=sorted(set(pts+([target] if target is not None else [])))
    return {'curve':dict(curve),'interval':dict(interval),'k':k,'target':list(target) if target else None,'A':A,'B':B,'U':U,'e':e,'root_lifts':[list(P) for P in roots]}
