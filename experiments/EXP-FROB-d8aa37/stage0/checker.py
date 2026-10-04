#!/usr/bin/env python3
"""Read-only independent checker for the fixed Frobenius stage0 package.

No driver import. Field products use nested coefficient convolution and binary
polynomial reduction; curve sums use explicit affine exceptional formulas.
Sage is imported only for independent exact lex ideal calibration. No scientific
objects are constructed on import or by --self-test (fixed GF2 fixtures only).
"""
import argparse
from collections import Counter, defaultdict, OrderedDict
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import time

RUN='RUN-FROB-2404fa'
FILES=('manifest.yaml','raw-result.json','fixtures.json','metrics.json','certificates.json','report.md','roots.jsonl.gz','tuples.jsonl.gz')


def demand(ok,msg):
    if not ok:raise ValueError(msg)


def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()+b'\n'


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def pt(p):return None if p is None else tuple(p)


def binary_product(a,b,modulus):
    out=0
    while b:
        if b&1:out^=a
        b>>=1;a<<=1
    degree=modulus.bit_length()-1
    while out.bit_length()>degree:
        out^=modulus << (out.bit_length()-degree-1)
    return out


def binary_remainder(a,b):
    while a and a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
    return a


def binary_gcd(a,b):
    while b:a,b=b,binary_remainder(a,b)
    return a


def binary_irreducible(coeff):
    p=sum(c<<i for i,c in enumerate(coeff));n=len(coeff)-1;x=2
    for i in range(1,n+1):
        x=binary_product(x,x,p)
        if i<=n//2 and binary_gcd(x^2,p)!=1:return False
    return x==2


class NestedField:
    def __init__(self,f,g):
        self.f,self.g=list(f),list(g)
        self.mod=sum(c<<i for i,c in enumerate(f))
        self.ops=Counter();self.cache=OrderedDict();self.hits=self.evictions=0
        self.bt=[[binary_product(a,b,self.mod) for b in range(8)] for a in range(8)]

    @staticmethod
    def unpack(a):return tuple((a>>(3*i))&7 for i in range(3))

    def mul(self,a,b):
        self.ops['K_multiply_calls']+=1
        key=(a,b)
        if key in self.cache:
            self.hits+=1;v=self.cache.pop(key);self.cache[key]=v;return v
        aa=self.unpack(a);bb=self.unpack(b);cc=[0]*5
        for i in range(3):
            for j in range(3):
                cc[i+j]^=self.bt[aa[i]][bb[j]]
                self.ops['F8_multiply_executed']+=1
                self.ops['F8_add_executed']+=1
        for degree in (4,3):
            lead=cc[degree]
            for j in range(3):
                cc[degree-3+j]^=self.bt[lead][self.g[j]]
                self.ops['F8_multiply_executed']+=1;self.ops['F8_add_executed']+=1
        out=sum(cc[i]<<(3*i) for i in range(3))
        if len(self.cache)==65536:self.cache.popitem(last=False);self.evictions+=1
        self.cache[key]=out
        return out

    def power(self,a,n):
        out=1
        while n:
            if n&1:out=self.mul(out,a)
            a=self.mul(a,a);n//=2
        return out

    def inv(self,a):
        demand(a!=0,'inverse zero');self.ops['K_inverse']+=1
        return self.power(a,510)

    def div(self,a,b):return self.mul(a,self.inv(b))

    def peval(self,coeff,x):
        out=0
        for c in reversed(coeff):out=self.mul(out,x)^c
        return out


class BinaryCurve:
    def __init__(self,field,A,B):self.k=field;self.A=A;self.B=B;self.operations=Counter()

    def neg(self,P):return None if P is None else (P[0],P[0]^P[1])

    def valid(self,P):
        if P is None:return True
        x,y=P;k=self.k
        return k.mul(y,y)^k.mul(x,y)==k.mul(k.mul(x,x),x)^k.mul(self.A,k.mul(x,x))^self.B

    def add(self,P,Q):
        self.operations['point_add']=self.operations['point_add']+1;k=self.k
        if P is None:return Q
        if Q is None:return P
        x,y=P;v,w=Q
        if x==v:
            if y!=w or x==0:return None
            lam=x^k.div(y,x)
            nx=k.mul(lam,lam)^lam^self.A
            ny=k.mul(x,x)^k.mul(lam^1,nx)
        else:
            lam=k.div(y^w,x^v)
            nx=k.mul(lam,lam)^lam^x^v^self.A
            ny=k.mul(lam,x^nx)^nx^y
        out=(nx,ny);demand(self.valid(out),'independent addition left curve');return out

    def scale(self,n,P):
        out=None
        while n:
            if n&1:out=self.add(out,P)
            P=self.add(P,P);n//=2
        return out

    def total(self,points):
        out=None
        for P in points:out=self.add(out,P)
        return out

    def frob(self,P,j=1):return None if P is None else (self.k.power(P[0],8**j),self.k.power(P[1],8**j))

    def points(self,size):
        return [(x,y) for x in range(size) for y in range(size) if self.valid((x,y))]


def integer_factors(n):
    out=[];p=2
    while p*p<=n:
        e=0
        while n%p==0:n//=p;e+=1
        if e:out.append([p,e])
        p+=1
    if n>1:out.append([n,1])
    return out


def prime(n):return n>=2 and integer_factors(n)==[[n,1]]


def verify_field(rec):
    fs=[]
    for low in itertools.product(range(2),repeat=3):
        c=list(low)+[1];ok=binary_irreducible(c);fs.append(dict(coefficients=c,irreducible=ok))
        if ok:break
    demand(fs==rec['f_attempts'] and fs[-1]['coefficients']==rec['f'],'canonical F8 modulus search')
    k=NestedField(rec['f'],rec['g']);gs=[]
    for low in itertools.product(range(8),repeat=3):
        c=list(low)+[1]
        ok=all(k.peval(c,x)!=0 for x in range(8)) # cubic: irreducible iff no root
        gs.append(dict(coefficients=c,irreducible=ok))
        if ok:break
    demand(gs==rec['g_attempts'] and gs[-1]['coefficients']==rec['g'],'canonical extension modulus search')
    hs=[]
    for low in itertools.product(range(2),repeat=9):
        c=list(low)+[1];ok=binary_irreducible(c);hs.append(dict(coefficients=c,irreducible=ok))
        if ok:break
    demand(hs==rec['absolute_attempts'] and hs[-1]['coefficients']==rec['absolute_modulus'],'absolute field construction log')
    modulus=sum(c<<i for i,c in enumerate(rec['absolute_modulus']))
    mapping=rec['canonical_to_absolute'];demand(len(set(mapping))==512,'conversion bijection')
    for a in range(512):
        for b in range(512):
            demand(mapping[a^b]==mapping[a]^mapping[b],'absolute addition conversion')
            demand(mapping[k.mul(a,b)]==binary_product(mapping[a],mapping[b],modulus),'absolute product conversion')
    demand(rec['isomorphism_pairs_checked']==512**2,'isomorphism audit coverage')
    def absolute_eval(coeff,a):
        out=0
        for c in reversed(coeff):out=binary_product(out,a,modulus)^c
        return out
    demand(mapping[2]==next(a for a in range(512) if absolute_eval(rec['f'],a)==0),'first absolute embedding of u')
    demand(mapping[8]==next(a for a in range(512) if absolute_eval([mapping[c] for c in rec['g']],a)==0),'first absolute embedding of z')
    matrix=[[(mapping[1<<j]>>i)&1 for j in range(9)] for i in range(9)]
    demand(matrix==rec['embedding_matrix'],'conversion matrix')
    phi=[[k.unpack(k.power(1<<(3*j),8))[i] for j in range(3)] for i in range(3)]
    demand(phi==rec['phi'],'physical Frobenius matrix')
    normals=[]
    for a in range(512):
        orb=[k.power(a,8**i) for i in range(3)]
        mat=[[k.unpack(orb[j])[i] for j in range(3)] for i in range(3)]
        rank=len(rref(k,mat))
        normals.append(dict(candidate=a,conjugates=orb,rank=rank))
        if rank==3:break
    demand(normals==rec['normal_attempts'] and a==rec['normal'],'normal generator search completeness')
    demand(mat==rec['normal_matrix'],'normal conversion matrix')
    mm=[[[k.unpack(k.mul(1<<(3*h),1<<(3*j)))[i] for j in range(3)] for i in range(3)] for h in range(3)]
    demand(mm==rec['multiplication_matrices'],'multiplication matrices')
    return k


def rref(k,rows):
    A=[list(r) for r in rows];i=0
    for j in range(len(A[0]) if A else 0):
        pivot=next((h for h in range(i,len(A)) if A[h][j]),None)
        if pivot is None:continue
        A[i],A[pivot]=A[pivot],A[i]
        inv=k.inv(A[i][j]);A[i]=[k.mul(v,inv) for v in A[i]]
        for h in range(len(A)):
            if h!=i:
                c=A[h][j];A[h]=[x^k.mul(c,y) for x,y in zip(A[h],A[i])]
        i+=1
    return [r for r in A if any(r)]


def rrefs(dim):
    result=[]
    for piv in itertools.combinations(range(3),dim):
        free=[(i,j) for i in range(dim) for j in range(piv[i]+1,3) if j not in piv]
        for vals in itertools.product(range(8),repeat=len(free)):
            A=[[int(j==piv[i]) for j in range(3)] for i in range(dim)]
            for (i,j),v in zip(free,vals):A[i][j]=v
            result.append(A)
    return sorted(result,key=lambda x:tuple(sum(x,[])))


def verify_subspaces(k,rec):
    candidates=[];stable=[]
    for d in (1,2):
        for rows in rrefs(d):
            enc=[sum(v<<(3*i) for i,v in enumerate(r)) for r in rows]
            fr=[list(k.unpack(k.power(x,8))) for x in enc]
            ok=len(rref(k,rows+fr))==d
            candidates.append(dict(dimension=d,basis=rows,stable=ok))
            if ok:
                piv=[next(i for i,v in enumerate(r) if v) for r in rows]
                phi=[[fr[j][piv[i]] for j in range(d)] for i in range(d)]
                elems=[];coords={}
                for cc in itertools.product(range(8),repeat=d):
                    a=0
                    for c,b in zip(cc,enc):a^=k.mul(c,b)
                    elems.append(a);coords[a]=cc
                stable.append(dict(dimension=d,basis=rows,basis_enc=enc,elements=sorted(elems),phi=phi,coordinate_map=coords))
    demand(candidates==rec['candidates'],'all RREF candidate census')
    demand([{a:b for a,b in v.items() if a!='coordinate_map'} for v in stable]==rec['stable'],'stable subspaces')
    # Independently factor T^3+1 over F8 by root division, including the
    # remaining irreducible quadratic. Verify each supplied kernel and union.
    factors=factor_small(k,[1,0,0,1],8)
    got=sorted((tuple(x['factor']),x['multiplicity']) for x in rec['kernels'])
    demand(got==sorted((tuple(x['coefficients']),x['multiplicity']) for x in factors),'T^3-1 factorization')
    for kr in rec['kernels']:
        members=[]
        for a in range(512):
            val=0
            for i,c in enumerate(kr['factor']):val^=k.mul(c,k.power(a,8**i))
            if val==0:members.append(list(k.unpack(a)))
        basis=rref(k,members)
        demand(basis==kr['basis'] and len(basis)==kr['dimension'],'kernel basis exactness')
    return stable


def verify_curves(k,records):
    selected=[];seen=set();position=0
    for A,B in itertools.product(range(8),repeat=2):
        demand(position<len(records),'curve search prematurely truncated')
        r=records[position];position+=1
        demand(r['A']==A and r['B']==B,'curve search order')
        if not B:demand(r.get('rejection')=='singular_B_zero','singular rejection');continue
        c=BinaryCurve(k,A,B)
        demand(r['discriminant']==B and r['j']==k.inv(B) and r['ordinary'] is True,'binary curve invariants')
        if r['j'] in seen:demand(r.get('rejection')=='duplicate_j','duplicate j');continue
        base=c.points(8);h0=len(base)+1;t=9-h0;ss=[2,t]
        for _ in range(2):ss.append(t*ss[-1]-8*ss[-2])
        order=513-ss[3];fac=integer_factors(order)
        demand([list(p) for p in base]==r['base_points'] and h0==r['base_order'] and t==r['trace'] and ss==r['power_sums'],'base count/trace')
        demand(order==r['order'] and fac==r['factors'],'extension order factorization')
        eligible=[p for p,e in fac if p>=17 and e==1 and h0%p]
        if not eligible:demand(r.get('rejection')=='no_eligible_prime','prime gate rejection');continue
        N=max(eligible);points=c.points(512)
        demand(N==r['N'] and order//N==r['cofactor'],'largest prime/cofactor')
        demand([list(p) for p in points]==r['points'] and len(points)+1==order==r['point_count'],'extension exact count')
        attempts=[];P=None
        for q in points:
            P=c.scale(order//N,q);attempts.append(dict(input=list(q),output=list(P) if P else None))
            if P:break
        demand(attempts==r['generator_attempts'],'generator first-point search')
        if P is None or c.scale(N,P) is not None:
            demand(r.get('rejection')=='generator_order_gate','generator gate');continue
        demand(P==pt(r['P']) and prime(N),'prime order generator')
        M=math.isqrt(N)+(math.isqrt(N)**2<N);baby={};trace=[];Q=None
        for j in range(M):
            baby.setdefault(Q,j);trace.append(dict(kind='baby',index=j,point=list(Q) if Q else None));Q=c.add(Q,P)
        Q=c.frob(P);step=c.neg(c.scale(M,P));mu=None
        for i in range(M+1):
            trace.append(dict(kind='giant',index=i,point=list(Q) if Q else None))
            if Q in baby:
                candidate=(i*M+baby[Q])%N
                if c.scale(candidate,P)==c.frob(P):mu=candidate;break
            Q=c.add(Q,step)
        demand(r['bsgs']==dict(M=M,trace=trace) and mu==r['mu'],'BSGS acquisition trace')
        if mu is None or mu==1 or pow(mu,3,N)!=1:
            demand(r.get('rejection')=='Frobenius_order_gate','mu gate');continue
        if c.total([P,c.frob(P),c.frob(P,2)]) is not None:
            demand(r.get('rejection')=='point_trace_gate','point trace gate');continue
        G=[];Q=P
        for _ in range(1,N):G.append(Q);Q=c.add(Q,P)
        demand(Q is None and sorted(G)==[tuple(p) for p in r['G']],'complete subgroup')
        demand(r['status']=='selected' and r['selected_index']==len(selected),'first selected curves')
        for p,check in zip(sorted(G),r['exceptional_checks']):
            demand(pt(check['P'])==p and pt(check['double'])==c.add(p,p),'doubling control')
            demand(c.add(p,c.neg(p)) is None and c.add(None,p)==p and c.add(p,None)==p,'exceptional group identities')
        demand(len(r['exceptional_checks'])==N-1,'exceptional control completeness')
        selected.append((c,r));seen.add(r['j'])
        if len(selected)==2:break
    demand(position==len(records),'extra candidate records')
    return selected


# Independent sparse polynomials: {exponent_tuple: integer coefficient}.
def padd(a,b):
    out=dict(a)
    for e,c in b.items():
        value=out.get(e,0)^c
        if value:out[e]=value
        else:out.pop(e,None)
    return out


def pmul(k,a,b):
    out={}
    for e,c in a.items():
        for f,d in b.items():
            g=tuple(x+y for x,y in zip(e,f));v=k.mul(c,d)
            out=padd(out,{g:v}) if v else out
    return out


def ppow(k,a,n,dimension):
    out={(0,)*dimension:1}
    while n:
        if n&1:out=pmul(k,out,a)
        a=pmul(k,a,a);n//=2
    return out


def precord(a):return [[list(e),c] for e,c in sorted(a.items())]


def pfrom(rows):return {tuple(e):c for e,c in rows}


def formal(k):
    one={(0,)*5:1};zero={}
    vs=[{tuple(int(i==j) for i in range(5)):1} for j in range(5)]
    a,b,c,d,B=vs
    product=lambda x,y:pmul(k,x,y)
    sq=lambda x:product(x,x)
    s3=padd(padd(sq(padd(padd(product(a,b),product(a,c)),product(b,c))),product(product(a,b),c)),B)
    aa=[sq(padd(a,b)),product(a,b),padd(sq(product(a,b)),B)]
    cc=[sq(padd(c,d)),product(c,d),padd(sq(product(c,d)),B)]
    matrix=[aa+[zero],[zero]+aa,cc+[zero],[zero]+cc]
    determinant={};terms=[]
    for perm in itertools.permutations(range(4)):
        term=one
        for i,j in enumerate(perm):term=product(term,matrix[i][j])
        determinant=padd(determinant,term)
        terms.append(dict(permutation=list(perm),polynomial=precord(term)))
    return s3,determinant,dict(s3=precord(s3),s4=precord(determinant),
        sylvester=[[precord(v) for v in row] for row in matrix],determinant_terms=terms,
        normalization_scalar=1,original_degrees=[2,2])


def eval_sparse(k,p,values):
    out=0
    for e,c in p.items():
        for x,n in zip(values,e):c=k.mul(c,k.power(x,n))
        out^=c
    return out


def trim(p):
    p=list(p)
    while p and not p[-1]:p.pop()
    return p


def divmod_poly(k,a,b):
    a=trim(a);b=trim(b);demand(b,'polynomial division by zero');q=[0]*max(0,len(a)-len(b)+1)
    while len(a)>=len(b):
        d=len(a)-len(b);c=k.div(a[-1],b[-1]);q[d]=c
        for i,v in enumerate(b):a[d+i]^=k.mul(c,v)
        a=trim(a)
    return trim(q),a


def gcd_poly(k,a,b):
    a,b=trim(a),trim(b)
    while b:a,b=b,divmod_poly(k,a,b)[1]
    return [k.div(c,a[-1]) for c in a] if a else []


def factor_small(k,p,size=512):
    p=trim(p);out=[]
    if len(p)<=1:return out
    p=[k.div(c,p[-1]) for c in p]
    for root in range(size):
        mult=0
        while len(p)>1 and k.peval(p,root)==0:
            p,rem=divmod_poly(k,p,[root,1]);demand(not rem,'root division');mult+=1
        if mult:out.append(dict(coefficients=[root,1],degree=1,multiplicity=mult))
    if len(p)>1:
        demand(len(p)<=3,'unexpected irreducible factor degree')
        out.append(dict(coefficients=p,degree=len(p)-1,multiplicity=1))
    return out


def check_fiber(k,xs,rx,B,rec):
    a,b,c=xs;d=rx
    A=[k.power(k.mul(a,b),2)^B,k.mul(a,b),k.power(a^b,2)]
    C=[k.power(k.mul(c,d),2)^B,k.mul(c,d),k.power(c^d,2)]
    demand(A==rec['A'] and C==rec['C'],'specialization padded coefficients')
    deg=[len(trim(p))-1 if trim(p) else None for p in (A,C)]
    gcd=gcd_poly(k,A,C);factors=factor_small(k,gcd)
    demand(deg==rec['affine_degrees'] and gcd==rec['gcd'],'specialization degrees/gcd')
    normalize=lambda rows:sorted(rows,key=lambda x:(x['degree'],x['coefficients'],x['multiplicity']))
    demand(normalize(factors)==normalize(rec['factors']),'common factor multiplicities')
    ia=next((i for i,c in enumerate(reversed(A)) if c),None)
    ic=next((i for i,c in enumerate(reversed(C)) if c),None)
    inf=(ia is None or ia>0) and (ic is None or ic>0)
    both=not trim(A) and not trim(C)
    finite=[dict(root=i,multiplicity=None) for i in range(512)] if both else sorted([dict(root=x['coefficients'][0],multiplicity=x['multiplicity']) for x in factors if x['degree']==1],key=lambda x:x['root'])
    exists=bool(factors) or both
    category='mixed_or_degenerate' if inf and exists else 'infinity_only' if inf else 'finite_common_root' if exists else 'no_common_projective_root'
    demand(rec['finite_K_roots']==finite and normalize(rec['non_K_factors'])==normalize([x for x in factors if x['degree']>1]),'K/nonK finite fiber')
    demand(rec['infinity_orders']==[ia,ic] and rec['infinity_common']==inf and rec['both_zero']==both and rec['category']==category,'projective infinity classification')


def rebuild_ideal(k,V,m,rx,B,form,D):
    n=m*V['dimension'];zero=(0,)*n;xx=[]
    for i in range(m):
        poly={}
        for j,b in enumerate(V['basis_enc']):
            e=[0]*n;e[i*V['dimension']+j]=1;poly[tuple(e)]=b
        xx.append(poly)
    const=lambda a:{zero:a} if a else {}
    args=xx+([const(rx)] if m==3 else [const(rx),{}])+[const(B)]
    sem={}
    for powers,c in form.items():
        term=const(c)
        for a,p in zip(args,powers):term=pmul(k,term,ppow(k,a,p,n))
        sem=padd(sem,term)
    def descend(p):return [{e:k.unpack(c)[j] for e,c in p.items() if k.unpack(c)[j]} for j in range(3)]
    equations=descend(sem);domains=[]
    for x in xx:
        g=const(1)
        for a in D:g=pmul(k,g,padd(x,const(a)))
        domains.extend(descend(g))
    fields=[]
    for i in range(n):
        a=[0]*n;a[i]=8;b=[0]*n;b[i]=1;fields.append({tuple(a):1,tuple(b):1})
    rec=dict(variable_order=['u_%d_%d'%(i,j) for i in range(m) for j in range(V['dimension'])],term_order='degrevlex',
             semaev=precord(sem),descended=[precord(x) for x in equations],domain_generators=[precord(x) for x in domains],field_generators=[precord(x) for x in fields])
    return equations+domains+fields,rec


def substitute_linear(k,p,sub,n):
    out={}
    for ex,c in p.items():
        term={(0,)*n:c}
        for v,e in zip(sub,ex):term=pmul(k,term,ppow(k,v,e,n))
        out=padd(out,term)
    return out


def check_covariance(k,V,m,gens,other,rec,phi):
    d=V['dimension'];n=d*m;zero=(0,)*n;sub=[]
    for i in range(m):
        for j in range(d):
            p={}
            for h in range(d):
                e=[0]*n;e[i*d+h]=1
                if V['phi'][j][h]:p[tuple(e)]=V['phi'][j][h]
            sub.append(p)
    want=[]
    for start,length in ((0,3),(3,3*m)):
        for block in range(start,start+length,3):
            for j in range(3):
                left=substitute_linear(k,other[block+j],sub,n);right={}
                for h in range(3):right=padd(right,pmul(k,{zero:phi[j][h]} if phi[j][h] else {},gens[block+h]))
                demand(left==right,'independent coefficient covariance')
                want.append(dict(generator=block+j,left=precord(left),right=precord(right)))
    start=3+3*m
    for i in range(m):
        for j in range(d):
            left=substitute_linear(k,other[start+i*d+j],sub,n);right={}
            for h in range(d):right=padd(right,pmul(k,{zero:V['phi'][j][h]} if V['phi'][j][h] else {},gens[start+i*d+h]))
            demand(left==right,'independent field covariance')
            want.append(dict(generator=start+i*d+j,left=precord(left),right=precord(right)))
    demand(want==rec['witnesses'] and rec['corrupted_add_one_rejected'] is True,'transport witness record')
    demand(padd(pfrom(want[0]['left']),{zero:1})!=pfrom(want[0]['right']),'corrupted transport control')


def leading(p):return max(p,key=lambda e:(sum(e),tuple(-v for v in reversed(e))))


def independent_buchberger(k,gens,key):
    basis=[];trace=[];degree=0
    def emit(x):trace.append(dict(type='buchberger',cell_target=key,record=x))
    def scale(p,c,shift):return {tuple(x+y for x,y in zip(e,shift)):k.mul(a,c) for e,a in p.items() if k.mul(a,c)}
    def normalize(p):
        lead=p[leading(p)];return {e:k.div(c,lead) for e,c in p.items()}
    def reduce(p):
        nonlocal degree
        p=dict(p);r={}
        while p:
            degree=max(degree,max(map(sum,p)));e=leading(p);c=p[e]
            for j,g in enumerate(basis):
                f=leading(g)
                if all(x>=y for x,y in zip(e,f)):
                    shift=tuple(x-y for x,y in zip(e,f));mult=k.div(c,g[f])
                    emit(dict(kind='reduce',reducer=j,before=precord(p),multiplier=precord({shift:mult})))
                    p=padd(p,scale(g,mult,shift));break
            else:r[e]=c;del p[e]
        return r
    for i,g in enumerate(gens):
        h=reduce(g)
        if h:
            h=normalize(h);basis.append(h)
            emit(dict(kind='initial_basis',generator=i,index=len(basis)-1,polynomial=precord(h)))
    pairs={(i,j) for j in range(len(basis)) for i in range(j)}
    def lcm(i,j):return tuple(max(x,y) for x,y in zip(leading(basis[i]),leading(basis[j])))
    while pairs:
        i,j=min(pairs,key=lambda ij:(sum(lcm(*ij)),*ij));pairs.remove((i,j));l=lcm(i,j)
        a=scale(basis[i],1,tuple(x-y for x,y in zip(l,leading(basis[i]))))
        b=scale(basis[j],1,tuple(x-y for x,y in zip(l,leading(basis[j]))));sp=padd(a,b)
        emit(dict(kind='pair',indices=[i,j],lcm=precord({l:1}),spoly=precord(sp)))
        degree=max(degree,max(map(sum,sp),default=0));h=reduce(sp)
        if h:
            h=normalize(h);n=len(basis);basis.append(h);pairs.update((z,n) for z in range(n))
            emit(dict(kind='new_basis',index=n,polynomial=precord(h)))
    return basis,dict(basis=[precord(g) for g in basis],operational_d_solve=degree,theoretical_d_reg=None,first_fall_degree=None),trace


def check_calibration(k,V,m,gens,ideal_rec,record,expected_roots,trace,key):
    # Separate nested arithmetic reconstructs every polynomial before the
    # checker asks Sage only for an in-process lex basis over the base field.
    import sage.all as s
    R2=s.PolynomialRing(s.GF(2),'u');u=R2.gen()
    F=s.GF(8,'u',modulus=sum(R2(c)*u**i for i,c in enumerate(k.f)))
    values=[sum((F.gen()**j for j in range(3) if (i>>j)&1),F.zero()) for i in range(8)]
    inverse={v:i for i,v in enumerate(values)}
    L=s.PolynomialRing(F,names=ideal_rec['variable_order'],order='lex')
    sg=[L({e:values[c] for e,c in g.items()}) for g in gens]
    gb=list(L.ideal(sg).groebner_basis(algorithm='libsingular:std'))
    encoded=lambda p:[[list(map(int,e)),inverse[c]] for e,c in sorted(p.dict().items())]
    demand(record['lex_basis']==[encoded(g) for g in gb],'independent exact lex basis')
    want=[]
    for coords in itertools.product(range(8),repeat=m*V['dimension']):
        if all(eval_sparse(k,g,coords)==0 for g in gens):want.append(coords)
    demand(want==[tuple(x) for x in record['coordinate_roots']]==sorted(expected_roots),'complete calibration roots')
    demand(all(g(*[values[v] for v in co])==0 for g in gb for co in want),'lex finite root substitution')
    _,grev,ind_trace=independent_buchberger(k,gens,key)
    demand(grev==record['grevlex'],'independent deterministic grevlex basis/degree')
    demand(trace==ind_trace,'complete deterministic S-pair/reduction trace')


class Cursor:
    def __init__(self,path,kind):
        self.f=gzip.open(path,'rb');self.pending=None;self.lines=0
        header=self.take('header')
        demand(header==dict(type='header',schema='frob.stage0.'+kind+'.v1',experiment='EXP-FROB-d8aa37'),'stream schema')

    def peek(self):
        if self.pending is None:
            raw=self.f.readline()
            if not raw:return None
            self.lines+=1
            row=json.loads(raw)
            demand(canon(row)==raw,'noncanonical JSONL bytes')
            self.pending=row
        return self.pending

    def take(self,kind):
        row=self.peek();demand(row is not None and row.get('type')==kind,'expected stream record '+kind)
        self.pending=None;return row

    def finish(self,status,outcome):
        demand(self.take('terminal')==dict(type='terminal',status=status,outcome=outcome),'terminal stream outcome')
        demand(self.peek() is None,'trailing stream records');self.f.close()


def verify_stream_binding(path,rec):
    demand(digest(path)==rec['compressed_sha256'] and path.stat().st_size==rec['compressed_bytes'],'compressed stream hash/size')
    with open(path,'rb') as f:header=f.read(10)
    demand(header[:3]==b'\x1f\x8b\x08' and header[3]==0 and header[4:8]==bytes(4),'gzip canonical header')
    h=hashlib.sha256();size=lines=0
    with gzip.open(path,'rb') as f:
        for line in f:
            h.update(line);size+=len(line);lines+=1
    demand(h.hexdigest()==rec['decompressed_sha256'] and size==rec['decompressed_bytes'] and lines==rec['lines'],'decompressed stream binding')


def verify_panel(k,curves,spaces,forms,fixtures,certs,metrics,result,run_dir):
    roots=Cursor(run_dir/'roots.jsonl.gz','roots');tuples=Cursor(run_dir/'tuples.jsonl.gz','tuples')
    for r in fixtures['curve_candidates']:
        demand(tuples.take('curve_candidate')==dict(type='curve_candidate',record=r),'candidate stream fidelity')
    for r in fixtures['subspaces']['candidates']:
        demand(tuples.take('subspace_candidate')==dict(type='subspace_candidate',record=r),'subspace stream fidelity')
    cell_records=[];domain_records=[];cal_targets=[];set_summaries=[];selected=None
    executed_tuples=executed_lifts=0
    for ci,(curve,rec) in enumerate(curves):
        G=sorted(pt(p) for p in rec['G'])
        for vi,V in enumerate(spaces):
            F=[p for p in G if p[0] in V['elements']];D=sorted({p[0] for p in F});lifts={x:[p for p in F if p[0]==x] for x in D}
            wrong=V['elements']==list(range(8))
            if wrong:
                demand(all(p[1]<8 for p in rec['points'] if p[0]<8),'wrong-base x/y implication')
                demand(not F and not [p for p in G if p[0]<8 and p[1]<8],'wrong-base subgroup intersection')
            domain_records.append(dict(curve=ci,subspace=vi,F=[list(p) for p in F],D=D,wrong_base=wrong,wrong_base_control_pass=wrong,empty=not D))
            for m in (2,3):
                key=[ci,vi,m];form=forms[m-2]
                if selected is None and D:selected=key
                calibration=key==selected
                counts=Counter();nt=0
                for points in itertools.product(F,repeat=m):
                    row=tuples.take('signed_tuple');nt+=1;executed_tuples+=1
                    total=curve.total(points);counts[total]+=1
                    expected=dict(type='signed_tuple',cell=key,points=[list(p) for p in points],xs=[p[0] for p in points],sum=list(total) if total else None,
                        intermediate_sums=[list(q) if q else None for q in [curve.total(points[:i]) for i in range(1,m+1)]],
                        stabilizer=[j for j in range(3) if tuple(curve.frob(p,j) for p in points)==points])
                    demand(row==expected,'signed tuple coverage/sum/stabilizer')
                sums=[dict(target=list(q) if q else None,count=n) for q,n in sorted(counts.items(),key=lambda item:(item[0] is not None,item[0] or ()))]
                demand(tuples.take('signed_cell_total')==dict(type='signed_cell_total',cell=key,expected=len(F)**m,executed=nt,sum_counts=sums,domain_empty=not F),'signed total')
                rootsets={};liftsets={};target_metrics=[];seen_cal={};cache_eq={};cache_hits=cache_miss=0
                ideal_entries=OrderedDict();ideal_hits=ideal_misses=ideal_evictions=0
                cal_hits=cal_misses=cal_evictions=0;cal_entries=OrderedDict()
                def cached_ideal(rx):
                    nonlocal ideal_hits,ideal_misses,ideal_evictions
                    if rx in ideal_entries:
                        ideal_hits+=1;answer=ideal_entries.pop(rx);ideal_entries[rx]=answer;return answer,True
                    ideal_misses+=1
                    answer=rebuild_ideal(k,V,m,rx,curve.B,form,D)
                    if len(ideal_entries)==65536:ideal_entries.popitem(last=False);ideal_evictions+=1
                    ideal_entries[rx]=answer;return answer,False
                for target in G:
                    pi=curve.frob(target);orbit=[target,pi,curve.frob(target,2)]
                    demand(len(set(orbit))==3 and curve.frob(target,3)==target,'target orbit')
                    rs=set();ls=set();valid=raw=spurious=0
                    for xs in itertools.product(D,repeat=m):
                        args=list(xs)+([target[0]] if m==3 else [target[0],0])+[curve.B]
                        if eval_sparse(k,form,args):continue
                        rs.add(xs);raw+=1
                        row=roots.take('root');all_lifts=[];good=[]
                        for points in itertools.product(*(lifts[x] for x in xs)):
                            total=curve.total(points);executed_lifts+=1
                            all_lifts.append(dict(points=[list(p) for p in points],sum=list(total) if total else None))
                            if total==target:good.append([list(p) for p in points])
                        valid+=len(good)
                        if good:ls.add(xs)
                        else:spurious+=1
                        mapped=[k.power(x,8) for x in xs]
                        demand(eval_sparse(k,form,mapped+([pi[0]] if m==3 else [pi[0],0])+[curve.B])==0,'root transport evaluation')
                        for points in good:demand(curve.total([curve.frob(pt(p)) for p in points])==pi,'signed transported lift')
                        expected=dict(type='root',cell=key,target=list(target),xs=list(xs),lifts=all_lifts,valid_lifts=good,multiplicity=len(good),transported_xs=mapped,
                            stabilizer=[j for j in range(3) if tuple(k.power(x,8**j) for x in xs)==xs],repeated_coordinates=len(set(xs))<m)
                        if m==3:
                            check_fiber(k,xs,target[0],curve.B,row['fiber']);expected['fiber']=row['fiber']
                        demand(row==expected,'complete root/lift record')
                    demand(valid==counts[target],'all signed sums reconciled with roots')
                    (gens,ideal_rec),hit=cached_ideal(target[0]);(other,_),phit=cached_ideal(pi[0])
                    row=roots.take('ideal');eqkey=hashlib.sha256(canon(ideal_rec)).hexdigest()
                    demand(row['cell']==key and pt(row['target'])==target and row['record']==ideal_rec and row['equation_key']==eqkey,'descended ideal exact definition')
                    demand(row['cache_hit']==hit and row['pi_cache_hit']==phit,'ideal cache accounting')
                    check_covariance(k,V,m,gens,other,row['covariance'],fixtures['field']['phi'])
                    if calibration:
                        trace=[]
                        while roots.peek() is not None and roots.peek().get('type')=='buchberger':trace.append(roots.take('buchberger'))
                        row=roots.take('calibration');cal=row['record']
                        expected_coords=sorted(tuple(c for x in xs for c in V['coordinate_map'][x]) for xs in rs)
                        ch=eqkey in cal_entries
                        if ch:
                            cal_hits+=1;prior=cal_entries.pop(eqkey);cal_entries[eqkey]=prior
                            demand(prior==cal and not trace,'cached calibration equality/trace allocation')
                        else:
                            cal_misses+=1
                            if len(cal_entries)==65536:cal_entries.popitem(last=False);cal_evictions+=1
                            check_calibration(k,V,m,gens,ideal_rec,cal,expected_coords,trace,key+[list(target)])
                            cal_entries[eqkey]=cal
                        demand(cal['equation_key']==eqkey and row['cache_hit']==ch and row['cell']==key and pt(row['target'])==target and row['exact_signed_lift_count']==valid,'calibration target/identity')
                        demand([tuple(x) for x in cal['coordinate_roots']]==expected_coords,'cached calibration complete roots')
                        cal_targets.append(dict(cell=key,target=list(target),equation_key=eqkey,cache_hit=ch,root_count=raw,lift_count=valid))
                    metric=dict(target=list(target),x_tuples=len(D)**m,raw_roots=raw,valid_lifts=valid,roots_with_lifts=len(ls),spurious_roots=spurious)
                    demand(roots.take('target_total')==dict(type='target_total',cell=key,record=metric),'all-target summary')
                    target_metrics.append(metric);rootsets[target]=rs;liftsets[target]=ls
                for target in G:
                    orbit=[target,curve.frob(target),curve.frob(target,2)];A,B,C=[rootsets[p] for p in orbit]
                    shared=sorted(A&B);union=sorted(A|B)
                    for xs in shared:
                        want=[]
                        for R in orbit[:2]:
                            want.append([[list(p) for p in points] for points in itertools.product(*(lifts[x] for x in xs)) if curve.total(points)==R])
                        demand(roots.take('overlap_witness')==dict(type='overlap_witness',cell=key,targets=[list(p) for p in orbit[:2]],xs=list(xs),target_lifts=want),'actual signed overlap witness')
                    recset=dict(cell=key,target=list(target),orbit=[list(p) for p in orbit],zero_set_ideal_sum_overlap=len(shared),zero_set_ideal_intersection_union=len(union),
                        prefix_union_cardinalities=[len(A),len(A|B),len(A|B|C)],shared_roots=[list(x) for x in shared],union_roots=[list(x) for x in union],
                        shared_roots_with_both_signed_targets=[list(x) for x in sorted(liftsets[target]&liftsets[orbit[1]])])
                    demand(roots.take('set_operations')==dict(type='set_operations',record=recset),'ideal sum/intersection set semantics')
                    set_summaries.append({a:b for a,b in recset.items() if a not in ('shared_roots','union_roots','shared_roots_with_both_signed_targets')})
                cell=dict(cell=key,F_size=len(F),D_size=len(D),signed_tuples=nt,targets=len(G),target_metrics=target_metrics,calibration=calibration,
                    ideal_cache=dict(limit=65536,entries=len(ideal_entries),hits=ideal_hits,misses=ideal_misses,evictions=ideal_evictions),
                    calibration_cache=dict(limit=65536,entries=len(cal_entries),hits=cal_hits,misses=cal_misses,evictions=cal_evictions),empty=not D)
                demand(roots.take('cell_total')==dict(type='cell_total',record=cell),'cell totals/cache accounting');cell_records.append(cell)
    demand(cell_records==result['cells'],'manifest cell summary')
    demand(domain_records==fixtures['domains'],'factor domains and wrong-base controls')
    coverage=certs['controls']['coverage']
    demand(coverage=={
        'A2_sign_fiber':{'target_comparisons':len(set_summaries),'completed_without_early_stop':True},
        'wrong_base_Fq':{'domains_checked':sum(d['wrong_base'] for d in domain_records)},
        'stableV1_V2':{'stable_subspaces':len(spaces),'complete_RREF_and_kernel_checks':True},
        'k1_identity_and_set_operations':{'target_orbits_checked':len(set_summaries)},
        'Frobenius_covariance_and_stabilizers':{'targets_checked':sum(c['targets'] for c in cell_records)},
        'S3_S4_independent_construction':{'producer_formal_determinant':True,'independent_checker_pending':True},
        'projective_degree_drop':{'fixed_controls':3,'all_m3_roots_retained':True},
        'exceptional_point_addition':{'selected_curve_nonzero_points_checked':sum(len(r['G']) for _,r in curves)},
        'complete_lex_calibration':{'cell':selected,'targets_checked':len(cal_targets),'status':'complete' if selected is not None else 'calibration_unavailable'},
        'invalid_relation_rejection':{'selected_generators_checked':len(curves),'target_coefficient_mutations_checked':sum(c['targets'] for c in cell_records)}},'all required control coverage')
    demand(cal_targets==certs['calibration_targets'],'calibration summary all targets')
    demand(set_summaries==certs['set_operations'],'overlap/union certificate summary')
    demand(result['calibration_selected']==selected and result['calibration_status']==('complete' if selected else 'calibration_unavailable'),'solution-independent calibration choice')
    outcome='complete' if len(curves)==2 and selected is not None else 'structural_unavailable' if len(curves)<2 else 'calibration_unavailable'
    demand(result['outcome']==outcome and result['selected_curves']==len(curves) and result['domain_census_complete'] is True,'complete domain coverage/outcome')
    demand(result['producer_stage0_checks_complete']==(outcome=='complete'),'producer stage gate')
    demand(metrics['operations'].get('executed_signed_tuples',0)==executed_tuples and metrics['operations'].get('executed_root_lift_checks',0)==executed_lifts,'executed operation counts')
    roots.finish('completed_valid',outcome);tuples.finish('completed_valid',outcome)
    return dict(verified_cells=len(cell_records),verified_targets=sum(x['targets'] for x in cell_records),verified_signed_tuples=executed_tuples,verified_root_lift_checks=executed_lifts)


def verify_controls(k,cert):
    c=cert['controls']
    demand(c['formal_resultant_determinant'] is True and c['invalid_generator_relation_rejection'] is True,'required controls')
    wanted=[]
    for a,b in [([0,1,0],[1,1,0]),([0,0,0],[0,0,0]),([1,0,0],[0,0,0])]:
        wanted.append(dict(A=a,C=b,gcd=gcd_poly(k,a,b),formal_resultant=0,infinity_common=True,both_zero=not trim(a) and not trim(b)))
    demand(c['projective_fixed_controls']==wanted,'fixed projective controls')
    demand(gcd_poly(k,[0,1],[1,1])==[1],'known-false finite-root implication')


def verify(run_dir):
    demand(platform.system()=='Linux','checker scientific execution requires Linux')
    demand(resource.getrlimit(resource.RLIMIT_AS)[0]==8192*1024*1024,'checker requires exact adapter RLIMIT_AS')
    demand(os.getpgrp()>0 and run_dir.name==RUN,'checker process/run identity')
    start=time.perf_counter();cpu=time.process_time()
    before={name:digest(run_dir/name) for name in FILES}
    for name in FILES:demand((run_dir/name).stat().st_size>0,'empty required artifact '+name)
    manifest=json.loads((run_dir/'manifest.yaml').read_text())['run']
    result=json.loads((run_dir/'raw-result.json').read_text())
    demand(manifest['id']==RUN and manifest['experiment_id']=='EXP-FROB-d8aa37','canonical run identifiers')
    demand(manifest['result']==result,'raw/manifest result mismatch')
    demand(manifest['status']=='completed_valid' and result['valid'] is True,'failed producer is not validated math')
    demand(result['certificate']['kind']=='none' and result['full_v1_complete'] is False and result['stage0_gate_complete'] is False and result['independent_review_pending'] is True,'claim boundary')
    for name,value in manifest['artifact_sha256'].items():demand(before[name]==value,'driver artifact binding '+name)
    demand(set(manifest['artifact_sha256'])==set(FILES)-{'manifest.yaml'},'exact seven-file manifest binding')
    for name,value in manifest['inputs']['stable_adapter_hashes'].items():demand(digest(run_dir/name)==value,'adapter stable input binding')
    launch=json.loads((run_dir/'launch.json').read_text());env=json.loads((run_dir/'environment.json').read_text())
    demand(manifest['code']['commit']==launch['authority']['commit'] and manifest['code']['command']==(run_dir/'command.txt').read_text(),'executing revision/command')
    demand(manifest['environment']['adapter_environment']==env,'adapter environment preservation')
    repo=Path(__file__).resolve().parents[3]
    for relative,expected in env['source_sha256'].items():demand(digest(repo/relative)==expected,'source binding '+relative)
    demand(digest(repo/'experiments/EXP-FROB-d8aa37/specification-stage0-v2.yaml')==env['specification_sha256']==manifest['inputs']['specification_sha256'],'specification hash')
    demand(isinstance(manifest['code']['dirty'],bool) and manifest['code']['dirty']==bool(manifest['code']['dirty_status_at_driver_start']),'truthful recorded dirty flag')
    fixtures=json.loads((run_dir/'fixtures.json').read_text());certs=json.loads((run_dir/'certificates.json').read_text());metrics=json.loads((run_dir/'metrics.json').read_text())
    for name,rec in metrics['streams'].items():verify_stream_binding(run_dir/name,rec)
    demand(set(metrics['streams'])=={'roots.jsonl.gz','tuples.jsonl.gz'},'stream coverage')
    k=verify_field(fixtures['field']);curves=verify_curves(k,fixtures['curve_candidates']);spaces=verify_subspaces(k,fixtures['subspaces'])
    S3,S4,frecord=formal(k);demand(frecord==certs['formal'],'independent formal resultant coefficients and multiplicity trace')
    # Explicit nonzero coefficient corruption is detected in memory.
    corrupt=dict(S4);e=next(iter(corrupt));corrupt[e]^=1
    demand(corrupt!=S4,'formal polynomial mutation rejection')
    verify_controls(k,certs)
    counts=verify_panel(k,curves,spaces,(S3,S4),fixtures,certs,metrics,result,run_dir)
    after={name:digest(run_dir/name) for name in FILES};demand(before==after,'checker modified artifacts')
    output=dict(checker='independent_nested_arithmetic',valid=True,scope='fixed_stage0_only',
        independent_scientific_review=False,counts=counts,operation_counts=dict(k.ops),
        opaque_inprocess_libsingular_lex_basis_calls=len({r['equation_key'] for r in certs['calibration_targets']}),
        field_cache=dict(limit=65536,entries=len(k.cache),hits=k.hits,evictions=k.evictions),
        group_operations=[dict(c.operations) for c,_ in curves],
        wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        opaque_internals='Only in-process Sage base-field lex basis internals are opaque; counted invocation count equals unique calibration equation count.',
        artifact_bytes=sum((run_dir/n).stat().st_size for n in FILES),artifacts_unchanged=True)
    print(canon(output).decode(),end='');return 0


def self_test():
    # A strict GF2 arithmetic stub prevents accidental stage0 construction.
    class F2:
        def mul(self,a,b):
            demand(a in (0,1) and b in (0,1),'non-F2 self-test coefficient');return a&b
        def div(self,a,b):demand(b==1,'F2 division');return a
        def power(self,a,n):return 1 if n==0 else a
        def unpack(self,a):return (a,0,0)
        def peval(self,c,x):
            out=0
            for v in reversed(c):out=self.mul(out,x)^v
            return out
    k=F2()
    demand(binary_product(3,3,7)==2,'fixed GF4 reduction fixture')
    demand(gcd_poly(k,[0,1],[1,1])==[1],'F2 projective/affine control')
    demand(gcd_poly(k,[],[])==[] and gcd_poly(k,[1],[])==[1],'zero and constant gcd')
    form={tuple(int(i==j) for i in range(5)):1 for j in (0,1,2,4)}
    V={'dimension':1,'basis_enc':[1],'phi':[[1]]}
    gens0,ideal_rec=rebuild_ideal(k,V,2,1,1,form,[0,1])
    n=2;sub=[{(1,0):1},{(0,1):1}]
    witness={'witnesses':[{'generator':i,'left':precord(g),'right':precord(g)} for i,g in enumerate(gens0)],'corrupted_add_one_rejected':True}
    check_covariance(k,V,2,gens0,gens0,witness,[[1,0,0],[0,1,0],[0,0,1]])
    curve=BinaryCurve(k,0,1);P=(1,0);T=(0,1)
    demand(curve.add(P,P)==T and curve.add(P,curve.neg(P)) is None,'fixed binary group fixture')
    points=[None,(0,1),(1,0),(1,1)]
    demand(all(curve.add(curve.add(a,b),c)==curve.add(a,curve.add(b,c)) for a,b,c in itertools.product(points,repeat=3)),'fixed group associativity')
    x={(1,0):1};y={(0,1):1}
    gens=[padd(pmul(k,x,x),x),padd(y,x)]
    basis,record,trace=independent_buchberger(k,gens,['fixed_F2_fixture'])
    demand([p for p in itertools.product(range(2),repeat=2) if all(eval_sparse(k,g,p)==0 for g in basis)]==[(0,0),(1,1)],'fixed F2 sparse Groebner roots')
    demand(canon({'z':1,'a':[True,None]})==b'{"a":[true,null],"z":1}\n','canonical JSON')
    print(canon(dict(test='independent_fixed_nonstage',passed=True,stage0_constructions=0,buchberger_trace_records=len(trace),fixed_generic_ideal_sha256=hashlib.sha256(canon(ideal_rec)).hexdigest())).decode(),end='')


def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run-dir',type=Path);group.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:self_test();return 0
    return verify(args.run_dir.resolve())


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print(canon(dict(valid=False,error_type=type(e).__name__,error=str(e))).decode(),file=sys.stderr,end='')
        sys.exit(1)
