from pathlib import Path
import os,sys,json,subprocess,time,shutil,argparse,hashlib
S=Path('/tmp/j3-lean-review');O=Path('/workspace/review-lean-evidence/research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts');F=Path('/workspace/lean-review-inputs');R=Path('/workspace/review-lean-evidence')
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1');sys.path.insert(0,str(R));from orchestration.formal import cli
rows=[]
def run(name,cmd,cwd):
 start=time.time();r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=120);(O/(name+'.stdout.log')).write_text(r.stdout);(O/(name+'.stderr.log')).write_text(r.stderr);d=dict(name=name,command=cmd,cwd=str(cwd),exit_code=r.returncode,elapsed_seconds=time.time()-start);rows.append(d);(O/'additional-commands.json').write_text(json.dumps(rows,indent=2)+'\n');print(name,r.returncode,flush=True);return r
repo=S/'shared-gate';repo.mkdir(exist_ok=True);(repo/'lean-toolchain').write_text('leanprover/lean4:v4.35.0\n');shutil.copytree(F/'crypto-lean/tools',repo/'tools',dirs_exist_ok=True);run('shared-git-init',['git','init','-q'],repo)
run('shared-selftest',['bash','tools/selftest/run.sh'],repo)
p=repo/'project';p.mkdir(exist_ok=True);(p/'lakefile.toml').write_text('name = "GateControl"\ndefaultTargets = ["Root"]\n[[lean_lib]]\nname = "Root"\n');(p/'Root.lean').write_text('theorem innocent : True := True.intro\n');(p/'Omitted.lean').write_text('theorem omittedFalse : False := by sorry\n');run('shared-git-add',['git','add','.'],repo)
run('shared-discovery',['bash','tools/proof-gate.sh','--list'],repo)
run('shared-omitted-module',['bash','tools/proof-gate.sh','--out',str(O/'shared-omitted-receipt'),'project'],repo)
run('shared-omitted-explicit',['bash','tools/proof-gate.sh','--out',str(O/'shared-explicit-receipt'),'project/Omitted.lean'],repo)
# CLI: execute the real verifier with deliberate timing mutation around a real version check.
base=S/'cli';shutil.copytree(S/'worker/positive',base/'formal',ignore=shutil.ignore_patterns('.lake'),dirs_exist_ok=True)
spec={'schema':'crypto.autoresearch.formal_task.v1','task_id':'CONTROL-cli','claim_id':'control','kind':'formalize_claim','claim':'instrument control','source':'control-note.md','theorem_name':'Control.good','theorem_file':'CryptoResearch/Test.lean','workspace':'formal'};(base/'spec.yaml').write_text(json.dumps(spec));(base/'control-note.md').write_text('instrument control\n')
def verify(name,mutate=None):
 real=cli.subprocess.run;changed=False
 def wrapped(cmd,*args,**kwargs):
  nonlocal changed
  result=real(cmd,*args,**kwargs)
  if mutate and list(cmd)==['lake','env','lean','--version'] and not changed:mutate();changed=True
  return result
 cli.subprocess.run=wrapped
 start=time.time()
 try: code=cli.main(['--repo-root',str(base),'verify','--task-file',str(base/'spec.yaml'),'--artifact-out',str(O/(name+'.json')),'--build-timeout','120'])
 finally:cli.subprocess.run=real
 rows.append({'name':name,'interface':'orchestration.formal.cli.main','exit_code':code,'mutated':changed,'elapsed_seconds':time.time()-start});(O/'additional-commands.json').write_text(json.dumps(rows,indent=2)+'\n');print(name,code,flush=True)
verify('cli-positive')
verify('cli-positive') # existing immutable output must be refused
verify('cli-stale-main',lambda:(base/'formal/CryptoResearch/Test.lean').write_text('namespace Control\ntheorem good : True := True.intro\nend Control\n-- mutation after source hashes\n'))
(base/'formal/CryptoResearch/Helper.lean').write_text('namespace Control\ndef helper : Nat := 1\nend Control\n');(base/'formal/CryptoResearch/Test.lean').write_text('import CryptoResearch.Helper\nnamespace Control\ntheorem good : True := True.intro\nend Control\n')
verify('cli-stale-import',lambda:(base/'formal/CryptoResearch/Helper.lean').write_text('namespace Control\ndef helper : Nat := 2\nend Control\n'))
# Replay summary then attack a single chosen receipt without changing the 66-row inventory.
summary=S/'summary';shutil.copytree(F/'crypto-autoresearcher',summary,dirs_exist_ok=True)
script=summary/'research/lean_retrospective_20261018/summarize.mjs';run('summary-original',['node',str(script)],summary)
receipt=summary/'research/lean_retrospective_20261018/receipts/ncp-affine-normal-form.json';original=receipt.read_bytes();data=json.loads(original);data['verification']['forbidden_constructs']=['sorry:forged'];data['verification']['theorem_name']='Wrong.name';data['build_log']='';data['audit_log']='';data['provenance']['lean_version']='not a real Lean run';receipt.write_text(json.dumps(data));run('summary-forged-inconsistent',['node',str(script)],summary);shutil.copy2(summary/'research/lean_retrospective_20261018/verification-summary.json',O/'summary-forged-result.json');(O/'forged-receipt.json').write_text(json.dumps(data,indent=2)+'\n');receipt.write_bytes(original)
target=summary/'formal/CryptoResearch/NCP/AffineNormalForm.lean';target.write_text(target.read_text()+'\n-- stale-source control\n');run('summary-stale-main',['node',str(script)],summary)
