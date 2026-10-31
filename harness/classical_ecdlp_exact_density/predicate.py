"""Source-bound public affine/Miller predicate and literal decoder specification.

All tables built elsewhere are diagnostic work. No old producer imports, entropy,
reference bank or candidate selection occurs here. Counts are named diagnostic
calls, not the old field-operation or attack-cost ledger.
"""
from collections import Counter
from itertools import combinations, product
from math import comb

PRIMARY = {'id':'circuit2.a1','kind':'candidate','alpha':-2,'beta':-1,'base_multiplier':1}
CELLS = [(t,e) for t in (0,1,2) for e in (0,2)]

class Group:
    def __init__(self, model):
        self.model = dict(model)
        self.p,self.a,self.b,self.r = (model[k] for k in ('p','a','b','r'))
        if self.p <= 3 or self.p%2 == 0: raise ValueError('unsupported field')
        self.a %= self.p; self.b %= self.p
        self.counts = Counter()
    def member(self, P):
        self.counts['membership_calls'] += 1
        return P is None or (isinstance(P,(list,tuple)) and len(P)==2 and
            all(type(v) is int and 0<=v<self.p for v in P) and
            (P[1]*P[1]-P[0]**3-self.a*P[0]-self.b)%self.p==0)
    def inv(self, v):
        self.counts['field_inverse_calls'] += 1
        return pow(v%self.p,-1,self.p)
    def addline(self,U,V):
        self.counts['group_addline_calls'] += 1
        if U is None or V is None: return (V if U is None else U),0
        x,y=U; X,Y=V; p=self.p
        if x==X:
            if (y+Y)%p==0: return None,0
            if y!=Y: raise ValueError('invalid same abscissa')
            m=(3*x*x+self.a)*self.inv(2*y)%p
        else: m=(Y-y)*self.inv(X-x)%p
        Z=(m*m-x-X)%p
        return (Z,(m*(x-Z)-y)%p),m
    def add(self,U,V): return self.addline(U,V)[0]
    def mul(self,n,P):
        self.counts['scalar_multiply_calls'] += 1
        if n<0: return self.mul(-n,None if P is None else (P[0],-P[1]%self.p))
        R=None
        for b in bin(n)[2:]:
            R=self.add(R,R)
            if b=='1': R=self.add(R,P)
        return R
    def z(self,P,inverse_r=None):
        self.counts['miller_calls'] += 1
        if P is None: return 0
        inv=self.inv(self.r) if inverse_r is None else inverse_r
        T=P; d=0
        for b in bin(self.r)[3:]:
            T,m=self.addline(T,T); d=(2*d+m)%self.p
            if b=='1': T,m=self.addline(T,P); d=(d+m)%self.p
        if T is not None: raise ValueError('point outside declared subgroup')
        return -d*inv%self.p

def answer(status,bit=None,reason=None,**fields):
    return dict(status=status,bit=bit,reason=reason,z=None,g=None,anchor=None,normalized=None,**{}) | fields

class Prepared:
    def __init__(self,model,base,arm=PRIMARY):
        self.g=Group(model); self.model=dict(model); self.base=None if base is None else tuple(base); self.arm=dict(arm)
        self.reason=None; self.inverse_r=self.z_base=self.c=self.anchor=self.inverse_anchor=self.root_factor=None
        p,r=self.g.p,self.g.r; P=self.base
        if p%4!=3 or r<=2 or r%2==0 or r==p: self.reason='DOMAIN_UNSUPPORTED'; return
        if P is None or not self.g.member(P): raise ValueError('invalid base')
        if P[1]==0: self.reason='ZERO_BASE_Y'; return
        self.inverse_r=self.g.inv(r); self.z_base=self.g.z(P,self.inverse_r)
        if arm['kind']=='wrong_root':
            self.anchor=pow((P[0]**3+self.g.a*P[0]+self.g.b)%p,(p+1)//4,p)
            if self.anchor==0: self.reason='ZERO_ANCHOR'; return
            self.root_factor=P[1]*self.g.inv(self.anchor)%p; return
        if self.z_base==0: self.reason='ZERO_BASE_Z'; return
        self.c=self.z_base*self.g.inv(P[1])%p
        self.anchor=(1+arm['alpha'])*self.z_base%p
        if self.anchor==0: self.reason='ZERO_ANCHOR'; return
        self.inverse_anchor=self.g.inv(self.anchor)
    def evaluate(self,P):
        self.g.counts['predicate_calls'] += 1
        if self.reason: return answer('UNDEFINED',reason=self.reason,anchor=self.anchor)
        if not self.g.member(P): raise ValueError('invalid query')
        if P is None: return answer('BIT',bit=0,z=0,anchor=self.anchor)
        p=self.g.p; x,y=P
        if self.arm['kind']=='wrong_root':
            root=self.root_factor*pow((x**3+self.g.a*x+self.g.b)%p,(p+1)//4,p)%p
            if y==root: bit=0
            elif y==-root%p: bit=1
            else: return answer('UNDEFINED',reason='ROOT_SIGN_MISMATCH',anchor=self.anchor,root=root)
            return answer('BIT',bit=bit,anchor=self.anchor,root=root)
        z=self.g.z(P,self.inverse_r)
        g=(z+self.c*y*(self.arm['alpha']+self.arm['beta']*self.c*(x-self.base[0])))%p
        if g==0: return answer('UNDEFINED',reason='ZERO_NUMERATOR',z=z,g=g,anchor=self.anchor)
        normalized=g*self.inverse_anchor%p
        character=pow(normalized,(p-1)//2,p)
        if character not in (1,p-1): raise ValueError('non-Legendre character')
        return answer('BIT',bit=int(character!=1),z=z,g=g,anchor=self.anchor,normalized=normalized)

def words(bits,t):
    erased=[i for i,b in enumerate(bits) if b is None]; defined=[i for i,b in enumerate(bits) if b is not None]
    for assignment in product((0,1),repeat=len(erased)):
        for w in range(min(t,len(defined))+1):
            for flipped in combinations(defined,w):
                out=list(bits)
                for i,b in zip(erased,assignment): out[i]=b
                for i in flipped: out[i]^=1
                V=0
                for b in out: V=2*V+b
                yield dict(value=V,bits=out,erasure_assignment=list(assignment),flipped_indices=list(flipped))

def interval(r,L,V):
    D=1<<L; k=(r*V+D-1)//D
    return k,0<=k<r and D*k<r*(V+1)

def literal_decode(bits,r,t,e_cap,a=1,b=1,checks=None,strict_status=None):
    """Literal finite list, with separate unconditional checks for every legal word.

    checks(k,x) must evaluate both equations and return their Boolean pair.
    This routine retains the original per-word data for regression/fixed controls.
    """
    if (t,e_cap) not in CELLS: raise ValueError('unfrozen cell')
    if not (1<=a<r and 1<=b<r): raise ValueError('nonzero multipliers required')
    L=len(bits); e=bits.count(None); capped=e>e_cap; inv=pow(b,-1,r)
    expected=0 if capped else (1<<e)*sum(comb(L-e,w) for w in range(min(t,L-e)+1))
    rows=[]; candidates=set(); recoveries=[]; zero=0
    for row in (() if capped else words(bits,t)):
        k,legal=interval(r,L,row['value']); x=tc=oc=None
        if legal:
            x=(a*inv%r)*k%r
            tc,oc=checks(k,x) if checks else (False,False)
            if type(tc) is not bool or type(oc) is not bool: raise ValueError('both checks must be Boolean')
            if x: candidates.add(x)
            else: zero+=1
            if tc and oc: recoveries.append(x)
        rows.append(row | dict(candidate_scalar_prime=k,legal=legal,candidate_scalar=x,
            public_checks=dict(transformed=tc,original=oc),status='RECOVERED' if tc and oc else 'REJECTED_FINAL_VERIFICATION' if legal else 'EMPTY_INTERVAL'))
    if len(rows)!=expected: raise AssertionError('word count')
    status='CAPPED_ERASURES' if capped else 'RECOVERED' if recoveries else 'EMPTY_INTERVAL' if rows and all(w['status']=='EMPTY_INTERVAL' for w in rows) else 'REJECTED_FINAL_VERIFICATION'
    if (t,e_cap)==(0,0):
        if strict_status is None: raise ValueError('original strict status required')
        status=strict_status
    return dict(radius=t,erasure_cap=e_cap,L=L,erasures=e,capped=capped,status=status,expected_word_count=expected,word_count=len(rows),words=rows,M=len(candidates),distinct_nonzero_candidates=sorted(candidates),zero_candidate_checks=zero,recovered_scalars=sorted(set(recoveries)),scalar=recoveries[0] if recoveries else None)

def attempt(prepared,base,target,a,b):
    g=prepared.g; r=g.r; L=r.bit_length()+1
    if not g.member(target) or target is None: raise ValueError('invalid nonzero target')
    if not(1<=a<r and 1<=b<r): raise ValueError('nonzero multipliers required')
    R=g.mul(b,target); current=R; trace=[]; bits=[]; reasons=[]; V=0
    for i in range(L):
        ans=prepared.evaluate(current); trace.append(dict(index=i,target=None if current is None else list(current),answer=ans))
        bit=ans['bit'] if ans['status']=='BIT' else None; bits.append(bit); V=2*V+(bit or 0)
        if bit is None: reasons.append(ans['reason'])
        if i+1<L: current=g.add(current,current)
    defined=not reasons; k,legal=interval(r,L,V); k=k if defined else None; legal=defined and legal
    inv=pow(b,-1,r); x=(a*inv%r)*k%r if legal else None; tc=oc=None
    if legal: tc=g.mul(k,prepared.base)==R; oc=g.mul(x,base)==target
    recovered=bool(legal and tc and oc)
    status='RECOVERED' if recovered else 'UNDEFINED' if not defined else 'EMPTY_INTERVAL' if not legal else 'REJECTED_FINAL_VERIFICATION'
    return dict(status=status,reason=None if recovered else ','.join(sorted(set(reasons))) if not defined else 'EMPTY_BINARY_INTERVAL' if not legal else 'FINAL_VERIFICATION_FAILED',L=L,candidate_scalar_prime=k,candidate_scalar=x,scalar_prime=k if recovered else None,scalar=x if recovered else None,target_multiplier_inverse=inv,interval=dict(value=V if defined else None,denominator=1<<L,lower_numerator=r*V if defined else None,upper_numerator=r*(V+1) if defined else None,nonempty=bool(legal)),predicate_evaluations=L,retained_bit_reads=0,predicate_trace=trace,public_checks=dict(transformed=tc,original=oc))
