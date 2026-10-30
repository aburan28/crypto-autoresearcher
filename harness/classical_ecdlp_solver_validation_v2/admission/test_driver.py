#!/usr/bin/env python3
"""Synthetic integrity/public-verifier controls; never runs the scientific cohort."""
from __future__ import annotations
import copy, hashlib, importlib.util, json
from pathlib import Path
import subprocess, tempfile, unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation_driver',HERE/'driver.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)


def cfg():
 return {'fixture_ids':['f17'],'fixture_meta':[{'id':'f17','p':17,'r':19,'N':19}],
         'target_meta':[{'fixture_id':'f17','target_id':'q3','ordinal':0,'subset':'core'}]}

def row(**extra):
 return {'scope':driver.SCOPE,'track':'solver-candidate','fixture':'f17',**extra}

def candidate_rows():
 values=[row(row_kind='kernel',feature='constant',training_samples=2048,heldout_samples=512,calibration_used_for_tuning=False),row(row_kind='not_applicable',feature='power_residue_5',outcome='not_applicable')]
 for mode in ('model','exact'):
  for beam in (1,8):
   candidates=[3] if beam==1 else list(range(1,9))
   values.append(row(row_kind='target',feature='constant',target_id='q3',prefix_mode=mode,beam_width=beam,candidates=candidates,candidate_count=beam,candidate_verification_hits=1,verified_scalar=3,inference_counters={},verification_counters={}))
 return values

def candidate_module():
 return {'name':'candidate_0','kind':'candidate','fixture_ids':['f17'],'tracks':['solver-candidate'],'features':['constant','power_residue_5']}

def solver_module():
 return {'name':'solvers_0','kind':'solvers','fixture_ids':['f17'],'tracks':['solver-baselines'],
  'methods':['rho_upstream_auto','rho_upstream_auto_aa','hybrid_xmod7_exact_b8_then_rho','bernstein_lange_precomp','bsgs_complete'],
  'hybrid_method':'hybrid_xmod7_exact_b8_then_rho','setup_rows':[['baseline_setup','bernstein_lange_precomp'],['baseline_setup','bsgs_complete'],['hybrid_setup','hybrid_xmod7_exact_b8_then_rho']]}

def solver_rows():
 common={'scope':driver.SCOPE,'track':'solver-baselines','fixture':'f17'}
 values=[{**common,'row_kind':'fixture_validation'}]
 for kind,method in solver_module()['setup_rows']:values.append({**common,'row_kind':kind,'method':method})
 for method in solver_module()['methods']:
  x={**common,'row_kind':'baseline_target','target_id':'q3','method':method,'candidates':[3],'candidate_verification_hits':1,'verified_scalar':3,'status':'solved','counters':{'group_additions':10},'process_cpu_seconds':0,'rho_seed':123}
  if method==solver_module()['hybrid_method']:
   x.update(prefix_candidates=[0,1,2,4,5,6,7,8],prefix_candidate_verification_hits=0,prefix_verified_scalar=None,fallback_used=True,candidate_alone_recovered=False,counters={'group_additions':15},stages={'prefix_total':{'group_additions':5},'fallback':{'group_additions':10}})
  values.append(x)
 return values

class Integrity(unittest.TestCase):
 def test_names_paths_and_capacity(self):
  self.assertEqual(driver.PART_COUNT,2560);self.assertEqual(driver.VERIFICATION_PART_COUNT,256)
  self.assertTrue(all(driver.module_name_valid(x)for x in driver.MODULES))
  for x in ('../bad','a/b','x;rm','0bad'):self.assertFalse(driver.module_name_valid(x))
  self.assertEqual(f'rows-part-{1024:03}.jsonl','rows-part-1024.jsonl')
  with self.assertRaises(ValueError):driver.safe(HERE,'../escape')
 def test_candidate_complete_coverage(self):
  values=candidate_rows();driver.validate_rows(candidate_module(),values,cfg())
  with self.assertRaisesRegex(ValueError,'coverage'):driver.validate_rows(candidate_module(),values[:-1],cfg())
  with self.assertRaisesRegex(ValueError,'duplicate'):driver.validate_rows(candidate_module(),values+[values[-1]],cfg())
 def test_candidate_scalar_and_diagnostics_contract(self):
  values=candidate_rows();values[-1]['candidates'][-1]=19
  with self.assertRaisesRegex(ValueError,'range'):driver.validate_rows(candidate_module(),values,cfg())
  values=candidate_rows();values[0]['calibration_used_for_tuning']=True
  with self.assertRaisesRegex(ValueError,'tuning'):driver.validate_rows(candidate_module(),values,cfg())
 def test_solver_complete_coverage_and_pairing(self):
  values=solver_rows();driver.validate_rows(solver_module(),values,cfg())
  with self.assertRaisesRegex(ValueError,'coverage'):driver.validate_rows(solver_module(),values[:-1],cfg())
  values=solver_rows();values[5]['rho_seed']=124
  with self.assertRaisesRegex(ValueError,'seed'):driver.validate_rows(solver_module(),values,cfg())
 def test_solver_cost_and_fallback_controls(self):
  values=solver_rows();values[5]['counters']['group_additions']=11
  with self.assertRaisesRegex(ValueError,'A/A'):driver.validate_rows(solver_module(),values,cfg())
  values=solver_rows();values[6]['counters']['group_additions']=16
  with self.assertRaisesRegex(ValueError,'decomposition'):driver.validate_rows(solver_module(),values,cfg())
  values=solver_rows();values[6]['candidate_alone_recovered']=True
  with self.assertRaisesRegex(ValueError,'prefix-only'):driver.validate_rows(solver_module(),values,cfg())
 def test_partition_four_digit_names_exact_bytes(self):
  values=candidate_rows();values[0]['padding']='x'*40000;values[1]['padding']='y'*40000
  with tempfile.TemporaryDirectory(dir=HERE,prefix='dev-parts-') as td:
   path=Path(td);data=b''.join((json.dumps(x)+'\n').encode()for x in values);(path/'.candidate_0.full.jsonl').write_bytes(data)
   result,nextslot=driver.partition(path,candidate_module(),1023,cfg())
   self.assertEqual(nextslot,1025);self.assertIn('rows-part-1024.jsonl',[x['path']for x in result['parts']])
   self.assertEqual(b''.join((path/x['path']).read_bytes()for x in result['parts']),data)
   self.assertEqual(result['original_sha256'],hashlib.sha256(data).hexdigest())
 def test_oversized_or_exhausted_output_retained(self):
  values=candidate_rows();values[0]['padding']='z'*driver.CHUNK_LIMIT
  with tempfile.TemporaryDirectory(dir=HERE,prefix='dev-overflow-') as td:
   path=Path(td);source=path/'.candidate_0.full.jsonl';data=b''.join((json.dumps(x)+'\n').encode()for x in values);source.write_bytes(data)
   with self.assertRaisesRegex(ValueError,'individual JSONL'):driver.partition(path,candidate_module(),0,cfg())
   self.assertEqual(source.read_bytes(),data)
  with tempfile.TemporaryDirectory(dir=HERE,prefix='dev-capacity-') as td:
   path=Path(td);source=path/'.candidate_0.full.jsonl';source.write_text(''.join(json.dumps(x)+'\n'for x in candidate_rows()))
   with self.assertRaisesRegex(ValueError,'capacity'):driver.partition(path,candidate_module(),driver.PART_COUNT,cfg())
   self.assertTrue(source.exists())
 def test_verification_covers_final_and_prefix(self):
  with tempfile.TemporaryDirectory(dir=HERE,prefix='dev-cases-') as td:
   path=Path(td);values=candidate_rows()+solver_rows();p=path/'test.jsonl';p.write_text(''.join(json.dumps(x)+'\n'for x in values))
   cases=driver.verification_cases(cfg(),path,{'modules':[{'name':'synthetic','parts':[{'path':p.name}]}]})
   self.assertEqual(len(cases),10);self.assertEqual(sum(x['kind']=='prefix'for x in cases.values()),1)
 def test_nonfinite_and_no_overwrite(self):
  for x in (float('nan'),{'a':float('inf')}):
   with self.assertRaisesRegex(ValueError,'nonfinite'):driver.finite(x)
  with tempfile.TemporaryDirectory(dir=HERE,prefix='dev-once-') as td:
   p=Path(td)/'once';driver.write_once(p,{'a':1})
   with self.assertRaises(FileExistsError):driver.write_once(p,{'a':2})

class PublicVerifier(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(dir=HERE,prefix='dev-verifier-');cls.root=Path(cls.temp.name);cls.binary=cls.root/'check'
  subprocess.run(['g++','-std=c++20','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-Wconversion','-Wshadow',str(HERE/'verify_candidates.cpp'),'-o',str(cls.binary)],check=True)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def files(self,fixture='f17 ordinary 17 2 2 5 1 19 19 9',targets=None,candidates=None):
  base=self.root/('case'+str(len(list(self.root.glob('case*')))));base.mkdir()
  f=base/'fixtures.tsv';t=base/'targets.tsv';c=base/'candidates.tsv';o=base/'output.tsv'
  f.write_text('id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\n'+fixture+'\n')
  t.write_text('fixture_id\ttarget_id\tQx\tQy\tQinf\n'+(targets or 'f17 q0 0 0 1\nf17 q1 5 1 0\nf17 q18 5 16 0')+'\n')
  c.write_text('fixture_id\ttarget_id\tcase_id\tcandidate\n'+(candidates or 'f17 q0 zero 0\nf17 q1 one 1\nf17 q18 rminusone 18\nf17 q1 wrong 2\nf17 q1 empty -1')+'\n')
  return f,t,c,o
 def runcheck(self,files):return subprocess.run([str(self.binary),'--verify',*map(str,files)],capture_output=True,text=True)
 def test_edges_mutation_empty_and_large_field(self):
  files=self.files();r=self.runcheck(files);self.assertEqual(r.returncode,0,r.stderr);text=files[-1].read_text();self.assertIn('wrong\t1\t0\t-1',text);self.assertIn('empty\t0\t0\t-1',text)
  files=self.files('big ordinary 524287 0 1 0 1 3 524288 9','big q0 0 0 1\nbig q1 0 1 0\nbig q2 0 524286 0','big q0 zero 0\nbig q1 one 1\nbig q2 rminusone 2');r=self.runcheck(files);self.assertEqual(r.returncode,0,r.stderr)
 def test_malformed_nonmember_and_duplicate_rejected(self):
  files=self.files('f17 ordinary 17 0 1 0 1 3 18 9','f17 outside 1 6 0','f17 outside bad 1');r=self.runcheck(files);self.assertNotEqual(r.returncode,0);self.assertIn('outside subgroup',r.stderr)
  files=self.files(candidates='f17 q1 dup 1\nf17 q1 dup 1');self.assertNotEqual(self.runcheck(files).returncode,0)
  files=self.files(targets='f17 q1 17 1 0');self.assertNotEqual(self.runcheck(files).returncode,0)
  files=self.files();files[0].write_text('bad header\n');self.assertNotEqual(self.runcheck(files).returncode,0)

if __name__=='__main__':unittest.main(verbosity=2)
