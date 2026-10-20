from core import *
from sympy import n_order
from scipy.stats import ks_2samp


def b1():
    rows=[]
    for p in (101,127,211):
        start=time.perf_counter();E=prime_order_curve(p);P=E.points[0]
        L=Lift(p,E.a,E.b);section=None;values=[];ok=0
        for dx in range(p):
            Q=L.point(P,dx);s=L.section(Q,E.N)
            if section is None:section=L.affine(s)
            assert L.affine(s)==section and L.t(L.mul(E.N,s))==0
            t=L.t(L.mul(E.N,Q));assert t%p==0
            values.append((t//p)*pow(E.N,-1,p)%p);ok+=1
        assert len(set(values))==p
        gen=rng('SNFS-B1',str(p));hom=0
        for _ in range(60):
            U,V=gen.sample(E.points,2);W=E.add(U,V)
            if W is None:continue
            SU=L.section(L.point(U),E.N);SV=L.section(L.point(V),E.N)
            SW=L.section(L.point(W),E.N)
            assert L.affine(L.add(SU,SV))==L.affine(SW);hom+=1
        rows.append(dict(p=p,a=E.a,b=E.b,N=E.N,precision_power=2,
            lift_independence_checks=ok,homomorphism_checks=hom,
            original_statistic_nonzero_count=0,rescaled_statistic_distinct_values=len(set(values)),
            wall_seconds=time.perf_counter()-start))
    write_result('SNFS-B1','Torsion section and lift-independence modulo p^2; original statistic is identically zero',rows,
        ['No ramified extensions or higher precision tested.','Rescaled uniformity is an exhaustive fixed-point/fixed-curve-lift calculation, not a general mutual-information estimate.'])


def b2():
    rows=[]
    for p,J,D in ((5,-96**3,-19),(11,-960**3,-43),(17,-5280**3,-67),(41,-640320**3,-163)):
        E=None
        for a in range(1,p):
            for b in range(1,p):
                den=(4*a**3+27*b*b)%p
                if not den or 1728*4*a**3*pow(den,-1,p)%p!=J%p:continue
                C=EC(p,a,b)
                if C.N==p:E=C;break
            if E:break
        assert E is not None
        P=E.points[0];gen=rng('SNFS-B2',str(p));success=degenerate=0
        begin=time.perf_counter()
        for _ in range(300):
            da,db=gen.randrange(p),gen.randrange(p);k=gen.randrange(1,p);Q=E.mul(k,P)
            L=Lift(p,E.a+p*da,E.b+p*db)
            u=L.t(L.mul(p,L.point(P)))//p%p
            v=L.t(L.mul(p,L.point(Q)))//p%p
            if u==0:
                assert v==0;degenerate+=1
            else:
                assert v*pow(u,-1,p)%p==k;success+=1
        # Class-number-one H_D=X-J gives an exact CM j over Z.
        lifts=[]
        for db in range(p):
            aa=E.a;bb=E.b+p*db;m=p*p;den=(4*aa**3+27*bb*bb)%m
            if 1728*4*aa**3*pow(den,-1,m)%m==J%m:lifts.append(bb)
        assert len(lifts)==1
        L=Lift(p,E.a,lifts[0]);u=L.t(L.mul(p,L.point(P)))//p%p
        assert u==0
        rows.append(dict(p=p,a=E.a,b=E.b,CM_discriminant=D,CM_j=J,
            trials=300,random_lift_successes=success,random_lift_degeneracies=degenerate,
            canonical_CM_lift_statistic=u,precision_power=2,
            wall_seconds=time.perf_counter()-begin))
    write_result('SNFS-B2','Known-answer Smart controls on four anomalous class-number-one CM curves modulo p^2',rows,
        ['No Hilbert class polynomial computation beyond four explicit degree-one polynomials.','Canonical-lift degeneracy was checked modulo p^2 only; no higher-precision implementation.'])


def miller(E,P,Q,n):
    p=E.p
    def line(A,B,Q):
        if A is None or B is None:return 1
        x,y=A;u,v=B;qx,qy=Q
        if x==u and (y+v)%p==0:return (qx-x)%p
        s=((3*x*x+E.a)*pow(2*y,-1,p) if A==B else (v-y)*pow(u-x,-1,p))%p
        C=E.add(A,B);num=(qy-y-s*(qx-x))%p
        den=1 if C is None else (qx-C[0])%p
        if not num or not den:raise ZeroDivisionError
        return num*pow(den,-1,p)%p
    R=P;f=1
    for bit in bin(n)[3:]:
        f=f*f*line(R,R,Q)%p;R=E.add(R,R)
        if bit=='1':f=f*line(R,P,Q)%p;R=E.add(R,P)
    assert R is None
    return pow(f,(p-1)//n,p)


def b3():
    rows=[]
    for p in (31,61,101,211):
        found=None
        for a in range(1,12):
            for b in range(1,12):
                if not (4*a**3+27*b*b)%p:continue
                E=EC(p,a,b)
                for ell in factorint(math.gcd(E.N,p-1)):
                    if ell<3:continue
                    P=next((E.mul(E.N//ell,R) for R in E.points
                            if E.mul(E.N//ell,R) is not None),None)
                    if P is None or E.mul(ell,P) is not None:continue
                    vals=[];points=[]
                    for Q in E.points:
                        try:t=miller(E,P,Q,ell)
                        except ZeroDivisionError:continue
                        vals.append(t);points.append(Q)
                    if any(t!=1 for t in vals):found=(E,ell,P,vals,points);break
                if found:break
            if found:break
        assert found
        E,ell,P,vals,points=found;gen=rng('SNFS-B3',str(p));checks=skipped=0
        for _ in range(80):
            U,V=gen.sample(points,2);W=E.add(U,V)
            if W is None:continue
            try:
                lhs=miller(E,P,W,ell);rhs=miller(E,P,U,ell)*miller(E,P,V,ell)%p
            except ZeroDivisionError:skipped+=1;continue
            assert lhs==rhs;checks+=1
        assert all(pow(t,ell,p)==1 for t in vals)
        rows.append(dict(p=p,a=E.a,b=E.b,N=E.N,ell=ell,
            evaluated_arguments=len(vals),nonidentity_pairings=sum(t!=1 for t in vals),
            homomorphism_checks=checks,support_poles_skipped=skipped))
    write_result('SNFS-B3','Reduced Tate-pairing positive controls at embedding degree one',rows,
        ['Generalized-Jacobian divisor/function arithmetic was not implemented, so no independent connecting-map/Miller agreement claim.','Extension-field k=2,3 tests remain unrun.'])


def b4():
    rows=[];dist={'pseudo-Mersenne':[],'random':[]}
    for bits in (8,10,12):
        special=int(prevprime(2**bits));gen=rng('SNFS-B4',str(bits))
        randomp=int(nextprime(gen.randrange(2**(bits-1),2**bits-20)))
        for kind,p in [('pseudo-Mersenne',special),('random',randomp)]:
            for trial in range(24):
                while True:
                    a,b=gen.randrange(p),gen.randrange(p)
                    if (4*a**3+27*b*b)%p:break
                E=EC(p,a,b);ell=max(factorint(E.N))
                if ell==p:
                    rows.append(dict(p=p,bits=bits,prime_type=kind,N=E.N,ell=ell,status='anomalous-excluded'));continue
                k=int(n_order(p,ell));assert pow(p,k,ell)==1
                normalized=k/(ell-1);dist[kind].append(normalized)
                rows.append(dict(p=p,bits=bits,prime_type=kind,N=E.N,ell=ell,
                    embedding_degree=k,normalized_order=normalized))
    ks=ks_2samp(dist['pseudo-Mersenne'],dist['random'])
    write_result('SNFS-B4','Small-field embedding-order distribution pilot with exact orders',rows,
        ['Small samples do not establish equality of distributions at cryptographic sizes.','CADO-NFS polynomial selection and Murphy-E comparisons were not run; no sieving was performed.','Curve25519 public-parameter order computation was not attempted.'],
        dict(KS_statistic=float(ks.statistic),KS_pvalue=float(ks.pvalue),no_sieving=True))


def b5():
    rows=[]
    for p in (5,7,11):
        for degree in (1,2,3,4):
            for ell in (2,3,5,7,11,13):
                torus=p**degree-1;unipotent=p
                # |C_M / ell C_M| = gcd(M,ell), directly enumerated.
                cosets=len({(ell*x)%torus for x in range(torus)})
                quotient=torus//cosets
                assert quotient==math.gcd(torus,ell)
                rows.append(dict(p=p,residue_degree=degree,ell=ell,torus_order=torus,
                    torus_extension_quotient_size=quotient,
                    unipotent_extension_quotient_size=math.gcd(unipotent,ell)))
    write_result('SNFS-B5','Finite cyclic-kernel Ext quotient sanity table',rows,
        ['Not an enumeration of generalized-Jacobian moduli or a computational classification of all transfers.','Receipt covers only the finite kernel divisibility calculation.'])


def b6():
    rows=[]
    for p in (257,65537):
        E=EC(p,2,3)
        for s in range(1,min(9,int(math.log2(p-1)))):
            order=2**s
            if (p-1)%order:continue
            xs=[x for x in range(1,p) if pow(x,order,p)==1]
            assert len(xs)==order
            FB=[P for P in E.points if P[0] in set(xs)]
            rows.append(dict(p=p,composition_depth=s,polynomial_degree=order,
                auxiliary_quadratic_equations=s,root_count=len(xs),factor_base_points=len(FB),
                factor_base_fraction=len(FB)/E.N))
    write_result('SNFS-B6','Explicit zero-dimensional factor bases described by repeated squaring',rows,
        ['Demonstrates compact equations for small algebraic bases; it does not demonstrate cheap point decomposition.','Does not contradict a correctly scoped bounded-degree positive-dimensional Hasse-Weil statement.'])


def fp2_count(p,a,b):
    d=next(q for q in range(2,p) if pow(q,(p-1)//2,p)==p-1)
    def add(x,y):return ((x[0]+y[0])%p,(x[1]+y[1])%p)
    def mul(x,y):return ((x[0]*y[0]+d*x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0])%p)
    vals=[(x,y) for x in range(p) for y in range(p)];sq={}
    for x in vals:
        z=mul(x,x);sq[z]=sq.get(z,0)+1
    count=2 # Even degree with square leading coefficient: two points at infinity.
    for x in vals:
        x2=mul(x,x);x6=mul(mul(x2,x2),x2)
        rhs=add(add(x6,(a*x2[0]%p,a*x2[1]%p)),(b%p,0))
        count+=sq.get(rhs,0)
    return count


def b7():
    rows=[]
    for p in (11,13,17,19,23,29):
        a,b=2,3
        if not (4*a**3+27*b*b)%p:continue
        E=EC(p,a,b);roots=E.roots
        C1=2+sum(len(roots.get((x**6+a*x*x+b)%p,[])) for x in range(p))
        C2=fp2_count(p,a,b)
        tr=p+1-C1;a2=(C2-p*p-1+tr*tr)//2
        J=1-tr+a2-p*tr+p*p
        other=1+sum(len(roots.get((b*u**3+a*u*u+1)%p,[])) for u in range(p))
        assert J==E.N*other
        mapped=set()
        for x in range(p):
            for y in roots.get((x**6+a*x*x+b)%p,[]):
                Q=(x*x%p,y);assert E.valid(Q);mapped.add(Q)
        rows.append(dict(p=p,cover='y^2=x^6+2x^2+3 -> (u,v)=(x^2,y)',
            genus=2,C_Fp=C1,C_Fp2=C2,Jacobian_order=J,E_order=E.N,
            complementary_E_order=other,split_order_identity=True,affine_image_points=len(mapped)))
    write_result('SNFS-B7','Genus-two split-cover point-count and isogeny-order control',rows,
        ['No Jacobian index calculus or rho comparison executed; no complexity exponent inferred.','Genus-three covers and descent-direction implementation remain unrun.'])


if __name__=='__main__':
    for fn in (b1,b2,b3,b4,b5,b6,b7):fn()
