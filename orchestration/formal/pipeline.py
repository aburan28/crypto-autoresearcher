"""Join the MathCode producer to the Lean verifier for one formal task.

``formalize_and_verify`` is the whole wiring: generate a candidate, and if it is
clean enough to enter the workspace, verify it with the untouched
:class:`~orchestration.formal.lean_worker.LeanWorker`.  The pipeline adds no
authority — it produces a proof artifact and an advisory
:class:`~orchestration.routing.models.VerificationOutcome`, and the canonical
Coordinator decides what, if anything, that is worth.

The one judgement made here is which failures are allowed to reach the
verifier's vocabulary at all.  A missing binary, a timeout, or an engine that
wrote nothing says nothing whatsoever about the claim, so those become
``INFRASTRUCTURE_FAILURE`` with no ``FormalProofResult`` at all rather than a
blocked proof — AGENTS.md rule 3.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from orchestration.routing.models import (
    BaselineComparison,
    ClaimInterpretation,
    VerificationFailureClass,
    VerificationOutcome,
    VerificationVerdict,
)

from .integration import verification_outcome_from_formal_result
from .lean_worker import LeanWorker
from .mathcode import FormalizationAttempt, FormalizationFailure, MathCodeFormalizer
from .models import FormalProofResult, FormalProofTask, FormalStatus

SCHEMA_FORMAL_PROOF_V1 = "crypto.autoresearch.formal_proof.v1"


@dataclass(frozen=True)
class FormalRunRecord:
    """One end-to-end formalize-then-verify run.

    ``result`` is None exactly when the run never reached a mathematical
    outcome, i.e. when the engine itself failed.
    """

    task: FormalProofTask
    attempt: FormalizationAttempt
    result: FormalProofResult | None

    @property
    def infrastructure_failure(self) -> bool:
        return self.result is None

    @property
    def machine_verified(self) -> bool:
        return self.result is not None and self.result.machine_verified

    def verification_outcome(
        self,
        *,
        attempt_id: str,
        task_result_hash: str,
        receipt_valid: bool = True,
        semantic_review_passed: bool | None = None,
    ) -> VerificationOutcome:
        if self.result is not None:
            return verification_outcome_from_formal_result(
                self.result,
                attempt_id=attempt_id,
                task_result_hash=task_result_hash,
                receipt_valid=receipt_valid,
                semantic_review_passed=semantic_review_passed,
            )
        return VerificationOutcome(
            task_id=self.task.task_id,
            attempt_id=attempt_id,
            task_result_hash=task_result_hash,
            verdict=VerificationVerdict.INVALID,
            receipt_valid=receipt_valid,
            # The engine broke; the claim is exactly as open as it was before.
            claim_interpretation=ClaimInterpretation.INCONCLUSIVE,
            baseline_comparison=BaselineComparison.NOT_APPLICABLE,
            failure_class=VerificationFailureClass.INFRASTRUCTURE_FAILURE,
            required_escalation=True,
            successor_constraints=(
                "repair_formalization_engine",
                "retry_formalization_attempt",
            ),
        )

    def as_proof_artifact(
        self,
        proof_id: str,
        *,
        source_commit: str | None = None,
        workspace_root: Path | None = None,
    ) -> dict[str, object]:
        """The inspectable record documented in docs/formal-research-lane.md.

        Hashes that could not be computed are recorded as null.  Nothing here is
        inferred: every field is read back off disk or off the run.
        """

        result = self.result
        return {
            "schema": SCHEMA_FORMAL_PROOF_V1,
            "proof_id": proof_id,
            "claim_id": self.task.claim_id,
            "hypothesis_ids": list(self.task.hypothesis_ids),
            "system": "lean4",
            "task": {
                "task_id": self.task.task_id,
                "kind": self.task.kind.value,
                "claim": self.task.claim,
                "workspace": self.task.workspace,
            },
            "theorem": {
                "file": self.task.theorem_file,
                "name": self.task.theorem_name,
            },
            "formalizer": self.attempt.as_dict(),
            "verification": {
                "status": result.status.value if result else None,
                "build": _passfail(result.build_passed if result else None),
                "axiom_audit": _passfail(result.axiom_audit_passed if result else None),
                "forbidden_constructs": list(result.forbidden_constructs) if result else [],
                "blocking_reason": result.blocking_reason if result else self.attempt.blocking_reason,
                "infrastructure_failure": self.infrastructure_failure,
            },
            "semantic_review": {
                # Compilation is never fidelity.  A machine-verified proof is
                # pending review, never passed review.
                "required": True,
                "status": "pending" if self.machine_verified else "not_applicable",
            },
            "provenance": {
                "source_commit": source_commit,
                "lean_toolchain_sha256": _file_sha256(workspace_root, "lean-toolchain"),
                "lake_manifest_sha256": _file_sha256(workspace_root, "lake-manifest.json"),
            },
        }


def formalize_and_verify(
    task: FormalProofTask,
    *,
    formalizer: MathCodeFormalizer,
    worker: LeanWorker,
) -> FormalRunRecord:
    """Generate a Lean candidate for ``task`` and verify it if it staged."""

    attempt = formalizer.formalize(task)

    if attempt.staged:
        return FormalRunRecord(task=task, attempt=attempt, result=worker.verify(task))

    if attempt.failure is FormalizationFailure.INCOMPLETE_PROOF:
        # The statement may well be right; the proof simply is not finished.
        # That is the input to find_proof_gap, not a verifier malfunction.
        return FormalRunRecord(
            task=task,
            attempt=attempt,
            result=FormalProofResult(
                task_id=task.task_id,
                status=FormalStatus.FORMALIZATION_BLOCKED,
                build_passed=False,
                axiom_audit_passed=False,
                forbidden_constructs=tuple(attempt.forbidden_constructs),
                theorem_file=task.theorem_file,
                theorem_name=task.theorem_name,
                blocking_reason=(
                    f"{attempt.blocking_reason} (candidate held in {attempt.attempt_dir}; "
                    "lake build not run, so the statement is unelaborated)"
                ),
            ),
        )

    if attempt.failure is FormalizationFailure.FORBIDDEN_CONSTRUCT:
        return FormalRunRecord(
            task=task,
            attempt=attempt,
            result=FormalProofResult(
                task_id=task.task_id,
                status=FormalStatus.INVALID,
                build_passed=False,
                axiom_audit_passed=False,
                forbidden_constructs=tuple(attempt.forbidden_constructs),
                theorem_file=task.theorem_file,
                theorem_name=task.theorem_name,
                blocking_reason=attempt.blocking_reason,
            ),
        )

    return FormalRunRecord(task=task, attempt=attempt, result=None)


def _passfail(value: bool | None) -> str | None:
    if value is None:
        return None
    return "PASS" if value else "FAIL"


def _file_sha256(root: Path | None, name: str) -> str | None:
    if root is None:
        return None
    path = root / name
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


__all__ = [
    "SCHEMA_FORMAL_PROOF_V1",
    "FormalRunRecord",
    "formalize_and_verify",
]
