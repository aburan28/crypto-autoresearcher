"""Base-only completion when the two residual E images cancel, without a pool."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(ROOT/'research/prime_field_factor_base_20261028'))
from prym_completion import CompletionContext
from arithmetic import interpolate,padd,pdiv,peval,pmul,quadratic_roots
from relations import uid
from independent import verify_fixture,verify_row as verify_old_row
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
from collect_width import public_projection,project
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations

PARAMETERS={'arms':['smooth','norm_completed'],'include_zero':True,'cover_shift':0,'max_retained_rows':2048}
_NATIVE_CAPABILITY=object()
LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',B='residual_neither_smooth_nor_norm_cancelling',A='canonical_alias',**{'+':'accepted'})


class NormContext(CompletionContext):
    def canonical_identity(self,descriptor):
        value=super().canonical_identity(descriptor);value.update(cover_shift=0,active_atoms=list(range(len(self.base))));return value

    def construct(self,descriptor):
        f=self.f;points=descriptor['points'];v=interpolate(f,points);intersection=padd(f,pmul(f,v,v),[self.b,0,self.a,0,0,0,1],sign=-1)
        if len(intersection)!=7:return None,LEGEND['P']
        known=[1]
        for x,y in points:known=pmul(f,known,[-x%self.p,1])
        residual,remainder=pdiv(f,intersection,known)
        if remainder!=[0]:raise ArithmeticError('residual division failed')
        roots=quadratic_roots(f,residual)
        if roots is None or len(roots)!=2:return None,LEGEND['R']
        if set(roots)&{x for x,y in points}:return None,LEGEND['X']
        images=[(f.mul(x,x),peval(f,v,x)) for x in roots];smooth=all(point[0] in self.by_x for point in images)
        cancelled=images[0][0]==images[1][0] and (images[0][1]+images[1][1])%self.p==0
        if not smooth and not cancelled:return None,LEGEND['B']
        coefficients=[0]*len(self.base)
        for j,sign,option in descriptor['labels']:coefficients[j]+=sign
        if smooth:
            for point in images:
                j=self.by_x[point[0]]
                if point==self.base[j]:coefficients[j]+=1
                elif point==(self.base[j][0],-self.base[j][1]%self.p):coefficients[j]-=1
                else:raise ArithmeticError('base endpoint orientation differs')
        return dict(schema='prym-norm-completed-row/v1',curve_uid=self.fixture['uid'],source_scalar=descriptor['source_scalar'],
            coefficients=[c%self.r for c in coefficients],constraints=[list(p) for p in points],base_labels=[list(t) for t in descriptor['labels']],
            v_coefficients=v,residual_coefficients=residual,residual_roots=roots,residual_E_images=[list(point) for point in images],
            norm_completed=not smooth,pole_orders_at_infinity=[3,3],source_locator='fixed cubic with smooth or cancelling residual E images; no outside unknowns'),None


def collect(cell,event,*,capability=None):
    fixture=cell['fixture']
    if capability is not _NATIVE_CAPABILITY and not (fixture.get('software_control') is True and fixture['p']<=211):raise ValueError('scientific norm collection requires native admission')
    verify_fixture(fixture);context=NormContext(fixture);sources=cell['source_order']
    if len(set(sources))!=len(sources) or any(type(s) is not int or not 0<s<fixture['r'] for s in sources):raise ValueError('bad source order')
    projection=public_projection(context,sources);rows=[];seen=set();counts=Counter();digest=sha256();attempts=0;blocks=[];codes={v:k for k,v in LEGEND.items()}
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
                            event(dict(kind='verified_witness_pending',attempt=attempts,row=row));verify_row(cell,row);rows.append(row)
                            if len(rows)>PARAMETERS['max_retained_rows']:raise ValueError('retained-row size gate exceeded; prefix retained, no truncation')
                            event(dict(kind='accepted',attempt=attempts,row_index=len(rows)-1,row=row))
                status=reason or 'accepted';counts[status]+=1;statuses.append(codes[status]);encoded=json.dumps([scalar,list(triple),list(options),identity,status],separators=(',',':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
        block=dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest());blocks.append(block)
        event(dict(kind='source_complete',**block,accepted=len(rows),counts=dict(counts)))
    return dict(schema='prym-norm-completion/v1',curve_uid=fixture['uid'],source_order=sources,complete=True,attempts=attempts,statuses=dict(counts),status_legend=LEGEND,
        status_blocks=blocks,branch_sha256=digest.hexdigest(),rows=rows,projection=projection,operation_vector=dict(context.f.counts),arms=[],scientific_promotion=False)


def analyze_arm(cell,result,name):
    if name not in PARAMETERS['arms'] or len(result['rows'])>PARAMETERS['max_retained_rows']:raise ValueError('arm/retained-row gate failed')
    f=cell['fixture'];base=AffineRelations(f['r'],result['projection']['U']);combined=AffineRelations(f['r'],result['projection']['U']);new=AffineRelations(f['r'],result['projection']['U'])
    for row in cell['preprocessing_rows']:
        verify_old_row(f,row);v,b=project(row,result['projection'],f['r']);base.add(v,b);combined.add(v,b)
    indices=[i for i,row in enumerate(result['rows']) if name=='norm_completed' or not row['norm_completed']];kernel=base.kernel();syndromes=[]
    for i in indices:
        v,b=project(result['rows'][i],result['projection'],f['r']);new.add(v,b);combined.add(v,b);syndromes.append([sum(a*b for a,b in zip(v,k))%f['r'] for k in kernel])
    return dict(arm=name,row_indices=indices,preprocessing_quality=base.summary(),new_quality=new.summary(),combined_quality=combined.summary(),
        rank_gain=combined.rank-base.rank,old_kernel=kernel,kernel=combined.kernel(),old_kernel_syndromes=syndromes,
        nonzero_old_kernel_syndromes=sum(any(v) for v in syndromes),norm_completed_witnesses=sum(result['rows'][i]['norm_completed'] for i in indices),complete=True)
