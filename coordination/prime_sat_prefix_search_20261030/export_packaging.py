#!/usr/bin/env python3
"""Post-data packaging correction; invokes the unchanged frozen PSEARCH analysis."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import experiment_protocol as native
import yaml


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Packaging:
    def __init__(self, expected):
        self.expected = expected
        self.seen = {}

    def row(self, **kw):
        arm = kw['arm']
        assert arm in self.expected and arm not in self.seen, 'unexpected or duplicate arm'
        assert kw['instance_id'] == 'fixed_inventory', 'unexpected instance label'
        assert type(kw['seed']) is int and kw['seed'] == 0, 'wrong seed'
        assert type(kw['replicate']) is int and kw['replicate'] == 0, 'wrong replicate'
        original = native.run_row(**kw)
        corrected = copy.deepcopy(original)
        corrected['instance_id'] = '0'
        self.compare(original, corrected)
        self.seen[arm] = {'before': original['instance_id'], 'after': corrected['instance_id'],
                          'seed': original['seed'], 'replicate': original['replicate'],
                          'all_other_fields_equal': True}
        return corrected

    @staticmethod
    def compare(original, corrected):
        expected = copy.deepcopy(original)
        expected['instance_id'] = '0'
        assert corrected == expected, 'nonidentity field changed'

    def complete(self):
        assert set(self.seen) == set(self.expected), 'missing arm'


def fixtures(expected):
    def kwargs():
        return dict(run_id='metadata-fixture', arm=next(iter(expected)), instance_id='fixed_inventory',
                    seed=0, replicate=0, status='succeeded', attempts=1,
                    measurements={'counted': {}, 'wall_valid': False},
                    verification={'status': 'not_run'}, exclusion={'excluded': False, 'rule': None},
                    artifacts=[], isolation={'tier': 'none', 'contended': None, 'blockers': []})
    k = kwargs(); p = Packaging(expected); row = p.row(**k)
    table = {(x['arm'], x['instance_id'], x['replicate']): x['seed'] for x in expected.values()}
    assert (k['arm'], k['instance_id'], k['replicate']) not in table
    assert table[(row['arm'], row['instance_id'], row['replicate'])] == row['seed']
    rejected = []
    for key, value in [('seed', 1), ('replicate', 1), ('arm', 'not-an-arm'), ('instance_id', 'unexpected')]:
        bad = dict(k); bad[key] = value
        try: Packaging(expected).row(**bad)
        except AssertionError: rejected.append(key)
        else: raise AssertionError('accepted malformed metadata')
    for label, action in [('duplicate', lambda: p.row(**k)), ('missing', p.complete),
                          ('nonidentity', lambda: Packaging.compare(row, dict(row, seed=9)))]:
        try: action()
        except AssertionError: rejected.append(label)
        else: raise AssertionError('accepted ' + label)
    return {'original_label_outside_seed_table': True, 'corrected_label_matches_seed_table': True,
            'rejected': rejected, 'scientific_samples': 0}


def main():
    ap = argparse.ArgumentParser()
    for flag in ['raw', 'protocol', 'out', 'analysis-out']:
        ap.add_argument('--' + flag, type=Path, required=True)
    args = ap.parse_args()
    paths = {k: v.resolve() for k, v in vars(args).items()}
    receipt = HERE / 'export-packaging-check.json'
    assert not any(p.exists() for p in [paths['out'], paths['analysis_out'], receipt]), 'refuse existing output'
    admission_path = HERE / 'export-packaging-admission.yaml'
    admission = yaml.safe_load(admission_path.read_text())
    helper = HERE / 'export_results.py'
    failure = HERE / 'export-packaging-failure-01.json'
    assert digest(helper) == admission['observed_source']['sha256']
    assert digest(paths['protocol']) == admission['protocol']['file_sha256']
    assert digest(failure) == admission['original_failure']['sha256']
    assert digest(ROOT / 'tools/experiment_protocol.py') == admission['native_validator']['sha256']
    protocol = native.read_json(paths['protocol'])
    expected = {x['arm']: x for x in admission['protocol']['expected_rows']}
    table = native.seeds_table(protocol)
    assert sorted((x['arm'], x['instance'], x['replicate'], x['seed']) for x in table) == sorted(
        (x['arm'], x['instance_id'], x['replicate'], x['seed']) for x in expected.values())
    checks = fixtures(expected)
    spec = importlib.util.spec_from_file_location('frozen_psearch_export', helper)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    packaging = Packaging(expected)
    validations = []
    class Facade:
        def __getattr__(self, name):
            return getattr(native, name)
        def run_row(self, **kw):
            return packaging.row(**kw)
        def lint_export(self, export, proto, base, verify_files):
            packaging.complete()
            assert verify_files is True
            for p in [admission_path, Path(__file__).resolve(), failure, helper]:
                ref = module.ref(p, base, 'other')
                if ref not in export['files']: export['files'].append(ref)
            export['notes'].append({'kind': 'observation', 'by': 'postdata-packaging-adapter',
                'text': 'Command includes export_packaging.py admitted after data. Unchanged frozen export_results.py performs all analysis; adapter changes only six aggregate instance labels fixed_inventory to protocol index 0. Seed0/replicate0 and every other row field are unchanged. Six bundles are not independent samples. Admission, adapter and retained original failure are hash-bound in files; final correction receipt is archived separately.'})
            errors = native.schema_errors(export, 'experiment.export/v1')
            errors += native.lint_export(export, proto, base, verify_files=True)
            validations.append({'schema_and_full_native_lint_errors': errors})
            return errors
    module.ep = Facade()
    module.build(paths['raw'], paths['protocol'], paths['out'], paths['analysis_out'])
    assert len(validations) == 1 and not validations[0]['schema_and_full_native_lint_errors']
    native.write_once(receipt, {'schema': 'prime-prefix-search-packaging-check/v1',
        'post_data': True, 'frozen_helper_invoked_unchanged': True,
        'input_hashes': {str(p.relative_to(ROOT)): digest(p) for p in [helper, admission_path, failure, Path(__file__).resolve(), paths['protocol']]},
        'metadata_fixtures': checks, 'row_corrections': packaging.seen, 'validation': validations,
        'outputs': {str(p.relative_to(ROOT)): digest(p) for p in [paths['out'], paths['analysis_out']]},
        'scientific_runs': 0, 'solver_invocations': 0, 'native_validator_modified': False})
    print(json.dumps({'packaging_receipt': str(receipt), 'native_validation': 'passed'}))

if __name__ == '__main__':
    main()
