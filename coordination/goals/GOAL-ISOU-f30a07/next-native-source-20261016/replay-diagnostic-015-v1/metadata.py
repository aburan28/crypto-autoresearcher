#!/usr/bin/env python3
"""Receipt/hash/JSON metadata only. Never launches a native test or math process."""
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
HA = HERE.parents[4]
B = json.loads((HERE / 'bindings.json').read_text())
SOURCE = B['source_commit']
ROOT = Path(B['output_root'])

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save(p, v):
    with Path(p).open('x') as f:
        json.dump(v, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')

def load(p):
    return json.loads(Path(p).read_text())

def identity():
    for item in B['files']:
        p = Path(item['path'])
        if not p.is_absolute():
            p = HA / p
        assert p.is_file() and p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], str(p)
    plan = load(HA / B['trial_plan'])
    assert sha(HA / plan['specification']) == plan['specification_sha256']
    for p, h in plan['source_sha256'].items():
        assert sha(HA / p) == h, p
    return True

def trial(index):
    t = B['trials'][int(index)]
    d = ROOT / t['run_id']
    c = HA / 'experiments' / B['experiment_id'] / 'runs' / t['run_id']
    return t, d, c

def trace_check(path, required_complete, pid):
    rows = [json.loads(s) for s in path.read_text().splitlines()]
    assert rows and rows[0]['stage'] == 'total' and rows[0]['event'] == 'begin'
    stack = []
    seen = set()
    last = -1
    terminal = None
    for r in rows:
        assert r['schema'] == 'isogeny-replay-stage/v1' and r['pid'] == pid
        assert r['elapsed_ms_operational_only'] >= last
        last = r['elapsed_ms_operational_only']
        assert terminal is None
        if r['event'] == 'begin':
            assert r['stage_id'] not in seen and r['parent_id'] == (stack[-1][0] if stack else None)
            seen.add(r['stage_id'])
            stack.append((r['stage_id'], r['stage']))
        elif r['event'] in ('end', 'error'):
            assert stack and stack.pop() == (r['stage_id'], r['stage'])
        elif r['event'] == 'terminal':
            assert not stack and r['stage'] == 'total'
            terminal = r['status']
        else:
            raise AssertionError('unknown trace event')
    if required_complete:
        assert terminal == 'COMPLETED' and not stack
    return {'records': len(rows), 'terminal': terminal, 'unfinished_stages': [s for _, s in stack],
            'last_operational_ms': last, 'sha256': sha(path)}

def os_time(path):
    s = path.read_text()
    m = re.search(r'([0-9.]+)\s+real\s+([0-9.]+)\s+user\s+([0-9.]+)\s+sys', s)
    if m:
        out=dict(zip(('real_seconds','user_seconds','system_seconds'), map(float,m.groups())))
        peak=re.search(r'(\d+)\s+maximum resident set size',s)
        out['maximum_resident_set_bytes']=int(peak.group(1)) if peak else None
        return out
    m = re.search(r'([0-9.]+)\s+real\s+([0-9.]+)\s+user\s+([0-9.]+)\s+sys', s.replace('\n',' '))
    assert m, 'OS time receipt missing; preserve raw and block dependents'
    return dict(zip(('real_seconds','user_seconds','system_seconds'), map(float,m.groups())))

def begin(index):
    identity()
    t,d,c = trial(index)
    d.mkdir()
    c.mkdir(parents=True, exist_ok=False)
    env = {'schema':'isogeny-native-diagnostic-environment/v1','collected_at':stamp(),
           'source_commit':SOURCE,'source_dirty':False,'binary_sha256':t['binary_sha256'],
           'compiled_reduction_policy':t['compiled_reduction_policy'],'shared_host':True,
           'uname':list(os.uname()),'load_average':list(os.getloadavg()),
           'actual_served_model':None,'actual_served_effort':None,
           'native_argv':t['native_argv'],'trace':t['trace'],
           'trace_environment':str(d/'replay-trace.jsonl') if t['trace'] else None,
           'evidence_root':str(d),'cpu_scope':'OS public command plus descendants; not per-stage CPU'}
    save(c/'environment.json',env)
    (c/'command.txt').write_text(shlex.join(t['native_argv'])+'\n')
    save(d/'begin.json',{'invocation_requested_at':stamp(),'monotonic_ns':time.monotonic_ns(),
                         'native_argv':t['native_argv'],'index':int(index)})

def finish(index, rc, blocked=None):
    t,d,c = trial(index)
    if blocked is not None:
        d.mkdir()
        c.mkdir(parents=True,exist_ok=False)
        save(c/'environment.json',{'native_process_started':False,'reason':blocked,'shared_host':True})
        (c/'command.txt').write_text(shlex.join(t['native_argv'])+'\n')
        start = stamp()
        elapsed = 0.0
    else:
        first = load(d/'begin.json')
        start = first['invocation_requested_at']
        elapsed = (time.monotonic_ns()-first['monotonic_ns'])/1e9
    errors = []
    entry = None
    receipt = None
    pid = None
    native_exit = None
    trace = None
    timing = None
    started = False if blocked is not None else None
    accepted = False
    allowed = False
    try:
        identity()
        if blocked is None:
            pidfile=d/'native/verification.pid'
            if pidfile.exists():
                pid=int(pidfile.read_text().strip())
                started=True
            if (d/'native/verification.receipt.json').exists():
                receipt=load(d/'native/verification.receipt.json')
                native_exit=receipt.get('exit_code')
            if (d/'native/entry.json').exists():
                entry=load(d/'native/entry.json')
                if pid is None and entry.get('status')=='REJECTED':
                    started=False
            assert rc not in (124,125,126,127,137), 'outer command incomplete; actual native exit unavailable'
            assert entry is not None and receipt is not None and pid is not None, 'missing required native receipt/PID'
            assert receipt['command']==[t['binary'],'challenge','__judge','--input',str(d/'native/artifact'),'--rss-ready',str(d/'native/resources-ready')]
            assert entry['verification']==receipt
            try:
                os.kill(pid,0)
            except ProcessLookupError:
                pass
            else:
                raise AssertionError('native worker PID still present; no dependent start')
            for stream in ('stdout','stderr'):
                p = d/'native'/receipt[stream] if stream in receipt else d/'native'/('verification.'+('json' if stream=='stdout' else 'stderr.txt'))
                assert sha(p) == receipt[stream+'_sha256'], str(p)
            assert int(receipt['resident_memory_limit_bytes']) == 8<<30
            assert receipt['memory_sampling_interval_ms'] == 25 and receipt['memory_monitor_grace_ms'] == 100
            assert int(receipt['sampled_peak_resident_bytes']) > 0
            assert isinstance(receipt['unavailable_memory_samples'], int)
            assert entry['season'] == B['season']
            inp = B['inputs'][t['input_key']]
            # Judge copies all three immutable input bytes before replay.
            for rel,h in inp['sha256'].items():
                assert sha(d/'native/artifact'/rel) == h
            accepted = entry['status']=='ACCEPTED' and receipt['status']=='PASS' and rc==0 and native_exit==0
            censor = entry['status']=='CENSORED' and receipt['status'] in ('TIMEOUT','MEMORY_LIMIT') and rc==3
            if accepted:
                assert entry['judge_binary_sha256']==t['binary_sha256']
                assert entry['tool']['git_commit']==SOURCE and entry['tool']['git_dirty']=='false'
                assert entry['tool']['standards_sha256']==B['standards_sha256']
                assert entry['prime_degree']==str(t['ell']) and entry['score']==str(t['ell'])
                assert entry['source_icv1']==t['curve_id'] and entry['map_sha256']==inp['map_sha256']
                assert entry['snapshot_search_sha256']==inp['sha256']['search.json']
                verified = load(d/'native/verification.json')
                assert verified['status']=='PASS' and verified['ell']==str(t['ell'])
                assert verified['source_icv1']==t['curve_id'] and verified['map_sha256']==inp['map_sha256']
                fc = verified['fresh_certificate']
                assert fc['status']=='PASS' and fc['degree_coverage']=='PARTIAL' and len(fc['records'])==1
                assert all(r['status']=='PASS' and r['public_scalar_transport_checks']==20 and r['source_icv1']==t['curve_id'] and r['ell']==t['ell'] for r in fc['records'])
                for prior in B['trials'][:int(index)]:
                    if prior['input_key'] == t['input_key']:
                        p=ROOT/prior['run_id']/'native/verification.json'
                        if p.exists() and load(ROOT/prior['run_id']/'assessment.json')['accepted']:
                            assert p.read_bytes()==(d/'native/verification.json').read_bytes(), 'full mathematical JSON mismatch; no field exclusions'
            if t['trace']:
                trace=trace_check(d/'replay-trace.jsonl',accepted,pid)
            else:
                assert not (d/'replay-trace.jsonl').exists()
            timing=os_time(d/'os-time.txt')
            assert accepted or (t['input_key']=='target' and censor), 'semantic/control/resource-monitor failure blocks dependents'
            allowed=True
    except Exception as e:
        errors.append(type(e).__name__+': '+str(e)+'\n'+traceback.format_exc())
    if blocked is not None:
        errors.append('NOT_STARTED: '+blocked)
    for src,dst in [('stdout.log','native.stdout.log'),('stderr.log','native.stderr.log')]:
        (c/dst).write_bytes((d/src).read_bytes() if (d/src).exists() else b'')
    status='completed_valid' if accepted and not errors else ('resource_exhaustion' if allowed and not errors else 'failed_infrastructure')
    if entry and entry.get('status')=='REJECTED':
        status='completed_invalid'
    out={'schema':'isogeny-native-diagnostic-observation/v1','run_id':t['run_id'],'native_worker_started':started,
         'native_worker_pid':pid,'native_exit_code':native_exit,'outer_command_exit_code':rc,
         'public_command_exit_code':rc if rc not in (None,124,125,126,127,137) else None,
         'entry':entry,'resource_receipt':receipt,'trace':trace,'os_time':timing,
         'accepted':accepted and not errors,'allow_next':allowed and not errors,'errors':errors,
         'started_at':start,'finished_at':stamp(),'wrapper_observation_seconds':elapsed,
         'verdict_scope':'observation only; independent review and Coordinator decision required'}
    save(d/'assessment.json',out)
    save(c/'raw-result.json',out)
    cpu=None if timing is None else timing['user_seconds']+timing['system_seconds']
    manifest={'run':{'id':t['run_id'],'experiment_id':B['experiment_id'],'status':status,
      'code':{'commit':SOURCE,'dirty':False,'command':shlex.join(t['native_argv'])},
      'environment':load(c/'environment.json'),
      'inputs':{'curve_id':t['curve_id'],'seed':0,'parameters':{'ell':t['ell'],'arm':t['arm'],'trace':t['trace'],'input_key':t['input_key']}},
      'timing':{'started_at':start,'finished_at':out['finished_at'],'wall_seconds':elapsed},
      'resources':{'peak_rss_bytes':int(receipt['sampled_peak_resident_bytes']) if receipt else None,'cpu_seconds':cpu},
      'result':{'metrics':out,'valid':accepted and not errors,'invalid_reason':'; '.join(errors) if errors else (None if accepted else 'bounded native resource censor'),
                'certificate':{'kind':'none','verified':None,'verifier':None}},
      'artifacts':{x:x for x in ('command.txt','environment.json','raw-result.json','native.stdout.log','native.stderr.log')}}}
    save(c/'manifest.yaml',manifest)  # JSON is a YAML subset, strict current schema.
    # Supported trial coverage describes successful observation emission, never
    # substitutes that status/return code for the separately recorded native exit.
    observation_code=0 if out['allow_next'] or blocked is not None else 3
    for a,b in [('native.stdout.log','stdout.log'),('native.stderr.log','stderr.log')]:
        (c/b).write_bytes((c/a).read_bytes())
    save(c/'launch.json',{'schema':'isogeny-native-shell-launch/v1','native_argv':t['native_argv'],
                         'native_worker_started':started,'started_at':start,'source_commit':SOURCE,
                         'launcher':'frozen direct shell; metadata Python launches no subprocess'})
    save(c/'check.stdout.log',{'scope':'metadata observation validation only','allow_dependent_start':out['allow_next'],
                              'native_worker_started':started,'native_exit_code':native_exit,'errors':errors})
    (c/'check.stderr.log').write_text('\n'.join(errors)+ ('\n' if errors else ''))
    names=('manifest.yaml','raw-result.json','native.stdout.log','native.stderr.log','launch.json','command.txt',
           'environment.json','stdout.log','stderr.log','check.stdout.log','check.stderr.log')
    save(c/'execution-receipt.json',{'schema':'crypto.autoresearch.trial_receipt.v1',
       'plan_sha256':sha(HA/B['trial_plan']),'trial_id':'native-'+str(index),'run_id':t['run_id'],
       'status':'output_validated' if observation_code==0 else 'invalid_output',
       'returncode':observation_code,'check_returncode':observation_code,
       'returncode_scope':'Actual metadata observation-driver return, NOT native/public command exit; native resource censor is a retained observation.',
       'native_exit_code':native_exit,'outer_command_exit_code':rc,'native_worker_started':started,
       'scientific_admission':accepted and not errors,'artifact_sha256':{p:sha(c/p) for p in names}})
    return out['allow_next']

def summary():
    observations=[load(ROOT/t['run_id']/'assessment.json') for t in B['trials']]
    controls=observations[:32]
    summaries=[]
    for arm in ('reference','candidate'):
        for trace in (False,True):
            rows=[o for t,o in zip(B['trials'],observations) if t['input_key']=='control' and t['arm']==arm and t['trace']==trace and o['accepted']]
            values=[o['os_time']['real_seconds'] for o in rows]
            summaries.append({'arm':arm,'trace':trace,'n':len(rows),'metric':'public_command_OS_real_seconds',
                              'q90_nearest_rank':sorted(values)[math.ceil(.9*len(values))-1] if len(values)==8 else None,
                              'q90_rule':'rank ceil(0.9*n), one-based; n8 rank8; no interpolation/drop',
                              'scope':'P2241471 descriptive repeat spread/instrumentation only, not speed claim or A/A'})
    save(ROOT/'summary.json',{'experiment':B['experiment_id'],'observations':observations,'control_summaries':summaries,
         'all_control_pairs_valid':all(o['accepted'] for o in controls),'scientific_promotion':False,'speed_claim':False,
         'historical_constructor_cost':'retained old input setup, not fresh cold pipeline denominator'})

def main():
    mode=sys.argv[1]
    if mode=='preflight':
        assert Path(sys.argv[2])==ROOT and not ROOT.exists() and not ROOT.is_symlink()
        assert not os.environ.get('ISOGENY_REPLAY_TRACE'), 'ambient trace override forbidden'
        identity()
        for t in B['trials']:
            assert not (HA/'experiments'/B['experiment_id']/'runs'/t['run_id']).exists()
    elif mode=='begin': begin(sys.argv[2])
    elif mode=='finish': return 0 if finish(sys.argv[2],int(sys.argv[3])) else 3
    elif mode=='nonstart': finish(sys.argv[2],None,sys.argv[3])
    elif mode=='summary': summary()
    elif mode=='check':
        assert (ROOT/'summary.json').is_file()
        for t in B['trials']:
            assert (ROOT/t['run_id']/'assessment.json').is_file()
    elif mode=='check-trial':
        t,d,c=trial(sys.argv[2])
        assert load(d/'assessment.json')['run_id']==t['run_id']
        for p in ('manifest.yaml','raw-result.json','environment.json','command.txt','native.stdout.log','native.stderr.log'):
            assert (c/p).is_file()
    else: raise ValueError('unknown metadata mode')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
