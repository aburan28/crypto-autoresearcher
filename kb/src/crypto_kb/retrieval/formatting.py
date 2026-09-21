"""Payload -> SearchResult, and human-readable rendering for the CLI."""

from __future__ import annotations

from typing import Any

from crypto_kb.models import SearchResponse, SearchResult


def to_result(hit: dict[str, Any], max_chars: int | None = None) -> SearchResult:
    payload = hit.get("payload", {}) or {}
    text = payload.get("text", "") or ""
    if max_chars and len(text) > max_chars:
        # Truncation is marked in the text itself: a passage that silently
        # ends mid-sentence reads as the source ending there.
        text = text[:max_chars].rstrip() + "\n[... passage truncated; fetch the source for the rest]"
    return SearchResult(
        chunk_id=payload.get("chunk_id", ""),
        source_id=payload.get("source_id", ""),
        title=payload.get("title", ""),
        text=text,
        section_path=list(payload.get("section_path") or []),
        section_headings=list(payload.get("section_headings") or []),
        page_start=payload.get("page_start"),
        page_end=payload.get("page_end"),
        score=float(hit.get("score", 0.0)),
        source_uri=payload.get("source_uri", ""),
        source_type=payload.get("source_type", ""),
        claim_status=payload.get("claim_status"),
        evidence_level=payload.get("evidence_level"),
        authority=payload.get("authority"),
        field_type=list(payload.get("field_type") or []),
        primitive=list(payload.get("primitive") or []),
        superseded=bool(payload.get("superseded", False)),
        supersedes=list(payload.get("supersedes") or []),
        verification_artifacts=list(payload.get("verification_artifacts") or []),
        experiment_id=payload.get("experiment_id"),
        run_ids=list(payload.get("run_ids") or []),
        git_commit=payload.get("git_commit"),
        content_hash=payload.get("content_hash", ""),
        parent_id=payload.get("parent_id"),
    )


def render(response: SearchResponse, show_text: bool = True, width: int = 100) -> str:
    """Plain-text rendering for `crypto-kb search`."""
    lines: list[str] = []
    header = f'query: {response.query!r}  ({len(response.results)} of {response.total_candidates} candidates'
    if response.latency_ms is not None:
        header += f", {response.latency_ms} ms"
    lines.append(header + ")")
    if response.filters_applied:
        lines.append(f"filters: {response.filters_applied}")
    for note in response.notes:
        lines.append(f"note: {note}")
    lines.append("")

    for position, result in enumerate(response.results, start=1):
        location = (
            " > ".join(result.section_path)
            or " | ".join(result.section_headings)
            or "(no section)"
        )
        pages = ""
        if result.page_start is not None:
            pages = f" p.{result.page_start}" + (
                f"-{result.page_end}" if result.page_end and result.page_end != result.page_start else ""
            )
        provenance = " | ".join(
            part
            for part in (
                result.source_type,
                result.claim_status,
                result.evidence_level,
                result.authority,
                "SUPERSEDED" if result.superseded else None,
            )
            if part
        )
        lines.append(f"[{position}] {result.score:.3f}  {result.source_id}  {result.title}")
        lines.append(f"     {location}{pages}")
        lines.append(f"     {provenance}")
        if result.experiment_id or result.run_ids:
            lines.append(f"     experiment={result.experiment_id} runs={','.join(result.run_ids) or '-'}")
        if result.supersedes:
            lines.append(f"     supersedes={','.join(result.supersedes)}")
        for artifact in result.verification_artifacts:
            lines.append(f"     verification={artifact}")
        lines.append(f"     {result.source_uri}")
        lines.append(f"     chunk_id={result.chunk_id}")
        if show_text:
            lines.append("")
            for paragraph in result.text.strip().splitlines():
                lines.extend(_wrap(paragraph, width, indent="     "))
        lines.append("")
    return "\n".join(lines)


def _wrap(text: str, width: int, indent: str) -> list[str]:
    import textwrap

    if not text.strip():
        return [""]
    return textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent) or [""]
