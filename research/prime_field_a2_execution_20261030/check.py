"""Independent norm/branch/point/rank replay, without producer imports."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('_a2_old_reference',ROOT/'research/prime_field_b2_execution_20261030/check.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
from independent import add,multiply,convolution,evaluate,vandermonde,verify_fixture,dense_rank,verify_row as verify_old_row
from check_inputs import public_projection

LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',B='residual_neither_smooth_nor_norm_cancelling',A='canonical_alias',**{'+':'accepted'})

class Reference(old.Reference):
    def __init__(self,cell):
        super().__init__(cell['fixture'],0,list(range(len(cell['fixture']['factor_base']))))
        self.base_by_x={a['point'][0]:(j,tuple(a['point'])) for j,a in enumerate(self.fixture['factor_base'])}

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
        images=[(x*x%self.p,evaluate(self.p,v,x)) for x in roots]
        smooth=all(point[0] in self.base_by_x for point in images)
        cancelled=images[0][0]==images[1][0] and (images[0][1]+images[1][1])%self.p==0
        if not smooth and not cancelled:return 'B',key,None
        coefficients=[0]*len(self.active)
        for j,op in zip(triple,options):coefficients[j]+=(-1 if op&1 else 1)
        if smooth:
            for point in images:
                j,atom=self.base_by_x[point[0]]
                if point==atom:coefficients[j]+=1
                elif point==(atom[0],-atom[1]%self.p):coefficients[j]-=1
                else:raise ValueError('independent base orientation differs')
        row=dict(schema='prym-norm-completed-row/v1',curve_uid=self.fixture['uid'],source_scalar=scalar,
            coefficients=[c%self.fixture['r'] for c in coefficients],residual_E_images=[list(point) for point in images],norm_completed=not smooth,
            constraints=[list(point) for point in points],base_labels=[[j,-1 if op&1 else 1,op] for j,op in zip(triple,options)],
            v_coefficients=v,residual_coefficients=quotient,residual_roots=roots,pole_orders_at_infinity=[3,3],
            source_locator='fixed cubic with smooth or cancelling residual E images; no outside unknowns')
        return '+',key,row


def verify_row(cell,row,reference=None):
    reference=Reference(cell) if reference is None else reference;f=cell['fixture'];p=f['p'];a=f['a']
    labels=row['base_labels'];triple=tuple(v[0] for v in labels);options=tuple(v[2] for v in labels)
    if type(row['source_scalar']) is not int or not 0<row['source_scalar']<f['r']:raise ValueError('invalid public source scalar')
    if len(labels)!=3 or tuple(sorted(set(triple)))!=triple or any(j not in range(len(f['factor_base'])) for j in triple) or any(op not in range(4) for op in options):raise ValueError('invalid constraint labels')
    status,key,expected=reference.outcome(row['source_scalar'],triple,options,set())
    if status!='+' or row!=expected:raise ValueError('partial principal-divisor witness differs')
    total=None
    for c,atom in zip(row['coefficients'],f['factor_base'],strict=True):total=add(p,0,a,total,multiply(p,0,a,c,tuple(atom['point'])))
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


def check_arms(cell,result):
    f=cell['fixture'];r=f['r'];projection=result['projection'];old_quality=old.quality(cell['preprocessing_rows'],projection,r)
    def kernel_check(vectors,rows,columns,rank):
        matrix=[old.project(row,projection,r)[0] for row in rows]
        if len(vectors)!=columns-rank or any(len(k)!=columns for k in vectors) or dense_rank(vectors,r)!=len(vectors) or any(sum(x*y for x,y in zip(k,row))%r for k in vectors for row in matrix):
            raise ValueError('incomplete or false right kernel')
    summaries=[]
    for arm,name in zip(result['arms'],('smooth','norm_completed'),strict=True):
        indices=[i for i,row in enumerate(result['rows']) if name=='norm_completed' or not row['norm_completed']];rows=[result['rows'][i] for i in indices]
        combined=cell['preprocessing_rows']+rows;quality=old.quality(combined,projection,r);new_quality=old.quality(rows,projection,r)
        gain=quality['rank']-old_quality['rank'];norm_rows=sum(row['norm_completed'] for row in rows)
        if any(arm.get(k)!=v for k,v in dict(arm=name,row_indices=indices,preprocessing_quality=old_quality,new_quality=new_quality,combined_quality=quality,rank_gain=gain,norm_completed_witnesses=norm_rows,complete=True).items()):
            raise ValueError('norm arm/affine rank metadata differs')
        kernel_check(arm['old_kernel'],cell['preprocessing_rows'],projection['U'],old_quality['rank']);kernel_check(arm['kernel'],combined,projection['U'],quality['rank'])
        syndromes=[[sum(a*b for a,b in zip(old.project(row,projection,r)[0],k))%r for k in arm['old_kernel']] for row in rows]
        if arm['old_kernel_syndromes']!=syndromes or arm['nonzero_old_kernel_syndromes']!=sum(any(v) for v in syndromes):raise ValueError('norm old-kernel action differs')
        summaries.append(dict(arm=name,rank_gain=gain,combined_rank=quality['rank'],base_rank=old_quality['rank'],norm_completed_witnesses=norm_rows))
    return summaries


def check(cell,result):
    f=cell['fixture'];verify_fixture(f);reference=Reference(cell);projection=public_projection(f,cell['source_order'])
    if result['projection']!=projection:raise ValueError('norm public projection differs')
    for row in cell['preprocessing_rows']:verify_old_row(f,row)
    seen=set();rows=[];counts=Counter();digest=sha256();attempts=0;blocks=[]
    for scalar in cell['source_order']:
        statuses=[];source_digest=sha256()
        for triple in combinations(range(len(f['factor_base'])),3):
            for options in product(range(4),repeat=3):
                attempts+=1;status,identity,row=reference.outcome(scalar,triple,options,seen);reason=LEGEND[status];counts[reason]+=1;statuses.append(status)
                if row is not None:verify_row(cell,row,reference);rows.append(row)
                encoded=json.dumps([scalar,list(triple),list(options),identity,reason],separators=(',',':')).encode()+b'\n';digest.update(encoded);source_digest.update(encoded)
        blocks.append(dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest()))
    if any(result.get(k)!=v for k,v in dict(schema='prym-norm-completion/v1',curve_uid=f['uid'],source_order=cell['source_order'],complete=True,attempts=attempts,statuses=dict(counts),status_legend=LEGEND,status_blocks=blocks,branch_sha256=digest.hexdigest(),rows=rows).items()):
        raise ValueError('complete norm branch replay differs')
    return dict(checked=True,complete_branch_replay=True,attempts_replayed=attempts,rows_verified=len(rows),arms=check_arms(cell,result),
        scope='Separate complete branch/arithmetic/rank implementation check, not independent staffed scientific review or counter audit.')
