"""Additional exact controls and representation witnesses, using reviewer code only."""
import itertools,json,math,sys,time,hashlib,resource
from pathlib import Path
import sympy as sp
import independent_check as ic
P=ic.P
OUT=Path(__file__).resolve().parent
result={};start=time.monotonic()
# Symbolic map and normalized dual identities over a generic characteristic-zero field.
u,a,b=sp.symbols('u a b');f=u**3+a*u**2+b*u
X=u+a+b/u;scale=1-b/u**2;bb=a*a-4*b
identity=sp.cancel(f*scale**2-(X**3-2*a*X**2+bb*X))
ic.need(identity==0,'universal quotient curve identity')
dx=(X-2*a+bb/X)/4
mx=3*u*u+2*a*u+b
expectedx=mx*mx/(4*f)-a-2*u
ic.need(sp.cancel(dx-expectedx)==0,'universal dual x duplication')
dy_over_y=scale*(1-bb/X**2)/8
expectedy_over_y=mx*(u-expectedx)/(2*f)-1
ic.need(sp.cancel(dy_over_y-expectedy_over_y)==0,'universal dual y duplication')
result['universal_isogeny_identities']='PASS: curve equation and dual x/y doubling rational identities'
# Truly nonrational auxiliary coordinate, beyond a merely wrong y-coordinate.
x=next(x for x in range(1,100) if pow(ic.rhs(x,ic.AUX),(P-1)//2,P)==P-1)
ic.need(ic.root(ic.rhs(x,ic.AUX)) is None,'nonsquare auxiliary x rejected')
result['nonsquare_auxiliary_control']={'x':x,'quadratic_character':-1,'rational_point_exists':False}
# The reviewer projective scalar routine has affine positive and non-order controls.
G=(48439561293906451759052585252797914202762949526041747995844080717082404635286,
36134250956749795798585127919587881956611106672985015071877198253568414405109)
for n in [0,1,2,3,7,31,257,65537]:
    j=ic.shortmul(n,G,-3)
    if j[2]:
        zi=pow(j[2],-1,P);Q=(j[0]*zi*zi%P,j[1]*zi**3%P)
    else:Q=None
    ic.need(Q==ic.mul(n,G,ic.TARGET),'projective vs affine independent reviewer arithmetic')
ic.need(ic.shortmul(ic.R,G,-3)[2]==0 and ic.shortmul(ic.R-1,G,-3)[2]!=0,'order/non-order controls')
result['reviewer_scalar_controls']={'affine_comparisons':8,'true_order_and_false_order_checked':True}
# Recompute original symmetric-terminal lengths for generic c at k=1,2.
u,v,w=sp.symbols('u v w');gens=(u,v,w);outputs=(u,v,w);terminal=ic.read(ic.BASE/'tracks/f1/checks-02/generic-k3.json')['terminal_c']
lengths=[]
for k in [1,2]:
    U,V,W=outputs
    outputs=tuple(sp.Poly(e,*gens,modulus=P).as_expr() for e in
        (U*U-2*V-6,V*V-2*U*W-4*U*U+8*V+12,W*W-2*V*V+4*U*W+4*U*U-8*V-8))
    equations=[outputs[0]-3*terminal,outputs[1]-3*terminal**2,outputs[2]-terminal**3]
    gb=sp.groebner(equations,*gens,modulus=P,order='grevlex')
    leads=[f.LM(order=gb.order).exponents for f in gb.polys]
    bounds=[min(m[j] for m in leads if m[j] and all(m[i]==0 for i in range(3) if i!=j)) for j in range(3)]
    length=sum(not any(all(x>=y for x,y in zip(m,l)) for l in leads) for m in itertools.product(*(range(n) for n in bounds)))
    N=2**k;roots=ic.dickson(k,terminal).roots()
    ic.need(len(roots)==N and all(m==1 for x,m in roots),'generic scalar squarefree split reference')
    ic.need(length==N**3,'independent symmetric terminal quotient length')
    weighted=6*math.comb(N,3)+3*N*(N-1)+N
    ic.need(weighted==length,'symmetric local multiplicities sum')
    lengths.append({'k':k,'quotient_length':length,'geometric_points':math.comb(N+2,3),'nonreduced':length>math.comb(N+2,3)})
result['symmetric_terminal_lengths']=lengths
# High-depth determinant without expanding F: F'(r)/h'(r), using scalar differentiation.
items=ic.read(ic.BASE/'tracks/f1/cubic-divisor/checks-01/identities.json')['deep_distinct_witnesses'];deep=[]
for item in items:
    k=item['k'];roots=item['three_distinct_roots'];c=item['c'];s=ic.elementary(roots)
    ic.need(c not in [2,P-2] and len(set(roots))==3,'generic deep triple')
    ic.need(list(s)==item['symmetric'],'deep symmetric coordinates')
    res=1
    for r in roots:
        value=r;derivative=1
        for j in range(k):derivative=2*value*derivative%P;value=(value*value-2)%P
        ic.need(value==c,'deep root by independent scalar composition')
        hp=math.prod((r-z)%P for z in roots if z!=r)%P
        res=res*derivative*pow(hp,-1,P)%P
    ic.need(res!=0 and res==item['jacobian_determinant'],'deep Jacobian via derivative/resultant identity')
    U,V,W=s
    for j in range(k):U,V,W=(U*U-2*V-6)%P,(V*V-2*U*W-4*U*U+8*V+12)%P,(W*W-2*V*V+4*U*W+4*U*U-8*V-8)%P
    ic.need((U,V,W)==(3*c%P,3*c*c%P,c**3%P),'deep symmetric terminal')
    deep.append({'k':k,'roots_verified':3,'jacobian_nonzero':True,'complete_solver_claim':False})
result['deep_representation_witnesses']=deep
record={'status':'PASS','assertions':ic.count,'observations':result,'command':[sys.executable,*sys.argv],
'wall_seconds':time.monotonic()-start,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
'reviewer_dependency_sha256':hashlib.sha256((OUT/'independent_check.py').read_bytes()).hexdigest(),
'producer_imports':False,'official_research_gate':False}
p=OUT/'controls-and-depth.json'
if p.exists():raise SystemExit('refuse overwrite')
p.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
