"""Separable Dickson cubic-divisor and repeated-stratum equations on P-256.

No benchmark. Set PYTHONDONTWRITEBYTECODE=1 to keep original F1 immutable.
"""
import hashlib,itertools,json,sys
from pathlib import Path
import sympy as sp
from flint import fmpz_mod_poly_ctx
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import f1
p=f1.p
V=sp.symbols('s1 s2 s3')
X,Y=sp.symbols('x y')
T=sp.Symbol('t')

def poly(e,vs=V):return sp.Poly(e,*vs,modulus=p)
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def record(f):return [[list(m),int(c)%p] for m,c in f.terms()]
def evaluate(f,values):
    return sum(int(c)*math_product(pow(x,e,p) for x,e in zip(values,m)) for m,c in f.terms())%p

def math_product(xs):
    z=1
    for x in xs:z=z*x%p
    return z

def shapes(fs):return [{'total_degree':int(f.total_degree()),'terms':len(f.terms())} for f in fs]
def remainder_circuit(k,c):
    """Three coefficients in Fp[s1,s2,s3][t]/(t^3-s1*t^2+s2*t-s3)."""
    u,v,w=map(poly,V);r0,r1,r2=poly(0),poly(1),poly(0)
    t4=(u*w,w-u*v,u*u-v);levels=[]
    for depth in range(1,k+1):
        c0,c1,c2,c3,c4=r0*r0,2*r0*r1,r1*r1+2*r0*r2,2*r1*r2,r2*r2
        r0,r1,r2=c0+w*c3+t4[0]*c4-2,c1-v*c3+t4[1]*c4,c2+u*c3+t4[2]*c4
        levels.append({'depth':depth,'coefficients':shapes([r0,r1,r2])})
    return [r0-c,r1,r2],levels

def repeated_equations(k,c):
    x,y=poly(X,(X,Y)),poly(Y,(X,Y));delta=poly(1,(X,Y))
    for _ in range(k):
        delta*=x+y
        x,y=x*x-2,y*y-2
    return [x-c,delta]

def s4_polynomial(Q,vs=V,sub=None):
    s=V if sub is None else sub
    return poly(sum(coef*sp.prod(s[j]**m[j] for j in range(3)) for m,coef in f1.s4_coeffs(Q[0])),vs)

def fixture(case_path,depth=None,target_kind='positive'):
    data=json.loads(case_path.read_text());k=depth or data['k'];c=data['terminal_c']
    if k!=data['k']:c=f1.domain(data['k']-k,c)[-1][0]
    xs=f1.domain(k,c)[-1];F=f1.base(xs)
    if target_kind=='positive':Q=f1.add(f1.add(F[0],F[len(F)//2]),F[-1])
    elif target_kind=='twoequal':
        P=F[0];R=next(Pt for Pt in F if Pt[0]!=P[0]);Q=f1.add(f1.add(P,P),R)
    elif target_kind=='allequal':Q=f1.mul(3,F[0])
    elif target_kind=='base':Q=F[0]
    elif target_kind=='generator':Q=f1.G
    else:raise ValueError(target_kind)
    assert Q is not None
    return {'k':k,'c':c,'xs':xs,'F':F,'Q':Q,'target_kind':target_kind,'input_file':str(case_path)}

def oracle(fix,stratum,with_s4=True):
    xs,Q=fix['xs'],fix['Q'];terms=f1.s4_coeffs(Q[0]);out=[]
    if stratum=='distinct':
        for triple in itertools.combinations(xs,3):
            s=f1.elementary(triple)
            if not with_s4 or f1.evaluate(terms,s)==0:out.append(s)
    elif stratum=='twoequal':
        for x in xs:
            for y in xs:
                if x==y:continue
                if not with_s4 or f1.evaluate(terms,f1.elementary((x,x,y)))==0:out.append((x,y))
    elif stratum=='allequal':
        for x in xs:
            if not with_s4 or f1.evaluate(terms,f1.elementary((x,x,x)))==0:out.append((x,))
    return sorted(set(out))

def root_triples(stratum,points):
    C=fmpz_mod_poly_ctx(p)
    for pt in points:
        if stratum=='distinct':
            u,v,w=pt;h=C([-w,v,-u,1]);roots=h.roots()
            assert len(roots)==3 and all(m==1 for _,m in roots)
            yield tuple(sorted(int(x) for x,m in roots))
        elif stratum=='twoequal':yield tuple(sorted((pt[0],pt[0],pt[1])))
        else:yield (pt[0],)*3

def recover(fix,stratum,points):
    return f1.recovered_solutions(fix['F'],fix['Q'],list(root_triples(stratum,points)))[0]

def rational_points(gens,vs):
    """Exact lex elimination and all finite-field roots, keeping every branch."""
    if not vs:return [()] if all(int(g)%p==0 for g in gens) else []
    gb=sp.groebner(gens,*vs,modulus=p,order='lex')
    if len(gb.polys)==1 and gb.polys[0].total_degree()==0:return []
    v=vs[-1];uni=[]
    for f in gb.polys:
        e=f.as_expr()
        if e.free_symbols<={v}:uni.append(sp.Poly(e,v,modulus=p))
    assert uni,'no univariate eliminant in claimed finite system'
    h=uni[0]
    for f in uni[1:]:h=sp.gcd(h,f)
    C=fmpz_mod_poly_ctx(p);hp=C([int(c)%p for c in reversed(h.all_coeffs())]);out=[]
    for root,multiplicity in hp.roots():
        z=int(root);sub=[f.as_expr().subs(v,z) for f in gb.polys]
        for pt in rational_points(sub,vs[:-1]):out.append(pt+(z,))
    return sorted(set(out))

def quotient_basis(gb):
    n=len(gb.gens);leads=[f.LM(order=gb.order).exponents for f in gb.polys]
    if any(not any(m) for m in leads):return []
    bounds=[min(m[j] for m in leads if m[j] and all(m[i]==0 for i in range(n) if i!=j)) for j in range(n)]
    return [m for m in itertools.product(*(range(b) for b in bounds))
            if not any(all(t[i]<=m[i] for i in range(n)) for t in leads)]

def certificate(gb,originals,expected):
    """Finite-domain certificate: independently known reduced ideal, exact zeros.

For this separable fully split input the true ideal is the vanishing ideal of
expected. G vanishes there, original generators reduce to zero by G, and its
finite standard monomial bound equals the number of points. These checks also
certify equality; critical pairs are checked explicitly as an adapter audit.
"""
    assert all(not gb.reduce(f.as_expr())[1] for f in originals)
    assert all(evaluate(f,pt)==0 for pt in expected for f in gb.polys)
    std=quotient_basis(gb);assert len(std)==len(expected)
    pairs=0
    for f,g in itertools.combinations(gb.polys,2):
        fm,gm=f.LM(order=gb.order).exponents,g.LM(order=gb.order).exponents
        lcm=tuple(max(x,y) for x,y in zip(fm,gm))
        mulf=sp.prod(v**(q-e) for v,q,e in zip(gb.gens,lcm,fm))
        mulg=sp.prod(v**(q-e) for v,q,e in zip(gb.gens,lcm,gm))
        sf=mulf*f.as_expr()*pow(int(f.LC(order=gb.order)),-1,p)-mulg*g.as_expr()*pow(int(g.LC(order=gb.order)),-1,p)
        assert not gb.reduce(sf)[1];pairs+=1
    return {'status':'PASS','original_generators_reduce_to_zero':True,
      'all_basis_polynomials_vanish_on_complete_oracle':True,'all_critical_pairs_zero':True,
      'critical_pairs_checked':pairs,'standard_monomial_count':len(std),
      'complete_reduced_oracle_point_count':len(expected),'standard_monomials':std,
      'scope':'exact finite-domain ideal equality using proved reduced fully split ideal; same-session check'}
