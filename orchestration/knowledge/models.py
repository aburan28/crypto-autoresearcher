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
# Research Loop task and successor kinds intentionally use snake_case, so
# underscore is part of the canonical identifier alphabet.
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
        # JSON preserves a signed zero.  The contracts deliberately do not.
        return 0.0 if value == 0.0 else value
    raise ContractValidationError(
        f"value of type {type(value).__name__} is not canonical JSON data"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Encode *value* as the compact, key-sorted canonical JSON used by v2."""

    try:
        return json.dumps(
            _canonicalize(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractValidationError(f"cannot canonicalize JSON value: {exc}") from exc


def canonical_json(value: Any) -> str:
    """Return the UTF-8 canonical JSON text for *value*."""

    return canonical_json_bytes(value).decode("utf-8")


def sha256_digest(value: Any) -> str:
    """Return the prefixed SHA-256 digest of canonical JSON *value*."""

    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


class ClosedModel(BaseModel):
    """A frozen Pydantic model whose wire shape cannot grow silently."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        validate_default=True,
    )


ContractT = TypeVar("ContractT", bound="CanonicalContract")


class CanonicalContract(ClosedModel):
    """A closed contract with a deterministic self-binding content hash.

    ``content_hash`` is computed over ``canonical_dict()`` -- all serialized
    fields except the hash itself -- and is therefore safe to persist in the
    full record returned by ``record_dict()``.  Supplying a hash is allowed
    only when it verifies, which makes transport round trips fail closed.
    """

    content_hash: HashValue | None = None

    @model_validator(mode="after")
    def _bind_content_hash(self) -> "CanonicalContract":
        expected = self.canonical_hash
        if self.content_hash is not None and self.content_hash != expected:
            raise ValueError(
                "content_hash does not match the canonical contract payload "
                f"(expected {expected})"
            )
        object.__setattr__(self, "content_hash", expected)
        return self

    def canonical_dict(self) -> dict[str, Any]:
        """The exact hash preimage, excluding the self-referential hash."""

        raw = self.model_dump(mode="python", by_alias=True, exclude={"content_hash"})
        normalized = _canonicalize(raw)
        if not isinstance(normalized, dict):  # defensive: all contracts are objects.
            raise ContractValidationError("contract canonical payload must be an object")
        return normalized

    def canonical_json_bytes(self) -> bytes:
        """The byte sequence used to compute ``content_hash``."""

        return canonical_json_bytes(self.canonical_dict())

    def canonical_json(self) -> str:
        """The UTF-8-decoded canonical hash preimage."""

        return self.canonical_json_bytes().decode("utf-8")

    @property
    def canonical_hash(self) -> str:
        """The SHA-256 binding for the canonical payload."""

        return "sha256:" + hashlib.sha256(self.canonical_json_bytes()).hexdigest()

    @property
    def sha256(self) -> str:
        """Alias for callers that name the digest rather than the field."""

        return self.canonical_hash

    def record_dict(self) -> dict[str, Any]:
        """The complete JSON-ready record, including its verified hash."""

        raw = self.model_dump(mode="python", by_alias=True)
        normalized = _canonicalize(raw)
        if not isinstance(normalized, dict):  # defensive: see canonical_dict().
            raise ContractValidationError("contract record must be an object")
        return normalized

    def record_json_bytes(self) -> bytes:
        """Canonical JSON for the complete record (including ``content_hash``)."""

        return canonical_json_bytes(self.record_dict())

    def record_json(self) -> str:
        return self.record_json_bytes().decode("utf-8")

    def with_updates(self: ContractT, **updates: Any) -> ContractT:
        """Create a revalidated replacement and recompute its content hash."""

        payload = self.model_dump(mode="python", by_alias=False, exclude={"content_hash"})
        payload.update(updates)
        return type(self).model_validate(payload)

    def model_copy(
        self: ContractT,
        *,
        update: Mapping[str, Any] | None = None,
        deep: bool = False,
    ) -> ContractT:
        """Prevent Pydantic's unchecked copy path from leaving a stale hash.

        ``deep`` is accepted for API compatibility.  Every contract and nested
        member is immutable, so revalidation is the meaningful operation.
        """

        del deep
        return self.with_updates(**dict(update or {}))


class SourceClass(str, Enum):
    LEDGER = "ledger"
    EXPERIMENT = "experiment"
    INTERNAL_NOTE = "internal-note"
    LITERATURE = "literature"
    CODE = "code"
    OTHER = "other"


class RetrievalAdapter(str, Enum):
    LOCAL = "local"
    MCP = "mcp"
    DIRECT_RECORD = "direct_record"
    MIXED = "mixed"


class EvidenceProvenance(ClosedModel):
    """How an evidence bundle was obtained, without granting source authority."""

    retrieval_adapter: RetrievalAdapter
    source_repository: Identifier
    index_manifest_hash: HashValue | None = None
    retrieval_policy_version: Identifier


class EvidenceCoverage(ClosedModel):
    """Deterministic/calibrated coverage by required evidence class, not confidence."""

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
    def _finite_coverage(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("coverage values must be finite")
        return value


class IndexFreshness(ClosedModel):
    """The source/index freshness decision and any direct-record recovery."""

    index_at_or_after_source_commit: bool
    direct_record_fallback_used: bool
    direct_record_ids: tuple[Identifier, ...] = Field(default_factory=tuple, max_length=64)
    freshness_note: ShortText | None = None

    @model_validator(mode="after")
    def _require_stale_fallback(self) -> "IndexFreshness":
        if not self.index_at_or_after_source_commit:
            if not self.direct_record_fallback_used:
                raise ValueError(
                    "a stale index must record direct_record_fallback_used=true"
                )
            if not self.direct_record_ids:
                raise ValueError(
                    "a stale index fallback must identify the direct records used"
                )
        if self.direct_record_fallback_used and not self.direct_record_ids:
            raise ValueError("direct-record fallback requires at least one direct record id")
        if not self.direct_record_fallback_used and self.direct_record_ids:
            raise ValueError(
                "direct_record_ids require direct_record_fallback_used=true"
            )
        if len(set(self.direct_record_ids)) != len(self.direct_record_ids):
            raise ValueError("direct_record_ids must be unique")
        return self


class Citation(ClosedModel):
    """A compact, source-preserving citation suitable for every host transport."""

    id: Identifier
    source_id: Identifier
    source_type: SourceClass
    locator: ShortText
    source_commit: GitCommit | None = None


class EvidencePassage(ClosedModel):
    """A bounded retrieved passage whose citations are resolved by the bundle."""

    id: Identifier
    source_id: Identifier
    text: PassageText
    citation_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _unique_citation_ids(self) -> "EvidencePassage":
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("a passage may not cite the same citation id twice")
        return self


class EvidenceStatement(ClosedModel):
    """A compact structured fact, negative result, or unresolved question."""

    text: StatementText
    citation_ids: tuple[Identifier, ...] = Field(default_factory=tuple, max_length=8)

    @model_validator(mode="after")
    def _unique_citation_ids(self) -> "EvidenceStatement":
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("an evidence statement may not repeat a citation id")
        return self


class EvidenceBundle(CanonicalContract):
    """The immutable, bounded evidence context for planning and shadow routing."""

    schema_version: Literal[SCHEMA_EVIDENCE_BUNDLE_V1] = Field(
        default=SCHEMA_EVIDENCE_BUNDLE_V1,
        alias="schema",
    )
    id: Identifier
    goal_id: Identifier
    frontier_node_id: Identifier | None = None
    query_plan_id: Identifier
    source_commit: GitCommit
    index_generation: Identifier
    retrieved_at: datetime
    provenance: EvidenceProvenance
    coverage: EvidenceCoverage
    freshness: IndexFreshness
    known_facts: tuple[EvidenceStatement, ...] = Field(default_factory=tuple, max_length=32)
    prior_experiments: tuple[EvidenceStatement, ...] = Field(
        default_factory=tuple,
        max_length=32,
    )
    negative_results: tuple[EvidenceStatement, ...] = Field(
        default_factory=tuple,
        max_length=32,
    )
    contradictions: tuple[EvidenceStatement, ...] = Field(
        default_factory=tuple,
        max_length=32,
    )
    open_questions: tuple[EvidenceStatement, ...] = Field(
        default_factory=tuple,
        max_length=32,
    )
    passages: tuple[EvidencePassage, ...] = Field(default_factory=tuple, max_length=8)
    citations: tuple[Citation, ...] = Field(default_factory=tuple, max_length=32)
    retrieval_warnings: tuple[ShortText, ...] = Field(default_factory=tuple, max_length=16)

    @field_validator("retrieved_at")
    @classmethod
    def _normalize_retrieved_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("retrieved_at must be timezone-aware")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def _validate_citations_and_bounds(self) -> "EvidenceBundle":
        citation_ids = tuple(citation.id for citation in self.citations)
        if len(set(citation_ids)) != len(citation_ids):
            raise ValueError("citation ids must be unique within an evidence bundle")
        known_citations = set(citation_ids)

        passage_ids = tuple(passage.id for passage in self.passages)
        if len(set(passage_ids)) != len(passage_ids):
            raise ValueError("passage ids must be unique within an evidence bundle")

        for passage in self.passages:
            unknown = set(passage.citation_ids) - known_citations
            if unknown:
                raise ValueError(
                    f"passage {passage.id!r} names unknown citation ids: {sorted(unknown)!r}"
                )
            cited_sources = {
                citation.source_id
                for citation in self.citations
                if citation.id in passage.citation_ids
            }
            if passage.source_id not in cited_sources:
                raise ValueError(
                    f"passage {passage.id!r} must cite its own source_id {passage.source_id!r}"
                )

        statement_groups = (
            self.known_facts,
            self.prior_experiments,
            self.negative_results,
            self.contradictions,
            self.open_questions,
        )
        for statements in statement_groups:
            for statement in statements:
                unknown = set(statement.citation_ids) - known_citations
                if unknown:
                    raise ValueError(
                        "an evidence statement names unknown citation ids: "
                        f"{sorted(unknown)!r}"
                    )
        return self


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
    "RetrievalAdapter",
    "SCHEMA_EVIDENCE_BUNDLE_V1",
    "SourceClass",
    "canonical_json",
    "canonical_json_bytes",
    "sha256_digest",
]
