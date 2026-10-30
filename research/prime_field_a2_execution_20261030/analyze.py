"""Prospective retained A2 analysis; no native collection, point draw or rank solver."""
import argparse
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,digest,expected_attempts,write_once


def retained(path):
    paths=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(paths)>1:raise ValueError('ambiguous retained encodings')
    return paths[0] if paths else None


def load(path):
    path=retained(path)
    if path is None:return None
    with (gzip.open if path.suffix=='.gz' else open)(path,'rt') as stream:return json.load(stream)


def lines(path):
    path=retained(path)
    if path is not None:
        with (gzip.open if path.suffix=='.gz' else open)(path,'rt') as stream:
            for line in stream:
                if line.strip():yield json.loads(line)


def project(row,projection,p):
    coefficients=row['coefficients'];mapping=projection['native_to_projected']
    if len(coefficients)!=len(mapping):raise ValueError('native coefficient width differs')
    vector=[0]*projection['U'];rhs=row['source_scalar']
    for c,m in zip(coefficients,mapping):
        if m[0]=='known':rhs-=c*m[1]
        elif m[0]=='unknown':vector[m[1]]+=c*m[2]
    return [v%p for v in vector],rhs%p


def check_residual_metadata(row,fixture):
    """Check retained norm labels/images/coefficient cancellation, no point search."""
    p,r=fixture['p'],fixture['r'];images=row['residual_E_images'];roots=row['residual_roots'];v=row['v_coefficients']
    if len(images)!=2 or len(roots)!=2 or len(set(roots))!=2 or type(row['norm_completed']) is not bool:
        raise ValueError('invalid residual pair/label')
    expected=[[x*x%p,sum(c*pow(x,j,p) for j,c in enumerate(v))%p] for x in roots]
    if images!=expected:raise ValueError('residual E images differ from retained polynomial')
    by_x={a['point'][0]:(j,a['point']) for j,a in enumerate(fixture['factor_base'])}
    smooth=all(q[0] in by_x for q in images)
    cancelling=images[0][0]==images[1][0] and (images[0][1]+images[1][1])%p==0
    if row['norm_completed']!=(not smooth) or not smooth and not cancelling:
        raise ValueError('false norm-completion label or noncancelling residual pair')
    coefficients=[0]*len(fixture['factor_base'])
    if len(row['base_labels'])!=3:raise ValueError('three oldbase constraints required')
    for j,sign,option in row['base_labels']:
        if not 0<=j<len(coefficients) or option not in range(4) or sign!=(-1 if option&1 else 1):raise ValueError('invalid oldbase sign label')
        coefficients[j]+=sign
    if smooth:
        for q in images:
            j,atom=by_x[q[0]]
            if q==atom:coefficients[j]+=1
            elif q==[atom[0],-atom[1]%p]:coefficients[j]-=1
            else:raise ValueError('residual oldbase orientation differs')
    if row['coefficients']!=[c%r for c in coefficients]:raise ValueError('base-only residual coefficient identity differs')
    if 'outside_coefficients' in row:raise ValueError('A2 cannot introduce outside unknowns')


def check_arm_metadata(arm,rows,definition,projection,p):
    indices=[i for i,row in enumerate(rows) if arm['arm']=='norm_completed' or not row['norm_completed']]
    if arm['row_indices']!=indices or arm.get('complete') is not True:raise ValueError('nested norm arm selection differs')
    quality=arm['preprocessing_quality'];new=arm['new_quality'];combined=arm['combined_quality'];width=projection['U']
    if (quality['rows']!=len(definition['preprocessing_rows']) or quality['columns']!=width or
        new['rows']!=len(indices) or new['columns']!=width or combined['rows']!=quality['rows']+len(indices) or combined['columns']!=width or
        quality['nullity']!=width-quality['rank'] or new['nullity']!=width-new['rank'] or combined['nullity']!=width-combined['rank'] or
        arm['rank_gain']!=combined['rank']-quality['rank']):raise ValueError('same-column rank/count metadata differs')
    old_kernel=arm['old_kernel'];kernel=arm['kernel']
    if len(old_kernel)!=quality['nullity'] or len(kernel)!=combined['nullity'] or any(len(k)!=width for k in old_kernel+kernel):
        raise ValueError('kernel dimensions differ')
    projected=[project(rows[i],projection,p) for i in indices];old=[project(w,projection,p) for w in definition['preprocessing_rows']]
    if any(sum(a*b for a,b in zip(vector,k))%p for vector,rhs in old for k in old_kernel):raise ValueError('old kernel fails retained oldM')
    if any(sum(a*b for a,b in zip(vector,k))%p for vector,rhs in old+projected for k in kernel):raise ValueError('combined kernel fails retained rows')
    syndromes=[[sum(a*b for a,b in zip(vector,k))%p for k in old_kernel] for vector,rhs in projected]
    if arm['old_kernel_syndromes']!=syndromes or arm['nonzero_old_kernel_syndromes']!=sum(any(v) for v in syndromes):
        raise ValueError('old-kernel row products differ')
    equations=set()
    for vector,rhs in projected:
        affine=vector+[rhs];first=next((x for x in affine if x),None)
        equations.add(tuple(x*pow(first,-1,p)%p for x in affine) if first else tuple(affine))
    norm_count=sum(rows[i]['norm_completed'] for i in indices)
    if new['unique_affine_equations']!=len(equations) or arm['norm_completed_witnesses']!=norm_count:
        raise ValueError('affine equation/norm-witness count differs')
    return dict(accepted_witnesses=len(indices),norm_completed_witnesses=norm_count,distinct_equations=len(equations),new_rank=new['rank'],
        combined_rank=combined['rank'],rank_gain=arm['rank_gain'],base_nullity_after=combined['nullity'],nonzero_old_kernel_syndromes=sum(any(v) for v in syndromes))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();execution=load(args.run/'execution.json');host=load(args.run/'host.json');protocol=load(args.protocol);data=json.loads(INPUTS.read_text())
    metrics=[m['id'] for m in protocol['metrics']['primary']];phases=list(lines(args.run/'raw/phases.jsonl'));cells=[];shared=[]
    for index,definition in enumerate(data['cells']):
        f=definition['fixture'];stem=definition['id'];final=load(args.run/'raw'/(stem+'.json'));snapshot=load(args.run/'raw'/(stem+'.collection.json'))
        value=final if final is not None else snapshot;verification=load(args.run/'raw'/(stem+'.verification.json'));events=list(lines(args.run/'raw'/(stem+'.events.jsonl')))
        if final is not None and snapshot is not None and {k:v for k,v in final.items() if k!='arms'}!={k:v for k,v in snapshot.items() if k!='arms'}:
            raise ValueError('final norm stream differs from retained collection snapshot')
        arms={} if value is None else {a['arm']:a for a in value['arms']};checks={} if verification is None else {a['arm']:a for a in verification['arms']}
        if value is not None:
            if (value.get('schema')!='prym-norm-completion/v1' or value.get('curve_uid')!=f['uid'] or value.get('source_order')!=definition['source_order'] or
                value.get('complete') is not True or value.get('attempts')!=expected_attempts(definition) or value.get('inputs_sha256')!=digest(INPUTS) or
                (final is not None and (len(arms)!=2 or set(arms)!=set(ARMS))) or (final is None and arms)):
                raise ValueError('wrong complete norm census identity')
            for row in value['rows']:check_residual_metadata(row,f)
            accepted=[e['row'] for e in events if e.get('kind')=='accepted'];sources=[e for e in events if e.get('kind')=='source_complete']
            if len(accepted)==len(value['rows']) and len(sources)==64:
                blocks=[{k:e[k] for k in ('scalar','attempts','statuses','branch_sha256')} for e in sources]
                if accepted!=value['rows'] or blocks!=value['status_blocks']:raise ValueError('complete witness/status journal differs')
        if verification is not None and (value is None or len(checks)!=2 or set(checks)!=set(ARMS)):raise ValueError('orphan/incomplete norm verification')
        verified=verification is not None and verification.get('checked') is True and verification.get('complete_branch_replay') is True
        if verified and (verification.get('attempts_replayed')!=value['attempts'] or verification.get('rows_verified')!=len(value['rows'])):raise ValueError('separate norm replay coverage differs')
        shared.append(dict(curve_uid=f['uid'],collection_attempts=None if value is None else value['attempts'],verification_attempts=verification['attempts_replayed'] if verified else None,
            attempts_lower_bound=max([0]+[e.get('attempts',e.get('attempt',0)) for e in events])))
        for name in ARMS:
            row=dict(cell_id=stem,curve_uid=f['uid'],arm=name,instance_id=str(index),status='unknown',verified=False,**{m:None for m in metrics},native_counters=None,
                phase_records=[p for p in phases if p.get('cell_id')==stem])
            if value is not None:
                row['logical_attempts']=value['attempts']
                if name=='smooth':row['native_counters']=value['operation_vector']
            if name in arms:
                metadata=check_arm_metadata(arms[name],value['rows'],definition,value['projection'],f['r']);row.update(status='collected_unverified',**metadata)
                if verified:
                    check=checks[name]
                    if (check.get('rank_gain')!=metadata['rank_gain'] or check.get('combined_rank')!=metadata['combined_rank'] or
                        check.get('base_rank')!=arms[name]['preprocessing_quality']['rank'] or check.get('norm_completed_witnesses')!=metadata['norm_completed_witnesses']):
                        raise ValueError('independent norm arm dense summary differs')
                    row.update(status='verified',verified=True)
            cells.append(row)
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cells)
    analysis=dict(schema='a2-retained-norm-analysis/v1',cells=cells,shared_collection=shared,panel_complete=complete,unknown_cells=sum(c['status']=='unknown' for c in cells),
        physical_collection_attempts_observed=sum(c['collection_attempts'] or 0 for c in shared),physical_replay_attempts_observed=sum(c['verification_attempts'] or 0 for c in shared),
        cost_scope='One full norm census per curve; nested logicalattempt counts repeat. Shared native counters only smooth rows and process resources once; counters incomplete, no complete-S/cost advantage claim.',
        verification_scope='Separate full principal/E/auxiliary, branch, affine rank/kernel replay; not independent staffed scientific review/counter audit.',performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_a2_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','A2-norm-completion-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    for cell in cells:
        status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status')=='failed' for p in cell['phase_records']) else 'interrupted'
        export['runs'].append(tools.run_row(run_id='A2-'+args.run.name+'-'+cell['instance_id']+'-'+cell['arm'],arm=cell['arm'],instance_id=cell['instance_id'],seed=0,replicate=0,warmup=False,status=status,
            measurements=dict(counted={k:cell[k] for k in metrics if cell[k] is not None},counters=cell['native_counters'] or {},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolated clock']),verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='Full separate principal/E/auxiliary branch and dense affine rank/kernel replay'),
            started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    export['backend_record']=dict(physical_executions=1,shared_process_ownership='ownership.json',shared_collection=shared,
        shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},phase_records=phases,wall_valid=False,
        counting_scope='Four nested records share two complete rawstreams in one process. Logicalattempt metrics repeat and must not be summed as physical work; counters only smooth records. Collection/elimination/replay phases are components, not extra executions.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export);print(json.dumps(dict(panel_complete=complete,unknown_cells=analysis['unknown_cells'])))


if __name__=='__main__':main()
