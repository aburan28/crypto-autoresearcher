from core import *
import multiprocessing as mp
from itertools import product
from sympy import symbols, Poly, resultant, expand
from fpylll import IntegerMatrix, LLL
import z3

x,y,z,u,v=symbols('x y z u v')


def S3(X,Y,Z,a,b):
    return (X-Y)**2*Z**2-2*((X+Y)*(X*Y+a)+2*b)*Z+(X*Y-a)**2-4*b*(X+Y)


def a1():
    rows=[]
    for a,b in ((2,3),(1,1),(5,7)):
        start=time.perf_counter()
        f3=Poly(S3(x,y,z,a,b),x,y,z)
        f4=Poly(resultant(S3(x,y,z,a,b),S3(u,v,z,a,b),z),x,y,u,v)
        assert max(f3.degree(q) for q in (x,y,z))==2
        assert max(f4.degree(q) for q in (x,y,u,v))==4
        build=time.perf_counter()-start
        for bits in (13,17,23):
            p=int(prevprime(2**bits));g=rng('SNFS-A1',f'{a}:{b}:{bits}')
            q=int(nextprime(g.randrange(2**(bits-1),2**bits-100)))
            for name,f in [('S3',f3),('S4',f4)]:
                supports=[]
                for prime in (p,q):supports.append({m for m,c in f.terms() if int(c)%prime})
                rows.append(dict(a=a,b=b,bits=bits,pseudo_Mersenne_prime=p,random_prime=q,
                    polynomial=name,integer_monomials=len(f.terms()),
                    support_symmetric_difference=len(supports[0]^supports[1]),
                    per_variable_degrees=[f.degree(t) for t in f.gens],symbolic_build_seconds=build))
    write_result('SNFS-A1','Integer S3/S4 support reduction for three fixed curves and matched prime bit sizes',rows,
        ['No universal Z[a,b] support claim: coefficient specialization/reduction exceptions remain possible.','No full decomposition-throughput ratio or modular-reduction time share measured.'])


def univariate_control():
    out=[]
    for p in (65521,1048573,16777213):
        for r in (3,7,11):
            X=16;m=2;t=2;f=Poly((x-r)*(x-(p//3)),x)
            # Reduce coefficients but retain a monic integer polynomial.
            f=Poly(sum((int(c)%p)*x**mon[0] for mon,c in f.terms()),x)
            pol=[]
            for k in range(m):
                for j in range(2):pol.append(Poly(x**j*f.as_expr()**k*p**(m-k),x))
            for j in range(t):pol.append(Poly(x**j*f.as_expr()**m,x))
            dim=2*m+t;M=IntegerMatrix(dim,dim)
            for i,g in enumerate(pol):
                for (j,),c in g.terms():M[i,j]=int(c)*X**j
            LLL.reduction(M)
            recovered=set()
            for i in range(dim):
                gp=Poly(sum((int(M[i,j])//X**j)*x**j for j in range(dim)),x)
                for rr in gp.ground_roots():
                    if rr.q==1 and 0<=int(rr)<X and f.eval(rr)%p==0:recovered.add(int(rr))
            assert r in recovered
            out.append(dict(p=p,root=r,recovered=True,dimension=dim))
    return out


def lattice_worker(queue,p,a,b,Rx,X,plant):
    try:
        start=time.perf_counter();f=Poly(S3(x,y,Rx,a,b),x,y);allroots=set();diags=[]
        for m,t in ((1,1),(2,0)):
            D=2*m+t;mons=[(i,j) for i in range(D+1) for j in range(D+1)]
            shifts=[]
            for i,j in mons:
                k=min(i//2,j//2,m)
                shifts.append(Poly(x**(i-2*k)*y**(j-2*k)*f.as_expr()**k*p**(m-k),x,y))
            M=IntegerMatrix(len(mons),len(mons));positions={mon:j for j,mon in enumerate(mons)}
            for i,g in enumerate(shifts):
                assert int(g.eval({x:plant[0],y:plant[1]}))%p**m==0
                for mon,c in g.terms():M[i,positions[mon]]=int(c)*X**sum(mon)
            LLL.reduction(M)
            short=[]
            for i in range(len(mons)):
                row=[int(M[i,j]) for j in range(len(mons))]
                certified=len(mons)*sum(c*c for c in row)<p**(2*m)
                if not certified:continue
                g=Poly(sum((c//X**sum(mon))*x**mon[0]*y**mon[1] for c,mon in zip(row,mons)),x,y)
                assert all(c%X**sum(mon)==0 for c,mon in zip(row,mons))
                assert g.eval({x:plant[0],y:plant[1]})==0
                if not g.is_zero:short.append(g)
            for first,second in combinations(short[:6],2):
                rr=resultant(first.as_expr(),second.as_expr(),y)
                if rr==0:continue
                rr=Poly(rr,x)
                for rx in rr.ground_roots():
                    if rx.q!=1 or not 0<=int(rx)<X:continue
                    gy=Poly(first.as_expr().subs(x,rx),y)
                    hy=Poly(second.as_expr().subs(x,rx),y)
                    common=gy.gcd(hy)
                    for ry in common.ground_roots():
                        if ry.q==1 and 0<=int(ry)<X and int(f.eval({x:rx,y:ry}))%p==0:
                            allroots.add((int(rx),int(ry)))
            diags.append(dict(m=m,dimension=len(mons),certified_short_polynomials=len(short)))
        queue.put(dict(status='completed',recovered_plant=(plant in allroots or plant[::-1] in allroots),
            recovered_roots=sorted(allroots),lattices=diags,wall_seconds=time.perf_counter()-start))
    except Exception as exc:queue.put(dict(status='error',error=repr(exc)))


def a2():
    controls=univariate_control();rows=[];ctx=mp.get_context('fork')
    for bits in (12,16,20):
        p=int(prevprime(2**bits));E=EC(p,2,3)
        for beta in (.20,.35,.50):
            X=int(p**beta);FB=[P for P in E.points if P[0]<X]
            g=rng('SNFS-A2',f'{bits}:{beta}')
            for trial in range(2):
                while True:
                    P,Q=g.choice(FB),g.choice(FB);R=E.add(P,Q)
                    if R is not None:break
                plant=(P[0],Q[0]);queue=ctx.Queue()
                worker=ctx.Process(target=lattice_worker,args=(queue,p,2,3,R[0],X,plant))
                begin=time.perf_counter();worker.start();worker.join(5)
                if worker.is_alive():
                    worker.terminate();worker.join();result=dict(status='timeout',wall_seconds=time.perf_counter()-begin)
                else:
                    result=queue.get(timeout=1)
                result['completed_wall_seconds_with_worker_launch']=time.perf_counter()-begin
                rows.append(dict(p=p,bits=bits,beta=beta,X=X,trial=trial,plant=plant,**result))
    write_result('SNFS-A2','Small S3 bivariate modular-lattice prototype with exact short-vector checks and root extraction',rows,
        ['Only two planted cases per cell; no 50%-recovery threshold or asymptotic exponent can be estimated.','Univariate monic Coppersmith controls passed; the required independent bivariate linear-control protocol is not implemented, so these multivariate numbers remain diagnostic.','No BKZ-20, dimension-200 sweep or S4 lattice experiment.','Timeouts are censored, not failures.'],
        dict(univariate_controls=controls,per_case_wall_cap_seconds=5))


def pair_enum(E,FB,R):
    allowed=set(FB)
    for P in FB:
        Q=E.add(R,E.neg(P))
        if Q in allowed:return P,Q
    return None


def sat_pair(E,R,X,kind,order,cap=1.):
    start=time.perf_counter();p=E.p;w=p.bit_length();x=z3.BitVec('sx',w);y=z3.BitVec('sy',w)
    def c(n):return z3.BitVecVal(n%p,w)
    def mul(a,b):return z3.Extract(w-1,0,z3.URem(z3.ZeroExt(w,a)*z3.ZeroExt(w,b),z3.BitVecVal(p,2*w)))
    def plus(a,b):return z3.Extract(w-1,0,z3.URem(z3.ZeroExt(1,a)+z3.ZeroExt(1,b),z3.BitVecVal(p,w+1)))
    def minus(a,b):return z3.Extract(w-1,0,z3.URem(z3.ZeroExt(1,a)+z3.BitVecVal(p,w+1)-z3.ZeroExt(1,b),z3.BitVecVal(p,w+1)))
    xy=mul(x,y);s=plus(x,y)
    expr=plus(minus(mul(mul(minus(x,y),minus(x,y)),c(R[0]**2)),
        mul(c(2*R[0]),plus(mul(s,plus(xy,c(E.a))),c(2*E.b)))),
        minus(mul(minus(xy,c(E.a)),minus(xy,c(E.a))),mul(c(4*E.b),s)))
    solver=z3.SolverFor('QF_BV');solver.add(z3.ULT(x,c(p-1)) | (x==c(p-1)))
    solver.add(z3.ULT(y,c(p-1)) | (y==c(p-1)),expr==c(0))
    if kind=='interval':solver.add(z3.ULT(x,c(X)),z3.ULT(y,c(X)))
    else:
        for a0 in (x,y):
            t=a0
            for _ in range(order.bit_length()-1):t=mul(t,t)
            solver.add(t==c(1))
    encoding=time.perf_counter()-start;rejected=0
    while time.perf_counter()-start<cap:
        solver.set(timeout=max(1,int((cap-(time.perf_counter()-start))*1000)))
        status=solver.check()
        if status!=z3.sat:
            return dict(status=str(status),encoding_seconds=encoding,rejected_models=rejected,
                        wall_seconds=time.perf_counter()-start)
        model=solver.model();xx=model[x].as_long();yy=model[y].as_long()
        for P in E.xpoints(xx):
            for Q in E.xpoints(yy):
                if E.add(P,Q)==R:
                    return dict(status='verified-sat',encoding_seconds=encoding,rejected_models=rejected,
                                wall_seconds=time.perf_counter()-start)
        solver.add(z3.Or(x!=c(xx),y!=c(yy)));rejected+=1
    return dict(status='unknown',encoding_seconds=encoding,rejected_models=rejected,
                wall_seconds=time.perf_counter()-start)


def a3():
    rows=[]
    families=[('interval',p,None) for p in (251,257,1019,1021,4091,4093)]
    families += [('subgroup',p,order) for p,order in ((257,16),(1153,32),(4289,64))]
    for kind,p,order in families:
        table_start=time.perf_counter();E=EC(p,2,3)
        point_table_seconds=time.perf_counter()-table_start
        X=math.isqrt(p);gen=rng('SNFS-A3',f'{kind}:{p}')
        setup=time.perf_counter()
        FB=[P for P in E.points if (P[0]<X if kind=='interval' else pow(P[0],order,p)==1)]
        setup=time.perf_counter()-setup
        for mode in ('planted','fresh'):
            for trial in range(3):
                if mode=='planted':
                    while True:
                        R=E.add(gen.choice(FB),gen.choice(FB))
                        if R is not None:break
                else:R=gen.choice(E.points)
                begin=time.perf_counter();baseline=pair_enum(E,FB,R)
                if baseline is not None:assert E.add(*baseline)==R
                enumtime=time.perf_counter()-begin
                sat=sat_pair(E,R,X,kind,order)
                if sat['status']=='verified-sat':assert baseline is not None
                if sat['status']=='unsat':assert baseline is None
                rows.append(dict(p=p,kind=kind,subgroup_order=order,X=X,target_type=mode,trial=trial,
                    factor_base_points=len(FB),factor_base_build_seconds=setup,
                    curve_point_table_seconds=point_table_seconds,
                    enumeration_wall_seconds=enumtime,enumeration_has_relation=baseline is not None,
                    enumeration_cold_total_seconds=point_table_seconds+setup+enumtime,
                    SAT_cold_total_seconds=point_table_seconds+setup+sat['wall_seconds'],
                    SAT=sat))
    write_result('SNFS-A3','Completed two-point decomposition: enumeration versus bit-vector SAT, interval and compositional subgroup bases',rows,
        ['SAT uses Z3 bit-vector arithmetic, not CryptoMiniSat/WDSat.','Small m=2 pilot only; no m=3, F4/F5 or completed relation/matrix index-calculus campaign.','No solver exponent fit: range is small and timeout censoring is material.','Factor-base setup and target solving are recorded separately; total cost must include both.'])


def a4():
    rows=[]
    for n in (6,10,12,15):
        p=int(prevprime(2**n));c=2**n-p;E=EC(p,2,3)
        for d in (2,3,5):
            if n%d:continue
            k=n//d;alpha=pow(2,k,p);assert (pow(alpha,d,p)-c)%p==0
            X=2**(n-k);D=[P for P in E.points if P[0]<X];allowed=set(D)
            gen=rng('SNFS-A4',f'{n}:{d}');N=10000;hits=0
            for _ in range(N):hits+=E.add(gen.choice(D),gen.choice(D)) in allowed
            null=[]
            for trial in range(8):
                S=gen.sample(E.points,len(D));ss=set(S)
                null.append(sum(E.add(gen.choice(S),gen.choice(S)) in ss for _ in range(N))/N)
            rows.append(dict(n=n,d=d,k=k,p=p,c=c,ring_map_verified=True,
                x_bound=X,base_size=len(D),curve_order=E.N,sampled_pairs=N,
                observed_closure=hits/N,uniform_group_reference=len(D)/E.N,
                random_subset_closure=null))
    write_result('SNFS-A4','Valid integral digit-ring maps and closure measurements with matched random-subset controls',rows,
        ['The original n,d grid has no valid pairs; this is an explicitly corrected small grid.','Digit-ring lifting/factorization of S3 and a matched random-prime closure experiment remain unrun.','Finite closure deviations are not evidence of an algebraically closed factor base.'])


if __name__=='__main__':
    for fn in (a1,a2,a3,a4):fn()
