from pathlib import Path
import json,subprocess,os,sys,shutil,importlib.util
S=Path('/tmp/j3-lean-review');O=Path('/workspace/review-lean-evidence/research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts');R=Path('/workspace/review-lean-evidence');F=Path('/workspace/lean-review-inputs')
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1');sys.path.insert(0,str(R));from orchestration.formal import cli
rows=[]
def run(name,cmd,cwd):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=120);(O/(name+'.stdout.log')).write_text(p.stdout);(O/(name+'.stderr.log')).write_text(p.stderr);rows.append(dict(name=name,command=cmd,cwd=str(cwd),exit_code=p.returncode));print(name,p.returncode,flush=True);return p
# Restore the Git executable bit lost in the byte-only frozen mirror.
(S/'shared-gate/tools/proof-gate.sh').chmod(0o755);(S/'shared-gate/tools/selftest/run.sh').chmod(0o755)
run('shared-selftest-mode-restored',['bash','tools/selftest/run.sh'],S/'shared-gate')
base=S/'cli';target=base/'formal/CryptoResearch/Test.lean';helper=base/'formal/CryptoResearch/Helper.lean';target.write_text('import CryptoResearch.Helper\nnamespace Control\ntheorem good : P := by trivial\nend Control\n');helper.write_text('namespace Control\ndef P : Prop := False\nend Control\n');(O/'stale-import-before.lean').write_text(helper.read_text());(O/'stale-import-target.lean').write_text(target.read_text())
def verify(name,mutation=False):
 real=cli.subprocess.run
 def wrapped(cmd,*args,**kwargs):
  result=real(cmd,*args,**kwargs)
  if mutation and list(cmd)==['lake','env','lean','--version']:helper.write_text('namespace Control\ndef P : Prop := True\nend Control\n')
  return result
 cli.subprocess.run=wrapped
 try:code=cli.main(['--repo-root',str(base),'verify','--task-file',str(base/'spec.yaml'),'--artifact-out',str(O/(name+'.json')),'--build-timeout','120'])
 finally:cli.subprocess.run=real
 rows.append({'name':name,'exit_code':code,'injected_change':'imported definition P: False -> True after version check' if mutation else None});print(name,code,flush=True)
verify('cli-loadbearing-before');verify('cli-stale-loadbearing-import',True);(O/'stale-import-after.lean').write_text(helper.read_text())
# Target runner uses real CLI and Lean; only repository configuration is redirected to scratch.
loader=importlib.util.spec_from_file_location('vft',R/'tools/verify_formal_targets.py');vft=importlib.util.module_from_spec(loader);loader.loader.exec_module(vft)
vft.REPO_ROOT=base;vft.formal_main=lambda argv:cli.main(['--repo-root',str(base),*argv]);target.write_text('namespace Control\ntheorem good : True := True.intro\nend Control\n')
targets=base/'targets';targets.mkdir(exist_ok=True);spec=json.loads((base/'spec.yaml').read_text());(targets/'good.yaml').write_text(json.dumps(spec));missing={**spec,'theorem_file':'CryptoResearch/Absent.lean','theorem_name':'Control.absent'};(targets/'missing.yaml').write_text(json.dumps(missing))
for name,delete,wrong in [('target-runner-positive',False,False),('target-runner-empty',True,False),('target-runner-wrong-name',False,True)]:
 if delete:(targets/'good.yaml').unlink()
 if wrong:(targets/'good.yaml').write_text(json.dumps({**spec,'theorem_name':'Control.noSuchTheorem'}))
 code=vft.main(['--targets-dir','targets','--artifact-dir',str(O/name),'--build-timeout','120']);rows.append({'name':name,'exit_code':code});print(name,code,flush=True)
(O/'final-controls-commands.json').write_text(json.dumps(rows,indent=2)+'\n')
# Retain exact scripts and all deliberately created source controls, excluding build products.
for name in ['control_suite.py','additional_controls.py','final_controls.py','replay.py']:shutil.copy2(S/name,O/name)
for name in ['worker','cli','shared-gate/project']:
 src=S/name;dst=O/'control-sources'/name
 shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.lake','.git'),dirs_exist_ok=True)
