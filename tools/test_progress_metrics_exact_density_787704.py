"""Committed-state controls for the fixed exact-density observation reader.

These are reader integrity tests; they do not rerun any scientific experiment.
"""
import contextlib
import copy
import gzip
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).with_name('progress_metrics.py')
spec = importlib.util.spec_from_file_location('exact_density_pm_under_test', MODULE)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)
RAW = 'experiments/EXP-ECDLP-787704/runs/RUN-ECDLP-53b08d/summary.json.gz'
REVIEW = ('coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-f7bbdf/'
          'reviews/TASK-20261030-cd89e7/independent-summary.json')
SOURCE_REPO = Path(os.environ.get('PM_TEST_SOURCE_REPO', Path(__file__).resolve().parents[1]))
SOURCE_REF = os.environ.get('PM_TEST_SOURCE_REF', 'HEAD')


class CommittedDensityReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = subprocess.check_output(['git', '-C', str(SOURCE_REPO), 'show', f'{SOURCE_REF}:{RAW}'])
        cls.review_bytes = subprocess.check_output(['git', '-C', str(SOURCE_REPO), 'show', f'{SOURCE_REF}:{REVIEW}'])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.previous_repo = pm.REPO
        pm.REPO = self.repo
        self.git('init', '-q')
        self.git('config', 'user.name', 'fixed-reader-control')
        self.git('config', 'user.email', 'fixed-reader-control@example.invalid')
        self.write(RAW, self.raw_bytes)
        self.write(REVIEW, self.review_bytes)
        self.commit()

    def tearDown(self):
        pm.REPO = self.previous_repo
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE).decode().strip()

    def write(self, path, data):
        out = self.repo / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixed committed source snapshot')
        return self.git('rev-parse', 'HEAD')

    def read(self, ref='HEAD', since='2026-10-30'):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pm.exact_density_787704_observations(ref, since)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def alter_review(self, mutate):
        data = json.loads(self.review_bytes)
        mutate(data)
        self.write(REVIEW, json.dumps(data).encode())
        self.commit()

    def test_full_committed_observations_and_explicit_zero(self):
        rows = self.read()
        self.assertEqual(len(rows), 30)
        by = {r['metric']: r for r in rows}
        self.assertEqual(len(by), len(rows))
        prefix = 'ecdlp.exact_density.787704.'
        self.assertEqual(by[prefix+'nonzero_states']['value'], 821638)
        self.assertEqual(by[prefix+'t1.e2.curves_positive_q']['value'], 35)
        self.assertEqual(by[prefix+'t2.e2.curves_zero_q']['value'], 0)
        self.assertTrue(all(r['better'] == 'neutral' for r in rows))
        self.assertTrue(all(RAW in r['source'] and REVIEW in r['source'] for r in rows))

    def test_dirty_and_untracked_payloads_do_not_change_committed_output(self):
        before = self.read()
        self.write(RAW, b'not gzip')
        self.write(REVIEW, b'{"fabricated": true}')
        self.write('summary.json', b'{}')
        self.assertEqual(self.read(), before)

    def test_missing_committed_review_has_no_working_tree_fallback(self):
        self.git('rm', REVIEW)
        self.git('commit', '-qm', 'remove committed review')
        self.write(REVIEW, self.review_bytes)
        self.assertEqual(self.read(), [])

    def test_missing_committed_raw_has_no_working_tree_fallback(self):
        self.git('rm', RAW)
        self.git('commit', '-qm', 'remove committed raw summary')
        self.write(RAW, self.raw_bytes)
        self.assertEqual(self.read(), [])

    def test_incomplete_or_duplicate_cell_makes_all_metrics_unknown(self):
        self.alter_review(lambda d: d['rows'].__setitem__(-1, copy.deepcopy(d['rows'][0])))
        self.assertEqual(self.read(), [])

    def test_disagreement_not_reported_as_zero(self):
        self.alter_review(lambda d: d['rows'][0].__setitem__('success_numerator', 1))
        self.assertEqual(self.read(), [])

    def test_forged_export_qualification_not_accepted(self):
        self.alter_review(lambda d: d['integrity'].__setitem__('frozen_protocol_export_returncode', 0))
        self.assertEqual(self.read(), [])

    def test_duplicate_json_member_is_rejected(self):
        self.write(REVIEW, b'{"schema":"first",' + self.review_bytes.lstrip()[1:])
        self.commit()
        self.assertEqual(self.read(), [])

    def test_wrong_data_type_is_rejected(self):
        self.alter_review(lambda d: d['rows'][0].__setitem__('success_numerator', True))
        self.assertEqual(self.read(), [])

    def test_invalid_gzip_is_unknown(self):
        self.write(RAW, b'not gzip')
        self.commit()
        self.assertEqual(self.read(), [])

    def test_date_filter_and_nonexistent_ref_emit_nothing(self):
        self.assertEqual(self.read(since='2026-10-31'), [])
        self.assertEqual(self.read(ref='does-not-exist'), [])

    def test_exact_ref_is_stable_after_new_commit(self):
        fixed = self.git('rev-parse', 'HEAD')
        before = self.read(fixed)
        self.alter_review(lambda d: d.__setitem__('schema', 'wrong'))
        self.assertEqual(self.read(), [])
        self.assertEqual(self.read(fixed), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
