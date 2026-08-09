"""Tests for formal-task routing and successor generation."""
from __future__ import annotations

import pytest

pytest.importorskip("pydantic", reason="Research Loop routing contracts require optional pydantic")

from orchestration.formal.integration import (
    formal_route_features,
    formal_successor_contract,
    successors_from_formal_result,
    verification_outcome_from_formal_result,
)
from orchestration.formal.models import (
    FormalProofResult,
    FormalProofTask,
    FormalStatus,
    FormalTaskKind,
)
from orchestration.routing.models import (
    ClaimInterpretation,
    VerificationFailureClass,
    VerificationVerdict,
)

HASH = "sha256:" + "a" * 64


def _task(kind: FormalTaskKind = FormalTaskKind.FIND_PROOF_GAP) -> FormalProofTask:
    return FormalProofTask(
        task_id="TASK-FORMAL-001",
        kind=kind,
        claim_id="CL-ECDLP-001",
        claim="A claimed generic-prime-field structural lemma.",
        theorem_name="CryptoResearch.ECDLP.claim",
        theorem_file="CryptoResearch/ECDLP/Claim.lean",
    )


def _result(
    status: FormalStatus,
    *,
    blocking_reason: str | None = None,
) -> FormalProofResult:
    passed = status is FormalStatus.MACHINE_VERIFIED
    return FormalProofResult(
        task_id="TASK-FORMAL-001",
        status=status,
        build_passed=passed,
        axiom_audit_passed=passed,
        forbidden_constructs=(),
        theorem_file="CryptoResearch/ECDLP/Claim.lean",
        theorem_name="CryptoResearch.ECDLP.claim",
        blocking_reason=blocking_reason,
    )


def test_formal_route_features_make_proof_work_highly_verifiable():
    features = formal_route_features(
        FormalTaskKind.FIND_PROOF_GAP,
        kb_coverage=0.81,
        contradiction_score=0.12,
        previous_failed_attempts=1,
    )

    assert features.task_type == "find_proof_gap"
    assert features.mathematical_depth >= 0.9
    assert features.output_verifiability >= 0.9
    assert features.kb_coverage == 0.81
    assert features.previous_failed_attempts == 1


def test_formal_tasks_require_typed_successors():
    contract = formal_successor_contract(FormalTaskKind.FIND_PROOF_GAP)

    assert contract.required is True
    assert contract.minimum_distinct_proposals >= 2
    assert "proof_obligation" in contract.required_classes
    assert "formal_counterexample" in contract.required_classes
    assert contract.campaign_terminal_authority is False


def test_machine_verified_result_still_requires_semantic_review():
    outcome = verification_outcome_from_formal_result(
        _result(FormalStatus.MACHINE_VERIFIED),
        attempt_id="ATTEMPT-001",
        task_result_hash=HASH,
        receipt_valid=True,
        semantic_review_passed=None,
    )

    assert outcome.verdict is VerificationVerdict.INCONCLUSIVE
    assert outcome.claim_interpretation is ClaimInterpretation.INCONCLUSIVE
    assert outcome.required_escalation is True
    assert "independent_semantic_fidelity_review_required" in outcome.successor_constraints
    assert outcome.campaign_terminal is False


def test_machine_verified_plus_semantic_review_can_pass_without_granting_authority():
    outcome = verification_outcome_from_formal_result(
        _result(FormalStatus.MACHINE_VERIFIED),
        attempt_id="ATTEMPT-001",
        task_result_hash=HASH,
        receipt_valid=True,
        semantic_review_passed=True,
    )

    assert outcome.verdict is VerificationVerdict.PASS
    assert outcome.claim_interpretation is ClaimInterpretation.OBSERVATION_ONLY
    assert outcome.required_escalation is False
    assert outcome.can_change_campaign is False


def test_blocked_proof_generates_gap_counterexample_and_refinement_successors():
    result = _result(
        FormalStatus.FORMALIZATION_BLOCKED,
        blocking_reason="Need independence of decomposition coordinates.",
    )
    successors = successors_from_formal_result(_task(), result)

    assert [proposal.successor_class for proposal in successors] == [
        "proof_obligation",
        "formal_counterexample",
        "weaken_or_refine_claim",
    ]
    assert all(
        proposal.blocking_obligation == "Need independence of decomposition coordinates."
        for proposal in successors
    )


def test_formal_refutation_is_valid_contradictory_evidence():
    outcome = verification_outcome_from_formal_result(
        _result(FormalStatus.FORMALLY_REFUTED),
        attempt_id="ATTEMPT-002",
        task_result_hash=HASH,
        receipt_valid=True,
    )

    assert outcome.verdict is VerificationVerdict.PASS
    assert outcome.claim_interpretation is ClaimInterpretation.CONTRADICTION_REQUIRES_REVIEW
    assert outcome.required_escalation is True
    assert outcome.failure_class is None


def test_invalid_formal_result_is_verifier_failure():
    outcome = verification_outcome_from_formal_result(
        _result(FormalStatus.INVALID, blocking_reason="Lean executable missing"),
        attempt_id="ATTEMPT-003",
        task_result_hash=HASH,
        receipt_valid=True,
    )

    assert outcome.verdict is VerificationVerdict.INVALID
    assert outcome.failure_class is VerificationFailureClass.VERIFIER_FAILURE
    assert outcome.required_escalation is True


def test_task_result_mismatch_cannot_generate_successors():
    task = _task()
    result = FormalProofResult(
        task_id="TASK-OTHER",
        status=FormalStatus.FORMALIZATION_BLOCKED,
        build_passed=False,
        axiom_audit_passed=False,
        forbidden_constructs=(),
        theorem_file="CryptoResearch/ECDLP/Claim.lean",
        theorem_name="CryptoResearch.ECDLP.claim",
        blocking_reason="missing lemma",
    )

    with pytest.raises(ValueError, match="task_id mismatch"):
        successors_from_formal_result(task, result)
