"""Sidecar metadata: loading, validation, and provenance discipline.

Two rules the plan is explicit about, enforced here rather than by convention:

1. Metadata is not generated freely by a model. A sidecar declares its
   ``provenance_class``; anything marked ``model-suggested`` may only carry
   soft fields (``topics``), and its authoritative fields are dropped with a
   warning rather than silently indexed.
2. Authority and evidence level are derived from the source's directory and
   records when they are not stated, so an un-annotated document never
   inherits a stronger claim than its provenance supports.
"""

from __future__ import annotations

import json
from typing import Any

from crypto_kb.hashing import hash_metadata
from crypto_kb.models import (
    Authority,
    ClaimStatus,
    EvidenceLevel,
    ProvenanceClass,
    SourceMetadata,
    SourceType,
)
from crypto_kb.storage.base import ObjectStore

METADATA_SUFFIX = ".metadata.json"

#: Fields a model-suggested sidecar is not permitted to set. These drive
#: filtering and citation, so a wrong value is worse than a missing one.
AUTHORITATIVE_FIELDS = frozenset(
    {
        "claim_status",
        "evidence_level",
        "authority",
        "superseded",
        "superseded_by",
        "supersedes",
        "experiment_id",
        "related_experiments",
        "run_ids",
        "git_commit",
        "verification_artifacts",
        "publication_year",
        "authors",
    }
)

#: Default authority when a sidecar leaves it unset, by source type. Chosen
#: conservatively: an unannotated internal note is analysis, not evidence.
_DEFAULT_AUTHORITY: dict[SourceType, Authority] = {
    SourceType.PAPER: Authority.PREPRINT,
    SourceType.PROOF: Authority.MACHINE_CHECKED_PROOF,
    SourceType.EXPERIMENT: Authority.SINGLE_RUN_EXPERIMENT,
    SourceType.LEDGER: Authority.INTERNAL_ANALYSIS,
    SourceType.INTERNAL_NOTE: Authority.INTERNAL_ANALYSIS,
    SourceType.REPOSITORY_DOC: Authority.INTERNAL_ANALYSIS,
}

#: Evidence level implies authority for experiment-like sources; a reproduced
#: run outranks a single run regardless of what the sidecar guessed.
_EVIDENCE_AUTHORITY: dict[EvidenceLevel, Authority] = {
    EvidenceLevel.MACHINE_CHECKED: Authority.MACHINE_CHECKED_PROOF,
    EvidenceLevel.INDEPENDENTLY_REPRODUCED: Authority.REPRODUCED_EXPERIMENT,
    EvidenceLevel.REPLICATED: Authority.REPRODUCED_EXPERIMENT,
    EvidenceLevel.SINGLE_RUN: Authority.SINGLE_RUN_EXPERIMENT,
}


class MetadataError(ValueError):
    """A sidecar that cannot be trusted. The object is rejected, not guessed at."""


def metadata_key(source_key: str) -> str:
    return source_key + METADATA_SUFFIX


def is_metadata_key(key: str) -> bool:
    return key.endswith(METADATA_SUFFIX)


def load_metadata(store: ObjectStore, source_key: str) -> tuple[SourceMetadata, list[str]]:
    """Load and normalize the sidecar for ``source_key``.

    Returns the metadata and any warnings raised while normalizing it.
    """
    key = metadata_key(source_key)
    if not store.exists(key):
        raise MetadataError(
            f"no sidecar at {key}; every object under source/ needs one "
            "(the pipeline does not invent metadata)"
        )
    try:
        raw = json.loads(store.get(key).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataError(f"{key} is not valid JSON: {exc}") from exc
    return normalize(raw, origin=key)


def normalize(raw: dict[str, Any], origin: str = "<inline>") -> tuple[SourceMetadata, list[str]]:
    """Validate a raw sidecar mapping and apply provenance rules."""
    warnings: list[str] = []
    data = dict(raw)

    provenance = data.get("provenance_class", ProvenanceClass.HUMAN_AUTHORED.value)
    if provenance == ProvenanceClass.MODEL_SUGGESTED.value:
        stripped = sorted(AUTHORITATIVE_FIELDS & set(data))
        for name in stripped:
            data.pop(name)
        if stripped:
            warnings.append(
                f"{origin}: dropped model-suggested authoritative fields {stripped}; "
                "these require a human-authored or deterministic sidecar"
            )

    try:
        metadata = SourceMetadata.model_validate(data)
    except Exception as exc:
        raise MetadataError(f"{origin}: invalid sidecar: {exc}") from exc

    resolved, resolution_warnings = resolve_authority(metadata)
    warnings.extend(f"{origin}: {w}" for w in resolution_warnings)
    return resolved, warnings


def resolve_authority(metadata: SourceMetadata) -> tuple[SourceMetadata, list[str]]:
    """Fill in ``authority`` and reconcile it with ``evidence_level``."""
    warnings: list[str] = []
    values = metadata.model_dump()

    evidence = metadata.evidence_level
    implied = _EVIDENCE_AUTHORITY.get(evidence) if evidence else None

    if metadata.authority is None:
        values["authority"] = (implied or _DEFAULT_AUTHORITY[metadata.source_type]).value
    elif implied is not None and metadata.authority != implied:
        # The evidence level is a statement about what was actually verified;
        # the authority label is a summary of it. When they disagree, the
        # verified fact wins and the disagreement is reported.
        warnings.append(
            f"authority {metadata.authority.value!r} disagrees with evidence_level "
            f"{evidence.value!r}; using {implied.value!r}"
        )
        values["authority"] = implied.value

    if metadata.superseded_by and not metadata.superseded:
        warnings.append("superseded_by is set but superseded is false; treating as superseded")
        values["superseded"] = True

    if metadata.source_type == SourceType.PAPER and metadata.claim_status not in {
        ClaimStatus.EXTERNAL_SOURCE,
        ClaimStatus.PUBLISHED,
    }:
        # An external paper's status describes publication, not this program's
        # verification of it. Internal claim statuses on a paper would let a
        # `claim_status=reproduced` filter return work we never reproduced.
        warnings.append(
            f"claim_status {metadata.claim_status.value!r} is an internal status on an "
            "external paper; recording as 'external-source'"
        )
        values["claim_status"] = ClaimStatus.EXTERNAL_SOURCE.value

    return SourceMetadata.model_validate(values), warnings


def metadata_fingerprint(metadata: SourceMetadata) -> str:
    """Hash of the metadata as it will be indexed.

    Computed from the resolved model, not the raw sidecar, so that a cosmetic
    edit that normalizes to the same values does not force a re-index -- while
    any change that would alter a payload does.
    """
    return hash_metadata(metadata.model_dump(mode="json"))
