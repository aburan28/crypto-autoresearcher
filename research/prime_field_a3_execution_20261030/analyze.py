"""Retained A3 accounting and exact-set checks; no point enumeration or rank solver."""
import argparse
from collections import Counter
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,digest,expected_attempts,expected_pairs,write_once


def load(path):
    paths=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(paths)>1:raise ValueError('ambiguous retained encodings')
    if not paths:return None
    with (gzip.open if paths[0].suffix=='.gz' else open)(paths[0],'rt') as stream:return json.load(stream)


def lines(path):
    paths=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(paths)>1:raise ValueError('ambiguous journal encodings')
    if paths:
        with (gzip.open if paths[0].suffix=='.gz' else open)(paths[0],'rt') as stream:
            for line in stream:
                if line.strip():yield json.loads(line)


def row_key(row):return (row['source_scalar'],tuple(row['triple']),tuple(row['signs']))


def project(row,projection,p):
    if len(row['coefficients'])!=len(projection['native_to_projected']):raise ValueError('native row width differs')
    vector=[0]*projection['U'];rhs=row['source_scalar']
    for c,m in zip(row['coefficients'],projection['native_to_projected']):
        if m[0]=='known':rhs-=c*m[1]
        elif m[0]=='unknown':vector[m[1]]+=c*m[2]
    return [v%p for v in vector],rhs%p


def check_phase_accounting(value):
    collection=value['collection_phases'];analysis=value.get('analysis');phases=collection+([] if analysis is None else analysis['analysis_phases'])
    if len({p['phase'] for p in phases})!=len(phases):raise ValueError('overlapping inner phase labels')
    for phase in phases:
        if phase['status']!='complete' or phase['wall_valid'] is not False or phase['cpu_seconds']<0 or phase['wall_seconds']<0:
            raise ValueError('invalid diagnostic phase')
        if any(type(v) is not int or v<0 for v in phase['counters'].values()):raise ValueError('invalid counted work')
    collection_total=Counter()
    for phase in collection:collection_total.update(phase['counters'])
    if dict(collection_total)!=value['collection_counters']:raise ValueError('collection counter conservation differs')
    total=Counter()
    for phase in phases:total.update(phase['counters'])
    if analysis is not None and dict(total)!=analysis['total_counters']:raise ValueError('total counter conservation differs')
    return phases,dict(total)


def check_row_metadata(value,cell):
    f=cell['fixture'];keys=[]
    for row in value['rows']:
        triple,signs=row['triple'],row['signs']
        if (row.get('schema')!='direct-three-sum-row/v1' or row.get('curve_uid')!=f['uid'] or row['source_scalar'] not in cell['source_order'] or
            len(triple)!=3 or triple!=sorted(set(triple)) or any(type(j) is not int or not 0<=j<16 for j in triple) or
            len(signs)!=3 or any(type(s) is not int or s not in (1,-1) for s in signs)):raise ValueError('invalid direct signed descriptor')
        expected=[0]*16
        for j,s in zip(triple,signs):expected[j]=s%f['r']
        if row['coefficients']!=expected:raise ValueError('direct coefficient identity differs')
        keys.append(row_key(row))
    if keys!=sorted(set(keys)):raise ValueError('direct rows not unique canonical order')


def check_analysis(value,cell):
    a=value['analysis'];projection=value['projection'];p=cell['fixture']['r'];width=projection['U'];rows=value['rows'];old=cell['preprocessing_rows']
    if width!=15 or a['rows']!=len(rows):raise ValueError('original column/row scope differs')
    for name in ('preprocessing','new','combined'):
        q=a[name]
        if q['columns']!=width or q['nullity']!=width-q['rank']:raise ValueError('same-column rank metadata differs')
    if a['rank_gain']!=a['combined']['rank']-a['preprocessing']['rank']:raise ValueError('rank gain differs')
    old_projected=[project(w,projection,p) for w in old];new_projected=[project(w,projection,p) for w in rows]
    old_kernel=a['old_kernel'];kernel=a['kernel']
    if len(old_kernel)!=a['preprocessing']['nullity'] or len(kernel)!=a['combined']['nullity'] or any(len(k)!=width for k in old_kernel+kernel):raise ValueError('kernel dimensions differ')
    if any(sum(x*y for x,y in zip(v,k))%p for v,b in old_projected for k in old_kernel):raise ValueError('old kernel fails M')
    if any(sum(x*y for x,y in zip(v,k))%p for v,b in old_projected+new_projected for k in kernel):raise ValueError('combined kernel fails retained rows')
    action=[[sum(x*y for x,y in zip(v,k))%p for k in old_kernel] for v,b in new_projected]
    if a['old_kernel_syndromes']!=action or a['nonzero_old_kernel_syndromes']!=sum(any(v) for v in action):raise ValueError('old kernel row products differ')
    equations=set()
    for v,b in new_projected:
        affine=v+[b];first=next((x for x in affine if x),None)
        equations.add(tuple(x*pow(first,-1,p)%p for x in affine) if first else tuple(affine))
    normalized=[list(v) for v in sorted(equations)]
    if a['normalized_equations']!=normalized or a['distinct_equations']!=len(normalized):raise ValueError('affine semantic set differs')
    return dict(distinct_equations=len(normalized),new_rank=a['new']['rank'],combined_rank=a['combined']['rank'],rank_gain=a['rank_gain'],base_nullity_after=a['combined']['nullity'],nonzero_old_kernel_syndromes=sum(any(v) for v in action))


def archived_subset(cell,direct_rows):
    lookup={row_key(r):i for i,r in enumerate(direct_rows)};indices=[];p=cell['fixture']['p']
    for row in cell['archived_norm_rows']:
        labels=row['base_labels'];key=(row['source_scalar'],tuple(v[0] for v in labels),tuple(v[1] for v in labels))
        if row.get('norm_completed') is not True or key not in lookup:raise ValueError('archived norm-only descriptor absent from D')
        direct=direct_rows[lookup[key]];images=row['residual_E_images']
        if direct['coefficients']!=row['coefficients'] or images[0][0]!=images[1][0] or (images[0][1]+images[1][1])%p:
            raise ValueError('archived norm coefficient/cancellation identity differs')
        indices.append(lookup[key])
    return dict(witnesses=len(indices),distinct_direct_descriptors=len(set(indices)),direct_row_indices=indices)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();execution=load(args.run/'execution.json');host=load(args.run/'host.json');protocol=load(args.protocol);data=json.loads(INPUTS.read_text())
    metrics=[m['id'] for m in protocol['metrics']['primary']];outer=list(lines(args.run/'raw/phases.jsonl'));cells=[];verification_records=[]
    for index,cell in enumerate(data['cells']):
        stem=cell['id'];final=load(args.run/'raw'/(stem+'.json'));snapshot=load(args.run/'raw'/(stem+'.collection.json'));value=final if final is not None else snapshot
        verification=load(args.run/'raw'/(stem+'.verification.json'));events=list(lines(args.run/'raw'/(stem+'.events.jsonl')))
        arms={} if value is None else {a['arm']:a for a in value['arms']};checks={} if verification is None else {a['arm']:a for a in verification['arms']}
        if value is not None and (value.get('schema')!='direct-three-sum-cell/v1' or value.get('cell_id')!=stem or value.get('curve_uid')!=cell['fixture']['uid'] or
            value.get('complete') is not True or value.get('inputs_sha256')!=digest(INPUTS) or len(arms)!=2 or set(arms)!=set(ARMS)):raise ValueError('wrong aggregate identity')
        if final is not None and snapshot is not None:
            for a,b in zip(final['arms'],snapshot['arms'],strict=True):
                if {k:v for k,v in a.items() if k!='analysis'}!={k:v for k,v in b.items() if k!='analysis'}:raise ValueError('final method differs from collection snapshot')
        if value is not None and (arms['enumeration']['rows']!=arms['pair_table']['rows'] or arms['enumeration']['projection']!=arms['pair_table']['projection']):raise ValueError('direct semantic sets/projections differ')
        subset=None if value is None else archived_subset(cell,arms['enumeration']['rows'])
        verified=verification is not None and verification.get('checked') is True and verification.get('complete_branch_replay') is True
        if verification is not None and (value is None or len(checks)!=2 or set(checks)!=set(ARMS)):raise ValueError('orphan/incomplete verification')
        if verified and (verification.get('attempts_replayed')!=expected_attempts(cell,'enumeration') or verification.get('pair_entries_checked')!=expected_pairs(cell) or
            verification.get('queries_checked')!=expected_attempts(cell,'pair_table') or verification.get('rows_verified')!=len(arms['enumeration']['rows']) or verification.get('archived_norm_subset')!=subset):raise ValueError('independent complete replay/subset scope differs')
        verification_records.append(dict(cell_id=stem,independent_replay=None if verification is None else {k:verification.get(k) for k in ('attempts_replayed','pair_entries_checked','queries_checked')},archived_norm_subset=subset))
        for name in ARMS:
            result=arms.get(name);record=dict(cell_id=stem,arm=name,instance_id=str(index),status='unknown',verified=False,**{m:None for m in metrics},counters=None,metered_phases=None,
                outer_phases=[p for p in outer if p.get('cell_id')==stem and p.get('arm') in (None,name)])
            if result is not None:
                if result.get('schema')!='direct-three-sum/v1' or result.get('curve_uid')!=cell['fixture']['uid'] or result.get('complete') is not True or result.get('source_order')!=cell['source_order'] or result.get('attempts')!=expected_attempts(cell,name) or len(result['pair_entries'])!=(expected_pairs(cell) if name=='pair_table' else 0):raise ValueError('wrong complete method scope')
                check_row_metadata(result,cell);phases,counters=check_phase_accounting(result)
                accepted=[e['row'] for e in events if e.get('kind')=='accepted' and e.get('arm')==name]
                if sorted(accepted,key=row_key)!=result['rows']:raise ValueError('accepted journal differs from complete rows')
                source_events=[{k:v for k,v in e.items() if k not in ('kind','arm')} for e in events if e.get('kind')=='source_complete' and e.get('arm')==name]
                if len(source_events)!=64 or [e['scalar'] for e in source_events]!=cell['source_order'] or source_events!=result['status_blocks']:
                    raise ValueError('complete source journal differs')
                pair_events=[e for e in events if e.get('kind')=='pair_entry' and e.get('arm')==name]
                if [e['index'] for e in pair_events]!=list(range(len(result['pair_entries']))) or [{k:v for k,v in e.items() if k not in ('kind','arm','index')} for e in pair_events]!=result['pair_entries']:
                    raise ValueError('complete pair journal differs')
                record.update(status='collected_unanalyzed',attempts=result['attempts'],pair_entries=len(result['pair_entries']),accepted_witnesses=len(result['rows']),counters=counters,metered_phases=phases)
                if result['analysis'] is not None:
                    measured=check_analysis(result,cell);record.update(status='collected_unverified',**measured)
                    if verified:
                        check=checks[name]
                        if any(check.get(k)!=v for k,v in measured.items() if k in ('distinct_equations','new_rank','combined_rank','rank_gain')) or check.get('base_rank')!=result['analysis']['preprocessing']['rank'] or check.get('accepted_witnesses')!=len(result['rows']):raise ValueError('independent method rank summary differs')
                        record.update(status='verified',verified=True)
            cells.append(record)
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cells)
    analysis=dict(schema='a3-retained-direct-analysis/v1',cells=cells,semantic_reference=verification_records,panel_complete=complete,unknown_cells=sum(c['status']=='unknown' for c in cells),
        cost_scope='Each direct method charges its own metered cold setup/source/sign/collector/analysis work. Descriptors and queries are unlike units. Sum disjoint innerphase counters only; outer/wholeprocess/replay clocks are separately retained and never added again. No complete-S/rho/novelty/speedup claim.',performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_a3_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','A3-direct-'+args.run.name);export['producer']=dict(runtime='codex',model=None,session=None,role='executor')
    export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    for c in cells:
        status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status')=='failed' for p in c['outer_phases']) else 'interrupted'
        export['runs'].append(tools.run_row(run_id='A3-'+args.run.name+'-'+c['instance_id']+'-'+c['arm'],arm=c['arm'],instance_id=c['instance_id'],seed=0,replicate=0,warmup=False,status=status,
            measurements=dict(counted={k:c[k] for k in metrics if c[k] is not None},counters=c['counters'] or {},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolated clock']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='Separate complete E enumeration, all pair/query, dense affine/kernel and archivednorm-subset checks; field counters not independently audited'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    export['backend_record']=dict(physical_executions=1,shared_process_ownership='ownership.json',independent_verification=verification_records,outer_phases=outer,inner_phase_cost_records='analysis.json cells[].metered_phases',
        shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},wall_valid=False,
        counting_scope='Four method/curve cells in one supervised panel; unlike method attempts. Method innerphases/counters occur once per method. Outerprocess/independentverification diagnostics are inclusive/separate and must not be added to inner costs.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export);print(json.dumps(dict(panel_complete=complete,unknown_cells=analysis['unknown_cells'])))


if __name__=='__main__':main()
