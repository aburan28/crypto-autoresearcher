"""Focused no-solver fixture and negative-output custody checks."""
from __future__ import annotations
import json, sys, tarfile, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; sys.path[:0]=[str(HERE),str(ROOT/"tools")]
import output_contract, fixture_supervisor

class ContractTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.run=Path(self.tmp.name); (self.run/"diagnostic").mkdir()
  self.launch={"run_id":"RUN-ICPERF-abcdef","trial_id":"fixture","plan_sha256":"a"*64,"authority":{"owner":"o","epoch":1}}
  source={str((HERE/name).relative_to(ROOT)): value for name,value in output_contract.verify_input_manifest()["source_sha256"].items()}; (self.run/"launch.json").write_bytes(output_contract.canonical(self.launch)); (self.run/"environment.json").write_bytes(output_contract.canonical({"commit":"c","source_sha256":source})); (self.run/"command.txt").write_text("fixture\n")
  self.raw={"a":b"a"}; self.receipt=self.base_receipt(); self.write_raw(); self.write_receipt()
 def base_receipt(self):
  return {"schema":output_contract.DIAGNOSTIC_SCHEMA,"experiment_id":"EXP","run_id":self.launch["run_id"],"trial_id":"fixture","plan_sha256":"a"*64,"launch_sha256":output_contract.digest((self.run/"launch.json").read_bytes()),"claim_owner":"o","claim_epoch":1,"started_utc":"2026-01-01T00:00:00+00:00","ended_utc":"2026-01-01T00:00:00+00:00","cells":[{"cell":"monitor-null","kind":"synthetic_null","attempted":True,"stop":"infrastructure_monitor_error","fault":{"code":"unreadable_live_root"}}]+[{"cell":c,"kind":"positive","attempted":True,"stop":"timeout_censored"} for c in output_contract.CELLS[1:]]}
 def write_raw(self, extra=False, duplicate=False, nonfile=False):
  d=self.run/"diagnostic"; [ (d/n).write_bytes(v) for n,v in self.raw.items() ]
  with tarfile.open(d/"raw.tar.gz","w:gz") as a:
   for n in self.raw: a.add(d/n,arcname=n)
   if extra: a.add(d/next(iter(self.raw)),arcname="extra")
   if duplicate: a.add(d/next(iter(self.raw)),arcname=next(iter(self.raw)))
   if nonfile: a.addfile(tarfile.TarInfo("dir"))
  self.receipt["raw_tar_sha256"]=output_contract.digest((d/"raw.tar.gz").read_bytes()); self.receipt["raw_members"]=[{"path":n,"sha256":output_contract.digest(v),"bytes":len(v)} for n,v in self.raw.items()]
 def write_receipt(self): (self.run/"diagnostic"/"receipt.json").write_bytes(output_contract.canonical(self.receipt))
 def valid(self): output_contract.write_outputs(self.run); output_contract.verify_outputs(self.run)
 def test_missing_and_empty_required_outputs_rejected(self):
  self.valid(); (self.run/"manifest.yaml").unlink()
  with self.assertRaisesRegex(output_contract.ContractError,"manifest.yaml"): output_contract.verify_outputs(self.run)
  (self.run/"manifest.yaml").write_bytes(b"")
  with self.assertRaisesRegex(output_contract.ContractError,"manifest.yaml"): output_contract.verify_outputs(self.run)
 def test_changed_digest_and_plan_claim_source_mismatch_rejected(self):
  self.valid(); (self.run/"raw-result.json").write_text("{}\n")
  with self.assertRaises(output_contract.ContractError): output_contract.verify_outputs(self.run)
  (self.run/"raw-result.json").unlink(); (self.run/"manifest.yaml").unlink(); self.receipt["claim_epoch"]=2; self.write_receipt()
  with self.assertRaisesRegex(output_contract.ContractError,"binding"): output_contract.write_outputs(self.run)
  self.receipt["claim_epoch"]=1; self.launch["plan_sha256"]="b"*64; (self.run/"launch.json").write_bytes(output_contract.canonical(self.launch)); self.write_receipt()
  with self.assertRaisesRegex(output_contract.ContractError,"binding"): output_contract.write_outputs(self.run)
  self.launch["plan_sha256"]="a"*64; (self.run/"launch.json").write_bytes(output_contract.canonical(self.launch)); environment=json.loads((self.run/"environment.json").read_text()); environment["source_sha256"][next(iter(environment["source_sha256"]))]="0"*64; (self.run/"environment.json").write_bytes(output_contract.canonical(environment)); self.write_receipt()
  with self.assertRaisesRegex(output_contract.ContractError,"source binding"): output_contract.write_outputs(self.run)
 def test_raw_member_bytes_extra_duplicate_and_nonfile_rejected(self):
  self.raw={"a":b"changed"}; self.write_raw(); self.receipt["raw_members"]=[{"path":"a","sha256":output_contract.digest(b"a"),"bytes":1}]; self.write_receipt()
  with self.assertRaisesRegex(output_contract.ContractError,"digest"): output_contract.derive(self.run)
  for kind in ("extra","duplicate","nonfile"):
   self.receipt=self.base_receipt(); self.write_raw(**{kind:True}); self.write_receipt()
   with self.subTest(kind=kind), self.assertRaisesRegex(output_contract.ContractError,"raw member|unlisted"): output_contract.derive(self.run)
 def test_false_success_rejected_and_censors_preserved(self):
  self.receipt["cells"][2]={"cell":"random-m2","kind":"positive","attempted":True,"stop":"exited","response":"forged"}; self.write_receipt()
  with self.assertRaisesRegex(output_contract.ContractError,"false successful"): output_contract.write_outputs(self.run)
  self.receipt["cells"][2]["response"]="canned_positive"; self.write_receipt(); self.valid(); raw=json.loads((self.run/"raw-result.json").read_text()); self.assertEqual(raw["cell_stops"]["coset-m2"],"timeout_censored")
 def test_real_supervisor_requires_committed_source(self):
  commit=__import__("subprocess").check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
  for mode in ("bounded-censor","canned-positive"):
   with self.subTest(mode=mode): self.assertEqual(fixture_supervisor.run(mode,commit)["status"],"output_validated")
if __name__ == "__main__": unittest.main()
