#!/usr/bin/env python3
"""Local arithmetic review. Never imports or executes producer source.

Run from anywhere with the supplied standalone Python environment. All output
goes to this owned review directory. Mathematical constants are copied from the
published definitions and checked against, rather than imported from, inputs.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations_with_replacement, product
from math import comb
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import traceback

import flint
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRACKS = ROOT / 'tracks'
P = 2**256-2**224+2**192+2**96-1
B = int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b',16)
R = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551',16)
GP = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16),
      int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16))
K = 2**256-2**32-977
KR = int('fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141',16)
GK = (int('79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',16),
      int('483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8',16))
READS = {}


def read(path):
    raw = path.read_bytes()
    READS[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class EC:
    """General short-Weierstrass Jacobian arithmetic with affine inputs."""
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def check(self, point):
        return point is None or (len(point)==2 and all(0<=u<self.p for u in point)
            and (point[1]**2-point[0]**3-self.a*point[0]-self.b)%self.p==0)

    def neg(self, point):
        return None if point is None else (point[0], -point[1]%self.p)

    def project(self, point):
        return (0,1,0) if point is None else (point[0],point[1],1)

    def normalize(self, point):
        u,v,w = point
        if not w:
            return None
        inv = pow(w,-1,self.p)
        return u*inv**2%self.p, v*inv**3%self.p

    def double(self, point):
        x,y,z = point
        if not y or not z:
            return (0,1,0)
        p=self.p
        h=y*y%p
        d=4*x*h%p
        e=(3*x*x+self.a*pow(z,4,p))%p
        xx=(e*e-2*d)%p
        return xx,(e*(d-xx)-8*h*h)%p,2*y*z%p

    def combine(self, left, right):
        x,y,z=left
        u,v,w=right
        if not z:
            return right
        if not w:
            return left
        p=self.p
        xx=x*w*w%p
        uu=u*z*z%p
        yy=y*pow(w,3,p)%p
        vv=v*pow(z,3,p)%p
        if xx==uu:
            return self.double(left) if yy==vv else (0,1,0)
        d=(uu-xx)%p
        e=(vv-yy)%p
        result=(e*e-d**3-2*xx*d*d)%p
        return result,(e*(xx*d*d-result)-yy*d**3)%p,d*z*w%p

    def add(self, left, right):
        return self.normalize(self.combine(self.project(left),self.project(right)))

    def mul(self, n, point):
        if n<0:
            return self.mul(-n,self.neg(point))
        out=(0,1,0)
        cur=self.project(point)
        while n:
            if n%2:
                out=self.combine(out,cur)
            cur=self.double(cur)
            n//=2
        return self.normalize(out)

    def linear(self, coeffs, points):
        out=(0,1,0)
        for c,point in zip(coeffs,points):
            if c:
                out=self.combine(out,self.project(self.mul(c,point)))
        return self.normalize(out)


EP, EK = EC(P,-3,B), EC(K,0,7)


def rank(rows, modulus, width=None):
    a=[[int(v)%modulus for v in row] for row in rows]
    ncols = len(a[0]) if a else width or 0
    at=0
    for j in range(ncols):
        pivot=next((i for i in range(at,len(a)) if a[i][j]),None)
        if pivot is None:
            continue
        a[at],a[pivot]=a[pivot],a[at]
        inv=pow(a[at][j],-1,modulus)
        a[at]=[v*inv%modulus for v in a[at]]
        for i in range(at+1,len(a)):
            c=a[i][j]
            if c:
                a[i]=[(v-c*w)%modulus for v,w in zip(a[i],a[at])]
        at+=1
        if at==len(a):
            break
    return at


def normalized_relations(items):
    return sorted((tuple(a['indices']),tuple(a['signs'])) for a in items)


def f3_checks():
    require(EP.check(GP) and EP.mul(R,GP) is None,'P-256 subgroup witness')
    uniform=[]
    adaptive=[]
    for q in [5,7,11]:
        for t1,t2 in product(range(q),repeat=2):
            c=(t2,-t1) if (t1,t2)!=(0,0) else (1,0)
            counts=Counter((c[0]*b1+c[1]*b2)%q for b1,b2 in product(range(q),repeat=2))
            require(set(counts.values())=={q} and len(counts)==q,'conditional useful law')
        uniform.append({'prime':q,'point_conditionings':q*q,'b_assignments_per_conditioning':q*q})
        nonzero=0
        for b in product(range(q),repeat=3):
            t=(1,2,3)
            c=((t[1]*b[2]-t[2]*b[1])%q,(t[2]*b[0]-t[0]*b[2])%q,(t[0]*b[1]-t[1]*b[0])%q)
            if not any(c):
                continue
            nonzero+=1
            require(sum(x*y for x,y in zip(c,t))%q==0,'adaptive control is a point relation')
            require(sum(x*y for x,y in zip(c,b))%q==0,'adaptive relation forces B zero')
        adaptive.append({'prime':q,'nonzero_label_dependent_relations':nonzero,'all_target_coefficients_zero':True})
    details=[]
    for name in ['natural_random','arranged_zero_Q','arranged_useful']:
        o=read(TRACKS/'f3'/'receipts'/'validation-02'/(name+'.json'))
        points=[tuple(z['point']) for z in o['base']]
        target=tuple(o['Q'])
        require(EP.check(target) and target is not None and EP.mul(R,target) is None,'target subgroup')
        require(len(set(x for x,y in points))==len(points),'unique coordinates')
        for z,point in zip(o['base'],points):
            require(EP.check(point),'point on curve')
            require(EP.add(EP.mul(z['a']%R,GP),EP.mul(z['b']%R,target))==point,'label agreement')
        expected=[]
        coordinate_roots=[]
        for i,j,k in product(*o['partitions']):
            hit=False
            for sj,sk in product((1,-1),repeat=2):
                if EP.add(points[i],points[j] if sj==1 else EP.neg(points[j]))==(
                        EP.neg(points[k]) if sk==1 else points[k]):
                    expected.append({'indices':[i,j,k],'signs':[1,sj,sk]})
                    hit=True
            if hit:
                coordinate_roots.append([i,j,k])
        for key in ['hybrid','exhaustive']:
            require(normalized_relations(expected)==normalized_relations(o[key]['relations']),'complete point-only search comparison')
        require(sorted(coordinate_roots)==sorted(o['hybrid']['coordinate_roots']),'rational coordinate roots')
        summaries=[]
        for rel,assessment in zip(o['hybrid']['relations'],o['assessments']):
            a=sum(s*o['base'][i]['a'] for i,s in zip(rel['indices'],rel['signs']))%R
            b=sum(s*o['base'][i]['b'] for i,s in zip(rel['indices'],rel['signs']))%R
            require((a,b)==(assessment['A'],assessment['B']),'assessed coefficients')
            require(EP.linear(rel['signs'],[points[i] for i in rel['indices']]) is None,'certified point sum')
            if b:
                recovered=-a*pow(b,-1,R)%R
                require(EP.mul(recovered,GP)==target and assessment['useful'],'recovered scalar witness')
            else:
                require(a==0 and not assessment['useful'],'zero-target coefficient rejected')
            summaries.append({'A_zero':a==0,'B_zero':b==0,'useful':bool(b)})
        require(len(o['assessments'])==len(expected),'all relation assessments present')
        for part,coeff in zip(o['partitions'],o['membership_polynomials_ascending']):
            poly=sp.Poly(1,sp.Symbol('X'),modulus=P)
            for i in part:
                poly*=sp.Poly(sp.Symbol('X')-points[i][0],sp.Symbol('X'),modulus=P)
            require([int(poly.nth(i))%P for i in range(len(part)+1)]==coeff,'membership polynomial')
        details.append({'case':name,'points_checked':len(points),'partition_triples':len(list(product(*o['partitions']))),
                        'relations':len(expected),'coefficients':summaries})
    # Literal nonzero integer c=(r) is zero as an F_r coefficient vector.
    require(EP.mul(R,GP) is None and (R*12345)%R==0,'integer multiplicity counterexample')
    return {'conditional_uniform_exhaustions':uniform,'adaptive_leakage_controls':adaptive,
            'certificate_cases':details,'integer_nonzero_vs_modular_nonzero_counterexample':{'c':[R], 'A_mod_r':0,'B_mod_r':0}}


def poly_trim(a):
    a=[int(v)%P for v in a]
    while len(a)>1 and a[-1]==0:
        a.pop()
    return a


def poly_add(a,b):
    return poly_trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])


def poly_mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,v in enumerate(a):
        for j,w in enumerate(b):
            out[i+j]=(out[i+j]+v*w)%P
    return poly_trim(out)


def poly_eval(a,x):
    value=0
    for v in reversed(a):
        value=(value*x+v)%P
    return value


def root_order(poly,x):
    """Synthetic division at x, including the normalized nonvanishing value."""
    a=poly_trim(poly)
    if a==[0]:
        return 1000000,0
    order=0
    while len(a)>1 and poly_eval(a,x)==0:
        q=[0]*(len(a)-1)
        q[-1]=a[-1]
        for j in range(len(q)-2,-1,-1):
            q[j]=(a[j+1]+x*q[j+1])%P
        require((a[0]+x*q[0])%P==0,'synthetic exact division')
        a=q
        order+=1
    return order,poly_eval(a,x)


def f4_case(o,ctx):
    a,b=map(poly_trim,(o['A'],o['B']))
    m=max(2*(len(a)-1) if a!=[0] else -1,3+2*(len(b)-1) if b!=[0] else -1)
    require(m==o['pole_order'],'pole order')
    nb=poly_mul([B,-3,0,1],poly_mul(b,b))
    norm=poly_add(poly_mul(a,a),[-v for v in nb])
    require(norm==o['norm'] and len(norm)-1==m,'full norm equality')
    complete=[o['norm_unit']]
    zeros={}
    unresolved=[]
    factor_count=0
    for item in o['norm_factors']:
        q=item['coefficients']
        e=item['multiplicity']
        require(item['degree']==len(q)-1 and q[-1]==1 and e>0,'factor metadata')
        require(ctx(q).is_irreducible(),'independent irreducible factor')
        factor_count+=1
        for _ in range(e):
            complete=poly_mul(complete,q)
        if len(q)!=2:
            unresolved.append({'norm_factor':q,'exponent':e,'degree':len(q)-1})
            continue
        xx=-q[0]*pow(q[1],-1,P)%P
        rhs=(xx**3-3*xx+B)%P
        require(rhs!=0,'no rational two-torsion fixture')
        if pow(rhs,(P-1)//2,P)!=1:
            unresolved.append({'norm_factor':q,'exponent':e,'reason':'nonsplit y'})
            continue
        yy=pow(rhs,(P+1)//4,P)
        va,aa=root_order(a,xx)
        vb,bb=root_order(b,xx)
        h=min(va,vb)
        # Divide both branches by their common (x-X)^h. At most one
        # normalized branch vanishes; the other has local valuation h.
        for yv in sorted({yy,-yy%P}):
            residual=((aa if va==h else 0)+yv*(bb if vb==h else 0))%P
            val=h if residual else e-h
            require(val>=0,'nonnegative local order')
            if val:
                zeros[(xx,yv)]=val
        require(sum(v for (xx2,_),v in zeros.items() if xx2==xx)==e,'norm valuation split')
    require(complete==norm,'complete norm factor product')
    declared={tuple(z['point']):z['multiplicity'] for z in o['zeros']}
    require(len(declared)==len(o['zeros']) and zeros==declared,'independent exact local multiplicities')
    require(unresolved==o['unresolved'],'all unresolved factors retained')
    require(all(EP.check(pt) for pt in zeros),'divisor points on curve')
    count=sum(zeros.values())
    full=not unresolved and count==m
    require((count,full)==(o['rational_degree'],o['fully_rational']),'rational completeness')
    row=Counter()
    per_x={}
    for (xx,yy),multiplicity in zeros.items():
        sign=1 if yy<=P//2 else -1
        row[str(xx)]+=sign*multiplicity
        per_x.setdefault(xx,[0,0])[sign<0]+=multiplicity
    row={k:v for k,v in row.items() if v}
    require(row==o['row'],'signed row')
    require(sum(min(v) for v in per_x.values())==o['inverse_pairs'],'inverse pair counts')
    anchors=Counter(tuple(pt) for pt in o['declared_anchors'])
    require(all(zeros.get(pt,0)>=v for pt,v in anchors.items()),'declared anchor multiplicity')
    if full:
        require(EP.linear(list(zeros.values()),list(zeros)) is None,'complete divisor group sum')
    require(o['group_sum_infinity']==full,'claimed divisor group status')
    return factor_count,len(zeros)


def f4_checks():
    cyclic=[]
    for q in [5,7,11,13]:
        for m in range(2,min(q,8)):
            actual=sum(sum(v)%q==0 for v in combinations_with_replacement(range(1,q),m))
            predicted=Fraction(comb(q+m-2,m),q)
            require(actual==predicted,'Burnside count')
            cyclic.append({'prime':q,'m':m,'count':actual})
    counts=read(TRACKS/'f4'/'receipts'/'exact-counts.json')
    for o in counts['controls']:
        m=o['pole_order']
        count=comb(R+m-2,m)//R
        prob=Fraction(count,P**(m-1))
        require(o['fully_rational_affine_effective_divisors']==count,'P-256 all-rational count')
        require(o['exact_pole_projective_functions']==P**(m-1),'exact sections count')
        require((o['fully_rational_probability_numerator'],o['fully_rational_probability_denominator'])==(prob.numerator,prob.denominator),'exact probability')
    ctx=flint.fmpz_mod_poly_ctx(P)
    require(ctx([B,-3,0,1]).is_irreducible(),'P-256 cubic independent irreducibility')
    folder=TRACKS/'f4'/'receipts'/'check-04'
    cases={}
    factors=branches=0
    for file in sorted(folder.glob('*.json')):
        o=read(file)
        if isinstance(o,dict) and 'norm' in o:
            fc,bc=f4_case(o,ctx)
            factors+=fc
            branches+=bc
            cases[o['id']]=o
    graphs=[]
    for file in sorted(folder.glob('graph_*.json')):
        o=read(file)
        rows=[cases[i]['row'] for i in o['case_ids']]
        allcols=o['all_columns']
        base=o['base_columns']
        outside=o['outside_columns']
        require(set(allcols)==set(base)|set(outside) and not set(base)&set(outside),'graph column partition')
        require(set(allcols)==set().union(*(set(row) for row in rows)),'complete graph columns')
        d=[[row.get(k,0) for k in allcols] for row in rows]
        incidence=[[row.get(k,0) for row in rows] for k in outside]
        kernel=[c['combination'] for c in o['cancelled_rows']]
        require(rank(kernel,R)==len(rows)-rank(incidence,R,width=len(rows)),'full outside kernel basis')
        outputs=[]
        canonical=[]
        for key in base:
            xx=int(key)
            y=pow((xx**3-3*xx+B)%P,(P+1)//4,P)
            canonical.append((xx,min(y,P-y)))
        for item in o['cancelled_rows']:
            c=item['combination']
            require(len(c)==len(rows),'combination size')
            require(all(sum(v*w for v,w in zip(c,line))%R==0 for line in incidence),'exact signed cancellation')
            row=[sum(v*raw.get(k,0) for v,raw in zip(c,rows))%R for k in base]
            require(item['row']=={k:v for k,v in zip(base,row) if v},'stitched output row')
            require(EP.linear(row,canonical) is None,'stitched group sum')
            outputs.append(row)
        rr,ar,cr=rank(d,R),rank(incidence,R,width=len(rows)),rank(outputs,R,width=len(base))
        require(rr-ar==cr,'cancellation rank identity')
        require((rr,ar,cr)==(o['rank_before_all_columns'],o['outside_incidence_rank'],o['rank_after_cancellation']),'graph claimed ranks')
        if file.stem=='graph_unbalanced_triangle':
            require(ar==3 and not kernel and cr==0,'unsigned triangle cannot cancel')
        graphs.append({'graph':file.stem,'ranks':[rr,ar,cr],'kernel_dimension':len(kernel)})
    inverse=cases['inverse_only']
    require(inverse['fully_rational'] and inverse['row']=={} and inverse['inverse_pairs']==1,'inverse-only rank-zero control')
    controls=read(folder/'sampling_controls.json')
    for o in controls:
        m=o['m']
        basis=[('A',i) for i in range(m//2+1)]+[('B',i) for i in range((m-3)//2+1)]
        require([list(v) for v in basis]==o['basis'],'sampler RR basis')
        evaluations=[[pow(pt[0],i,P)*(1 if kind=='A' else pt[1])%P for kind,i in basis] for pt in o['anchors']]
        rk=rank(evaluations,P,width=len(basis))
        require((rk,len(basis)-rk)==(o['evaluation_rank'],o['kernel_dimension']),'actual anchor evaluation rank')
        case=cases[o['case']]
        require(all((poly_eval(case['A'],pt[0])+pt[1]*poly_eval(case['B'],pt[0]))%P==0 for pt in o['anchors']),'sampler anchor evaluations')
    return {'small_cyclic_counts':cyclic,'exact_P256_probabilities_rechecked':len(counts['controls']),
            'complete_divisor_cases':len(cases),'norm_irreducible_factors':factors,'rational_local_branches':branches,
            'graphs':graphs,'sampler_anchor_laws_checked':len(controls),'inverse_only_rejected_as_information':True,
            'coverage':'final check-04 certificates; historical attempts are not re-executed'}


def sf3(x,y,t):
    return (x-y)**2*t*t-2*((x+y)*(x*y-3)+2*B)*t+(x*y+3)**2-4*B*(x+y)


def coverage_width(s):
    lo,hi=0,1
    def valid(b):
        return 2*comb(2*(b+1)+s-1,s)>=R-1
    while not valid(hi):
        hi*=2
    while lo<hi:
        mid=(lo+hi)//2
        if valid(mid):
            hi=mid
        else:
            lo=mid+1
    require(valid(lo) and (lo==0 or not valid(lo-1)),'minimal interval capacity threshold')
    return lo


def largest_b(n,k,exponent):
    rhs=P**(4*k)
    const=n*(n-1)
    if const>=rhs.bit_length():
        return None
    lhs=pow(n,2*n)<<const
    if lhs>=rhs:
        return None
    lo=0
    while (lhs<<((lo+1)*exponent))<rhs:
        lo+=1
    return lo


def f6_checks():
    o=read(TRACKS/'f6'/'receipt.json')
    require((o['curve']['p'],o['curve']['a'],o['curve']['b'],o['curve']['r'])==(P,-3,B,R),'F6 published curve constants')
    pts={k:tuple(v) for k,v in o['public_constructed_points'].items()}
    require(all(EP.check(v) for v in pts.values()),'F6 points on curve')
    require(pts['Q']==EP.mul(17,pts['P']) and pts['R']==EP.mul(29,pts['P']),'fixture point construction')
    require(pts['T']==EP.add(EP.add(pts['P'],pts['Q']),pts['R']),'three-point sum')
    x,y,z,w=sp.symbols('x y z w')
    t=pts['T'][0]
    polynomials=[sp.Poly(sf3(x,y,t),x,y),sp.Poly(sp.resultant(sf3(x,y,z),sf3(z,w,t),z),x,y,w)]
    for name,poly in zip(['f3_two_unknowns','f4_three_unknowns'],polynomials):
        emitted=read(TRACKS/'f6'/(name+'.json'))
        expected={tuple(a):int(v)%P for a,v in poly.terms()}
        require(expected=={tuple(a):int(v) for a,v in emitted['terms']},'complete independent summation polynomial coefficients')
    require(int(polynomials[1].eval({x:pts['P'][0],y:pts['Q'][0],w:pts['R'][0]}))%P==0,'three-point polynomial witness')
    widths={s:coverage_width(s) for s in [2,3]}
    finite=[]
    for c in o['finite_cases']:
        s,e,d,m=c['variables'],c['individual_degree'],c['D'],c['m']
        n=(d+1)**s
        # Sum floor-min values directly instead of only the layer-count formula.
        k=sum(min(m,*(u//e for u in a)) for a in product(range(d+1),repeat=s))
        require(k==sum((d-e*j+1)**s for j in range(1,min(m,d//e)+1)),'determinant K by direct enumeration')
        best=largest_b(n,k,2*s*d*n)
        require((n,k,m*n-k,s*d*n//2,best)==(c['n'],c['K'],c['determinant_p_exponent'],c['determinant_B_exponent'],c['largest_admissible_power_of_two_b']),'rectangular exact window')
        require(c['required_nonnegative_interval_width']==widths[s],'interval endpoint convention')
        require(widths[s]**(e*e*s*(s+1))>P**(2*(e+1)),'capacity exceeds relaxed family-wide bound')
        finite.append({'s':s,'D':d,'K':k,'largest_B_power_of_two':best})
    digit=o['digit_box']
    bmin=sp.integer_nthroot(widths[2]+1,2)[0]-1
    while (bmin+1)**2<widths[2]+1:
        bmin+=1
    u0,u1,v0,v1=sp.symbols('u0 u1 v0 v1')
    digitpoly=sp.Poly(sf3(u0+2**128*u1,v0+2**128*v1,pts['P'][0]),u0,u1,v0,v1)
    leading=max(digitpoly.terms(),key=lambda term:(sum(term[0]),term[0]))
    require(leading==((2,0,2,0),1),'digit leading monomial')
    for c in digit['cases']:
        d=c['D']
        n=comb(d+4,4)
        aa=comb(d+4,5)
        kk=sum(comb(d-4*j+4,4) for j in range(1,c['m']+1))
        require((n,aa,kk)==(c['n'],c['A_per_digit'],c['K']),'digit exact determinant exponents')
        require(largest_b(n,kk,16*aa)==c['largest_admissible_power_of_two_b'],'digit sufficient bound')
        require(c['minimum_digit_B_for_half_target_count']==bmin,'digit cardinality convention')
    cert=read(TRACKS/'f6'/'bounded_lattice_certificate.json')
    require(cert['root']==[1,1] and cert['offsets']==[pts['P'][0]-1,pts['Q'][0]-1],'known-root offset fixture')
    u=EP.add(pts['P'],pts['Q'])
    shifted=sp.Poly(sf3(x+cert['offsets'][0],y+cert['offsets'][1],u[0]),x,y)
    shifted=sp.Poly.from_dict({a:(int(v)+P//2)%P-P//2 for a,v in shifted.terms()},(x,y))
    require(int(shifted.eval({x:1,y:1}))%P==0,'offset modular root')
    mons=sorted(product(range(3),repeat=2),key=lambda a:(sum(a),a))
    require([list(a) for a in mons]==cert['mons'],'bounded lattice monomials')
    rows=[]
    for i,j in mons:
        kk=min(i//2,j//2,1)
        gg=sp.Poly(P**(1-kk)*x**(i-2*kk)*y**(j-2*kk)*shifted.as_expr()**kk,x,y)
        rows.append([int(gg.nth(a,b))*2**(a+b) for a,b in mons])
    require(rows==cert['basis_rows'],'full bounded basis from actual curve equation')
    mm,ll=sp.Matrix(rows),sp.Matrix(cert['lll_rows'])
    require(abs(mm.det())==P**8*2**18,'exact bounded lattice determinant')
    change=ll*mm.inv()
    require(all(v.q==1 for v in change) and abs(change.det())==1,'integer unimodular row transformation')
    lifted=[]
    for row in ll.tolist():
        require(all(v%2**sum(a)==0 for a,v in zip(mons,row)),'integral polynomial descaling')
        coeff=[int(v)//2**sum(a) for a,v in zip(mons,row)]
        require(sum(coeff)%P==0,'each lattice row modular divisibility')
        if 9*sum(v*v for v in row)<P*P:
            require(sum(coeff)==0,'strict sufficient norm gives integer zero')
            lifted.append(sum(c*x**a*y**b for (a,b),c in zip(mons,coeff)))
    gb=sp.groebner(lifted,x,y,domain=sp.QQ)
    require(gb.is_zero_dimensional and list(gb)==[x-1,y-1],'certified bounded extraction ideal')
    require(not sp.groebner([x-1],x,y,domain=sp.QQ).is_zero_dimensional,'one polynomial extraction negative control')
    return {'polynomial_term_counts':[len(v.terms()) for v in polynomials],'finite_windows':finite,
            'capacity_minimum_B':{str(s):v for s,v in widths.items()},'digit_cases':len(digit['cases']),
            'known_root_lattice':{'rows':len(rows),'qualified_integer_zero_rows':len(lifted),'groebner_basis':[str(v) for v in gb],
                'unimodular_transform':True,'offsets_depend_on_solution':True},'insufficient_extraction_control_rejected':True}


def f8_checks():
    o=read(TRACKS/'f8'/'orbit_certificate.json')
    require((o['curve']['p'],o['curve']['a'],o['curve']['b'],o['curve']['r'])==(K,0,7,KR),'secp constants')
    require(tuple(o['generator'])==GK and EK.check(GK) and EK.mul(KR,GK) is None,'secp subgroup generator')
    beta,lam=o['beta'],o['lambda']
    require(beta==pow(2,(K-1)//3,K) and beta!=1 and (beta*beta+beta+1)%K==0,'field scalar automorphism')
    require(lam!=1 and (lam*lam+lam+1)%KR==0,'subgroup eigenvalue equation')
    require(EK.mul(lam,GK)==(beta*GK[0]%K,GK[1]),'eigenvalue action on generator')
    require(EK.mul(o['other_lambda'],GK)!=(beta*GK[0]%K,GK[1]),'conjugate eigenvalue rejected')
    reps=[tuple(v) for v in o['representatives']]
    points=[tuple(v) for v in o['points']]
    mapping=o['representative_index']
    factors=o['compression_factor']
    require(len(set(points))==48 and len(reps)==8,'orbit disjointness')
    allowed={sign*pow(lam,j,KR)%KR for sign in [1,-1] for j in range(3)}
    require(len(allowed)==6,'six scalar actions')
    for i,pt in enumerate(reps,1):
        require(pt==EK.mul(i,GK),'public representative fixture labels')
    for pt,i,factor in zip(points,mapping,factors):
        require(EK.check(pt) and factor in allowed and pt==EK.mul(factor,reps[i]),'every point-to-representative action')
    full=[]
    compressed=[]
    for file in sorted((TRACKS/'f8').glob('matrix_block_*.json')):
        for item in read(file):
            row=item['full']
            require(len(row)==48,'full row shape')
            require(EK.linear(row,points) is None,'raw relation point sum')
            small=[0]*8
            for c,i,factor in zip(row,mapping,factors):
                small[i]=(small[i]+c*factor)%KR
            require(small==item['compressed'],'exact compression matrix action')
            require(sum(v*(i+1) for i,v in enumerate(small))%KR==0,'compressed homogeneous point relation')
            full.append(row)
            compressed.append(small)
    constraints=read(TRACKS/'f8'/'symmetry_constraints.json')
    for row in constraints:
        image=[0]*8
        for c,i,factor in zip(row,mapping,factors):
            image[i]=(image[i]+c*factor)%KR
        require(not any(image),'symmetry row in kernel of C')
    sr,rr,jr,cr=rank(constraints,KR),rank(full,KR),rank(constraints+full,KR),rank(compressed,KR)
    require(sr==48-8 and jr-sr==cr and cr==7,'compression quotient rank identity')
    false=[1]+[0]*7
    require(rank(compressed+[false],KR)==8 and EK.linear(false,reps) is not None,'false compressed full-rank relation rejected')
    require(any((pt[1]**2-(2*pt[0])**3-7)%K for pt in reps),'nonroot beta action rejected')
    return {'points':len(points),'raw_rows':len(full),'ranks':{'symmetry':sr,'full':rr,'joint':jr,'compressed':cr},
            'rank_identity':jr-sr==cr,'false_rank_eight_control_rejected':True,
            'fairness':'algebraic compression is equally available to both conventional relation solving and generic automorphism-aware baselines; no cost comparison run'}


def main():
    output=HERE/'independent-results.json'
    require(not output.exists(),'write-once output path already exists')
    report={'schema':'local-independent-relations-bounds/v1','task':'TASK-20261025-6d88b2',
            'created_utc':datetime.now(timezone.utc).isoformat(),'command':sys.argv,'python':sys.version,
            'executable':sys.executable,'platform':platform.platform(),'sympy':sp.__version__,'python_flint':flint.__version__,
            'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'scientific_review_gate_discharged':False,'producer_imports':False,'sections':{}}
    for name,fn in [('F3',f3_checks),('F4',f4_checks),('F6',f6_checks),('F8',f8_checks)]:
        try:
            data=fn()
            report['sections'][name]={'status':'passed','details':data}
            print(json.dumps({'section':name,'status':'passed'}),flush=True)
        except Exception as error:
            report['sections'][name]={'status':'failed','error':str(error),'traceback':traceback.format_exc()}
            print(json.dumps({'section':name,'status':'failed','error':str(error)}),flush=True)
    report['input_sha256']=READS
    report['status']='passed' if all(v['status']=='passed' for v in report['sections'].values()) else 'failed'
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'output':str(output)}),flush=True)
    return 0 if report['status']=='passed' else 1


if __name__=='__main__':
    sys.exit(main())
