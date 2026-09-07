"""Real Lean controls. Run in CI with the pinned toolchain, never a fake runner."""
import json
from pathlib import Path
import shutil

import pytest

from orchestration.formal import FormalProofTask, FormalTaskKind, LeanWorker
from orchestration.formal.cli import main

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which('lake') is None, reason='requires pinned Lean toolchain')


@pytest.fixture()
def workspace(tmp_path):
    shutil.copytree(ROOT / 'formal/smoke', tmp_path / 'formal', ignore=shutil.ignore_patterns('.lake'))
    shutil.copy2(ROOT / 'formal/AxiomAudit.lean', tmp_path / 'formal/AxiomAudit.lean')
    return tmp_path


def task(name='CryptoResearch.Smoke.add_zero'):
    return FormalProofTask(task_id='test-only', kind=FormalTaskKind.FORMALIZE_CLAIM,
        claim_id='smoke-only', claim='Adding zero preserves a natural number.',
        theorem_name=name, theorem_file='CryptoResearch/Smoke.lean')


def test_real_lean_accepts_proof_and_keeps_review_pending(workspace):
    result = LeanWorker(workspace).verify(task())
    assert result.machine_verified, result.build_log + result.audit_log
    assert result.needs_semantic_review
    assert 'CryptoResearch.Smoke.add_zero' in result.audit_log


@pytest.mark.parametrize('name', ['CryptoResearch.Smoke.missing', 'Nat.add'])
def test_real_lean_rejects_absent_theorem_and_definition(workspace, name):
    result = LeanWorker(workspace).verify(task(name))
    assert not result.machine_verified
    assert 'not a theorem' in result.audit_log


def test_real_lean_rejects_false_control(workspace):
    (workspace / 'formal/CryptoResearch/Smoke.lean').write_text(
        'namespace CryptoResearch.Smoke\ntheorem add_zero : False := by trivial\nend CryptoResearch.Smoke\n')
    result = LeanWorker(workspace).verify(task())
    assert not result.machine_verified
    assert not result.build_passed


def test_real_lean_finds_axiom_hidden_from_text_scan(workspace):
    # Escaped identifier evades a naive `sorry` keyword scan; kernel dependency
    # inspection must still reject it even if the supplied project audit is empty.
    (workspace / 'formal/CryptoResearch/Smoke.lean').write_text(
        'namespace CryptoResearch.Smoke\ntheorem add_zero : False := «sorryAx» False true\nend CryptoResearch.Smoke\n')
    (workspace / 'formal/AxiomAudit.lean').write_text('import CryptoResearch\n')
    result = LeanWorker(workspace).verify(task())
    assert not result.machine_verified
    assert result.build_passed, result.build_log
    assert 'target axiom audit failed' in result.audit_log


def test_verify_cli_needs_no_generator_and_preserves_receipt(workspace):
    spec = workspace / 'task.json'
    spec.write_text(json.dumps(dict(schema='crypto.autoresearch.formal_task.v1',
        **task().__dict__, source='formal/CryptoResearch/Smoke.lean')))
    artifact = workspace / 'receipt.json'
    args = ['--repo-root', str(workspace), 'verify', '--task-file', str(spec), '--artifact-out', str(artifact)]
    assert main(args) == 0
    data = json.loads(artifact.read_text())
    assert data['verification']['status'] == 'machine_verified'
    assert data['semantic_review']['status'] == 'pending'
    assert data['provenance']['theorem_sha256']
    before = artifact.read_bytes()
    assert main(args) == 2
    assert artifact.read_bytes() == before
