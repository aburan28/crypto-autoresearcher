"""Blind geometric control: recover base locus, then line/conic sections.

Classical split-cubic-pencil geometry; no algorithmic novelty claimed.
The solver receives only p,a,b,G,R,d and outputs polynomial section maps.
"""
from pathlib import Path
import sys, json, time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from blind_sections import cubic,second,validate,class_oracle
from core import nullspace,monomials,combinations,EC
from flint import nmod_poly,nmod
import flint


def square_roots(a,p):
    try:y=int(nmod(a,p).sqrt())
    except flint.utils.flint_exceptions.DomainError:return []
    return sorted({y,-y%p})


def recover_base(data):
    p=data['p'];x=nmod_poly([0,1],p);f=x**3+data['a']*x+data['b']
    zero=nmod_poly([],p);U=zero;V=zero
    # G affine: monomial order is X^i Y^j Z^(3-i-j).
    pos=0
    for i in range(4):
        for j in range(4-i):
            c=data['G'][pos];pos+=1
            if j%2:U+=c*x**i*f**(j//2)
            else:V+=c*x**i*f**(j//2)
    elim=V*V-U*U*f
    points=[]
    for xx,m in elim.roots():
        xx=int(xx)
        for yy in square_roots(int(f(xx)),p):
            if (int(U(xx))*yy+int(V(xx)))%p==0:points.append((xx,yy))
    # Input family guarantees all 9 base points are finite, distinct and split.
    assert len(set(points))==9
    return sorted(set(points))


def polynomial_value(coeffs,xyz,p):return sum(c*v for c,v in zip(coeffs,monomials((*xyz,1),len_degree(coeffs))))%p


def len_degree(cs):return 1 if len(cs)==3 else 2


def parameterize(data,base,subset,poly):
    p=data['p'];d=data['d'];R=data['R'];v=nmod_poly([0,1],p)
    if d==1:
        A=base[subset[0]]
        XYZ=[nmod_poly([R[i],A[i]],p) for i in (0,1)]+[1+v]
    else:
        ax,ay=next(base[i] for i in subset if base[i][0]!=R[0])
        u0=(R[1]-ay)*pow(R[0]-ax,-1,p)%p;u=u0+v
        # Conic coefficient order: Z²,YZ,Y²,XZ,XY,X².
        c0,cy,cyy,cx,cxy,cxx=poly
        L=(cx+cxy*ay+2*cxx*ax)+(cy+2*cyy*ay+cxy*ax)*u
        Q=cxx+cxy*u+cyy*u*u
        XYZ=[ax*Q-L,ay*Q-u*L,Q]
    X,Y,Z=XYZ
    F=cubic(X,Y,Z,data['a'],data['b']);G=second(X,Y,Z,data['G'])
    common=F.gcd(G);f=F//common;g=G//common
    assert f.degree()<=1 and g.degree()<=1
    assert int(f[0])%p==0 # v=0 is R on the t=0 fibre.
    numerator=nmod_poly([-int(f[0]),-int(g[0])],p)
    denominator=nmod_poly([int(f[1]),int(g[1])],p)
    result=[]
    for coord in XYZ:
        result.append(sum((int(coord[j])*numerator**j*denominator**(d-j) for j in range(d+1)),nmod_poly([],p)))
    z0=int(result[2][0]);assert z0%p
    scale=pow(z0,-1,p)
    rows=[[int(q[i])*scale%p for i in range(d+1)] for q in result]
    # Same primitive chart as the Groebner experiment.
    if d==1:res=rows[1][1]-R[1]*rows[2][1]
    else:
        from sympy import Matrix
        y0,y1,y2=rows[1];z0,z1,z2=rows[2]
        res=Matrix([[y2,y1,y0,0],[0,y2,y1,y0],[z2,z1,z0,0],[0,z2,z1,z0]]).det()
    if int(res)%p==0:return None
    return rows


def prepare(data):
    start=time.perf_counter();base=recover_base(data);split=time.perf_counter();classes=[]
    for subset in combinations(range(9),2 if data['d']==1 else 5):
        ns=nullspace([monomials((*base[i],1),data['d']) for i in subset],data['p'])
        assert len(ns)==1
        if ns[0][-1]%data['p']:classes.append((subset,ns[0]))
    return base,classes,dict(base_recovery_seconds=split-start,class_precomputation_seconds=time.perf_counter()-split)


def search(data,base,classes):
    start=time.perf_counter()
    for subset,poly in classes:
        if polynomial_value(poly,data['R'],data['p']):continue
        xyz=parameterize(data,base,subset,poly)
        if xyz is not None:return dict(status='sat',xyz=xyz,wall_seconds=time.perf_counter()-start)
    return dict(status='unsat',wall_seconds=time.perf_counter()-start)


def run():
    source=json.loads((ROOT/'blind-results.json').read_text());rows=[];prepared={}
    for row in source['rows']:
        if row['method']!='raw':continue
        surface=next(s for s in source['surfaces'] if s['p']==row['p'])
        data={k:surface[k] for k in ('p','a','b','G')};data.update(R=row['R'],d=row['d'])
        key=(row['p'],row['d'])
        if key not in prepared:prepared[key]=prepare(data)
        base,classes,setup=prepared[key];out=search(data,base,classes)
        assert (out['status']=='sat')==row['oracle_bounded_degree_exists']
        E=EC(surface['p'],surface['a'],surface['b']);P=tuple(surface['P']);Q=E.mul(row['k'],P)
        if out['status']=='sat':out.update(validate(data,out,[tuple(q) for q in surface['points']],surface['scalars'],E,P,Q))
        rows.append(dict(p=row['p'],d=row['d'],mode=row['mode'],trial=row['trial'],solver=out,
            setup=setup,classes=len(classes),rho=row['rho'],
            cold_seconds=sum(setup.values())+out['wall_seconds']+out.get('verification_seconds',0)))
    out=dict(evidence_class='finite-control',scope='Blind classical line/conic construction on the identical E3 cases.',
        inputs='p,a,b,G,R,d; base points recovered by a degree-at-most-9 resultant, never supplied.',
        novelty='None claimed. Recovers known split-pencil geometry; not a general section-solving algorithm.',
        rows=rows,limitations=['Only fixed degrees 1 and 2. Enumerating classes is a bounded-height search and does not remove the coverage cost.',
            'Precomputation may be shared per surface and degree; cold cost records it once per target for comparison.',
            'Known specialization logs are used only by the parent to validate output maps and recovered logs.'])
    (ROOT/'geometry-results.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':run()
