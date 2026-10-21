"""Blind coefficient solving on cubic pencils, synthetic known-answer fibres.

Workers receive only a surface, a target point and the degree bound. They
receive neither the base points nor MW generators nor the planted answer.
Fixed-degree Res(Y,Z) != 0 excludes common-factor and lower-degree maps.
This chart omits section images passing through [1:0:0].
"""
from pathlib import Path
import sys, json, time, multiprocessing as mp, resource, traceback
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'snfs-ecdlp-experiments'
sys.path.insert(0,str(PREV))
from core import prime_order_curve, good_pencil, rng, nullspace, monomials, combinations
from surface_pilots import coords, norm, rho
import sympy as sp
from statistics import median


def cubic(X,Y,Z,a,b):return Y*Y*Z-X**3-a*X*Z*Z-b*Z**3


def second(X,Y,Z,G):
    return sum(c*m for c,m in zip(G,monomials((X,Y,Z),3)))


def coefficient_system(data,method):
    p,a,b,G,R,d=(data[k] for k in ('p','a','b','G','R','d'))
    t=sp.Symbol('t');xx=sp.symbols(f'x1:{d+1}');yy=sp.symbols(f'y1:{d+1}');zz=sp.symbols(f'z1:{d+1}')
    X=R[0]+sum(xx[i]*t**(i+1) for i in range(d))
    Y=R[1]+sum(yy[i]*t**(i+1) for i in range(d))
    Z=1+sum(zz[i]*t**(i+1) for i in range(d))
    allv=xx+yy+zz
    coeff=sp.Poly(sp.expand(cubic(X,Y,Z,a,b)+t*second(X,Y,Z,G)),t)
    equations=[coeff.nth(i) for i in range(1,3*d+2)]
    # Compute before specialization: resultant includes common roots at infinity.
    guard=sp.resultant(Y,Z,t)
    sub={}
    if method=='jet':
        inv=pow(2*R[1],-1,p)
        for k in range(d):
            ex=sp.Poly(equations[k].subs(sub),*allv,modulus=p).as_expr()
            rest=sp.expand(ex-2*R[1]*yy[k])
            sub[yy[k]]=sp.Poly(-inv*rest,*allv,modulus=p).as_expr()
            assert yy[k] not in sub[yy[k]].free_symbols
        variables=xx+zz
        equations=[sp.Poly(e.subs(sub),*variables,modulus=p).as_expr() for e in equations[d:]]
        guard=sp.Poly(guard.subs(sub),*variables,modulus=p).as_expr()
    else:variables=allv
    w=sp.Symbol('w')
    equations.append(w*guard-1)
    return (w,)+variables,equations,(X,Y,Z),sub,allv,t


def field_solution(expressions,variables,p,assignment=None):
    assignment={} if assignment is None else assignment
    remaining=[v for v in variables if v not in assignment]
    reduced=[]
    for e in expressions:
        e=sp.expand(e.subs(assignment))
        if not e.free_symbols:
            if int(e)%p:return None
        else:reduced.append(e)
    if not remaining:return assignment
    candidates=[e for e in reduced if len(e.free_symbols)==1]
    if not candidates:return None
    poly=min(candidates,key=lambda e:sp.degree(e,next(iter(e.free_symbols))))
    v=next(iter(poly.free_symbols))
    for root in sp.Poly(poly,v,modulus=p).ground_roots():
        out=field_solution(reduced,variables,p,{**assignment,v:int(root)%p})
        if out is not None:return out
    return None


def worker(data,method,conn):
    try:
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(6,6))
        started=time.perf_counter()
        variables,eq,XYZ,sub,allv,t=coefficient_system(data,method)
        built=time.perf_counter()
        gb=sp.groebner(eq,*variables,modulus=data['p'],order='grevlex',method='f5b')
        gbtime=time.perf_counter()
        stats=dict(variables=len(variables),equations=len(eq),basis_size=len(gb.polys),
            max_basis_degree=max((g.total_degree() for g in gb.polys),default=0),
            build_seconds=built-started,groebner_seconds=gbtime-built)
        if len(gb.polys)==1 and gb.polys[0].as_expr()==1:
            conn.send(dict(status='unsat',**stats));return
        if not gb.is_zero_dimensional:
            conn.send(dict(status='positive-dimensional',**stats));return
        lex=gb.fglm('lex')
        sol=field_solution([g.as_expr() for g in lex.polys],variables,data['p'])
        if sol is None:conn.send(dict(status='no-Fp-root',**stats));return
        sol.update({v:int(e.subs(sol))%data['p'] for v,e in sub.items()})
        xyz=[[int(sp.Poly(e.subs(sol),t).nth(i))%data['p'] for i in range(data['d']+1)] for e in XYZ]
        conn.send(dict(status='sat',xyz=xyz,**stats))
    except BaseException as e:conn.send(dict(status='error',error=str(e),traceback=traceback.format_exc()))
    finally:conn.close()


def solve(data,method,cap=4.0):
    begin=time.perf_counter();parent,child=mp.Pipe(False)
    process=mp.get_context('fork').Process(target=worker,args=(data,method,child))
    process.start();child.close()
    if parent.poll(cap):
        try:result=parent.recv()
        except EOFError:result=dict(status='worker-exit',exitcode=process.exitcode)
    else:result=dict(status='timeout',wall_cap_seconds=cap)
    if process.is_alive():process.terminate()
    process.join();parent.close()
    result['wall_seconds']=time.perf_counter()-begin
    return result


def validate(data,answer,points,scalars,E,P,Q):
    start=time.perf_counter();p=data['p'];d=data['d'];t=sp.Symbol('t')
    XYZ=[sum(c*t**i for i,c in enumerate(row)) for row in answer['xyz']]
    X,Y,Z=XYZ
    assert tuple(row[0] for row in answer['xyz'])==(*data['R'],1)
    identity=sp.Poly(sp.expand(cubic(X,Y,Z,E.a,E.b)+t*second(X,Y,Z,data['G'])),t,modulus=p)
    assert identity.is_zero
    # Fixed-size Sylvester determinant, also after specialization at infinity.
    if d==1:res=answer['xyz'][1][1]-data['R'][1]*answer['xyz'][2][1]
    else:
        y0,y1,y2=answer['xyz'][1];z0,z1,z2=answer['xyz'][2]
        res=sp.det(sp.Matrix([[y2,y1,y0,0],[0,y2,y1,y0],[z2,z1,z0,0],[0,z2,z1,z0]]))
    assert int(res)%p
    mi=[]
    for x,y in points:
        A=sp.Poly(X-x*Z,t,modulus=p);B=sp.Poly(Y-y*Z,t,modulus=p)
        assert not (A.is_zero and B.is_zero)
        m=int(sp.gcd(A,B).degree()+d-max(A.degree(),B.degree()))
        mi.append(m)
    assert sum(mi)==3*d-1 and sum(m*m for m in mi)==d*d+1
    v=coords(d,mi);assert norm(v)==2+2*mi[8]
    cs=[(scalars[i]-scalars[8])%E.N for i in range(7)]+[(-scalars[0]-scalars[1]-scalars[8])%E.N]
    recovered=sum(x*c for x,c in zip(v,cs))%E.N
    assert E.mul(recovered,P)==Q
    return dict(verified=True,multiplicities=mi,lattice_coordinates=v,recovered_log=recovered,
                verification_seconds=time.perf_counter()-start)


def class_oracle(E,points,d):
    out=[];n=2 if d==1 else 5
    for subset in combinations(range(9),n):
        ns=nullspace([monomials((*points[i],1),d) for i in subset],E.p)
        assert len(ns)==1
        # The last coefficient is X^d. Nonzero excludes image through [1:0:0].
        if ns[0][-1]%E.p:out.append((subset,ns[0]))
    return out


def run():
    start=time.perf_counter();rows=[];surfaces=[]
    log=(ROOT/'blind-progress.jsonl').open('w')
    for p in (101,257,1021):
        E=prime_order_curve(p);P=E.points[0];gen=rng('SNFS-E3',f'round2-blind:{p}')
        points,scalars,G,attempts=good_pencil(E,gen,P)
        surfaces.append(dict(p=p,a=E.a,b=E.b,N=E.N,P=P,points=points,scalars=scalars,G=G,attempts=attempts))
        for d in (1,2):
            classes=class_oracle(E,points,d)
            for mode in ('fresh','planted'):
                for trial in range(2 if mode=='fresh' else 1):
                    for _ in range(1000):
                        if mode=='fresh':k=gen.randrange(1,E.N)
                        else:
                            subset,_=gen.choice(classes)
                            k=(-sum(scalars[i] for i in subset)-scalars[8])%E.N
                        Q=E.mul(k,P);R=E.add(Q,points[8])
                        if R is not None and R not in points and R[1]!=0:break
                    else:raise RuntimeError('Target conditioning exhausted')
                    data=dict(p=p,a=E.a,b=E.b,G=G,R=R,d=d)
                    oracle=any(sum(a*b for a,b in zip(poly,monomials((*R,1),d)))%p==0 for _,poly in classes)
                    if mode=='planted':assert oracle
                    rh=rho(E,P,Q,gen);assert rh['status']=='verified' and rh['k']==k
                    for method in ('raw','jet'):
                        answer=solve(data,method)
                        if answer['status']=='sat':
                            assert oracle
                            answer.update(validate(data,answer,points,scalars,E,P,Q))
                        elif answer['status'] in ('unsat','no-Fp-root'):assert not oracle
                        row=dict(p=p,N=E.N,d=d,mode=mode,trial=trial,k=k,R=R,method=method,
                                 oracle_bounded_degree_exists=oracle,solver=answer,rho=rh)
                        rows.append(row);log.write(json.dumps(row)+'\n');log.flush()
                        print(json.dumps(dict(p=p,d=d,mode=mode,method=method,status=answer['status'],oracle=oracle)),flush=True)
    log.close()
    summary=[]
    for d in (1,2):
        for method in ('raw','jet'):
            cc=[r for r in rows if r['d']==d and r['method']==method]
            status={s:sum(r['solver']['status']==s for r in cc) for s in sorted({r['solver']['status'] for r in cc})}
            sat=[r for r in cc if r['solver']['status']=='sat']
            summary.append(dict(d=d,method=method,cases=len(cc),statuses=status,
                oracle_solvable=sum(r['oracle_bounded_degree_exists'] for r in cc),
                sat_median_full_time_to_rho=(median((r['solver']['wall_seconds']+r['solver']['verification_seconds'])/r['rho']['wall_seconds'] for r in sat) if sat else None)))
    out=dict(provisional_id='SNFS-E3',evidence_class='finite-control',surfaces=surfaces,rows=rows,summary=summary,
        wall_seconds=time.perf_counter()-start,
        scope='Exact degree-1/2 rational maps on split cubic pencils, Res(Y,Z) nonzero chart, prime-order toy fibres.',
        solver_inputs='p,a,b,G,R,d only. No base points, generators, oracle classes or known target log.',
        oracle_scope='Lines through 2 / conics through 5 of all 9 base points, outside projection centre, used only after target sampling and never passed to workers.',
        cost_scope='Solver wall includes child launch, system construction, Groebner, root recovery. Successful answers additionally charged identity, primitive-chart, divisor-class and recovered-log validation. Surface construction, pre-certified generators and sampling excluded for both methods; rho has no surface setup charged, so this is a solver diagnostic, not full attack timing.',
        limitations=['Very low degree; failure or success does not establish complexity at coverage heights.',
            'Targets conditioned to finite, non-base fibre points with nonzero y; exceptional sections need other charts.',
            'One surface per size and only 2 fresh / 1 planted target per degree; timings and success rates are pilots.',
            'Raw and jet use the same F5B implementation; jet substitution increases polynomial degrees.',
            'Groebner basis maximum degree is recorded, not claimed to be degree of regularity.'])
    (ROOT/'blind-results.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':run()
