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
    assert calls == [["lake", "build"], ["lake", "env", "lean", "AxiomAudit.lean"]]


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
