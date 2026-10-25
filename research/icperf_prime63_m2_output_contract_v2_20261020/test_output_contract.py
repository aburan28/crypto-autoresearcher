from __future__ import annotations
import sys, tarfile, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; sys.path[:0]=[str(HERE),str(ROOT/"tools")]
import output_contract, fixture_supervisor
class ContractTests(unittest.TestCase):
 def test_real_supervisor_bounded_and_canned_positive(self):
  for mode in ("bounded-censor","canned-positive"):
   with self.subTest(mode=mode):
    r=fixture_supervisor.run(mode); self.assertEqual(r["status"],"output_validated"); self.assertEqual(r["receipt_status"],"output_validated")
 def test_negative_controls_reject_tampering_and_extra_raw(self):
  with tempfile.TemporaryDirectory() as tmp:
   run=Path(tmp); (run/"diagnostic").mkdir(); launch={"run_id":"RUN-ICPERF-abcdef","trial_id":"fixture","plan_sha256":"a"*64,"authority":{"owner":"o","epoch":1}}
   (run/"launch.json").write_bytes(output_contract.canonical(launch)); (run/"environment.json").write_bytes(output_contract.canonical({"commit":"c","source_sha256":{"x":"b"*64}})); (run/"command.txt").write_text("fixture\n"); (run/"diagnostic"/"a").write_text("a")
   with tarfile.open(run/"diagnostic"/"raw.tar.gz","w:gz") as archive: archive.add(run/"diagnostic"/"a",arcname="a")
   receipt={"schema":output_contract.DIAGNOSTIC_SCHEMA,"experiment_id":"EXP","run_id":launch["run_id"],"trial_id":"fixture","plan_sha256":"a"*64,"launch_sha256":output_contract.digest((run/"launch.json").read_bytes()),"claim_owner":"o","claim_epoch":1,"started_utc":"2026-01-01T00:00:00+00:00","ended_utc":"2026-01-01T00:00:00+00:00","raw_tar_sha256":output_contract.digest((run/"diagnostic"/"raw.tar.gz").read_bytes()),"raw_members":[{"path":"a"}],"cells":[{"cell":"monitor-null","kind":"synthetic_null","attempted":True,"stop":"infrastructure_monitor_error","fault":{"code":"unreadable_live_root"}}]+[{"cell":c,"kind":"positive","attempted":True,"stop":"timeout_censored"} for c in output_contract.CELLS[1:]]}
   (run/"diagnostic"/"receipt.json").write_bytes(output_contract.canonical(receipt)); output_contract.write_outputs(run); output_contract.verify_outputs(run); (run/"raw-result.json").write_text("{}\n")
   with self.assertRaises(output_contract.ContractError): output_contract.verify_outputs(run)
   receipt["raw_members"].append({"path":"ghost"}); (run/"diagnostic"/"receipt.json").write_bytes(output_contract.canonical(receipt))
   with self.assertRaises(output_contract.ContractError): output_contract.derive(run)
if __name__ == "__main__": unittest.main()
