"""Committed-Git controls for exploratory relation-diversity gauges."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('prym_lead_metrics', Path(__file__).resolve().parents[1]/'tools/progress_metrics.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
SOURCE = 'research/prym_leads_20261027/derived/matrix-duplicate-review.json'


class DiversityGaugesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('commit', '--allow-empty', '-qm', 'empty')
        self.empty = self.git('rev-parse', 'HEAD').strip()
        self.document = dict(schema='prym-retained-duplicate-explanation/v1', new_scientific_trials=0,
                             source_logical_sha256='8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007',
                             cells=[dict(ec1_curve_uid='urn:ec-record:1:sha256:'+'a'*64,
                                         native_witnesses=7, distinct_projected_affine_rows=2,
                                         rank_of_distinct_rows=2, dependencies_among_distinct_rows=0,
                                         groups=[dict(native_witness_count=n, admissible_constraint_triples=n,
                                                      exact_constraint_subset_match=True) for n in [3, 4]])])

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=test',
                                        '-c', 'user.email=test@example.invalid', *args], text=True)

    def commit(self, document):
        p = self.root/SOURCE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(document))
        self.git('add', SOURCE)
        self.git('commit', '-qm', 'review')
        return self.git('rev-parse', 'HEAD').strip()

    def read(self, ref):
        out = io.StringIO()
        with patch.object(M, 'REPO', self.root), contextlib.redirect_stdout(out):
            M.prym_equation_diversity(ref)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_committed_counts_keep_exploratory_neutral_provenance(self):
        ref = self.commit(self.document)
        rows = self.read(ref)
        self.assertEqual({r['metric'].rsplit('.', 1)[-1]: r['value'] for r in rows},
                         dict(distinct_affine_rows=2, duplicate_witnesses=5))
        self.assertTrue(all(r['better'] == 'neutral' and r['kind'] == 'gauge'
                            and 'exploratory' in r['metric'] and r['source'] == SOURCE+'@'+ref for r in rows))

    def test_dirty_untracked_and_missing_sources_cannot_supply_values(self):
        ref = self.commit(self.document)
        rows = self.read(ref)
        (self.root/SOURCE).write_text('{"planned_rank":15}')
        self.assertEqual(self.read(ref), rows)
        self.assertEqual(self.read(self.empty), [])

    def test_invalid_or_inconsistent_source_emits_nothing_atomically(self):
        for change in [lambda d: d['cells'][0].update(native_witnesses=True),
                       lambda d: d['cells'][0].update(native_witnesses=8),
                       lambda d: d['cells'][0].update(rank_of_distinct_rows=1),
                       lambda d: d.update(new_scientific_trials=True),
                       lambda d: d.update(source_logical_sha256='0'*64),
                       lambda d: d['cells'].append(copy.deepcopy(d['cells'][0]))]:
            with self.subTest(change=change):
                document = copy.deepcopy(self.document)
                change(document)
                self.assertEqual(self.read(self.commit(document)), [])

    def test_selected_commit_is_unchanged_after_branch_advances(self):
        ref = self.commit(self.document)
        original = self.read(ref)
        changed = copy.deepcopy(self.document)
        changed['cells'][0]['native_witnesses'] = 9
        changed['cells'][0]['groups'][0].update(native_witness_count=5, admissible_constraint_triples=5)
        self.commit(changed)
        self.assertEqual(self.read(ref), original)


if __name__ == '__main__':
    unittest.main()
