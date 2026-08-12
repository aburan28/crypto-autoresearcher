"""Result diversification.

Without it, a hybrid search over a corpus containing one long survey returns
six passages from that survey and reports the field as unanimous. Diversity
caps are a correctness measure here, not a presentation preference: an agent
asked to report contradictory sources cannot find them if one document
monopolises the result list.

Dropped-but-eligible results are counted so the caller can say how much was
withheld rather than implying the corpus had nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass

from crypto_kb.models import SearchResult


@dataclass
class DiversityCaps:
    max_per_source: int = 2
    max_per_parent: int = 3
    max_results: int = 8


def diversify(
    results: list[SearchResult], caps: DiversityCaps, top_k: int
) -> tuple[list[SearchResult], int]:
    """Apply per-source and per-parent caps. Returns (kept, suppressed count)."""
    per_source: dict[str, int] = {}
    per_parent: dict[str, int] = {}
    kept: list[SearchResult] = []
    suppressed = 0
    limit = min(top_k, caps.max_results)

    for result in results:
        if len(kept) >= limit:
            break
        source_count = per_source.get(result.source_id, 0)
        parent_key = result.parent_id or f"{result.source_id}::no-parent"
        parent_count = per_parent.get(parent_key, 0)
        if source_count >= caps.max_per_source or parent_count >= caps.max_per_parent:
            suppressed += 1
            continue
        per_source[result.source_id] = source_count + 1
        per_parent[parent_key] = parent_count + 1
        kept.append(result)

    return kept, suppressed


def deduplicate(results: list[SearchResult]) -> tuple[list[SearchResult], int]:
    """Drop chunks with identical content.

    Overlap between neighbouring chunks and near-duplicate documents (a note
    and the record it was promoted from) otherwise spend the result budget
    saying the same thing twice.
    """
    seen: set[str] = set()
    kept: list[SearchResult] = []
    dropped = 0
    for result in results:
        key = result.content_hash or result.chunk_id
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        kept.append(result)
    return kept, dropped
