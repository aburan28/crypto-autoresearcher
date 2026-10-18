from pathlib import Path
import json,subprocess,sys,os,time
R=Path('/workspace/review-lean-evidence');F=Path('/workspace/lean-review-inputs/crypto-autoresearcher');S=Path('/tmp/j3-lean-review');O=R/'research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts'
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1');sys.path.insert(0,str(R));from orchestration.formal.targets import load_spec,task_from_spec;from orchestration.formal.lean_worker import target_audit_source,LeanWorker
by_workspace={};rows=[]
for spec in sorted((F/'formal/targets').glob('*.yaml')):
 task=task_from_spec(load_spec(spec));w=S/'formal-cache'/Path(task.workspace).relative_to('formal');exists=(w/task.theorem_file).is_file();rows.append(dict(spec=str(spec.relative_to(F)),workspace=task.workspace,theorem=task.theorem_name,theorem_file=task.theorem_file,exists=exists))
 if exists:by_workspace.setdefault(w,[]).append(task)
commands=[]
for w,tasks in by_workspace.items():
 imports=sorted({Path(t.theorem_file).with_suffix('').as_posix().replace('/','.') for t in tasks});text=''.join('import '+m+'\n' for m in imports)+'import Lean\nopen Lean Elab Command\n'
 for t in tasks:text+=target_audit_source(Path(t.theorem_file).with_suffix('').as_posix().replace('/','.'),t.theorem_name).split('open Lean Elab Command\n',1)[1]
 name='all-frozen-'+('main' if w.name=='formal-cache' else 'scoped');(w/'J3AllFrozenAudit.lean').write_text(text);(O/(name+'.lean')).write_text(text)
 for phase,cmd in [('build',['lake','build']),('audit',['lake','env','lean','J3AllFrozenAudit.lean'])]:
  start=time.time();r=subprocess.run(cmd,cwd=w,capture_output=True,text=True,timeout=120);(O/(name+'-'+phase+'.stdout.log')).write_text(r.stdout);(O/(name+'-'+phase+'.stderr.log')).write_text(r.stderr);commands.append(dict(name=name+'-'+phase,command=cmd,cwd=str(w),exit_code=r.returncode,elapsed_seconds=time.time()-start,requested_theorems=len(tasks)));print(name,phase,r.returncode,len(tasks),flush=True)
 scans=LeanWorker._scan_forbidden(w);commands.append(dict(name=name+'-source-scan',forbidden_constructs=list(scans)));print(name,'scan',scans,flush=True)
(O/'all-frozen-audit-commands.json').write_text(json.dumps(commands,indent=2)+'\n');(O/'all-frozen-targets.json').write_text(json.dumps(rows,indent=2)+'\n')
