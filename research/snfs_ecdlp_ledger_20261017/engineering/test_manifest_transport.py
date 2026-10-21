"""Transport fixtures only. No scientific producer or trial is executed."""
from pathlib import Path
import importlib.util,json,tempfile,unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from manifest_transport import prepare,digest
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tools'))
import validate_ledger
import yaml

class TransportTests(unittest.TestCase):
    def fixture(self,root):
        run=root/'experiments/EXP-ECDLP-f34097/runs/RUN-ECDLP-62ec3d';run.mkdir(parents=True)
        (run/'launch.json').write_text(json.dumps(dict(run_id=run.name,authority={'commit':'a'*40},argv=['fixture-only'],plan_sha256='b'*64,started_at='2026-10-17T00:00:00Z')))
        (run/'environment.json').write_text(json.dumps(dict(commit='a'*40,platform='fixture',source_sha256={'fixture.py':'c'*64})))
        (run/'raw-result.json').write_text(json.dumps({'fixture_only':True,'experiment_id':'EXP-ECDLP-f34097'}))
        (run/'producer-manifest.yaml').write_text(yaml.safe_dump(dict(experiment_id='EXP-ECDLP-f34097',id=run.name,metrics={'fixture_only':True},raw_result_sha256=digest(run/'raw-result.json'))))
        for name in ('command.txt','stdout.log','stderr.log'):(run/name).write_text('fixture only')
        return run
    def call(self,run):return prepare(run,experiment_id='EXP-ECDLP-f34097',run_id='RUN-ECDLP-62ec3d',scientific_parameters={'fixture_only':True})
    def test_copies_observation_without_claiming_validation(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));before=digest(run/'producer-manifest.yaml');m=yaml.safe_load(self.call(run).read_text())
            self.assertEqual(before,digest(run/'producer-manifest.yaml'));self.assertFalse(m['run']['result']['output_validated']);self.assertEqual(m['run']['result']['certificate']['kind'],'none');self.assertTrue(m['metrics']['fixture_only'])
    def test_current_run_schema_accepts_fixture_envelope(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));manifest=self.call(run);ctx=validate_ledger.Ctx(set());validate_ledger.check_run(str(manifest),ctx)
            self.assertEqual(ctx.errors,[])
    def test_refuses_sealed_run(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));(run/'execution-receipt.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'sealed'):self.call(run)
    def test_refuses_wrong_identity(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));p=run/'launch.json';j=json.loads(p.read_text());j['run_id']='RUN-ECDLP-000000';p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'identity'):self.call(run)
    def test_refuses_raw_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));(run/'raw-result.json').write_text('{"tampered_fixture":true}')
            with self.assertRaisesRegex(ValueError,'digest'):self.call(run)
    def test_refuses_source_commit_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));p=run/'environment.json';j=json.loads(p.read_text());j['commit']='d'*40;p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'commit'):self.call(run)
    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            run=self.fixture(Path(d));self.call(run)
            with self.assertRaises(FileExistsError):self.call(run)

if __name__=='__main__':unittest.main()
