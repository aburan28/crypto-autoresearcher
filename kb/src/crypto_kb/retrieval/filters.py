"""Translate the validated filter model into a Qdrant filter.

Agents never supply filter expressions -- only values for named fields. That
is the whole security posture of the read path: an arbitrary expression
surface on an agent-facing server is both an injection vector and an unbounded
query-cost vector, and a closed vocabulary costs nothing to maintain because
the fields are the same ones the payload indexes cover.
"""

from __future__ import annotations

from typing import Any

from crypto_kb.index.schema import PAYLOAD_INDEXES
from crypto_kb.models import AUTHORITY_ORDER, Authority, SearchFilters, authority_rank


def _models():
    from crypto_kb.index.qdrant import _models as loader

    return loader()


def authorities_at_least(minimum: Authority) -> list[str]:
    """Authority values ranked at or above ``minimum``."""
    limit = authority_rank(minimum)
    return [a.value for a in AUTHORITY_ORDER if authority_rank(a) <= limit]


def build_filter(
    filters: SearchFilters | None,
    *,
    include_parents: bool = False,
    exclude_source_ids: list[str] | None = None,
    parent_ids: list[str] | None = None,
    identity_tokens: list[str] | None = None,
) -> Any | None:
    """Build the Qdrant filter for a search.

    ``include_parents`` is False for search and True for context expansion:
    parent chunks are 3,000-token context units and returning them as search
    results would blow the caller's budget and duplicate their own children.
    """
    models = _models()
    must: list[Any] = []
    must_not: list[Any] = []

    if not include_parents:
        must.append(models.FieldCondition(key="is_parent", match=models.MatchValue(value=False)))

    if parent_ids:
        must.append(models.FieldCondition(key="parent_id", match=models.MatchAny(any=parent_ids)))

    if identity_tokens:
        must.append(
            models.FieldCondition(
                key="identity_tokens", match=models.MatchAny(any=identity_tokens)
            )
        )

    for source_id in exclude_source_ids or []:
        must_not.append(
            models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id))
        )

    if filters is not None:
        must.extend(_field_conditions(models, filters))
        if filters.superseded is not None:
            # Superseded material is excluded by default and never deleted, so
            # a retracted conclusion stays auditable without answering queries.
            must.append(
                models.FieldCondition(
                    key="superseded", match=models.MatchValue(value=filters.superseded)
                )
            )
        if filters.min_authority is not None:
            must.append(
                models.FieldCondition(
                    key="authority",
                    match=models.MatchAny(any=authorities_at_least(filters.min_authority)),
                )
            )
        if filters.publication_year_min is not None or filters.publication_year_max is not None:
            must.append(
                models.FieldCondition(
                    key="publication_year",
                    range=models.Range(
                        gte=filters.publication_year_min, lte=filters.publication_year_max
                    ),
                )
            )

    if not must and not must_not:
        return None
    return models.Filter(must=must or None, must_not=must_not or None)


#: SearchFilters field -> payload field. Every entry must be a payload index.
_LIST_FIELDS: dict[str, str] = {
    "source_id": "source_id",
    "source_type": "source_type",
    "primitive": "primitive",
    "field_type": "field_type",
    "curves": "curves",
    "topics": "topics",
    "claim_status": "claim_status",
    "evidence_level": "evidence_level",
    "experiment_id": "experiment_id",
    "git_commit": "git_commit",
}

_UNINDEXED = sorted(set(_LIST_FIELDS.values()) - set(PAYLOAD_INDEXES))
if _UNINDEXED:  # pragma: no cover - guards a schema/filter drift at import time
    raise RuntimeError(f"filter fields without a payload index: {_UNINDEXED}")


def _field_conditions(models, filters: SearchFilters) -> list[Any]:
    conditions: list[Any] = []
    for attribute, payload_field in _LIST_FIELDS.items():
        values = getattr(filters, attribute)
        if not values:
            continue
        normalized = [v.value if hasattr(v, "value") else str(v) for v in values]
        conditions.append(
            models.FieldCondition(key=payload_field, match=models.MatchAny(any=normalized))
        )
    return conditions


def describe(filters: SearchFilters | None) -> dict[str, Any]:
    """The filter as applied, for the response and the query log."""
    if filters is None:
        return {}
    dumped = filters.model_dump(mode="json", exclude_none=True)
    return dumped
