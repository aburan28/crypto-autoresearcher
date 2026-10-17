import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'vendor'))
import hashlib
import json
import math
import random
import time
from fractions import Fraction as F
from itertools import combinations

from sympy import factorint, isprime, nextprime, prevprime

INPUTS = ROOT/'inputs' if (ROOT/'inputs').exists() else ROOT.parent/'snfs-ecdlp-intake'
LEDGER = json.loads((INPUTS/'normalized-ledger.json').read_text())
INTAKE = json.loads((INPUTS/'intake-manifest.json').read_text())
SEEDS = {r['provisional_id']: r['seed_candidate_hex'] for r in INTAKE['records']}


def rng(pid, case):
    raw = f'bounded-pilot-v1|{pid}|{SEEDS[pid]}|{case}'.encode()
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(), 'big'))


def write_result(pid, scope, rows, limitations, checks=None):
    original = next(r for r in LEDGER['records'] if r['provisional_id'] == pid)
    result = dict(provisional_id=pid, title=original['title'], original_status=original['status'],
        evidence_class='finite-control' if not original['status'].startswith('theorem-closed') else 'receipt-only',
        execution_status='pilot-completed', scope=scope, rows=rows, limitations=limitations,
        checks=checks or {}, seed_derivation='SHA256(bounded-pilot-v1|provisional_id|local candidate|case); campaign reservation pending',
        seed_candidate=SEEDS[pid], claim_boundary='Synthetic small-field finite pilot only; no asymptotic or deployed-curve claim')
    path = ROOT/'results'/f'{pid}.json'
    path.write_text(json.dumps(result, indent=2, default=str)+'\n')
    print(json.dumps({'record':pid,'rows':len(rows),'status':'pilot-completed'}), flush=True)
    return result


class EC:
    def __init__(self,p,a,b):
        assert isprime(p) and p>3 and (4*a**3+27*b*b)%p
        self.p,self.a,self.b=p,a%p,b%p
        self.ops=0
        roots={}
        for y in range(p): roots.setdefault(y*y%p,[]).append(y)
        self.roots=roots
        self.points=[(x,y) for x in range(p) for y in roots.get((x**3+a*x+b)%p,[])]
        self.N=len(self.points)+1
    def neg(self,P): return None if P is None else (P[0],-P[1]%self.p)
    def add(self,P,Q):
        self.ops+=1
        if P is None:return Q
        if Q is None:return P
        p=self.p;x,y=P;u,v=Q
        if x==u and (y+v)%p==0:return None
        s=((3*x*x+self.a)*pow(2*y,-1,p) if P==Q else (v-y)*pow(u-x,-1,p))%p
        w=(s*s-x-u)%p
        return w,(s*(x-w)-y)%p
    def mul(self,n,P):
        if n<0:return self.mul(-n,self.neg(P))
        out=None
        while n:
            if n&1:out=self.add(out,P)
            P=self.add(P,P);n>>=1
        return out
    def order(self,P):
        n=self.N
        for q in factorint(n):
            while n%q==0 and self.mul(n//q,P) is None:n//=q
        return n
    def valid(self,P):
        return P is None or (P[1]**2-P[0]**3-self.a*P[0]-self.b)%self.p==0
    def xpoints(self,x):
        return [(x,y) for y in self.roots.get((x**3+self.a*x+self.b)%self.p,[])]


def prime_order_curve(p):
    for a in range(1,30):
        for b in range(1,30):
            if not (4*a**3+27*b*b)%p:continue
            E=EC(p,a,b)
            if isprime(E.N) and E.N!=p:return E
    raise RuntimeError('No prime-order example found')


def rref(matrix,p):
    rows=[[int(x)%p for x in row] for row in matrix];rank=0;piv=[]
    for c in range(len(rows[0])):
        k=next((i for i in range(rank,len(rows)) if rows[i][c]),None)
        if k is None:continue
        rows[k],rows[rank]=rows[rank],rows[k]
        inv=pow(rows[rank][c],-1,p);rows[rank]=[x*inv%p for x in rows[rank]]
        for i in range(len(rows)):
            if i!=rank:
                q=rows[i][c]
                rows[i]=[(x-q*y)%p for x,y in zip(rows[i],rows[rank])]
        piv.append(c);rank+=1
        if rank==len(rows):break
    return rows,piv


def nullspace(matrix,p):
    rr,piv=rref(matrix,p);n=len(matrix[0]);out=[]
    for j in range(n):
        if j in piv:continue
        v=[0]*n;v[j]=1
        for i,c in enumerate(piv):v[c]=-rr[i][j]%p
        out.append(v)
    return out


def monomials(P,d):
    x,y,z=P
    return [x**i*y**j*z**(d-i-j) for i in range(d+1) for j in range(d-i+1)]


def good_pencil(E,gen,known_generator=None):
    # All base points chosen before any target. Complete intersection sum is O.
    for attempt in range(1000):
        if known_generator is not None:
            scalars=gen.sample(range(1,E.N),8)
            first=[E.mul(k,known_generator) for k in scalars]
        else:
            first=gen.sample(E.points,8);scalars=None
        ninth=None
        for P in first:ninth=E.add(ninth,P)
        ninth=E.neg(ninth)
        if ninth is None or ninth in first:continue
        points=first+[ninth]
        if any(E.add(E.add(a,b),c) is None for a,b,c in combinations(points,3)):continue
        M=[[x% E.p for x in monomials((*P,1),3)] for P in points]
        ns=nullspace(M,E.p)
        if len(ns)!=2:continue
        Fpoly=[-E.b%E.p,0,1,0,-E.a%E.p,0,0,0,0,-1%E.p]
        G=next(v for v in ns if len(rref([Fpoly,v],E.p)[1])==2)
        assert all(sum(x*y for x,y in zip(row,G))%E.p==0 for row in M)
        if scalars is not None:scalars.append(-sum(scalars)%E.N)
        return points,scalars,G,attempt+1
    raise RuntimeError('Pencil search exhausted')


def smooth(n,B):
    n=abs(int(n))
    if n==0:return False
    for q in range(2,B+1):
        if isprime(q):
            while n%q==0:n//=q
    return n==1


def qadd(P,Q,a,b):
    if P is None:return Q
    if Q is None:return P
    x,y=P;u,v=Q
    if x==u and y==-v:return None
    s=(3*x*x+a)/(2*y) if P==Q else (v-y)/(u-x)
    w=s*s-x-u
    return w,s*(x-w)-y


def qmul(n,P,a,b):
    if n<0:return qmul(-n,(P[0],-P[1]),a,b)
    out=None
    while n:
        if n&1:out=qadd(out,P,a,b)
        P=qadd(P,P,a,b);n>>=1
    return out


def height(P,a,b,steps=5):
    Q=P
    for _ in range(steps):Q=qadd(Q,Q,a,b)
    if Q is None:return 0.0
    x=Q[0]
    return .5*math.log(max(abs(x.numerator),x.denominator))/4**steps


def eds(a,b,x,y,mod=None):
    cache={0:0,1:1,2:2*y,3:3*x**4+6*a*x*x+12*b*x-a*a,
        4:4*y*(x**6+5*a*x**4+20*b*x**3-5*a*a*x*x-4*a*b*x-8*b*b-a**3)}
    if mod:cache={k:v%mod for k,v in cache.items()}
    def W(n):
        if n<0:return -W(-n)
        if n not in cache:
            m=n//2
            if n%2:v=W(m+2)*W(m)**3-W(m-1)*W(m+1)**3
            else:
                z=W(m)*(W(m+2)*W(m-1)**2-W(m-2)*W(m+1)**2)
                if mod:v=z*pow(2*y,-1,mod)
                else:
                    assert z%(2*y)==0
                    v=z//(2*y)
            cache[n]=v%mod if mod else v
        return cache[n]
    return W


class Lift:
    # Jacobian arithmetic modulo p^2. Scalar-multiple paths are chosen so no
    # unequal p-adically close finite points require incomplete addition.
    def __init__(self,p,a,b):self.p=p;self.m=p*p;self.a=a%self.m;self.b=b%self.m
    def valid(self,Q):
        X,Y,Z=Q;m=self.m
        return (Y*Y-X**3-self.a*X*Z**4-self.b*Z**6)%m==0 and any(v%self.p for v in Q)
    def point(self,P,dx=0):
        x,y=P;p=self.p;m=self.m
        xx=(x+p*dx)%m
        dy=((xx**3+self.a*xx+self.b-y*y)//p)*pow(2*y,-1,p)%p
        Q=(xx,(y+p*dy)%m,1)
        assert self.valid(Q)
        return Q
    def double(self,Q):
        X,Y,Z=Q;m=self.m
        if Z%m==0:return (1,1,0)
        s=4*X*Y*Y;m0=3*X*X+self.a*Z**4
        x=(m0*m0-2*s)%m;y=(m0*(s-x)-8*Y**4)%m;z=2*Y*Z%m
        out=x,y,z
        assert self.valid(out)
        return out
    def add(self,P,Q):
        m=self.m
        if P[2]%m==0:return Q
        if Q[2]%m==0:return P
        X,Y,Z=P;U,V,W=Q
        u1=X*W*W%m;u2=U*Z*Z%m;s1=Y*W**3%m;s2=V*Z**3%m
        H=(u2-u1)%m;R=(s2-s1)%m
        if H==0:
            if R==0:return self.double(P)
            if R%self.p:return (R*R%m,-R**3%m,0)
        if H%self.p==0 and R%self.p==0:
            raise ArithmeticError('Incomplete Jacobian addition at close unequal finite points')
        x=(R*R-H**3-2*u1*H*H)%m
        y=(R*(u1*H*H-x)-s1*H**3)%m;z=H*Z*W%m
        out=x,y,z
        assert self.valid(out)
        return out
    def mul(self,n,P):
        # Left-to-right keeps prefix scalar below n and handles the final O case.
        R=(1,1,0)
        for bit in bin(n)[2:]:
            R=self.double(R)
            if bit=='1':R=self.add(R,P)
        return R
    def t(self,P):
        assert P[2]%self.p==0 and P[1]%self.p
        return -P[0]*P[2]*pow(P[1],-1,self.m)%self.m
    def affine(self,P):
        if P[2]%self.m==0:return None
        z=pow(P[2],-1,self.m)
        return P[0]*z*z%self.m,P[1]*z**3%self.m
    def section(self,P,N):
        delta=self.mul(N,P);t=self.t(delta)*pow(N,-1,self.m)%self.m
        # Translation by formal parameter -t, to first order. Since p|t,
        # all quadratic terms vanish modulo p^2. Using an unnormalized
        # Jacobian addition here would lose precision through common factors.
        x,y=self.affine(P)
        out=((x-2*y*t)%self.m,(y-(3*x*x+self.a)*t)%self.m,1)
        assert self.valid(out)
        return out
