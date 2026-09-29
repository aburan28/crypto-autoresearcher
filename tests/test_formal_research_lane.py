from pathlib import Path
import subprocess

import pytest

from orchestration.formal import FormalProofTask, FormalStatus, FormalTaskKind, LeanWorker


def test_task_rejects_workspace_escape() -> None:
    with pytest.raises(ValueError):
        FormalProofTask(
            task_id="TASK-FORMAL-1",
            kind=FormalTaskKind.FORMALIZE_CLAIM,
            claim_id="CL-1",
            claim="x = x",
            theorem_name="Example.identity",
            theorem_file="../escape.lean",
        )


def test_worker_marks_clean_build_and_audit_machine_verified(tmp_path: Path) -> None:
    formal = tmp_path / "formal"
    formal.mkdir()
    (formal / "Theorem.lean").write_text("theorem identity (x : Nat) : x = x := rfl\n")
    (formal / "AxiomAudit.lean").write_text("#print axioms identity\n")

    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    task = FormalProofTask(
        task_id="TASK-FORMAL-2",
        kind=FormalTaskKind.FORMALIZE_CLAIM,
        claim_id="CL-2",
        claim="Natural-number equality is reflexive.",
        theorem_name="identity",
        theorem_file="Theorem.lean",
    )
    result = LeanWorker(tmp_path, runner=runner).verify(task)

    assert result.status is FormalStatus.MACHINE_VERIFIED
    assert result.machine_verified
    assert result.needs_semantic_review
    assert calls[:3] == [["lake", "build"], ["lake", "build", "+Theorem"],
                         ["lake", "env", "lean", "AxiomAudit.lean"]]
    assert calls[3][:3] == ["lake", "env", "lean"]
    assert not Path(calls[3][3]).exists()  # temporary target audit is cleaned up


def test_worker_rejects_sorry_even_if_lean_builds(tmp_path: Path) -> None:
    formal = tmp_path / "formal"
    formal.mkdir()
    (formal / "Theorem.lean").write_text("theorem bogus : False := by sorry\n")
    (formal / "AxiomAudit.lean").write_text("#print axioms bogus\n")

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    task = FormalProofTask(
        task_id="TASK-FORMAL-3",
        kind=FormalTaskKind.FIND_PROOF_GAP,
        claim_id="CL-3",
        claim="False.",
        theorem_name="bogus",
        theorem_file="Theorem.lean",
    )
    result = LeanWorker(tmp_path, runner=runner).verify(task)

    assert result.status is FormalStatus.INVALID
    assert not result.machine_verified
    assert any(item.startswith("sorry:") for item in result.forbidden_constructs)


def test_scanner_ignores_nested_comments_strings_and_dependency_caches(tmp_path):
    from orchestration.formal.lean_worker import scan_forbidden_text, forbidden_sites
    source = '/- sorry /- unsafe -/ admit -/\ndef label := "sorry and axiom"\n-- sorry\ntheorem x : True := by\n  sorry\n'
    assert scan_forbidden_text(source) == ('sorry',)
    assert forbidden_sites(source) == (('sorry', 5),)
    (tmp_path / '.lake' / 'packages').mkdir(parents=True)
    (tmp_path / '.lake' / 'packages' / 'Dependency.lean').write_text('unsafe def x := 1\n')
    (tmp_path / 'Proof.lean').write_text('theorem identity (x : Nat) : x = x := rfl\n')
    assert LeanWorker._scan_forbidden(tmp_path) == ()


def test_requested_theorem_audit_failure_cannot_pass(tmp_path):
    formal = tmp_path / 'formal'
    formal.mkdir()
    (formal / 'Theorem.lean').write_text('theorem other : True := True.intro\n')
    (formal / 'AxiomAudit.lean').write_text('-- a project audit may cover no target\n')
    def runner(command, **kwargs):
        is_target = 'TargetAudit-' in command[-1]
        if is_target:
            assert 'let target := `missing' in Path(command[-1]).read_text()
        return subprocess.CompletedProcess(command, 1 if is_target else 0, 'missing theorem' if is_target else '', '')
    task = FormalProofTask(task_id='test', kind=FormalTaskKind.FORMALIZE_CLAIM,
                          claim_id='test', claim='True', theorem_name='missing', theorem_file='Theorem.lean')
    result = LeanWorker(tmp_path, runner=runner).verify(task)
    assert not result.machine_verified
    assert 'missing theorem' in result.audit_log


@pytest.mark.parametrize('toolchain,packages', [
    ('leanprover/lean4:stable', []),
    ('leanprover/lean4:v4.22.0', [{'type': 'git', 'rev': 'master'}]),
    ('leanprover/lean4:v4.22.0', [{'type': 'path', 'dir': '../mutable'}]),
])
def test_direct_verification_refuses_moving_pins(tmp_path, toolchain, packages):
    import json
    from orchestration.formal.cli import _check_verification_pins
    (tmp_path / 'lean-toolchain').write_text(toolchain)
    (tmp_path / 'lake-manifest.json').write_text(json.dumps({'packages': packages}))
    with pytest.raises(ValueError):
        _check_verification_pins(tmp_path)
