"""Local adversarial checks; no producer-module imports and no producer writes."""
import argparse, gzip, hashlib, itertools, json, math, platform, resource, sys, time, zipfile
from pathlib import Path
from flint import fmpz_mod_poly_ctx
BASE=Path(__file__).resolve().parents[2]
REPO=BASE.parents[1]
OUT=Path(__file__).resolve().parent
P=2**256-2**224+2**192+2**96-1
B=int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
R=int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
TARGET=(0,P-3,B); AUX=(0,1,0)
CTX=fmpz_mod_poly_ctx(P)
count=0

def need(ok,what):
    global count
    count+=1
    if not ok: raise AssertionError(what)
def read(path):
    raw=gzip.decompress(path.read_bytes()) if str(path).endswith('.gz') else path.read_bytes()
    return json.loads(raw)
def rhs(x,C):
    a,b,c=C
    return (x**3+a*x*x+b*x+c)%P

def on(Q,C):return Q is None or (Q[1]**2-rhs(Q[0],C))%P==0

def add(Q,S,C):
    if Q is None:return S
    if S is None:return Q
    x,y=Q;v,w=S;a,b,c=C
    if x==v and (y+w)%P==0:return None
    m=((3*x*x+2*a*x+b)*pow(2*y,-1,P) if x==v else (w-y)*pow(v-x,-1,P))%P
    z=(m*m-a-x-v)%P
    return z,(m*(x-z)-y)%P

def mul(n,Q,C):
    acc=None
    while n:
        if n&1:acc=add(acc,Q,C)
        Q=add(Q,Q,C);n//=2
    return acc

def jdouble(Q,a):
    x,y,z=Q
    if z==0 or y==0:return (0,1,0)
    s=4*x*y*y%P;m=(3*x*x+a*z**4)%P
    xx=(m*m-2*s)%P
    return xx,(m*(s-xx)-8*pow(y,4,P))%P,2*y*z%P

def jplus(Q,S):
    x,y,z=Q;v,w=S
    if not z:return v,w,1
    u=v*z*z%P;t=w*z*z*z%P
    h=(u-x)%P;d=(t-y)%P
    if not h:raise ValueError('equal x in mixed addition')
    xx=(d*d-h*h*h-2*x*h*h)%P
    return xx,(d*(x*h*h-xx)-y*h*h*h)%P,z*h%P

def shortmul(n,Q,a):
    ans=(0,1,0)
    for bit in bin(n)[2:]:
        ans=jdouble(ans,a)
        if bit=='1':
            x,y,z=ans
            if z and (Q[0]*z*z-x)%P==0:
                ans=jdouble(ans,a) if (Q[1]*z*z*z-y)%P==0 else (0,1,0)
            else:ans=jplus(ans,Q)
    return ans

def root(v):
    w=pow(v%P,(P+1)//4,P)
    return min(w,P-w) if w*w%P==v%P else None

def dickson(k,c=0):
    t=CTX([0,1])
    for _ in range(k):t=t*t-2
    return t-c

def product(vals):
    fs=[CTX([-v,1]) for v in vals]
    while len(fs)>1:fs=[fs[j]*fs[j+1] if j+1<len(fs) else fs[j] for j in range(0,len(fs),2)]
    return fs[0] if fs else CTX([1])

def elementary(xs):
    a,b,c=xs
    return ((a+b+c)%P,(a*b+a*c+b*c)%P,a*b*c%P)

def det3(m):
    return sum((1 if perm in [(0,1,2),(1,2,0),(2,0,1)] else -1)*math.prod(m[j][perm[j]] for j in range(3)) for perm in itertools.permutations(range(3)))%P

def resultant4(x,y,z,q):
    # f3(x,y,T): A*T^2+B*T+C. Sylvester determinant of the two quadratics.
    def coeff(x,y):return ((x-y)**2%P,-2*((x+y)*(x*y-3)+2*B)%P,((x*y+3)**2-4*B*(x+y))%P)
    a,b,c=coeff(x,y);d,e,f=coeff(z,q)
    return ((a*f-c*d)**2-(a*e-b*d)*(b*f-c*e))%P

def signed_base(xs):
    pts=[]
    for x in sorted(xs):
        y=root(rhs(x,TARGET))
        if y is not None:
            need(y!=0,'unexpected target 2-torsion')
            pts.extend([(x,y),(x,P-y)])
    return pts

def signed_solutions(pts,Q):
    pairs={(i,j):add(pts[i],pts[j],TARGET) for i in range(len(pts)) for j in range(i,len(pts))}
    return [list((i,j,k)) for i,j,k in itertools.combinations_with_replacement(range(len(pts)),3) if add(pairs[i,j],pts[k],TARGET)==Q]

def custody():
    exc=read(BASE/'reviews/local-custody-exception.json')
    zpath=Path(exc['custody']['local_delta_zip'])
    need(hashlib.sha256(zpath.read_bytes()).hexdigest()==exc['custody']['zip_sha256'],'ZIP digest')
    audit=read(BASE/'archive/payload-audit.json');total=0;relevant=0
    for rec in audit['manifest_sha256']:
        f=REPO/rec['path'];need(hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256'],'manifest binding')
        for row in read(f):
            if '/tracks/f1/' in row['path'] or '/tracks/f2/' in row['path'] or '/baseline/' in row['path']:
                data=(REPO/row['path']).read_bytes()
                need(hashlib.sha256(data).hexdigest()==row['sha256'],'sealed input '+row['path'])
                need(len(data)==row['bytes'],'input length');relevant+=1
            total+=1
    return dict(zip_sha256=exc['custody']['zip_sha256'],manifest_entries=total,relevant_files_bound=relevant,
                canonical_pushed_precondition_met=False,publication_authorized=False)

def f1():
    ans=[]
    for path in sorted((BASE/'tracks/f1/checks-02').glob('*.json')):
        data=read(path)
        if 'domain' not in data:continue
        k=data['k'];c=data['terminal_c'];xs=data['domain'];a=data['alpha'];b=data['beta']
        # Fixture domain is in its original membership parameter; curve coordinates are affine images.
        raw=xs
        F=dickson(k,c)
        if c!=2:
            need(F==product(raw),'complete generic factorization '+path.name)
        else:
            need(F.gcd(F.derivative())!=1,'ramification present')
            factors=product(raw);need((F%factors).is_zero(),'radical divides ramified F')
            need(factors.degree()==2**(k-1)+1,'ramified root count')
            need((F//F.gcd(F.derivative()))==factors,'complete ramified radical')
        curve_x=sorted((a*t+b)%P for t in raw)
        pts=signed_base(curve_x)
        need(pts==[tuple(q) for q in data['signed_base']],'complete signed lift '+path.name)
        for q in data['queries']:
            Q=tuple(q['target']);need(on(Q,TARGET),'target curve')
            sols=signed_solutions(pts,Q)
            need(sols==q['complete_signed_decompositions'],'all signed decompositions '+path.name)
            zero_count=sum(resultant4(*tri,Q[0])==0 for tri in itertools.combinations_with_replacement(curve_x,3))
            need(zero_count==q['s4_zero_symmetric_states'],'independent resultant zero count '+path.name)
        ans.append(dict(case=path.name,N=len(raw),M=len(pts)//2,query_counts=[q['complete_count'] for q in data['queries']]))
    return dict(complete_cases=ans,query_sets=sum(3 for a in ans),independent_resultant=True)

class Dual:
    def __init__(self,v,g=(0,0,0)):self.v=v%P;self.g=tuple(x%P for x in g)
    def __add__(self,b):
        b=b if isinstance(b,Dual) else Dual(b)
        return Dual(self.v+b.v,tuple(x+y for x,y in zip(self.g,b.g)))
    __radd__=__add__
    def __neg__(self):return Dual(-self.v,tuple(-x for x in self.g))
    def __sub__(self,b):return self+-b if isinstance(b,Dual) else self+(-b)
    def __mul__(self,b):
        b=b if isinstance(b,Dual) else Dual(b)
        return Dual(self.v*b.v,tuple(x*b.v+y*self.v for x,y in zip(self.g,b.g)))
    __rmul__=__mul__

def divide_dual(F,s):
    # Differentiate generic polynomial long division, not the producer recurrence.
    u,v,w=[Dual(s[j],tuple(int(i==j) for i in range(3))) for j in range(3)]
    h=[-w,v,-u,Dual(1)];a=[Dual(int(v)) for v in F.coeffs()]
    for d in range(len(a)-1,2,-1):
        lead=a[d]
        for j in range(4):a[d-3+j]=a[d-3+j]-lead*h[j]
    return a[:3]

def cubic():
    derived=[];joint=[]
    for k in [2,3,4]:
        path=BASE/f'tracks/f1/checks-02/generic-k{k if k>2 else 3}.json';data=read(path)
        c=data['terminal_c']
        if k==2:
            # The published k2 fixture is a specified subfibre, whose c is serialized in its attempt.
            c=read(BASE/'tracks/f1/cubic-divisor/attempts-01/distinct-k2-positive.json')['c']
        F=dickson(k,c);xs=sorted(int(v) for v,m in F.roots());need(F==product(xs),'cubic complete root list')
        divs=0
        for tri in itertools.combinations(xs,3):
            s=elementary(tri);h=CTX([-s[2],s[1],-s[0],1]);q,r=divmod(F,h)
            need(r.is_zero(),'divisor membership')
            rem=divide_dual(F,s);need(all(e.v==0 for e in rem),'independent long division')
            det=det3([list(e.g) for e in rem]);res=math.prod(int(q(v)) for v in tri)%P
            need(det==res and det!=0,'Jacobian sign and nonsingularity')
            divs+=1
        need(divs==math.comb(2**k,3),'divisor geometric count')
        repeated=sum(1 for x in xs for y in xs if x!=y)
        need(divs+repeated+len(xs)==math.comb(len(xs)+2,3),'strata complete')
        derived.append(dict(k=k,distinct=divs,twoequal=repeated,allequal=len(xs),nonzero_jacobians=divs))
    F=dickson(3,2);h=CTX([0,-4,0,1]);need((F%h).is_zero(),'nonseparable control divides')
    rem=divide_dual(F,(0,P-4,0));need(det3([list(e.g) for e in rem])==0,'nonseparable control singular')
    for path in sorted((BASE/'tracks/f1/cubic-divisor/checks-01').glob('query-*.json')):
        d=read(path);xs=d['domain'];Q=tuple(d['Q']);pts=signed_base(xs)
        need([list(q) for q in pts]==d['signed_base'],'cubic exact signed base')
        sols=signed_solutions(pts,Q);need(sols==d['full_signed_oracle'],'cubic complete point sums')
        strata={'distinct':0,'twoequal':0,'allequal':0}
        for tri in itertools.combinations_with_replacement(xs,3):
            if resultant4(*tri,Q[0])==0:strata[{3:'distinct',2:'twoequal',1:'allequal'}[len(set(tri))]]+=1
        for key,row in d['strata'].items():
            if row['status']=='PASS':need(row['point_count']==strata[key],'cubic stratum root count')
        joint.append(dict(case=path.name,independent_coordinate_states=strata,signed_solutions=len(sols),
                          algebraic_complete_claim=d['complete_algebraic_combination']))
    return dict(divisors=derived,query_sets=joint,nonseparable_control_rejected=True)

# Sparse multivariate basis checker: full certificates, independent division engine.
def key(m):return (sum(m),tuple(-x for x in reversed(m)))
def sparse(rows):return {tuple(m):c%P for m,c in rows if c%P}
def ev(f,pt):return sum(c*math.prod(pow(x,e,P) for x,e in zip(pt,m)) for m,c in f.items())%P

def subtract_multiple(f,g,m,c):
    for n,b in g.items():
        j=tuple(x+y for x,y in zip(n,m));f[j]=(f.get(j,0)-b*c)%P
        if f[j]==0:del f[j]

def reducepoly(f,bs):
    f=f.copy();r={}
    while f:
        m=max(f,key=key);c=f[m]
        for g in bs:
            lead=max(g,key=key)
            if all(x>=y for x,y in zip(m,lead)):
                shift=tuple(x-y for x,y in zip(m,lead));subtract_multiple(f,g,shift,c*pow(g[lead],-1,P)%P);break
        else:r[m]=f.pop(m)
    return r

def basis():
    checks=[]
    folder=BASE/'tracks/f1/cubic-divisor/attempts-01'
    for path in sorted(folder.glob('*.json*')):
        if path.name=='receipt.json':continue
        d=read(path)
        if d.get('status')!='PASS':continue
        gs=list(map(sparse,d['groebner_basis']));eq=list(map(sparse,d['equations']));n=len(next(iter(gs[0])))
        need(all(not reducepoly(f,gs) for f in eq),'all original generators in basis ideal')
        pairs=0
        for f,g in itertools.combinations(gs,2):
            m=max(f,key=key);z=max(g,key=key);l=tuple(max(x,y) for x,y in zip(m,z));s={}
            subtract_multiple(s,f,tuple(x-y for x,y in zip(l,m)),pow(f[m],-1,P))
            subtract_multiple(s,g,tuple(x-y for x,y in zip(l,z)),-pow(g[z],-1,P)%P)
            need(not reducepoly(s,gs),'critical pair');pairs+=1
        # Independently enumerate complete coordinate roots from fixture domain and resultant.
        xs=d['fixture']['domain'];Q=d['target'];stratum=d['stratum'];pts=[]
        if stratum=='distinct':objects=itertools.combinations(xs,3)
        elif stratum=='twoequal':objects=((x,x,y) for x in xs for y in xs if x!=y)
        else:objects=((x,x,x) for x in xs)
        for tri in objects:
            if d['mode']=='membership' or resultant4(*tri,Q[0])==0:
                pts.append(elementary(tri) if stratum=='distinct' else ((tri[0],tri[2]) if stratum=='twoequal' else (tri[0],)))
        need(sorted(set(pts))==sorted(map(tuple,d['complete_stratum_points'])),'independent complete coordinate roots')
        need(all(ev(g,pt)==0 for g in gs for pt in pts),'basis vanishes on complete points')
        leads=[max(g,key=key) for g in gs]
        if (0,)*n in leads:dim=0
        else:
            bounds=[min(m[j] for m in leads if m[j] and all(not m[i] for i in range(n) if i!=j)) for j in range(n)]
            dim=sum(not any(all(x>=y for x,y in zip(m,l)) for l in leads) for m in itertools.product(*(range(b) for b in bounds)))
        need(dim==len(pts)==d['certificate']['standard_monomial_count'],'finite quotient equality')
        checks.append(dict(case=path.name,dimension=dim,critical_pairs=pairs))
    return dict(certificates=checks,critical_pairs=sum(x['critical_pairs'] for x in checks))

def map_edge(Q,e):
    if Q is None:return None
    x,y=Q;u=(x-e['r'])%P
    if not u:return None
    X=(u*u+e['a']*u+e['b'])*pow(u,-1,P)%P
    Y=y*(u*u-e['b'])*pow(u*u,-1,P)%P
    return X,Y

def chainmap(Q,edges):
    for e in edges:Q=map_edge(Q,e)
    return Q

def dual_edge(Q,e):
    if Q is None or Q[0]==0:return None
    x,y=Q;aa=-2*e['a']%P;bb=(e['a']**2-4*e['b'])%P
    xx=(x*x+aa*x+bb)*pow(4*x,-1,P)%P
    yy=y*(x*x-bb)*pow(8*x*x,-1,P)%P
    return (xx+e['r'])%P,yy

def f2():
    directory=BASE/'tracks/f2/receipts/validation-001';d=read(directory/'chain.json');edges=d['edges'];H=tuple(read(directory/'generator.json')['generator'])
    need(P%4==3 and (P+1)&-(P+1)==2**96,'field 2-adic valuation')
    need(on(H,AUX),'aux order witness on curve')
    need(mul(2**96,H,AUX) is None and mul(2**95,H,AUX) is not None,'exact aux generator order')
    need(math.gcd(P+1,R)==1 and P+1!=R,'target/aux separation')
    dualchecks=0
    for i,e in enumerate(edges):
        C=tuple(e['source']);D=tuple(e['destination']);r=e['r'];a=e['a'];b=e['b'];K=tuple(e['kernel_point']);G=tuple(e['source_generator']);im=tuple(e['image_generator'])
        need(K==(r,0) and on(K,C),'kernel genuine 2 torsion')
        need(a==(3*r+C[0])%P and b==(3*r*r+2*C[0]*r+C[1])%P,'translate kernel')
        need(D==(-2*a%P,(a*a-4*b)%P,0) and b!=0 and (a*a-4*b)%P!=0,'quotient identity coefficients')
        need(map_edge(K,e) is None and map_edge(None,e) is None,'projective pole images')
        need(on(G,C) and map_edge(G,e)==im and on(im,D),'chain generator image')
        need(mul(2**(95-i),im,D) is None and mul(2**(94-i),im,D) is not None,'image exact order')
        if i+1<len(edges):need(list(D)==edges[i+1]['source'] and list(im)==edges[i+1]['source_generator'],'chain linkage')
        controls=read(directory/'edges'/f'edge-{i:02}.json')
        for ex in controls['examples']:
            U=tuple(ex['source']);W=tuple(ex['destination_point'])
            need(dual_edge(map_edge(U,e),e)==mul(2,U,C),'dual phi identity sample')
            need(map_edge(dual_edge(W,e),e)==mul(2,W,D),'phi dual identity sample');dualchecks+=2
    allrows=0;accepted=0;summaries=[];negative={}
    for path in sorted((directory/'cases').glob('*/summary.json')):
        s=read(path);rows=[r for chunk in s['certificate_chunks'] for r in read(directory/chunk)]
        family=s['family'];meta=s['metadata'];xs=set();acc=0
        for row in rows:
            x=row['x'];need(0<=x<P and x not in xs,'canonical distinct fibre coordinate');xs.add(x)
            if family.startswith('elliptic'):
                point=tuple(row['auxiliary_point']);need(point[0]==x and on(point,AUX),'auxiliary row equation')
                image=chainmap(point,edges[:meta['chain_length']])
                need(image==(tuple(meta['endpoint']) if family=='elliptic_generic' else None),'exact rational fibre row')
            else:
                value=x
                for _ in range(meta['composition_depth']):value=(value*value-2)%P
                need(value==meta['terminal'],'Dickson row membership')
                a,b=row['torus_point'];need((a*a+b*b)%P==1 and 2*a%P==x,'torus row')
            y=root(rhs(x,TARGET));T=row['target_point']
            if T is None:need(y is None,'all rejected lifts nonsquare')
            else:
                need(y is not None and T==[x,y] and y>0,'all target lift coordinates')
                need(shortmul(R,tuple(T),-3)[2]==0,'independent subgroup arithmetic')
                acc+=1
        need(len(rows)==len(xs)==s['raw_x_size'],'complete raw domain cardinality')
        need(acc==s['accepted_x_size'],'complete accepted target incidence')
        if family=='elliptic_kernel':need(len(xs)==meta['kernel_order']//2,'kernel complete by cyclic order')
        if family=='elliptic_generic':need(len(xs)==2**meta['chain_length'] and meta['endpoint'][1]!=0,'generic complete by map degree')
        summaries.append(dict(case=s['case'],rows=len(xs),accepted=acc));allrows+=len(xs);accepted+=acc
    compact=read(directory/'compact-full-chain.json');K=tuple(compact['kernel_generator']);O=tuple(compact['generic_offset']);Q=tuple(compact['generic_endpoint'])
    need(on(K,AUX) and on(O,AUX),'compact valid source points')
    need(mul(2**16,K,AUX) is None and mul(2**15,K,AUX) is not None,'compact kernel exact order')
    need(chainmap(K,edges) is None and chainmap(O,edges)==Q and Q[1]!=0,'compact complete fibre theorem hypotheses')
    # Negative controls are checked by an independent validator, never by trusting scalar x alone.
    need(map_edge((edges[0]['r'],0),edges[0]) is None,'pole excluded from affine value');negative['pole']='rejected as finite fibre root'
    fake=next((x,1) for x in range(20) if not on((x,1),AUX));need(not on(fake,AUX),'nonrational source control');negative['off_curve_source']='rejected'
    bad=(Q[0],(Q[1]+1)%P);need(not on(bad,tuple(edges[-1]['destination'])) and chainmap(O,edges)!=bad,'corrupt endpoint control');negative['corrupt_endpoint']='rejected'
    return dict(edges_checked=len(edges),dual_composition_samples=dualchecks,rows=allrows,accepted=accepted,cases=summaries,
        compact_degree=65536,compact_full_target_lifts_enumerated=False,controls=negative)

def algebra():
    directory=BASE/'tracks/f2/receipts/validation-001';edges=read(directory/'chain.json')['edges'];N=CTX([0,1]);D=CTX([1]);ans=[]
    H=tuple(read(directory/'generator.json')['generator'])
    for lev,e in enumerate(edges[:12],1):
        U=N-e['r']*D
        N,D=U*U+e['a']*U*D+e['b']*D*D,U*D
        need(N.gcd(D).degree()==0,'no hidden rational-map cancellation')
        if lev not in [6,8,10,12]:continue
        n=2**lev;need(N.degree()==n and D.degree()==n-1,'expanded map degrees')
        K=mul(2**(96-lev),H,AUX);point=K;poles=[]
        for j in range(n//2):poles.append(point[0]);point=add(point,K,AUX)
        need(len(set(poles))==n//2 and 0 in poles,'complete pole list')
        expected=CTX([0,1])*product([v for v in poles if v!=0])**2
        need(D==expected,'complete finite poles and multiplicities')
        W=N.derivative()*D-N*D.derivative();need(W.degree()==2*n-2 and W.gcd(W.derivative()).degree()==0,'ramification degree/simplicity')
        need(W.gcd(CTX([0,1,0,1])).degree()==0,'source 2 torsion unramified x')
        Wfinite=W//W.gcd(D);a,b,c=e['destination'];branch=N**3+a*N*N*D+b*N*D*D+c*D**3
        need((branch%Wfinite).is_zero(),'all finite branch images in destination 2 torsion')
        record=read(directory/'algebra'/f'level-{lev:02}.json')
        need(record['critical_polynomial_degree']==W.degree() and record['finite_branch_critical_degree']==Wfinite.degree(),'branch receipt counts')
        ans.append(dict(level=lev,degree=n,simple_poles=1,double_poles=n//2-1,critical_degree=W.degree(),finite_branch_degree=Wfinite.degree()))
    return dict(levels=ans)

PARTS=dict(custody=custody,f1=f1,cubic=cubic,basis=basis,f2=f2,algebra=algebra)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('part',choices=PARTS);args=parser.parse_args()
    start=time.monotonic();dest=OUT/(args.part+'-independent.json')
    if dest.exists():raise SystemExit('refuse overwrite')
    try:
        result=PARTS[args.part]();status='PASS'
    except BaseException as ex:
        import traceback
        result={'error':type(ex).__name__+': '+str(ex),'traceback':traceback.format_exc()};status='FAIL'
    record=dict(status=status,part=args.part,assertions=count,observations=result,command=[sys.executable,*sys.argv],
      python=sys.version,platform=platform.platform(),wall_seconds=time.monotonic()-start,
      maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      producer_imports=False,official_research_gate=False)
    dest.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));sys.exit(0 if status=='PASS' else 1)
