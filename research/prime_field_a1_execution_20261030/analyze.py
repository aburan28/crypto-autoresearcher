"""Retained A1 analysis: no pool generation, branch collection or rank solver."""
import argparse
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,digest,expected_attempts,write_once


def retained(path):
    files=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(files)>1:raise ValueError('ambiguous retained encodings: '+str(path))
    return files[0] if files else None


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


def check_cancellations(arm,p):
    """Verify carried original-row identities without constructing a kernel."""
    B,U,rhs=arm['B'],arm['U'],arm['rhs'];count=len(B)
    if len(U)!=count or len(rhs)!=count:raise ValueError('partial matrix lengths differ')
    width=arm['preprocessing_quality']['columns']
    outside_width=len(U[0]) if U else 0
    if any(len(v)!=width for v in B) or any(len(v)!=outside_width for v in U):raise ValueError('partial matrix widths differ')
    cancellation=arm['cancellation']
    before=arm['preprocessing_quality']['rank']
    if (arm['rank_gain']!=arm['stacked_rank']-arm['outside_rank']-before or
        arm['base_rank_after']-before!=arm['rank_gain'] or
        cancellation['base_rank_before']!=before or cancellation['base_rank_after']!=arm['base_rank_after'] or
        cancellation['outside_rank']!=arm['outside_rank'] or cancellation['rank_gain']!=arm['rank_gain']):
        raise ValueError('cancelled Delta rank identity differs')
    certificates=cancellation['cancellations']
    if len(certificates)!=count-arm['outside_rank']:raise ValueError('incomplete carried cancellation count')
    for record in certificates:
        weights=record['partial_row_weights']
        if len(weights)!=count or any(type(w) is not int or not 0<=w<p for w in weights):raise ValueError('bad carried row weights')
        if any(sum(w*row[j] for w,row in zip(weights,U))%p for j in range(outside_width)):
            raise ValueError('carried row weights do not cancel outside columns')
        coefficients=[sum(w*row[j] for w,row in zip(weights,B))%p for j in range(width)]
        value=sum(w*b for w,b in zip(weights,rhs))%p
        if record['coefficients']!=coefficients or record['rhs']!=value:raise ValueError('false carried cancellation equation')
    return len(certificates)


def project_partial_metadata(row,result,prefix,p):
    """Reproject retained signed coefficients; no group or rank computation."""
    projection=result['projection'];outside=result['outside_projection']['native_to_projected']
    if len(row['coefficients'])!=len(projection['native_to_projected']) or len(row['outside_coefficients'])!=len(outside):
        raise ValueError('native partial coefficient width differs')
    B=[0]*projection['U'];U=[0]*sum(m[0]=='unknown' for m in outside[:prefix]);rhs=row['source_scalar']
    for c,mapping in zip(row['coefficients'],projection['native_to_projected']):
        if mapping[0]=='known':rhs-=c*mapping[1]
        elif mapping[0]=='unknown':B[mapping[1]]+=c*mapping[2]
    for c,mapping in zip(row['outside_coefficients'][:prefix],outside[:prefix]):
        if mapping[0]=='known':rhs-=c*mapping[1]
        else:U[mapping[1]]+=c
    return [b%p for b in B],[u%p for u in U],rhs%p


def check_pool_metadata(data,cell,value):
    pool=value['pool'];points=pool['points'];f=cell['fixture']
    if pool.get('curve_uid')!=cell['pool_curve_uid'] or pool.get('recipe')!=data['pool_recipe'] or pool.get('scalar_labels_generated') is not False or len(points)!=32:
        raise ValueError('pool differs from frozen full-EC1 recipe')
    old={(a['point'][0],min(a['point'][1],-a['point'][1]%f['p'])) for a in f['factor_base']}
    if (any(not isinstance(q,list) or len(q)!=2 or any(type(v) is not int for v in q) or
            not 0<=q[0]<f['p'] or not 0<=q[1]<=f['p']//2 for q in points) or
        len({tuple(q) for q in points})!=32 or any(tuple(q) in old for q in points)):
        raise ValueError('noncanonical, repeated or old-base pool point')
    # Rationality/subgroup/earliest hash selection and known signed scalars are
    # independently checked by the native recipe oracle; never generated here.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();execution=load(args.run/'execution.json');host=load(args.run/'host.json')
    protocol=load(args.protocol);data=json.loads(INPUTS.read_text());metrics=[m['id'] for m in protocol['metrics']['primary']]
    phases=list(lines(args.run/'raw/phases.jsonl'));cells=[];shared=[]
    for index,definition in enumerate(data['cells']):
        f=definition['fixture'];stem=definition['id'];final_value=load(args.run/'raw'/(stem+'.json'));collection_value=load(args.run/'raw'/(stem+'.collection.json'))
        value=final_value if final_value is not None else collection_value
        if final_value is not None and collection_value is not None and {k:v for k,v in final_value.items() if k!='arms'}!={k:v for k,v in collection_value.items() if k!='arms'}:
            raise ValueError('collected snapshot differs from finalized shared stream')
        verification=load(args.run/'raw'/(stem+'.verification.json'));events=list(lines(args.run/'raw'/(stem+'.events.jsonl')))
        arm_values={} if value is None else {a['arm']:a for a in value['arms']}
        arm_checks={} if verification is None else {a['arm']:a for a in verification['arms']}
        if value is not None:
            if (value.get('schema')!='prym-residual-partials/v1' or value.get('curve_uid')!=f['uid'] or value.get('complete') is not True or
                value.get('source_order')!=definition['source_order'] or value.get('attempts')!=expected_attempts(definition) or
                value.get('inputs_sha256')!=digest(INPUTS) or (final_value is not None and (len(arm_values)!=3 or set(arm_values)!=set(ARMS))) or
                (final_value is None and arm_values)):
                raise ValueError('wrong complete shared census identity')
            check_pool_metadata(data,definition,value)
        if verification is not None and (value is None or len(arm_checks)!=3 or set(arm_checks)!=set(ARMS)):
            raise ValueError('orphan or incomplete arm verification')
        global_verified=verification is not None and verification.get('checked') is True and verification.get('complete_branch_replay') is True and verification.get('pool_recipe_checked') is True
        if global_verified and (verification.get('attempts_replayed')!=value['attempts'] or verification.get('rows_verified')!=len(value['rows'])):
            raise ValueError('full independent replay coverage differs')
        if value is not None:
            accepted=[e['row'] for e in events if e.get('kind')=='accepted']
            source_events=[e for e in events if e.get('kind')=='source_complete']
            if len(accepted)==len(value['rows']) and len(source_events)==64:
                blocks=[{k:e[k] for k in ('scalar','attempts','statuses','branch_sha256')} for e in source_events]
                if accepted!=value['rows'] or blocks!=value['status_blocks']:raise ValueError('complete witness/source-status journal differs')
            hash_events=[{k:v for k,v in e.items() if k!='kind'} for e in events if e.get('kind')=='pool_hash_attempt']
            if hash_events and hash_events!=value['pool']['hash_attempts']:raise ValueError('pool hash journal differs')
        lower=max([0]+[e.get('attempts',e.get('attempt',0)) for e in events])
        shared.append(dict(curve_uid=f['uid'],collection_attempts=None if value is None else value['attempts'],
            verification_attempts=verification['attempts_replayed'] if global_verified else None,attempts_lower_bound=lower))
        for name,prefix in zip(ARMS,(0,16,32)):
            row=dict(cell_id=stem,curve_uid=f['uid'],arm=name,instance_id=str(index),status='unknown',verified=False,
                **{m:None for m in metrics},native_counters=None,phase_records=[p for p in phases if p.get('cell_id')==stem])
            if value is not None:
                row['logical_attempts']=value['attempts']
                if name=='smooth':row['native_counters']=dict(value['operation_vector'])
                if name=='smooth' and 'hash_group_ops' in value['pool']:row['native_counters']['separate_pool_hash_group_ops']=value['pool']['hash_group_ops']
            arm=arm_values.get(name)
            if arm is not None:
                if arm.get('pool_prefix')!=prefix or arm.get('complete') is not True:raise ValueError('incomplete/wrong nested arm')
                indices=[i for i,w in enumerate(value['rows']) if all(j<prefix for j in w['outside_indices_used'])]
                if arm['row_indices']!=indices:raise ValueError('nested arm filter differs from original pool ordinals')
                projected=[project_partial_metadata(value['rows'][i],value,prefix,f['r']) for i in indices]
                if arm['B']!=[b for b,u,v in projected] or arm['U']!=[u for b,u,v in projected] or arm['rhs']!=[v for b,u,v in projected]:
                    raise ValueError('retained signed/public-anchor partial projection differs')
                certificates=check_cancellations(arm,f['r'])
                outside=value['outside_projection']['native_to_projected'][:prefix]
                outside_count=sum(m[0]=='unknown' for m in outside);known_count=sum(m[0]=='known' for m in outside)
                if any(len(u)!=outside_count for u in arm['U']):raise ValueError('prefix outside-column width differs')
                # Distinct affine signatures include both declared B and U columns.
                equations=set()
                for B,U,b in zip(arm['B'],arm['U'],arm['rhs']):
                    affine=[v%f['r'] for v in B+U+[b]];first=next((v for v in affine if v),None)
                    equations.add(tuple(v*pow(first,-1,f['r'])%f['r'] for v in affine) if first else tuple(affine))
                if arm['new_quality']['rows']!=len(indices) or arm['new_quality']['unique_affine_equations']!=len(equations):
                    raise ValueError('partial distinct-equation count differs')
                kernel=arm['old_kernel']
                if len(kernel)!=arm['preprocessing_quality']['nullity'] or any(len(k)!=value['projection']['U'] for k in kernel):
                    raise ValueError('old-kernel dimensions differ')
                syndromes=[[sum(a*b for a,b in zip(c['coefficients'],k))%f['r'] for k in kernel] for c in arm['cancellation']['cancellations']]
                if arm['cancelled_old_kernel_syndromes']!=syndromes or arm['nonzero_old_kernel_syndromes']!=sum(any(v) for v in syndromes):
                    raise ValueError('cancelled old-kernel products differ')
                row.update(status='collected_unverified',logical_attempts=value['attempts'],accepted_witnesses=len(indices),distinct_equations=len(equations),
                    outside_unknown_columns=outside_count,outside_rank=arm['outside_rank'],stacked_rank=arm['stacked_rank'],
                    base_rank_before=arm['preprocessing_quality']['rank'],base_rank_after=arm['base_rank_after'],delta=arm['rank_gain'],
                    cancellation_equations=certificates,known_public_pool_points=known_count,
                    direct_base_rank=arm['direct_base_rank'],direct_base_gain=arm['direct_base_gain'],cross_row_cancellation_gain=arm['cross_row_cancellation_gain'])
                if arm['direct_base_rank']-arm['preprocessing_quality']['rank']!=arm['direct_base_gain'] or arm['rank_gain']-arm['direct_base_gain']!=arm['cross_row_cancellation_gain'] or not 0<=arm['direct_base_gain']<=arm['rank_gain']:
                    raise ValueError('direct versus cross-row cancellation gain differs')
                checked=arm_checks.get(name)
                if global_verified:
                    if checked is None or any(checked.get(k)!=arm[k] for k in ('rank_gain','outside_rank','stacked_rank','base_rank_after','direct_base_rank','direct_base_gain','cross_row_cancellation_gain')) or checked.get('cancellations_verified')!=certificates:
                        raise ValueError('dense independent arm oracle/certificates differ')
                    row.update(status='verified',verified=True)
            cells.append(row)
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cells)
    analysis=dict(schema='a1-retained-partial-analysis/v1',cells=cells,shared_collection=shared,panel_complete=complete,
        unknown_cells=sum(c['status']=='unknown' for c in cells),physical_collection_attempts_observed=sum(c['collection_attempts'] or 0 for c in shared),
        physical_replay_attempts_observed=sum(c['verification_attempts'] or 0 for c in shared),
        cost_scope='One shared32pool census per curve. Logical arm attempts repeat; native counters only smooth rows; process/phase costs once. Partial counters do not establish complete S or Delta-per-total-cost.',
        verification_scope='Independent recipe/branch/cancellation+dense rank implementation check, not independent scientific review or counter audit.',performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_a1_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','A1-residual-pool-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']})
    export['runs']=[]
    for cell in cells:
        status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status')=='failed' for p in cell['phase_records']) else 'interrupted'
        export['runs'].append(tools.run_row(run_id='A1-'+args.run.name+'-'+cell['instance_id']+'-'+cell['arm'],arm=cell['arm'],instance_id=cell['instance_id'],seed=0,replicate=0,warmup=False,status=status,
            measurements=dict(counted={k:cell[k] for k in metrics if cell[k] is not None},counters=cell['native_counters'] or {},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolated clock']),verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='Full pool/branch replay, carried cancellation weights and independent dense rank oracle'),
            started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    export['backend_record']=dict(physical_executions=1,shared_process_ownership='ownership.json',shared_collection=shared,
        shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},phase_records=phases,wall_valid=False,
        counting_scope='Six nested arm/curve records share two rawstreams in one physical process. Do not sum logicalattempts as physical work. Native shared counters only smooth rows; process resources once here. Pool/collection/elimination/replay phases are components, not extra executions.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export);print(json.dumps(dict(panel_complete=complete,unknown_cells=analysis['unknown_cells'])))


if __name__=='__main__':main()
