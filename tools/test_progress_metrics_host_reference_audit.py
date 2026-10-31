"""Committed-source audit coverage gates, with no scientific algorithm execution."""
import contextlib,copy,hashlib,importlib.util,io,json,subprocess,tempfile,unittest
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('audit_metrics_under_test',Path(__file__).with_name('progress_metrics.py'))
pm=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(pm)
B='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/'
REPORT='experiments/EXP-ECDLP-080f41/reports/review-DEC-20261030-c55f30/observations.json'
def encoded(v):return (json.dumps(v,sort_keys=True)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
class HostReferenceAuditMetricsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);subprocess.run(['git','init','-q',str(self.root)],check=True);self.previous=pm.REPO;pm.REPO=self.root;self.addCleanup(setattr,pm,'REPO',self.previous)
  law={'task_id':'TASK-20261030-3393bd','phase2_retained_audit':{'totals':{'null_draws':7,'uniform_rows':9,'reconstructed_decoder_words':20,'uniform_zero_M':2}}}
  truth={'task_id':'TASK-20261030-88d5bd','coverage':{'curves':3,'uniform_rows':9,'decoder_words':20,'decoder_public_equations':30,'BSGS_targets':4,'setup_base_equations':5,'uniform_M0_rows':2}}
  self.sources={};self.files={}
  for role,task in [('law',law['task_id']),('truth',truth['task_id']),('cost','TASK-20261030-f55ebb')]:
   logical=B+'reviews/'+task+'/checks.json';payload=encoded(law if role=='law' else truth) if role!='cost' else b'large retained payload fixture, deliberately absent from Git\n';ds=digest(payload)
   stored=logical if role!='cost' else logical+'.blob.json';data=payload if role!='cost' else encoded({'schema':'crypto.autoresearch.blob_pointer.v1','encoding':'identity','sha256':ds,'content_sha256':ds,'size':len(payload),'content_size':len(payload),'uri':'s3://setec-astronomy-artifacts/store/sha256/'+ds[:2]+'/'+ds})
   self.files[stored]=data;rp=B+'claims/'+task+'.1.release.json';rel=encoded({'task_id':task,'epoch':1,'outcome':'completed','artifact_sha256':{logical:ds}});self.files[rp]=rel
   row={'task_id':task,'joint_id':'J-'+role,'path':logical,'payload_sha256':ds,'payload_bytes':len(payload),'stored_path':stored,'stored_sha256':digest(data),'release_path':rp,'release_sha256':digest(rel)}
   if role=='cost':
    modern=B+'reviews/'+task+'/.artifacts.json';md=encoded({'schema':'artifacts.manifest/v1','files':{'checks.json':{'sha256':ds,'bytes':len(payload)}}});self.files[modern]=md;row.update(modern_manifest_path=modern,modern_manifest_sha256=digest(md))
   self.sources[role]=row
  self.data={'schema':'classical.ecdlp.host-reference-audit.observations/v1','recorded_at':'2026-10-30T00:00:00+00:00','run_id':'RUN-ECDLP-939237','experiment_id':'EXP-ECDLP-080f41','batch_id':'BATCH-128d4e','source_launch_status':'invalid_output','check_returncode':1,'published':False,'wall_valid':False,'native_counter_replay_qualified':False,'scientific_status_changed':False,'metric_sources':self.sources,'audit_coverage':{'curves_checked':3,'orientation_draws_checked':7,'uniform_rows_checked':9,'decoder_word_records_checked':20,'decoder_public_equations_checked':30,'bsgs_final_equations_checked':4,'prepared_setup_equations_checked':5,'zero_budget_rows_checked':2}}
  for name,blob in self.files.items():self.put(name,blob)
  self.save();self.ref=self.commit()
 def put(self,p,b):
  f=self.root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 def save(self):self.put(REPORT,encoded(self.data))
 def commit(self):
  subprocess.run(['git','-C',str(self.root),'add','--all'],check=True);subprocess.run(['git','-C',str(self.root),'-c','user.name=Audit metrics fixture','-c','user.email=audit-fixture@example.invalid','commit','-qm','fixed administrative fixture'],check=True);return subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
 def rows(self,ref=None):
  stream=io.StringIO()
  with contextlib.redirect_stdout(stream):pm.host_reference_audit_observations(ref or self.ref,'2026-10-29')
  return [json.loads(line) for line in stream.getvalue().splitlines()]
 def test_valid_committed_counts_pointer_and_neutral_separate_ids(self):
  rows=self.rows();self.assertEqual(len(rows),8);self.assertTrue(all(r['better']=='neutral' and r['unit']=='count' and r['metric'].startswith('audit.939237.') for r in rows));self.assertEqual(next(r['value'] for r in rows if r['metric'].endswith('curves_checked')),3);self.assertTrue(all(r['source'].endswith('@'+self.ref) for r in rows));self.assertFalse((self.root/self.sources['cost']['path']).exists())
 def test_dirty_or_missing_worktree_does_not_change_committed_metrics(self):
  expected=self.rows();self.data['audit_coverage']['curves_checked']=999;self.save();(self.root/self.sources['truth']['path']).unlink();self.assertEqual(self.rows(),expected)
 def test_missing_unknown_metric_is_omitted_without_zero_fill(self):
  self.data['audit_coverage']['bsgs_final_equations_checked']=None;del self.data['audit_coverage']['zero_budget_rows_checked'];self.save();ref=self.commit();rows=self.rows(ref);self.assertEqual(len(rows),6);self.assertFalse(any(r['metric'].endswith(('bsgs_final_equations_checked','zero_budget_rows_checked')) for r in rows))
 def test_adversarial_value_mismatch_or_bool_emits_nothing(self):
  for value in (99,True):
   self.data['audit_coverage']['curves_checked']=value;self.save();self.assertEqual(self.rows(self.commit()),[])
 def test_missing_pointer_or_self_consistent_wrong_pointer_is_rejected(self):
  pointer=self.sources['cost']['stored_path'];original=(self.root/pointer).read_bytes();(self.root/pointer).unlink();self.assertEqual(self.rows(self.commit()),[])
  d=json.loads(original);d['content_sha256']='0'*64;blob=encoded(d);self.put(pointer,blob);self.data['metric_sources']['cost']['stored_sha256']=digest(blob);self.save();self.assertEqual(self.rows(self.commit()),[])
 def test_changed_source_with_new_report_hash_still_needs_release_binding(self):
  logical=self.sources['truth']['path'];d=json.loads((self.root/logical).read_text());d['coverage']['curves']=99;blob=encoded(d);self.put(logical,blob);self.data['audit_coverage']['curves_checked']=99;self.sources['truth']['stored_sha256']=digest(blob);self.sources['truth']['payload_sha256']=digest(blob);self.save();self.assertEqual(self.rows(self.commit()),[])
 def test_old_exporter_function_output_and_id_namespace_unchanged(self):
  old=io.StringIO()
  with contextlib.redirect_stdout(old):pm.controlled_followup_observations(self.ref,'2026-10-29');pm.controlled_followup_080f41_observations(self.ref,'2026-10-29')
  self.assertEqual(old.getvalue(),'');self.assertFalse(any(r['metric'].startswith('controlled.') for r in self.rows()))
if __name__=='__main__':unittest.main()
