"""Adversarial integrity checks against real, tiny Git histories."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import claim_evidence_matrix as matrix


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.data = b'Header\nA bounded claim.\nEnd\n'
        (self.repo / 'evidence.txt').write_bytes(self.data)
        (self.repo / 'link').symlink_to('evidence.txt')
        self.git('add', 'evidence.txt', 'link')
        self.git('commit', '-qm', 'fixture')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.source = dict(id='source', kind='git', repo='fixture', commit=self.commit,
                           path='evidence.txt', blob_oid=self.git('rev-parse', 'HEAD:evidence.txt').strip(),
                           sha256=matrix.digest(self.data))
        self.claim = dict(id='claim', classification='computed', source_id='source',
                          excerpt=dict(start_line=2, end_line=2, text='A bounded claim.\n',
                                       sha256=matrix.digest(b'A bounded claim.\n')),
                          statement='A bounded claim.', assumptions=[], evidence={},
                          open_obligations=['Execution review absent.'])
        self.record = dict(schema=matrix.SCHEMA,
                           scope=dict(objective='Fixture', coverage='partial', omissions=['Other claims.']),
                           sources=[self.source], claims=[self.claim])

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def check(self):
        return matrix.check(self.record, {'fixture': self.repo})

    def test_working_tree_edits_cannot_change_bound_evidence(self):
        (self.repo / 'evidence.txt').write_text('Different uncommitted claim')
        result = self.check()
        self.assertEqual(result['integrity_status'], 'passed')
        self.assertFalse(result['coverage_complete'])
        self.assertIsNone(result['individual_claim_denominator'])

    def test_all_roles_present_does_not_promote_scientific_validity(self):
        self.claim['evidence'] = {r: ['source'] for r in matrix.REQUIRED['computed']}
        result = self.check()
        self.assertEqual(result['claims'][0]['missing_evidence_roles'], [])
        self.assertEqual(result['claims'][0]['scientific_validity'], 'not_assessed_by_integrity_checker')

    def test_unavailable_evidence_remains_missing(self):
        self.record['sources'].append(dict(id='missing', kind='unavailable', locator='old run', reason='not archived'))
        self.claim['evidence']['replay'] = ['source', 'missing']
        result = self.check()['claims'][0]
        self.assertIn('replay', result['missing_evidence_roles'])
        self.assertEqual(result['unavailable_evidence'], ['missing'])

    def test_false_bindings_refused(self):
        original = copy.deepcopy(self.record)
        for field, value in [('commit', 'HEAD'), ('commit', self.source['blob_oid']),
                             ('blob_oid', '0' * 40), ('sha256', '0' * 64),
                             ('path', '../evidence.txt'), ('path', './evidence.txt'),
                             ('path', 'absent')]:
            with self.subTest(field=field, value=value):
                self.record = copy.deepcopy(original)
                self.record['sources'][0][field] = value
                with self.assertRaises(matrix.MatrixError):
                    self.check()

    def test_symlink_source_refused(self):
        self.source.update(path='link', blob_oid=self.git('rev-parse', 'HEAD:link').strip(),
                           sha256=matrix.digest(b'evidence.txt'))
        with self.assertRaisesRegex(matrix.MatrixError, 'regular Git blob'):
            self.check()

    def test_local_git_replacement_cannot_substitute_source(self):
        original = self.source['blob_oid']
        (self.repo / 'replacement').write_text('Fabricated result\n')
        replacement = self.git('hash-object', '-w', 'replacement').strip()
        self.git('replace', original, replacement)
        self.assertEqual(self.check()['integrity_status'], 'passed')

    def test_aggregate_cap_refuses_before_fetching_next_blob(self):
        self.record['sources'].append({**self.source, 'id': 'second'})
        with patch.object(matrix, 'MAX_TOTAL', len(self.data)*2-1), patch.object(matrix, 'git', wraps=matrix.git) as calls:
            with self.assertRaisesRegex(matrix.MatrixError, 'total reader limit'):
                self.check()
        fetches = [call for call in calls.call_args_list if call.args[1:3] == ('cat-file', 'blob')]
        self.assertEqual(len(fetches), 1)

    def test_cli_refuses_oversized_matrix_before_git_reads(self):
        path = self.repo / 'oversized.json'
        path.write_text(json.dumps(self.record))
        with patch.object(matrix, 'MAX_MATRIX', 8), patch.object(matrix, 'git') as calls:
            self.assertEqual(matrix.main([str(path)]), 2)
            calls.assert_not_called()

    def test_changed_excerpt_or_range_refused(self):
        original = copy.deepcopy(self.claim['excerpt'])
        for field, value in [('text', 'Invented result\n'), ('start_line', 1),
                             ('end_line', 99), ('start_line', True), ('sha256', '0' * 64)]:
            with self.subTest(field=field):
                self.claim['excerpt'] = {**original, field: value}
                with self.assertRaises(matrix.MatrixError):
                    self.check()

    def test_dangling_or_duplicate_references_and_unknown_roles_refused(self):
        for evidence in [{'replay': ['missing']}, {'replay': ['source', 'source']},
                         {'proof_of_everything': ['source']}]:
            self.claim['evidence'] = evidence
            with self.assertRaises(matrix.MatrixError):
                self.check()

    def test_duplicate_ids_refused(self):
        self.record['sources'].append(copy.deepcopy(self.source))
        with self.assertRaisesRegex(matrix.MatrixError, 'duplicate source'):
            self.check()
        self.record['sources'].pop()
        self.record['claims'].append(copy.deepcopy(self.claim))
        with self.assertRaisesRegex(matrix.MatrixError, 'duplicate claim'):
            self.check()

    def test_duplicate_json_keys_refused(self):
        path = self.repo / 'bad.json'
        path.write_text('{"schema": 1, "schema": 2}')
        with self.assertRaisesRegex(matrix.MatrixError, 'duplicate JSON key'):
            matrix.load(path)

    def test_cli_receipt_is_write_once(self):
        path, output = self.repo / 'matrix.json', self.repo / 'receipt.json'
        path.write_text(json.dumps(self.record))
        args = [str(path), '--repo', f'fixture={self.repo}', '--output', str(output)]
        self.assertEqual(matrix.main(args), 0)
        before = output.read_bytes()
        self.assertEqual(matrix.main(args), 2)
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual(json.loads(before)['matrix_sha256'], matrix.digest(path.read_bytes()))


if __name__ == '__main__':
    unittest.main()
