"""Bounded exact forward symmetric elimination; supervisor preserves watchdogs.

The Groebner adapter supplies candidates. Completeness at fixed domain depth is
checked separately against every inverse-recursion multiset. No unsupported
claim that this is a scalable solver or independently certified Groebner engine.
"""
import argparse,itertools,json,math,sys
from pathlib import Path
import sympy as sp
from flint import fmpz_mod_poly_ctx
from f1 import p,phi,elementary,domain,base,add,s4_coeffs,evaluate,write,digest

V=sp.symbols('s1 s2 s3')
def poly(x):return sp.Poly(x,*V,modulus=p)
def as_record(f):return [[list(m),int(c)%p] for m,c in f.terms()]
def event(kind,**d):print(json.dumps({'event':kind,**d}),flush=True)
def degrees(fs):return [{'total_degree':f.total_degree(),'terms':len(f.terms())} for f in fs]
def forward(k,c):
    u,v,w=map(poly,V)
    levels=[]
    for level in range(k):
        u,v,w=u*u-2*v-6,v*v-2*u*w-4*u*u+8*v+12,w*w-2*v*v+4*u*w+4*u*u-8*v-8
        levels.append({'level':level+1,'polynomials':degrees([u,v,w])})
    return [u-3*c,v-3*c*c,w-c*c*c],levels

def quotient_dimension(gb):
    leads=[f.LM(order=gb.order).exponents for f in gb.polys]
    bounds=[]
    for j in range(len(V)):
        bounds.append(min(m[j] for m in leads if m[j] and all(m[i]==0 for i in range(len(V)) if i!=j)))
    standard=[m for m in itertools.product(*(range(b) for b in bounds))
              if not any(all(t[i]<=m[i] for i in range(3)) for t in leads)]
    return len(standard),standard

def rational_points(gens,vs):
    if not vs:
        return [()] if all(int(g)%p==0 for g in gens) else []
    gb=sp.groebner(gens,*vs,modulus=p,order='lex')
    if len(gb.polys)==1 and gb.polys[0].total_degree()==0:return []
    v=vs[-1];uni=[]
    for f in gb.polys:
        e=f.as_expr()
        if e.free_symbols <= {v}:uni.append(sp.Poly(e,v,modulus=p))
    assert uni,'zero-dimensional elimination missing'
    h=uni[0]
    for f in uni[1:]:h=sp.gcd(h,f)
    C=fmpz_mod_poly_ctx(p);hp=C([int(c)%p for c in reversed(h.all_coeffs())])
    points=[]
    for root,mult in hp.roots():
        z=int(root)
        sub=[f.as_expr().subs(v,z) for f in gb.polys]
        for pt in rational_points(sub,vs[:-1]):points.append(pt+(z,))
    return sorted(set(points))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mode',choices=['membership','joint'],required=True)
    ap.add_argument('--depth',type=int);args=ap.parse_args()
    data=json.loads(args.case.read_text());k=args.depth or data['k'];c=data['terminal_c']
    # A depth-one subfibre inherits its terminal by descending one level.
    if k!=data['k']:c=domain(data['k']-k,c)[-1][0]
    xs=domain(k,c)[-1];F=base(xs)
    Q=add(add(F[0],F[len(F)//2]),F[-1]);assert Q is not None
    equations,levels=forward(k,c)
    terms=s4_coeffs(Q[0]);s4=poly(sum(coef*sp.prod(V[i]**m[i] for i in range(3)) for m,coef in terms))
    if args.mode=='joint':equations.append(s4)
    event('input',k=k,c=c,mode=args.mode,input_degrees=degrees(equations),levels=levels)
    event('groebner-start',order='grevlex',adapter='SymPy 1.14.0 default Buchberger')
    gb=sp.groebner([f.as_expr() for f in equations],*V,modulus=p,order='grevlex')
    dim,std=quotient_dimension(gb)
    event('groebner-end',polynomials=len(gb.polys),quotient_dimension=dim,degrees=degrees(gb.polys))
    out={'status':'PASS','mode':args.mode,'k':k,'c':c,'Q':Q,'source_case':str(args.case),
         'equations':[as_record(f) for f in equations],'levels':levels,
         'adapter':'SymPy 1.14.0, default Buchberger, grevlex; lex recursive elimination for rational points',
         'quotient_dimension':dim,'quotient_standard_monomials':std,
         'groebner_basis':[as_record(f) for f in gb.polys],
         'independent_ideal_membership_witnesses':False}
    states=list(itertools.combinations_with_replacement(xs,3))
    expected=sorted({elementary(s) for s in states if args.mode=='membership' or evaluate(terms,elementary(s))==0})
    # Every geometric membership solution is a split domain triple: all roots of
    # the fully split D_S-c lie in Fp. Radical computation is avoided here.
    if args.mode=='joint':
        points=rational_points([f.as_expr() for f in gb.polys],V)
        assert points==expected
        for point in points:
            assert all(int(f.as_expr().subs(dict(zip(V,point))))%p==0 for f in equations)
        out.update(rational_points=points,complete_finite_domain_check=True)
    out.update(distinct_membership_states=len(states),finite_domain_zero_states=len(expected),
               finite_domain_solution_digest=digest(expected),nonreduced_quotient=dim>len(expected))
    write(args.out,out);event('complete',finite_domain_zero_states=len(expected),quotient_dimension=dim)

if __name__=='__main__':main()
