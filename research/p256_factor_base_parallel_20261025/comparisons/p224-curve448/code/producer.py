"""Self-contained finite-domain comparison. Run with python-flint 0.8.

Parameters and symmetric S4 are copied from the declared local inputs;
the Dickson trace construction is reimplemented here. No producer arithmetic
is shared with independent.py. All targets and points are public synthetic data.
"""
import hashlib, itertools, json, platform, subprocess, sys, time
from pathlib import Path
from flint import fmpz, fmpz_mod_poly_ctx

HERE=Path(__file__).resolve().parent.parent
STUDY=HERE.parents[1]
def dump(path,v):
    path.write_text(json.dumps(v,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def hx(s):return int(s,16)
P224=dict(name='P-224',p=2**224-2**96+1,a=-3,
 b=hx('b4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4'),
 r=hx('ffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d'),h=1,mode='split',
 generator_x=hx('b70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21'))
p448=2**448-2**224-1; A448=156326
C448=dict(name='Curve448',p=p448,a=(1-A448*A448*pow(3,-1,p448))%p448,
 b=(2*A448**3*pow(27,-1,p448)-A448*pow(3,-1,p448))%p448,
 r=2**446-hx('8335dc163bb124b65129c96fde933d8d723a70aadc873d6d54a7bb0d'),h=4,
 mode='norm-one',montgomery_A=A448,generator_x=(5+A448*pow(3,-1,p448))%p448)

def sqrt(n,p):
    n%=p
    if not n:return 0
    if pow(n,(p-1)//2,p)!=1:return None
    q,s=p-1,0
    while q%2==0:q//=2;s+=1
    z=2
    while pow(z,(p-1)//2,p)!=p-1:z+=1
    c,x,t,m=pow(z,q,p),pow(n,(q+1)//2,p),pow(n,q,p),s
    while t!=1:
        i,v=0,t
        while v!=1:v=v*v%p;i+=1
        b=pow(c,2**(m-i-1),p);x=x*b%p;t=t*b*b%p;c=b*b%p;m=i
    return min(x,p-x)

class Jacobian:
    def __init__(self,c):self.p,self.a=c['p'],c['a']
    def of(self,P):return (0,1,0) if P is None else (*P,1)
    def affine(self,P):
        x,y,z=P
        if not z:return None
        v=pow(z,-1,self.p);return x*v*v%self.p,y*v*v*v%self.p
    def add(self,P,Q):
        p=self.p;X,Y,Z=P;U,V,W=Q
        if not Z:return Q
        if not W:return P
        z2=Z*Z%p;w2=W*W%p;u1=X*w2%p;u2=U*z2%p;s1=Y*W*w2%p;s2=V*Z*z2%p
        h=(u2-u1)%p;r=(s2-s1)%p
        if not h:
            if r or not Y:return (0,1,0)
            yy=Y*Y%p;d=4*X*yy%p;e=(3*X*X+self.a*z2*z2)%p
            xx=(e*e-2*d)%p
            return xx,(e*(d-xx)-8*yy*yy)%p,2*Y*Z%p
        hh=h*h%p;hhh=h*hh%p;v=u1*hh%p;xx=(r*r-hhh-2*v)%p
        return xx,(r*(v-xx)-s1*hhh)%p,h*Z*W%p
    def mul(self,k,P):
        out=(0,1,0);base=self.of(P)
        while k:
            if k&1:out=self.add(out,base)
            base=self.add(base,base);k//=2
        return self.affine(out)
    def sum(self,points):
        out=(0,1,0)
        for P in points:out=self.add(out,self.of(P))
        return self.affine(out)

def coset(p,S,mode):
    if mode=='split':
        mul=lambda a,b:a*b%p
        power=lambda a,k:pow(a,k,p)
        inv=lambda a:pow(a,-1,p)
        trace=lambda a:(a+inv(a))%p
        one=1;ambient=p-1
        candidates=iter(range(2,1000))
    else:
        # F_(p^2)=F_p[i], i^2=-1, valid because p=3 mod4.
        assert p%4==3
        mul=lambda a,b:((a[0]*b[0]-a[1]*b[1])%p,(a[0]*b[1]+a[1]*b[0])%p)
        def power(a,k):
            out=(1,0)
            while k:
                if k&1:out=mul(out,a)
                a=mul(a,a);k//=2
            return out
        inv=lambda a:(a[0],-a[1]%p)
        trace=lambda a:2*a[0]%p
        def beta(k):
            v=pow(k*k+1,-1,p)
            return (k*k-1)*v%p,2*k*v%p
        one=(1,0);ambient=p+1;candidates=(beta(k) for k in range(1,1000))
    assert ambient%S==0
    for z in candidates:
        g=power(z,ambient//S)
        if power(g,S)==one and power(g,S//2)!=one:break
    else:raise RuntimeError('no exact order root')
    candidates=range(2,1000) if mode=='split' else (beta(k) for k in range(1,1000))
    for alpha in candidates:
        c=trace(power(alpha,S))
        if c not in (2,p-2):break
    roots=[];v=alpha
    for _ in range(S):roots.append(trace(v));v=mul(v,g)
    assert len(set(roots))==S and v==alpha
    C=fmpz_mod_poly_ctx(p);X=C([0,1]);D=X
    for _ in range(S.bit_length()-1):D=D*D-2
    H=D-c;factor=C([1])
    for x in roots:factor*=X-x
    assert H==factor and H.gcd(H.derivative()).degree()==0
    flint_roots=sorted(int(x) for x,m in H.roots() if m==1)
    assert flint_roots==sorted(roots)
    return dict(S=S,c=c,alpha=alpha,zeta=g,ambient_order=ambient,
                two_adicity=(ambient&-ambient).bit_length()-1,
                polynomial_coefficients=[int(v) for v in H],roots=sorted(roots),
                full_factorization=[dict(root=x,multiplicity=1) for x in sorted(roots)])

def identity(c,G):
    # Same canonical metadata-hash algorithm as tools/curve_identity.py.
    field=dict(characteristic=c['p'],degree=1,representation='prime-residue',element_encoding='integer 0<=x<p')
    curve=dict(model='short-weierstrass',a=c['a']%c['p'],b=c['b']%c['p'],subgroup_order=c['r'],
               cofactor=c['h'],generator=list(G),target_group='prime-order r subgroup')
    raw=json.dumps(dict(field=field,curve=curve),sort_keys=True,separators=(',',':')).encode()
    h=hashlib.sha256(raw).hexdigest();tag='p224' if c['name']=='P-224' else 'curve448short'
    return dict(field=field,curve=curve,curve_uid='urn:ec-record:1:sha256:'+h,
                curve_id=f"EC1P{c['p'].bit_length()}C{tag}h{h[:12]}")

def run_case(c,S,s4):
    started=time.time();p=c['p'];E=Jacobian(c);dom=coset(p,S,c['mode'])
    assert bool(fmpz(p).is_prime()) and bool(fmpz(c['r']).is_prime())
    assert (4*c['a']**3+27*c['b']**2)%p
    records=[];M=[]
    for x in dom['roots']:
        y=sqrt(x**3+c['a']*x+c['b'],p)
        row=dict(x=x,y=y)
        if y is None:row['status']='non-lift'
        elif y==0:row['status']='zero-y exclusion'
        else:
            residual=E.mul(c['r'],(x,y));row['r_multiple']=residual
            row['status']='accepted' if residual is None else 'cofactor rejection'
            if residual is None:M.append((x,y))
        records.append(row)
    G=(c['generator_x'],sqrt(c['generator_x']**3+c['a']*c['generator_x']+c['b'],p))
    assert G[1] is not None and E.mul(c['r'],G) is None
    F=[P for x,y in M for P in [(x,y),(x,-y%p)]]
    record=dict(parameters=c,identity=identity(c,G),domain=dom,lifts=records,canonical_M=M,
                signed_base=F,public_generator=G,field_prime=True,subgroup_order_prime=True,
                nonsingular=True,generator_r_multiple=None,cases=[])
    label=c['name'].lower().replace('-','')+f'-s{S}'
    if not M:
        dump(HERE/'certificates'/f'{label}-domain.json',record);return dict(name=c['name'],S=S,M=0)
    targets=[('constructed-positive-repeated',E.sum([M[0],M[0],M[min(1,len(M)-1)]])),
             ('base-cancellation',M[-1]),('unrelated-public-generator',G)]
    assert all(Q is not None for _,Q in targets)
    # Complete signed triples, using Jacobian arithmetic only.
    direct={Q:[] for _,Q in targets}
    for ijk in itertools.combinations_with_replacement(range(len(F)),3):
        R=E.sum([F[i] for i in ijk])
        if R in direct:direct[R].append(ijk)
    byx={P[0]:i for i,P in enumerate(M)}
    lift_byx={r['x']:r for r in records}
    for name,Q in targets:
        coeffs=[(powers,eval(expr,{'__builtins__':{}},dict(a=c['a'],b=c['b'],t=Q[0]))%p)
                for powers,expr in s4['terms']]
        algebraic=[];found=set();excluded={'non-lift':0,'cofactor rejection':0,'zero-y exclusion':0}
        for xx in itertools.combinations_with_replacement(dom['roots'],3):
            x,y,z=xx;s1=(x+y+z)%p;s2=(x*y+y*z+z*x)%p;s3=x*y*z%p
            v=[[(pow(s,k,p)) for k in range(5)] for s in (s1,s2,s3)]
            if sum(co*v[0][a]*v[1][b]*v[2][d] for (a,b,d),co in coeffs)%p:continue
            statuses=[lift_byx[x]['status'] for x in xx]
            row=dict(x=xx,status='accepted-lifts' if all(s=='accepted' for s in statuses) else 'excluded')
            if row['status']=='excluded':
                row['reasons']=sorted(set(s for s in statuses if s!='accepted'))
                for reason in row['reasons']:excluded[reason]+=1
            else:
                local=set()
                for signs in itertools.product(range(2),repeat=3):
                    ids=tuple(sorted(2*byx[x]+s for x,s in zip(xx,signs)))
                    if E.sum([F[i] for i in ids])==Q:local.add(ids);found.add(ids)
                row['signed_solutions']=sorted(local)
            algebraic.append(row)
        assert sorted(found)==direct[Q],(label,name)
        cert=dict(curve=c['name'],S=S,control=name,target=Q,
                  full_x_multisets_checked=S*(S+1)*(S+2)//6,
                  signed_multisets_checked=len(F)*(len(F)+1)*(len(F)+2)//6,
                  S4_zero_candidates=algebraic,excluded_candidates=excluded,
                  complete_signed_solutions=sorted(found),independent_check_pending=True)
        path=HERE/'certificates'/f'{label}-{name}.json';dump(path,cert)
        record['cases'].append(dict(control=name,certificate=str(path.relative_to(HERE)),
                                   algebraic_candidates=len(algebraic),solutions=len(found),
                                   repeated_coordinate_solutions=sum(len({F[i][0] for i in ijk})<3 for ijk in found)))
    dump(HERE/'certificates'/f'{label}-domain.json',record)
    counts={s:sum(r['status']==s for r in records) for s in ('accepted','non-lift','cofactor rejection','zero-y exclusion')}
    out=dict(name=c['name'],S=S,M=len(M),signed_base=len(F),lift_counts=counts,c=dom['c'],
             domain_certificate=f'certificates/{label}-domain.json',cases=record['cases'],wall_seconds=time.time()-started)
    print(json.dumps(out),flush=True);return out

if __name__=='__main__':
    t=time.time();s4path=STUDY/'baseline'/'s4-symmetric.json';s4=json.loads(s4path.read_text())
    results=[run_case(c,S,s4) for c in (P224,C448) for S in (16,32)]
    for c in (P224,C448):
        if not any(r['M'] for r in results if r['name']==c['name']):results.append(run_case(c,64,s4))
    dump(HERE/'producer-result.json',dict(schema='published-curves-finite-comparison/v1',task='TASK-20261025-8c305c',
      status='producer exact checks passed; independent replay pending',results=results,wall_seconds=time.time()-t,
      provenance=dict(python=sys.version,platform=platform.platform(),source_sha256=sha(Path(__file__)),
       s4_input_sha256=sha(s4path),parameters_input_sha256=sha(STUDY/'baseline'/'parameters.py'),
       base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
       git_status=subprocess.check_output(['git','status','--short'],cwd=HERE,text=True).splitlines()),
      custody=dict(pushed_handoff_condition_met=False,local_only=True,publication_approval_pending=True,
       exception='../../reviews/local-custody-exception.json',normal_dispatch_compliance=False),
      scope='Exact finite domains on published fields; no asymptotic, yield, timing advantage, or attack-cost claim.'))
