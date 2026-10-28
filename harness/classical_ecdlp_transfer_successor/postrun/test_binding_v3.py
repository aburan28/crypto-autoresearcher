"""Actual frozen metadata only; no scientific data or verifier execution."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys

BASE = Path(__file__).parent
REPO = Path('/workspace/classical-ecdlp-validation-ready')
SOURCE = REPO / 'harness/classical_ecdlp_transfer_successor'
PROTOCOL_PATH = REPO / 'experiments/EXP-ECDLP-8dc19d/protocol.json'
SPEC = importlib.util.spec_from_file_location('successor_binding_v3', BASE / 'run_postrun.v3.py')
V3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V3)


class FrozenBinding(unittest.TestCase):
    def test_actual_analysis_and_independent_verifier_have_separate_pins(self):
        protocol = V3.read(PROTOCOL_PATH)
        manifest = V3.read(SOURCE / 'source-manifest.json')
        for name, digest in manifest['files'].items():
            self.assertEqual(V3.analysis.sha(SOURCE / name), digest)
        self.assertEqual(manifest['files']['verify.py'], '2654f5c9d800233447c8e2deed5a9fff7ee674adc1fb5214319e184857ca7d5a')
        self.assertNotEqual(manifest['files']['verify.py'], protocol['analysis_plan']['script']['sha256'])
        self.assertEqual(V3.analysis.sha(BASE / 'analysis.py'), protocol['analysis_plan']['script']['sha256'])

    def test_export_identifies_actual_registered_analysis(self):
        sys.path.insert(0, str(REPO / 'tools'))
        import experiment_protocol as ep
        protocol = V3.read(PROTOCOL_PATH)
        manifest = V3.read(SOURCE / 'source-manifest.json')
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            for target, original in [('compute-plan.json', SOURCE / 'compute-plan.json'),
                                     ('source-manifest.json', SOURCE / 'source-manifest.json'),
                                     ('prior-exclusions.json', REPO / protocol['extensions']['transfer_study']['prior_exclusions']['path'])]:
                (out / target).write_bytes(original.read_bytes())
            (out / 'provider-context.json').write_text('{"synthetic_metadata_test":true}\n')
            (out / 'census.json').write_text('{}\n')
            census = {'source_revision_c': manifest['source_revision_c'], 'per_curve_arm_metrics': [],
                      'attempt_accounting': {'synthetic_metadata_test': True}, 'common_work': None,
                      'compute_summary': None, 'parse_and_mapping_findings': []}
            bundle = V3.make_export(ep, protocol, PROTOCOL_PATH, SOURCE, out, out, out, 'synthetic-binding-only',
                                    out / 'census.json', out / 'absent-report.json', census, [], {})
            self.assertEqual(bundle['analysis']['script']['sha256'], protocol['analysis_plan']['script']['sha256'])
            self.assertEqual((out / bundle['analysis']['script']['path']).resolve(), (BASE / 'analysis.py').resolve())
            self.assertEqual(bundle['runs'], [])  # In-memory metadata check, never published as a measurement.


if __name__ == '__main__':
    unittest.main()
