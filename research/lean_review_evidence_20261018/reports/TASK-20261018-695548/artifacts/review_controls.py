"""Independent real-Lean repair controls; every output uses this task directory.

Run after bootstrap-v2.py, with a fresh task scratch/output namespace for replay.
No producer directory is a command's working directory for a Lean invocation.
"""
from pathlib import Path
import contextlib,copy,hashlib,io,json,os,shutil,subprocess,sys,time

ART=Path(__file__).resolve().parent
SCRATCH=Path('/tmp/TASK-20261018-695548')
RUNTIME=SCRATCH/'runtime-v2'
FROZEN=Path('/workspace/lean-review-repairs')
REVIEW=Path('/workspace/review-lean-evidence')
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',
                  XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1',GIT_NO_LAZY_FETCH='1')
sys.path.insert(0,str(RUNTIME))
from orchestration.formal import cli
from orchestration.formal.receipts import receipt_errors,workspace_inputs
from orchestration.formal.targets import load_spec,task_from_spec

real_run=subprocess.run
rows=[]
def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def run(name,cmd,cwd,expected=0,env=None):
    dest=ART/'controls'/name;dest.mkdir(parents=True)
    start=time.monotonic()
    p=real_run(cmd,cwd=cwd,capture_output=True,text=True,timeout=180,env=env)
    (dest/'stdout.log').write_text(p.stdout);(dest/'stderr.log').write_text(p.stderr)
    row=dict(id=name,command=cmd,cwd=str(cwd),exit_code=p.returncode,expected_exit_code=expected,
             expectation_met=p.returncode==expected,elapsed_seconds=time.monotonic()-start)
    save_json(dest/'command.json',row);rows.append(row);print(name,p.returncode,flush=True)
    return p
def snapshot(root,dest):
    shutil.copytree(root,dest,ignore=shutil.ignore_patterns('.lake','.git','__pycache__'))
def write_spec(repo):
    spec=dict(schema='crypto.autoresearch.formal_task.v1',task_id='CONTROL-695548',
        claim_id='CONTROL-695548',kind='formalize_claim',claim='Engineering instrument control.',
        theorem_name='Control.good',theorem_file='CryptoResearch/Test.lean',
        workspace='formal',source='control-note.md')
    (repo/'spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    (repo/'control-note.md').write_text('Instrument control, no scientific assertion.\n')
def setup_cli(name,false=False,hidden=False):
    repo=SCRATCH/'cli'/name
    shutil.copytree(RUNTIME/'formal/smoke',repo/'formal')
    ws=repo/'formal';(ws/'CryptoResearch/Smoke.lean').unlink()
    shutil.copy2(RUNTIME/'formal/AxiomAudit.lean',ws/'AxiomAudit.lean')
    helper=ws/('.hidden/Helper.lean' if hidden else 'CryptoResearch/Helper.lean')
    helper.parent.mkdir(parents=True,exist_ok=True)
    helper.write_text('namespace Control\ndef P : Prop := '+('False' if false else 'True')+'\nend Control\n')
    target=ws/'CryptoResearch/Test.lean'
    target.write_text('import '+('Helper' if hidden else 'CryptoResearch.Helper')+'\nnamespace Control\ntheorem good : P := by trivial\nend Control\n')
    if hidden:
        with (ws/'lakefile.toml').open('a') as f:f.write('\n[[lean_lib]]\nname = "Helper"\nsrcDir = ".hidden"\n')
    write_spec(repo)
    return repo,helper,target
def cli_case(name,expected,false=False,hidden=False,hook=None):
    repo,helper,target=setup_cli(name,false=false,hidden=hidden)
    dest=ART/'controls'/name;dest.mkdir(parents=True)
    snapshot(repo,dest/'sources-before')
    calls=[];mutated=False
    def wrapper(cmd,*args,**kwargs):
        nonlocal mutated
        start=time.monotonic();p=real_run(cmd,*args,**kwargs)
        record={'command':list(cmd),'cwd':str(kwargs.get('cwd')),'exit_code':p.returncode,
                'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.monotonic()-start}
        calls.append(record)
        if hook and not mutated:
            mutated=bool(hook(cmd,repo,helper,target))
            if mutated:record['mutation_injected_after_command']=True
        return p
    out=dest/'receipt.json';stdout=io.StringIO();stderr=io.StringIO();start=time.monotonic()
    argv=['--repo-root',str(repo),'verify','--task-file',str(repo/'spec.json'),
          '--artifact-out',str(out),'--build-timeout','120']
    cli.subprocess.run=wrapper
    try:
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):rc=cli.main(argv)
    finally:cli.subprocess.run=real_run
    (dest/'stdout.log').write_text(stdout.getvalue());(dest/'stderr.log').write_text(stderr.getvalue())
    save_json(dest/'subprocesses.json',calls);snapshot(repo,dest/'sources-after')
    data=json.loads(out.read_text()) if out.exists() else None
    row={'id':name,'interface':'orchestration.formal.cli.main','argv':argv,'exit_code':rc,
         'expected_exit_code':expected,'expectation_met':rc==expected,'mutation_injected':mutated,
         'elapsed_seconds':time.monotonic()-start,'infrastructure_failure':data.get('infrastructure_failure') if data else None,
         'verification_status':(data.get('verification') or {}).get('status') if data else None,
         'target_before_sha256':hashlib.sha256((dest/'sources-before/formal/CryptoResearch/Test.lean').read_bytes()).hexdigest(),
         'target_after_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
         'workspace_inputs':data['provenance']['workspace_inputs'] if data else None}
    save_json(dest/'command.json',row);rows.append(row);print(name,rc,flush=True)
    return repo,data
def after_version(action):
    def hook(cmd,repo,helper,target):
        if list(cmd)==['lake','env','lean','--version']:
            action(repo,helper,target);return True
        return False
    return hook
def after_named(action):
    def hook(cmd,repo,helper,target):
        if any('TargetAudit-' in str(s) for s in cmd):action(repo,helper,target);return True
        return False
    return hook

# J3-F1: identical gate bytes at each public/shared entry point, real Lake.
for owner,rel in [('crypto-lean','tools/proof-gate.sh'),('crypto','tools/lean/proof-gate.sh'),
                  ('cryptanalysis','tools/lean/proof-gate.sh')]:
    for case in ['unconfigured-false','unconfigured-good','configured-good','configured-false']:
        name='gate-'+owner+'-'+case;repo=SCRATCH/'gates'/name;repo.mkdir(parents=True)
        gate=repo/rel;gate.parent.mkdir(parents=True);shutil.copy2(FROZEN/owner/rel,gate);gate.chmod(0o755)
        shutil.copy2(FROZEN/'crypto-lean/tools/AuditAxioms.lean',gate.parent/'AuditAxioms.lean')
        project=repo/'project';project.mkdir()
        (project/'lean-toolchain').write_text('leanprover/lean4:v4.35.0\n')
        (project/'lakefile.toml').write_text('name = "ReviewGate"\ndefaultTargets = ["Root"]\n[[lean_lib]]\nname = "Root"\n')
        (project/'Root.lean').write_text('theorem rootTrue : True := by trivial\n')
        (project/'Omitted.lean').write_text('theorem omittedTrue : True := by trivial\n' if case.endswith('good') else 'theorem omittedFalse : False := by sorry\n')
        if case.startswith('configured'):
            with (project/'lakefile.toml').open('a') as f:f.write('\n[[lean_lib]]\nname = "Omitted"\n')
        real_run(['git','init','-q'],cwd=repo,check=True);real_run(['git','add','.'],cwd=repo,check=True)
        snapshot(repo,ART/'control-sources'/name)
        expected=0 if case=='configured-good' else 1
        run(name,['bash',rel,'--out',str(ART/'gate-receipts'/name),'project'],repo,expected)

# J3-F3: original positive/false baseline and persistent input-set mutations.
baseline_repo,baseline=cli_case('cli-positive',0)
cli_case('cli-false-before',1,false=True)
cli_case('cli-loadbearing-import-mutated',3,false=True,
         hook=after_version(lambda r,h,t:h.write_text('namespace Control\ndef P : Prop := True\nend Control\n')))
cli_case('cli-added-source',3,hook=after_version(lambda r,h,t:(h.parent/'Added.lean').write_text('theorem added : True := by trivial\n')))
cli_case('cli-deleted-imported-source',3,hook=after_named(lambda r,h,t:h.unlink()))
cli_case('cli-target-mutated',3,hook=after_version(lambda r,h,t:t.write_text(t.read_text()+'\n-- persistent target change\n')))
cli_case('cli-audit-mutated',3,hook=after_version(lambda r,h,t:(r/'formal/AxiomAudit.lean').write_text((r/'formal/AxiomAudit.lean').read_text()+'\n-- changed audit\n')))
cli_case('cli-lakefile-mutated',3,hook=after_version(lambda r,h,t:(r/'formal/lakefile.toml').write_text((r/'formal/lakefile.toml').read_text()+'\n# changed config\n')))

# Additional attack on the promised complete local-source boundary: a normal
# Lake local source library whose configured srcDir is hidden, not a dependency.
cli_case('cli-hidden-positive',0,hidden=True)
cli_case('cli-hidden-false-before',1,false=True,hidden=True)
hidden_repo,hidden_data=cli_case('cli-hidden-loadbearing-mutated',3,false=True,hidden=True,
         hook=after_version(lambda r,h,t:h.write_text('namespace Control\ndef P : Prop := True\nend Control\n')))

# J3-F2: baseline is the actual CLI receipt above, then mutate individual fields.
spec=baseline_repo/'spec.json';task=task_from_spec(load_spec(spec))
attacks=[('verification','theorem_name','Wrong.name'),('verification','theorem_file','Wrong.lean'),
 ('verification','task_id','wrong-task'),('verification','forbidden_constructs',['sorry:forged']),
 ('verification','status','formalization_blocked'),('verification','build_passed',1),
 ('verification','axiom_audit_passed',1),('verification','blocking_reason','failure'),
 ('provenance','lean_version','bogus'),('provenance','workspace_inputs',{}),
 ('provenance','verifier_inputs',{}),(None,'build_log',''),(None,'audit_log',''),
 (None,'schema','wrong'),(None,'infrastructure_failure','failed')]
receipt_rows=[]
for section,key,value in [(None,'baseline',None),*attacks]:
    data=copy.deepcopy(baseline)
    if key!='baseline':(data[section] if section else data)[key]=value
    errors=receipt_errors(data,repo=baseline_repo,spec=spec,task=task)
    name='receipt-'+key
    dest=ART/'receipt-attacks'/name;dest.mkdir(parents=True)
    save_json(dest/'receipt.json',data)
    row={'id':name,'errors':errors,'expected_accepted':key=='baseline',
         'expectation_met':bool(errors)==(key!='baseline')}
    save_json(dest/'result.json',row);receipt_rows.append(row)
helper=baseline_repo/'formal/CryptoResearch/Helper.lean';helper_before=helper.read_bytes()
helper.write_text(helper.read_text()+'\n-- stale helper\n')
errors=receipt_errors(baseline,repo=baseline_repo,spec=spec,task=task)
receipt_rows.append({'id':'receipt-stale-helper','errors':errors,'expected_accepted':False,
                     'expectation_met':'local source inputs' in errors})
helper.write_bytes(helper_before)
save_json(ART/'receipt-attacks/results.json',receipt_rows)

# Exercise the active Node wrapper, not just the validator API.
study=baseline_repo/'research/lean_retrospective_20261018';study.mkdir(parents=True)
shutil.copy2(FROZEN/'crypto-autoresearcher/research/lean_retrospective_20261018/summarize.mjs',study/'summarize.mjs')
save_json(study/'inventory.json',{'revision':'engineering-control','targets':[{'spec':'spec.json'}]})
receipts=study/'receipts-v2';receipts.mkdir()
save_json(receipts/'control.json',baseline)
env={**os.environ,'PYTHON':sys.executable,'PYTHONPATH':str(RUNTIME)}
run('summary-wrapper-positive',['node',str(study/'summarize.mjs'),'--min-verified','1','--output',str(ART/'summary-positive.json')],baseline_repo,0,env)
forged=copy.deepcopy(baseline)
forged['verification'].update(theorem_name='Wrong.name',forbidden_constructs=['sorry:forged'])
forged['build_log']='';forged['audit_log']='';forged['provenance']['lean_version']='bogus'
(receipts/'control.json').write_text(json.dumps(forged,indent=2)+'\n')
run('summary-wrapper-original-forgery',['node',str(study/'summarize.mjs'),'--min-verified','1','--output',str(ART/'summary-forgery.json')],baseline_repo,1,env)
save_json(ART/'controls-results.json',{'controls':rows,'receipt_controls':receipt_rows})
print(json.dumps({'controls':len(rows),'unexpected':[r['id'] for r in rows if not r['expectation_met']],
                  'receipt_controls':len(receipt_rows),'receipt_unexpected':[r['id'] for r in receipt_rows if not r['expectation_met']]}))
