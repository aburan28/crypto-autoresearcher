"""Complete planted native-shaped packages only; no target labels or network."""
from contextlib import redirect_stdout
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

import export_width as export


class WidthExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='software-export-', dir=export.HERE)
        self.root = Path(self.temp.name)
        self.protocol_path = self.root/'protocol.json'
        self.protocol = export.ep.read_json(export.ROOT/'experiments/EXP-ECDLP-a9b6a5/protocol.json')
        self.protocol['protocol_id'] = 'PLANTED-width-export-software-only'
        self.protocol['analysis_plan']['script'] = dict(path=str(Path(export.__file__).resolve()),
                                                        sha256=export.ep.sha256_file(Path(export.__file__)))
        self.protocol['analysis_plan']['frozen_before_data'] = True
        for arm, character in zip(self.protocol['arms'], ['1', '2']):
            arm['instrument'].update(commit=character*40, binary_sha256=character*64)
        self.protocol['freeze'].update(status='frozen', protocol_sha256=None,
                                       commit='3'*40, frozen_at='2026-10-26T00:00:00Z',
                                       filed_before_affected_data=True)
        self.protocol['freeze']['protocol_sha256'] = export.ep.protocol_hash(self.protocol)
        self.protocol_path.write_text(json.dumps(self.protocol))
        self.candidate = self.package('candidate', '1', 'm16_full35840')
        self.reference = self.package('reference', '2', 'full3584')
        self.output = self.root/'export.json'

    def tearDown(self):
        self.temp.cleanup()

    def package(self, name, character, native_arm):
        directory = self.root/name
        directory.mkdir()
        fixtures = [dict(uid=name+'-'+str(b), p=101, b=b) for b in [13, 16]]
        fixture_path = directory/'fixtures.json'
        fixture_path.write_text(json.dumps(dict(fixtures=fixtures)))
        fixture_relative = str(fixture_path.relative_to(export.ROOT))
        protocol_relative = str(self.protocol_path.relative_to(export.ROOT))
        run_id = 'PLANTED-'+name
        cells = [dict(curve_uid=f['uid'], p=101, b=f['b'], arm=native_arm, seed=0,
                      attempts=64, rows=[{'planted': True}, {'planted': True}],
                      reasons={'+': 2, 'R': 62},
                      projection=dict(U=3, rank=1, augmented_rank=1),
                      attack_operation_vector={'field_mul': 123}, online_matrix_units=9,
                      cache_entries={'source': 2}, source_checkpoints=[{'attempt': 64, 'rank': 1}],
                      wall_seconds=1.25, cpu_seconds=1.0) for f in fixtures]
        raw = dict(software_control=True, complete=True, experiment_id='PLANTED-'+name, run_id=run_id,
                   cells=cells, protocol_binding=dict(path=protocol_relative,
                        file_sha256=export.ep.sha256_file(self.protocol_path),
                        canonical_sha256=self.protocol['freeze']['protocol_sha256']))
        (directory/'raw-result.json').write_text(json.dumps(raw))
        checks = [dict(curve_uid=f['uid'], arm=native_arm, attempts_replayed=64, rows_verified=2,
                       U=3, rank=1, augmented_rank=1) for f in fixtures]
        check = dict(status='passed', cells=checks, raw_result_sha256=export.ep.sha256_file(directory/'raw-result.json'),
                     replay_operation_vector={'branches_replayed': 128}, wall_seconds=0.25)
        (directory/'verification.json').write_text(json.dumps(check))
        manifest = dict(id=run_id, experiment_id='PLANTED-'+name,
                        code=dict(repository='PLANTED-SOFTWARE-ONLY', commit=character*40, dirty_tree='',
                                  source_sha256={export.ARM_SOURCE['m16_candidate' if name == 'candidate' else 'm8_reference']: character*64}),
                        inputs=dict(config={'fixture_file': fixture_relative}, sha256={
                            fixture_relative: export.ep.sha256_file(fixture_path),
                            protocol_relative: export.ep.sha256_file(self.protocol_path)}))
        (directory/'manifest.yaml').write_text(yaml.safe_dump({'run': manifest}))
        (directory/'environment.json').write_text(json.dumps(dict(commit=character*40, platform='planted')))
        (directory/'launch.json').write_text(json.dumps(dict(run_id=run_id, authority={'commit': character*40},
                                                            plan_sha256='4'*64, argv=['planted-native'])))
        (directory/'events.jsonl').write_text('{"software_control":true}\n')
        self.reseal(directory, run_id)
        return directory

    def reseal(self, directory, run_id=None):
        path = directory/'execution-receipt.json'
        receipt = json.loads(path.read_text()) if path.exists() else dict(
            run_id=run_id, plan_sha256='4'*64, status='output_validated', resumed=0)
        receipt['artifact_sha256'] = {n: export.ep.sha256_file(directory/n) for n in export.REQUIRED
                                      if n != 'execution-receipt.json'}
        path.write_text(json.dumps(receipt))

    def mutate_raw(self, directory, mutate):
        path = directory/'raw-result.json'
        raw = json.loads(path.read_text())
        mutate(raw)
        path.write_text(json.dumps(raw))
        checker = json.loads((directory/'verification.json').read_text())
        checker['raw_result_sha256'] = export.ep.sha256_file(path)
        (directory/'verification.json').write_text(json.dumps(checker))
        self.reseal(directory)

    def build(self):
        return export.build(self.protocol_path, self.candidate, self.reference, self.output, software=True)

    def test_complete_package_generic_check_export_and_files(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(export.main(['export', '--protocol', str(self.protocol_path),
                '--candidate-run-dir', str(self.candidate), '--reference-run-dir', str(self.reference),
                '--output', str(self.output), '--software']), 0)
        result = export.ep.read_json(self.output)
        self.assertEqual(result['flow']['planned'], 4)
        self.assertEqual(result['flow']['completed'], 4)
        self.assertEqual(result['runs'][0]['measurements']['counted'],
                         {'attempted': 64, 'accepted': 2, 'U': 3, 'rank': 1, 'augmented_rank': 1, 'nullity': 2})
        self.assertTrue(all(not r['measurements']['wall_valid'] for r in result['runs']))
        self.assertIsNone(result['producer']['model'])
        self.assertIsNone(result['host']['summary']['cpu_model'])
        checked = subprocess.run([sys.executable, str(export.ROOT/'tools/experiment_protocol.py'), 'check-export',
                                  str(self.output), '--protocol', str(self.protocol_path), '--verify-files'],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(checked.returncode, 0, checked.stdout+checked.stderr)
        self.assertIn('(0 finding(s))', checked.stdout)

    def test_wrong_protocol_and_script_refused(self):
        self.protocol['question'] += ' post-freeze mutation'
        self.protocol_path.write_text(json.dumps(self.protocol))
        with self.assertRaises(export.ep.Refused):
            self.build()

    def test_wrong_file_bytes_refused(self):
        (self.reference/'events.jsonl').write_text('changed')
        with self.assertRaisesRegex(export.ep.Refused, 'commitment'):
            self.build()

    def test_seed_missing_and_wrong_refused_without_planned_fill(self):
        for value in [None, 1]:
            self.mutate_raw(self.candidate, lambda raw: raw['cells'][0].update(seed=value))
            with self.assertRaisesRegex(export.ep.Refused, 'seed'):
                self.build()

    def test_missing_successful_cell_coverage_refused(self):
        self.mutate_raw(self.reference, lambda raw: raw['cells'].pop())
        with self.assertRaisesRegex(export.ep.Refused, 'coverage'):
            self.build()

    def test_missing_observed_commit_refused(self):
        path = self.reference/'manifest.yaml'
        manifest = yaml.safe_load(path.read_text())
        manifest['run']['code']['commit'] = None
        path.write_text(yaml.safe_dump(manifest))
        self.reseal(self.reference)
        with self.assertRaisesRegex(export.ep.Refused, 'identity'):
            self.build()

    def test_missing_observed_executable_identity_refused(self):
        path = self.reference/'manifest.yaml'
        manifest = yaml.safe_load(path.read_text())
        manifest['run']['code']['source_sha256'] = {}
        path.write_text(yaml.safe_dump(manifest))
        self.reseal(self.reference)
        with self.assertRaisesRegex(export.ep.Refused, 'executable source identity'):
            self.build()

    def test_generic_checker_rejects_wrong_protocol_and_cell_coverage(self):
        result, _, _ = self.build()
        for name, mutation in [('protocol', lambda e: e['protocol'].update(sha256='0'*64)),
                               ('coverage', lambda e: e['runs'].pop())]:
            bad = deepcopy(result)
            mutation(bad)
            bad['flow'] = export.ep.compute_flow(bad['runs'])
            path = self.root/(name+'-bad-export.json')
            path.write_text(json.dumps(bad))
            checked = subprocess.run([sys.executable, str(export.ROOT/'tools/experiment_protocol.py'),
                'check-export', str(path), '--protocol', str(self.protocol_path), '--verify-files'],
                capture_output=True, text=True, check=False)
            self.assertEqual(checked.returncode, 1, checked.stdout+checked.stderr)

    def test_historical_pointer_is_not_hydration(self):
        (self.reference/'raw-result.json').unlink()
        (self.reference/'raw-result.json.gz.blob.json').write_text('{"uri":"s3://PLANTED-NO-GET"}')
        with self.assertRaisesRegex(export.ep.Refused, 'hydrate'):
            self.build()

    def test_resumed_unknown_clock_invalid_and_counters_retained(self):
        path = self.candidate/'execution-receipt.json'
        receipt = json.loads(path.read_text())
        receipt['resumed'] = 2
        path.write_text(json.dumps(receipt))
        result, _, _ = self.build()
        row = result['runs'][0]
        self.assertEqual(row['resumed'], 2)
        self.assertFalse(row['measurements']['wall_valid'])
        self.assertEqual(row['measurements']['counters']['reason_R'], 62)
        self.assertEqual(row['measurements']['counters']['producer.attack_operation_vector.field_mul'], 123)
        self.assertEqual(row['measurements']['counters']['checker.replay_operation_vector.branches_replayed'], 128)

    def test_native_failure_remains_excluded_row_and_flow(self):
        def incomplete(raw):
            raw.update(complete=False, cells=[])
            raw.pop('protocol_binding')
        self.mutate_raw(self.candidate, incomplete)
        path = self.candidate/'execution-receipt.json'
        receipt = json.loads(path.read_text()); receipt['status'] = 'timeout'
        path.write_text(json.dumps(receipt))
        result, _, _ = self.build()
        self.assertEqual(result['flow']['not_completed'], 2)
        self.assertEqual(len(result['flow']['excluded'][0]['run_ids']), 2)
        self.assertIsNone(result['runs'][0]['seed'])
        self.assertEqual(result['runs'][0]['measurements']['counted'], {})

    def test_sealed_run_output_refused(self):
        with self.assertRaisesRegex(export.ep.Refused, 'sealed'):
            export.build(self.protocol_path, self.candidate, self.reference,
                         self.candidate/'export.json', software=True)

    def test_protocol_full_file_and_canonical_binding_are_distinct(self):
        import runtime_width
        relative = str(self.protocol_path.relative_to(export.ROOT))
        digest = export.ep.sha256_file(self.protocol_path)
        plan = dict(input_sha256={relative: digest},
                    execution_plan={'protocol_hashes': [dict(path=relative, sha256=digest)]})
        binding = runtime_width.validate_protocol_binding(plan, self.protocol_path)
        self.assertEqual(binding['canonical_sha256'], self.protocol['freeze']['protocol_sha256'])
        self.assertNotEqual(binding['canonical_sha256'], binding['file_sha256'])
        specification = self.root/'specification.yaml'
        specification.write_text(yaml.safe_dump({'experiment': {'execution_plan': deepcopy(plan['execution_plan'])}}))
        plan['specification'] = str(specification.relative_to(export.ROOT))
        self.assertEqual(runtime_width.validate_protocol_binding(plan, self.protocol_path), binding)
        specification.write_text(yaml.safe_dump({'experiment': {'execution_plan': {'protocol_hashes': []}}}))
        with self.assertRaisesRegex(ValueError, 'specification protocol'):
            runtime_width.validate_protocol_binding(plan, self.protocol_path)
        plan['execution_plan']['protocol_hashes'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'binding'):
            runtime_width.validate_protocol_binding(plan, self.protocol_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
