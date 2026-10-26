"""Prospective queues retain and actually verify completed archive custody."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location('planted_preapproval_fixtures', ROOT/'tests/test_experiment_preapproval.py')
fixtures = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(fixtures)


def with_completed_archive(root):
    packet, files = fixtures.fixture(root)
    queue = json.loads(files['queue'].read_text())
    producer_id, archive_id = 'TASK-20261017-c0ffee', 'TASK-20261017-decafe'
    source_path, receipt_path = 'history/source.txt', 'history/receipt.json'
    (root/'history').mkdir()
    (root/source_path).write_text('Deliberately planted historical source.\n')
    fixtures._write(root/receipt_path, {'planted': True})
    fixtures._git(root, 'add', 'history')
    fixtures._git(root, 'commit', '-qm', archive_id)
    commit = fixtures._git(root, 'rev-parse', 'HEAD')
    parent = fixtures._git(root, 'rev-parse', 'HEAD^')
    handoff = dict(id=producer_id, role='coordinator', objective='planted history source',
                   uncertainty_reduced='custody', inputs=['driver.py'], constraints=['exact bytes'],
                   deliverables=[source_path], completion_gate=['source retained'],
                   budget={'maximum_runs': 0}, archived_by=archive_id)
    source = dict(id=producer_id, title='planted completed source', role='coordinator', state='completed',
                  priority=10, review_required=False, depends_on=[], read_scope=['driver.py'],
                  write_scope=[source_path], artifact_paths=[source_path], archived_by=archive_id, handoff=handoff)
    archive = deepcopy(queue['tasks'][1])
    archive.update(id=archive_id, title='planted completed archive', state='completed', depends_on=[producer_id],
                   read_scope=[source_path], write_scope=[receipt_path], artifact_paths=[receipt_path], archived_by=archive_id)
    archive['handoff'].update(id=archive_id, inputs=[source_path], deliverables=[receipt_path])
    archive['archive'].update(source_task_ids=[producer_id], binding_mode='content_at_commit', commit_sha=commit,
                              parent_sha=parent, record_ids=[], path_sha256={name: fixtures._sha((root/name).read_bytes())
                                                                           for name in [source_path, receipt_path]})
    queue['tasks'].extend([source, archive])
    fixtures._write(files['queue'], queue)
    return packet, files, queue


class Tests(unittest.TestCase):
    def test_completed_archive_is_verified_without_dropping_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, files, queue = with_completed_archive(root)
            result = fixtures.probe.assess(root, packet)
            self.assertTrue(result['approvable'], result['blockers'])
            self.assertEqual(len(json.loads(files['queue'].read_text())['tasks']), 4)

    def test_corrupt_completed_archive_digest_blocks_preapproval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, files, queue = with_completed_archive(root)
            queue['tasks'][-1]['archive']['path_sha256']['history/source.txt'] = '0'*64
            fixtures._write(files['queue'], queue)
            result = fixtures.probe.assess(root, packet)
            self.assertFalse(result['approvable'])
            self.assertTrue(any('prospective queue' in reason and 'mismatch' in reason.lower()
                                for reason in result['blockers']), result['blockers'])


if __name__ == '__main__':
    unittest.main()
