"""Independent fixture selection, complete sum oracle, queries and target certificates."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/prym_experiment_design_20261019/implementation'))
sys.path.insert(0,str(ROOT/'research/prym_factor_base_width_20261025'))
sys.path.insert(0,str(ROOT/'tools'))
from independent import prime, add, multiply, dense_rank, verify_fixture
from check_inputs import public_projection
from curve_identity import curve_identity


def encoded(v): return json.dumps(v,sort_keys=True,separators=(',',':'))
def hashed(*args): return sha256('|'.join(map(str,args)).encode()).hexdigest()
def row_key(v): return (v['source_scalar'],tuple(v['triple']),tuple(v['signs']))
def target_key(v): return (v['target_index'],tuple(v['triple']),tuple(v['signs']))


def check_generation(rules,generated):
    roots={};used=set();cells=[];trace=[];point_tests=0
    for field in rules['fields']:
        p=field['p'];root={}
        for y in range(p): root.setdefault(y*y%p,y)
        roots[p]=root
        for index in range(rules['curves_per_field']):
            for counter in range(rules['maximum_curve_candidates']):
                b=1+int(hashed(rules['domain'],'curve',p,index,counter),16)%(p-1);a=rules['a'];fixture=None
                if b%p==0 or (4*a*a*a+27*b*b)%p==0: trial=dict(reason='singular_or_zero_B',point_tests=0)
                else:
                    r=p+1+sum(0 if (u:=(x**3+a*x+b)%p)==0 else 1 if u in root else -1 for x in range(p));point_tests+=p
                    trial=dict(reason='composite_order',r=r,point_tests=p)
                    if r>2 and prime(r):
                        P=next((x,root[(x**3+a*x+b)%p]) for x in range(p) if (x**3+a*x+b)%p in root)
                        base=[];seen=set()
                        for x in range(p):
                            u=x*x%p;y=root.get((u**3+a*u+b)%p)
                            if y is None or u in seen: continue
                            seen.add(u);base.append(dict(point=[u,y],lift=[x,y]))
                            if len(base)==field['base_size']: break
                        if len(base)!=field['base_size']: trial.update(reason='insufficient_distinct_factor_base',base_size=len(base))
                        else:
                            fixture=dict(p=p,a=a,b=b,r=r,P=list(P),factor_base=base)
                            trial['reason']='eligible'
                if (p,b) in used: fixture=None;trial['reason']='previous_selected_curve'
                if fixture is not None and fixture['r']==p: fixture=None;trial['reason']='anomalous_order_excluded'
                trace.append(dict(p=p,curve_index=index,counter=counter,b=b,**trial))
                if fixture is None: continue
                actual=generated['cells'][len(cells)];f=actual['fixture']
                if any(f[k]!=v for k,v in fixture.items()): raise ValueError('holdout selection/base differs from independent construction')
                uid=sha256(encoded(fixture).encode()).hexdigest()
                if f['uid']!=uid: raise ValueError('fixture UID differs')
                field_data=dict(characteristic=p,degree=1,representation='Z/pZ',element_encoding='canonical integers 0..p-1')
                curve=dict(model='short_weierstrass',a4=a,a6=b,subgroup_order=f['r'],cofactor=1,generator=f['P'],target_group='E(Fp)')
                identity=curve_identity(field_data,curve,'prymtoy');curve['curve_id']=identity['curve_id']
                if f['ec1']!=dict(field=field_data,curve=curve,**identity): raise ValueError('canonical EC1 identity differs')
                order=sorted(range(1,rules['sources']+1),key=lambda s:hashed(rules['domain'],'source',identity['curve_uid'],s))
                if actual['id']!='p'+str(p)+'-i'+str(index) or actual['source_order']!=order or actual['preprocessing_rows'] or actual['archived_norm_rows']:
                    raise ValueError('source ordering or original empty preprocessing differs')
                verify_fixture(f);cells.append(actual);used.add((p,b));break
            else: raise ValueError('independent candidate gate exhausted')
    if generated.get('complete')is not True or generated['search_trace']!=trace or len(generated['cells'])!=len(cells): raise ValueError('full curve selection trace differs')
    return dict(checked=True,curves=len(cells),candidate_records=len(trace),order_point_tests=point_tests,scope='Independent complete eligibility/base construction and EC1 metadata; producer field-operation counts not audited.')


def project(row,projection,r):
    vector=[0]*projection['U'];rhs=row['source_scalar']
    for c,m in zip(row['coefficients'],projection['native_to_projected'],strict=True):
        if m[0]=='known': rhs-=c*m[1]
        elif m[0]=='unknown': vector[m[1]]+=c*m[2]
    return [v%r for v in vector],rhs%r


def check_system(summary,rows,values,r):
    width=summary['columns'];rank=dense_rank(rows,r);kernel=summary['kernel']
    if (summary['rank']!=rank or summary['rows']!=len(rows) or summary['nullity']!=width-rank or
        dense_rank([v+[b] for v,b in zip(rows,values)],r)!=rank): raise ValueError('system affine rank/consistency differs')
    if (len(kernel)!=width-rank or any(len(k)!=width for k in kernel) or dense_rank(kernel,r)!=len(kernel) or
        any(sum(x*y for x,y in zip(v,k))%r for v in rows for k in kernel)): raise ValueError('incomplete or false kernel')


def check_identified(record,vector,rows,values,kernel,r):
    syndrome=[sum(x*y for x,y in zip(vector,k))%r for k in kernel];identifiable=not any(syndrome)
    if record['identifiable']is not identifiable or record['syndrome']!=syndrome: raise ValueError('identifiability/kernel criterion differs')
    if not identifiable:
        if record['row_weights']is not None or record['value']is not None or record['scalar']is not None: raise ValueError('unidentifiable target has fabricated value')
        return
    weights=record['row_weights']
    if len(weights)!=len(rows) or any(sum(w*row[j] for w,row in zip(weights,rows))%r!=vector[j] for j in range(len(vector))):
        raise ValueError('false target row-weight certificate')
    if record['value']!=sum(w*b for w,b in zip(weights,values))%r: raise ValueError('false target certificate RHS')


def check_prefix(cell,rules,result,record):
    f=cell['fixture'];r=f['r'];p=f['p'];projection=result['projection'];width=projection['U'];count=record['prefix'];targets=rules['targets']
    if count not in rules['prefixes']: raise ValueError('unplanned prefix')
    indices=[i for i,row in enumerate(result['rows']) if row['source_scalar'] in cell['source_order'][:count]]
    if record['source_row_indices']!=indices: raise ValueError('wrong source prefix')
    source=[project(result['rows'][i],projection,r) for i in indices];natural=[project(row,projection,r) for row in result['target_collection']['rows']]
    M=[v for v,b in source];rhs=[b for v,b in source]
    if record['base']['columns']!=width: raise ValueError('base unknown width changed')
    check_system(record['base'],M,rhs,r)
    equations=set()
    for v,b in source:
        affine=v+[b];first=next((x for x in affine if x),None);equations.add(tuple(x*pow(first,-1,r)%r for x in affine) if first else tuple(affine))
    if record['distinct_equations']!=len(equations) or len(record['singles'])!=len(natural): raise ValueError('prefix equation or single count differs')
    for index,(row,(vector,offset),single) in enumerate(zip(result['target_collection']['rows'],natural,record['singles'],strict=True)):
        if single['target_row_index']!=index or single['target_index']!=row['target_index'] or single['offset']!=offset: raise ValueError('wrong natural target row')
        check_identified(single,vector,M,rhs,record['base']['kernel'],r)
        if single['identifiable']:
            scalar=(single['value']-offset)%r
            if single['scalar']!=scalar or multiply(p,0,f['a'],scalar,tuple(f['P']))!=tuple(row['target_point']): raise ValueError('single recovery public equation differs')
    joint=[v+[0]*targets for v in M];joint_rhs=list(rhs)
    for row,(v,b) in zip(result['target_collection']['rows'],natural,strict=True):
        suffix=[0]*targets;suffix[row['target_index']]=r-1;joint.append(v+suffix);joint_rhs.append(b)
    if record['joint']['columns']!=width+targets: raise ValueError('joint target width changed')
    check_system(record['joint'],joint,joint_rhs,r)
    if len(record['joint_recoveries'])!=targets: raise ValueError('missing joint target record')
    for target,identified in zip(result['target_generation']['targets'],record['joint_recoveries'],strict=True):
        unit=[0]*(width+targets);unit[width+target['index']]=1
        if identified['target_index']!=target['index']: raise ValueError('joint target identity differs')
        check_identified(identified,unit,joint,joint_rhs,record['joint']['kernel'],r)
        if identified['identifiable'] and (identified['scalar']!=identified['value'] or multiply(p,0,f['a'],identified['value'],tuple(f['P']))!=tuple(target['point'])):
            raise ValueError('joint recovery public equation differs')
    outside=dense_rank([v[width:] for v in joint],r);base_rank_after=record['joint']['rank']-outside
    singles=sorted({s['target_index'] for s in record['singles'] if s['identifiable']});joint_ids=[s['target_index'] for s in record['joint_recoveries'] if s['identifiable']]
    if (record['outside_target_rank']!=outside or record['base_rank_after_target_cancellation']!=base_rank_after or record['target_base_rank_gain']!=base_rank_after-record['base']['rank'] or
        record['single_identified_targets']!=singles or record['joint_identified_targets']!=joint_ids): raise ValueError('outside-adjusted base information or recovery summary differs')
    return dict(prefix=count,base_columns=width,base_rank=record['base']['rank'],base_nullity=width-record['base']['rank'],source_rows=len(source),distinct_equations=len(equations),
                single_targets=len(singles),joint_targets=len(joint_ids),joint_rank=record['joint']['rank'],base_rank_after_target_cancellation=base_rank_after,
                early_single_targets=len(singles) if record['base']['rank']<width else 0,early_joint_targets=len(joint_ids) if base_rank_after<width else 0)


def check(cell,rules,result):
    f=cell['fixture'];p,r=f['p'],f['r'];n=len(f['factor_base']);verify_fixture(f);root={}
    for y in range(p): root.setdefault(y*y%p,y)
    trace=[];expected_targets=[];used=set()
    for index in range(rules['targets']):
        for counter in range(rules['maximum_target_candidates']):
            x=int(hashed(rules['domain'],'target',f['ec1']['curve_uid'],index,counter),16)%p;y=root.get((x**3+f['a']*x+f['b'])%p)
            point=None if y is None else (x,y);reason='not_rational' if y is None else 'duplicate_target' if point in used else 'selected'
            trace.append(dict(target_index=index,counter=counter,x=x,y=y,reason=reason))
            if reason=='selected': used.add(point);expected_targets.append(dict(index=index,point=list(point)));break
        else: raise ValueError('reference target candidate gate exhausted')
    if result['target_generation']!=dict(targets=expected_targets,search_trace=trace): raise ValueError('independent target draw differs')
    sources={s:multiply(p,0,f['a'],s,tuple(f['P'])) for s in cell['source_order']};base=[tuple(a['point']) for a in f['factor_base']]
    signed={(j,s):(q[0],s*q[1]%p) for j,q in enumerate(base) for s in (1,-1)};plus=lambda x,y:add(p,0,f['a'],x,y)
    wanted=set(sources.values())|{tuple(q['point']) for q in expected_targets};oracle=defaultdict(list);digest=sha256();count=0
    for triple in combinations(range(n),3):
        for signs in product((1,-1),repeat=3):
            count+=1;total=plus(plus(signed[triple[0],signs[0]],signed[triple[1],signs[1]]),signed[triple[2],signs[2]])
            digest.update((encoded([triple,signs,total])+'\n').encode())
            if total in wanted: oracle[total].append((triple,signs))
    def row(scalar,triple,signs):
        coefficients=[0]*n
        for j,s in zip(triple,signs): coefficients[j]=s%r
        return dict(schema='direct-three-sum-row/v1',curve_uid=f['uid'],source_scalar=scalar,triple=list(triple),signs=list(signs),coefficients=coefficients)
    source_rows=sorted([row(s,triple,signs) for s,Q in sources.items() for triple,signs in oracle[Q]],key=row_key);target_rows=[]
    for q in expected_targets:
        for triple,signs in oracle[tuple(q['point'])]:
            v=row(0,triple,signs);v.update(schema='holdout-target-row/v1',target_index=q['index'],target_point=q['point']);target_rows.append(v)
    target_rows.sort(key=target_key)
    if result['rows']!=source_rows or result['target_collection']['rows']!=target_rows: raise ValueError('complete independent source/target sum census differs')
    pairs=[];table=defaultdict(list)
    for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
        point=plus(signed[j,signs[0]],signed[k,signs[1]]);pairs.append(dict(indices=[j,k],signs=list(signs),point=None if point is None else list(point)));table[point].append(len(pairs)-1)
    if result['pair_entries']!=pairs: raise ValueError('pair table entry differs')
    def queries(Q):
        records=[]
        for third,sign in product(range(n),(1,-1)):
            q=signed[third,sign];key=plus(Q,(q[0],-q[1]%p));bucket=table.get(key,[])
            records.append(dict(third=third,sign=sign,wanted=None if key is None else list(key),bucket=list(bucket),accepted=[i for i in bucket if pairs[i]['indices'][1]<third]))
        return records
    blocks=[];branch=sha256();attempts=0
    for s in cell['source_order']:
        records=queries(sources[s]);attempts+=len(records);d=sha256()
        for record in records:
            value=(encoded([s,record])+'\n').encode();branch.update(value);d.update(value)
        blocks.append(dict(scalar=s,attempts=attempts,queries=records,branch_sha256=d.hexdigest()))
    if result['status_blocks']!=blocks or result['attempts']!=attempts or result['branch_sha256']!=branch.hexdigest(): raise ValueError('source query/bucket replay differs')
    blocks=[];branch=sha256();target_attempts=0
    for q in expected_targets:
        records=queries(tuple(q['point']));target_attempts+=len(records)
        for record in records: branch.update((encoded([q['index'],record])+'\n').encode())
        blocks.append(dict(target_index=q['index'],queries=records,attempts=target_attempts))
    if result['target_collection']['status_blocks']!=blocks or result['target_collection']['attempts']!=target_attempts or result['target_collection']['branch_sha256']!=branch.hexdigest():
        raise ValueError('target query/bucket replay differs')
    projection=public_projection(f,cell['source_order'])
    if result['projection']!=projection: raise ValueError('full64 public projection differs')
    known={};base_lookup={}
    for s,Q in sources.items(): known[Q]=s;known[(Q[0],-Q[1]%p)]=-s%r
    for j,Q in enumerate(base): base_lookup[Q]=[j,1];base_lookup[(Q[0],-Q[1]%p)]=[j,-1]
    diagnostics=[]
    for target in expected_targets:
        Q=tuple(target['point']);matches=[]
        for t in range(1,rules['collision_multipliers']+1):
            point=multiply(p,0,f['a'],t,Q)
            if point in known: matches.append(dict(multiplier=t,public_source_scalar=known[point]))
        diagnostics.append(dict(target_index=target['index'],direct_public_scalar=known.get(Q),signed_base_atom=base_lookup.get(Q),bounded_multiple_matches=matches))
    if result['collision_diagnostics']!=diagnostics: raise ValueError('bounded public collision diagnostics differ')
    if [v['prefix'] for v in result['prefixes']]!=rules['prefixes']: raise ValueError('incomplete prefix panel')
    summaries=[check_prefix(cell,rules,result,v) for v in result['prefixes']];total=Counter()
    phases=result['holdout_collection_phases']+[phase for v in result['prefixes'] for phase in v['phases']]
    if len({v['phase'] for v in phases})!=len(phases): raise ValueError('duplicate cost phases')
    for phase in phases:
        if phase['status']!='complete' or phase['wall_valid']is not False or any(type(v)is not int or v<0 for v in phase['counters'].values()): raise ValueError('invalid cost phase')
        total.update(phase['counters'])
    if dict(total)!=result['total_counters']: raise ValueError('cost counter conservation differs')
    expected_counts={'pair_table_insertions':len(pairs),'queries':attempts,'pair_table_lookups':attempts,
                     'target_queries':target_attempts,'target_table_lookups':target_attempts,
                     'relation_certificates':len(source_rows)}
    if any(total.get(k,0)!=v for k,v in expected_counts.items()): raise ValueError('logical collection counters differ')
    return dict(checked=True,complete_sum_oracle=True,signed_triples_enumerated=count,sum_oracle_sha256=digest.hexdigest(),pair_entries_checked=len(pairs),source_queries_checked=attempts,
                target_queries_checked=target_attempts,source_rows_verified=len(source_rows),target_rows_verified=len(target_rows),prefixes=summaries,
                scope='Independent complete signed-sum/source/target/table/query, eligibility, public equations and dense algebra certificates; not staffed scientific review or producer field-counter audit.')
