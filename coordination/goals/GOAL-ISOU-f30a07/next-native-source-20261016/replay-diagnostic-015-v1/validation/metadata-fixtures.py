"""Metadata-only parser fixtures, zero native/test/build invocations."""
from pathlib import Path
import importlib.util, json, shutil, copy, hashlib, datetime
import jsonschema
import sys
sys.path.insert(0,'/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools')
import experiment_execution
HA=Path('/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015')
P=HA/'coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/replay-diagnostic-015-v1'
sp=importlib.util.spec_from_file_location('receipt_adapter',P/'metadata.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
scratch=Path('/private/tmp/replay-diagnostic-metadata-fixtures-v5');scratch.mkdir(exist_ok=False)
m.HA=scratch/'ha';m.ROOT=scratch/'external';m.ROOT.mkdir();m.identity=lambda:True
m.B=copy.deepcopy(m.B)
(m.HA/Path(m.B['trial_plan']).parent).mkdir(parents=True,exist_ok=True)
shutil.copy(HA/m.B['trial_plan'],m.HA/m.B['trial_plan'])
source=Path('/Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/reference/controls/cache/valid-judge')
trace=source.parent/'valid.jsonl'
schema=json.loads((HA/'schemas/run-manifest.schema.json').read_text())
checks=[]
def prepare(index, mutate=False):
    t=m.B['trials'][index];t['trace']=True
    d=m.ROOT/t['run_id'];t['native_argv'][-3]=str(d/'native')
    m.begin(index)
    shutil.copytree(source,d/'native')
    shutil.copy(Path(m.B['inputs']['control']['path'])/'search.json',d/'native/artifact/search.json')
    shutil.copy(trace,d/'replay-trace.jsonl')
    r=json.loads((d/'native/verification.receipt.json').read_text())
    r['command']=[t['binary'],'challenge','__judge','--input',str(d/'native/artifact'),'--rss-ready',str(d/'native/resources-ready')]
    if mutate:
        v=json.loads((d/'native/verification.json').read_text());v['metadata_fixture_injected_field']=True
        (d/'native/verification.json').write_text(json.dumps(v))
        r['stdout_sha256']=hashlib.sha256((d/'native/verification.json').read_bytes()).hexdigest()
    e=json.loads((d/'native/entry.json').read_text());e['verification']=r;e['snapshot_search_sha256']=m.B['inputs']['control']['sha256']['search.json']
    (d/'native/verification.receipt.json').write_text(json.dumps(r));(d/'native/entry.json').write_text(json.dumps(e))
    (d/'os-time.txt').write_text('1.00 real 0.75 user 0.01 sys\n123456 maximum resident set size\n')
    (d/'stdout.log').write_text('metadata fixture only; retained native JSON inputs copied, no new invocation\n');(d/'stderr.log').write_text('')
    return d
d=prepare(0);assert m.finish(0,0);checks.append({'case':'retained_valid_native_bytes_with_fixture_path_receipt','accepted':True})
d=prepare(1,True);assert not m.finish(1,0);assert any('full mathematical JSON mismatch' in x for x in json.loads((d/'assessment.json').read_text())['errors']);checks.append({'case':'rehashed_math_change_rejected','accepted':False})
assert not m.finish(2,None,'metadata_fixture_dependency_nonstart');o=json.loads((m.ROOT/m.B['trials'][2]['run_id']/'assessment.json').read_text());assert not o['native_worker_started'] and o['native_exit_code'] is None
checks.append({'case':'genuine_nonstart_nullable_native_exit','accepted':False})
plan=json.loads((m.HA/m.B['trial_plan']).read_text());digest=hashlib.sha256((m.HA/m.B['trial_plan']).read_bytes()).hexdigest()
states=[experiment_execution.trial_state(m.HA,plan,plan['trials'][i],digest) for i in range(3)]
assert states==['output_validated','needs_reconciliation','output_validated'],states
old=HA/'experiments/EXP-ISOU-32a530/runs/RUN-ISOU-93b2b3'
t=m.B['trials'][32];d=m.ROOT/t['run_id'];m.begin(32);shutil.copytree(old/'native',d/'native');shutil.copy(old/'replay-trace.jsonl',d/'replay-trace.jsonl')
r=json.loads((d/'native/verification.receipt.json').read_text());r['command']=[t['binary'],'challenge','__judge','--input',str(d/'native/artifact'),'--rss-ready',str(d/'native/resources-ready')]
e=json.loads((d/'native/entry.json').read_text());e['verification']=r
(d/'native/verification.receipt.json').write_text(json.dumps(r));(d/'native/entry.json').write_text(json.dumps(e))
(d/'os-time.txt').write_text('3600.05 real 1716.81 user 62.75 sys\n250052608 maximum resident set size\n');(d/'stdout.log').write_text('metadata fixture only');(d/'stderr.log').write_text('')
assert m.finish(32,3)
o=json.loads((d/'assessment.json').read_text());assert not o['accepted'] and o['allow_next'] and o['native_exit_code'] is None and o['public_command_exit_code']==3
assert experiment_execution.trial_state(m.HA,plan,plan['trials'][32],digest)=='output_validated'
checks.append({'case':'synthetic_path_bound_retained_timeout_allows_scheduled_B_without_native_exit_fabrication','accepted':False,'allow_next':True})
for index in range(3):
    p=m.HA/'experiments'/m.B['experiment_id']/'runs'/m.B['trials'][index]['run_id']/'manifest.yaml'
    jsonschema.validate(json.loads(p.read_text()),schema)
result={'scope':'metadata-only copied/synthetic path/timing fixtures, not native results','native_invocations':0,'cryptographic_work':False,'checks':checks,'strict_current_run_schema_cases':3,'supported_coverage_states':states,'timeout_observation_coverage':'output_validated, native mathematical acceptance false','scratch':str(scratch),'retained_original_inputs_unchanged':True}
(scratch/'fixture-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
