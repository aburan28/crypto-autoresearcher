"""Coverage must not disappear because a citation happens to name an idea."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.idea_experiment_coverage import scan


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write('orchestration/research-priority.yaml', {'ecc_areas': ['ECDLP']})
        self.iid = 'IDEA-20260907-abcdef'
        self.idea = {'id': self.iid, 'question_id': 'RQ-ECDLP-001', 'status': 'proposed'}
        self.write('ledger/proposals/' + self.iid + '.yaml', {'idea': self.idea})

    def write(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value))

    def row(self):
        return next(r for r in scan(self.root)['ideas'] if r['id'] == self.iid)

    def test_prose_citation_does_not_count_as_experiment(self):
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'citations': [{'ref': self.iid}],
            'source_proposal': 'This differs from ' + self.iid}})
        row = self.row()
        self.assertEqual(row['link_status'], 'mention_only')
        self.assertEqual(row['experiments'], [])

    def test_hypothesis_alone_remains_a_gap(self):
        self.write('ledger/hypotheses/H-ECDLP-111111.yaml', {'hypothesis': {
            'id': 'H-ECDLP-111111', 'derived_from_idea': self.iid}})
        self.assertEqual(self.row()['link_status'], 'hypothesis_only')
        self.assertEqual(scan(self.root)['counts']['ecc_without_explicit_experiment'], 1)

    def test_exact_hypothesis_chain_links_but_does_not_prove_completion(self):
        self.write('ledger/hypotheses/H-ECDLP-111111.yaml', {'hypothesis': {
            'id': 'H-ECDLP-111111', 'source_idea_id': self.iid}})
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'hypothesis_id': 'H-ECDLP-111111', 'status': 'draft'}})
        report = scan(self.root)
        self.assertEqual(report['counts']['all_without_explicit_experiment'], 0)
        self.assertFalse(report['completion_proven'])
        self.assertEqual(self.row()['experiments'][0]['source_status'], 'draft')

    def test_multiple_direct_sources_count_once_per_idea(self):
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'proposal_id': self.iid, 'source_idea_ids': [self.iid]}})
        self.assertEqual(len(self.row()['experiments']), 1)
        self.assertEqual(len(self.row()['experiments'][0]['lineage'][0]['fields']), 2)

    def test_all_statuses_and_legacy_layout_remain_visible(self):
        legacy = 'IDEA-20260701-003'
        self.write('ledger/' + legacy + '.yaml', {'idea': {
            'id': legacy, 'question_id': 'RQ-AES-001', 'status': 'rejected'}})
        self.write('ledger/ideas/IDEA-20260907-123456.yaml', {
            'id': 'IDEA-20260907-123456', 'question_id': 'RQ-ECDLP-001'})
        report = scan(self.root)
        self.assertEqual(report['counts']['ideas'], 3)
        self.assertEqual(report['counts']['ecc_ideas'], 2)
        self.assertEqual(report['counts']['all_without_explicit_experiment'], 3)

    def test_classification_partition_requires_explicit_policy_membership(self):
        self.write('orchestration/research-priority.yaml', {
            'ecc_areas': ['ECDLP'], 'excluded_areas': {'AES': 'Explicit non-ECC scope'}})
        unknown = 'IDEA-20260907-111111'
        missing = 'IDEA-20260907-222222'
        excluded = 'IDEA-20260907-333333'
        for iid, fields in (
            (unknown, {'question_id': 'RQ-UNLISTED-001', 'status': 'proposed'}),
            (missing, {'status': 'rejected'}),
            (excluded, {'goal_id': 'GOAL-AES-001'}),
        ):
            self.write('ledger/proposals/' + iid + '.yaml', {'idea': {'id': iid, **fields}})
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'source_idea_id': unknown,
            'status': 'draft', 'approved_by': None}})
        report = scan(self.root)
        rows = {r['id']: r for r in report['ideas']}
        for iid, classification, ecc, unresolved, unknown_areas in (
            (self.iid, 'ecc', True, False, []),
            (unknown, 'unclassified', False, True, ['UNLISTED']),
            (missing, 'unclassified', False, True, []),
            (excluded, 'non_ecc', False, False, []),
        ):
            with self.subTest(iid=iid):
                row = rows[iid]
                self.assertEqual(row['classification'], classification)
                self.assertEqual(row['ecc'], ecc)
                self.assertEqual(row['classification_unresolved'], unresolved)
                self.assertEqual(row['policy_unknown_areas'], unknown_areas)
        self.assertEqual(report['counts']['classification'], {
            'ecc': 1, 'non_ecc': 1, 'unclassified': 2})
        self.assertEqual(report['counts']['classification_unresolved'], 2)
        self.assertEqual(report['counts']['ideas'], 4)
        self.assertEqual(rows[missing]['source_statuses'], ['rejected'])
        self.assertEqual(rows[excluded]['source_statuses'], ['unspecified'])
        self.assertEqual(rows[unknown]['source_statuses'], ['proposed'])
        self.assertEqual(rows[unknown]['link_status'], 'explicit_experiment_link')
        self.assertEqual(rows[unknown]['experiments'][0]['source_status'], 'draft')
        self.assertIsNone(rows[unknown]['experiments'][0]['source_approved_by'])
        self.assertEqual(rows[unknown]['experiments'][0]['semantic_coverage'],
                         'not_adjudicated_by_this_tool')
        self.assertFalse(report['completion_proven'])

    def test_unknown_area_is_not_resolved_by_an_explicitly_excluded_source(self):
        self.write('orchestration/research-priority.yaml', {
            'ecc_areas': ['ECDLP'], 'excluded_areas': {'AES': 'Explicit non-ECC scope'}})
        self.write('ledger/proposals/' + self.iid + '.yaml', {'idea': {
            **self.idea, 'question_id': 'RQ-AES-001'}})
        self.write('coordination/batch/new_ideas.yaml', {'proposals': [{
            **self.idea, 'question_id': 'RQ-UNLISTED-001'}]})
        report = scan(self.root)
        row = report['ideas'][0]
        self.assertEqual(row['areas'], ['AES', 'UNLISTED'])
        self.assertEqual(row['classification'], 'unclassified')
        self.assertFalse(row['ecc'])
        self.assertTrue(row['classification_unresolved'])
        self.assertEqual(row['policy_unknown_areas'], ['UNLISTED'])
        self.assertEqual(len(report['duplicate_records']), 1)
        self.assertEqual(row['link_status'], 'no_experiment_link')

    def test_explicit_ecc_source_keeps_priority_and_unknown_area_visible(self):
        self.write('orchestration/research-priority.yaml', {
            'ecc_areas': ['ECDLP'], 'excluded_areas': {'AES': 'Explicit non-ECC scope'}})
        self.write('coordination/batch/new_ideas.yaml', {'proposals': [{
            **self.idea, 'question_id': 'RQ-UNLISTED-001'}]})
        self.write('ledger/proposals/IDEA-20260907-111111.yaml', {'idea': {
            'id': 'IDEA-20260907-111111', 'question_id': 'RQ-AES-001',
            'recommended_priority': 'high'}})
        report = scan(self.root)
        row = report['ideas'][0]
        self.assertEqual(row['id'], self.iid)
        self.assertEqual(row['classification'], 'ecc')
        self.assertTrue(row['ecc'])
        self.assertFalse(row['classification_unresolved'])
        self.assertEqual(row['policy_unknown_areas'], ['UNLISTED'])
        self.assertEqual(report['counts']['ecc_ideas'], 1)

    def test_duplicate_and_malformed_sources_are_not_silently_lost(self):
        self.write('ledger/ideas/' + self.iid + '.yaml', {'idea': self.idea})
        self.write('ledger/ideas/broken.yaml', ['not', 'a', 'record'])
        report = scan(self.root)
        self.assertEqual(report['counts']['ideas'], 1)
        self.assertEqual(len(report['duplicate_records']), 1)
        self.assertEqual(len(report['errors']), 1)
        self.assertEqual(len(report['ideas'][0]['paths']), 2)

    def test_exact_source_path_and_unknown_id_are_reported(self):
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'source_proposal_path': 'ledger/proposals/' + self.iid + '.yaml',
            'source_idea_ids': ['IDEA-20260907-999999']}})
        report = scan(self.root)
        self.assertEqual(self.row()['link_status'], 'explicit_experiment_link')
        self.assertEqual(report['unknown_source_ids'][0]['id'], 'IDEA-20260907-999999')

    def test_registered_replacement_is_hash_checked_before_linking(self):
        old = 'experiments/EXP-ECDLP-111111/specification.yaml'
        new = 'ledger/corrections/schema-supersessions/test/experiment.yaml'
        self.write(old, {'experiment': {'id': 'EXP-ECDLP-111111'}})
        self.write(new, {'experiment': {'id': 'EXP-ECDLP-111111', 'proposal_id': self.iid}})
        self.write('tools/schema_supersession_registry.yaml', {
            'schema': 'schema-supersession-registry-v1', 'records': [{
                'kind': 'experiment', 'superseded_path': old, 'superseding_path': new,
                'superseded_sha256': hashlib.sha256((self.root / old).read_bytes()).hexdigest(),
                'superseding_sha256': hashlib.sha256((self.root / new).read_bytes()).hexdigest(),
                'defect': 'Test replacement', 'registered': '2026-09-07'}]})
        report = scan(self.root)
        self.assertEqual(report['errors'], [])
        self.assertEqual(self.row()['experiments'][0]['effective_path'], new)
        (self.root / new).write_text('{}')
        report = scan(self.root)
        self.assertEqual(report['ideas'][0]['experiments'], [])
        self.assertIn('hash mismatch', report['errors'][0]['error'])

    def test_unrecognized_experiment_layout_is_an_error(self):
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'unknown': self.iid})
        report = scan(self.root)
        self.assertEqual(len(report['errors']), 1)
        self.assertFalse(report['completion_proven'])

    def test_legacy_markdown_and_unapproved_contract_do_not_fake_completion(self):
        folder = self.root / 'ideas/rejected'
        folder.mkdir(parents=True)
        (self.root / 'ideas/README.md').write_text(
            'research hypotheses for generic\nprime-field ECDLP')
        iid = 'ECDLP-IDEA-436'
        (folder / (iid + '_valuation.md')).write_text(
            '# ' + iid + ' — Valuation\n- State: `rejected`\n')
        self.write('ideas/rejected/contracts/test.yaml', {'experiment': {
            'id': 'EXP-ECDLP-IDEA-436-PREFLIGHT', 'hypothesis_id': iid,
            'status': 'review_required', 'approved_by': None}})
        report = scan(self.root)
        row = next(r for r in report['ideas'] if r['id'] == iid)
        self.assertTrue(row['ecc'])
        self.assertEqual(row['source_statuses'], ['rejected'])
        self.assertEqual(row['experiments'], [])
        self.assertEqual(len(row['legacy_contract_candidates']), 1)
        self.assertEqual(report['counts']['all_without_explicit_experiment'], 2)

    def test_archive_lists_add_sources_without_counting_duplicate_ids_twice(self):
        new = 'IDEA-20260805-0cd03f'
        self.write('coordination/batch/new_ideas.yaml', {'proposals': [
            self.idea, {'id': new, 'goal_id': 'GOAL-ECDLP-001', 'status': 'proposed'}]})
        self.write('experiments/EXP-ECDLP-111111/specification.yaml', {'experiment': {
            'id': 'EXP-ECDLP-111111', 'source_idea_id': new}})
        report = scan(self.root)
        self.assertEqual(report['counts']['ideas'], 2)
        self.assertEqual(report['counts']['ecc_ideas'], 2)
        self.assertEqual(len(report['duplicate_records']), 1)
        self.assertEqual(report['unknown_source_ids'], [])
        row = next(r for r in report['ideas'] if r['id'] == new)
        self.assertEqual(row['source_locations'][0]['location'], 'proposals[1]')

    def test_legacy_id_prefix_alone_does_not_classify_ecc(self):
        folder = self.root / 'ideas'
        folder.mkdir()
        (folder / 'ECDLP-IDEA-436_test.md').write_text('# ECDLP-IDEA-436 Test\n')
        row = next(r for r in scan(self.root)['ideas'] if r['id'] == 'ECDLP-IDEA-436')
        self.assertFalse(row['ecc'])
        self.assertTrue(row['classification_unresolved'])
        self.assertEqual(row['classification'], 'unclassified')
        self.assertEqual(row['policy_unknown_areas'], [])

    def test_archive_malformed_item_is_reported(self):
        self.write('coordination/test.yaml', {'ideas': ['reference only']})
        self.assertIn('no recognized idea id', scan(self.root)['errors'][0]['error'])

    def test_review_quotations_do_not_create_new_ideas(self):
        self.write('coordination/batch/reviews/report.yaml', {'ideas': [
            {'id': 'IDEA-20260907-999999', 'title': 'Quotation under review'}]})
        self.assertEqual(scan(self.root)['counts']['ideas'], 1)


if __name__ == '__main__':
    unittest.main()
