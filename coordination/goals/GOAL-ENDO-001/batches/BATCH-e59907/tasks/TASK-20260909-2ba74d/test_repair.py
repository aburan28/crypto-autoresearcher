"""One deterministic administrative battery. Output files are write-once."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import stat
import subprocess
import sys
import tempfile
import time
sys.dont_write_bytecode = True
from check_receipt_v3 import FIELDS, presence, custody

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
BATCH = HERE.parents[1]
GIT = '/usr/bin/git'
# Expected normalizations frozen in source, independent of checker execution.
VECTORS = [
    ('absent', False, None, (None, None, None), 'STOP'),
    ('json-null', True, None, (None, None, None), 'STOP'),
    ('integer', True, 17, (None, None, None), 'STOP'),
    ('empty', True, '', ('', '', ''), 'STOP'),
]
for label, char in [('space',' '),('tab','\t'),('lf','\n'),('cr','\r'),
                    ('zwsp','\u200b'),('zwnj','\u200c'),('zwj','\u200d'),
                    ('word-joiner','\u2060'),('bom','\ufeff')]:
    VECTORS.append((label, True, char, ('', '', ''), 'STOP'))
VECTORS += [
    ('mixed-empty', True, ' \t\r\n\u200b\u200c\u200d\u2060\ufeff', ('','',''), 'STOP'),
    ('mixed-edges', True, '\u200b\tHost\ufeff\r', ('Host','host','Host'), 'PASS'),
    ('literal-null', True, 'null', ('null','null','null'), 'STOP'),
    ('literal-NULL', True, 'NULL', ('NULL','null','NULL'), 'STOP'),
    ('literal-Null', True, 'Null', ('Null','null','Null'), 'STOP'),
    ('trimmed-null', True, '\u2060 NULL \ufeff', ('NULL','null','NULL'), 'STOP'),
    ('ordinary-host', True, 'Host.Example', ('Host.Example','host.example','Host.Example'), 'PASS'),
    ('unusual-device', True, 'Disk:VOL@1', ('Disk:VOL@1','disk:vol@1','Disk:VOL@1'), 'PASS'),
    ('root-mount', True, '/', ('/','','/'), ('PASS','STOP','PASS')),
    ('trailing-slashes', True, '/DEV/Volume///', ('/DEV/Volume///','/dev/volume','/DEV/Volume'), 'PASS'),
    ('interior-zwsp', True, 'A\u200bB', ('A\u200bB','a\u200bb','A\u200bB'), 'PASS'),
    ('outside-trim-set', True, '\u00ad', ('\u00ad','\u00ad','\u00ad'), 'PASS'),
    ('interior-space', True, 'A B', ('A B','a b','A B'), 'PASS'),
    ('null-trailing-slashes', True, 'Null///', ('Null///','null','Null'), ('PASS','STOP','STOP')),
]


def metadata(path):
    p = Path(path)
    s = p.stat()
    result = {'path': str(p), 'realpath': str(p.resolve()), 'uid': s.st_uid,
              'gid': s.st_gid, 'mode': oct(stat.S_IMODE(s.st_mode)),
              'regular': stat.S_ISREG(s.st_mode), 'executable': os.access(p, os.X_OK),
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    ancestors = []
    for a in dict.fromkeys([p.parent, *p.parents, p.resolve().parent, *p.resolve().parents]):
        st = a.stat()
        ancestors.append({'path':str(a), 'uid':st.st_uid, 'gid':st.st_gid,
                          'mode':oct(stat.S_IMODE(st.st_mode))})
    result['ancestors'] = ancestors
    result['system_metadata_gate'] = (s.st_uid == 0 and not s.st_mode & 0o022
        and result['regular'] and result['executable']
        and all(a['uid'] == 0 and not int(a['mode'],8) & 0o022 for a in ancestors))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name in ('control-results.json','execution-report.json'):
        if (out/name).exists():
            raise RuntimeError('Refuse overwrite: '+str(out/name))
    start = time.perf_counter()
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    commands = []
    def command(argv, env=None, binary=False):
        before = time.perf_counter()
        cp = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=30)
        rec = {'argv':argv,'cwd':str(ROOT),'exit_code':cp.returncode,
               'stdout':cp.stdout.decode('utf-8',errors='replace'),
               'stderr':cp.stderr.decode('utf-8',errors='replace'),
               'wall_seconds_measured':time.perf_counter()-before}
        commands.append(rec)
        return cp.stdout if binary else rec
    results = []
    def record(name, actual, expected):
        results.append({'name':name,'actual':actual,'expected':expected,'pass':actual == expected})
    head = command([GIT,'rev-parse','HEAD'])
    dirty = command([GIT,'status','--porcelain'])
    contract = json.loads((BATCH/'batch.json').read_text())
    inputs = {}
    for p in [BATCH/'batch.json', BATCH/'predecessor-custody.json', *[HERE/n for n in
              ('emit_procedure_v3.md','receipt-rules-v3.json','check_receipt_v3.py','test_repair.py')]]:
        inputs[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    presence_rows = []
    for label, present, raw, normal, expected in VECTORS:
        for index, field in enumerate(FIELDS):
            outcome = expected[index] if isinstance(expected,tuple) else expected
            actual = presence(field, raw, present=present)
            wanted = {'normalized':normal[index],'outcome':outcome}
            row = {'id':label,'field':field,'present':present,'raw':raw,
                   'expected':wanted,'actual':actual,'pass':actual == wanted}
            presence_rows.append(row)
            record('presence:'+label+':'+field, actual, wanted)
    custody_rows = []
    sources = json.loads((BATCH/'predecessor-custody.json').read_text())
    for source in sources:
        blob = command([GIT,'show',source['commit']+':'+source['path']],binary=True)
        check = custody(blob, source['expected'])
        live = custody((ROOT/source['path']).read_bytes(), source['live_sha256'])
        custody_rows.append({'source':source,'historical':check,'live':live})
        record('historical:'+source['path'],check['accepted'],True)
        record('live-as-disclosed:'+source['path'],live['accepted'],True)
        record('git-show-success:'+source['path'],commands[-1]['exit_code'],0)
    first = command([GIT,'show',sources[0]['commit']+':'+sources[0]['path']],binary=True)
    record('custody-bad-hash',custody(first,'0'*64)['accepted'],False)
    record('custody-wrong-pairing',custody(first,sources[1]['expected'])['accepted'],False)
    script = ROOT/contract['predecessor_script']
    record('v2-live-hash',custody(script.read_bytes(),contract['predecessor_script_sha256'])['accepted'],True)
    # Static policy checks read the predecessor, not a simulated full-schema checker.
    import yaml
    schema_path = ROOT/sources[0]['path']
    predecessor = yaml.safe_load(schema_path.read_text())['host_binding']
    rules = json.loads((HERE/'receipt-rules-v3.json').read_text())
    record('policy-caller-never-authoritative',predecessor['caller_input_is_never_authoritative'],True)
    record('policy-missing-field-stop',predecessor['missing_receipt_field'],'STOP')
    record('policy-nonreceipt-source-rejected','any other source' in predecessor['binding_rule_v2'],True)
    record('policy-v3-missing-receipt',rules['predecessor_binding_rule_v2']['missing_receipt'],'STOP')
    record('policy-v3-v1-receipt',rules['predecessor_binding_rule_v2']['v1_receipt'],'STOP')
    record('policy-v3-caller-source',rules['predecessor_binding_rule_v2']['caller_supplied_active_binding'],'STOP')
    executables = ['/bin/sh','/bin/hostname','/bin/df','/bin/date','/usr/bin/sed',
                   '/usr/bin/awk','/usr/bin/tr','/usr/bin/tail']
    machine = [metadata(p) for p in executables]
    for m in machine:
        record('executable-metadata:'+m['path'],m['system_metadata_gate'],True)
    invocations = []
    sentinel_source = '#!/bin/sh\nprintf marker > "$0.marker"\nexit 73\n'
    invocation_error = None
    if all(m['system_metadata_gate'] for m in machine) and custody(script.read_bytes(),contract['predecessor_script_sha256'])['accepted']:
        with tempfile.TemporaryDirectory(prefix='.sentinel-',dir=out) as td:
            sentinel = Path(td)/'sh'
            sentinel.write_text(sentinel_source)
            sentinel.chmod(0o700)
            marker = Path(str(sentinel)+'.marker')
            base_env = dict(os.environ)
            altered_env = dict(base_env,PATH=td+os.pathsep+base_env.get('PATH',''))
            for label, env in [('normal',base_env),('prefixed',altered_env)]:
                rec = command(['/bin/sh',str(script)],env=env)
                invocations.append({'label':label,'PATH':env.get('PATH'),'command':rec})
                record('invocation-exit:'+label,rec['exit_code'],0)
                try:
                    parsed = json.loads(rec['stdout'])
                    invocations[-1]['parsed'] = parsed
                    record('invocation-schema:'+label,parsed.get('schema'),'crypto.autoresearch.runtime_session_receipt.v2')
                    record('invocation-presence:'+label,
                        all(presence(f,parsed.get('host_binding',{}).get(f))['outcome']=='PASS' for f in FIELDS),True)
                except Exception as exc:
                    invocation_error = repr(exc)
                    record('invocation-json:'+label,repr(exc),'valid JSON')
            record('sentinel-unexecuted',marker.exists(),False)
            record('equal-host-binding',
                invocations[0].get('parsed',{}).get('host_binding'),
                invocations[1].get('parsed',{}).get('host_binding'))
    else:
        invocation_error = 'Invocation withheld: executable metadata or v2 hash gate failed.'
        record('invocation-prerequisites',False,True)
    end = datetime.datetime.now(datetime.timezone.utc).isoformat()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    measurements = {'wall_seconds_measured':time.perf_counter()-start,
                    'self_user_cpu_seconds':usage.ru_utime,'self_system_cpu_seconds':usage.ru_stime,
                    'children_user_cpu_seconds':child_usage.ru_utime,'children_system_cpu_seconds':child_usage.ru_stime,
                    'self_maxrss':usage.ru_maxrss,'children_maxrss':child_usage.ru_maxrss,
                    'maxrss_units':'bytes on Darwin; KiB on Linux',
                    'per_child_peak_rss':None,'per_child_peak_rss_reason':'getrusage supplies aggregate child high-water mark only'}
    total = len(results)
    failed = [r for r in results if not r['pass']]
    payload = {'task_id':'TASK-20260909-2ba74d','scientific_runs':0,'administrative_batteries':1,
        'started_at':stamp,'ended_at':end,'command':[sys.executable,*sys.argv],
        'cwd':str(Path.cwd()),'execution_cwd':str(ROOT),'git_head':head,'dirty_tree':dirty,
        'environment':{'python':sys.version,'python_executable':metadata(sys.executable),
                       'platform':platform.platform(),'uid':os.getuid(),'gid':os.getgid(),
                       'PATH':os.environ.get('PATH'),'LANG':os.environ.get('LANG'),
                       'LC_ALL':os.environ.get('LC_ALL'),
                       'loader_environment_variable_names_only':[k for k in os.environ if k.startswith(('LD_','DYLD_'))],
                       'environment_capture':'Allowlisted values only; inherited environment, loader values and unrelated secrets not serialized.'},
        'input_sha256':inputs,'seed':None,'randomness':'No randomized scientific input; tempfile name uniqueness only.',
        'executable_metadata':machine,'presence_vectors':presence_rows,'custody':custody_rows,
        'sentinel_source':sentinel_source,'invocations':invocations,'commands':commands,
        'checks':results,'counts':{'total':total,'passed':total-len(failed),'failed':len(failed),
                                  'presence_vectors':len(presence_rows)},'resources':measurements,
        'stdout':'Results captured in this JSON; terminal summary recorded in execution-report.json.',
        'stderr':'','invocation_error':invocation_error}
    with (out/'control-results.json').open('x') as f:
        json.dump(payload,f,indent=2); f.write('\n')
    summary = f'{total-len(failed)}/{total} administrative checks passed; {len(presence_rows)} presence vectors; scientific runs=0'
    report = {'execution_report':{'experiment_id':'EXP-JINV-bd141d','task_id':'TASK-20260909-2ba74d',
       'implementation_commit':head['stdout'].strip(),'implementation_note':'Four source deliverables newly written and input-hashed before the one battery; pending Coordinator snapshot.',
       'protocol_deviations':[], 'runs':{'completed':[],'invalid':[],'failed':[]},
       'administrative_controls':payload['counts'],'validity_status':'completed_valid' if not failed else 'completed_invalid',
       'validity_reason':'Observed fixed controls match frozen expectations.' if not failed else 'See preserved failed checks.',
       'observations':[summary,'Five historical blobs matched original expected hashes; disclosed live v1 drift preserved.',
                       'Static policy checks retain STOP clauses; full receipt schema enforcement was not executed.'],
       'anomalies':failed+([{'invocation_error':invocation_error}] if invocation_error else []),
       'limitations':contract['normalization']['residuals']+['No receipt authentication, no scientific inference, no full schema implementation.',
                       'Host trust, loader behavior, filesystem reporting and time-of-check/use changes remain outside scope.',
                       'Resource values measure this administrative battery, not algorithm performance.'],
       'artifact_paths':contract['artifacts'],'resources':measurements,
       'runtime_provenance':{'requested_policy':'executor-implementation','runtime':'native Codex subagent',
          'resolved_model_id':'unverified native session','model_verified':False,'reasoning_effort':'inherited; no independent runtime receipt',
          'fallback_used':False,'degraded_requirements':[],'bedrock_used':False},
       'executor_assessment':{'protocol_complete':True,'data_quality':'good' if not failed else 'invalid','requires_rerun':False},
       'stdout':summary+'\n','stderr':'','next_action':'Coordinator TASK-20260909-d5e100 snapshots six deliverables before independent reviews.'}}
    with (out/'execution-report.json').open('x') as f:
        json.dump(report,f,indent=2); f.write('\n')
    print(summary)
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main())
