#!/usr/bin/env python3
"""Exact rectangular Semaev shift screen; no multivariate root theorem assumed."""
import hashlib, itertools, json, math, platform, sys
from pathlib import Path
import sympy as S

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'baseline'))
from parameters import CURVES
from curve_arithmetic import Curve
C=next(c for c in CURVES if c['name']=='P-256')
p,r=C['p'],C['r']; E=Curve(p,C['a'],C['b'])
x,y,z,w=S.symbols('x y z w')
def f3(x,y,z):
    a,b=C['a'],C['b']
    return (x-y)**2*z**2-2*((x+y)*(x*y+a)+2*b)*z+(x*y-a)**2-4*b*(x+y)

def coverage_width(s):
    # B denotes |u|<=B after an interval offset, at most B+1 distinct x's
    # for the nonnegative interval [0,B]; both signs give <=2(B+1) points.
    lo,hi=0,1
    while 2*math.comb(2*(hi+1)+s-1,s)<r-1: hi*=2
    while lo<hi:
        mid=(lo+hi)//2
        if 2*math.comb(2*(mid+1)+s-1,s)>=r-1: hi=mid
        else: lo=mid+1
    return lo

def screen(s,e,D,m):
    n=(D+1)**s
    K=sum((D-e*k+1)**s for k in range(1,min(m,D//e)+1))
    degree=2*s*D*n
    rhs=pow(p,4*K)
    # For B=2^b, exact strict inequality is n^(2n)*2^(n(n-1)+b*degree)<p^(4K).
    # Bit length gives a sufficient exact rejection before allocating the LHS.
    if n*(n-1)>=rhs.bit_length():
        best=None
    else:
        lhs=pow(n,2*n) << (n*(n-1))
        best=-1
        for b in range(257):
            if lhs << (b*degree) < rhs: best=b
            else: break
        if best<0: best=None
    req=coverage_width(s)
    # A looser family-wide consequence: beta < 2(D+1)/(e*s*D*(s+1));
    # D>=e implies beta < A=2(e+1)/(e^2*s*(s+1)). Test req>=p^A exactly.
    anum,aden=2*(e+1),e*e*s*(s+1)
    assert pow(req,aden)>pow(p,anum)
    return dict(variables=s,individual_degree=e,D=D,m=m,n=n,K=K,
                determinant_p_exponent=m*n-K,determinant_B_exponent=s*D*n//2,
                inequality_B_exponent=degree,largest_admissible_power_of_two_b=best,
                required_nonnegative_interval_width=req,
                required_width_log2=math.log2(req),family_relaxed_exponent=[anum,aden],
                required_width_exceeds_relaxed_family_bound=True)

def digit_screen():
    u0,u1,v0,v1=S.symbols('u0 u1 v0 v1'); radix=2**128
    t=next(E.lift(i) for i in range(1,128) if E.lift(i))[0]
    F=S.Poly(f3(u0+radix*u1,v0+radix*v1,t),u0,u1,v0,v1)
    lead=max(F.terms(),key=lambda ac:(sum(ac[0]),ac[0]))
    assert lead==((2,0,2,0),1) and F.total_degree()==4
    req=coverage_width(2)
    # Two digits give <=(B+1)^2 x-coordinates. req+1 x's are necessary.
    minimum_digit_B=math.isqrt(req+1)-1
    while (minimum_digit_B+1)**2<req+1:minimum_digit_B+=1
    cases=[]
    for D in range(4,13):
        n=math.comb(D+4,4);A=math.comb(D+4,5)
        K=sum(math.comb(D-4*k+4,4) for k in range(1,D//4+1))
        rhs=pow(p,4*K); base_exponent=n*(n-1)
        best=None
        if base_exponent<rhs.bit_length():
            lhs=pow(n,2*n)<<base_exponent
            for b in range(257):
                if lhs << (b*16*A)<rhs:best=b
                else:break
        cases.append({'D':D,'m':D//4,'n':n,'K':K,'A_per_digit':A,
                      'largest_admissible_power_of_two_b':best,
                      'minimum_digit_B_for_half_target_count':minimum_digit_B})
    return {'radix':radix,'digit_variables':4,'digits_per_coordinate':2,
            'polynomial_terms':len(F.terms()),'total_degree':4,
            'leading_monomial':[2,0,2,0],'leading_coefficient':1,
            'minimum_digit_B_log2':math.log2(minimum_digit_B),'cases':cases,
            'asymptotic_sufficient_exponent_per_digit':[1,16]}

def main():
    P=next(E.lift(i) for i in range(1,128) if E.lift(i) is not None)
    Q=E.mul(17,P); R=E.mul(29,P); T=E.add(E.add(P,Q),R)
    assert E.mul(r,P) is None
    t=T[0]
    F2=S.Poly(f3(x,y,t),x,y)
    F3=S.Poly(S.resultant(f3(x,y,z),f3(z,w,t),z),x,y,w)
    assert F2.degree_list()==(2,2) and F2.coeff_monomial(x*x*y*y)==1
    assert F3.degree_list()==(4,4,4) and F3.coeff_monomial(x**4*y**4*w**4)==1
    U=E.add(P,Q)
    f2relation=S.Poly(f3(x,y,U[0]),x,y)
    assert int(f2relation.eval({x:P[0],y:Q[0]}))%p==0
    assert int(F3.eval({x:P[0],y:Q[0],w:R[0]}))%p==0
    polys=[]
    for name,F in [('f3_two_unknowns',F2),('f4_three_unknowns',F3)]:
        polys.append(dict(name=name,variables=[str(v) for v in F.gens],terms=len(F.terms()),
            individual_degrees=list(F.degree_list()),total_degree=F.total_degree(),
            leading_coefficient=1))
        (HERE/(name+'.json')).write_text(json.dumps({'terms':[[list(a),str(int(b)%p)] for a,b in F.terms()]},indent=2)+'\n')
    # Actual triangular basis determinant check on actual P-256 f3 at D=2,m=1,B=2.
    D,m,B=2,1,2; mons=sorted(itertools.product(range(D+1),repeat=2),key=lambda a:(sum(a),a))
    rows=[]; ks=[]
    shifted=S.Poly(f2relation.as_expr().subs({x:x+P[0]-1,y:y+Q[0]-1}),x,y)
    shifted=S.Poly.from_dict({a:(int(c)+p//2)%p-p//2 for a,c in shifted.terms()},(x,y))
    assert int(shifted.eval({x:1,y:1}))%p==0
    for i,j in mons:
        k=min(m,i//2,j//2); ks.append(k)
        G=S.Poly(p**(m-k)*x**(i-2*k)*y**(j-2*k)*shifted.as_expr()**k,x,y)
        rows.append([int(G.coeff_monomial(x**a*y**b))*B**(a+b) for a,b in mons])
    M=S.Matrix(rows); n=len(mons); K=sum(ks)
    predicted=p**(m*n-K)*B**(2*D*n//2)
    assert abs(int(M.det()))==predicted
    # LLL itself is a bounded correctness example, not a scale measurement.
    L=M.lll(delta=S.Rational(3,4))
    assert abs(int(L.det()))==predicted
    # Evaluate p^m divisibility and recover integer polynomials from every row.
    divisible=0; zero_lift_candidates=0; lifted_polynomials=[]
    for row in L.tolist():
        coeff=[int(c)//B**sum(a) for c,a in zip(row,mons)]
        assert all(c%B**sum(a)==0 for c,a in zip(row,mons))
        val=sum(coeff)
        assert val%p==0; divisible+=1
        if n*sum(int(c)**2 for c in row)<p**(2*m):
            assert val==0
            zero_lift_candidates+=1
            lifted_polynomials.append(sum(c*x**a*y**b for c,(a,b) in zip(coeff,mons)))
    GB=S.groebner(lifted_polynomials,x,y,domain=S.QQ)
    assert GB.is_zero_dimensional
    assert list(GB)==[x-1,y-1]
    (HERE/'bounded_lattice_certificate.json').write_text(json.dumps({
        'offsets':[P[0]-1,Q[0]-1],'root':[1,1],'mons':[list(a) for a in mons],
        'basis_rows':rows,'lll_rows':[[int(v) for v in row] for row in L.tolist()],
        'integer_groebner_basis':[str(g) for g in GB]},indent=2)+'\n')
    cases=[screen(s,e,D,D//e) for s,e in [(2,2),(3,4)] for D in range(e,17)]
    out=dict(schema='f6-exact-screen-v1',task='TASK-20261025-f439ca',
        scope='implementation validation and sufficient-bound theory screen',curve=C,
        software={'python':platform.python_version(),'sympy':S.__version__},
        public_constructed_points={'P':P,'Q':Q,'R':R,'T':T},polynomials=polys,
        finite_cases=cases,digit_box=digit_screen(),triangular_and_lll_check={'D':2,'m':1,'B':2,
            'rows':n,'determinant_equal':True,'lll_determinant_equal':True,
            'modular_divisibility_rows':divisible,'norm_qualified_rows':zero_lift_candidates,
            'planted_roots_in_B2_box':True,'planted_root':[1,1],
            'offsets_chosen_using_known_root':True,
            'zero_dimensional_in_this_constructed_case':True,
            'integer_groebner_basis':[str(g) for g in GB],
            'general_root_recovery_claim':False},completion_sentinel=True)
    (HERE/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'completion_sentinel':True,'parameter_cases':len(cases),
        'polynomial_checks':2,'determinant_and_lll_rows':n,
        'largest_B_bits_by_s':{str(s):max((c['largest_admissible_power_of_two_b'] or 0) for c in cases if c['variables']==s) for s in [2,3]}}))

if __name__=='__main__':main()
