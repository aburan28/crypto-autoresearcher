"""Closed Phase-0 contracts for advisory routing and task-attempt outcomes.

Nothing in this module selects a model, runs a task, verifies evidence, writes
a queue, or advances a campaign.  It only defines immutable records so later
implementations can compare a proposed route and a terminal *attempt* outcome
without confusing either with an authoritative campaign transition.
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from orchestration.knowledge.models import (
    CanonicalContract,
    ClosedModel,
    GitCommit,
    HashValue,
    Identifier,
    ShortText,
    UnitInterval,
)


SCHEMA_ROUTE_DECISION_V1 = "crypto.autoresearch.route_decision.v1"
SCHEMA_TASK_ENVELOPE_V1 = "crypto.autoresearch.task_envelope.v1"
SCHEMA_TASK_RESULT_V1 = "crypto.autoresearch.task_result.v1"
SCHEMA_VERIFICATION_OUTCOME_V1 = "crypto.autoresearch.verification_outcome.v1"

ArtifactPath = ShortText
ReasonCode = ShortText
PolicyId = Identifier
BackendId = Identifier
ModelId = Identifier


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    IDEA_GENERATOR = "idea-generator"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    VALIDATOR = "validator"
    RED_TEAM = "red-team"
    THEORY_AGENT = "theory-agent"
    BENCHMARK_AGENT = "benchmark-agent"


class RouteMode(str, Enum):
    """The only Phase-0 route modes: neither changes current execution."""

    SHADOW = "shadow"
    ADVISORY = "advisory"


class RouteSelectionStatus(str, Enum):
    RECOMMENDED = "recommended"
    NO_ELIGIBLE_CANDIDATE = "no_eligible_candidate"


class AttemptTerminalStatus(str, Enum):
    COMPLETED = "completed"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TOOL_DENIED = "tool_denied"
    MODEL_ERROR = "model_error"
    INVALID_OUTPUT = "invalid_output"
    CANCELLED = "cancelled"


class AttemptStopReason(str, Enum):
    COMPLETED = "completed"
    WALL_CLOCK_BUDGET_EXHAUSTED = "wall_clock_budget_exhausted"
    MAXIMUM_RUNS_EXHAUSTED = "maximum_runs_exhausted"
    TOOL_DENIED = "tool_denied"
    MODEL_ERROR = "model_error"
    INVALID_OUTPUT = "invalid_output"
    CANCELLED = "cancelled"


class VerificationVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"
    INVALID = "invalid"


class ClaimInterpretation(str, Enum):
    """A verifier's limited interpretation, never a ledger state transition."""

    INCONCLUSIVE = "inconclusive"
    OBSERVATION_ONLY = "observation_only"
    BASELINE_NOT_IMPROVED = "baseline_not_improved"
    CONTRADICTION_REQUIRES_REVIEW = "contradiction_requires_review"


class BaselineComparison(str, Enum):
    NO_IMPROVEMENT = "no_improvement"
    IMPROVEMENT_OBSERVED = "improvement_observed"
    REGRESSION_OBSERVED = "regression_observed"
    NOT_APPLICABLE = "not_applicable"
    UNAVAILABLE = "unavailable"


class VerificationFailureClass(str, Enum):
    RECEIPT_INVALID = "receipt_invalid"
    SCHEMA_FAILURE = "schema_failure"
    VERIFIER_FAILURE = "verifier_failure"
    CONTROL_FAILURE = "control_failure"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    EVIDENCE_INSUFFICIENT = "evidence_insufficient"


class RouteFeatures(ClosedModel):
    """Deterministic/classified inputs recorded for an auditable route."""

    task_type: Identifier
    novelty: UnitInterval
    mathematical_depth: UnitInterval
    ambiguity: UnitInterval
    tool_dominance: UnitInterval
    output_verifiability: UnitInterval
    kb_coverage: UnitInterval
    contradiction_score: UnitInterval
    previous_failed_attempts: int = Field(ge=0, le=1_000_000)

    @field_validator(
        "novelty",
        "mathematical_depth",
        "ambiguity",
        "tool_dominance",
        "output_verifiability",
        "kb_coverage",
        "contradiction_score",
    )
    @classmethod
    def _finite_scores(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("route feature scores must be finite")
        return value


class HardPolicyFloor(ClosedModel):
    """Non-negotiable capability requirements before any cost comparison."""

    minimum_policy: PolicyId
    independent_session: bool
    no_degradation: bool = True
    required_runtime_capabilities: tuple[Identifier, ...] = Field(
        default_factory=tuple,
        max_length=16,
    )

    @model_validator(mode="after")
    def _unique_capabilities(self) -> "HardPolicyFloor":
        if len(set(self.required_runtime_capabilities)) != len(
            self.required_runtime_capabilities
        ):
            raise ValueError("required_runtime_capabilities must be unique")
        return self


class RouteCandidate(ClosedModel):
    """A policy/backend/model binding that survived the declared hard gates."""

    policy: PolicyId
    backend: BackendId
    resolved_model_id: ModelId
    reasoning_effort: Identifier
    capability_fit: Literal["eligible"] = "eligible"
    estimated_cost_usd: ShortText | None = None
    estimated_latency_seconds: float | None = Field(default=None, ge=0.0)
    reason_codes: tuple[ReasonCode, ...] = Field(default_factory=tuple, max_length=16)

    @field_validator("estimated_latency_seconds")
    @classmethod
    def _finite_latency(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("estimated_latency_seconds must be finite")
        return value

    @property
    def binding_key(self) -> tuple[str, str, str]:
        return (self.policy, self.backend, self.resolved_model_id)


class RouteRejection(ClosedModel):
    """A binding excluded before selection, with a machine-reviewable reason."""

    policy: PolicyId
    backend: BackendId
    resolved_model_id: ModelId
    reason_code: ReasonCode
    hard_gate: bool

    @property
    def binding_key(self) -> tuple[str, str, str]:
        return (self.policy, self.backend, self.resolved_model_id)


class EscalationPolicy(ClosedModel):
    """A proposed future escalation rule, not a scheduling command."""

    verifier_failure_policy: PolicyId
    repeated_failure_count: int = Field(ge=1, le=1_000_000)
    contradiction_threshold: UnitInterval

    @field_validator("contradiction_threshold")
    @classmethod
    def _finite_threshold(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("contradiction_threshold must be finite")
        return value


class RouteDecision(CanonicalContract):
    """An immutable shadow/advisory recommendation with no execution authority."""

    schema_version: Literal[SCHEMA_ROUTE_DECISION_V1] = Field(
        default=SCHEMA_ROUTE_DECISION_V1,
        alias="schema",
    )
    id: Identifier
    task_id: Identifier
    evidence_bundle_id: Identifier
    evidence_bundle_hash: HashValue
    mode: RouteMode = RouteMode.SHADOW
    advisory_only: Literal[True] = True
    routing_changed: Literal[False] = False
    campaign_transition_authority: Literal["none"] = "none"
    features: RouteFeatures
    hard_requirements: HardPolicyFloor
    candidates: tuple[RouteCandidate, ...] = Field(default_factory=tuple, max_length=32)
    rejections: tuple[RouteRejection, ...] = Field(default_factory=tuple, max_length=32)
    selection_status: RouteSelectionStatus
    selected: RouteCandidate | None = None
    reason_codes: tuple[ReasonCode, ...] = Field(default_factory=tuple, max_length=32)
    escalation_policy: EscalationPolicy
    router_version: Identifier

    @model_validator(mode="after")
    def _validate_advisory_selection(self) -> "RouteDecision":
        candidate_keys = tuple(candidate.binding_key for candidate in self.candidates)
        rejected_keys = tuple(rejection.binding_key for rejection in self.rejections)
        if len(set(candidate_keys)) != len(candidate_keys):
            raise ValueError("route candidates must not repeat a binding")
        if len(set(rejected_keys)) != len(rejected_keys):
            raise ValueError("route rejections must not repeat a binding")
        overlap = set(candidate_keys) & set(rejected_keys)
        if overlap:
            raise ValueError(
                "a route binding cannot be both eligible and rejected: "
                f"{sorted(overlap)!r}"
            )
        if self.selection_status is RouteSelectionStatus.RECOMMENDED:
            if self.selected is None:
                raise ValueError("a recommended route decision requires selected")
            if self.selected.binding_key not in set(candidate_keys):
                raise ValueError("selected route must be one of the eligible candidates")
        elif self.selected is not None:
            raise ValueError("a no-eligible-candidate decision may not select a route")
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("route reason_codes must be unique")
        return self

    @property
    def hard_policy_floor(self) -> str:
        """Convenience accessor for the non-negotiable minimum policy."""

        return self.hard_requirements.minimum_policy

    @property
    def can_change_routing(self) -> bool:
        """Phase 0 is intentionally read-only with respect to execution."""

        return False

    @property
    def can_change_campaign(self) -> bool:
        return False


class HandoffReference(ClosedModel):
    """Immutable reference to an existing handoff rather than a replacement."""

    id: Identifier
    source_commit: GitCommit
    content_hash: HashValue


class KnowledgeContract(ClosedModel):
    """The required evidence binding for a single bounded task attempt."""

    query_plan_id: Identifier
    evidence_bundle_id: Identifier
    evidence_bundle_hash: HashValue
    minimum_coverage: UnitInterval
    required_source_classes: tuple[Identifier, ...] = Field(min_length=1, max_length=8)

    @field_validator("minimum_coverage")
    @classmethod
    def _finite_coverage(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("minimum_coverage must be finite")
        return value

    @model_validator(mode="after")
    def _unique_source_classes(self) -> "KnowledgeContract":
        if len(set(self.required_source_classes)) != len(self.required_source_classes):
            raise ValueError("required_source_classes must be unique")
        return self


class RoutingContract(ClosedModel):
    """The shadow/advisory route binding carried by a task envelope."""

    route_decision_id: Identifier
    route_decision_hash: HashValue
    minimum_policy: PolicyId
    cheap_first_allowed: bool
    route_is_advisory: Literal[True] = True


class SuccessorContract(ClosedModel):
    """Requested follow-up proposals; it grants no ability to admit or dispatch them."""

    required: bool
    minimum_distinct_proposals: int = Field(ge=0, le=64)
    required_classes: tuple[Identifier, ...] = Field(default_factory=tuple, max_length=16)
    campaign_terminal_authority: Literal[False] = False

    @model_validator(mode="after")
    def _validate_requirements(self) -> "SuccessorContract":
        if self.required and self.minimum_distinct_proposals < 1:
            raise ValueError("required successors need at least one proposal")
        if self.required and not self.required_classes:
            raise ValueError("required successors need at least one required class")
        if len(set(self.required_classes)) != len(self.required_classes):
            raise ValueError("required_classes must be unique")
        return self


class TaskEnvelope(CanonicalContract):
    """A hash-bound extension around a legacy handoff for one task, not a campaign."""

    schema_version: Literal[SCHEMA_TASK_ENVELOPE_V1] = Field(
        default=SCHEMA_TASK_ENVELOPE_V1,
        alias="schema",
    )
    task_id: Identifier
    frontier_node_id: Identifier
    goal_id: Identifier
    role: AgentRole
    task_type: Identifier
    handoff: HandoffReference
    knowledge_contract: KnowledgeContract
    routing_contract: RoutingContract
    successor_contract: SuccessorContract
    campaign_state: Literal["unchanged"] = "unchanged"
    campaign_transition_authority: Literal["none"] = "none"

    @property
    def can_change_campaign(self) -> bool:
        return False


class ArtifactReference(ClosedModel):
    """A bounded immutable artifact reference produced or reviewed by an attempt."""

    path: ArtifactPath
    content_hash: HashValue
    media_type: ShortText | None = None


class TaskResult(CanonicalContract):
    """Observations from one terminal worker attempt, never a campaign result."""

    schema_version: Literal[SCHEMA_TASK_RESULT_V1] = Field(
        default=SCHEMA_TASK_RESULT_V1,
        alias="schema",
    )
    task_id: Identifier
    attempt_id: Identifier
    worker_status: AttemptTerminalStatus
    attempt_terminal: Literal[True] = True
    stop_reason: AttemptStopReason
    observations: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=64)
    artifacts: tuple[ArtifactReference, ...] = Field(default_factory=tuple, max_length=64)
    anomalies: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=32)
    limitations: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=32)
    suggested_followups: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=32)
    inference_receipt: ArtifactReference | None = None
    campaign_state: Literal["unchanged"] = "unchanged"
    campaign_transition_authority: Literal["none"] = "none"
    campaign_terminal: Literal[False] = False

    @model_validator(mode="after")
    def _validate_attempt_terminal_reason(self) -> "TaskResult":
        allowed_reasons = {
            AttemptTerminalStatus.COMPLETED: {AttemptStopReason.COMPLETED},
            AttemptTerminalStatus.BUDGET_EXHAUSTED: {
                AttemptStopReason.WALL_CLOCK_BUDGET_EXHAUSTED,
                AttemptStopReason.MAXIMUM_RUNS_EXHAUSTED,
            },
            AttemptTerminalStatus.TOOL_DENIED: {AttemptStopReason.TOOL_DENIED},
            AttemptTerminalStatus.MODEL_ERROR: {AttemptStopReason.MODEL_ERROR},
            AttemptTerminalStatus.INVALID_OUTPUT: {AttemptStopReason.INVALID_OUTPUT},
            AttemptTerminalStatus.CANCELLED: {AttemptStopReason.CANCELLED},
        }
        if self.stop_reason not in allowed_reasons[self.worker_status]:
            raise ValueError(
                f"stop_reason {self.stop_reason.value!r} is incompatible with "
                f"worker_status {self.worker_status.value!r}"
            )
        artifact_keys = tuple((artifact.path, artifact.content_hash) for artifact in self.artifacts)
        if len(set(artifact_keys)) != len(artifact_keys):
            raise ValueError("artifacts must not repeat the same path/hash reference")
        return self

    @property
    def is_task_attempt_terminal(self) -> bool:
        return True

    @property
    def can_change_campaign(self) -> bool:
        return False


class VerificationOutcome(CanonicalContract):
    """Verifier output for one task attempt; Coordinator review remains separate."""

    schema_version: Literal[SCHEMA_VERIFICATION_OUTCOME_V1] = Field(
        default=SCHEMA_VERIFICATION_OUTCOME_V1,
        alias="schema",
    )
    task_id: Identifier
    attempt_id: Identifier
    task_result_hash: HashValue
    verdict: VerificationVerdict
    receipt_valid: bool
    claim_interpretation: ClaimInterpretation
    baseline_comparison: BaselineComparison
    failure_class: VerificationFailureClass | None = None
    required_escalation: bool
    successor_constraints: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=32)
    review_artifacts: tuple[ArtifactReference, ...] = Field(default_factory=tuple, max_length=32)
    campaign_state: Literal["unchanged"] = "unchanged"
    campaign_transition_authority: Literal["none"] = "none"
    campaign_terminal: Literal[False] = False

    @model_validator(mode="after")
    def _validate_verdict(self) -> "VerificationOutcome":
        if self.verdict is VerificationVerdict.PASS and not self.receipt_valid:
            raise ValueError("a passing verification outcome requires a valid receipt")
        if self.verdict is VerificationVerdict.INVALID and self.failure_class is None:
            raise ValueError("an invalid verification outcome requires failure_class")
        artifact_keys = tuple(
            (artifact.path, artifact.content_hash) for artifact in self.review_artifacts
        )
        if len(set(artifact_keys)) != len(artifact_keys):
            raise ValueError("review_artifacts must not repeat the same path/hash reference")
        return self

    @property
    def can_change_campaign(self) -> bool:
        return False


__all__ = [
    "AgentRole",
    "ArtifactReference",
    "AttemptStopReason",
    "AttemptTerminalStatus",
    "BaselineComparison",
    "ClaimInterpretation",
    "EscalationPolicy",
    "HardPolicyFloor",
    "HandoffReference",
    "KnowledgeContract",
    "RouteCandidate",
    "RouteDecision",
    "RouteFeatures",
    "RouteMode",
    "RouteRejection",
    "RouteSelectionStatus",
    "RoutingContract",
    "SCHEMA_ROUTE_DECISION_V1",
    "SCHEMA_TASK_ENVELOPE_V1",
    "SCHEMA_TASK_RESULT_V1",
    "SCHEMA_VERIFICATION_OUTCOME_V1",
    "SuccessorContract",
    "TaskEnvelope",
    "TaskResult",
    "VerificationFailureClass",
    "VerificationOutcome",
    "VerificationVerdict",
]
