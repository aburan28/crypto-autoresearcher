from core import *
from itertools import product
from sympy import Matrix

G=Matrix(8,8,lambda i,j:2 if i==j else 1)
for i in range(7):G[i,7]=G[7,i]=0 if i<2 else 1
assert G.det()==1
GI=G.inv();GM=[list(map(int,G.row(i))) for i in range(8)]


def norm(v):return sum(v[i]*GM[i][j]*v[j] for i in range(8) for j in range(8))


def coords(d,mi):
    pair=Matrix([1+mi[8]-mi[i] for i in range(7)]+[1+mi[8]-d+mi[0]+mi[1]])
    v=GI*pair
    assert all(t.q==1 for t in v)
    return tuple(map(int,v))


def lattice_vectors(H):
    L,D=G.LDLdecomposition(hermitian=False);U=L.T
    uf=[[float(U[i,j]) for j in range(8)] for i in range(8)];dd=[float(D[i,i]) for i in range(8)]
    v=[0]*8;out=[]
    def rec(i,remaining):
        if i<0:
            q=norm(v)
            if q<=H:out.append((tuple(v),q))
            return
        center=-sum(uf[i][j]*v[j] for j in range(i+1,8))
        bound=math.sqrt(max(0,remaining)/dd[i])
        for n in range(math.ceil(center-bound-1e-8),math.floor(center+bound+1e-8)+1):
            rem=remaining-dd[i]*(n-center)**2
            if rem>=-1e-7:v[i]=n;rec(i-1,max(0,rem))
    rec(7,H)
    return out


def small_sections(E,points):
    start=time.perf_counter();sections=[]
    for i in range(8):
        mi=[0]*9;mi[i]=-1;v=coords(0,mi);assert norm(v)==2
        sections.append(dict(type='exceptional',point=points[i],v=v))
    for degree,number in ((1,2),(2,5)):
        for subset in combinations(range(8),number):
            ns=nullspace([monomials((*points[i],1),degree) for i in subset],E.p)
            assert len(ns)==1
            mi=[int(i in subset) for i in range(9)];v=coords(degree,mi);assert norm(v)==2
            sections.append(dict(type='plane-curve',degree=degree,polynomial=ns[0],v=v))
    return sections,time.perf_counter()-start


def geometry_target(E,points,sections,Q):
    R=E.add(Q,points[8]);rp=(0,1,0) if R is None else (*R,1)
    for s in sections:
        if s['type']=='exceptional':match=R==s['point']
        elif R in points:continue # Polynomial vanishing at a blown-up base point is not sufficient.
        else:match=sum(a*b for a,b in zip(s['polynomial'],monomials(rp,s['degree'])))%E.p==0
        if match:return s['v']
    return None


def halves(E,basis,M):
    start=time.perf_counter();left={};right=[]
    def enum(B):
        out=[(None,())]
        for P in B:
            choices=[(E.mul(c,P),c) for c in range(-M,M+1)];nxt=[]
            for R,v in out:
                for Q,c in choices:nxt.append((E.add(R,Q),v+(c,)))
            out=nxt
        return out
    for R,v in enum(basis[:4]):left.setdefault(R,[]).append(v)
    right=enum(basis[4:])
    return left,right,time.perf_counter()-start


def mitm(E,left,right,Q,H):
    for R,v in right:
        T=E.add(Q,E.neg(R))
        for u in left.get(T,[]):
            candidate=u+v
            if norm(candidate)<=H:return candidate
    return None


def rho(E,P,Q,gen):
    start=time.perf_counter();before=E.ops;N=E.N
    def step(state):
        R,a,b=state;part=0 if R is None else R[0]%3
        if part==0:return E.add(R,P),(a+1)%N,b
        if part==1:return E.add(R,R),2*a%N,2*b%N
        return E.add(R,Q),a,(b+1)%N
    for retry in range(8):
        a,b=gen.randrange(N),gen.randrange(N)
        s=(E.add(E.mul(a,P),E.mul(b,Q)),a,b);f=s
        for _ in range(20*math.isqrt(N)+100):
            s=step(s);f=step(step(f))
            if s[0]!=f[0]:continue
            den=(f[2]-s[2])%N
            if den:
                k=(s[1]-f[1])*pow(den,-1,N)%N
                assert E.mul(k,P)==Q
                return dict(status='verified',k=k,wall_seconds=time.perf_counter()-start,
                            group_operations=E.ops-before,retries=retry)
            break
    return dict(status='retry-cap',wall_seconds=time.perf_counter()-start,group_operations=E.ops-before)


def run():
    start=time.perf_counter();vectors=lattice_vectors(8);enumtime=time.perf_counter()-start
    counts={H:sum(q<=H for v,q in vectors) for H in (2,4,6,8)}
    assert counts=={2:241,4:2401,6:9121,8:26641}
    rows1=[];rows2=[];rows3=[];rows4=[]
    for p in (257,1021,4093,16381):
        E=prime_order_curve(p);P=E.points[0]
        for case in range(2):
            gen=rng('SNFS-E1',f'{p}:{case}');start=time.perf_counter()
            points,scalars,poly,attempts=good_pencil(E,gen,P)
            a9=scalars[8];cs=[(scalars[i]-a9)%E.N for i in range(7)]+[(-scalars[0]-scalars[1]-a9)%E.N]
            basis=[E.mul(c,P) for c in cs];pencilsetup=time.perf_counter()-start
            rows1.append(dict(p=p,a=E.a,b=E.b,N=E.N,case=case,chi=1,
                rational_base_points=points,known_scalars=scalars,pencil_G=poly,
                general_position_attempts=attempts,pencil_build_seconds=pencilsetup,
                rank_from_split_blowup_geometry=8,rank_type='arithmetic and geometric',
                target_included_in_construction=False))
            rows2.append(dict(p=p,case=case,chi=1,rank=8,Gram_determinant=1,
                shortest_squared_norm=2,source='Even positive determinant-one Gram with exhibited norm-two vectors; exact geometric height formula'))
            for H in (2,4,6,8):
                values=[sum(a*b for a,b in zip(v,cs))%E.N for v,q in vectors if q<=H]
                covered=len(set(values))
                rows4.append(dict(p=p,case=case,N=E.N,H=H,lattice_points=len(values),
                    volume_heuristic=math.pi**4/24*H**4,
                    occupied_fibre_points=covered,coverage=covered/E.N,
                    independent_occupancy_reference=1-math.exp(-len(values)/E.N)))
            sections,geomsetup=small_sections(E,points)
            # Verify every low-section's class specialization without a target.
            for s in sections:
                k=sum(a*b for a,b in zip(s['v'],cs))%E.N
                Q=E.mul(k,P)
                v=geometry_target(E,points,sections,Q)
                assert v is not None
                assert E.mul(sum(a*b for a,b in zip(v,cs))%E.N,P)==Q
            tables={}
            for M in (1,2):tables[M]=halves(E,basis,M)
            tg=rng('SNFS-E3',f'{p}:{case}')
            targets=[('fresh',tg.randrange(1,E.N)) for _ in range(20)]
            targets += [('planted-low-section',sum(a*b for a,b in zip(tg.choice(sections)['v'],cs))%E.N) for _ in range(3)]
            for index,(mode,k) in enumerate(targets):
                if k==0:continue
                Q=E.mul(k,P);start=time.perf_counter();v=geometry_target(E,points,sections,Q)
                if v is not None:
                    recovered=sum(a*b for a,b in zip(v,cs))%E.N
                    assert E.mul(recovered,P)==Q and recovered==k
                geotime=time.perf_counter()-start
                geo=dict(success=v is not None,wall_seconds=geotime,precompute_seconds=geomsetup,
                    section_candidates=len(sections),search_height=2,
                    coverage_scope='92 explicit exceptional/line/conic sections, a strict subset of all height-two sections')
                mm={}
                for M in (1,2):
                    left,right,setup=tables[M];start=time.perf_counter();vv=mitm(E,left,right,Q,8)
                    if vv is not None:
                        recovered=sum(a*b for a,b in zip(vv,cs))%E.N
                        assert E.mul(recovered,P)==Q and recovered==k
                    lookup=time.perf_counter()-start
                    mm[str(M)]=dict(success=vv is not None,lookup_seconds=lookup,
                        precompute_seconds=setup,one_target_total_seconds=pencilsetup+setup+lookup,
                        coefficient_box_radius=M,maximum_squared_height=8,
                        scope='Oracle group search with known MW basis; not a blind section solver')
                rh=rho(E,P,Q,rng('SNFS-E3',f'rho:{p}:{case}:{index}'))
                if rh['status']=='verified':assert rh['k']==k
                rows3.append(dict(p=p,case=case,N=E.N,target_type=mode,
                    target_index=index,pencil_build_seconds=pencilsetup,
                    geometry_low_section=geo,oracle_MITM=mm,rho=rh))
    # Direct j-image calculation in the stated nonconstant Ulmer equation.
    jrows=[]
    for p in (257,1021,4093):
        for d in (1,2,4,8):
            image=set();smooth_count=0
            for t in range(p):
                u=pow(t,d,p);den=u*(1-432*u)%p
                if den:smooth_count+=1;image.add(pow(den,-1,p))
            chi=math.ceil(d/6)
            assert len(image)*2*d>=smooth_count
            jrows.append(dict(p=p,d=d,chi_model_bound=chi,smooth_parameters=smooth_count,
                distinct_j=len(image),image_density=len(image)/p,
                original_claimed_image_count_upper_bound=12*chi,
                rank_of_this_Ulmer_family_certified=False))
    write_result('SNFS-E1','Eight prescribed-fibre split rational surfaces, plus explicit nonconstant j-image controls',rows1,
        ['Rank eight follows from checked split cubic-pencil geometry; no random-surface zeta-function rank experiment.','No higher-chi rank-growth construction tested; j-image samples are not conditioned on high rank.'],
        dict(j_image_samples=jrows,Gram_matrix=GM,twist_discriminant_identity='Delta_twist=f^6 Delta; a simple zero at a good target fibre destroys good reduction'))
    write_result('SNFS-E2','Exact height lattice of the constructed split rational surfaces',rows2,
        ['This is a selected E8 family with chi=1, not a universal height theorem for arbitrary surfaces.','No empirical D2 random-lift height comparison or chi=2,3 surface experiment.'])
    write_result('SNFS-E3','Fresh-target low-section interpolation search, bounded-MW oracle MITM, and known-answer rho',rows3,
        ['Geometry search covers 92 known height-two section classes only; it is not a general bounded-height section solver.','MITM is oracle-assisted group search; no blind F4/F5/SAT rational-section coefficient-system solver was executed.','Success on planted low sections does not establish fresh-target coverage.','Precomputation, pencil construction and query costs are reported separately; shared precomputation cannot be silently omitted.','MW-coordinate recovery for these explicit classes is exact from the determinant-one Gram matrix; no kernel-relation collection is required because basis specialization logs are known by construction.'])
    write_result('SNFS-E4','Complete E8 short-vector counts and actual specialization coverage',rows4,
        ['Exact enumeration verified against the first four E8 theta-series counts.','Coverage is measured on eight selected rank-eight surfaces, not extrapolated to rank 100 or 300.','Independent occupancy and volume expressions are reference heuristics, not proofs of uniformity.'],
        dict(E8_exact_counts=counts,enumeration_seconds=enumtime,
            shortest_squared_norm=2,Gram_determinant=1,
            H_256bit_rank8_volume_proxy=(2.0**256/(math.pi**4/24))**.25))


if __name__=='__main__':run()
