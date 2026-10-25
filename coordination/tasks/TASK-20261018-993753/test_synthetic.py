"""Software-only controls. No complete frozen worksheet is evaluated.

Tiny alternative fields/rationals and a wholly fabricated metadata repository
exercise code paths. Synthetic provenance is explicitly a mock, not a run.
"""
from pathlib import Path
from copy import deepcopy
from contextlib import redirect_stdout
import ast
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.dont_write_bytecode = True
TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]
IDS = ("080496","4a3f03","5a293e","6491b4","65f903","911c16")


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScientificSoftwareControls(unittest.TestCase):
    def modules(self, suffix):
        directory=ROOT / "experiments" / ("EXP-ECDLP-"+suffix) / "implementation"
        return [load(directory/(name+".py"),suffix+name) for name in ("route_a","route_b","oracle")]

    def agreement(self, suffix, fixture):
        modules=self.modules(suffix)
        results=[module.compute(deepcopy(fixture)) for module in modules]
        self.assertEqual(results[0],results[1]); self.assertEqual(results[0],results[2])
        assessments=[module.assess(deepcopy(fixture),results[0]["measurement"]) for module in modules]
        self.assertEqual(assessments[0],assessments[1]); self.assertEqual(assessments[0],assessments[2])
        return results[0],assessments[0]

    def test_syntax_and_no_scientific_cross_imports(self):
        paths=list(TASK.glob("*.py"))
        for suffix in IDS:
            paths.extend((ROOT/"experiments"/("EXP-ECDLP-"+suffix)/"implementation").glob("*.py"))
        for path in paths:
            tree=ast.parse(path.read_text(),filename=str(path))
            if path.name in ("route_a.py","route_b.py","oracle.py"):
                for node in ast.walk(tree):
                    if isinstance(node,ast.ImportFrom):
                        self.assertNotIn(node.module,("route_a","route_b","oracle"))
                    elif isinstance(node,ast.Import):
                        self.assertTrue(all(alias.name not in ("route_a","route_b","oracle") for alias in node.names))

    def test_hesse_alternative_small_field(self):
        result,_=self.agreement("080496",dict(p=5,d=2,O=[1,4,0],predicted=dict(point_count=-1,fixed_points=-1,sigma_O=[])))
        self.assertEqual(result["measurement"]["chart_candidates_tested"],31)
        self.assertFalse(result["measurement"]["tail_point_on_curve"])

    def test_negation_alternative_small_field_and_modular_map(self):
        result,_=self.agreement("5a293e",dict(p=5,A=1,B=1,maps=["x","x_plus_1","y"],
            predicted=dict(affine_point_count=-1,x_mismatches=-1,x_plus_1_mismatches=-1,y_mismatches=-1)))
        row=next(r for r in result["witness"]["pointwise_map_values"] if r["point"]==[4,2])
        self.assertEqual(row["x_plus_1"],[0,0])

    def test_orbit_alternative_fields(self):
        fields={"field7":dict(p=19,B=2,beta_factor=-1,sign_factor=-1,factor_product=-1,trace=-1),
                "field13":dict(p=31,B=3,embed_degree=-1,beta_factor=-1,sign_factor=-1)}
        self.agreement("4a3f03",dict(**fields,alpha_numerators=[1,2,5],alpha_denominators=[2,3,7],
            third_gap_num=-1,third_gap_den=1,depth_values=[1,3],grid_cells=-1,depth_product=-1))

    def test_query_fraction_alternative_cells_and_false_prediction(self):
        result,assessment=self.agreement("6491b4",dict(n=13,cells=[dict(P=0,T=0,predicted="0/1"),
            dict(P=0,T=3,predicted="0/1"),dict(P=1,T=2,predicted="0/1")],
            leak_claim=dict(P=0,T=0,claimed_success="1/1")))
        self.assertEqual(result["measurement"]["bound_by_cell"],["1/13","10/13","7/13"])
        self.assertTrue(all(assessment[0].values())); self.assertFalse(assessment[1]["bounds"])

    def test_band_alternative_rationals_and_base(self):
        self.agreement("65f903",dict(left="1/9",witness="1/7",right="1/3",n=8,
            predicted=dict(witness_inside=True,n_squared=64,n_cubed=512,reversed_below=False)))

    def test_theta_coprime_software_fixture(self):
        result,_=self.agreement("911c16",dict(numeric=dict(M=3,b=2),predicted=dict(good_ratio="1/8",
            good_remaining="3/4",bad_ratio="1/2",bad_remaining="0/1",bad_label="does_not_suffice")))
        self.assertTrue(result["measurement"]["numeric_matches_symbolic"])


class MetadataSoftwareControls(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix="synthetic-only-",dir=TASK)
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        copied=self.root/"coordination/tasks/TASK-20261018-993753/worksheet_envelope.py"
        copied.parent.mkdir(parents=True)
        shutil.copyfile(TASK/"worksheet_envelope.py",copied)
        self.helper=load(copied,"synthetic_metadata")
        self.impl=self.root/"experiments/EXP-ECDLP-aa0001/implementation"
        self.impl.mkdir(parents=True)
        measured='def compute(i):\n return {"measurement":{"sum":i["u"]+i["v"]},"witness":{"terms":[i["u"],i["v"]]}}\ndef assess(i,m):\n return {"arithmetic_control":True},{"deliberately_false_prediction":False}\n'
        oracle='def compute(i):\n total=sum([i["v"],i["u"]])\n return {"measurement":{"sum":total},"witness":{"terms":[i["u"],i["v"]]}}\ndef assess(i,m):\n return {"arithmetic_control":True},{"deliberately_false_prediction":False}\n'
        for name in ("route_a.py","route_b.py"):
            (self.impl/name).write_text(measured)
        (self.impl/"oracle.py").write_text(oracle)
        for name in ("run.py","check.py"):
            (self.impl/name).write_text('# synthetic entry point, not a real scientific launcher\n')
        self.spec=self.impl.parent/"specification.yaml"
        self.spec.write_text(yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-aa0001","inputs":{"u":2,"v":5}}}))
        sources={str(path.relative_to(self.root)):self.helper.digest(path) for path in [copied,*self.impl.glob("*.py")]}
        trials=[]
        for route in ("a","b"):
            trials.append(dict(id="synthetic-"+route,run_id="RUN-ECDLP-aa000"+("1" if route=="a" else "2"),route=route,
                argv=["python3",str((self.impl/"run.py").relative_to(self.root)),"--route",route,"--trial-plan","experiments/EXP-ECDLP-aa0001/trial-plan.json","--run-dir","{run_dir}"],
                check_argv=["python3",str((self.impl/"check.py").relative_to(self.root)),"--route",route,"--trial-plan","experiments/EXP-ECDLP-aa0001/trial-plan.json","--run-dir","{run_dir}"],
                artifacts=list(self.helper.OUTPUTS),depends_on=[] if route=="a" else ["synthetic-a"],
                comparison_trial_id=None if route=="a" else "synthetic-a"))
        self.plan={"schema":"crypto.autoresearch.trial_plan.v1","frozen":True,"experiment_id":"EXP-ECDLP-aa0001",
            "source_sha256":sources,"specification":str(self.spec.relative_to(self.root)),
            "specification_sha256":self.helper.digest(self.spec),"trials":trials}
        self.plan_path=self.impl.parent/"trial-plan.json"
        self.plan_path.write_text(json.dumps(self.plan))

    def directory(self,route):
        trial=next(t for t in self.plan["trials"] if t["route"]==route)
        directory=self.impl.parent/"runs"/trial["run_id"]
        directory.mkdir(parents=True)
        argv=[s.replace("{run_dir}",str(directory)) for s in trial["argv"]]
        check=[s.replace("{run_dir}",str(directory)) for s in trial["check_argv"]]
        launch=dict(trial_id=trial["id"],run_id=trial["run_id"],plan_sha256=self.helper.digest(self.plan_path),
            argv=argv,check_argv=check,authority={"commit":"a"*40,"synthetic_only":True})
        environment=dict(source_sha256=self.plan["source_sha256"],specification_sha256=self.plan["specification_sha256"],
            commit="a"*40,synthetic_only=True)
        (directory/"launch.json").write_text(json.dumps(launch)); (directory/"environment.json").write_text(json.dumps(environment))
        (directory/"command.txt").write_text(json.dumps(argv))
        (directory/"stdout.log").write_text("synthetic software fixture\n"); (directory/"stderr.log").write_text("")
        return directory

    def invoke(self,method,directory,route):
        args=["synthetic", "--trial-plan",str(self.plan_path),"--run-dir",str(directory),"--route",route]
        with patch.object(sys,"argv",args), patch.object(self.helper.subprocess,"run",return_value=type("MockStatus",(),{"stdout":"?? synthetic\n"})()),redirect_stdout(io.StringIO()):
            getattr(self.helper,method)()

    def test_native_envelope_and_false_prediction_is_valid(self):
        directory=self.directory("a")
        self.invoke("run",directory,"a"); self.invoke("check",directory,"a")
        manifest=yaml.safe_load((directory/"manifest.yaml").read_text())["run"]
        self.assertTrue(manifest["result"]["valid"])
        self.assertIsNone(manifest["inputs"]["seed"])
        self.assertFalse(manifest["result"]["metrics"]["prediction_comparison"]["deliberately_false_prediction"])
        sys.path.insert(0,str(ROOT/"tools"))
        try:
            import experiment_execution
            self.assertEqual(experiment_execution.manifest_schema_errors(directory/"manifest.yaml"),[])
        finally:
            sys.path.pop(0)

    def test_manifest_parameters_tamper_rejected(self):
        directory=self.directory("a"); self.invoke("run",directory,"a")
        path=directory/"manifest.yaml"; value=yaml.safe_load(path.read_text())
        value["run"]["inputs"]["parameters"]["route"]="b"
        path.write_text(yaml.safe_dump(value))
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")

    def test_no_overwrite_and_source_change_rejected(self):
        directory=self.directory("a"); self.invoke("run",directory,"a")
        with self.assertRaises(ValueError):
            self.invoke("run",directory,"a")
        with (self.impl/"route_a.py").open("a") as stream:
            stream.write("# synthetic tamper\n")
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")

    def test_invalid_reason_and_witness_scope_tamper_rejected(self):
        directory=self.directory("a"); self.invoke("run",directory,"a")
        manifest_path=directory/"manifest.yaml"; original=manifest_path.read_text()
        value=yaml.safe_load(original); value["run"]["result"]["invalid_reason"]="invented restriction"
        manifest_path.write_text(yaml.safe_dump(value))
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")
        value=yaml.safe_load(original)
        certificate_path=directory/"certificate.yaml"; certificate=yaml.safe_load(certificate_path.read_text())
        certificate["worksheet_witness"]["boundary"]="formal universal proof"
        certificate_path.write_text(yaml.safe_dump(certificate))
        value["run"]["artifacts"]["certificate.yaml"]["sha256"]=self.helper.digest(certificate_path)
        manifest_path.write_text(yaml.safe_dump(value))
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")

    def test_boolean_integer_and_boolean_resource_tamper_rejected(self):
        self.spec.write_text(yaml.safe_dump({"experiment":{"id":"EXP-ECDLP-aa0001","inputs":{"u":0,"v":1}}}))
        self.plan["specification_sha256"]=self.helper.digest(self.spec)
        self.plan_path.write_text(json.dumps(self.plan))
        directory=self.directory("a"); self.invoke("run",directory,"a")
        raw_path=directory/"raw-result.json"; raw=json.loads(raw_path.read_text())
        raw["measurement"]["sum"]=True
        raw_path.write_text(json.dumps(raw))
        certificate_path=directory/"certificate.yaml"; certificate=yaml.safe_load(certificate_path.read_text())
        certificate["worksheet_witness"]["raw_result_sha256"]=self.helper.digest(raw_path)
        certificate_path.write_text(yaml.safe_dump(certificate))
        manifest_path=directory/"manifest.yaml"; manifest=yaml.safe_load(manifest_path.read_text())
        for name in ("raw-result.json","certificate.yaml"):
            manifest["run"]["artifacts"][name]["sha256"]=self.helper.digest(directory/name)
        manifest_path.write_text(yaml.safe_dump(manifest))
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")
        # Restore a correct raw/witness binding, then isolate resource typing.
        raw["measurement"]["sum"]=1; raw_path.write_text(json.dumps(raw))
        certificate["worksheet_witness"]["raw_result_sha256"]=self.helper.digest(raw_path)
        certificate_path.write_text(yaml.safe_dump(certificate))
        for name in ("raw-result.json","certificate.yaml"):
            manifest["run"]["artifacts"][name]["sha256"]=self.helper.digest(directory/name)
        manifest["run"]["resources"]["cpu_seconds"]=True
        manifest_path.write_text(yaml.safe_dump(manifest))
        with self.assertRaises(ValueError):
            self.invoke("check",directory,"a")

    def test_separate_route_dependency_and_changed_previous_artifact(self):
        first=self.directory("a"); self.invoke("run",first,"a"); self.invoke("check",first,"a")
        hashes={p.name:self.helper.digest(p) for p in first.iterdir()}
        receipt=dict(schema="crypto.autoresearch.trial_receipt.v1",status="output_validated",returncode=0,check_returncode=0,
            plan_sha256=self.helper.digest(self.plan_path),trial_id="synthetic-a",run_id="RUN-ECDLP-aa0001",artifact_sha256=hashes)
        (first/"execution-receipt.json").write_text(json.dumps(receipt))
        second=self.directory("b"); self.invoke("run",second,"b"); self.invoke("check",second,"b")
        m=yaml.safe_load((second/"manifest.yaml").read_text())["run"]
        self.assertTrue(m["result"]["metrics"]["implementations_agree"])
        with (first/"raw-result.json").open("a") as stream:
            stream.write("\n")
        with self.assertRaises(ValueError):
            self.invoke("check",second,"b")

    def test_route_comparison_binds_canonical_witness(self):
        first=self.directory("a"); self.invoke("run",first,"a"); self.invoke("check",first,"a")
        # A synthetic dependency has equal measurements but a different witness.
        # This deliberately mocked receipt is not authenticated execution evidence.
        raw_path=first/"raw-result.json"; raw=json.loads(raw_path.read_text())
        raw["witness"]["terms"]=[3,4]
        raw_path.write_text(json.dumps(raw))
        receipt=dict(schema="crypto.autoresearch.trial_receipt.v1",status="output_validated",returncode=0,check_returncode=0,
            plan_sha256=self.helper.digest(self.plan_path),trial_id="synthetic-a",run_id="RUN-ECDLP-aa0001",
            artifact_sha256={p.name:self.helper.digest(p) for p in first.iterdir()})
        (first/"execution-receipt.json").write_text(json.dumps(receipt))
        second=self.directory("b"); self.invoke("run",second,"b"); self.invoke("check",second,"b")
        manifest=yaml.safe_load((second/"manifest.yaml").read_text())["run"]
        self.assertFalse(manifest["result"]["metrics"]["implementations_agree"])
        self.assertFalse(manifest["result"]["valid"])


if __name__=="__main__":
    unittest.main(verbosity=2)
