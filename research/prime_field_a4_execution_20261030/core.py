"""Prospective holdout generation and target recovery, on public synthetic curves."""
from collections import defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter, process_time

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0,str(OLD))
from fixtures import describe, attach_ec1
from arithmetic import Field
spec=importlib.util.spec_from_file_location('_holdout_direct',ROOT/'research/prime_field_a3_execution_20261030/core.py')
direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
PARAMETERS={'prefixes':[0,16,64],'max_retained_rows':2048,'max_pair_entries':4096,'generation_after_admission':True}
_NATIVE_CAPABILITY=object()


def code(value): return json.dumps(value,sort_keys=True,separators=(',',':'))
def hashed(*values): return sha256('|'.join(str(v) for v in values).encode()).hexdigest()


def generate(rules,event,*,capability=None):
    if capability is not _NATIVE_CAPABILITY and not (rules.get('software_control') is True and all(f['p']<=211 for f in rules['fields'])):
        raise ValueError('holdout generation requires native admission')
    cells=[];trace=[];used=set();wall,cpu=perf_counter(),process_time()
    for field in rules['fields']:
        p=field['p']
        for index in range(rules['curves_per_field']):
            for counter in range(rules['maximum_curve_candidates']):
                b=1+int(hashed(rules['domain'],'curve',p,index,counter),16)%(p-1)
                fixture,trial=describe(p,rules['a'],b,field['base_size'])
                if (p,b) in used: fixture=None;trial={**trial,'reason':'previous_selected_curve'}
                if fixture is not None and fixture['r']==p: fixture=None;trial={**trial,'reason':'anomalous_order_excluded'}
                record=dict(p=p,curve_index=index,counter=counter,b=b,**trial);trace.append(record);event(dict(kind='curve_candidate',**record))
                if fixture is None: continue
                fixture=attach_ec1(fixture);used.add((p,b));uid=fixture['ec1']['curve_uid']
                order=sorted(range(1,rules['sources']+1),key=lambda s:hashed(rules['domain'],'source',uid,s))
                cell=dict(id='p'+str(p)+'-i'+str(index),fixture=fixture,source_order=order,preprocessing_rows=[],archived_norm_rows=[])
                cells.append(cell);event(dict(kind='curve_selected',cell=cell));break
            else: raise ValueError('curve candidate gate exhausted; retain prefix, no replacement field')
    return dict(schema='holdout-generated-fixtures/v1',cells=cells,search_trace=trace,complete=True,
                generation_diagnostics=dict(wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False),
                cost_scope='Retained candidate point-test counts and selected fixture field calls; generation clocks diagnostic, not complete operation model.')


class CertifiedSystem:
    """Metered sparse affine elimination with carried original-row certificates."""
    def __init__(self,width,meter):
        self.width=width;self.meter=meter;self.f=meter.ring;self.rows=[];self.rhs=[];self.pivots={}

    def reduce(self,row,rhs,weights):
        f=self.f
        for pivot,(old,value,certificate) in sorted(self.pivots.items()):
            scale=row.get(pivot,0)
            if not scale: continue
            for j,x in old.items():
                new=f.sub(row.get(j,0),f.mul(scale,x))
                if new: row[j]=new
                else: row.pop(j,None)
            rhs=f.sub(rhs,f.mul(scale,value))
            for j,x in certificate.items():
                new=f.sub(weights.get(j,0),f.mul(scale,x))
                if new: weights[j]=new
                else: weights.pop(j,None)
        return row,rhs,weights

    def add(self,vector,rhs):
        if len(vector)!=self.width: raise ValueError('affine width mismatch')
        row={j:x%self.f.p for j,x in enumerate(vector) if x%self.f.p};index=len(self.rows)
        reduced,value,weights=self.reduce(dict(row),rhs%self.f.p,{index:1})
        if not reduced and value: raise ValueError('inconsistent affine system')
        if reduced:
            pivot=min(reduced);inverse=self.f.inv(reduced[pivot])
            self.pivots[pivot]=({j:self.f.mul(x,inverse) for j,x in reduced.items()},self.f.mul(value,inverse),
                                {j:self.f.mul(x,inverse) for j,x in weights.items()})
        self.rows.append([row.get(j,0) for j in range(self.width)]);self.rhs.append(rhs%self.f.p)
        self.meter.other['affine_rows_inserted']+=1

    def kernel(self):
        result=[];f=self.f
        for free in range(self.width):
            if free in self.pivots: continue
            vector=[0]*self.width;vector[free]=1
            for pivot,(row,_,_) in sorted(self.pivots.items(),reverse=True):
                value=0
                for j,x in row.items():
                    if j!=pivot: value=f.add(value,f.mul(x,vector[j]))
                vector[pivot]=f.sub(0,value)
            result.append(vector)
        return result

    def identify(self,vector,kernel):
        f=self.f;syndrome=[]
        for k in kernel:
            value=0
            for x,y in zip(vector,k): value=f.add(value,f.mul(x,y))
            syndrome.append(value)
        row={j:x%f.p for j,x in enumerate(vector) if x%f.p};remaining,value,weights=self.reduce(row,0,{})
        if remaining: return dict(identifiable=False,value=None,row_weights=None,syndrome=syndrome)
        return dict(identifiable=True,value=f.sub(0,value),row_weights=[f.sub(0,weights.get(i,0)) for i in range(len(self.rows))],syndrome=syndrome)

    def summary(self,kernel): return dict(rows=len(self.rows),columns=self.width,rank=len(self.pivots),nullity=self.width-len(self.pivots),kernel=kernel)


def targets(cell,rules,meter,event):
    f=cell['fixture'];p=f['p'];uid=f['ec1']['curve_uid'];used=set();values=[];trace=[]
    for index in range(rules['targets']):
        for counter in range(rules['maximum_target_candidates']):
            x=int(hashed(rules['domain'],'target',uid,index,counter),16)%p;y=meter.f.sqrt(meter.e.rhs(x))
            point=None if y is None else (x,y);reason='not_rational' if y is None else 'duplicate_target' if point in used else 'selected'
            record=dict(target_index=index,counter=counter,x=x,y=y,reason=reason);trace.append(record);event(dict(kind='target_candidate',**record))
            if reason!='selected': continue
            used.add(point);values.append(dict(index=index,point=list(point)));break
        else: raise ValueError('target candidate gate exhausted; prefix retained, no redraw domain')
    return dict(targets=values,search_trace=trace)


def target_collection(cell,rules,result,meter,event):
    n=len(cell['fixture']['factor_base']);r=cell['fixture']['r'];pairs=result['pair_entries'];table=defaultdict(list)
    for index,pair in enumerate(pairs): table[None if pair['point'] is None else tuple(pair['point'])].append(index)
    meter.other['reused_pair_entries']+=len(pairs)
    signed={(j,s):tuple(a['point']) if s==1 else meter.neg(tuple(a['point'])) for j,a in enumerate(cell['fixture']['factor_base']) for s in (1,-1)}
    rows=[];blocks=[];digest=sha256();attempts=0
    for target in result['target_generation']['targets']:
        records=[];Q=tuple(target['point'])
        for third in range(n):
            for sign in (1,-1):
                attempts+=1;meter.other['target_queries']+=1;wanted=meter.e.add(Q,meter.neg(signed[third,sign]));bucket=table.get(wanted,[])
                meter.other['target_table_lookups']+=1;accepted=[]
                for index in bucket:
                    meter.other['target_bucket_entries_inspected']+=1;pair=pairs[index]
                    if pair['indices'][1]>=third: continue
                    accepted.append(index);triple=pair['indices']+[third];signs=pair['signs']+[sign]
                    row=direct.make_row(cell['fixture'],0,triple,signs);row.update(schema='holdout-target-row/v1',target_index=target['index'],target_point=target['point'])
                    event(dict(kind='target_accepted',row=row));rows.append(row)
                    if len(rows)>rules['max_retained_rows']: raise ValueError('target row size gate exceeded; prefix retained')
                record=dict(third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=list(bucket),accepted=accepted)
                records.append(record);digest.update((code([target['index'],record])+'\n').encode());meter.other['target_sha256_updates']+=1
        block=dict(target_index=target['index'],queries=records,attempts=attempts);blocks.append(block);event(dict(kind='target_complete',**block))
    rows.sort(key=lambda row:(row['target_index'],tuple(row['triple']),tuple(row['signs'])))
    return dict(rows=rows,status_blocks=blocks,attempts=attempts,branch_sha256=digest.hexdigest())


def collisions(cell,rules,result,meter):
    f=cell['fixture'];P=tuple(f['P']);known={};base={}
    for scalar in cell['source_order']:
        point=meter.e.mul(scalar,P);known[point]=scalar;known[meter.neg(point)]=(-scalar)%f['r']
    for j,atom in enumerate(f['factor_base']):
        q=tuple(atom['point']);base[q]=[j,1];base[meter.neg(q)]=[j,-1]
    records=[]
    for target in result['target_generation']['targets']:
        Q=tuple(target['point']);matches=[]
        for multiple in range(1,rules['collision_multipliers']+1):
            point=meter.e.mul(multiple,Q);meter.other['public_multiple_lookups']+=1
            if point in known: matches.append(dict(multiplier=multiple,public_source_scalar=known[point]))
        records.append(dict(target_index=target['index'],direct_public_scalar=known.get(Q),signed_base_atom=base.get(Q),bounded_multiple_matches=matches))
    return records


def collect(cell,rules,event,*,capability=None):
    if capability is not _NATIVE_CAPABILITY and not (cell['fixture'].get('software_control') is True and cell['fixture']['p']<=211):
        raise ValueError('holdout collection requires native admission')
    result,meter=direct.collect(cell,'pair_table',event,capability=direct._NATIVE_CAPABILITY)
    result['target_generation']=meter.stage('target_generation',lambda:targets(cell,rules,meter,event))
    result['target_collection']=meter.stage('target_queries_and_extraction',lambda:target_collection(cell,rules,result,meter,event))
    def certify():
        for row in result['target_collection']['rows']:
            total=None
            for j,s in zip(row['triple'],row['signs']):
                point=tuple(cell['fixture']['factor_base'][j]['point']);total=meter.e.add(total,point if s==1 else meter.neg(point))
            if not meter.equal(total,tuple(row['target_point'])): raise ValueError('target point equation fails')
            meter.other['target_certificates']+=1
    meter.stage('target_certification',certify)
    result['collision_diagnostics']=meter.stage('public_collision_diagnostics',lambda:collisions(cell,rules,result,meter))
    result['holdout_collection_phases']=list(meter.phases);result['holdout_collection_counters']=meter.counters();result['prefixes']=[]
    return result,meter


def prefix_analysis(cell,rules,result,meter,count):
    start=len(meter.phases);projection=result['projection'];width=projection['U'];r=cell['fixture']['r'];target_count=rules['targets']
    indices=[i for i,row in enumerate(result['rows']) if row['source_scalar'] in cell['source_order'][:count]]
    source_rows=[result['rows'][i] for i in indices];target_rows=result['target_collection']['rows']
    projected_source=meter.stage('prefix'+str(count)+'_source_projection',lambda:[direct.project(row,projection,meter) for row in source_rows])
    projected_target=meter.stage('prefix'+str(count)+'_target_projection',lambda:[direct.project(row,projection,meter) for row in target_rows])
    system=CertifiedSystem(width,meter)
    meter.stage('prefix'+str(count)+'_base_elimination',lambda:[system.add(v,b) for v,b in projected_source])
    kernel=meter.stage('prefix'+str(count)+'_base_kernel',system.kernel)
    equations=meter.stage('prefix'+str(count)+'_normalization',lambda:direct.normalize(projected_source,meter))
    def singles():
        values=[]
        for index,(row,(vector,offset)) in enumerate(zip(target_rows,projected_target,strict=True)):
            identified=system.identify(vector,kernel);scalar=None
            if identified['identifiable']:
                scalar=meter.ring.sub(identified['value'],offset)
                if not meter.equal(meter.e.mul(scalar,tuple(cell['fixture']['P'])),tuple(row['target_point'])): raise ValueError('single target recovery public verification failed')
            values.append(dict(target_row_index=index,target_index=row['target_index'],offset=offset,**identified,scalar=scalar))
        return values
    single=meter.stage('prefix'+str(count)+'_single_recovery',singles)
    joint=CertifiedSystem(width+target_count,meter)
    def joint_insert():
        for v,b in projected_source: joint.add(v+[0]*target_count,b)
        for row,(v,b) in zip(target_rows,projected_target,strict=True):
            target=[0]*target_count;target[row['target_index']]=r-1;joint.add(v+target,b)
    meter.stage('prefix'+str(count)+'_joint_elimination',joint_insert)
    joint_kernel=meter.stage('prefix'+str(count)+'_joint_kernel',joint.kernel)
    def combined_recoveries():
        values=[]
        for target in result['target_generation']['targets']:
            unit=[0]*(width+target_count);unit[width+target['index']]=1;identified=joint.identify(unit,joint_kernel)
            if identified['identifiable'] and not meter.equal(meter.e.mul(identified['value'],tuple(cell['fixture']['P'])),tuple(target['point'])): raise ValueError('joint target recovery public verification failed')
            values.append(dict(target_index=target['index'],**identified,scalar=identified['value']))
        return values
    combined=meter.stage('prefix'+str(count)+'_joint_recovery',combined_recoveries)
    outside_rank=len({row['target_index'] for row in target_rows});base_rank_after=len(joint.pivots)-outside_rank
    return dict(prefix=count,source_row_indices=indices,base=system.summary(kernel),distinct_equations=len(equations),
                singles=single,joint=joint.summary(joint_kernel),joint_recoveries=combined,outside_target_rank=outside_rank,
                base_rank_after_target_cancellation=base_rank_after,target_base_rank_gain=base_rank_after-len(system.pivots),
                single_identified_targets=sorted({v['target_index'] for v in single if v['identifiable']}),
                joint_identified_targets=[v['target_index'] for v in combined if v['identifiable']],
                phases=meter.phases[start:],cumulative_counters=meter.counters())
