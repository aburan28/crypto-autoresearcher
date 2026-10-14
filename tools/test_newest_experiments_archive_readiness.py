"""Selector readiness retains real Git custody checks for completed snapshots.

Only temporary Git fixture commits are created; no experiment program executes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import newest_experiments as newest
from test_research_dispatch import archive_task, queue, task

EXP = 'EXP-TEST-aaaaaa'
SPEC = f'experiments/{EXP}/specification.yaml'
PLAN = f'experiments/{EXP}/trial-plan.json'
QUEUE = 'coordination/fixture-queue.json'


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ['git', '-C', str(root), '-c', 'user.name=Fixture',
         '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
         '-c', 'core.hooksPath=/dev/null', *args],
        check=True, text=True, capture_output=True,
    ).stdout.strip()


def _write(root: Path, path: str, value) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value) + '\n')


def _fixture(root: Path) -> dict:
    _git(root, 'init', '-q')
    (root / 'README.md').write_text('temporary fixture\n')
    _git(root, 'add', 'README.md')
    _git(root, 'commit', '-qm', 'fixture parent')
    parent = _git(root, 'rev-parse', 'HEAD')
    producer = task('PRODUCER', 1, state='completed')
    initial = archive_task('INPUT-ARCHIVE', [producer], state='completed', record_ids=['REC-INPUT'])
    initial['archive']['binding_mode'] = 'content_at_commit'
    paths = producer['artifact_paths'] + initial['artifact_paths']
    for path in paths:
        _write(root, path, {'fixture_payload': path})
    _git(root, 'add', *paths)
    _git(root, 'commit', '-qm', 'INPUT-ARCHIVE REC-INPUT fixture snapshot')
    initial['archive'].update({
        'commit_sha': _git(root, 'rev-parse', 'HEAD'), 'parent_sha': parent,
        'path_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths},
    })
    worker = task('EXECUTOR', 1, depends_on=[initial['id']])
    output = archive_task('RUN-ARCHIVE', [worker])
    _write(root, 'driver.py', {'fixture': 'this file is never executed'})
    _write(root, SPEC, {'experiment': {
        'id': EXP, 'status': 'approved', 'approved_by': 'coordinator', 'frozen': True,
    }})
    plan = {
        'schema': 'crypto.autoresearch.trial_plan.v1', 'experiment_id': EXP,
        'task_id': worker['id'], 'approved_by': 'coordinator', 'frozen': True,
        'specification': SPEC, 'specification_sha256': hashlib.sha256((root / SPEC).read_bytes()).hexdigest(),
        'queue': QUEUE, 'source_sha256': {'driver.py': hashlib.sha256((root / 'driver.py').read_bytes()).hexdigest()},
        'trials': [{'id': 'fixture-trial', 'run_id': 'RUN-TEST-aaaaaa',
                    'argv': ['python3', 'driver.py'], 'check_argv': ['python3', 'driver.py'],
                    'artifacts': ['manifest.yaml', 'raw-result.json'], 'memory_mb': 64}],
    }
    _write(root, PLAN, plan)
    worker['handoff']['execution'] = {
        'mode': 'experiments', 'kind': 'run', 'experiment_id': EXP,
        'trial_plan': PLAN, 'trial_plan_sha256': hashlib.sha256((root / PLAN).read_bytes()).hexdigest(),
        'approved_by': 'coordinator',
    }
    data = queue(producer, initial, worker, output, maximum=1)
    _write(root, QUEUE, data)
    return data


class ArchiveReadinessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_completed_snapshot_is_ready_only_after_real_git_verification(self):
        tmp_path = self.root
        _fixture(tmp_path)
        progress = newest.execution_progress(tmp_path / f'experiments/{EXP}', tmp_path)
        assert progress['execution_state'] == 'ready'
        assert progress['coverage']['planned'] == 1


    def test_archived_hash_mismatch_remains_not_ready(self):
        tmp_path = self.root
        data = _fixture(tmp_path)
        archive = data['tasks'][1]
        path = archive['artifact_paths'][0]
        archive['archive']['path_sha256'][path] = '0' * 64
        _write(tmp_path, QUEUE, data)
        progress = newest.execution_progress(tmp_path / f'experiments/{EXP}', tmp_path)
        assert progress['execution_state'] == 'needs_dispatch_queue'
        assert 'sha256' in progress['reason'].lower() or 'hash' in progress['reason'].lower()


    def test_unresolvable_snapshot_remains_not_ready(self):
        tmp_path = self.root
        data = _fixture(tmp_path)
        data['tasks'][1]['archive']['commit_sha'] = '0' * 40
        _write(tmp_path, QUEUE, data)
        progress = newest.execution_progress(tmp_path / f'experiments/{EXP}', tmp_path)
        assert progress['execution_state'] == 'needs_dispatch_queue'
        assert 'resolve' in progress['reason']


    def test_wrong_first_parent_remains_not_ready(self):
        tmp_path = self.root
        data = _fixture(tmp_path)
        archive = data['tasks'][1]['archive']
        archive['parent_sha'] = archive['commit_sha']
        _write(tmp_path, QUEUE, data)
        progress = newest.execution_progress(tmp_path / f'experiments/{EXP}', tmp_path)
        assert progress['execution_state'] == 'needs_dispatch_queue'
        assert 'first parent' in progress['reason']

if __name__ == "__main__":
    unittest.main()
