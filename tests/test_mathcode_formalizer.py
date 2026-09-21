"""The MathCode producer half of the formal lane, driven by a fake engine.

No test here installs, downloads, or runs MathCode.  The engine is injected as
a callable that writes the Lean a real run would have written, which is what
makes the failure modes worth asserting: the interesting ones are the ones a
live engine produces rarely and at the worst moment.
"""
from pathlib import Path
import subprocess

import pytest

from orchestration.formal import (
    FormalProofTask,
    FormalStatus,
    FormalTaskKind,
    FormalizationFailure,
    LeanWorker,
    MathCodeConfig,
    MathCodeFormalizer,
)
from orchestration.formal.pipeline import formalize_and_verify

PROVED = "import Mathlib\n\ntheorem evenSquare (n : Nat) : 2 ∣ n → 2 ∣ n * n := by\n  omega\n"
UNFINISHED = "import Mathlib\n\ntheorem evenSquare (n : Nat) : 2 ∣ n → 2 ∣ n * n := by\n  sorry\n"
SMUGGLED = "import Mathlib\n\naxiom cheat : False\n\ntheorem evenSquare : True := trivial\n"


def make_task(**overrides) -> FormalProofTask:
    fields = dict(
        task_id="TASK-FORMAL-MC1",
        kind=FormalTaskKind.FORMALIZE_CLAIM,
        claim_id="CL-MC-1",
        claim="The square of an even natural number is even.",
        theorem_name="evenSquare",
        theorem_file="Theorem.lean",
    )
    fields.update(overrides)
    return FormalProofTask(**fields)


def make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "formal"
    workspace.mkdir()
    (workspace / "AxiomAudit.lean").write_text("#print axioms evenSquare\n")
    return workspace


def engine(source: str | None, *, returncode: int = 0, version: str = "mathcode 0.1.0"):
    """A fake `mathcode` that writes ``source`` where the real one writes."""

    calls: list[list[str]] = []

    def runner(command, **kwargs):
        calls.append(list(command))
        if command[1:] == ["--version"]:
            return subprocess.CompletedProcess(command, 0, stdout=version + "\n", stderr="")
        if source is not None:
            out = Path(kwargs["cwd"]) / "LeanFormalizations"
            out.mkdir(parents=True, exist_ok=True)
            (out / "Result.lean").write_text(source, encoding="utf-8")
        return subprocess.CompletedProcess(command, returncode, stdout="done\n", stderr="")

    runner.calls = calls  # type: ignore[attr-defined]
    return runner


def formalizer(tmp_path: Path, runner, *, binary: str | None = "/usr/local/bin/mathcode"):
    return MathCodeFormalizer(
        tmp_path,
        config=MathCodeConfig(attempt_root=str(tmp_path / ".formal-attempts")),
        runner=runner,
        which=lambda _name: binary,
    )


def lean(returncode: int = 0):
    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, returncode, stdout="ok\n", stderr="")

    return runner


# -- producing and staging ------------------------------------------------


def test_clean_candidate_is_staged_into_the_workspace(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    runner = engine(PROVED)

    attempt = formalizer(tmp_path, runner).formalize(make_task())

    assert attempt.staged
    assert attempt.failure is None
    assert (workspace / "Theorem.lean").read_text() == PROVED
    assert attempt.engine_version == "mathcode 0.1.0"
    assert attempt.source_sha256 and attempt.prompt_sha256
    # The engine ran non-interactively, with a prompt, inside its attempt dir.
    invocation = runner.calls[-1]
    assert invocation[0] == "/usr/local/bin/mathcode"
    assert "-p" in invocation


def test_engine_runs_outside_the_lean_workspace(tmp_path: Path) -> None:
    """A scratch file left by the agent must not be scanned as workspace source."""

    workspace = make_workspace(tmp_path)
    runner = engine(PROVED)
    task = make_task()

    attempt = formalizer(tmp_path, runner).formalize(task)

    attempt_dir = Path(attempt.attempt_dir).resolve()
    assert workspace.resolve() not in attempt_dir.parents
    assert attempt_dir != workspace.resolve()


def test_repeated_attempts_never_overwrite_the_previous_one(tmp_path: Path) -> None:
    make_workspace(tmp_path)
    engine_runner = engine(PROVED)
    subject = formalizer(tmp_path, engine_runner)

    first = subject.formalize(make_task())
    second = subject.formalize(make_task())

    assert first.attempt_dir != second.attempt_dir
    assert Path(first.attempt_dir, "prompt.txt").is_file()


# -- candidates that must not reach the workspace -------------------------


def test_unfinished_proof_is_held_back_and_reported_as_an_obligation(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)

    attempt = formalizer(tmp_path, engine(UNFINISHED)).formalize(make_task())

    assert not attempt.staged
    assert attempt.failure is FormalizationFailure.INCOMPLETE_PROOF
    assert not attempt.failure.is_infrastructure
    assert attempt.unproved_sites == ("sorry:4",)
    # Held back precisely so it cannot poison the workspace-wide scan.
    assert not (workspace / "Theorem.lean").exists()
    # ...but preserved, because it is the record of what was tried.
    assert Path(attempt.attempt_dir, attempt.source_path).read_text() == UNFINISHED


def test_smuggled_axiom_is_a_contract_violation_not_an_obligation(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    attempt = formalizer(tmp_path, engine(SMUGGLED)).formalize(make_task())

    assert attempt.failure is FormalizationFailure.FORBIDDEN_CONSTRUCT
    assert "custom_axiom" in attempt.forbidden_constructs


def test_engine_answering_a_different_question_is_rejected(tmp_path: Path) -> None:
    make_workspace(tmp_path)
    other = "import Mathlib\n\ntheorem somethingElse : True := trivial\n"

    attempt = formalizer(tmp_path, engine(other)).formalize(make_task())

    assert attempt.failure is FormalizationFailure.THEOREM_NAME_MISSING
    assert attempt.failure.is_infrastructure


# -- infrastructure failures are never evidence ---------------------------


def test_missing_engine_reports_unavailable_without_inventing_lean(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    attempt = formalizer(tmp_path, engine(PROVED), binary=None).formalize(make_task())

    assert attempt.failure is FormalizationFailure.ENGINE_UNAVAILABLE
    assert attempt.failure.is_infrastructure
    assert attempt.source_sha256 is None
    assert not (tmp_path / "formal" / "Theorem.lean").exists()


def test_engine_timeout_is_infrastructure_not_a_blocked_proof(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    def timing_out(command, **kwargs):
        if command[1:] == ["--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="v\n", stderr="")
        raise subprocess.TimeoutExpired(command, 1)

    record = formalize_and_verify(
        make_task(),
        formalizer=formalizer(tmp_path, timing_out),
        worker=LeanWorker(tmp_path, runner=lean()),
    )

    assert record.attempt.failure is FormalizationFailure.TIMEOUT
    assert record.infrastructure_failure
    assert record.result is None


def test_engine_writing_nothing_is_not_a_statement_about_the_claim(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    attempt = formalizer(tmp_path, engine(None)).formalize(make_task())

    assert attempt.failure is FormalizationFailure.NO_OUTPUT
    assert attempt.failure.is_infrastructure


# -- the joined pipeline --------------------------------------------------


def test_verified_proof_still_requires_semantic_review(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    record = formalize_and_verify(
        make_task(),
        formalizer=formalizer(tmp_path, engine(PROVED)),
        worker=LeanWorker(tmp_path, runner=lean()),
    )

    assert record.machine_verified
    assert record.result.needs_semantic_review
    artifact = record.as_proof_artifact("FP-MC-1", workspace_root=tmp_path / "formal")
    assert artifact["semantic_review"] == {"required": True, "status": "pending"}
    assert artifact["verification"]["build"] == "PASS"
    assert artifact["formalizer"]["source_sha256"] == record.attempt.source_sha256
    # Nothing is invented: absent files hash to null, not to a placeholder.
    assert artifact["provenance"]["lean_toolchain_sha256"] is None


def test_failed_lake_build_blocks_rather_than_refutes(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    record = formalize_and_verify(
        make_task(),
        formalizer=formalizer(tmp_path, engine(PROVED)),
        worker=LeanWorker(tmp_path, runner=lean(returncode=1)),
    )

    assert record.result.status is FormalStatus.FORMALIZATION_BLOCKED
    assert not record.infrastructure_failure


def test_unfinished_proof_becomes_a_blocked_result_not_an_invalid_one(tmp_path: Path) -> None:
    make_workspace(tmp_path)

    record = formalize_and_verify(
        make_task(kind=FormalTaskKind.FIND_PROOF_GAP),
        formalizer=formalizer(tmp_path, engine(UNFINISHED)),
        worker=LeanWorker(tmp_path, runner=lean()),
    )

    assert record.result.status is FormalStatus.FORMALIZATION_BLOCKED
    assert "sorry:4" in record.result.blocking_reason
    assert "lake build not run" in record.result.blocking_reason


def test_infrastructure_failure_carries_the_infrastructure_failure_class(tmp_path: Path) -> None:
    pytest.importorskip("pydantic")
    from orchestration.routing.models import VerificationFailureClass

    make_workspace(tmp_path)
    record = formalize_and_verify(
        make_task(),
        formalizer=formalizer(tmp_path, engine(PROVED), binary=None),
        worker=LeanWorker(tmp_path, runner=lean()),
    )

    outcome = record.verification_outcome(
        attempt_id="A-1", task_result_hash="sha256:" + "0" * 64
    )

    assert outcome.failure_class is VerificationFailureClass.INFRASTRUCTURE_FAILURE
    assert outcome.required_escalation


# -- prompt contract ------------------------------------------------------


def test_prompt_pins_the_theorem_name_and_forbids_hidden_assumptions(tmp_path: Path) -> None:
    task = make_task(theorem_name="CryptoResearch.ECDLP.bound")
    prompt = formalizer(tmp_path, engine(PROVED)).build_prompt(task)

    assert "CryptoResearch.ECDLP.bound" in prompt
    assert "`bound`" in prompt
    assert "axiom" in prompt and "unsafe" in prompt
    assert task.claim in prompt


def test_each_task_kind_asks_for_something_different(tmp_path: Path) -> None:
    subject = formalizer(tmp_path, engine(PROVED))
    prompts = {kind: subject.build_prompt(make_task(kind=kind)) for kind in FormalTaskKind}

    assert len(set(prompts.values())) == len(FormalTaskKind)
    assert "REFUTE" in prompts[FormalTaskKind.FORMAL_COUNTEREXAMPLE]


def test_relative_escape_is_refused_when_the_task_is_built(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        make_task(theorem_file="nested/../../escape.lean")


def test_symlinked_subdirectory_cannot_land_a_file_outside_the_workspace(tmp_path: Path) -> None:
    """The task-level check is textual; this one survives resolution."""

    workspace = make_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace / "link").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError):
        formalizer(tmp_path, engine(PROVED)).formalize(
            make_task(theorem_file="link/Escape.lean")
        )
    assert not (outside / "Escape.lean").exists()


# -- the generated root module -------------------------------------------


def test_staging_regenerates_the_root_so_lake_actually_builds_the_file(tmp_path: Path) -> None:
    """A staged file nothing imports would compile-pass without being compiled."""

    workspace = make_workspace(tmp_path)
    (workspace / "CryptoResearch").mkdir()
    (workspace / "CryptoResearch.lean").write_text("-- stale\n")

    formalize_and_verify(
        make_task(theorem_file="CryptoResearch/Demo/EvenSquare.lean"),
        formalizer=formalizer(tmp_path, engine(PROVED)),
        worker=LeanWorker(tmp_path, runner=lean()),
    )

    root = (workspace / "CryptoResearch.lean").read_text()
    assert "import CryptoResearch.Demo.EvenSquare" in root
    assert "stale" not in root


def test_root_is_not_invented_for_a_workspace_that_has_no_library(tmp_path: Path) -> None:
    from orchestration.formal.workspace import rebuild_root

    workspace = make_workspace(tmp_path)

    assert rebuild_root(workspace) is None
    assert not (workspace / "CryptoResearch.lean").exists()
