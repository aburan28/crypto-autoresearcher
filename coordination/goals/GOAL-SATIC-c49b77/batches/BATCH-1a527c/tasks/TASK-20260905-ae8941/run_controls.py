#!/usr/bin/env python3
"""Write the terminal pre-execution receipt. Never invoke a solver or retry limits.

The Executor already performed the recorded limit probes through exec_command.
Both probes failed; the Coordinator instructed preservation without retry.
This once-only recorder intentionally stops at that frozen resource gate.
"""
import datetime
import hashlib
import itertools
import json
import pathlib
import platform
import subprocess
import sys
import time

START = time.monotonic()
ROOT = pathlib.Path.cwd()
HERE = pathlib.Path(__file__).resolve().parent
BATCH = HERE.parent.parent
CONTRACT_PATH = BATCH / 'contracts/readiness.json'
CONTRACT = json.loads(CONTRACT_PATH.read_text())
TASK = CONTRACT['task_id']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def git(*args):
    cmd = ['git', *args]
    t = time.monotonic()
    start = utc()
    p = subprocess.run(cmd, capture_output=True, timeout=10)
    return {'command': cmd, 'start_utc': start, 'end_utc': utc(),
            'elapsed_seconds': time.monotonic()-t, 'returncode': p.returncode,
            'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()}

for name in ['report.json', 'transcript.json']:
    if (HERE/name).exists():
        raise SystemExit('Refusing to overwrite existing artifact: '+name)

hard_probe = """import resource,platform
print(platform.platform())
for name in ['RLIMIT_AS','RLIMIT_RSS','RLIMIT_DATA']:
 try:
  r=getattr(resource,name); resource.setrlimit(r,(1073741824,1073741824)); print(name, resource.getrlimit(r))
 except Exception as e: print(name,type(e).__name__,str(e))
"""
soft_probe = """import resource
for n in ['RLIMIT_AS','RLIMIT_RSS','RLIMIT_DATA']:
 r=getattr(resource,n); print(n,resource.getrlimit(r))
 try: resource.setrlimit(r,(1073741824,resource.getrlimit(r)[1])); print('soft-only accepted',resource.getrlimit(r))
 except Exception as e: print(type(e).__name__,str(e))
"""
probe_outputs = [
    'macOS-26.6-arm64-arm-64bit-Mach-O\nRLIMIT_AS ValueError current limit exceeds maximum limit\nRLIMIT_RSS ValueError current limit exceeds maximum limit\nRLIMIT_DATA ValueError current limit exceeds maximum limit\n',
    'RLIMIT_AS (9223372036854775807, 9223372036854775807)\nValueError current limit exceeds maximum limit\nRLIMIT_RSS (9223372036854775807, 9223372036854775807)\nValueError current limit exceeds maximum limit\nRLIMIT_DATA (9223372036854775807, 9223372036854775807)\nValueError current limit exceeds maximum limit\n'
]
probes = []
for source, output in zip([hard_probe, soft_probe],probe_outputs):
    probes.append({'command': ['python3', '-'], 'stdin_utf8': source,
      'stdout_utf8': output, 'stderr_utf8': '', 'returncode': 0,
      'start_utc': None, 'end_utc': None, 'elapsed_seconds': None,
      'timing_unavailable_reason': 'Probe ran in an earlier exec_command shell batch; separate process timings and timestamps were not captured.',
      'capture_provenance': 'Executor transcribed the exact Python source and its output from tool receipts before writing this recorder; this recorder does not rerun probes.'})

fixtures = []
for f in CONTRACT['fixtures']:
    rows = []
    sat = []
    for bits in itertools.product([0,1], repeat=f['variables']):
        values = [any((bits[abs(l)-1] == 1) if l > 0 else (bits[abs(l)-1] == 0) for l in clause) for clause in f['clauses']]
        rows.append({'assignment': list(bits), 'clauses_satisfied': values, 'satisfies_formula': all(values)})
        if all(values): sat.append(list(bits))
    dimacs = 'p cnf %s %s\n' % (f['variables'],len(f['clauses']))
    dimacs += ''.join(' '.join(map(str,c))+' 0\n' for c in f['clauses'])
    fixtures.append({'id':f['id'], 'terminal_state':'cancelled_by_budget',
      'failure_class':'infrastructure_error',
      'reason':'Required 1 GiB memory cap could not be established before solver execution.',
      'input_status':'literal DIMACS prepared in memory only; no temporary fixture or solver invocation',
      'dimacs_utf8':dimacs, 'dimacs_sha256':sha(dimacs.encode()),
      'truth_table':rows,'enumerated_satisfying_assignments':sat,
      'frozen_assignments_match':sat == f['satisfying_assignments'],
      'solver_result':None,'sat_model':None,'model_clause_check':None,
      'command':None,'returncode':None,'stdout':None,'stderr':None,
      'start_utc':None,'end_utc':None,'elapsed_seconds':None,
      'memory_bytes':None,'memory_unavailable_reason':'Solver was never launched.'})

binary = pathlib.Path(CONTRACT['solver'])
try:
    binary_info = {'configured_path':str(binary),'resolved_path':str(binary.resolve(strict=True)),
                   'sha256':sha(binary.read_bytes()),'version_response':None,
                   'version_unavailable_reason':'Information invocation not performed after resource gate failure.'}
except OSError as e:
    binary_info = {'configured_path':str(binary),'resolved_path':None,'sha256':None,'read_error':str(e),'version_response':None}

planpath = pathlib.Path('/tmp/satic-ae8941-authority-plan.json')
plan = json.loads(planpath.read_text())
transcript = {'task_id':TASK,'recorded_at':utc(),
 'recorder_command':['python3',str(pathlib.Path(__file__).relative_to(ROOT))],
 'contract_path':str(CONTRACT_PATH.relative_to(ROOT)),'contract_sha256':sha(CONTRACT_PATH.read_bytes()),
 'authority_validation':{'command':['python3','tools/research_dispatch.py',str((BATCH/'authority_queue.json').relative_to(ROOT)), '--output','/tmp/satic-ae8941-authority-plan.json','--report','/tmp/satic-ae8941-authority-plan.md'], 'returncode':0,'stdout':'','stderr':'','plan':plan},
 'git':{'head':git('rev-parse','HEAD'),'dirty_state':git('status','--porcelain=v1'),
        'origin_main':git('rev-parse','origin/main')},
 'environment':{'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),
                'environment_variables':'Not collected; avoid credential exposure.'},
 'inference':{'requested_policy':'executor-implementation','requested_reasoning_effort':'medium',
   'runtime':'native Codex subagent','backend':'OpenAI native session',
   'resolved_model_id':None,'model_verified':False,
   'provenance_limitation':'Exact serving identifier and actual effort are not exposed to this agent; requested effort is not a measured runtime property.',
   'fallback_used':False,'degraded_requirements':[]},
 'resource_limit_probes':probes,'binary':binary_info,
 'solver_information_invocations':0,'solver_solve_invocations':0,'fixtures':fixtures,
 'randomness':CONTRACT['randomness'],
 'resource_cap':{'requested_bytes':1073741824,'established':False,
   'observed_exception':'ValueError: current limit exceeds maximum limit',
   'cause':'Undetermined. Tool output alone does not distinguish Python/macOS resource behavior from a sandbox restriction; no sandbox denial was reported.'},
 'protocol_deviations':['Required timestamps and isolated elapsed times for the preliminary resource probes were not captured; no values inferred.',
 'Runner records a pre-execution infrastructure stop; it does not implement or execute the solver phase after the failed gate.'],
 'recorder_elapsed_seconds':time.monotonic()-START}
report = {'task_id':TASK,'experiment_id':None,'kind':CONTRACT['kind'],
 'status':'failed_infrastructure','failure_class':'infrastructure_error',
 'reason':'Cannot establish the frozen 1 GiB memory cap with the attempted standard-library resource limits.',
 'implementation_commit':transcript['git']['head']['stdout'].strip(),
 'implementation_status':'New uncommitted stop-recorder; Coordinator snapshot pending.',
 'solver_information_invocations':0,'solver_solve_invocations':0,
 'runs':{'completed':[],'invalid':[], 'failed':[],
         'not_executed':[{'id':f['id'],'terminal_state':f['terminal_state'],'reason':f['reason']} for f in fixtures]},
 'observations':[{'fixture':f['id'],'frozen_assignments_match':f['frozen_assignments_match']} for f in fixtures],
 'protocol_deviations':transcript['protocol_deviations'],
 'anomalies':[transcript['resource_cap']],
 'artifact_paths':CONTRACT['required_artifacts'],
 'artifact_sha256':{'run_controls.py':sha(pathlib.Path(__file__).read_bytes())},
 'executor_assessment':{'protocol_complete':False,'data_quality':'limited','requires_rerun':False,
   'next_action':'Coordinator assessment of resource enforcement and new approved successor/amendment before any solver execution; this recorder must not be rerun.'},
 'scope':'Administrative pre-execution tooling failure only; no solver readiness pass and no mathematical observation or hypothesis conclusion.'}
with (HERE/'transcript.json').open('x') as out: json.dump(transcript,out,indent=2); out.write('\n')
report['artifact_sha256']['transcript.json']=sha((HERE/'transcript.json').read_bytes())
with (HERE/'report.json').open('x') as out: json.dump(report,out,indent=2); out.write('\n')
print(json.dumps({'status':report['status'],'solver_invocations':0,'artifacts':{p.name:sha(p.read_bytes()) for p in [pathlib.Path(__file__),HERE/'report.json',HERE/'transcript.json']}},indent=2))
