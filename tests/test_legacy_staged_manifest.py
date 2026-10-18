"""Synthetic staging/metadata controls only; no original scientific panel."""
from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import legacy_staged_manifest as a

OLD = "experiments/EXP-ECDLP-aaaaaa"
NEW = "experiments/EXP-ECDLP-bbbbbb"
DRIVER = '''import argparse,json,pathlib
p=argparse.ArgumentParser();p.add_argument("--stage",type=int);p.add_argument("--trial-plan");p.add_argument("--run-dir");v=p.parse_args()
e=pathlib.Path(__file__).resolve().parents[1];d=pathlib.Path(v.run_dir)
def w(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb") as f:f.write(b)
s=v.stage;out="S0-FREEZE-OK" if s==0 else "O-MIXED"
if s==0:
 for n,b in [("protocol-freeze.json",b'{"null_seed":20261007}\\n'),("preregistered-predictions.json",b'{"fixture":7}\\n'),("worksheet-note.md",b"exact omitted note\\n")]:w(e/"stage0"/n,b)
else:
 assert (e/"stage0/protocol-freeze.json").read_bytes()==b'{"null_seed":20261007}\\n'
 for n,b in [("census.json",b'{"synthetic":7}\\n'),("control-table.json",b'{"fixture":7}\\n')]:w(e/"stage1"/n,b)
 w(e/"RESULTS.md",b"exact global stage1 report\\n")
r={"stage":s,"outcome":out,"claims":{"attack":False,"break":False,"exponent_move":False},"fixture":7}
w(d/"raw-result.json",(json.dumps(r,indent=3)+"\\n").encode())
w(d/"manifest.yaml",f"experiment_id: EXP-ECDLP-aaaaaa\\nstage: {s}\\noutcome: {out}\\n".encode())
w(d/"RESULTS.md",b"exact local legacy report\\n")
'''
CHECKER = '''import json,pathlib,sys
r=pathlib.Path(sys.argv[1]);x=json.loads((r/"raw-result.json").read_bytes())
e=pathlib.Path("experiments/EXP-ECDLP-aaaaaa")
assert x["outcome"] in ("S0-FREEZE-OK","O-MIXED","O-IMPEDIMENT")
if x["stage"]==0:assert (e/"stage0/protocol-freeze.json").is_file()
elif x["outcome"]!="O-IMPEDIMENT":assert (e/"stage1/census.json").is_file() and (e/"stage1/control-table.json").is_file()
'''


class StagedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="legacy-staged-synthetic-");self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.write(a.SELF,Path(a.__file__).read_bytes())
        self.write(OLD+"/implementation/run.py",DRIVER)
        self.write(OLD+"/implementation/check.py",CHECKER)
        self.write(OLD+"/specification.yaml",yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-aaaaaa","inputs":{"seeds":{"null_seed":20261007}}}}))
        self.old={"schema":"crypto.autoresearch.trial_plan.v1","frozen":True,"experiment_id":"EXP-ECDLP-aaaaaa","specification":OLD+"/specification.yaml","specification_sha256":a.sha(self.root/(OLD+"/specification.yaml")),"source_sha256":{n:a.sha(self.root/n) for n in (OLD+"/implementation/run.py",OLD+"/implementation/check.py")},"trials":[]}
        for stage,run in ((0,"RUN-ECDLP-aaaaaa"),(1,"RUN-ECDLP-cccccc")):
            self.old["trials"].append({"id":f"stage{stage}","run_id":run,"argv":["python3",OLD+"/implementation/run.py","--stage",str(stage),"--trial-plan",OLD+"/trial-plan.json","--run-dir","{run_dir}"],"check_argv":["python3",OLD+"/implementation/check.py","{run_dir}"],"artifacts":["manifest.yaml","raw-result.json","RESULTS.md"]})
        self.write(OLD+"/trial-plan.json",a.json_text(self.old))
        self.write(NEW+"/specification.yaml",yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-bbbbbb"}}))
        block={"trial_plan":OLD+"/trial-plan.json","trial_plan_sha256":a.sha(self.root/(OLD+"/trial-plan.json")),"experiment_id":"EXP-ECDLP-aaaaaa","input_seed":20261007,"input_seed_semantics":"Stage0 freezes actual fixed seed without RNG; Stage1 old random-null seed20261007; no new draw.","curve_id":None,"checker_scope":a.CHECKER_SCOPE,"stages":[]}
        for stage in (0,1):
            names=["stage0/protocol-freeze.json","stage0/preregistered-predictions.json","stage0/worksheet-note.md"] if stage==0 else ["stage1/census.json","stage1/control-table.json","RESULTS.md"]
            block["stages"].append({"stage":stage,"trial_id":f"native-stage{stage}","legacy_trial_id":f"stage{stage}","global_outputs":[OLD+"/"+n for n in names],"outcomes":["S0-FREEZE-OK"] if stage==0 else ["O-MIXED","O-IMPEDIMENT"],"optional_globals_outcomes":[] if stage==0 else ["O-IMPEDIMENT"]})
        self.plan={"schema":"crypto.autoresearch.trial_plan.v1","frozen":True,"experiment_id":"EXP-ECDLP-bbbbbb","specification":NEW+"/specification.yaml","specification_sha256":a.sha(self.root/(NEW+"/specification.yaml")),"legacy_staged":block,"source_sha256":{**self.old["source_sha256"],OLD+"/trial-plan.json":block["trial_plan_sha256"],OLD+"/specification.yaml":self.old["specification_sha256"],a.SELF:a.sha(self.root/a.SELF)},"trials":[]}
        self.path=self.root/(NEW+"/trial-plan.json")
        for stage,run in ((0,"RUN-ECDLP-bbbbbb"),(1,"RUN-ECDLP-dddddd")):
            base=[sys.executable,a.SELF,"run","--trial-plan",NEW+"/trial-plan.json","--run-dir","{run_dir}"]
            check=base.copy();check[2]="check"
            self.plan["trials"].append({"id":f"native-stage{stage}","run_id":run,"argv":base,"check_argv":check,"artifacts":list(a.OUTPUTS),"depends_on":[] if stage==0 else ["native-stage0"]})
        self.write(NEW+"/trial-plan.json",a.json_text(self.plan))
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        subprocess.run(["git","-C",str(self.root),"add","."],check=True)
        subprocess.run(["git","-C",str(self.root),"-c","user.name=Synthetic","-c","user.email=synthetic@example.invalid","commit","-qm","synthetic-only fixture"],check=True)
        self.commit=subprocess.check_output(["git","-C",str(self.root),"rev-parse","HEAD"],text=True).strip()
        self.dirs=[self.root/NEW/"runs"/t["run_id"] for t in self.plan["trials"]]
        for d in self.dirs:d.mkdir(parents=True)
        self.provenance()

    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(value.encode() if isinstance(value,str) else value)

    def provenance(self):
        self.path.write_text(a.json_text(self.plan))
        for d,t in zip(self.dirs,self.plan["trials"]):
            launch={"trial_id":t["id"],"run_id":t["run_id"],"plan_sha256":a.sha(self.path),"argv":a.expand(t["argv"],d),"check_argv":a.expand(t["check_argv"],d),"authority":{"commit":self.commit}}
            (d/"launch.json").write_text(a.json_text(launch));(d/"command.txt").write_text(a.json_text(launch["argv"]))
            (d/"environment.json").write_text(a.json_text({"commit":self.commit,"source_sha256":self.plan["source_sha256"],"specification_sha256":self.plan["specification_sha256"]}))
            for n in set(a.GENERATED)-set(a.PROVENANCE):(d/n).touch()

    def source(self,name,text):
        p=OLD+"/implementation/"+name;self.write(p,text)
        self.old["source_sha256"][p]=a.sha(self.root/p)
        self.write(OLD+"/trial-plan.json",a.json_text(self.old))
        self.plan["source_sha256"][p]=self.old["source_sha256"][p]
        h=a.sha(self.root/(OLD+"/trial-plan.json"));self.plan["source_sha256"][OLD+"/trial-plan.json"]=h;self.plan["legacy_staged"]["trial_plan_sha256"]=h
        self.provenance()

    def execute(self,stage):a.execute(self.path,self.dirs[stage],root=self.root)
    def check(self,stage):a.check(self.path,self.dirs[stage],root=self.root)
    def seal0(self):
        d=self.dirs[0];t=self.plan["trials"][0]
        receipt={"schema":"crypto.autoresearch.trial_receipt.v1","status":"output_validated","returncode":0,"check_returncode":0,"plan_sha256":a.sha(self.path),"trial_id":t["id"],"run_id":t["run_id"],"artifact_sha256":{n:a.sha(d/n) for n in (*a.OUTPUTS,*a.GENERATED)}}
        (d/"execution-receipt.json").write_text(a.json_text(receipt))

    def test_two_distinct_stages_preserve_exact_bytes_sources_all_globals_and_native_gate(self):
        self.execute(0);self.check(0);self.seal0()
        before={p.name:a.sha(p) for p in self.dirs[0].iterdir()}
        self.execute(1);self.check(1)
        self.assertEqual(before,{p.name:a.sha(p) for p in self.dirs[0].iterdir()})
        import experiment_execution
        for stage,d in enumerate(self.dirs):
            self.assertEqual(experiment_execution.manifest_schema_errors(d/"manifest.yaml"),[])
            files=a.archive_files(d/"legacy-workspace.tar")
            self.assertEqual(files[OLD+"/stage0/worksheet-note.md"],b"exact omitted note\n")
            self.assertEqual(files[OLD+"/implementation/run.py"],DRIVER.encode())
            m=yaml.safe_load((d/"manifest.yaml").read_bytes())["run"]
            self.assertEqual(m["inputs"]["seed"],20261007)
            self.assertEqual(m["result"]["certificate"]["kind"],"none")
            self.assertIn("no independent arithmetic",m["environment"]["checker_scope"])
            self.assertIn(b'   "fixture": 7',(d/"raw-result.json").read_bytes())
            self.assertEqual(set(p.name for p in d.iterdir()),set(a.OUTPUTS)|set(a.GENERATED)|({"execution-receipt.json"} if stage==0 else set()))
        self.assertFalse((self.root/OLD/"stage0").exists());self.assertFalse((self.root/OLD/"stage1").exists())

    def test_stage1_requires_native_stage0_not_just_freeze_or_archive(self):
        self.execute(0)
        with self.assertRaises(FileNotFoundError):self.execute(1)
        self.assertFalse((self.dirs[1]/"legacy-workspace.tar").exists())

    def test_predecessor_complete_coverage_and_hashes_required(self):
        self.execute(0);self.seal0();p=self.dirs[0]/"execution-receipt.json";r=a.read_json(p);r["artifact_sha256"].pop("check.stderr.log");p.write_text(a.json_text(r))
        with self.assertRaisesRegex(a.StagedError,"coverage incomplete"):self.execute(1)
        self.seal0();(self.dirs[0]/"legacy-workspace.tar").write_bytes(b"drift")
        with self.assertRaisesRegex(a.StagedError,"bound file changed"):self.execute(1)

    def test_source_closure_and_fixed_seed_types_refused(self):
        self.plan["source_sha256"].pop(OLD+"/implementation/check.py");self.provenance()
        with self.assertRaisesRegex(a.StagedError,"every legacy dependency"):self.execute(0)
        self.plan["source_sha256"][OLD+"/implementation/check.py"]=a.sha(self.root/(OLD+"/implementation/check.py"));self.plan["legacy_staged"]["input_seed"]=True;self.provenance()
        with self.assertRaisesRegex(a.StagedError,"seed/checker"):self.execute(0)

    def test_source_and_supervisor_command_tampering_refused(self):
        self.write(OLD+"/implementation/run.py",DRIVER+"# changed\n")
        with self.assertRaisesRegex(a.StagedError,"bound file changed"):self.execute(0)
        self.write(OLD+"/implementation/run.py",DRIVER)
        (self.dirs[0]/"command.txt").write_text('["changed"]')
        with self.assertRaisesRegex(a.StagedError,"provenance mismatch"):self.execute(0)

    def test_legacy_entrypoint_must_be_copied_source(self):
        self.old["trials"][0]["argv"][1]="/tmp/unbound.py"
        self.write(OLD+"/trial-plan.json",a.json_text(self.old))
        h=a.sha(self.root/(OLD+"/trial-plan.json"));self.plan["source_sha256"][OLD+"/trial-plan.json"]=h;self.plan["legacy_staged"]["trial_plan_sha256"]=h;self.provenance()
        with self.assertRaisesRegex(a.StagedError,"relative path"):self.execute(0)

    def test_no_overwrite_or_retry_consumed_workspace(self):
        self.execute(0)
        with self.assertRaisesRegex(a.StagedError,"consumed outputs"):self.execute(0)
        self.assertTrue((self.dirs[0]/"legacy-workspace.tar").is_file())

    def test_failed_driver_retains_partial_bytes_without_success_manifest(self):
        partial=DRIVER.replace('s=v.stage;out=', 'w(e/"stage0/protocol-freeze.json",b"exact partial freeze\\n");w(d/"raw-result.json",b"exact partial raw\\n");raise SystemExit(3)\ns=v.stage;out=')
        self.source("run.py",partial)
        with self.assertRaisesRegex(a.StagedError,"legacy_driver failed: 3"):self.execute(0)
        files=a.archive_files(self.dirs[0]/"legacy-workspace.tar")
        self.assertEqual(files[OLD+"/stage0/protocol-freeze.json"],b"exact partial freeze\n")
        self.assertEqual((self.dirs[0]/"raw-result.json").read_bytes(),b"exact partial raw\n")
        self.assertFalse((self.dirs[0]/"manifest.yaml").exists())
        self.assertEqual(a.read_json(self.dirs[0]/"legacy-execution.json")["status"],"failed")
        with self.assertRaisesRegex(a.StagedError,"consumed outputs"):self.execute(0)

    def test_failed_checker_retained_without_successful_envelope(self):
        self.source("check.py",CHECKER+"raise SystemExit(4)\n")
        with self.assertRaisesRegex(a.StagedError,"legacy_checker failed: 4"):self.execute(0)
        self.assertFalse((self.dirs[0]/"manifest.yaml").exists())
        self.assertIn(OLD+"/stage0/worksheet-note.md",a.archive_files(self.dirs[0]/"legacy-workspace.tar"))
        self.assertEqual(a.read_json(self.dirs[0]/"legacy-execution.json")["phases"][1]["returncode"],4)

    def test_stage1_impediment_absence_not_fabricated(self):
        modified=DRIVER.replace('s=v.stage;out="S0-FREEZE-OK" if s==0 else "O-MIXED"','s=v.stage;out="S0-FREEZE-OK" if s==0 else "O-IMPEDIMENT"').replace('else:\n assert (e/', 'elif False:\n assert (e/')
        self.source("run.py",modified);self.execute(0);self.seal0();self.execute(1);self.check(1)
        files=a.archive_files(self.dirs[1]/"legacy-workspace.tar")
        for n in self.plan["legacy_staged"]["stages"][1]["global_outputs"]:self.assertNotIn(n,files)
        receipt=a.read_json(self.dirs[1]/"legacy-execution.json")
        self.assertEqual(receipt["workspace_absent_paths"],sorted(self.plan["legacy_staged"]["stages"][1]["global_outputs"]))
        self.assertEqual(json.loads((self.dirs[1]/"raw-result.json").read_bytes())["outcome"],"O-IMPEDIMENT")

    def test_stage1_cannot_mutate_imported_stage0_globals(self):
        modified=DRIVER.replace(' w(e/"RESULTS.md",b"exact global stage1 report\\n")',' w(e/"RESULTS.md",b"exact global stage1 report\\n")\n (e/"stage0/protocol-freeze.json").write_bytes(b"mutated")')
        self.source("run.py",modified);self.execute(0);self.seal0()
        with self.assertRaisesRegex(a.StagedError,"stage0 globals changed"):self.execute(1)
        self.assertFalse((self.dirs[1]/"manifest.yaml").exists())
        self.assertIn(b'mutated',a.archive_files(self.dirs[1]/"legacy-workspace.tar").values())

    def test_archive_rejects_traversal_duplicates_links(self):
        for mode in ("traversal","duplicate","link"):
            p=self.root/(mode+".tar")
            with tarfile.open(p,"w:") as t:
                n="../escape" if mode=="traversal" else "file"
                m=tarfile.TarInfo(n)
                if mode=="link":m.type=tarfile.SYMTYPE;m.linkname="/etc/passwd";t.addfile(m)
                else:
                    m.size=1;t.addfile(m,io.BytesIO(b"a"))
                    if mode=="duplicate":t.addfile(m,io.BytesIO(b"b"))
            with self.assertRaises(a.StagedError):a.archive_files(p)

    def test_receipt_command_raw_manifest_and_bool_tampering_refused(self):
        self.execute(0);d=self.dirs[0]
        p=d/"legacy-execution.json";original=p.read_bytes();r=a.read_json(p);r["phases"][0]["returncode"]=False;p.write_text(a.json_text(r))
        with self.assertRaisesRegex(a.StagedError,"child command/resource"):self.check(0)
        p.write_bytes(original)
        r=a.read_json(p);r["phases"][0]["finished_at"]="2099-01-01T00:00:00+00:00";p.write_text(a.json_text(r))
        with self.assertRaisesRegex(a.StagedError,"timestamp interval"):self.check(0)
        p.write_bytes(original)
        m=d/"manifest.yaml";v=yaml.safe_load(m.read_bytes());v["run"]["inputs"]["parameters"]["legacy_stage"]["stage"]=False;m.write_text(yaml.safe_dump(v))
        with self.assertRaisesRegex(a.StagedError,"envelope differs"):self.check(0)
        (d/"raw-result.json").write_bytes(b"drift")
        with self.assertRaisesRegex(a.StagedError,"bound file changed"):self.check(0)


if __name__=="__main__":unittest.main()
