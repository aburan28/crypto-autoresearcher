#!/usr/bin/env python3
"""Source-bound supervisor run/check/plan-only; never retries scientific work."""
from pathlib import Path
import argparse
import json
import sys
import tarfile
import hashlib
sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller as c


def check_transport(out):
    out = Path(out)
    record = c.read(out/'controller-receipt.json')
    c.need(record.get('schema') == c.SCHEMA+'controller-receipt/v1' and record.get('automatic_retry') is False and record.get('wall_valid') is False, 'receipt contract')
    entries = c.validate_entries(record['files'], record['plan']['limits'])
    for entry in entries:
        path = c.safe(out/'collected', entry['path'])
        c.need(path.is_file() and path.stat().st_size == entry['size'] and c.sha_file(path) == entry['sha256'], 'retained bytes differ')
    if record['status'] == 'complete':
        c.need(c.read(out/'custody.json') == c.custody_for(out/'collected', record), 'custody differs')
        c.need(record.get('engine_returncode') == 0 and record.get('vm_creates') == (0 if record.get('fixture_only') is True else 1) and record.get('engine_execs') == 1, 'complete operation counters')
    else:
        c.need(record['status'] == 'failed', 'operational state')
    return {'transport_evidence_integrity': True, 'operational_status': record['status'],
            'scientific_validity': 'not_assessed', 'wall_valid': False}


def seal_evidence(out):
    entries=[]
    for path in sorted((out/'modal').rglob('*')):
        c.need(not path.is_symlink(),'evidence symlink')
        if path.is_file():entries.append({'path':path.relative_to(out).as_posix(),'sha256':c.sha_file(path),'bytes':path.stat().st_size})
    manifest={'schema':c.SCHEMA+'supervisor-evidence/v1','files':entries}
    c.write(out/'modal-evidence-manifest.json',manifest)
    with (out/'modal-evidence.tar.gz').open('xb') as target:
        with tarfile.open(fileobj=target,mode='w|gz',dereference=False) as archive:
            for e in entries:archive.add(out/e['path'],arcname=e['path'],recursive=False)
    return {'path':'modal-evidence.tar.gz','sha256':c.sha_file(out/'modal-evidence.tar.gz'),
            'bytes':(out/'modal-evidence.tar.gz').stat().st_size,
            'member_manifest':'modal-evidence-manifest.json','member_manifest_sha256':c.sha_file(out/'modal-evidence-manifest.json')}


def run(repo,config_path,out,sdk=None,experiment_id=None,run_id=None):
    out=Path(out)
    c.need(isinstance(experiment_id,str) and experiment_id.startswith('EXP-') and isinstance(run_id,str) and run_id.startswith('RUN-'),'allocated supervisor IDs required')
    c.need(out.is_dir() and not any((out/name).exists() for name in ['modal','manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json']),'supervisor-provided fresh run_dir required')
    record=None;error=None
    try:
        config=config_path if isinstance(config_path,dict) else c.read(config_path)
        declared=c.read(Path(__file__).with_name('source-manifest.json'))
        c.write(out/'program-source.before.json',c.source_snapshot(repo,declared['files']))
        protocol=c.read(c.safe(repo,config['inputs']['protocol']['path']))
        c.need(protocol['protocol_id']==experiment_id,'allocated supervisor experiment differs from frozen protocol')
        record=c.run(repo,config_path,out/'modal',sdk=sdk,supervisor_identity={'experiment_id':experiment_id,'run_id':run_id})
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc)}
        # Keep readable declared protocol/static inputs even on pre-VM refusal.
        modal=out/'modal';modal.mkdir(exist_ok=True)
        try:
            config=config_path if isinstance(config_path,dict) else c.read(config_path)
            if not (modal/'config.json').exists():c.write(modal/'config.json',config)
            for role,binding in config.get('inputs',{}).items():
                if role not in {'protocol','image_receipt','engine_plan','prior_exclusions','worker_manifest','host_manifest','engine_interface','host_interface'}:continue
                path=c.safe(repo,binding['path'])
                if path.is_file() and not (modal/(role+'.json')).exists() and path.stat().st_size<=64<<20:
                    with (modal/(role+'.json')).open('xb') as target:target.write(path.read_bytes())
        except Exception as snapshot_error:error['snapshot_error']={'type':type(snapshot_error).__name__,'message':str(snapshot_error)}
        c.write(modal/'controller-error.json',error)
    declared=c.read(Path(__file__).with_name('source-manifest.json'))
    c.write(out/'program-source.after.json',c.source_snapshot(repo,declared['files']))
    evidence=seal_evidence(out)
    complete=record is not None and record.get('status')=='complete' and error is None
    raw={'schema':c.SCHEMA+'supervisor-trial/v1','controller':record,'driver_error':error,'evidence':evidence,
         'experiment_id':experiment_id,'run_id':run_id,'operational_status':'completed' if complete else 'failed','scientific_validity':'not_assessed',
         'independent_public_verification':False,'analysis_executed':False,'attack_claimed':False,
         'automatic_retry':False,'maximum_scientific_attempts':1,'all_clocks_wall_valid':False,'program_source_captures':{n:c.sha_file(out/n) for n in ('program-source.before.json','program-source.after.json')}}
    c.write(out/'raw-result.json',raw)
    # Complete JSON envelope: native helper must preserve exact bytes (unchanged).
    launch=c.read(out/'launch.json');environment=c.read(out/'environment.json')
    import datetime
    body={'id':run_id,'experiment_id':experiment_id,'task_id':launch.get('task_id',config.get('task_id')),'trial_id':launch['trial_id'],'approved_by':config.get('approved_by'),'status':raw['operational_status'],'attack_claimed':False,
        'code':{'commit':launch['authority']['commit'],'command':launch['argv'],'check_command':launch['check_argv'],'command_file':'command.txt','instrument_source_binding':'full SHA and bytes captured; source-context revision is not an execution-source commit'},
        'environment':{'file':'environment.json',**environment},'inputs':{'trial_plan':config['trial_plan'],'plan_sha256':launch['plan_sha256'],'trial_id':launch['trial_id'],'parameters':config['trial_parameters']},
        'timing':{'started_at':launch['started_at'],'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},
        'result':{'raw_result':'raw-result.json','certificate':{'kind':'none','verified':None}},'metrics':{'transport_complete':complete,'scientific_validity':'not_assessed','all_clocks_wall_valid':False}}
    c.write(out/'manifest.yaml',{'run':body})
    return raw


def check(out, allow_inner=False):
    out=Path(out)
    if not (out/'raw-result.json').exists():
        c.need(allow_inner is True, 'supervisor envelope required; inner transport mode must be explicit')
        result=check_transport(out)
        result['integrity_scope']='inner_transport_only'
        return result
    raw=c.read(out/'raw-result.json');evidence=raw['evidence']
    for name,digest in raw['program_source_captures'].items():c.need(c.sha_file(out/name)==digest,'program source capture binding')
    captures=[c.read(out/n)['files'] for n in ('program-source.before.json','program-source.after.json')]
    c.need(captures[0]==captures[1],'program source changed during execution')
    for record in captures[0].values():
        data=__import__('base64').b64decode(record['base64'],validate=True)
        c.need(len(data)==record['bytes'] and c.sha_bytes(data)==record['sha256'],'captured full program bytes')
    c.need(type(raw.get('attack_claimed')) is bool and raw['attack_claimed'] is False,'typed false attack claim')
    run_manifest=c.read(out/'manifest.yaml')['run']
    identity={'experiment_id':raw.get('experiment_id'),'run_id':raw.get('run_id')}
    c.need(isinstance(identity['experiment_id'],str) and identity['experiment_id'].startswith('EXP-') and isinstance(identity['run_id'],str) and identity['run_id'].startswith('RUN-'), 'allocated supervisor IDs required')
    c.need(run_manifest.get('id')==identity['run_id'] and run_manifest.get('experiment_id')==identity['experiment_id'] and run_manifest.get('status')==raw.get('operational_status'), 'manifest/supervisor identity or status mismatch')
    protocol_path=out/'modal/protocol.json'
    if protocol_path.exists():
        c.need(c.read(protocol_path).get('protocol_id')==identity['experiment_id'], 'supervisor/protocol experiment mismatch')
    else:
        c.need(raw.get('controller') is None and raw.get('driver_error') is not None and raw.get('operational_status')=='failed', 'protocol snapshot required')

    c.need(raw['schema']==c.SCHEMA+'supervisor-trial/v1' and raw['automatic_retry'] is False and raw['all_clocks_wall_valid'] is False,'supervisor contract')
    c.need(evidence['path']=='modal-evidence.tar.gz' and evidence['member_manifest']=='modal-evidence-manifest.json','fixed archive paths')
    archive_path=out/evidence['path'];member_path=out/evidence['member_manifest']
    c.need(c.sha_file(archive_path)==evidence['sha256'] and archive_path.stat().st_size==evidence['bytes'] and c.sha_file(member_path)==evidence['member_manifest_sha256'],'evidence archive hashes')
    manifest=c.read(member_path)
    c.need(manifest.get('schema')==c.SCHEMA+'supervisor-evidence/v1' and isinstance(manifest.get('files'),list), 'supervisor member manifest contract')
    for e in manifest['files']:
        c.need(set(e)=={'path','sha256','bytes'} and isinstance(e['path'],str) and e['path'].startswith('modal/') and c.HEX.fullmatch(e['sha256']) and type(e['bytes']) is int and e['bytes']>=0,'archive entry contract')
        c.safe(out,e['path'])
    expected={e['path']:e for e in manifest['files']}
    live=set()
    for path in (out/'modal').rglob('*'):
        c.need(not path.is_symlink() and (path.is_file() or path.is_dir()),'unsafe live supervisor tree')
        if path.is_file():live.add(path.relative_to(out).as_posix())
    c.need(live==set(expected),'unbound or missing supervisor tree member')
    c.need(len(expected)==len(manifest['files']),'duplicate archive members')
    seen=set()
    with tarfile.open(archive_path,'r|gz') as archive:
        for member in archive:
            c.safe(out,member.name)
            c.need(member.name.startswith('modal/') and member.name in expected and member.name not in seen and member.isfile(),'unsafe archive member')
            seen.add(member.name);entry=expected[member.name];digest=hashlib.sha256()
            source=archive.extractfile(member)
            for block in iter(lambda:source.read(1<<20),b''):digest.update(block)
            path=c.safe(out,member.name)
            c.need(member.size==entry['bytes'] and digest.hexdigest()==entry['sha256'] and path.is_file() and c.sha_file(path)==entry['sha256'],'archive/member/local mismatch')
    c.need(seen==set(expected),'archive incomplete')
    receipt=out/'modal/controller-receipt.json'
    if raw['controller'] is not None:
        c.need(receipt.is_file() and c.read(receipt)==raw['controller'],'controller receipt duplicate mismatch')
        c.need(type(raw['controller'].get('engine_returncode')) is int,'primitive engine returncode integer')
        c.need(raw['controller'].get('supervisor_identity')==identity,'controller/supervisor identity mismatch')
        status=check_transport(out/'modal')['operational_status']
    else:
        c.need(not receipt.exists() and (out/'modal/controller-error.json').is_file() and raw.get('driver_error') is not None,'failed controller envelope mismatch')
        status='failed'
    c.need(raw['operational_status']==('completed' if status=='complete' and raw['driver_error'] is None else 'failed'),'supervisor operational status')
    return {'transport_evidence_integrity':True,'operational_status':status,'scientific_validity':'not_assessed','wall_valid':False,'integrity_scope':'complete_supervisor','run_id':identity['run_id'],'experiment_id':identity['experiment_id']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['run','check','plan-only'])
    p.add_argument('--repo-root',type=Path)
    p.add_argument('--config',type=Path,help='optional already constructed invocation wrapper; canonical readiness uses explicit input flags')
    for name in ['protocol','image-receipt','compute-plan','prior-exclusions','worker-manifest','host-manifest','engine-interface','host-interface']:
        p.add_argument('--'+name)
    p.add_argument('--trial-plan',type=Path)
    p.add_argument('--trial-id')
    p.add_argument('--experiment-id')
    p.add_argument('--run-id')
    p.add_argument('--out',type=Path)
    p.add_argument('--allow-inner-transport',action='store_true',help='check only an explicitly supplied standalone inner transport tree; no supervisor qualification')
    a=p.parse_args()
    if a.action=='check':
        p.error('--out required') if a.out is None else None
        result=check(a.out,allow_inner=a.allow_inner_transport)
        print(json.dumps(result,sort_keys=True))
        return 0 if result['operational_status']=='complete' else 1
    if a.repo_root is None:p.error('--repo-root required')
    config=a.config
    if config is None:
        paths={k:getattr(a,n) for k,n in [('protocol','protocol'),('image_receipt','image_receipt'),('engine_plan','compute_plan'),('prior_exclusions','prior_exclusions'),('worker_manifest','worker_manifest'),('host_manifest','host_manifest'),('engine_interface','engine_interface'),('host_interface','host_interface')]}
        if any(v is None for v in paths.values()):p.error('all eight frozen input flags required')
        config=c.invocation_config(a.repo_root,paths)
    if a.action=='plan-only':
        print(json.dumps(c.make_plan(a.repo_root,config)[0],sort_keys=True)); return 0
    if a.out is None: p.error('--out required')
    if not a.experiment_id or not a.run_id:p.error('--experiment-id and --run-id required')
    c.need(a.trial_plan is not None and a.trial_id,'actual native trial context required')
    config=c.read(config) if not isinstance(config,dict) else dict(config)
    frozen=c.read(a.trial_plan);trial=next(t for t in frozen['trials'] if t['id']==a.trial_id)
    config.update(trial_plan=str(a.trial_plan.resolve().relative_to(a.repo_root.resolve())),trial_parameters=trial.get('parameters',{}),approved_by=frozen.get('approved_by'),task_id=frozen.get('task_id'))
    result=run(a.repo_root,config,a.out,experiment_id=a.experiment_id,run_id=a.run_id)
    print(json.dumps({'status':result['operational_status'],'automatic_retry':False,'wall_valid':False}))
    return 0 if result['operational_status']=='completed' else 1


if __name__=='__main__': raise SystemExit(main())
