"""Closed, hash-bound contracts for bounded research evidence.

These are Phase-0 data contracts only.  They do not perform retrieval, talk to
an MCP server, or write any repository state.  Keeping the contracts here lets
an in-process client and an MCP client produce byte-for-byte equivalent
evidence records later in the rollout.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Annotated, ClassVar, Literal, Mapping, TypeVar

try:  # Deliberately local to this optional module; see package __init__.py.
    from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by minimal installs.
    raise ImportError(
        "orchestration.knowledge.models requires the optional 'pydantic' dependency; "
        "install the campaign contracts dependency before importing this module"
    ) from exc


SCHEMA_EVIDENCE_BUNDLE_V1 = "crypto.autoresearch.evidence_bundle.v1"

_HASH_PATTERN = r"^sha256:[0-9a-f]{64}$"
_GIT_COMMIT_PATTERN = r"^[0-9a-f]{7,64}$"
# Task and successor kinds in Research Loop v2 intentionally use snake_case
# (for example ``experiment_execution`` and ``find_proof_gap``), so underscore
# is part of the canonical identifier alphabet alongside the existing URI-ish
# punctuation.
_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/@+_\-]*$"

Identifier = Annotated[
    str,
    Field(min_length=1, max_length=256, pattern=_IDENTIFIER_PATTERN),
]
GitCommit = Annotated[str, Field(pattern=_GIT_COMMIT_PATTERN)]
HashValue = Annotated[str, Field(pattern=_HASH_PATTERN)]
ShortText = Annotated[str, Field(min_length=1, max_length=512)]
PassageText = Annotated[str, Field(min_length=1, max_length=8_000)]
StatementText = Annotated[str, Field(min_length=1, max_length=4_000)]
UnitInterval = Annotated[float, Field(ge=0.0, le=1.0)]


class ContractValidationError(ValueError):
    """Raised when a value cannot be represented as canonical JSON."""


def _canonicalize(value: Any) -> Any:
    """Return a recursively JSON-native, deterministic representation.

    This deliberately has a smaller type surface than a general serializer:
    contracts must be portable across Codex, Claude Code, OpenCode, direct
    Python clients, and MCP transports.  In particular, non-finite floats,
    naïve datetimes, arbitrary objects, and non-string mapping keys fail
    closed instead of acquiring transport-specific encodings.
    """

    if isinstance(value, BaseModel):
        return _canonicalize(value.model_dump(mode="python", by_alias=True))
    if isinstance(value, Enum):
        return _canonicalize(value.value)
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ContractValidationError("canonical timestamps must carry a timezone")
        normalized = value.astimezone(timezone.utc)
        return normalized.isoformat().replace("+00:00", "Z")
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractValidationError("canonical JSON object keys must be strings")
            normalized[key] = _canonicalize(item)
        return normalized
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractValidationError("canonical JSON forbids non-finite floats")
        return value
    raise ContractValidationError(
        f"unsupported value in canonical contract: {type(value).__name__}"
    )


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


CanonicalT = TypeVar("CanonicalT", bound="CanonicalContract")


class CanonicalContract(ClosedModel):
    """Closed record with deterministic serialization and a self-verifying hash."""

    content_hash: HashValue | None = None

    @model_validator(mode="after")
    def _verify_content_hash(self: CanonicalT) -> CanonicalT:
        if self.content_hash is not None and self.content_hash != self.canonical_hash:
            raise ValueError("content_hash does not match canonical payload")
        return self

    def canonical_dict(self) -> dict[str, Any]:
        """Return the hash payload (all fields except the self-referential hash)."""

        payload = self.model_dump(mode="python", by_alias=True, exclude={"content_hash"})
        return _canonicalize(payload)

    def canonical_json_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_dict(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def canonical_json(self) -> str:
        return self.canonical_json_bytes().decode("utf-8")

    @property
    def canonical_hash(self) -> str:
        return "sha256:" + hashlib.sha256(self.canonical_json_bytes()).hexdigest()

    def record_dict(self) -> dict[str, Any]:
        payload = self.model_dump(mode="python", by_alias=True, exclude={"content_hash"})
        payload["content_hash"] = self.canonical_hash
        return _canonicalize(payload)

    def with_updates(self: CanonicalT, **changes: Any) -> CanonicalT:
        """Return a revalidated copy while recomputing any prior content hash."""

        if "content_hash" not in changes:
            changes["content_hash"] = None
        return self.model_copy(update=changes).model_validate(
            self.model_copy(update=changes).model_dump(mode="python", by_alias=True)
        )


class SourceClass(str, Enum):
    LEDGER = "ledger"
    EXPERIMENT = "experiment"
    INTERNAL_NOTE = "internal-note"
    LITERATURE = "literature"
    CODE = "code"
    EXTERNAL_PRIMARY = "external-primary"


class RetrievalAdapter(str, Enum):
    LOCAL = "local"
    MCP = "mcp"
    MIXED = "mixed"


class Citation(ClosedModel):
    id: Identifier
    source_id: Identifier
    source_type: SourceClass
    locator: ShortText
    source_commit: GitCommit | None = None


class EvidencePassage(ClosedModel):
    id: Identifier
    source_id: Identifier
    text: PassageText
    citation_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def _unique_citations(self) -> "EvidencePassage":
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("citation_ids must be unique")
        return self


class EvidenceStatement(ClosedModel):
    text: StatementText
    citation_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def _unique_citations(self) -> "EvidenceStatement":
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("statement citation_ids must be unique")
        return self


class EvidenceCoverage(ClosedModel):
    overall: UnitInterval
    canonical_prior_art: UnitInterval
    project_history: UnitInterval
    negative_results: UnitInterval
    contradictory_evidence: UnitInterval

    @field_validator(
        "overall",
        "canonical_prior_art",
        "project_history",
        "negative_results",
        "contradictory_evidence",
    )
    @classmethod
    def _finite_scores(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("coverage scores must be finite")
        return value


class IndexFreshness(ClosedModel):
    index_at_or_after_source_commit: bool
    direct_record_fallback_used: bool
    direct_record_ids: tuple[Identifier, ...] = Field(default_factory=tuple, max_length=64)
    freshness_note: ShortText | None = None

    @model_validator(mode="after")
    def _validate_fallback(self) -> "IndexFreshness":
        if not self.index_at_or_after_source_commit and not self.direct_record_fallback_used:
            raise ValueError(
                "stale index requires direct_record_fallback_used before evidence may be routed"
            )
        if self.direct_record_fallback_used and not self.direct_record_ids:
            raise ValueError("direct record fallback requires at least one direct_record_id")
        if not self.direct_record_fallback_used and self.direct_record_ids:
            raise ValueError("direct_record_ids require direct_record_fallback_used")
        return self


class EvidenceProvenance(ClosedModel):
    retrieval_adapter: RetrievalAdapter
    source_repository: Identifier
    index_manifest_hash: HashValue
    retrieval_policy_version: Identifier


class EvidenceBundle(CanonicalContract):
    schema_version: Literal[SCHEMA_EVIDENCE_BUNDLE_V1] = Field(
        default=SCHEMA_EVIDENCE_BUNDLE_V1,
        alias="schema",
    )
    id: Identifier
    goal_id: Identifier
    frontier_node_id: Identifier
    query_plan_id: Identifier
    source_commit: GitCommit
    index_generation: Identifier
    retrieved_at: datetime
    provenance: EvidenceProvenance
    coverage: EvidenceCoverage
    freshness: IndexFreshness
    known_facts: tuple[EvidenceStatement, ...] = Field(default_factory=tuple, max_length=64)
    negative_results: tuple[EvidenceStatement, ...] = Field(default_factory=tuple, max_length=64)
    contradictory_evidence: tuple[EvidenceStatement, ...] = Field(default_factory=tuple, max_length=64)
    unresolved_questions: tuple[EvidenceStatement, ...] = Field(default_factory=tuple, max_length=64)
    passages: tuple[EvidencePassage, ...] = Field(default_factory=tuple, max_length=64)
    citations: tuple[Citation, ...] = Field(default_factory=tuple, max_length=128)

    @field_validator("retrieved_at")
    @classmethod
    def _timestamp_is_utc_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("retrieved_at must carry a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def _validate_references(self) -> "EvidenceBundle":
        citation_ids = [citation.id for citation in self.citations]
        if len(set(citation_ids)) != len(citation_ids):
            raise ValueError("citation IDs must be unique")
        passage_ids = [passage.id for passage in self.passages]
        if len(set(passage_ids)) != len(passage_ids):
            raise ValueError("passage IDs must be unique")
        citation_set = set(citation_ids)
        for item in (
            *self.known_facts,
            *self.negative_results,
            *self.contradictory_evidence,
            *self.unresolved_questions,
            *self.passages,
        ):
            missing = set(item.citation_ids) - citation_set
            if missing:
                raise ValueError(f"unknown citation IDs: {sorted(missing)!r}")
        if not self.passages:
            raise ValueError("evidence bundle requires at least one bounded passage")
        return self

    @property
    def content_hash(self) -> str:
        # Preserve the ergonomic access used throughout the migration: a newly
        # constructed bundle is hash-addressable even before it is serialized
        # as a record containing its explicit self-verifying hash.
        return self.canonical_hash


__all__ = [
    "CanonicalContract",
    "Citation",
    "ClosedModel",
    "ContractValidationError",
    "EvidenceBundle",
    "EvidenceCoverage",
    "EvidencePassage",
    "EvidenceProvenance",
    "EvidenceStatement",
    "GitCommit",
    "HashValue",
    "Identifier",
    "IndexFreshness",
    "PassageText",
    "RetrievalAdapter",
    "SCHEMA_EVIDENCE_BUNDLE_V1",
    "ShortText",
    "SourceClass",
    "StatementText",
    "UnitInterval",
]
