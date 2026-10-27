"""Implementation validation body; run through run_validation.py."""
import hashlib,json,platform,sys,time,resource
from pathlib import Path
from flint import fmpz,fmpz_mod_poly_ctx
import flint
from arithmetic import *

BITS=(6,8,10,12)
CHAIN_LENGTH=16
CHUNK=64

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def digest_poly(poly):
    h=hashlib.sha256()
    for coeff in poly.coeffs(): h.update(int(coeff).to_bytes(32,'big'))
    return h.hexdigest()

def product(ctx,values):
    level=[ctx([-x%P,1]) for x in values]
    while len(level)>1:
        level=[level[i]*level[i+1] if i+1<len(level) else level[i]
               for i in range(0,len(level),2)]
    return level[0] if level else ctx([1])

def nonsingular(curve):
    a,b,c=curve
    # Cubic discriminant for a monic cubic.
    return (a*a*b*b-4*b*b*b-4*a*a*a*c-27*c*c+18*a*b*c)%P!=0

def tor_mul(z,w):
    a,b=z;c,d=w
    return ((a*c-b*d)%P,(a*d+b*c)%P)

def tor_pow(z,n):
    acc=(1,0)
    while n:
        if n&1: acc=tor_mul(acc,z)
        z=tor_mul(z,z);n>>=1
    return acc

def tor_seed(seed):
    # (s+i)/(s-i), norm one in F_p[i], since i^2=-1.
    s=int.from_bytes(hashlib.sha256(seed.encode()).digest(),'big')%P
    inv=pow(s*s+1,-1,P)
    return ((s*s-1)*inv%P,2*s*inv%P)

def run(out,inject=None):
    start=time.monotonic(); checks=0
    def require(truth,message):
        nonlocal checks
        checks+=1
        if not truth: raise AssertionError(message)
    require(bool(fmpz(P).is_prime()),'field prime')
    require(bool(fmpz(TARGET_R).is_prime()),'target order prime')
    require(P%4==3 and ((P+1)&-(P+1))==2**96,'field residues')
    require(pow(P-1,(P-1)//2,P)==P-1,'-1 nonsquare')
    require(nonsingular(AUX) and nonsingular(TARGET),'curve nonsingularity')
    require(not nonsingular((0,0,0)),'singular negative control')
    require(not on_curve((0,0),TARGET),'wrong point negative control')
    require(not exact_two_power((0,0),2,AUX),'wrong order negative control')
    if inject=='exception': raise RuntimeError('intentional unexpected-exception control')
    if inject=='early_return': return None
    odd=(P+1)>>96; generator_attempts=[]
    for candidate in range(32):
        point,tries=point_from_seed('F2-aux-generator-'+str(candidate),AUX)
        h=mul(odd,point,AUX)
        ok=exact_two_power(h,96,AUX)
        generator_attempts.append(dict(candidate=candidate,seed_point=list(point),point_search_tries=tries,
                                       projected_point=None if h is None else list(h),exact_order_2_96=ok))
        if ok: break
    else: raise RuntimeError('32 generator candidates exhausted')
    require(ok,'exact order 2^96 generator')
    curves=[AUX];edges=[];images=[h];edge_receipts=[]
    current=h
    for index in range(CHAIN_LENGTH):
        curve=curves[-1];remaining=96-index
        kernel=mul(1<<(remaining-1),current,curve)
        edge=make_edge(curve,kernel);destination=tuple(edge['destination'])
        require(nonsingular(destination),'nonsingular destination')
        require(map_point(kernel,edge) is None,'kernel image O')
        require(map_point(None,edge) is None,'infinity image O')
        new=map_point(current,edge)
        require(exact_two_power(new,remaining-1,destination),'exact image generator order')
        examples=[]
        for sample in range(4):
            u,_=point_from_seed(f'F2-edge-{index}-left-{sample}',curve)
            v,_=point_from_seed(f'F2-edge-{index}-right-{sample}',curve)
            fu,fv=map_point(u,edge),map_point(v,edge)
            require(on_curve(fu,destination) and on_curve(fv,destination),'map curve equation')
            require(map_point(add(u,v,curve),edge)==add(fu,fv,destination),'homomorphism sample')
            require(dual(fu,edge)==mul(2,u,curve),'dual phi=[2]')
            w,_=point_from_seed(f'F2-edge-{index}-destination-{sample}',destination)
            require(on_curve(dual(w,edge),curve),'dual curve equation')
            require(map_point(dual(w,edge),edge)==mul(2,w,destination),'phi dual=[2]')
            require(not on_curve((fu[0],(fu[1]+1)%P),destination),'mutated image rejected')
            examples.append(dict(source=list(u),image=list(fu),dual_of_image=list(dual(fu,edge)),
                                 destination_point=list(w),dual_destination=list(dual(w,edge))))
        edge.update(index=index,kernel_point=list(kernel),source_generator=list(current),
                    source_generator_order_two_exponent=remaining,image_generator=list(new))
        edges.append(edge);curves.append(destination);images.append(new);current=new
        edge_receipts.append(dict(index=index,examples=examples,checks='PASS'))
    dump(out/'generator.json',dict(p=P,auxiliary_curve=list(AUX),order=P+1,
         order_two_exponent=96,odd_cofactor=odd,generator=list(h),attempts=generator_attempts,
         point_count_proof='character-sum x,-x cancellation; chi(-1)=-1',
         cyclic_two_primary_proof='only rational nonzero 2-torsion is (0,0)'))
    dump(out/'chain.json',dict(edges=edges,degree=2**CHAIN_LENGTH,curves=[list(c) for c in curves]))
    for item in edge_receipts: dump(out/'edges'/f"edge-{item['index']:02}.json",item)
    ctx=fmpz_mod_poly_ctx(P);x=ctx([0,1]);numerator=x;denominator=ctx([1]);polynomials={}
    for level,edge in enumerate(edges,1):
        u=numerator-edge['r']*denominator
        nnew=u*u+edge['a']*u*denominator+edge['b']*denominator*denominator
        dnew=u*denominator
        gcd=nnew.gcd(dnew); numerator=nnew//gcd;denominator=dnew//gcd
        # Expanded symbolic checks are retained through level 12; the remaining chain stays factored.
        if level in BITS:
            polynomials[level]=(numerator,denominator)
            require(numerator.degree()==2**level and denominator.degree()==2**level-1,'rational map degrees')
            require(numerator.gcd(denominator).degree()==0,'reduced rational map')
        if level==max(BITS): break
    tor_candidates=[]
    for j in range(32):
        z=tor_pow(tor_seed('F2-torus-generator-'+str(j)),odd)
        good=tor_pow(z,2**96)==(1,0) and tor_pow(z,2**95)!=(1,0)
        tor_candidates.append(dict(index=j,point=list(z),exact_order_2_96=good))
        if good: break
    else: raise RuntimeError('torus generator search exhausted')
    require(good,'torus generator exact order')
    torus_generator=z;torus_offset=tor_seed('F2-Dickson-generic-offset')
    aux_offset,offset_tries=point_from_seed('F2-generic-offset-v1',AUX)
    summaries=[];all_cases=[]
    for bits in BITS:
        size=1<<bits; n,d=polynomials[bits]
        endpoint=map_chain(aux_offset,edges[:bits])
        require(endpoint is not None and endpoint[1]!=0,'generic endpoint non-2-torsion')
        inverse,invlevels=inverse_fibre(endpoint[0],edges[:bits])
        kg=mul(1<<(96-bits),h,AUX)
        require(exact_two_power(kg,bits,AUX),'fibre kernel order')
        coset=[];current=aux_offset
        for j in range(size):
            require(on_curve(current,AUX),'auxiliary coset point')
            require(map_chain(current,edges[:bits])==endpoint,'coset endpoint')
            coset.append(current);current=add(current,kg,AUX)
        require(current==aux_offset,'coset closed')
        require(len({point[0] for point in coset})==size,'generic distinct x')
        require(inverse=={point[0] for point in coset},'recursive complete fibre equality')
        f=n-endpoint[0]*d
        pf=product(ctx,sorted(inverse))
        require(f==pf,'generic full linear factorization')
        # This also checks every pole: one simple at x=0, the rest double, plus infinity simple.
        pole_kg=mul(1<<(96-bits),h,AUX)
        poles=[];current=pole_kg
        for j in range(1,size//2+1):
            require(map_chain(current,edges[:bits]) is None,'kernel point maps to O')
            poles.append(current[0]); current=add(current,pole_kg,AUX)
        nonzero_poles=[value for value in poles if value!=0]
        expected_d=x*product(ctx,nonzero_poles)**2
        require(d==expected_d,'complete poles multiplicities')
        w=n.derivative()*d-n*d.derivative()
        require(w.degree()==2*size-2,'ramification total degree')
        require(w.gcd(w.derivative()).degree()==0,'all rational map critical points simple')
        require(w.gcd(x*x*x+x).degree()==0,'source two torsion unramified on x line')
        finite=w//w.gcd(d)
        ca,cb,_=curves[bits]
        branch=n**3+ca*n*n*d+cb*n*d*d
        require((branch%finite).is_zero(),'finite critical values are destination two torsion')
        algebra=dict(level=bits,degree=size,numerator_sha256=digest_poly(n),denominator_sha256=digest_poly(d),
             fibre_polynomial_sha256=digest_poly(f),factor_product_sha256=digest_poly(pf),
             fibre_degree=f.degree(),fibre_squarefree=f.gcd(f.derivative()).degree()==0,
             denominator_degree=d.degree(),simple_finite_poles=1,double_finite_poles=size//2-1,
             infinity_pole_order=1,critical_polynomial_degree=w.degree(),critical_polynomial_squarefree=True,
             critical_poles=size//2-1,finite_branch_critical_degree=finite.degree(),
             finite_branch_values_destination_two_torsion=True)
        dump(out/'algebra'/f'level-{bits:02}.json',algebra)
        # Kernel coordinate base uses one more edge so its raw x size matches the generic fibre size.
        kernel_bits=bits+1
        generator=mul(1<<(96-kernel_bits),h,AUX)
        require(exact_two_power(generator,kernel_bits,AUX),'base kernel exact order')
        kernel_points=[];current=generator
        for j in range(1,size+1):
            require(on_curve(current,AUX),'base kernel point equation')
            require(map_chain(current,edges[:kernel_bits]) is None,'base kernel endpoint')
            kernel_points.append(current);current=add(current,generator,AUX)
        require(len({point[0] for point in kernel_points})==size,'kernel distinct x')
        tor_kernel=tor_pow(torus_generator,1<<(96-bits))
        tor_end=tor_pow(torus_offset,size)
        terminal=2*tor_end[0]%P
        require(terminal not in (2,P-2),'generic Dickson endpoint')
        dickson_points=[];zz=torus_offset
        for j in range(size):
            require((zz[0]*zz[0]+zz[1]*zz[1])%P==1,'torus norm one')
            dickson_points.append((2*zz[0]%P,zz))
            zz=tor_mul(zz,tor_kernel)
        require(zz==torus_offset,'torus coset closed')
        require(len({item[0] for item in dickson_points})==size,'Dickson distinct x')
        dd=x
        for _ in range(bits): dd=dd*dd-2
        df=dd-terminal
        require(df==product(ctx,[item[0] for item in dickson_points]),'Dickson complete fibre factorization')
        case_specs=[('elliptic_generic',coset,dict(chain_length=bits,endpoint=list(endpoint),
                    kernel_generator=list(kg),offset=list(aux_offset),inverse_level_sizes=invlevels)),
                    ('elliptic_kernel',kernel_points,dict(chain_length=kernel_bits,
                    kernel_generator=list(generator),kernel_order=2*size)),
                    ('Dickson_generic',dickson_points,dict(composition_depth=bits,terminal=terminal,
                    torus_generator=list(tor_kernel),offset=list(torus_offset),
                    polynomial_sha256=digest_poly(df)))]
        level_summaries=[]
        for family,points,meta in case_specs:
            name=f'{family}-M{size}';rows=[];accepted=[]; rejected=[]
            for index,item in enumerate(points):
                if family=='Dickson_generic':
                    xx,torpoint=item;auxpoint=None
                else: xx=item[0];auxpoint=list(item);torpoint=None
                yy=root(rhs(xx,TARGET))
                if yy is None:
                    rejected.append(xx)
                    row=dict(index=index,x=xx,auxiliary_point=auxpoint,torus_point=torpoint,
                             target_point=None,quadratic_character=-1)
                else:
                    targetpoint=(xx,yy)
                    require(on_curve(targetpoint,TARGET),'target lift equation')
                    require(mul(TARGET_R,targetpoint,TARGET) is None,'target prime subgroup')
                    require(yy!=0,'target has no order two points')
                    accepted.append(xx)
                    row=dict(index=index,x=xx,auxiliary_point=auxpoint,torus_point=torpoint,
                             target_point=list(targetpoint),quadratic_character=1,
                             target_order=TARGET_R,target_order_check='r*P=O')
                rows.append(row)
            filenames=[]
            for chunk_start in range(0,len(rows),CHUNK):
                filename=f'cases/{name}/rows-{chunk_start:05}.json'
                dump(out/filename,rows[chunk_start:chunk_start+CHUNK]);filenames.append(filename)
            case=dict(case=name,family=family,raw_x_size=size,accepted_x_size=len(accepted),
                      rejected_x_size=len(rejected),target_signed_point_count=2*len(accepted),
                      canonical_sign='0<y<=floor(p/2)',d=3,complete_raw_domain=True,
                      certificate_chunks=filenames,metadata=meta)
            dump(out/'cases'/name/'summary.json',case)
            all_cases.append(case);level_summaries.append(case)
        matched=min(case['accepted_x_size'] for case in level_summaries)
        for case in level_summaries:
            case['matched_accepted_M']=matched
            case['matching_rule']='sort accepted x; retain first matched_accepted_M'
            dump(out/'cases'/case['case']/'summary.json',case)
        summaries.append(dict(raw_M=size,degree_generic=size,degree_kernel=2*size,
             d=3,matched_final_M=matched,counts={case['family']:case['accepted_x_size'] for case in level_summaries},
             target_signed_points_matched=2*matched))
    compact_bits=16;compact_k=mul(1<<(96-compact_bits),h,AUX)
    compact_q=map_chain(aux_offset,edges)
    require(exact_two_power(compact_k,compact_bits,AUX),'full chain compact kernel order')
    require(compact_q is not None and compact_q[1]!=0,'full chain generic terminal')
    dump(out/'compact-full-chain.json',dict(chain_length=16,degree=65536,
        kernel_generator=list(compact_k),kernel_order=65536,generic_offset=list(aux_offset),
        generic_endpoint=list(compact_q),complete_fibre_formula='x(P+j*K), 0<=j<65536',
        distinct_x_proof='if P+jK=-(P+lK), then 2*Phi(P)=O, contradicted by endpoint y!=0',
        enumeration_status='compact proof certificate; full 65536 target lifts not enumerated',
        kernel_x_count=32768,target_lift_enumeration_status='NOT_RUN at degree 65536'))
    dump(out/'comparison.json',dict(summaries=summaries,matching='same final canonical x size M and d=3; deterministic sorted-prefix selection',
        conditional_sampling='structured complete fibres; no uniform target or relation-yield inference',
        membership_circuits=dict(elliptic_step='(x-r)^2+(a-X)*(x-r)+b=0, with x!=r',
        Dickson_step='X=x^2-2'),
        costs=dict(elliptic_sequential_x_step='1 inversion, 1 multiplication by b; translations/additions',
        elliptic_polynomial_constraint='quadratic bilinear equation plus denominator nonzero constraints',
        Dickson_step='one squaring, one subtraction; no finite poles',
        setup='elliptic generator projection, kernel generation, curve/map constants; torus norm-one generator projection',
        recovery='both require root/fibre enumeration, target square roots, rejection and subgroup validation',
        relation_solver='NOT_IMPLEMENTED; same d=3 and matched accepted M do not certify any relation cost',
        amortization='setup may be reused; sorted-prefix selection and per-query solving still charged'),
        performance_claim=None))
    result=dict(task='TASK-20261025-929e0f',track='F2',status='implementation_validation_pass',
        scope='exact arithmetic and theory screening; no admitted scientific performance trial or state transition',
        checks=checks,field=P,target=dict(curve=list(TARGET),r=TARGET_R,h=1),
        auxiliary=dict(curve=list(AUX),order=P+1,v2_order=96,generator=list(h)),
        chain=dict(edges=16,degree=65536,rational=True,separable=True,dual_composition_checks=128),
        complete_enumerated_cases=len(all_cases),raw_x_rows=sum(c['raw_x_size'] for c in all_cases),
        summaries=summaries,software=dict(python=sys.version,flint=flint.__version__,platform=platform.platform()),
        limits=dict(point_search_cap=10000,generator_search_cap=32,max_concurrent_processes=1,memory_envelope_gb=2),
        validation_resources=dict(wall_seconds=time.monotonic()-start,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        limitations=['No summation-polynomial relation solver, rank evidence, or attack/performance claim.',
          'Full degree-65536 fibre has compact mathematical certificate; only degrees 64,256,1024,4096 have enumerated target lifts.',
          'Primality uses FLINT rigorous is_prime backend; no portable primality proof object serialized.',
          'Target cardinality r is the published P-256 parameter; all accepted lifts additionally satisfy [r]P=O.',
          'No rational homomorphism from target into auxiliary curve; coordinates are reinterpreted, not group-transferred.',
          'Model binding unprobed as instructed; no independent review performed in this producing session.'],
        next_decisive_step='At the frozen matched final M and d=3, implement complete relation solving for both rational-chain and Dickson membership, with saturation of all denominators and full cost accounting.',
        completion_sentinel='F2_EXACT_CHECKS_COMPLETE')
    dump(out/'result.json',result)
    return result

if __name__=='__main__':
    raise SystemExit('Use run_validation.py; direct implementation execution is refused.')
