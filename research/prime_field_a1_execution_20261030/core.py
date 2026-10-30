"""Fixed-base cubic collection with bounded, independently hashed residual pools."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(ROOT/'research/prime_field_factor_base_20261028'))
from prym_completion import CompletionContext
from arithmetic import interpolate,padd,pdiv,peval,pmul,quadratic_roots
from relations import uid
from independent import verify_fixture,verify_row as verify_old_row
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
from collect_width import public_projection,project
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations,cancel_outside

PARAMETERS={'pool_prefixes':[0,16,32],'include_zero':True,'cover_shift':0,'max_partial_rows':2048,'max_outside_columns':32}
_NATIVE_CAPABILITY=object()
LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',
 R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',
 B='residual_endpoint_outside_base_and_pool',A='canonical_alias',**{'+':'accepted'})


def guard(cell,capability):
    f=cell['fixture']
    if capability is not _NATIVE_CAPABILITY and not (f.get('software_control') is True and f['p']<=211):
        raise ValueError('scientific residual collection requires native admission')


def canonical(point,p):return (point[0],min(point[1],-point[1]%p))


def generate_pool(cell,recipe,event,*,capability=None):
    guard(cell,capability);f=cell['fixture'];p=f['p'];curve=Curve(p,f['a'],f['b'])
    if recipe['size']!=32 or recipe['max_counter']!=10000 or recipe['domain']!='prime-field-residual-pool/20261030/v1':raise ValueError('fixed pool recipe required')
    excluded={canonical(atom['point'],p) for atom in f['factor_base']};points=[];attempts=[]
    for index in range(recipe['size']):
        for counter in range(recipe['max_counter']):
            message=f"{recipe['domain']}|{cell['pool_curve_uid']}|{index}|{counter}";digest=sha256(message.encode()).hexdigest()
            x=int(digest,16)%p;point=curve.lift_x(x)
            reason='accepted'
            if point is None:reason='no_rational_point'
            elif curve.mul(f['r'],point) is not None:reason='outside_subgroup'
            elif point in excluded:reason='base_or_previous_pool_point'
            item=dict(index=index,counter=counter,sha256=digest,x=x,point=None if point is None else list(point),status=reason)
            attempts.append(item);event(dict(kind='pool_hash_attempt',**item))
            if reason=='accepted':points.append(list(point));excluded.add(point);break
        else:raise ValueError('pool hash counter bound exhausted')
    return dict(schema='prym-residual-pool/v1',curve_uid=cell['pool_curve_uid'],recipe=recipe,points=points,hash_attempts=attempts,
                hash_group_ops=curve.ops.group_ops,scalar_labels_generated=False)


class ResidualContext(CompletionContext):
    def __init__(self,fixture,pool):
        super().__init__(fixture);self.pool=pool['points'];self.by_pool={tuple(point):j for j,point in enumerate(self.pool)}

    def canonical_identity(self,descriptor):
        value=super().canonical_identity(descriptor);value.update(cover_shift=0,active_atoms=list(range(len(self.base))));return value

    def construct(self,descriptor):
        f=self.f;points=descriptor['points'];v=interpolate(f,points)
        intersection=padd(f,pmul(f,v,v),[self.b,0,self.a,0,0,0,1],sign=-1)
        if len(intersection)!=7:return None,LEGEND['P']
        known=[1]
        for x,y in points:known=pmul(f,known,[-x%self.p,1])
        residual,remainder=pdiv(f,intersection,known)
        if remainder!=[0]:raise ArithmeticError('residual division failed')
        roots=quadratic_roots(f,residual)
        if roots is None or len(roots)!=2:return None,LEGEND['R']
        if set(roots)&{x for x,y in points}:return None,LEGEND['X']
        coefficients=[0]*len(self.base);outside=[0]*len(self.pool);used=set()
        for j,sign,option in descriptor['labels']:coefficients[j]+=sign
        for x in roots:
            point=(f.mul(x,x),peval(f,v,x));j=self.by_x.get(point[0])
            if j is not None:
                if point==self.base[j]:coefficients[j]+=1
                elif point==(self.base[j][0],-self.base[j][1]%self.p):coefficients[j]-=1
                else:raise ArithmeticError('base endpoint orientation differs')
            else:
                key=canonical(point,self.p);j=self.by_pool.get(key)
                if j is None:return None,LEGEND['B']
                outside[j]+=1 if point==key else -1;used.add(j)
        return dict(schema='prym-residual-row/v1',curve_uid=self.fixture['uid'],source_scalar=descriptor['source_scalar'],
            coefficients=[c%self.r for c in coefficients],outside_coefficients=[c%self.r for c in outside],outside_indices_used=sorted(used),
            constraints=[list(p) for p in points],base_labels=[list(t) for t in descriptor['labels']],
            v_coefficients=v,residual_coefficients=residual,residual_roots=roots,pole_orders_at_infinity=[3,3],
            source_locator='fixed-base cubic interpolation with independently hashed residual pool; no scalar oracle'),None


def outside_projection(context,sources,pool):
    known={};derivations=[];mapping=[];unknown=[]
    for s in sources:
        point=context.e.mul(s,context.P);key=canonical(point,context.p);sign=1 if point==key else -1
        if key in known and known[key]!=sign*s%context.r:raise ValueError('inconsistent public source')
        known[key]=sign*s%context.r
    for point in pool['points']:
        key=tuple(point)
        if key in known:
            mapping.append(['known',known[key]]);derivations.append(dict(point=point,scalar=known[key]))
        else:mapping.append(['unknown',len(unknown)]);unknown.append(point)
    return dict(U=len(unknown),native_to_projected=mapping,unknown_points=unknown,public_derivations=derivations)


def project_partial(row,projection,outside,r,prefix):
    B,rhs=project(row,projection,r);columns=sum(m[0]=='unknown' for m in outside['native_to_projected'][:prefix]);U=[0]*columns
    for c,mapping in zip(row['outside_coefficients'][:prefix],outside['native_to_projected'][:prefix],strict=True):
        if mapping[0]=='known':rhs-=c*mapping[1]
        else:U[mapping[1]]+=c
    return B,[u%r for u in U],rhs%r


def collect(cell,pool,event,*,capability=None):
    guard(cell,capability);fixture=cell['fixture'];verify_fixture(fixture);context=ResidualContext(fixture,pool);sources=cell['source_order']
    if len(set(sources))!=len(sources) or any(type(s) is not int or not 0<s<fixture['r'] for s in sources):raise ValueError('bad source order')
    projection=public_projection(context,sources);outside=outside_projection(context,sources,pool)
    if outside['U']>PARAMETERS['max_outside_columns']:raise ValueError('outside-column size gate exceeded')
    rows=[];seen=set();counts=Counter();digest=sha256();attempts=0;blocks=[];codes={v:k for k,v in LEGEND.items()}
    from check import verify_row
    for scalar in sources:
        statuses=[];source_digest=sha256()
        for triple in combinations(range(len(context.base)),3):
            for options in product(range(4),repeat=3):
                attempts+=1;descriptor,reason=context.descriptor(scalar,triple,options);identity=None
                if reason=='source_no_nonzero_rational_lift':reason=LEGEND['S']
                if descriptor is not None:
                    identity=uid(context.canonical_identity(descriptor))
                    if identity in seen:reason=LEGEND['A']
                    else:
                        seen.add(identity);row,reason=context.construct(descriptor)
                        if row is not None:
                            event(dict(kind='verified_witness_pending',attempt=attempts,row=row))
                            verify_row(cell,pool,row);rows.append(row)
                            if len(rows)>PARAMETERS['max_partial_rows']:raise ValueError('partial-row size gate exceeded; prefix retained, no truncation')
                            event(dict(kind='accepted',attempt=attempts,row_index=len(rows)-1,row=row))
                status=reason or 'accepted';counts[status]+=1;statuses.append(codes[status])
                encoded=json.dumps([scalar,list(triple),list(options),identity,status],separators=(',',':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
        block=dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest())
        blocks.append(block);event(dict(kind='source_complete',**block,accepted=len(rows),counts=dict(counts)))
    return dict(schema='prym-residual-partials/v1',curve_uid=fixture['uid'],pool=pool,projection=projection,outside_projection=outside,
        source_order=sources,complete=True,attempts=attempts,statuses=dict(counts),status_legend=LEGEND,status_blocks=blocks,
        branch_sha256=digest.hexdigest(),rows=rows,operation_vector=dict(context.f.counts),arms=[],scientific_promotion=False)


def analyze_arm(cell,result,prefix):
    if prefix not in PARAMETERS['pool_prefixes'] or len(result['rows'])>PARAMETERS['max_partial_rows'] or result['outside_projection']['U']>PARAMETERS['max_outside_columns']:
        raise ValueError('elimination size gate exceeded')
    fixture=cell['fixture'];r=fixture['r'];base=AffineRelations(r,result['projection']['U'])
    for row in cell['preprocessing_rows']:verify_old_row(fixture,row);base.add(*project(row,result['projection'],r))
    indices=[i for i,row in enumerate(result['rows']) if all(j<prefix for j in row['outside_indices_used'])]
    projected=[project_partial(result['rows'][i],result['projection'],result['outside_projection'],r,prefix) for i in indices]
    B=[b for b,u,v in projected];U=[u for b,u,v in projected];rhs=[v for b,u,v in projected]
    columns=sum(m[0]=='unknown' for m in result['outside_projection']['native_to_projected'][:prefix])
    stacked=AffineRelations(r,base.columns+columns);new=AffineRelations(r,base.columns+columns)
    for v,b in zip(base.rows,base.rhs):stacked.add(v+[0]*columns,b)
    for b,u,v in projected:stacked.add(b+u,v);new.add(b+u,v)
    cancellation=cancel_outside(base,B,U,rhs);old_kernel=base.kernel()
    direct=AffineRelations(r,base.columns)
    for v,b in zip(base.rows,base.rhs):direct.add(v,b)
    direct_indices=[]
    for i,(b,u,v) in zip(indices,projected):
        if not any(u):direct.add(b,v);direct_indices.append(i)
    syndromes=[[sum(a*b for a,b in zip(c['coefficients'],kernel))%r for kernel in old_kernel] for c in cancellation['cancellations']]
    return dict(arm='smooth' if prefix==0 else 'pool'+str(prefix),pool_prefix=prefix,row_indices=indices,B=B,U=U,rhs=rhs,
        preprocessing_quality=base.summary(),new_quality=new.summary(),stacked_rank=stacked.rank,outside_rank=cancellation['outside_rank'],
        outside_columns=columns,rank_gain=cancellation['rank_gain'],base_rank_after=cancellation['base_rank_after'],
        base_nullity_after=base.columns-cancellation['base_rank_after'],cancellation=cancellation,
        naive_augmented_gain=stacked.rank-base.rank,old_kernel=old_kernel,cancelled_old_kernel_syndromes=syndromes,
        direct_base_rank=direct.rank,direct_base_gain=direct.rank-base.rank,direct_base_row_indices=direct_indices,
        cross_row_cancellation_gain=cancellation['base_rank_after']-direct.rank,
        nonzero_old_kernel_syndromes=sum(any(v) for v in syndromes),complete=True)
