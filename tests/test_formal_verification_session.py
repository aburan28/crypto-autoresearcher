"""A batch may share common checks only while every bound input is unchanged."""
from pathlib import Path
import subprocess

import pytest

from orchestration.formal import FormalProofTask, FormalTaskKind, LeanWorker
from orchestration.formal import lean_worker
from orchestration.formal.lean_worker import verification_session


@pytest.fixture
def batch(tmp_path):
    formal = tmp_path / 'formal'
    formal.mkdir()
    (formal / 'Theorem.lean').write_text('theorem identity (x : Nat) : x = x := rfl\n')
    (formal / 'Helper.lean').write_text('def helper := 1\n')
    (formal / 'AxiomAudit.lean').write_text('#print axioms identity\n')
    (formal / 'lake-manifest.json').write_text('{"packages": []}\n')
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, 'fresh native output\n', '')

    task = FormalProofTask(task_id='session-control', kind=FormalTaskKind.FORMALIZE_CLAIM,
        claim_id='session-control', claim='Reflexivity', theorem_name='identity',
        theorem_file='Theorem.lean')
    return tmp_path, formal, calls, runner, task


def test_batch_reuses_common_checks_but_rechecks_each_target_and_expires(batch):
    root, _, calls, runner, task = batch
    worker = LeanWorker(root, runner=runner)
    with verification_session():
        first = worker.verify(task)
        second = worker.verify(task)
        assert first.machine_verified and second.machine_verified
        assert second.needs_semantic_review
        assert 'Reused fresh workspace build' in second.build_log
        assert 'Reused fresh project axiom audit' in second.audit_log
        assert calls.count(['lake', 'build']) == 1
        assert calls.count(['lake', 'build', '+Theorem']) == 2
        assert calls.count(['lake', 'env', 'lean', 'AxiomAudit.lean']) == 1
        assert sum('TargetAudit-' in c[-1] for c in calls) == 2
    assert worker.verify(task).machine_verified
    assert calls.count(['lake', 'build']) == 2


@pytest.mark.parametrize('changed', ['helper', 'manifest', 'verifier', 'runner', 'timeout'])
def test_changed_input_or_execution_context_requires_fresh_common_checks(batch, monkeypatch, changed):
    root, formal, calls, runner, task = batch
    worker = LeanWorker(root, runner=runner)
    with verification_session():
        assert worker.verify(task).machine_verified
        if changed == 'helper':
            (formal / 'Helper.lean').write_text('def helper := 2\n')
        elif changed == 'manifest':
            (formal / 'lake-manifest.json').write_text('{"packages": [], "version": 1}\n')
        elif changed == 'verifier':
            original = lean_worker.verifier_inputs()
            monkeypatch.setattr(lean_worker, 'verifier_inputs', lambda: {**original, 'new.py': 'new-digest'})
        elif changed == 'runner':
            worker.runner = lambda *args, **kwargs: runner(*args, **kwargs)
        else:
            worker.timeout_seconds += 1
        assert worker.verify(task).machine_verified
        assert calls.count(['lake', 'build']) == 2
        assert calls.count(['lake', 'env', 'lean', 'AxiomAudit.lean']) == 2


def test_failed_project_audit_never_enters_session(batch):
    root, _, calls, original, task = batch

    def failing(command, **kwargs):
        result = original(command, **kwargs)
        if command == ['lake', 'env', 'lean', 'AxiomAudit.lean']:
            return subprocess.CompletedProcess(command, 1, 'audit refused\n', '')
        return result

    with verification_session():
        for _ in range(2):
            assert not LeanWorker(root, runner=failing).verify(task).machine_verified
    assert calls.count(['lake', 'build']) == 2


def test_source_change_during_target_audit_invalidates_common_result(batch):
    root, formal, calls, original, task = batch
    mutate = [True]

    def changing(command, **kwargs):
        result = original(command, **kwargs)
        if 'TargetAudit-' in command[-1] and mutate[0]:
            (formal / 'Helper.lean').write_text('def helper := 2\n')
            mutate[0] = False
        return result

    with verification_session():
        worker = LeanWorker(root, runner=changing)
        result = worker.verify(task)
        assert not result.machine_verified
        assert 'inputs changed' in result.blocking_reason
        assert worker.verify(task).machine_verified
        assert calls.count(['lake', 'build']) == 2
