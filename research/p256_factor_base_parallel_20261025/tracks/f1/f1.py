"""Exact F1 implementation checks on P-256. No benchmark or experiment trial.

Run using /workspace/dickson-solver/.venv/bin/python f1.py --out DIR
The solver receives public curve points, never generation scalars.
"""
import argparse, hashlib, importlib.util, itertools, json, math, os, platform, sys
from pathlib import Path
from collections import Counter

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent.parent
spec=importlib.util.spec_from_file_location('published_parameters',STUDY/'baseline/parameters.py')
parameters=importlib.util.module_from_spec(spec);spec.loader.exec_module(parameters)
PARAM=next(c for c in parameters.CURVES if c['name']=='P-256')
p,a,b,r=PARAM['p'],PARAM['a'],PARAM['b'],PARAM['r']
S4_DATA=json.loads((STUDY/'baseline/s4-symmetric.json').read_text())
G=(int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16),
   int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16))

def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def sqr(x):
    x%=p
    if not x:return 0
    y=pow(x,(p+1)//4,p)
    return min(y,p-y) if y*y%p==x else None

def neg(P):return None if P is None else (P[0],-P[1]%p)
def add(P,Q):
    if P is None:return Q
    if Q is None:return P
    x,y=P;u,v=Q
    if x==u:
        if (y+v)%p==0:return None
        m=(3*x*x+a)*pow(2*y,-1,p)%p
    else:m=(v-y)*pow(u-x,-1,p)%p
    w=(m*m-x-u)%p
    return w,(m*(x-w)-y)%p

def mul(n,P):
    R=None
    while n:
        if n&1:R=add(R,P)
        n//=2;P=add(P,P)
    return R

def lift(x):
    y=sqr(x*x*x+a*x+b)
    return None if y is None else (x%p,y)

def elementary(xs):
    x,y,z=xs
    return ((x+y+z)%p,(x*y+x*z+y*z)%p,x*y*z%p)

def phi(s):
    u,v,w=s
    return ((u*u-2*v-6)%p,(v*v-2*u*w-4*u*u+8*v+12)%p,
            (w*w-2*v*v+4*u*w+4*u*u-8*v-8)%p)

def iterate(s,k):
    for _ in range(k):s=phi(s)
    return s

def dickson(x,k):
    for _ in range(k):x=(x*x-2)%p
    return x

def affine(s,alpha=1,beta=0):
    u,v,w=s
    return ((alpha*u+3*beta)%p,(alpha*alpha*v+2*alpha*beta*u+3*beta*beta)%p,
      (alpha**3*w+alpha*alpha*beta*v+alpha*beta*beta*u+beta**3)%p)

def s4_coeffs(t):
    env={'a':a,'b':b,'t':t}
    return [(tuple(m),int(eval(c,{'__builtins__':{}},env))%p) for m,c in S4_DATA['terms']]

def evaluate(terms,s):
    powers=[[pow(v,e,p) for e in range(5)] for v in s]
    return sum(c*powers[0][m[0]]*powers[1][m[1]]*powers[2][m[2]] for m,c in terms)%p

def cmul(z,w):return ((z[0]*w[0]-z[1]*w[1])%p,(z[0]*w[1]+z[1]*w[0])%p)
def cpow(z,n):
    v=(1,0)
    while n:
        if n&1:v=cmul(v,z)
        z=cmul(z,z);n//=2
    return v

def torus(t):
    d=pow(t*t+1,-1,p)
    return ((t*t-1)*d%p,2*t*d%p)

def trace(z):return 2*z[0]%p

def domain(k,c):
    levels=[[c]]
    for _ in range(k):
        roots=set()
        for y in levels[-1]:
            z=sqr(y+2)
            if z is not None:roots.update((z,-z%p))
        levels.append(sorted(roots))
    return levels

def torus_roots(k,t,enumerate_roots=True):
    S=1<<k
    for j in range(1,100):
        w=cpow(torus(j),(p+1)//S)
        if cpow(w,S)==(1,0) and (S==1 or cpow(w,S//2)!=(1,0)):break
    else:raise AssertionError('no bounded exact-order torus element')
    z=torus(t);c=trace(cpow(z,S));out=[];q=z
    if not enumerate_roots:return c,None,j,w
    for _ in range(S):out.append(trace(q));q=cmul(q,w)
    assert q==z
    return c,sorted(set(out)),j,w

def base(xs,alpha=1,beta=0):
    F=[]
    for u in xs:
        P=lift((alpha*u+beta)%p)
        if P is not None:
            F.extend([P,neg(P)] if P[1] else [P])
    return sorted(F)

def inverse_symmetric(k,c):
    """Exact recursion on split cubics, quotienting permutation at each level.

Each state stores its three split roots. Every inverse is obtained from all
square roots of y_i+2; canonical sorting removes only S3 duplicates.
"""
    states={(c,c,c)};growth=[]
    for level in range(k):
        out=set();sqrt_queries=0;raw=0
        for ys in states:
            choices=[]
            for y in ys:
                z=sqr(y+2);sqrt_queries+=1
                choices.append([] if z is None else sorted({z,-z%p}))
            for xs in itertools.product(*choices):
                raw+=1;out.add(tuple(sorted(xs)))
        states=out
        growth.append({'level':level+1,'distinct_split_symmetric_states':len(states),
                       'square_root_requests':sqrt_queries,'raw_branches':raw})
    assert len(states)==math.comb(len(domain(k,c)[-1])+2,3)
    return states,growth

def direct_solutions(F,Q):
    out=[];look={P:i for i,P in enumerate(F)};visits=0
    for i,P in enumerate(F):
        for j in range(i,len(F)):
            visits+=1
            h=look.get(add(Q,neg(add(P,F[j]))))
            if h is not None and h>=j:out.append((i,j,h))
    return sorted(out),visits

def recovered_solutions(F,Q,xtriples):
    byx={}
    for i,P in enumerate(F):byx.setdefault(P[0],[]).append(i)
    out=set();sign_visits=0
    for xs in xtriples:
        for inds in itertools.product(*(byx.get(x,[]) for x in xs)):
            sign_visits+=1
            i,j,h=inds
            if add(add(F[i],F[j]),F[h])==Q:out.add(tuple(sorted(inds)))
    return sorted(out),sign_visits

def select_matched(k):
    S=1<<k;ramroots=domain(k,2)[-1];M=len(base(ramroots))//2
    records=[]
    for t in range(1,257):
        c,xs,j,w=torus_roots(k-1,t)
        if c in (2,p-2):continue
        f=base(xs);records.append({'t':t,'canonical_base_size':len(f)//2})
        if len(f)//2==M:return M,(c,xs,t,j,w),records
    raise AssertionError(('no matched generic coset in declared search',k,M,records))

def case_record(name,k,c,xs,alpha=1,beta=0,torus_certificate=None):
    F=base(xs,alpha,beta)
    assert all(mul(r,P) is None for P in F)
    states,growth=inverse_symmetric(k,c)
    canonical={elementary(x) for x in states}
    assert len(canonical)==len(states)
    assert all(iterate(s,k)==elementary((c,c,c)) for s in canonical)
    assert states==set(itertools.combinations_with_replacement(xs,3))
    seedpoints=[F[0],F[len(F)//2],F[-1]]
    target=add(add(*seedpoints[:2]),seedpoints[2])
    # Three public finite correctness targets, with no generation labels in solvers.
    targets=[('constructed positive',target),('base member incl inverse-pair decompositions',F[0]),
             ('fixed public unrelated point',G)]
    answers=[]
    for label,Q in targets:
        assert Q is not None
        terms=s4_coeffs(Q[0]);hits=[]
        for x in states:
            if evaluate(terms,affine(elementary(x),alpha,beta))==0:
                hits.append(tuple(sorted((alpha*u+beta)%p for u in x)))
        found,signs=recovered_solutions(F,Q,hits)
        reference,visits=direct_solutions(F,Q)
        assert found==reference
        answers.append({'label':label,'target':Q,'s4_zero_symmetric_states':len(hits),
                        'signed_lift_candidates':signs,'s4_evaluations':len(states),
                        'direct_pair_visits':visits,'complete_signed_decompositions':found,
                        'complete_count':len(found),'solution_digest':digest(found)})
    return {'name':name,'parameters':PARAM,'k':k,'S':1<<k,'terminal_c':c,
            'alpha':alpha,'beta':beta,'domain':xs,'domain_size':len(xs),
            'canonical_base_size':len(F)//2,'signed_base':F,'torus_certificate':torus_certificate,
            'inverse_growth':growth,'complete_symmetric_states':len(states),
            'certificate':'inverse recursion == every domain multiset; all S4 hits lifted; exact pair-join equality',
            'queries':answers}

def determinant4(M):
    out=0
    for perm in itertools.permutations(range(4)):
        inv=sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
        v=(-1)**inv
        for i in range(4):v=v*M[i][perm[i]]%p
        out+=v
    return out%p

def s3coeff(x,y):
    return ((x-y)**2%p,(-2*(x*y+a)*(x+y)-4*b)%p,((x*y-a)**2-4*b*(x+y))%p)

def identity_checks():
    import sympy as sp
    x,y,z=sp.symbols('x y z');u,v,w=sp.symbols('u v w')
    symmetric=sp.symmetrize([(x*x-2)+(y*y-2)+(z*z-2),
      (x*x-2)*(y*y-2)+(x*x-2)*(z*z-2)+(y*y-2)*(z*z-2),
      (x*x-2)*(y*y-2)*(z*z-2)],[x,y,z],formal=True)
    expected=[u*u-2*v-6,v*v-2*u*w-4*u*u+8*v+12,
              w*w-2*v*v+4*u*w+4*u*u-8*v-8]
    for (f,rem),e in zip(symmetric[0],expected):
        assert rem==0 and sp.expand(f.subs(dict(zip([s[0] for s in symmetric[1]],[u,v,w])))-e)==0
    for i in range(40):
        vals=tuple(int.from_bytes(hashlib.sha256(f'f1/{i}/{j}'.encode()).digest(),'big')%p for j in range(4))
        x,y,z,t=vals
        assert phi(elementary((x,y,z)))==elementary(tuple((h*h-2)%p for h in (x,y,z)))
        q=s3coeff(x,y);h=s3coeff(z,t)
        M=[[q[0],q[1],q[2],0],[0,q[0],q[1],q[2]],
           [h[0],h[1],h[2],0],[0,h[0],h[1],h[2]]]
        assert determinant4(M)==evaluate(s4_coeffs(t),elementary((x,y,z)))
    return {'status':'PASS','symbolic_symmetric_identities':3,'s4_resultant_identity_cases':40,
            'numeric_phi_cases':40,'published_generator_on_curve':G[1]*G[1]%p==(G[0]**3+a*G[0]+b)%p,
            'published_generator_order_checked':mul(r,G) is None}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    import flint,sympy
    receipt={'scope':'fixed implementation correctness checks; no scientific trial or timing comparison',
      'task':'TASK-20261025-cfb933','input_commit':'2c8c71cfff6f7f63297fbe4de4608cd94d857184',
      'working_tree':'track implementation files added; shared tree owned by root; no git operation performed',
      'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                     'sympy':sympy.__version__,'python_flint':flint.__version__},
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'input_sha256':{str(q.relative_to(STUDY)):hashlib.sha256(q.read_bytes()).hexdigest() for q in
                      [STUDY/'baseline/parameters.py',STUDY/'baseline/s4-symmetric.json']},
      'identity_checks':identity_checks(),'cases':[],'matched_searches':[],'large_domain_checks':[]}
    for k in [3,4,5]:
        M,generic,search=select_matched(k);c,xs,t,j,w=generic
        receipt['matched_searches'].append({'ramified_k':k,'target_M':M,'generic_k':k-1,'attempts':search})
        datasets=[case_record(f'ramified-k{k}',k,2,domain(k,2)[-1]),
                  case_record(f'generic-k{k-1}',k-1,c,xs,torus_certificate={'t':t,'omega_t':j,'omega':w})]
        # Deterministic translated-coordinate control at the same actual M.
        affine_search=[]
        for beta in range(1,257):
            n=len(base(xs,3,beta))//2;affine_search.append({'beta':beta,'M':n})
            if n==M:break
        else:raise AssertionError('matched affine control unavailable')
        receipt['matched_searches'][-1]['affine_attempts']=affine_search
        datasets.append(case_record(f'generic-affine-k{k-1}',k-1,c,xs,3,beta))
        for data in datasets:
            dest=args.out/(data['name']+'.json');write(dest,data)
            receipt['cases'].append({'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
               'M':data['canonical_base_size'],'domain_size':data['domain_size'],
               'symmetric_states':data['complete_symmetric_states'],
               'complete_solution_counts':[q['complete_count'] for q in data['queries']]})
            print(data['name'],'M',data['canonical_base_size'],'states',data['complete_symmetric_states'],
                  'solutions',[q['complete_count'] for q in data['queries']],flush=True)
    for k in [6,7,8,16,32,64,96]:
        c,xs,j,w=torus_roots(k,2,enumerate_roots=k<=8)
        assert c not in (2,p-2)
        # High-depth circuit witness only: no huge domain construction.
        witness=trace(torus(2))
        assert dickson(witness,k)==c and iterate(elementary((witness,)*3),k)==elementary((c,)*3)
        rec={'k':k,'S':1<<k,'c':c,'witness_x':witness,'exact_order_omega':w,
             'high_depth_circuit_witness':True,'complete_domain_enumerated':False}
        if k<=8:
            roots=domain(k,c)[-1]
            assert roots==xs and len(xs)==1<<k
            rec.update(complete_domain_enumerated=True,domain_size=len(xs),M=len(base(xs))//2)
        receipt['large_domain_checks'].append(rec)
    receipt['status']='PASS';write(args.out/'checks.json',receipt)
    print('PASS: 9 exact finite-domain solution bundles, 27 complete query sets, 7 high-depth witnesses',flush=True)

if __name__=='__main__':main()
