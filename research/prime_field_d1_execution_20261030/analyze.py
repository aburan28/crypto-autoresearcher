"""Prospective retained-target analysis; never generates targets or collects rows."""
import argparse
import copy
import gzip
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
from common import HERE, ROOT, INPUTS, METHODS, digest, expected_attempts, write_once


def retained(path):
    options=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(options)>1:raise ValueError('ambiguous raw encodings: '+str(path))
    return options[0] if options else None


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


def check_recipe_metadata(data,cell,index,result):
    """Verify retained public recipe bytes, without searching or drawing a Q."""
    recipe=result['target_recipe'];f=cell['fixture'];selected=recipe['selected']
    if (recipe.get('curve_uid')!=cell['target_curve_uid'] or recipe.get('domain')!=data['target_domain'] or
        recipe.get('index')!=index or recipe.get('scalar_label_generated') is not False or
        recipe.get('subgroup_order')!=f['r'] or recipe.get('point')!=result['target'] or
        type(selected.get('counter')) is not int or not 0<=selected['counter']<data['max_target_counters']):
        raise ValueError('wrong frozen full-EC1 target recipe')
    rejected=recipe['rejected']
    if [r['counter'] for r in rejected]!=list(range(selected['counter'])):
        raise ValueError('incomplete target hash rejection prefix')
    for record in rejected+[selected]:
        message=f"{data['target_domain']}|{cell['target_curve_uid']}|{index}|{record['counter']}".encode('utf-8')
        hashed=sha256(message).hexdigest()
        if record['sha256']!=hashed or record['x']!=int(hashed,16)%f['p']:
            raise ValueError('retained target hash recipe bytes differ')
    if result['target'][0]!=selected['x']:raise ValueError('target x differs from selected hash')
    # Rationality, canonical root, subgroup and earliest-success selection are
    # independently verified by check_targets.check_recipe, not regenerated here.
    return recipe


def project(row,projection,p):
    vector,rhs=[0]*projection['U'],row['source_scalar']
    if len(row['coefficients'])!=len(projection['native_to_projected']):raise ValueError('bad projected row width')
    for c,mapping in zip(row['coefficients'],projection['native_to_projected']):
        if mapping[0]=='known':rhs-=c*mapping[1]
        elif mapping[0]=='unknown':vector[mapping[1]]+=c*mapping[2]
    return [v%p for v in vector],rhs%p


def check_certificate(record,result,preprocessing_rows,p,target_rows=None):
    """Check a target-unit row combination on retained original rows only."""
    width=result['projection']['U'];n=len(result['rows']) if target_rows is None else target_rows
    if type(n) is not int or not 0<=n<=len(result['rows']):raise ValueError('bad certificate target prefix')
    A=[];rhs=[]
    for row in preprocessing_rows:
        vector,value=project(row,result['projection'],p);A.append(vector+[0]);rhs.append(value)
    for row in result['rows'][:n]:
        vector,value=project(row,result['projection'],p)
        A.append(vector+[-row['target_coefficient']%p]);rhs.append(value)
    weights=record.get('row_weights')
    if (record.get('identifiable') is not True or record.get('verified') is not True or
        record.get('value')!=record.get('scalar') or not isinstance(weights,list) or len(weights)!=len(A) or
        any(type(w) is not int or not 0<=w<p for w in weights) or record.get('base_rows')!=len(preprocessing_rows) or
        record.get('base_columns')!=width or record.get('target_rows')!=n):
        raise ValueError('wrong target certificate metadata')
    if ([sum(w*row[j] for w,row in zip(weights,A))%p for j in range(width+1)] != [0]*width+[1] or
        sum(w*b for w,b in zip(weights,rhs))%p != record['scalar']):
        raise ValueError('false target row-combination certificate')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();execution=load(args.run/'execution.json');host=load(args.run/'host.json')
    protocol=load(args.protocol);data=json.loads(INPUTS.read_text())
    metric_ids=[m['id'] for m in protocol['metrics']['primary']]
    phases=list(lines(args.run/'raw/phases.jsonl'));cases=[]
    for cell in data['cells']:
        fixture=cell['fixture']
        for index in cell['target_indices']:
            stem=fixture['uid']+'-target-'+str(index)
            value=load(args.run/'raw'/(stem+'.json'));verification=load(args.run/'raw'/(stem+'.verification.json'))
            events=list(lines(args.run/'raw'/(stem+'.events.jsonl')))
            case=dict(curve_uid=fixture['uid'],target_curve_uid=cell['target_curve_uid'],target_index=index,
                instance_id=str(len(cases)),status='unknown',verified=False,verification_attempts=None,
                target_recipe=None,target=None,target_is_signed_base_point=None,target_is_public_anchor=None,
                collection_counters=None,**{m:None for m in metric_ids})
            case['phase_records']=[p for p in phases if p.get('fixture_uid',p.get('curve_uid'))==fixture['uid'] and p.get('target_index')==index]
            case['attempts_lower_bound']=max([0]+[e.get('attempts',e.get('attempt',0)) for e in events])
            recipes=[e['recipe'] for e in events if e.get('kind')=='target_generated']
            if recipes:case['unverified_observed_hash_recipe']=recipes[-1]
            if value is not None:
                if (value.get('schema')!='prym-natural-target-completion/v1' or value.get('curve_uid')!=fixture['uid'] or
                    value.get('source_order')!=cell['source_order'] or value.get('multipliers')!=data['multipliers'] or
                    value.get('complete') is not True or value.get('attempts')!=expected_attempts(data,cell) or
                    value.get('stopping_rule')!='full census regardless of recovery' or value.get('inputs_sha256')!=digest(INPUTS)):
                    raise ValueError('wrong complete target identity: '+stem)
                recipe=check_recipe_metadata(data,cell,index,value)
                diagnostic=value['target_identification'];quality=value['preprocessing']
                if (diagnostic['base_rank']!=quality['rank'] or diagnostic['base_columns']!=quality['columns'] or
                    diagnostic['base_rows']!=len(cell['preprocessing_rows']) or diagnostic['target_rows']!=len(value['rows']) or
                    quality['columns']!=value['projection']['U'] or quality['nullity']!=quality['columns']-quality['rank']):
                    raise ValueError('target/preprocessing metadata differs')
                single=value['first_single_recovery'];combined=value['first_combined_recovery'];final=value['final_target_certificate']
                if bool(diagnostic['identifiable']) != (final is not None) or bool(diagnostic['identifiable']) != (combined is not None):
                    raise ValueError('target identification and recovery disagree')
                if final is not None:
                    check_certificate(final,value,cell['preprocessing_rows'],fixture['r'])
                    if any(diagnostic.get(k)!=final.get(k) for k in ('value','row_weights','base_rank','base_rows','base_columns','target_rows','augmented_rank','syndrome')):
                        raise ValueError('final target identification differs from certificate')
                if combined is not None:
                    check_certificate(combined['certificate'],value,cell['preprocessing_rows'],fixture['r'],combined['certificate']['target_rows'])
                for first in (single,combined):
                    if first is not None and (type(first['attempt']) is not int or not 0<first['attempt']<=value['attempts']):
                        raise ValueError('invalid first recovery position')
                case.update(status='collected_unverified',target_recipe=recipe,target=value['target'],
                    target_is_signed_base_point=value['target_is_signed_base_point'],target_is_public_anchor=value['target_is_public_anchor'],
                    attempts=value['attempts'],witnesses=len(value['rows']),identified_target=int(diagnostic['identifiable']),
                    single_recovery=int(single is not None),combined_recovery=int(combined is not None),base_rank=quality['rank'],
                    augmented_rank=diagnostic['augmented_rank'],base_nullity=quality['nullity'],
                    first_single_attempt=None if single is None else single['attempt'],first_combined_attempt=None if combined is None else combined['attempt'],
                    collection_counters=value['operation_vector'])
                if 'target_validation_group_ops' in value:
                    case['collection_counters']=dict(case['collection_counters'],separate_curve_validation_group_ops=value['target_validation_group_ops'])
                if 'target_hash_group_ops' in value:
                    case['collection_counters']=dict(case['collection_counters'],separate_target_hash_group_ops=value['target_hash_group_ops'])
                if verification is not None:
                    if (verification.get('checked') is not True or verification.get('complete_branch_replay') is not True or
                        verification.get('hash_recipe_checked') is not True or verification.get('attempts_replayed')!=value['attempts'] or
                        verification.get('rows_verified')!=len(value['rows']) or verification.get('base_rank')!=quality['rank'] or
                        verification.get('augmented_rank')!=diagnostic['augmented_rank'] or
                        verification.get('target_identifiable')!=diagnostic['identifiable']):
                        raise ValueError('separate full hash/target verification mismatch')
                    case.update(verified=True,status='verified',verification_attempts=verification['attempts_replayed'])
                witness_events=[e['row'] for e in events if e.get('kind')=='verified_witness']
                multipliers=[e for e in events if e.get('kind')=='multiplier_complete']
                case['journal_complete']=len(multipliers)==64 and len(witness_events)==len(value['rows'])
                if case['journal_complete']:
                    if witness_events!=value['rows'] or recipes!=[recipe]:raise ValueError('target recipe/witness journal differs')
                    blocks=[dict(multiplier=e['multiplier'],attempts=e['attempts'],statuses=e['statuses'],branch_sha256=e['branch_sha256']) for e in multipliers]
                    if blocks!=value['status_blocks']:raise ValueError('multiplier journal differs from checked status blocks')
            elif verification is not None:raise ValueError('orphan target verification')
            cases.append(case)
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cases)
    analysis=dict(schema='d1-retained-target-analysis/v1',cells=cases,panel_complete=complete,unknown_cases=sum(c['status']=='unknown' for c in cases),
        collection_attempts_observed=sum(c['attempts'] or 0 for c in cases),verification_attempts_observed=sum(c['verification_attempts'] or 0 for c in cases),
        collection_attempts_lower_bound=sum(max(c['attempts'] or 0,c['attempts_lower_bound']) for c in cases),
        count_scope='Exact completed target-census attempts only; missing/partial cases are null and journal progress is a lower bound. Reference method duplicates must not be summed.',
        verification_scope='Independent recipe/branch/arithmetic certificate implementation check; counters not audited, not independent scientific review.',
        performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_d1_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','D1-natural-targets-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor')
    export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']})
    export['runs']=[]
    for case in cases:
        row=tools.run_row(run_id='D1-'+args.run.name+'-'+case['instance_id'],arm='natural_target',instance_id=case['instance_id'],seed=0,replicate=0,warmup=False,
            status='succeeded' if case['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status')=='failed' for p in case['phase_records']) else 'interrupted',
            measurements=dict(counted={k:case[k] for k in metric_ids if case[k] is not None},counters=case['collection_counters'] or {},
                wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolated clock']),
            verification=dict(status='verified' if case['verified'] else 'not_run',verifier='Separate full-EC1 hash recipe and complete target-branch/affine recovery replay; counters not independently checked'),
            started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner'])
        export['runs'].append(row);reference=copy.deepcopy(row);reference.update(run_id=row['run_id']+'-replay',arm='finite_replay');reference['measurements']['counters']={};export['runs'].append(reference)
    export['backend_record']=dict(physical_executions=1,shared_process_ownership='ownership.json',
        shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},
        phase_records=phases,wall_valid=False,counting_scope='Eight natural targets plus eight integrated reference method records share one physical process. Reference exact counts duplicate verification and must not be summed. Whole-process resources once here; partial counters only natural_target rows. Hash/collection/replay phases are components, not extra process costs.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export)
    print(json.dumps(dict(panel_complete=complete,unknown_cases=analysis['unknown_cases'])))


if __name__=='__main__':main()
