"""Checked shifted-subset cubic collection on the unchanged elliptic base."""
from collections import Counter
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0,str(OLD))
from relations import Context,uid
from arithmetic import Elliptic,interpolate,padd,pdiv,peval,pmul,quadratic_roots
from independent import verify_fixture,verify_row as verify_old_row
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
from collect_width import public_projection,project
from crypto_autoresearcher.index_calculus.cover_frames import ShiftedCover
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations

PARAMETERS={'arms':['baseline','shifted'],'complete_zero':True,'subset_policy':'constraints_and_residual'}
_NATIVE_CAPABILITY=object()
LEGEND=dict(S='source_no_rational_lift',D='duplicate_interpolation_x',P='exceptional_pole_order',
            R='residual_not_two_distinct_rational_roots',X='intersection_not_squarefree',
            B='residual_endpoint_outside_active_subset',A='canonical_alias',**{'+':'accepted'})


class ShiftedContext(Context):
    def __init__(self,fixture,h,active_atoms):
        super().__init__(fixture)
        self.h=h
        if type(h) is not int or not 0<=h<self.p:raise ValueError('canonical field shift required')
        if active_atoms!=sorted(set(active_atoms)) or len(active_atoms)<3 or any(type(j) is not int or not 0<=j<len(self.base) for j in active_atoms):
            raise ValueError('ordered distinct active native atom indices required')
        self.active=list(active_atoms);self.active_set=set(self.active)
        self.frame=ShiftedCover(self.p,self.a,self.b,h)
        self.F=list(self.frame.polynomial)
        self.aux=Elliptic(self.f,*self.frame.auxiliary_coefficients)
        self.lifts=[None]*len(self.base)
        for j in self.active:
            u,y=self.base[j];x=self.f.sqrt(self.f.sub(u,h))
            if x is None:raise ValueError('active atom has no rational cover lift')
            self.lifts[j]=(x,y)

    def lift_source(self,scalar,source=None):
        source=self.P if source is None else source
        key=(scalar,source)
        if key in self.source_cache:
            self.f.counts['source_cache_hits']+=1;return self.source_cache[key]
        self.f.counts['source_cache_misses']+=1
        point=self.e.neg(self.e.mul(scalar,source))
        root=None if point is None else self.f.sqrt(self.f.sub(point[0],self.h))
        value=None if root is None else (root,point[1])
        self.source_cache[key]=value;return value

    def descriptor(self,scalar,triple,options):
        if len(triple)!=3 or len(set(triple))!=3 or not set(triple)<=self.active_set or len(options)!=3 or any(type(o) is not int or o not in range(4) for o in options):
            raise ValueError('three active atoms and sign/deck options required')
        first=self.lift_source(scalar)
        if first is None:return None,LEGEND['S']
        points,labels=[first],[]
        for j,option in zip(triple,options):
            x,y=self.lifts[j];sign=-1 if option&1 else 1
            points.append(((-x if option&2 else x)%self.p,sign*y%self.p));labels.append((j,sign,option))
        if len({x for x,y in points})!=4:return None,LEGEND['D']
        return dict(source_scalar=scalar,points=points,labels=labels),None

    def canonical_identity(self,descriptor):
        value=super().canonical_identity(descriptor)
        return dict(value,cover_shift=self.h,active_atoms=self.active)

    def pi2(self,point):
        # Not used as a selection filter. Retain the corrected auxiliary map.
        return self.frame.auxiliary_image(point)

    def construct(self,descriptor):
        f=self.f;points=descriptor['points'];v=interpolate(f,points)
        intersection=padd(f,pmul(f,v,v),self.F,sign=-1)
        if len(intersection)!=7:return None,LEGEND['P']
        known=[1]
        for x,y in points:known=pmul(f,known,[-x%self.p,1])
        residual,remainder=pdiv(f,intersection,known)
        if remainder!=[0]:raise ArithmeticError('shifted interpolation did not divide intersection')
        roots=quadratic_roots(f,residual)
        if roots is None or len(roots)!=2:return None,LEGEND['R']
        if set(roots)&{x for x,y in points}:return None,LEGEND['X']
        coefficients=[0]*len(self.base)
        for j,sign,option in descriptor['labels']:coefficients[j]+=sign
        for x in roots:
            y=peval(f,v,x);u=f.add(f.mul(x,x),self.h);j=self.by_x.get(u)
            if j not in self.active_set:return None,LEGEND['B']
            if y==self.base[j][1]:coefficients[j]+=1
            elif y==-self.base[j][1]%self.p:coefficients[j]-=1
            else:raise ArithmeticError('shifted endpoint orientation mismatch')
        return dict(schema='prym-shifted-row/v1',curve_uid=self.fixture['uid'],cover_shift=self.h,
                    active_atoms=self.active,source_scalar=descriptor['source_scalar'],
                    coefficients=[c%self.r for c in coefficients],constraints=[list(p) for p in points],
                    base_labels=[list(t) for t in descriptor['labels']],v_coefficients=v,
                    residual_coefficients=residual,residual_roots=roots,pole_orders_at_infinity=[3,3],
                    source_locator='shifted cubic interpolation and residual quadratic; no post-hoc kernel'),None


def collect(cell,h,arm,event,*,capability=None):
    fixture=cell['fixture']
    if capability is not _NATIVE_CAPABILITY and not (fixture.get('software_control') is True and fixture['p']<=211):
        raise ValueError('scientific shifted collection requires native admission')
    from check import verify_row
    verify_fixture(fixture)
    sources=cell['source_order']
    if len(set(sources))!=len(sources) or any(type(s) is not int or not 0<s<fixture['r'] for s in sources):raise ValueError('invalid public source schedule')
    context=ShiftedContext(fixture,h,cell['active_atoms']);projection=public_projection(context,sources)
    old=AffineRelations(fixture['r'],projection['U']);combined=AffineRelations(fixture['r'],projection['U'])
    new=AffineRelations(fixture['r'],projection['U'])
    for row in cell['preprocessing_rows']:
        verify_old_row(fixture,row)
        vector,rhs=project(row,projection,fixture['r']);old.add(vector,rhs);combined.add(vector,rhs)
    old_kernel=old.kernel();seen=set();rows=[];counts=Counter();digest=sha256()
    attempts=0;blocks=[];progress=[];syndromes=[];codes={v:k for k,v in LEGEND.items()}
    for scalar in sources:
        statuses=[];source_digest=sha256()
        for triple in combinations(context.active,3):
            for options in product(range(4),repeat=3):
                attempts+=1;descriptor,reason=context.descriptor(scalar,triple,options);identity=None
                if descriptor is not None:
                    identity=uid(context.canonical_identity(descriptor))
                    if identity in seen:reason=LEGEND['A']
                    else:
                        seen.add(identity);row,reason=context.construct(descriptor)
                        if row is not None:
                            verify_row(fixture,h,context.active,row)
                            vector,rhs=project(row,projection,fixture['r']);new.add(vector,rhs);combined.add(vector,rhs)
                            syndrome=[sum(a*b for a,b in zip(vector,kernel))%fixture['r'] for kernel in old_kernel]
                            syndromes.append(syndrome);rows.append(row)
                            location=dict(attempt=attempts,row_index=len(rows)-1,new_rank=new.rank,combined_rank=combined.rank)
                            progress.append(location)
                            event(dict(kind='accepted',**location,row=row,old_kernel_syndrome=syndrome,
                                       source_zero=descriptor['points'][0][0]==0,
                                       constraint_zero=any(x==0 for x,y in descriptor['points'][1:])))
                status=reason or 'accepted';counts[status]+=1;statuses.append(codes[status])
                encoded=json.dumps([scalar,list(triple),list(options),identity,status],separators=(',',':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
        block=dict(scalar=scalar,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest())
        blocks.append(block);event(dict(kind='source_complete',**block,accepted=len(rows),new_rank=new.rank,combined_rank=combined.rank,counts=dict(counts)))
    return dict(schema='prym-shifted-subset/v1',cell_id=cell['id'],arm=arm,curve_uid=fixture['uid'],
                cover_shift=h,active_atoms=context.active,source_order=sources,complete=True,attempts=attempts,
                statuses=dict(counts),status_legend=LEGEND,status_blocks=blocks,branch_sha256=digest.hexdigest(),rows=rows,
                new_quality=new.summary(),combined_quality=combined.summary(),preprocessing_quality=old.summary(),
                projection=projection,kernel=combined.kernel(),old_kernel=old_kernel,old_kernel_syndromes=syndromes,
                rank_progress=progress,operation_vector=dict(context.f.counts),
                cost_scope='Producer Field/group counters only; excludes helper primality, coefficient integer work, inline separate row verification, replay, hashes, elimination/serialization/storage and complete S.',
                scientific_promotion=False)
