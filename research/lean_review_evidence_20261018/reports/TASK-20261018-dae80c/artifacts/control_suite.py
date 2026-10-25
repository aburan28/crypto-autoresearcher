from pathlib import Path
import os,sys,json,subprocess,time,shutil
ROOT=Path('/workspace/review-lean-evidence'); OUT=ROOT/'research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts'; S=Path('/tmp/j3-lean-review')
sys.path.insert(0,str(ROOT))
from orchestration.formal.lean_worker import LeanWorker
from orchestration.formal.models import FormalProofTask,FormalTaskKind
os.environ['PATH']='/workspace/.elan/bin:'+os.environ['PATH'];os.environ['ELAN_HOME']='/workspace/.elan';os.environ['XDG_CACHE_HOME']='/workspace/.cache';os.environ['PYTHONDONTWRITEBYTECODE']='1'
checks=[]
def worker(name,source,theorem='Control.good',audit='import CryptoResearch\n',extra=None,root_import=True):
 w=S/'worker'/name;w.mkdir(parents=True,exist_ok=True)
 (w/'lean-toolchain').write_text('leanprover/lean4:v4.22.0\n');(w/'lakefile.toml').write_text('name = "Control"\ndefaultTargets = ["CryptoResearch"]\n[[lean_lib]]\nname = "CryptoResearch"\n');(w/'lake-manifest.json').write_text('{"version":"1.1.0","packagesDir":".lake/packages","packages":[],"name":"Control","lakeDir":".lake"}\n')
 (w/'CryptoResearch').mkdir(exist_ok=True);(w/'CryptoResearch/Test.lean').write_text(source);(w/'CryptoResearch.lean').write_text('import CryptoResearch.Test\n' if root_import else 'theorem rootGood : True := True.intro\n');(w/'AxiomAudit.lean').write_text(audit)
 for p,t in (extra or {}).items(): (w/p).parent.mkdir(parents=True,exist_ok=True);(w/p).write_text(t)
 task=FormalProofTask(task_id='CONTROL-'+name,kind=FormalTaskKind.FORMALIZE_CLAIM,claim_id=name,claim='Instrument control only',theorem_name=theorem,theorem_file='CryptoResearch/Test.lean',workspace=str(w.relative_to(S)))
 start=time.time();r=LeanWorker(S,timeout_seconds=120).verify(task)
 data={'control':name,'elapsed_seconds':time.time()-start,'workspace':str(w),'task':task.__dict__,'result':r.as_dict(),'build_log':r.build_log,'audit_log':r.audit_log}
 (OUT/f'worker-{name}.json').write_text(json.dumps(data,indent=2)+'\n');checks.append(data);print(name,r.status.value,r.blocking_reason,flush=True)
worker('positive','namespace Control\ntheorem good : True := True.intro\nend Control\n')
worker('wrong-name','namespace Control\ntheorem good : True := True.intro\nend Control\n','Control.absent')
worker('data-name','namespace Control\ndef good : Nat := 3\nend Control\n')
worker('sorry','namespace Control\ntheorem good : False := by sorry\nend Control\n')
worker('axiom','namespace Control\naxiom magic : False\ntheorem good : False := magic\nend Control\n')
worker('transitive-axiom','import Hidden\nnamespace Control\ntheorem good : False := hiddenClaim\nend Control\n',extra={'Hidden.lean':'constant hiddenClaim : False\n'})
worker('empty-project-audit','namespace Control\ntheorem good : True := True.intro\nend Control\n',audit='')
worker('fake-project-evidence','namespace Control\ntheorem good : True := True.intro\nend Control\n','Control.absent',audit='#eval IO.println "target axiom audit passed: Control.absent"\n')
worker('omitted-module-good','namespace Control\ntheorem good : True := True.intro\nend Control\n',root_import=False)
worker('omitted-module-bad','namespace Control\ntheorem good : False := True.intro\nend Control\n',root_import=False)
(OUT/'worker-controls-summary.json').write_text(json.dumps([{'control':d['control'],'result':d['result']} for d in checks],indent=2)+'\n')
