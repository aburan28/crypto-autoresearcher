"""Offline adapter tests: synthetic metadata producers, never scientific trials."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import legacy_trial_manifest as adapter

DRIVER = '''import argparse,json,pathlib
p=argparse.ArgumentParser();p.add_argument("--trial-plan");p.add_argument("--run-dir");a=p.parse_args()
d=pathlib.Path(a.run_dir)
raw={"experiment_id":"EXP-ECDLP-aaaaaa","run_id":"RUN-ECDLP-aaaaaa","attack_claimed":False,"fixture":7}
(d/"raw-result.json").write_text(json.dumps(raw,indent=3)+"\\n")
(d/"manifest.yaml").write_text("run:\\n  experiment_id: EXP-ECDLP-aaaaaa\\n  run_id: RUN-ECDLP-aaaaaa\\n  attack_claimed: false\\n  metrics:\\n    planted_ok: true\\n    value: 7\\n")
'''
CHECKER = '''import json,pathlib,sys
d=pathlib.Path(sys.argv[1]);x=json.loads((d/"raw-result.json").read_text())
assert x=={"experiment_id":"EXP-ECDLP-aaaaaa","run_id":"RUN-ECDLP-aaaaaa","attack_claimed":False,"fixture":7}
assert "experiment_id: EXP-ECDLP-aaaaaa" in (d/"manifest.yaml").read_text()
'''

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="legacy-adapter-test-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        old=self.root/"experiments/EXP-ECDLP-aaaaaa"
        old.mkdir(parents=True)
        (old/"implementation").mkdir()
        self.write("tools/legacy_trial_manifest.py",Path(adapter.__file__).read_text())
        self.write("experiments/EXP-ECDLP-aaaaaa/implementation/run.py",DRIVER)
        self.write("experiments/EXP-ECDLP-aaaaaa/implementation/check.py",CHECKER)
        self.write("experiments/EXP-ECDLP-aaaaaa/specification.yaml",yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-aaaaaa","inputs":{"fixed_value":7}}}))
        old_sources={p:adapter.sha(self.root/p) for p in ["experiments/EXP-ECDLP-aaaaaa/implementation/run.py","experiments/EXP-ECDLP-aaaaaa/implementation/check.py"]}
        old_plan={"schema":"crypto.autoresearch.trial_plan.v1","frozen":True,"experiment_id":"EXP-ECDLP-aaaaaa","source_sha256":old_sources,"specification":"experiments/EXP-ECDLP-aaaaaa/specification.yaml","specification_sha256":adapter.sha(old/"specification.yaml"),"trials":[{"id":"worksheet","run_id":"RUN-ECDLP-aaaaaa","argv":[sys.executable,"experiments/EXP-ECDLP-aaaaaa/implementation/run.py","--trial-plan","experiments/EXP-ECDLP-aaaaaa/trial-plan.json","--run-dir","{run_dir}"],"check_argv":[sys.executable,"experiments/EXP-ECDLP-aaaaaa/implementation/check.py","{run_dir}"],"artifacts":["manifest.yaml","raw-result.json"]}]}
        self.write("experiments/EXP-ECDLP-aaaaaa/trial-plan.json",json.dumps(old_plan))
        self.write("experiments/EXP-ECDLP-bbbbbb/specification.yaml",yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-bbbbbb"}}))
        block={"trial_plan":"experiments/EXP-ECDLP-aaaaaa/trial-plan.json","trial_plan_sha256":adapter.sha(old/"trial-plan.json"),"trial_id":"worksheet","experiment_id":"EXP-ECDLP-aaaaaa","run_id":"RUN-ECDLP-aaaaaa","input_seed":None,"input_seed_semantics":"No new random draw; fixed synthetic fixture","curve_id":None}
        sources={**old_sources,block["trial_plan"]:block["trial_plan_sha256"],old_plan["specification"]:old_plan["specification_sha256"],adapter.SELF:adapter.sha(self.root/adapter.SELF)}
        prefix=[sys.executable,adapter.SELF]
        self.plan={"schema":"crypto.autoresearch.trial_plan.v1","frozen":True,"experiment_id":"EXP-ECDLP-bbbbbb","specification":"experiments/EXP-ECDLP-bbbbbb/specification.yaml","specification_sha256":adapter.sha(self.root/"experiments/EXP-ECDLP-bbbbbb/specification.yaml"),"legacy_trial":block,"source_sha256":sources,"trials":[{"id":"metadata-successor","run_id":"RUN-ECDLP-bbbbbb","argv":prefix+["run","--trial-plan","experiments/EXP-ECDLP-bbbbbb/trial-plan.json","--run-dir","{run_dir}"],"check_argv":prefix+["check","--trial-plan","experiments/EXP-ECDLP-bbbbbb/trial-plan.json","--run-dir","{run_dir}"],"artifacts":list(adapter.OUTPUTS)}]}
        self.path=self.root/"experiments/EXP-ECDLP-bbbbbb/trial-plan.json"
        self.path.write_text(json.dumps(self.plan))
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        subprocess.run(["git","-C",str(self.root),"-c","user.name=Fixture","-c","user.email=fixture@example.invalid","add","."],check=True)
        subprocess.run(["git","-C",str(self.root),"-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","-qm","synthetic test inputs"],check=True)
        self.commit=subprocess.check_output(["git","-C",str(self.root),"rev-parse","HEAD"],text=True).strip()
        self.directory=self.root/"experiments/EXP-ECDLP-bbbbbb/runs/RUN-ECDLP-bbbbbb"
        self.directory.mkdir(parents=True)
        self.refresh_provenance()

    def write(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)

    def refresh_provenance(self):
        self.path.write_text(json.dumps(self.plan))
        trial=self.plan["trials"][0]
        launch={"trial_id":trial["id"],"run_id":trial["run_id"],"plan_sha256":adapter.sha(self.path),"argv":adapter.expand(trial["argv"],self.directory),"check_argv":adapter.expand(trial["check_argv"],self.directory),"authority":{"commit":self.commit}}
        (self.directory/"launch.json").write_text(json.dumps(launch))
        (self.directory/"command.txt").write_text(json.dumps(launch["argv"])+"\n")
        (self.directory/"environment.json").write_text(json.dumps({"commit":self.commit,"source_sha256":self.plan["source_sha256"],"specification_sha256":self.plan["specification_sha256"]}))
        for name in ["stdout.log","stderr.log"]:(self.directory/name).touch()

    def execute(self):adapter.execute(self.path,self.directory,root=self.root)
    def check(self):adapter.check(self.path,self.directory,root=self.root)

    def replace_legacy_source(self,name,text):
        relative="experiments/EXP-ECDLP-aaaaaa/implementation/"+name
        self.write(relative,text)
        p=self.root/self.plan["legacy_trial"]["trial_plan"]
        old=json.loads(p.read_text());old["source_sha256"][relative]=adapter.sha(self.root/relative)
        p.write_text(json.dumps(old))
        self.plan["source_sha256"][relative]=adapter.sha(self.root/relative)
        self.plan["legacy_trial"]["trial_plan_sha256"]=adapter.sha(p)
        self.plan["source_sha256"][self.plan["legacy_trial"]["trial_plan"]]=adapter.sha(p)
        self.refresh_provenance()

    def test_original_bytes_ids_metrics_and_null_seed_survive(self):
        self.execute();self.check()
        raw=(self.directory/"raw-result.json").read_bytes()
        self.assertIn(b'   "experiment_id": "EXP-ECDLP-aaaaaa"',raw)
        m=yaml.safe_load((self.directory/"manifest.yaml").read_text())["run"]
        self.assertEqual(m["id"],"RUN-ECDLP-bbbbbb")
        self.assertEqual(m["experiment_id"],"EXP-ECDLP-bbbbbb")
        self.assertEqual(m["result"]["metrics"],{"planted_ok":True,"value":7})
        self.assertIsNone(m["inputs"]["seed"])
        self.assertEqual(m["inputs"]["parameters"]["legacy_inputs"],{"fixed_value":7})
        self.assertGreater(m["resources"]["peak_rss_bytes"],0)
        self.assertEqual(m["code"]["commit"],self.commit)
        self.assertEqual(m["result"]["certificate"]["kind"],"none")
        self.assertEqual(set(p.name for p in self.directory.iterdir()),set(adapter.OUTPUTS)|set(adapter.PROVENANCE)|{"stdout.log","stderr.log"})

    def test_native_manifest_gate_accepts_envelope_without_inventing_seed(self):
        self.execute()
        import experiment_execution
        self.assertEqual(experiment_execution.manifest_schema_errors(self.directory/"manifest.yaml"),[])

    def test_source_tamper_and_incomplete_closure_refused_before_child(self):
        self.plan["source_sha256"].pop("experiments/EXP-ECDLP-aaaaaa/implementation/check.py")
        self.refresh_provenance()
        with self.assertRaisesRegex(adapter.LegacyTrialError,"closure does not bind"):
            self.execute()
        self.assertFalse((self.directory/"raw-result.json").exists())

    def test_original_source_tamper_refused(self):
        self.write("experiments/EXP-ECDLP-aaaaaa/implementation/run.py",DRIVER+"# drift\n")
        with self.assertRaisesRegex(adapter.LegacyTrialError,"bound file changed"):
            self.execute()

    def test_checker_rejects_raw_and_canonical_identity_tampering(self):
        self.execute()
        original=(self.directory/"raw-result.json").read_bytes()
        (self.directory/"raw-result.json").write_bytes(original+b" ")
        with self.assertRaisesRegex(adapter.LegacyTrialError,"bound file changed"):
            self.check()
        (self.directory/"raw-result.json").write_bytes(original)
        p=self.directory/"manifest.yaml";m=yaml.safe_load(p.read_text());m["run"]["id"]="RUN-ECDLP-cccccc";p.write_text(yaml.safe_dump(m))
        with self.assertRaisesRegex(adapter.LegacyTrialError,"canonical envelope differs"):
            self.check()

    def test_supervisor_command_tamper_and_overwrite_refused(self):
        self.execute()
        with self.assertRaisesRegex(adapter.LegacyTrialError,"outputs already exist"):
            self.execute()
        (self.directory/"command.txt").write_text('["wrong"]')
        with self.assertRaisesRegex(adapter.LegacyTrialError,"command.txt"):
            self.check()

    def test_failed_driver_preserves_original_bytes_and_failure_receipt(self):
        self.replace_legacy_source("run.py",DRIVER+"raise SystemExit(3)\n")
        with self.assertRaisesRegex(adapter.LegacyTrialError,"original driver failed: 3"):
            self.execute()
        self.assertFalse((self.directory/"manifest.yaml").exists())
        self.assertTrue((self.directory/"legacy-manifest.yaml").is_file())
        self.assertTrue((self.directory/"raw-result.json").is_file())
        r=json.loads((self.directory/"legacy-execution.json").read_text())
        self.assertEqual(r["status"],"failed")
        self.assertEqual(r["phases"][0]["returncode"],3)
        self.assertEqual(len(r["phases"]),1)

    def test_failed_checker_never_emits_successful_envelope(self):
        self.replace_legacy_source("check.py",CHECKER+"raise SystemExit(4)\n")
        with self.assertRaisesRegex(adapter.LegacyTrialError,"original checker failed: 4"):
            self.execute()
        self.assertFalse((self.directory/"manifest.yaml").exists())
        r=json.loads((self.directory/"legacy-execution.json").read_text())
        self.assertEqual(r["status"],"failed")
        self.assertEqual(r["phases"][1]["returncode"],4)

    def test_receipt_cannot_replace_actual_legacy_command(self):
        self.execute()
        p=self.directory/"legacy-execution.json";r=json.loads(p.read_text());r["phases"][0]["argv"][0]="not-the-original-interpreter";p.write_text(json.dumps(r))
        with self.assertRaisesRegex(adapter.LegacyTrialError,"legacy phase command"):
            self.check()

if __name__=="__main__":unittest.main()
