"""Real kernel controls for the scoped torsion proof; no inference engine needed."""
from dataclasses import replace
from pathlib import Path
import shutil

import pytest

from orchestration.formal.lean_worker import LeanWorker
from orchestration.formal.models import FormalProofTask, FormalTaskKind

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which('lake') is None, reason='Pinned Lean/lake unavailable')


@pytest.fixture
def proof_workspace(tmp_path):
    repo = tmp_path / 'repo'
    workspace = repo / 'formal'
    shutil.copytree(ROOT / 'formal/scoped-obstructions', workspace,
                    ignore=shutil.ignore_patterns('.lake', 'TargetAudit-*'))
    task = FormalProofTask(task_id='CONTROL-SCOPED-TORSION', claim_id='SCOPED-TORSION',
        kind=FormalTaskKind.FORMALIZE_CLAIM, claim='Odd torsion translation under explicit additive laws.',
        theorem_name='ScopedObstructions.AdditiveModel.odd_translation_outside_kernel',
        theorem_file='ScopedObstructions/Torsion.lean', workspace='formal')
    return repo, workspace, task


def test_real_kernel_accepts_exact_theorem_and_zero_axiom_audit(proof_workspace):
    repo, _, task = proof_workspace
    result = LeanWorker(repo, timeout_seconds=60).verify(task)
    assert result.machine_verified, result.build_log + result.audit_log
    assert result.needs_semantic_review is True
    assert 'zero-axiom audit passed' in result.audit_log
    assert 'target axiom audit passed' in result.audit_log


@pytest.mark.parametrize('name,proposition,proof', [
    ('even_strengthening', 'xorModel.multiple 2 (xorModel.add false true) = true', 'rfl'),
    ('zero_torsion_strengthening',
     'xorModel.multiple 3 (xorModel.add false false) ≠ xorModel.zero', 'decide'),
])
def test_kernel_rejects_false_strengthenings(proof_workspace, name, proposition, proof):
    repo, workspace, task = proof_workspace
    (workspace / 'ScopedObstructions/Negative.lean').write_text(
        'import ScopedObstructions\nnamespace ScopedObstructions.Negative\n'
        f'theorem {name} : {proposition} := by {proof}\n'
        'end ScopedObstructions.Negative\n')
    task = replace(task, theorem_name='ScopedObstructions.Negative.' + name,
                   theorem_file='ScopedObstructions/Negative.lean')
    result = LeanWorker(repo, timeout_seconds=60).verify(task)
    assert result.machine_verified is False
    assert result.build_passed is False
    assert result.blocking_reason == 'lake build failed'


def test_requested_definition_is_not_accepted_as_a_theorem(proof_workspace):
    repo, _, task = proof_workspace
    result = LeanWorker(repo, timeout_seconds=60).verify(
        replace(task, theorem_name='ScopedObstructions.xorModel'))
    assert result.machine_verified is False
    assert result.axiom_audit_passed is False
    assert 'requested declaration is not a theorem' in result.audit_log
