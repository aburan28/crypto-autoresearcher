"""The retrieval contract, plus the internal pipeline types.

Phase 0 of the plan: the agent-facing interface is defined here, before any
ingestion code, and everything downstream is written to satisfy it. The MCP
server adds no fields of its own -- it serialises these models.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --------------------------------------------------------------------------
# Controlled vocabularies
# --------------------------------------------------------------------------


class SourceType(str, Enum):
    """What kind of document this is. Mirrors the S3 source/ prefixes."""

    PAPER = "paper"
    INTERNAL_NOTE = "internal-note"
    EXPERIMENT = "experiment"
    PROOF = "proof"
    LEDGER = "ledger"
    REPOSITORY_DOC = "repository-doc"


class ClaimStatus(str, Enum):
    """How much the program itself stands behind the content."""

    EXTERNAL_SOURCE = "external-source"
    PUBLISHED = "published"
    SUPPORTED = "supported"
    REPRODUCED = "reproduced"
    WEAKENED = "weakened"
    REJECTED_SCOPED = "rejected-scoped"
    INCONCLUSIVE = "inconclusive"
    HYPOTHESIS = "hypothesis"


class EvidenceLevel(str, Enum):
    """Strength of the empirical backing, where there is any."""

    MACHINE_CHECKED = "machine-checked"
    INDEPENDENTLY_REPRODUCED = "independently-reproduced"
    REPLICATED = "replicated"
    SINGLE_RUN = "single-run"
    ANALYTICAL = "analytical"
    NONE = "none"


class Authority(str, Enum):
    """Provenance rank (plan Phase 13), highest first in ``AUTHORITY_ORDER``."""

    MACHINE_CHECKED_PROOF = "machine-checked-proof"
    REPRODUCED_EXPERIMENT = "reproduced-experiment"
    SINGLE_RUN_EXPERIMENT = "single-run-experiment"
    PEER_REVIEWED = "peer-reviewed-source"
    PREPRINT = "unreviewed-preprint"
    INTERNAL_ANALYSIS = "internal-analysis"
    AGENT_HYPOTHESIS = "agent-hypothesis"
    PRIMARY_SOURCE = "primary-source"


#: Descending authority. ``PRIMARY_SOURCE`` is an authorship claim rather than
#: a verification claim, so it is ranked with unreviewed material: being the
#: original author of a statement says nothing about whether it was checked.
AUTHORITY_ORDER: tuple[Authority, ...] = (
    Authority.MACHINE_CHECKED_PROOF,
    Authority.REPRODUCED_EXPERIMENT,
    Authority.SINGLE_RUN_EXPERIMENT,
    Authority.PEER_REVIEWED,
    Authority.PREPRINT,
    Authority.PRIMARY_SOURCE,
    Authority.INTERNAL_ANALYSIS,
    Authority.AGENT_HYPOTHESIS,
)

_AUTHORITY_RANK: dict[str, int] = {a.value: i for i, a in enumerate(AUTHORITY_ORDER)}


def authority_rank(authority: str | Authority | None) -> int:
    """Sort key: lower is more authoritative. Unknown values sort last."""
    if authority is None:
        return len(AUTHORITY_ORDER)
    key = authority.value if isinstance(authority, Authority) else str(authority)
    return _AUTHORITY_RANK.get(key, len(AUTHORITY_ORDER))


class ProvenanceClass(str, Enum):
    """Who asserted a metadata field.

    The plan is explicit that models must not silently mint authoritative
    metadata. Every field group carries the class of its author, and the
    ingestion pipeline refuses to promote ``model-suggested`` values into
    fields that filtering depends on.
    """

    DETERMINISTIC = "deterministic"
    HUMAN_AUTHORED = "human-authored"
    MODEL_SUGGESTED = "model-suggested"


class IngestState(str, Enum):
    """Ingestion state machine (plan Phase 3). Ordered."""

    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    PARSED = "PARSED"
    NORMALIZED = "NORMALIZED"
    CHUNKED = "CHUNKED"
    EMBEDDED = "EMBEDDED"
    INDEXED = "INDEXED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


INGEST_ORDER: tuple[IngestState, ...] = (
    IngestState.DISCOVERED,
    IngestState.DOWNLOADED,
    IngestState.PARSED,
    IngestState.NORMALIZED,
    IngestState.CHUNKED,
    IngestState.EMBEDDED,
    IngestState.INDEXED,
)


# --------------------------------------------------------------------------
# Source metadata (the S3 sidecar)
# --------------------------------------------------------------------------


class SourceMetadata(BaseModel):
    """Sidecar metadata for one source object.

    Written by hand or derived deterministically from repository records --
    never generated freely by a model. Unknown keys are rejected so a typo in
    a sidecar surfaces at ingest rather than silently disabling a filter.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    source_id: str
    title: str
    source_type: SourceType

    authors: list[str] = Field(default_factory=list)
    publication_year: int | None = None
    publication_status: str | None = None

    primitive: list[str] = Field(default_factory=list)
    field_type: list[str] = Field(default_factory=list)
    curves: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)

    claim_status: ClaimStatus = ClaimStatus.EXTERNAL_SOURCE
    evidence_level: EvidenceLevel | None = None
    authority: Authority | None = None

    superseded: bool = False
    superseded_by: str | None = None
    supersedes: list[str] = Field(default_factory=list)

    experiment_id: str | None = None
    related_experiments: list[str] = Field(default_factory=list)
    run_ids: list[str] = Field(default_factory=list)
    git_commit: str | None = None
    verification_artifacts: list[str] = Field(default_factory=list)

    source_url: str | None = None
    provenance_class: ProvenanceClass = ProvenanceClass.HUMAN_AUTHORED

    @field_validator("source_id")
    @classmethod
    def _source_id_is_namespaced(cls, value: str) -> str:
        if ":" not in value:
            raise ValueError(
                f"source_id must be namespaced as '<kind>:<identifier>', got {value!r}"
            )
        return value

    def payload_fields(self) -> dict[str, Any]:
        """The subset copied onto every chunk payload for filtering."""
        return {
            "source_id": self.source_id,
            "title": self.title,
            "source_type": self.source_type.value,
            "authors": self.authors,
            "publication_year": self.publication_year,
            "primitive": self.primitive,
            "field_type": self.field_type,
            "curves": self.curves,
            "topics": self.topics,
            "claim_status": self.claim_status.value,
            "evidence_level": self.evidence_level.value if self.evidence_level else None,
            "authority": self.authority.value if self.authority else None,
            "superseded": self.superseded,
            "superseded_by": self.superseded_by,
            "experiment_id": self.experiment_id,
            "run_ids": self.run_ids,
            "git_commit": self.git_commit,
            "source_url": self.source_url,
        }


# --------------------------------------------------------------------------
# Parsing and chunking
# --------------------------------------------------------------------------


class ParsedDocument(BaseModel):
    """Output of a parser: normalized markdown plus optional structure."""

    model_config = ConfigDict(extra="forbid")

    markdown: str
    structured: dict[str, Any] | None = None
    parser: str
    parser_version: str
    page_count: int | None = None
    #: Non-fatal problems found by parsing/validation.py. Carried forward onto
    #: the manifest so a bad conversion is visible without re-parsing.
    warnings: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    """A retrievable passage, or (when ``is_parent``) a context-expansion unit."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    source_id: str
    chunk_index: int
    text: str
    content_hash: str

    #: The chunk's own address: the deepest heading path that covers all of
    #: it. When a chunk spans sections this is their common ancestor, so it
    #: never claims to come from a section it only partly covers.
    section_path: list[str] = Field(default_factory=list)
    #: Every heading path the chunk actually covers, in order. This is what a
    #: table of contents is built from -- ``section_path`` alone loses the
    #: headings whenever short sections merge.
    section_headings: list[str] = Field(default_factory=list)
    parent_id: str | None = None
    is_parent: bool = False
    token_count: int = 0
    page_start: int | None = None
    page_end: int | None = None
    #: Set when the chunk contains a block that must not be split (theorem,
    #: proof, algorithm, result table...). Used by the chunker's size relaxation
    #: and surfaced so a reader can tell a long chunk from a runaway one.
    atomic_blocks: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Retrieval contract
# --------------------------------------------------------------------------


class SearchFilters(BaseModel):
    """Validated filter set.

    Deliberately a closed vocabulary of fields rather than a pass-through of
    Qdrant filter expressions: the MCP server is exposed to agents, and an
    arbitrary-expression surface is both an injection risk and an unbounded
    query-cost risk.
    """

    model_config = ConfigDict(extra="forbid")

    source_id: list[str] | None = None
    source_type: list[SourceType] | None = None
    primitive: list[str] | None = None
    field_type: list[str] | None = None
    curves: list[str] | None = None
    topics: list[str] | None = None
    claim_status: list[ClaimStatus] | None = None
    evidence_level: list[EvidenceLevel] | None = None
    experiment_id: list[str] | None = None
    git_commit: list[str] | None = None
    publication_year_min: int | None = None
    publication_year_max: int | None = None
    #: Default excludes superseded material from retrieval without deleting it
    #: (plan Phase 13). Set to None to include superseded chunks explicitly.
    superseded: bool | None = False
    #: Minimum authority, by name; results ranked below it are excluded.
    min_authority: Authority | None = None

    def is_empty(self) -> bool:
        return all(
            value is None
            for name, value in self.model_dump().items()
            if name != "superseded"
        ) and self.superseded is None


class SearchResult(BaseModel):
    """One retrieved passage. Every field the agent needs to cite it."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    source_id: str
    title: str
    text: str
    section_path: list[str] = Field(default_factory=list)
    #: Every heading path the passage covers. Populated even when
    #: ``section_path`` is empty because the passage spans sections with no
    #: common ancestor -- "(no section)" would otherwise misdescribe it.
    section_headings: list[str] = Field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
    score: float
    source_uri: str
    source_type: str
    claim_status: str | None = None
    evidence_level: str | None = None
    authority: str | None = None
    field_type: list[str] = Field(default_factory=list)
    primitive: list[str] = Field(default_factory=list)
    superseded: bool = False
    experiment_id: str | None = None
    run_ids: list[str] = Field(default_factory=list)
    git_commit: str | None = None
    content_hash: str
    parent_id: str | None = None


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    results: list[SearchResult] = Field(default_factory=list)
    total_candidates: int = 0
    filters_applied: dict[str, Any] = Field(default_factory=dict)
    query_id: str | None = None
    latency_ms: int | None = None
    #: Set when the answer is shaped by a limit the caller did not ask for --
    #: diversification caps, top_k clamping, an unavailable reranker. Silent
    #: truncation reads as complete coverage; this is how it stays visible.
    notes: list[str] = Field(default_factory=list)


class ContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    source_id: str
    title: str
    section_path: list[str] = Field(default_factory=list)
    before: list[SearchResult] = Field(default_factory=list)
    chunk: SearchResult | None = None
    after: list[SearchResult] = Field(default_factory=list)
    parent_text: str | None = None
    notes: list[str] = Field(default_factory=list)


class SourceDocument(BaseModel):
    """Bounded description of a source.

    Never the full document: the point of the index is to stop agents pulling
    whole papers into context. Callers who need the bytes get ``source_uri``.
    """

    model_config = ConfigDict(extra="forbid")

    source_id: str
    title: str
    source_type: str
    source_uri: str
    authors: list[str] = Field(default_factory=list)
    publication_year: int | None = None
    claim_status: str | None = None
    evidence_level: str | None = None
    authority: str | None = None
    superseded: bool = False
    superseded_by: str | None = None
    experiment_id: str | None = None
    run_ids: list[str] = Field(default_factory=list)
    git_commit: str | None = None
    topics: list[str] = Field(default_factory=list)
    primitive: list[str] = Field(default_factory=list)
    field_type: list[str] = Field(default_factory=list)
    table_of_contents: list[str] = Field(default_factory=list)
    chunk_count: int = 0
    summary: str | None = None
    content_hash: str | None = None
    indexed_at: str | None = None


# --------------------------------------------------------------------------
# Manifests
# --------------------------------------------------------------------------


class Manifest(BaseModel):
    """Per-document ingestion record. The pipeline's only durable memory."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    s3_bucket: str | None = None
    s3_key: str
    s3_version_id: str | None = None
    etag: str | None = None
    source_sha256: str
    metadata_hash: str
    document_fingerprint: str

    parser: str | None = None
    parser_version: str | None = None
    chunker_version: str | None = None
    dense_model: str | None = None
    sparse_model: str | None = None
    collection: str | None = None

    status: IngestState = IngestState.DISCOVERED
    chunk_count: int = 0
    parent_chunk_count: int = 0
    point_ids: list[str] = Field(default_factory=list)
    #: This document's contribution to the corpus-wide sparse statistics, kept
    #: here so replacing or deleting it can retract exactly what it added.
    sparse_terms: list[str] = Field(default_factory=list)
    sparse_mean_length: int = 0
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    indexed_at: str | None = None
    updated_at: str = Field(default_factory=lambda: utcnow())

    def touch(self) -> None:
        self.updated_at = utcnow()


def utcnow() -> str:
    """RFC3339 UTC timestamp, second resolution."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------
# Claims (plan Phase 13)
# --------------------------------------------------------------------------


class Claim(BaseModel):
    """An explicit, citable assertion with its verification trail."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str
    statement: str
    claim_status: ClaimStatus
    authority: Authority
    source_ids: list[str] = Field(default_factory=list)
    superseded: bool = False
    superseded_by: str | None = None
    verification_artifacts: list[str] = Field(default_factory=list)
    #: Scope is not optional in this program: a conclusion is only ever about
    #: the curves, parameters, solver, and budget it was tested at.
    boundaries: list[str] = Field(default_factory=list)
