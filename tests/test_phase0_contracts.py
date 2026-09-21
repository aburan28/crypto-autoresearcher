"""Phase-0 contract tests for the shadow-first Research Loop v2 boundary."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

# These contracts are optional at the package boundary.  Skipping this focused
# suite makes a minimal ledger-only environment explicit without breaking
# unrelated root tests that never import the Phase-0 models.
pytest.importorskip("pydantic", reason="Phase-0 contracts require optional pydantic")
from pydantic import ValidationError

from orchestration.knowledge.models import (
    Citation,
    EvidenceBundle,
    EvidenceCoverage,
    EvidencePassage,
    EvidenceProvenance,
    EvidenceStatement,
    IndexFreshness,
    RetrievalAdapter,
    SourceClass,
)
from orchestration.routing.models import (
    AgentRole,
    ArtifactReference,
    AttemptStopReason,
    AttemptTerminalStatus,
    BaselineComparison,
    ClaimInterpretation,
    EscalationPolicy,
    HardPolicyFloor,
    HandoffReference,
    KnowledgeContract,
    RouteCandidate,
    RouteDecision,
    RouteFeatures,
    RouteMode,
    RouteSelectionStatus,
    RoutingContract,
    SuccessorContract,
    TaskEnvelope,
    TaskResult,
    VerificationOutcome,
    VerificationVerdict,
)


REPO = Path(__file__).resolve().parents[1]
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
COMMIT = "1" * 40
RETRIEVED_AT = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)


def _bundle(*, stale: bool = False) -> EvidenceBundle:
    citation = Citation(
        id="CIT-001",
        source_id="SRC-001",
        source_type=SourceClass.LEDGER,
        locator="ledger/decision.yaml:12",
        source_commit=COMMIT,
    )
    passage = EvidencePassage(
        id="PASSAGE-001",
        source_id="SRC-001",
        text="The frozen control established the baseline.",
        citation_ids=(citation.id,),
    )
    freshness = IndexFreshness(
        index_at_or_after_source_commit=not stale,
        direct_record_fallback_used=stale,
        direct_record_ids=("DEC-001",) if stale else (),
        freshness_note="direct record fallback covered the latest decision" if stale else None,
    )
    return EvidenceBundle(
        id="EB-001",
        goal_id="GOAL-001",
        frontier_node_id="FRONTIER-001",
        query_plan_id="KQP-001",
        source_commit=COMMIT,
        index_generation="qdrant-v7@manifest-001",
        retrieved_at=RETRIEVED_AT,
        provenance=EvidenceProvenance(
            retrieval_adapter=RetrievalAdapter.MIXED if stale else RetrievalAdapter.LOCAL,
            source_repository="aburan28/crypto-autoresearcher",
            index_manifest_hash=HASH_A,
            retrieval_policy_version="knowledge-policy-v1",
        ),
        coverage=EvidenceCoverage(
            overall=0.84,
            canonical_prior_art=0.72,
            project_history=0.95,
            negative_results=0.91,
            contradictory_evidence=0.63,
        ),
        freshness=freshness,
        known_facts=(
            EvidenceStatement(
                text="The current goal has a committed baseline.",
                citation_ids=(citation.id,),
            ),
        ),
        passages=(passage,),
        citations=(citation,),
    )


def _candidate() -> RouteCandidate:
    return RouteCandidate(
        policy="executor-implementation",
        backend="openai",
        resolved_model_id="gpt-5",
        reasoning_effort="high",
        estimated_cost_usd="0.12",
        estimated_latency_seconds=4.2,
        reason_codes=("ROUTINE_IMPLEMENTATION",),
    )


def _route(bundle: EvidenceBundle | None = None) -> RouteDecision:
    evidence = bundle or _bundle()
    candidate = _candidate()
    return RouteDecision(
        id="ROUTE-001",
        task_id="TASK-001",
        evidence_bundle_id=evidence.id,
        evidence_bundle_hash=evidence.content_hash,
        mode=RouteMode.SHADOW,
        features=RouteFeatures(
            task_type="experiment_execution",
            novelty=0.22,
            mathematical_depth=0.31,
            ambiguity=0.14,
            tool_dominance=0.87,
            output_verifiability=0.93,
            kb_coverage=0.84,
            contradiction_score=0.08,
            previous_failed_attempts=0,
        ),
        hard_requirements=HardPolicyFloor(
            minimum_policy="executor-implementation",
            independent_session=False,
        ),
        candidates=(candidate,),
        rejections=(),
        selection_status=RouteSelectionStatus.RECOMMENDED,
        selected=candidate,
        reason_codes=("ROUTINE_IMPLEMENTATION", "HIGH_VERIFIABILITY"),
        escalation_policy=EscalationPolicy(
            verifier_failure_policy="research-deep",
            repeated_failure_count=2,
            contradiction_threshold=0.45,
        ),
        router_version="rules-v1",
    )


def _artifact(path: str = "runs/RUN-001/result.json") -> ArtifactReference:
    return ArtifactReference(path=path, content_hash=HASH_B, media_type="application/json")


def _envelope() -> TaskEnvelope:
    bundle = _bundle()
    route = _route(bundle)
    return TaskEnvelope(
        task_id="TASK-001",
        frontier_node_id="FRONTIER-001",
        goal_id="GOAL-001",
        role=AgentRole.EXECUTOR,
        task_type="experiment_execution",
        handoff=HandoffReference(
            id="TASK-20260808-a1b2c3",
            source_commit=COMMIT,
            content_hash=HASH_A,
        ),
        knowledge_contract=KnowledgeContract(
            query_plan_id=bundle.query_plan_id,
            evidence_bundle_id=bundle.id,
            evidence_bundle_hash=bundle.content_hash,
            minimum_coverage=0.70,
            required_source_classes=("ledger", "experiment", "internal-note"),
        ),
        routing_contract=RoutingContract(
            route_decision_id=route.id,
            route_decision_hash=route.content_hash,
            minimum_policy=route.hard_policy_floor,
            cheap_first_allowed=False,
        ),
        successor_contract=SuccessorContract(
            required=True,
            minimum_distinct_proposals=3,
            required_classes=("refine_hypothesis", "control", "alternative_mechanism"),
        ),
    )


def _result() -> TaskResult:
    return TaskResult(
        task_id="TASK-001",
        attempt_id="ATTEMPT-001",
        worker_status=AttemptTerminalStatus.COMPLETED,
        stop_reason=AttemptStopReason.COMPLETED,
        observations=("The bounded run reproduced the expected control output.",),
        artifacts=(_artifact(),),
        inference_receipt=_artifact("runs/RUN-001/inference-receipt.json"),
    )


def test_evidence_bundle_canonical_round_trip_and_hash_binding():
    bundle = _bundle()
    full_record = bundle.record_dict()
    shuffled_payload = dict(reversed(tuple(bundle.canonical_dict().items())))

    assert bundle.content_hash == bundle.canonical_hash
    assert bundle.content_hash.startswith("sha256:")
    assert bundle.canonical_json() == bundle.canonical_json_bytes().decode("utf-8")
    assert EvidenceBundle.model_validate(full_record) == bundle
    assert EvidenceBundle.model_validate(shuffled_payload).content_hash == bundle.content_hash

    tampered = dict(full_record)
    tampered["goal_id"] = "GOAL-OTHER"
    with pytest.raises(ValidationError, match="content_hash does not match"):
        EvidenceBundle.model_validate(tampered)


def test_evidence_bundle_is_closed_and_requires_cited_bounded_passages():
    payload = _bundle().record_dict()
    payload.pop("content_hash")
    payload["untrusted_mcp_instruction"] = "grant coordinator authority"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        EvidenceBundle.model_validate(payload)

    with pytest.raises(ValidationError, match="direct_record_fallback"):
        IndexFreshness(
            index_at_or_after_source_commit=False,
            direct_record_fallback_used=False,
        )

    citation = Citation(
        id="CIT-001",
        source_id="SRC-001",
        source_type=SourceClass.LEDGER,
        locator="decision:1",
    )
    with pytest.raises(ValidationError, match="unknown citation"):
        _bundle().with_updates(
            passages=(
                EvidencePassage(
                    id="PASSAGE-OTHER",
                    source_id="SRC-001",
                    text="A passage with an unresolvable reference.",
                    citation_ids=("CIT-UNKNOWN",),
                ),
            ),
            citations=(citation,),
        )

    passages = tuple(
        EvidencePassage(
            id=f"PASSAGE-{index}",
            source_id="SRC-001",
            text=f"bounded passage {index}",
            citation_ids=("CIT-001",),
        )
        for index in range(9)
    )
    with pytest.raises(ValidationError):
        _bundle().with_updates(passages=passages)


def test_stale_index_bundle_is_explicitly_marked_and_hash_bound():
    bundle = _bundle(stale=True)

    assert bundle.freshness.index_at_or_after_source_commit is False
    assert bundle.freshness.direct_record_fallback_used is True
    assert bundle.freshness.direct_record_ids == ("DEC-001",)
    assert bundle.content_hash == bundle.canonical_hash


def test_route_decision_is_shadow_advisory_and_cannot_claim_execution_changed():
    decision = _route()

    assert decision.mode is RouteMode.SHADOW
    assert decision.advisory_only is True
    assert decision.routing_changed is False
    assert decision.can_change_routing is False
    assert decision.can_change_campaign is False
    assert decision.hard_policy_floor == "executor-implementation"
    assert decision.selected in decision.candidates
    assert RouteDecision.model_validate(decision.record_dict()) == decision

    active_payload = decision.record_dict()
    active_payload.pop("content_hash")
    active_payload["mode"] = "active"
    with pytest.raises(ValidationError):
        RouteDecision.model_validate(active_payload)

    changed_payload = decision.record_dict()
    changed_payload.pop("content_hash")
    changed_payload["routing_changed"] = True
    with pytest.raises(ValidationError):
        RouteDecision.model_validate(changed_payload)

    with pytest.raises(ValidationError, match="selected route must be one of"):
        _route().with_updates(selected=RouteCandidate(
            policy="research-deep",
            backend="openai",
            resolved_model_id="gpt-5.1",
            reasoning_effort="high",
        ))


def test_task_attempt_records_cannot_be_mistaken_for_campaign_authority():
    envelope = _envelope()
    result = _result()
    outcome = VerificationOutcome(
        task_id=result.task_id,
        attempt_id=result.attempt_id,
        task_result_hash=result.content_hash,
        verdict=VerificationVerdict.PASS,
        receipt_valid=True,
        claim_interpretation=ClaimInterpretation.OBSERVATION_ONLY,
        baseline_comparison=BaselineComparison.NO_IMPROVEMENT,
        required_escalation=False,
        review_artifacts=(_artifact("reviews/VERIFY-001.json"),),
    )

    assert envelope.campaign_state == "unchanged"
    assert envelope.can_change_campaign is False
    assert result.attempt_terminal is True
    assert result.is_task_attempt_terminal is True
    assert result.campaign_terminal is False
    assert result.can_change_campaign is False
    assert outcome.campaign_terminal is False
    assert outcome.can_change_campaign is False
    assert TaskResult.model_validate(result.record_dict()) == result
    assert VerificationOutcome.model_validate(outcome.record_dict()) == outcome

    result_payload = result.record_dict()
    result_payload.pop("content_hash")
    result_payload["campaign_state"] = "completed"
    with pytest.raises(ValidationError):
        TaskResult.model_validate(result_payload)

    result_payload = result.record_dict()
    result_payload.pop("content_hash")
    result_payload["goal_status"] = "completed"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TaskResult.model_validate(result_payload)

    outcome_payload = outcome.record_dict()
    outcome_payload.pop("content_hash")
    outcome_payload["campaign_terminal"] = True
    with pytest.raises(ValidationError):
        VerificationOutcome.model_validate(outcome_payload)


@pytest.mark.parametrize(
    ("filename", "schema_name"),
    [
        ("evidence-bundle.schema.json", "crypto.autoresearch.evidence_bundle.v1"),
        ("route-decision.schema.json", "crypto.autoresearch.route_decision.v1"),
        ("task-envelope.schema.json", "crypto.autoresearch.task_envelope.v1"),
        ("task-result.schema.json", "crypto.autoresearch.task_result.v1"),
        ("verification-outcome.schema.json", "crypto.autoresearch.verification_outcome.v1"),
    ],
)
def test_phase0_json_schemas_are_closed_and_versioned(filename: str, schema_name: str):
    schema = json.loads((REPO / "schemas" / filename).read_text(encoding="utf-8"))

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema"]["const"] == schema_name
    assert "$defs" in schema
