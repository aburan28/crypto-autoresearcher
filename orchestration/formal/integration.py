"""Bridge formal-method outcomes into Research Loop v2 routing contracts.

This module is deliberately pure: it creates advisory route profiles,
verification outcomes, and successor proposals.  It does not admit frontier
nodes, dispatch workers, write the ledger, or grant campaign-transition
authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from orchestration.formal.models import (
    FormalProofResult,
    FormalProofTask,
    FormalStatus,
    FormalTaskKind,
)
from orchestration.routing.models import (
    BaselineComparison,
    ClaimInterpretation,
    RouteFeatures,
    SuccessorContract,
    VerificationFailureClass,
    VerificationOutcome,
    VerificationVerdict,
)


@dataclass(frozen=True)
class FormalSuccessorProposal:
    """One advisory successor candidate derived from a formal result."""

    successor_class: str
    task_kind: FormalTaskKind
    claim_id: str
    rationale: str
    blocking_obligation: str | None = None


_PROFILE = {
    FormalTaskKind.FORMALIZE_CLAIM: dict(
        novelty=0.45,
        mathematical_depth=0.70,
        ambiguity=0.55,
        tool_dominance=0.80,
        output_verifiability=0.95,
    ),
    FormalTaskKind.FIND_PROOF_GAP: dict(
        novelty=0.60,
        mathematical_depth=0.90,
        ambiguity=0.65,
        tool_dominance=0.70,
        output_verifiability=0.95,
    ),
    FormalTaskKind.FORMAL_COUNTEREXAMPLE: dict(
        novelty=0.55,
        mathematical_depth=0.78,
        ambiguity=0.35,
        tool_dominance=0.88,
        output_verifiability=0.98,
    ),
    FormalTaskKind.PROOF_GENERALIZATION: dict(
        novelty=0.78,
        mathematical_depth=0.92,
        ambiguity=0.72,
        tool_dominance=0.62,
        output_verifiability=0.93,
    ),
}


def formal_route_features(
    kind: FormalTaskKind,
    *,
    kb_coverage: float,
    contradiction_score: float = 0.0,
    previous_failed_attempts: int = 0,
) -> RouteFeatures:
    """Create deterministic route features for a formal frontier task."""

    profile = _PROFILE[kind]
    return RouteFeatures(
        task_type=kind.value,
        kb_coverage=kb_coverage,
        contradiction_score=contradiction_score,
        previous_failed_attempts=previous_failed_attempts,
        **profile,
    )


def formal_successor_contract(kind: FormalTaskKind) -> SuccessorContract:
    """Require typed follow-up work after every formal task attempt."""

    required_classes = {
        FormalTaskKind.FORMALIZE_CLAIM: (
            "semantic_fidelity_review",
            "find_proof_gap",
        ),
        FormalTaskKind.FIND_PROOF_GAP: (
            "proof_obligation",
            "formal_counterexample",
            "weaken_or_refine_claim",
        ),
        FormalTaskKind.FORMAL_COUNTEREXAMPLE: (
            "refine_hypothesis",
            "proof_generalization",
        ),
        FormalTaskKind.PROOF_GENERALIZATION: (
            "semantic_fidelity_review",
            "find_proof_gap",
            "boundary_case_search",
        ),
    }[kind]
    return SuccessorContract(
        required=True,
        minimum_distinct_proposals=2,
        required_classes=required_classes,
    )


def verification_outcome_from_formal_result(
    result: FormalProofResult,
    *,
    attempt_id: str,
    task_result_hash: str,
    receipt_valid: bool,
    semantic_review_passed: bool | None = None,
) -> VerificationOutcome:
    """Translate a mechanical Lean result into a non-authoritative verifier record.

    A machine-verified proof remains inconclusive until an independent semantic
    reviewer confirms that the theorem statement faithfully captures the human
    research claim.  A formal refutation is treated as valid contradictory
    evidence, not as a verifier failure.
    """

    constraints: list[str] = []
    failure_class = None
    required_escalation = False

    if not receipt_valid:
        verdict = VerificationVerdict.INVALID
        interpretation = ClaimInterpretation.INCONCLUSIVE
        failure_class = VerificationFailureClass.RECEIPT_INVALID
        required_escalation = True
        constraints.append("repair_or_reproduce_formal_receipt")
    elif result.status is FormalStatus.INVALID:
        verdict = VerificationVerdict.INVALID
        interpretation = ClaimInterpretation.INCONCLUSIVE
        failure_class = VerificationFailureClass.VERIFIER_FAILURE
        required_escalation = True
        constraints.append("repair_formal_verification_failure")
    elif result.status is FormalStatus.FORMALIZATION_BLOCKED:
        verdict = VerificationVerdict.INCONCLUSIVE
        interpretation = ClaimInterpretation.INCONCLUSIVE
        required_escalation = True
        constraints.extend(("extract_blocking_proof_obligation", "propose_typed_successors"))
    elif result.status is FormalStatus.FORMALLY_REFUTED:
        verdict = VerificationVerdict.PASS
        interpretation = ClaimInterpretation.CONTRADICTION_REQUIRES_REVIEW
        required_escalation = True
        constraints.extend(("independent_refutation_review", "refine_or_reject_claim"))
    elif semantic_review_passed is True:
        verdict = VerificationVerdict.PASS
        interpretation = ClaimInterpretation.OBSERVATION_ONLY
        constraints.append("coordinator_may_consider_machine_verified_promotion")
    else:
        verdict = VerificationVerdict.INCONCLUSIVE
        interpretation = ClaimInterpretation.INCONCLUSIVE
        required_escalation = True
        constraints.append("independent_semantic_fidelity_review_required")

    return VerificationOutcome(
        task_id=result.task_id,
        attempt_id=attempt_id,
        task_result_hash=task_result_hash,
        verdict=verdict,
        receipt_valid=receipt_valid,
        claim_interpretation=interpretation,
        baseline_comparison=BaselineComparison.NOT_APPLICABLE,
        failure_class=failure_class,
        required_escalation=required_escalation,
        successor_constraints=tuple(constraints),
    )


def successors_from_formal_result(
    task: FormalProofTask,
    result: FormalProofResult,
) -> tuple[FormalSuccessorProposal, ...]:
    """Generate typed successor candidates from a formal task outcome.

    This is intentionally deterministic.  The campaign controller may score,
    deduplicate, reject, or enrich these proposals, but a blocked proof cannot
    silently terminate a campaign merely because a worker stopped.
    """

    if task.task_id != result.task_id:
        raise ValueError("formal task/result task_id mismatch")

    if result.status is FormalStatus.FORMALIZATION_BLOCKED:
        blocker = result.blocking_reason or "unclassified proof obligation"
        return (
            FormalSuccessorProposal(
                successor_class="proof_obligation",
                task_kind=FormalTaskKind.FIND_PROOF_GAP,
                claim_id=task.claim_id,
                rationale="Isolate the smallest unresolved lemma preventing the formal proof.",
                blocking_obligation=blocker,
            ),
            FormalSuccessorProposal(
                successor_class="formal_counterexample",
                task_kind=FormalTaskKind.FORMAL_COUNTEREXAMPLE,
                claim_id=task.claim_id,
                rationale="Attack the blocking obligation with a machine-checkable counterexample search.",
                blocking_obligation=blocker,
            ),
            FormalSuccessorProposal(
                successor_class="weaken_or_refine_claim",
                task_kind=FormalTaskKind.FORMALIZE_CLAIM,
                claim_id=task.claim_id,
                rationale="Restate the claim with the minimal assumptions exposed by the failed proof.",
                blocking_obligation=blocker,
            ),
        )

    if result.status is FormalStatus.FORMALLY_REFUTED:
        return (
            FormalSuccessorProposal(
                successor_class="refine_hypothesis",
                task_kind=FormalTaskKind.FORMALIZE_CLAIM,
                claim_id=task.claim_id,
                rationale="Replace the refuted statement with the strongest surviving restricted claim.",
            ),
            FormalSuccessorProposal(
                successor_class="proof_generalization",
                task_kind=FormalTaskKind.PROOF_GENERALIZATION,
                claim_id=task.claim_id,
                rationale="Characterize the boundary separating refuted and surviving parameter regimes.",
            ),
        )

    if result.status is FormalStatus.MACHINE_VERIFIED:
        return (
            FormalSuccessorProposal(
                successor_class="semantic_fidelity_review",
                task_kind=FormalTaskKind.FORMALIZE_CLAIM,
                claim_id=task.claim_id,
                rationale="Independently check that the proved Lean proposition matches the intended scientific claim.",
            ),
            FormalSuccessorProposal(
                successor_class="proof_generalization",
                task_kind=FormalTaskKind.PROOF_GENERALIZATION,
                claim_id=task.claim_id,
                rationale="Test whether the verified theorem is structural or specific to its current assumptions.",
            ),
        )

    return (
        FormalSuccessorProposal(
            successor_class="implementation_repair",
            task_kind=task.kind,
            claim_id=task.claim_id,
            rationale="Repair or reproduce the invalid formal verification attempt before drawing research conclusions.",
            blocking_obligation=result.blocking_reason,
        ),
    )


__all__ = [
    "FormalSuccessorProposal",
    "formal_route_features",
    "formal_successor_contract",
    "successors_from_formal_result",
    "verification_outcome_from_formal_result",
]
