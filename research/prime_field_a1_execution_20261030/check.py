"""Independent pool/branch/point/cancellation replay, without producer imports."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('_a1_old_reference',ROOT/'research/prime_field_b2_execution_20261030/check.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
from independent import add,multiply,convolution,evaluate,vandermonde,verify_fixture,dense_rank,verify_row as verify_old_row
from check_inputs import public_projection

LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',
 R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',
 B='residual_endpoint_outside_base_and_pool',A='canonical_alias',**{'+':'accepted'})


def canonical(point,p):return (point[0],min(point[1],-point[1]%p))


def check_pool(cell,pool,recipe):
    f=cell['fixture'];p=f['p'];roots={}
    for y in range(p):roots.setdefault(y*y%p,y)
    excluded={canonical(a['point'],p) for a in f['factor_base']};points=[];attempts=[]
    for index in range(recipe['size']):
        for counter in range(recipe['max_counter']):
            digest=sha256(f"{recipe['domain']}|{cell['pool_curve_uid']}|{index}|{counter}".encode()).hexdigest();x=int(digest,16)%p
            y=roots.get((x**3+f['a']*x+f['b'])%p);point=None if y is None else (x,y);status='accepted'
            if point is None:status='no_rational_point'
            elif multiply(p,0,f['a'],f['r'],point) is not None:status='outside_subgroup'
            elif point in excluded:status='base_or_previous_pool_point'
            attempts.append(dict(index=index,counter=counter,sha256=digest,x=x,point=None if point is None else list(point),status=status))
            if status=='accepted':points.append(list(point));excluded.add(point);break
        else:raise ValueError('independent pool hash bound exhausted')
    expected=dict(schema='prym-residual-pool/v1',curve_uid=cell['pool_curve_uid'],recipe=recipe,points=points,hash_attempts=attempts,scalar_labels_generated=False)
    if any(pool.get(k)!=v for k,v in expected.items()):raise ValueError('pool recipe/first-counter certificate differs')
    return len(attempts)


class Reference(old.Reference):
    def __init__(self,cell,pool):
        super().__init__(cell['fixture'],0,list(range(len(cell['fixture']['factor_base']))));self.pool=pool['points']
        self.base_by_x={a['point'][0]:(j,tuple(a['point'])) for j,a in enumerate(self.fixture['factor_base'])}
        self.pool_by_point={tuple(point):j for j,point in enumerate(self.pool)}

    def outcome(self,scalar,triple,options,seen):
        points,status=self.descriptor(scalar,triple,options)
        if points is None:return status,None,None
        identities=[]
        for deck,sign in product((1,-1),repeat=2):
            transformed=[(deck*x%self.p,sign*y%self.p) for x,y in points]
            labels=sorted((j,sign*(-1 if op&1 else 1),*point) for j,op,point in zip(triple,options,transformed[1:]))
            identities.append(dict(curve_uid=self.fixture['uid'],source_scalar=sign*scalar%self.fixture['r'],
                **{'lambda':1},signed_fb_lift_ids=dict(source_lift=transformed[0],base_lifts=labels)))
        encode=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'))
        chosen=min(identities,key=encode);chosen.update(cover_shift=0,active_atoms=self.active);key=sha256(encode(chosen).encode()).hexdigest()
        if key in seen:return 'A',key,None
        seen.add(key);v=vandermonde(self.p,points)
        if len(v)==4 and v[-1]*v[-1]%self.p==1:return 'P',key,None
        vv=convolution(self.p,v,v);remainder=[((vv[j] if j<len(vv) else 0)-self.F[j])%self.p for j in range(7)]
        divisor=[1]
        for x,y in points:divisor=convolution(self.p,divisor,[-x%self.p,1])
        quotient=[0]*3
        for j in (2,1,0):
            quotient[j]=remainder[j+4]
            for i,c in enumerate(divisor):remainder[j+i]=(remainder[j+i]-quotient[j]*c)%self.p
        if any(remainder):raise ValueError('independent residual division failed')
        c,b,a=quotient;disc=(b*b-4*a*c)%self.p
        if not a or not disc or disc not in self.roots:return 'R',key,None
        root=self.roots[disc];inv=pow(2*a,-1,self.p);roots=sorted({(-b-root)*inv%self.p,(-b+root)*inv%self.p})
        if len(roots)!=2 or set(roots)&{x for x,y in points}:return 'X',key,None
        coefficients=[0]*len(self.active);outside=[0]*len(self.pool);used=set()
        for j,op in zip(triple,options):coefficients[j]+=(-1 if op&1 else 1)
        for x in roots:
            point=(x*x%self.p,evaluate(self.p,v,x));base=self.base_by_x.get(point[0])
            if base is not None:
                j,atom=base
                if point==atom:coefficients[j]+=1
                elif point==(atom[0],-atom[1]%self.p):coefficients[j]-=1
                else:raise ValueError('independent base orientation mismatch')
            else:
                k=canonical(point,self.p);j=self.pool_by_point.get(k)
                if j is None:return 'B',key,None
                outside[j]+=1 if k==point else -1;used.add(j)
        row=dict(schema='prym-residual-row/v1',curve_uid=self.fixture['uid'],source_scalar=scalar,
            coefficients=[c%self.fixture['r'] for c in coefficients],outside_coefficients=[c%self.fixture['r'] for c in outside],outside_indices_used=sorted(used),
            constraints=[list(point) for point in points],base_labels=[[j,-1 if op&1 else 1,op] for j,op in zip(triple,options)],
            v_coefficients=v,residual_coefficients=quotient,residual_roots=roots,pole_orders_at_infinity=[3,3],
            source_locator='fixed-base cubic interpolation with independently hashed residual pool; no scalar oracle')
        return '+',key,row


def verify_row(cell,pool,row,reference=None):
    reference=Reference(cell,pool) if reference is None else reference;f=cell['fixture'];p=f['p'];a=f['a']
    labels=row['base_labels'];triple=tuple(v[0] for v in labels);options=tuple(v[2] for v in labels)
    if type(row['source_scalar']) is not int or not 0<row['source_scalar']<f['r']:raise ValueError('invalid public source scalar')
    if len(labels)!=3 or tuple(sorted(set(triple)))!=triple or any(j not in range(len(f['factor_base'])) for j in triple) or any(op not in range(4) for op in options):raise ValueError('invalid constraint labels')
    status,key,expected=reference.outcome(row['source_scalar'],triple,options,set())
    if status!='+' or row!=expected:raise ValueError('partial principal-divisor witness differs')
    total=None
    for c,atom in zip(row['coefficients'],f['factor_base'],strict=True):total=add(p,0,a,total,multiply(p,0,a,c,tuple(atom['point'])))
    for c,point in zip(row['outside_coefficients'],pool['points'],strict=True):total=add(p,0,a,total,multiply(p,0,a,c,tuple(point)))
    if total!=multiply(p,0,a,row['source_scalar'],tuple(f['P'])):raise ValueError('partial original E equation fails')
    all_points=[tuple(v) for v in row['constraints']]+[(x,evaluate(p,row['v_coefficients'],x)) for x in row['residual_roots']]
    auxiliary=None
    for x,y in all_points:
        if (y*y-x**6-a*x*x-f['b'])%p:raise ValueError('partial intersection point off C')
        if x:
            inverse=pow(x,-1,p);point=(f['b']*inverse**2%p,f['b']*y*inverse**3%p)
            auxiliary=add(p,a,0,auxiliary,point)
    if auxiliary is not None:raise ValueError('partial auxiliary principal sum fails')
    return True


def outside_projection(cell,pool):
    f=cell['fixture'];p,r=f['p'],f['r'];known={};derivations=[];mapping=[];unknown=[]
    for s in cell['source_order']:
        point=multiply(p,0,f['a'],s,tuple(f['P']));key=canonical(point,p);value=s if point==key else -s%r
        if key in known and known[key]!=value:raise ValueError('public source inconsistency')
        known[key]=value
    for point in pool['points']:
        key=tuple(point)
        if key in known:mapping.append(['known',known[key]]);derivations.append(dict(point=point,scalar=known[key]))
        else:mapping.append(['unknown',len(unknown)]);unknown.append(point)
    return dict(U=len(unknown),native_to_projected=mapping,unknown_points=unknown,public_derivations=derivations)


def check_arms(cell,result):
    f=cell['fixture'];r=f['r'];projection=result['projection'];outside=result['outside_projection']
    oldrows=[old.project(row,projection,r) for row in cell['preprocessing_rows']];M=[v for v,b in oldrows];base_rank=dense_rank(M,r);summaries=[]
    def quality(vectors,values,columns):
        keys=set()
        for v,b in zip(vectors,values):
            affine=v+[b];first=next((x for x in affine if x),None)
            keys.add(tuple(x*pow(first,-1,r)%r for x in affine) if first else tuple(affine))
        rank=dense_rank(vectors,r)
        return dict(rows=len(vectors),unique_affine_equations=len(keys),duplicate_equations=len(vectors)-len(keys),rank=rank,columns=columns,nullity=columns-rank)
    for arm,prefix in zip(result['arms'],(0,16,32),strict=True):
        name='smooth' if prefix==0 else 'pool'+str(prefix);indices=[i for i,row in enumerate(result['rows']) if all(j<prefix for j in row['outside_indices_used'])]
        columns=sum(m[0]=='unknown' for m in outside['native_to_projected'][:prefix]);B=[];U=[];rhs=[]
        for i in indices:
            row=result['rows'][i];v,b=old.project(row,projection,r);u=[0]*columns
            for coefficient,mapping in zip(row['outside_coefficients'][:prefix],outside['native_to_projected'][:prefix],strict=True):
                if mapping[0]=='known':b-=coefficient*mapping[1]
                else:u[mapping[1]]+=coefficient
            B.append(v);U.append([c%r for c in u]);rhs.append(b%r)
        rank_u=dense_rank(U,r);stacked=[v+[0]*columns for v in M]+[b+u for b,u in zip(B,U)];rank=dense_rank(stacked,r)
        delta=rank-rank_u-base_rank
        direct_indices=[i for i,u in zip(indices,U) if not any(u)];direct_rank=dense_rank(M+[b for b,u in zip(B,U) if not any(u)],r)
        kernel=arm['old_kernel'];nullity=projection['U']-base_rank
        if (len(kernel)!=nullity or any(len(v)!=projection['U'] for v in kernel) or dense_rank(kernel,r)!=nullity or
            any(sum(x*y for x,y in zip(v,row))%r for v in kernel for row in M)):
            raise ValueError('old kernel is incomplete or does not annihilate M')
        if arm['preprocessing_quality']!=quality(M,[b for v,b in oldrows],projection['U']) or arm['new_quality']!=quality([b+u for b,u in zip(B,U)],rhs,projection['U']+columns):
            raise ValueError('affine quality metadata differs')
        if any(arm.get(k)!=v for k,v in dict(arm=name,pool_prefix=prefix,row_indices=indices,B=B,U=U,rhs=rhs,
            stacked_rank=rank,outside_rank=rank_u,rank_gain=delta,base_rank_after=base_rank+delta,
            base_nullity_after=projection['U']-base_rank-delta,outside_columns=columns,naive_augmented_gain=rank-base_rank,
            direct_base_rank=direct_rank,direct_base_gain=direct_rank-base_rank,direct_base_row_indices=direct_indices,cross_row_cancellation_gain=base_rank+delta-direct_rank).items()):
            raise ValueError('arm projection/rank identity differs')
        certificates=arm['cancellation']['cancellations'];cancelled=[];cancel_rhs=[];weights_matrix=[]
        previous=base_rank
        for cert in certificates:
            weights=cert['partial_row_weights']
            if len(weights)!=len(B):raise ValueError('partial cancellation weight count differs')
            if any(sum(w*u[j] for w,u in zip(weights,U))%r for j in range(columns)):raise ValueError('outside column did not cancel')
            v=[sum(w*b[j] for w,b in zip(weights,B))%r for j in range(projection['U'])];b=sum(w*t for w,t in zip(weights,rhs))%r
            if cert['coefficients']!=v or cert['rhs']!=b:raise ValueError('carried cancellation equation differs')
            weights_matrix.append(weights);cancelled.append(v);cancel_rhs.append(b)
            current=dense_rank(M+cancelled,r)
            if cert['independent_of_base_and_previous']!=(current>previous):raise ValueError('cancellation independence flag differs')
            previous=current
            point=None
            for coefficient,atom in zip(v,projection['unknown_points']):point=add(f['p'],0,f['a'],point,multiply(f['p'],0,f['a'],coefficient,tuple(atom)))
            if point!=multiply(f['p'],0,f['a'],b,tuple(f['P'])):raise ValueError('cancelled base equation fails public verification')
        if len(certificates)!=len(B)-rank_u or dense_rank(weights_matrix,r)!=len(certificates):raise ValueError('incomplete cancellation-weight kernel')
        after=dense_rank(M+cancelled,r)
        if after!=base_rank+delta or dense_rank([v+[b] for v,b in oldrows]+[v+[b] for v,b in zip(cancelled,cancel_rhs)],r)!=after:
            raise ValueError('cancelled base rank/consistency differs')
        if any(arm['cancellation'].get(k)!=v for k,v in dict(outside_rank=rank_u,base_rank_before=base_rank,base_rank_after=after,rank_gain=delta).items()):raise ValueError('cancellation summary differs')
        syndromes=[[sum(x*y for x,y in zip(v,k))%r for k in kernel] for v in cancelled]
        if arm['cancelled_old_kernel_syndromes']!=syndromes or arm['nonzero_old_kernel_syndromes']!=sum(any(v) for v in syndromes):raise ValueError('cancelled old-kernel action differs')
        summaries.append(dict(arm=name,rank_gain=delta,outside_rank=rank_u,stacked_rank=rank,base_rank_after=after,cancellations_verified=len(certificates),
            direct_base_rank=direct_rank,direct_base_gain=direct_rank-base_rank,cross_row_cancellation_gain=after-direct_rank))
    return summaries


def check(cell,result,recipe):
    f=cell['fixture'];verify_fixture(f);hashes=check_pool(cell,result['pool'],recipe);reference=Reference(cell,result['pool'])
    projection=public_projection(f,cell['source_order'])
    if result['projection']!=projection or result['outside_projection']!=outside_projection(cell,result['pool']):raise ValueError('public projection differs')
    for row in cell['preprocessing_rows']:verify_old_row(f,row)
    seen=set();rows=[];counts=Counter();digest=sha256();attempts=0;blocks=[]
    for scalar in cell['source_order']:
        statuses=[];source_digest=sha256()
        for triple in combinations(range(len(f['factor_base'])),3):
            for options in product(range(4),repeat=3):
                attempts+=1;status,identity,row=reference.outcome(scalar,triple,options,seen);reason=LEGEND[status];counts[reason]+=1;statuses.append(status)
                if row is not None:verify_row(cell,result['pool'],row,reference);rows.append(row)
                encoded=json.dumps([scalar,list(triple),list(options),identity,reason],separators=(',',':')).encode()+b'\n';digest.update(encoded);source_digest.update(encoded)
        blocks.append(dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest()))
    if any(result.get(k)!=v for k,v in dict(schema='prym-residual-partials/v1',curve_uid=f['uid'],source_order=cell['source_order'],
        complete=True,attempts=attempts,statuses=dict(counts),status_legend=LEGEND,status_blocks=blocks,branch_sha256=digest.hexdigest(),rows=rows).items()):
        raise ValueError('complete residual branch replay differs')
    arms=check_arms(cell,result)
    return dict(checked=True,complete_branch_replay=True,pool_recipe_checked=True,attempts_replayed=attempts,hash_attempts_replayed=hashes,rows_verified=len(rows),arms=arms,
        scope='Separate arithmetic/branch/hash/cancellation implementation check; producer counters not audited, not independent staffed scientific review.')
