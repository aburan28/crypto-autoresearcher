"""Check retained metadata/certificates and export; never generate a curve/point/table."""
import argparse
from collections import Counter
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,digest,specifications,expected_work,write_once


def load(path):
    found=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(found)>1:raise ValueError('ambiguous retained encodings')
    if not found:return None
    with (gzip.open if found[0].suffix=='.gz' else open)(found[0],'rt') as stream:return json.load(stream)


def lines(path):
    found=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(found)>1:raise ValueError('ambiguous retained journal encodings')
    if found:
        with (gzip.open if found[0].suffix=='.gz' else open)(found[0],'rt') as stream:
            for line in stream:
                if line.strip():yield json.loads(line)


def key(row,target=False):return (row['target_index'] if target else row['source_scalar'],tuple(row['triple']),tuple(row['signs']))


def project(row,mapping,r):
    if len(row['coefficients'])!=len(mapping['native_to_projected']):raise ValueError('native projection width differs')
    v=[0]*mapping['U'];b=row['source_scalar']
    for c,m in zip(row['coefficients'],mapping['native_to_projected'],strict=True):
        if m[0]=='known':b-=c*m[1]
        elif m[0]=='unknown':v[m[1]]+=c*m[2]
    return [x%r for x in v],b%r


def phase_sum(phases):
    if len({p['phase'] for p in phases})!=len(phases):raise ValueError('duplicate disjoint phase label')
    total=Counter()
    for p in phases:
        if p['status']!='complete' or p['wall_valid']is not False or min(p['cpu_seconds'],p['wall_seconds'])<0 or any(type(v)is not int or v<0 for v in p['counters'].values()):raise ValueError('invalid diagnostic phase')
        total.update(p['counters'])
    return dict(total)


def certificate(record,vector,rows,rhs,kernel,r):
    syndrome=[sum(x*y for x,y in zip(vector,k))%r for k in kernel]
    if record['syndrome']!=syndrome or record['identifiable']is not (not any(syndrome)):raise ValueError('false kernel identifiability')
    if not record['identifiable']:
        if any(record[k] is not None for k in ('value','row_weights','scalar')):raise ValueError('unidentified value fabricated')
        return
    weights=record['row_weights']
    if len(weights)!=len(rows) or any(sum(w*row[j] for w,row in zip(weights,rows))%r!=vector[j] for j in range(len(vector))):raise ValueError('false row-weight certificate')
    if record['value']!=sum(w*b for w,b in zip(weights,rhs))%r:raise ValueError('false certificate RHS')


def system(summary,rows,rhs,width,r):
    if summary['columns']!=width or summary['rows']!=len(rows) or not 0<=summary['rank']<=width or summary['nullity']!=width-summary['rank']:raise ValueError('system metadata differs')
    kernel=summary['kernel']
    if len(kernel)!=summary['nullity'] or any(len(k)!=width for k in kernel) or any(sum(x*y for x,y in zip(row,k))%r for row in rows for k in kernel):raise ValueError('kernel does not annihilate retained rows')


def prefix_metrics(cell,rules,result,record):
    r=cell['fixture']['r'];width=result['projection']['U'];count=record['prefix'];target_rows=result['target_collection']['rows'];nt=rules['targets']
    indices=[i for i,row in enumerate(result['rows']) if row['source_scalar'] in cell['source_order'][:count]]
    if record['source_row_indices']!=indices:raise ValueError('prefix membership differs')
    source=[project(result['rows'][i],result['projection'],r) for i in indices];natural=[project(row,result['projection'],r) for row in target_rows]
    M=[v for v,b in source];rhs=[b for v,b in source];system(record['base'],M,rhs,width,r)
    equations=set()
    for v,b in source:
        affine=v+[b];first=next((x for x in affine if x),None);equations.add(tuple(x*pow(first,-1,r)%r for x in affine) if first else tuple(affine))
    if record['distinct_equations']!=len(equations) or len(record['singles'])!=len(natural):raise ValueError('affine/source-row count differs')
    for i,(row,(v,b),single) in enumerate(zip(target_rows,natural,record['singles'],strict=True)):
        if single['target_row_index']!=i or single['target_index']!=row['target_index'] or single['offset']!=b:raise ValueError('natural target identity differs')
        certificate(single,v,M,rhs,record['base']['kernel'],r)
        if single['identifiable'] and single['scalar']!=(single['value']-b)%r:raise ValueError('single scalar differs from affine identity')
    J=[v+[0]*nt for v in M];jr=list(rhs)
    for row,(v,b) in zip(target_rows,natural,strict=True):
        suffix=[0]*nt;suffix[row['target_index']]=r-1;J.append(v+suffix);jr.append(b)
    system(record['joint'],J,jr,width+nt,r)
    if len(record['joint_recoveries'])!=nt:raise ValueError('missing joint target records')
    for i,identified in enumerate(record['joint_recoveries']):
        unit=[0]*(width+nt);unit[width+i]=1
        if identified['target_index']!=i:raise ValueError('joint target index differs')
        certificate(identified,unit,J,jr,record['joint']['kernel'],r)
        if identified['identifiable'] and identified['scalar']!=identified['value']:raise ValueError('joint scalar differs')
    singles=sorted({v['target_index'] for v in record['singles'] if v['identifiable']});joint=[v['target_index'] for v in record['joint_recoveries'] if v['identifiable']]
    outside=len({v['target_index'] for v in target_rows});after=record['joint']['rank']-outside
    if record['outside_target_rank']!=outside or record['base_rank_after_target_cancellation']!=after or record['target_base_rank_gain']!=after-record['base']['rank'] or record['single_identified_targets']!=singles or record['joint_identified_targets']!=joint or not 0<=after<=width:raise ValueError('outside-adjusted information differs')
    return dict(source_rows=len(source),target_rows=len(natural),base_columns=width,base_rank_after_target_cancellation=after,single_targets=len(singles),joint_targets=len(joint),early_single_targets=len(singles) if record['base']['nullity'] else 0,early_joint_targets=len(joint) if after<width else 0,accepted_witnesses=len(source),distinct_equations=len(equations),base_rank=record['base']['rank'],base_nullity=record['base']['nullity'],joint_rank=record['joint']['rank'],joint_base_nullity=width-after,target_base_rank_gain=after-record['base']['rank'],single_identified_targets=len(singles),joint_identified_targets=len(joint),joint_recoveries_with_base_uncertainty=len(joint) if after<width else 0,bounded_collision_targets=sum(bool(v['bounded_multiple_matches']) for v in result['collision_diagnostics']))


def check_journal(result,events,cell,rules):
    if sorted([e['row'] for e in events if e.get('kind')=='accepted'],key=key)!=result['rows']:raise ValueError('source accepted journal differs')
    if sorted([e['row'] for e in events if e.get('kind')=='target_accepted'],key=lambda r:key(r,True))!=result['target_collection']['rows']:raise ValueError('target accepted journal differs')
    source=[{k:v for k,v in e.items() if k not in ('kind','arm')} for e in events if e.get('kind')=='source_complete']
    if len(source)!=rules['sources'] or [v['scalar'] for v in source]!=cell['source_order'] or source!=result['status_blocks']:raise ValueError('complete source journal differs')
    target=[{k:v for k,v in e.items() if k!='kind'} for e in events if e.get('kind')=='target_complete']
    if len(target)!=rules['targets'] or [v['target_index'] for v in target]!=list(range(rules['targets'])) or target!=result['target_collection']['status_blocks']:raise ValueError('complete target journal differs')
    pairs=[e for e in events if e.get('kind')=='pair_entry']
    if [e['index'] for e in pairs]!=list(range(len(result['pair_entries']))) or [{k:v for k,v in e.items() if k not in ('kind','arm','index')} for e in pairs]!=result['pair_entries']:raise ValueError('pair-entry journal differs')
    trace=[{k:v for k,v in e.items() if k!='kind'} for e in events if e.get('kind')=='target_candidate']
    if trace!=result['target_generation']['search_trace']:raise ValueError('target recipe journal differs')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args()
    execution=load(args.run/'execution.json');host=load(args.run/'host.json');protocol=load(args.protocol);rules=json.loads(INPUTS.read_text());specs=specifications(rules)
    generated=load(args.run/'raw/generated.json');gencheck=load(args.run/'raw/generation.verification.json');genjournal=list(lines(args.run/'raw/generation.events.jsonl'));outer=list(lines(args.run/'raw/phases.jsonl'))
    if generated is not None:
        if generated.get('schema')!='holdout-generated-fixtures/v1' or generated.get('complete')is not True or generated.get('inputs_sha256')!=digest(INPUTS) or [v['id'] for v in generated['cells']]!=[v['id'] for v in specs]:raise ValueError('generated panel identity differs')
        if [{k:v for k,v in e.items() if k!='kind'} for e in genjournal if e.get('kind')=='curve_candidate']!=generated['search_trace'] or [e['cell'] for e in genjournal if e.get('kind')=='curve_selected']!=generated['cells']:raise ValueError('full generation journal differs')
    if gencheck is not None and (generated is None or gencheck.get('checked')is not True or gencheck.get('curves')!=len(specs) or gencheck.get('candidate_records')!=len(generated['search_trace'])):raise ValueError('generation verification scope differs')
    actual={} if generated is None else {c['id']:c for c in generated['cells']};metrics=[v['id'] for v in protocol['metrics']['primary']];cells=[];checks=[];costs=[]
    for index,spec in enumerate(specs):
        stem=spec['id'];cell=actual.get(stem);result=load(args.run/'raw'/(stem+'.json'));snapshot=load(args.run/'raw'/(stem+'.collection.json'));value=result if result is not None else snapshot;verification=load(args.run/'raw'/(stem+'.verification.json'));events=list(lines(args.run/'raw'/(stem+'.events.jsonl')));work=expected_work(spec,rules)
        if value is not None:
            if cell is None or value.get('cell_id')!=stem or value.get('schema')!='direct-three-sum/v1' or value.get('curve_uid')!=cell['fixture']['uid'] or value.get('arm')!='pair_table' or value.get('inputs_sha256')!=digest(INPUTS) or value.get('complete')is not True or value.get('source_order')!=cell['source_order'] or value.get('attempts')!=work['source_queries'] or value['target_collection']['attempts']!=work['target_queries'] or len(value['pair_entries'])!=work['pair_entries']:raise ValueError('wrong collection scope')
            check_journal(value,events,cell,rules)
            if result is not None and snapshot is not None and {k:v for k,v in result.items() if k not in ('prefixes','total_counters')}!={k:v for k,v in snapshot.items() if k not in ('prefixes','total_counters')}:raise ValueError('final differs from immutable collection')
            if phase_sum(value['holdout_collection_phases'])!=value['holdout_collection_counters']:raise ValueError('collection counter conservation differs')
        prefixes={} if value is None else {p['prefix']:p for p in value['prefixes']};summaries={} if verification is None else {p['prefix']:p for p in verification['prefixes']}
        if result is not None and list(prefixes)!=rules['prefixes']:raise ValueError('incomplete final prefix panel')
        verified=verification is not None and verification.get('checked')is True and verification.get('complete_sum_oracle')is True and gencheck is not None
        if verification is not None and (result is None or list(summaries)!=rules['prefixes'] or any(verification.get(k)!=v for k,v in dict(signed_triples_enumerated=work['oracle_signed_triples'],pair_entries_checked=work['pair_entries'],source_queries_checked=work['source_queries'],target_queries_checked=work['target_queries'],source_rows_verified=len(value['rows']),target_rows_verified=len(value['target_collection']['rows'])).items())):raise ValueError('independent replay work scope differs')
        if result is not None:
            disjoint=value['holdout_collection_phases']+[p for record in value['prefixes'] for p in record['phases']]
            if phase_sum(disjoint)!=value['total_counters']:raise ValueError('total counter conservation differs')
            for n,p in enumerate(value['prefixes']):
                upto=value['holdout_collection_phases']+[q for record in value['prefixes'][:n+1] for q in record['phases']]
                if phase_sum(upto)!=p['cumulative_counters']:raise ValueError('cumulative counters differ')
            costs.append(dict(cell_id=stem,disjoint_phases=disjoint,total_counters=value['total_counters']))
        checks.append(dict(cell_id=stem,verification=verification))
        for count in rules['prefixes']:
            record=dict(cell_id=stem,instance_id=str(index),arm='prefix'+str(count),prefix=count,status='unknown',verified=False,**{m:None for m in metrics},counters=None,outer_phases=[p for p in outer if p.get('cell_id')==stem])
            if value is not None:
                record.update(status='collected_unanalyzed',**{k:work[k] for k in ('source_queries','target_queries','pair_entries')})
                record['counters']=value['holdout_collection_counters'] if count==0 else {}
            if count in prefixes:
                m=prefix_metrics(cell,rules,value,prefixes[count]);record.update(status='collected_unverified',**m)
                if verified:
                    expected=dict(base_columns=value['projection']['U'],base_rank=m['base_rank'],base_nullity=m['base_nullity'],source_rows=m['accepted_witnesses'],distinct_equations=m['distinct_equations'],single_targets=m['single_identified_targets'],joint_targets=m['joint_identified_targets'],joint_rank=m['joint_rank'],base_rank_after_target_cancellation=value['projection']['U']-m['joint_base_nullity'],early_single_targets=m['single_identified_targets'] if m['base_nullity'] else 0,early_joint_targets=m['joint_recoveries_with_base_uncertainty'])
                    if any(summaries[count].get(k)!=v for k,v in expected.items()):raise ValueError('independent prefix summary differs')
                    record.update(status='verified',verified=True)
            cells.append(record)
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cells)
    analysis=dict(schema='a4-retained-holdout-analysis/v1',cells=cells,panel_complete=complete,unknown_cells=sum(c['status']=='unknown' for c in cells),generation=generated,generation_verification=gencheck,independent_checks=checks,physical_cost_records=costs,cost_scope='Onephysicalpanel;4sharedsource/targetstreams,12prefixanalyses. Prefix logical querycounts repeat; shared collection counters onlyprefix0. Backend disjoint prefixphase costs once; cumulative totals and inclusive outer clocks never added. No completeS/rho/advantage.',performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_a4_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','A4-holdout-'+args.run.name);export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    for c in cells:
        status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status')=='failed' for p in c['outer_phases']) else 'interrupted'
        export['runs'].append(tools.run_row(run_id='A4-'+args.run.name+'-'+c['instance_id']+'-'+c['arm'],arm=c['arm'],instance_id=c['instance_id'],seed=0,replicate=0,warmup=False,status=status,measurements=dict(counted={k:c[k] for k in metrics if c[k]is not None},counters=c['counters'] or {},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolated clock']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='Separate complete recipe/sum/table/query/denseaffine/certificate checks; fieldcounters not independently audited'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    export['backend_record']=dict(physical_executions=1,outer_phases=outer,generation_diagnostics=None if generated is None else generated['generation_diagnostics'],physical_cost_records='analysis.json physical_cost_records',shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},wall_valid=False,counting_scope='12prefixrecords,4collectionstreams,1physicalpanel. Sharedquerycounts repeat; collection counters onlyprefix0. Prefixphasecosts once in backend. No summing cumulative/inclusiveviews.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()];export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')];export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export);print(json.dumps(dict(panel_complete=complete,unknown_cells=analysis['unknown_cells'])))


if __name__=='__main__':main()
