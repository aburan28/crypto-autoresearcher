from pathlib import Path
import json,os,shutil,subprocess,time,sys
S=Path('/tmp/j3-lean-review');O=Path('/workspace/review-lean-evidence/research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts');F=Path('/workspace/lean-review-inputs')
os.environ.update(PATH='/workspace/.elan/bin:'+os.environ['PATH'],ELAN_HOME='/workspace/.elan',XDG_CACHE_HOME='/workspace/.cache',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,'/workspace/review-lean-evidence');from orchestration.formal.lean_worker import target_audit_source
results=[]
def run(name,cmd,cwd,timeout=600):
 start=time.time();r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=timeout);(O/(name+'.stdout.log')).write_text(r.stdout);(O/(name+'.stderr.log')).write_text(r.stderr);row=dict(name=name,command=cmd,cwd=str(cwd),exit_code=r.returncode,elapsed_seconds=time.time()-start);results.append(row);(O/'replay-commands.json').write_text(json.dumps(results,indent=2)+'\n');print(name,r.returncode,row['elapsed_seconds'],flush=True);return r
for repo in ['crypto','cryptanalysis']:
 src=Path('/workspace')/repo/'research/lean_retrospective_20261018/lean';w=S/repo/'lean';shutil.copytree(src,w,symlinks=True,dirs_exist_ok=True)
 for p in (w/'.lake/packages').iterdir():
  target=(S/'crypto-lean-cache') if p.name=='CryptoLean' else S/'crypto-lean-cache/.lake/packages'/p.name
  p.unlink();p.symlink_to(target)
 run(repo+'-build',['lake','build'],w)
 run(repo+'-axioms',['lake','env','lean','AxiomAudit.lean'],w)
 module='Retrospective.Transport' if repo=='crypto' else 'Retrospective.RhoCollision'
 run(repo+'-audit',['lake','env','lean','--run',str(F/'crypto-lean/tools/AuditAxioms.lean'),module],w)
w=S/'formal-cache'
run('autoresearcher-build',['lake','build'],w)
run('autoresearcher-project-audit',['lake','env','lean','AxiomAudit.lean'],w)
m=json.loads((F/'crypto-autoresearcher/research/lean_retrospective_20261018/proof-map.json').read_text())
text='import Lean\n'+''.join('import '+d['file'].removeprefix('formal/').removesuffix('.lean').replace('/','.')+'\n' for d in {d['file']:d for d in m['declarations']}.values())+'open Lean Elab Command\n'
for d in m['declarations']:
 module=d['file'].removeprefix('formal/').removesuffix('.lean').replace('/','.')
 text+='#print axioms '+d['declaration']+'\n'+target_audit_source(module,d['declaration']).split('open Lean Elab Command\n',1)[1]
(w/'J3NamedAudit.lean').write_text(text);(O/'J3NamedAudit.lean').write_text(text)
run('autoresearcher-10-named-audit',['lake','env','lean','J3NamedAudit.lean'],w)
