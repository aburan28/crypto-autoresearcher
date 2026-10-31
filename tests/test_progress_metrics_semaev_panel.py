"""Reject stale inventory bindings and unsupported bounds; no scientific trials."""
import copy, hashlib, importlib.util, json, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pm',Path(__file__).resolve().parents[1]/'tools/progress_metrics.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT='analysis/semaev-degree-five-quotient-lift/'
class PanelMetricsTests(unittest.TestCase):
 def setUp(self):
  self.parent=json.dumps({'items':[{'prior_id':'a'},{'prior_id':'b'}]})
  self.result=json.dumps({'prior_id':'a','status':'certificate_verified','last_fall_degree_lower_bound':5,'certified_codimension_lower_bound':9,'exact_solutions':1})
  self.d={'created_at':'2026-10-30T19:00:00+00:00','parent_inventory':'runtime/original.json','parent_sha256':self.sha(self.parent),'items':[{'prior_id':'b'}],'terminal_inputs':{'a':{'path':'reports/a/result.json','result_sha256':self.sha(self.result),'status':'certificate_verified','last_fall_degree_lower_bound':5}},'terminal_count':1,'certified_lfd_at_least5':1}
 def sha(self,x):return hashlib.sha256(x.encode()).hexdigest()
 def run_export(self, extra=None):
  files={ROOT+'runtime/original.json':self.parent,ROOT+'reports/a/result.json':self.result,ROOT+'runtime/panel-remaining-after-local002.json':json.dumps(self.d)};rows=[]
  if extra:files.update({ROOT+'runtime/'+name:json.dumps(value) for name,value in extra.items()})
  with patch.object(m,'ls',return_value=list(files)),patch.object(m,'show',side_effect=lambda ref,path:files.get(path)),patch.object(m,'emit',side_effect=lambda name,value,**kw:rows.append((name,value))):m.semaev_panel_snapshots('fixed-ref','2026-10-01')
  return rows
 def test_valid_named_counts(self):self.assertEqual([v for _,v in self.run_export()],[1,1,1])
 def test_changed_result_bytes(self):self.result+=' ';self.assertEqual(self.run_export(),[])
 def test_overlap_pending_terminal(self):self.d['items']=[{'prior_id':'a'}];self.assertEqual(self.run_export(),[])
 def test_equality_is_not_lower_bound(self):
  d=json.loads(self.result);d['certified_codimension_lower_bound']=1;self.result=json.dumps(d);self.d['terminal_inputs']['a']['result_sha256']=self.sha(self.result);self.assertEqual(self.run_export(),[])
 def test_cap_is_not_certificate(self):
  d=json.loads(self.result);d['status']='resource_capped';self.result=json.dumps(d);e=self.d['terminal_inputs']['a'];e.update(status='resource_capped',result_sha256=self.sha(self.result));self.assertEqual(self.run_export(),[])
 def test_newer_inventory_resolves_historical_tie(self):
  newer=copy.deepcopy(self.d);newer['created_at']='2026-10-30T20:00:00+00:00'
  extra={'panel-remaining-after-local003.json':self.d,'panel-remaining-after-local004.json':newer}
  self.assertEqual([v for _,v in self.run_export(extra)],[1,1,1])
 def test_latest_tie_stays_ambiguous(self):
  self.assertEqual(self.run_export({'panel-remaining-after-local003.json':self.d}),[])
 def test_older_tie_after_newest_does_not_hide_it(self):
  older=copy.deepcopy(self.d);older['created_at']='2026-10-30T18:00:00+00:00'
  extra={'panel-remaining-after-local003.json':older,'panel-remaining-after-local004.json':older}
  self.assertEqual([v for _,v in self.run_export(extra)],[1,1,1])
if __name__=='__main__':unittest.main()
