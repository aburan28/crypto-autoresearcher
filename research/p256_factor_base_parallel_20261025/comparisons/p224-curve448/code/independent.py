"""Independent checker: no producer import or shared arithmetic.

Affine secant/tangent sums, quadratic-resultant S4, polynomial convolution,
and independent FLINT roots verify the exported finite domains and full sets.
"""
import hashlib,itertools,json,sys,time
from pathlib import Path
from flint import fmpz,fmpz_mod_poly_ctx

ROOT=Path(__file__).resolve().parent.parent
def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def point_add(P,Q,p,a):
    if P is None:return Q
    if Q is None:return P
    x,y=P;u,v=Q
    if x==u:
        if (y+v)%p==0:return None
        numerator=3*x*x+a;denominator=2*y
    else:numerator=v-y;denominator=u-x
    slope=numerator*pow(denominator%p,-1,p)%p
    out=(slope*slope-x-u)%p
    return out,(slope*(x-out)-y)%p

def scalar(n,P,p,a):
    # Left-to-right ladder, unlike the producer's right-to-left Jacobians.
    acc=None
    for bit in bin(n)[2:]:
        acc=point_add(acc,acc,p,a)
        if bit=='1':acc=point_add(acc,P,p,a)
    return acc

def pmul(a,b,p):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]=(out[i+j]+x*y)%p
    return out

def f3quadratic(x,y,a,b,p):
    return ((x-y)**2%p,-2*((x+y)*(x*y+a)+2*b)%p,((x*y-a)**2-4*b*(x+y))%p)

def resultant(x,y,z,t,a,b,p):
    A,B,C=f3quadratic(x,y,a,b,p);D,E,F=f3quadratic(z,t,a,b,p)
    return ((A*F-C*D)**2-(A*E-B*D)*(B*F-C*E))%p

def check(path):
    cert=load(path);c=cert['parameters'];p=c['p'];a=c['a'];b=c['b'];r=c['r'];dom=cert['domain'];S=dom['S']
    assert fmpz(p).is_prime() and fmpz(r).is_prime()
    assert p==(2**224-2**96+1 if c['name']=='P-224' else 2**448-2**224-1)
    assert c['h']==(1 if c['name']=='P-224' else 4)
    if c['name']=='Curve448':
        assert c['montgomery_A']==156326
        assert a==(1-156326**2*pow(3,-1,p))%p
        assert b==(2*156326**3*pow(27,-1,p)-156326*pow(3,-1,p))%p
        assert cert['public_generator'][0]==(5+156326*pow(3,-1,p))%p
    assert dom['c'] not in [2,p-2] and S in (16,32,64)
    ambient=p-1 if c['mode']=='split' else p+1
    assert ambient==dom['ambient_order'] and (ambient&-ambient).bit_length()-1==dom['two_adicity']
    # Verify explicit exact-order generator and coset directly from data.
    if c['mode']=='split':
        mul=lambda z,w:z*w%p
        one=1
        power=lambda z,n:pow(z,n,p)
        trace=lambda z:(z+pow(z,-1,p))%p
    else:
        assert p%4==3
        def mul(z,w):return ((z[0]*w[0]-z[1]*w[1])%p,(z[0]*w[1]+z[1]*w[0])%p)
        one=(1,0)
        def power(z,n):
            acc=one
            for bit in bin(n)[2:]:
                acc=mul(acc,acc)
                if bit=='1':acc=mul(acc,z)
            return acc
        trace=lambda z:2*z[0]%p
        for z in (dom['alpha'],dom['zeta']):assert (z[0]*z[0]+z[1]*z[1])%p==1
    alpha=dom['alpha'];g=dom['zeta']
    if c['mode']!='split':alpha=tuple(alpha);g=tuple(g)
    assert power(g,S)==one and power(g,S//2)!=one
    assert trace(power(alpha,S))==dom['c']
    xs=sorted(trace(mul(alpha,power(g,k))) for k in range(S))
    assert xs==dom['roots'] and len(set(xs))==S
    # Characteristic polynomial and complete linear factorization.
    polynomial=[0,1]
    for _ in range(S.bit_length()-1):
        polynomial=pmul(polynomial,polynomial,p);polynomial[0]=(polynomial[0]-2)%p
    polynomial[0]=(polynomial[0]-dom['c'])%p
    product=[1]
    for x in xs:product=pmul(product,[-x%p,1],p)
    assert product==polynomial==dom['polynomial_coefficients']
    C=fmpz_mod_poly_ctx(p);H=C(polynomial)
    assert H.gcd(H.derivative()).degree()==0
    assert sorted((int(z),m) for z,m in H.roots())==[(x,1) for x in xs]
    M=[];excluded=0
    for x,row in zip(xs,cert['lifts']):
        assert x==row['x'];rhs=(x**3+a*x+b)%p;y=row['y']
        if y is None:
            assert rhs and pow(rhs,(p-1)//2,p)==p-1 and row['status']=='non-lift';excluded+=1;continue
        assert y*y%p==rhs and y<=p-y
        if y==0:assert row['status']=='zero-y exclusion';excluded+=1;continue
        residual=scalar(r,(x,y),p,a)
        assert residual==(None if row['r_multiple'] is None else tuple(row['r_multiple']))
        if residual is None:assert row['status']=='accepted';M.append((x,y))
        else:assert row['status']=='cofactor rejection';excluded+=1
    assert M==[tuple(P) for P in cert['canonical_M']]
    F=[tuple(P) for P in cert['signed_base']]
    assert F==[P for x,y in M for P in [(x,y),(x,-y%p)]]
    G=tuple(cert['public_generator']);assert G[1]**2%p==(G[0]**3+a*G[0]+b)%p and scalar(r,G,p,a) is None
    reports=[]
    for summary in cert['cases']:
        cp=ROOT/summary['certificate'];case=load(cp);Q=tuple(case['target']);expected=[]
        # Exact affine brute-force point sums, with a different pairing order.
        for i,j,k in itertools.combinations_with_replacement(range(len(F)),3):
            if point_add(F[j],point_add(F[k],F[i],p,a),p,a)==Q:expected.append((i,j,k))
        assert expected==[tuple(v) for v in case['complete_signed_solutions']]
        algebraic=[]
        for xx in itertools.combinations_with_replacement(xs,3):
            if resultant(*xx,Q[0],a,b,p)==0:algebraic.append(xx)
        assert algebraic==[tuple(row['x']) for row in case['S4_zero_candidates']]
        if case['control']=='constructed-positive-repeated':
            assert point_add(M[0],point_add(M[0],M[min(1,len(M)-1)],p,a),p,a)==Q
            assert any(len({F[i][0] for i in triple})<3 for triple in expected)
        elif case['control']=='base-cancellation':
            assert Q==M[-1]
            assert all(tuple(sorted([2*i,2*i+1,2*(len(M)-1)])) in expected for i in range(len(M)))
        else:assert Q==G
        reports.append(dict(control=case['control'],solutions=len(expected),S4_candidates=len(algebraic),
          repeated_coordinate_solutions=sum(len({F[i][0] for i in triple})<3 for triple in expected),
          certificate_sha256=digest(cp),point_sum_complete=True,resultant_domain_complete=True))
    return dict(domain_certificate=str(path.relative_to(ROOT)),sha256=digest(path),curve=c['name'],S=S,
                M=len(M),excluded_domain_coordinates=excluded,controls=reports,all_checks_passed=True)

if __name__=='__main__':
    started=time.time();records=[]
    for path in sorted((ROOT/'certificates').glob('*-domain.json')):
        result=check(path);records.append(result);print(json.dumps(result),flush=True)
    out=dict(schema='independent-finite-comparison-check/v1',status='PASS',producer_arithmetic_imported=False,
      checks=records,source_sha256=digest(Path(__file__)),python=sys.version,wall_seconds=time.time()-started,
      limitation='Independent implementation by the same executor session; no independent scientific review or promotion.')
    (ROOT/'independent-result.json').write_text(json.dumps(out,indent=2)+'\n')
