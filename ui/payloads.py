"""The data contract, built once and served two ways.

Every payload the browser reads is produced here. `ui/server.py` computes
them on demand from a live index; `ui/build.py` writes the identical bytes
to files for GitHub Pages. That is the whole reason this module exists
separately from either: a static site and a local server that disagree
about their own data are two products, and the second one is always the
broken one.

The shape is deliberately file-shaped rather than query-shaped -- no
endpoint takes a filter -- because a static host cannot answer a query.
Filtering, sorting and search all happen in the browser over
`data/index.json`, which is ~0.8 MB gzipped and therefore cheap to hold in
full. The live server serves the same files from memory, so the local
dashboard is exactly the static site with a fresher index.
"""

from __future__ import annotations

from typing import Any

from .index import KIND_LABELS, KIND_ORDER, TERMINAL_GOAL_STATUSES, ResearchIndex

# `data/index.json` rows are positional, not objects. At 14.6k records the
# repeated key names cost more than the values do: as objects the file is
# 2.6 MB, as rows 1.4 MB. The client names them once, in `rowToRecord`.
INDEX_COLUMNS = ["id", "kind", "status", "title", "date", "area", "ecc", "backlinks"]

# Titles are for scanning a list, not for reading. Anything longer is body
# text and belongs in the record, not in an index every visitor downloads.
INDEX_TITLE_CHARS = 300


def index_rows(index: ResearchIndex) -> list[list]:
    return [
        [
            record.record_id,
            record.kind,
            record.status,
            record.title[:INDEX_TITLE_CHARS],
            record.date,
            record.area or "",
            1 if (record.area and record.area in index.ecc_areas) else 0,
            len(index.backlinks.get(record.record_id, ())),
        ]
        for record in index.records.values()
    ]


def meta_payload(index: ResearchIndex, *, mode: str, commit: str | None = None,
                 repo_url: str | None = None, built_at: str | None = None) -> dict[str, Any]:
    """What the reader is looking at, and how stale it is.

    A static site is a SNAPSHOT and must say so: `commit` and `built_at`
    are what let a reader tell whether the page reflects the ledger they
    are working in. A live server sets `mode: "live"` and omits them.
    """
    return {
        "mode": mode,
        "commit": commit,
        "repo_url": repo_url,
        "built_at": built_at,
        "records": len(index.records),
        "goals": len(index.goals),
        "experiments": len(index.experiments),
        "runs": sum(len(e.runs) for e in index.experiments),
        "columns": INDEX_COLUMNS,
        "kind_order": KIND_ORDER,
        "kind_labels": KIND_LABELS,
        "ecc_areas": sorted(index.ecc_areas),
        "ecc_policy_error": index.ecc_error,
        "facets": index.facets(),
    }


def goal_payload(index: ResearchIndex, goal, detail: bool = False) -> dict[str, Any]:
    payload = {
        "id": goal.record_id,
        "title": goal.title,
        "status": goal.status,
        "area": goal.area,
        "ecc": goal.ecc,
        "owner": goal.owner,
        "path": goal.path,
        "sharded": goal.sharded,
        "current_batch_id": goal.current_batch_id,
        "updated_at": goal.updated_at,
        "created_at": goal.created_at,
        "question_ids": goal.question_ids,
        "active_hypothesis_ids": goal.active_hypothesis_ids,
        "budget": goal.budget,
        "batches": len(goal.checkpoints),
        "impediment_count": len(goal.impediments),
        "flags": goal.flags,
        "terminal": goal.status in TERMINAL_GOAL_STATUSES,
        "next_action_preview": goal.next_action[:260],
    }
    if detail:
        payload |= {
            "objective": goal.objective,
            "next_action": goal.next_action,
            "completion_criteria": goal.completion_criteria,
            "impediments": goal.impediments,
            "checkpoints": goal.checkpoints,
            # Identifiers only. The browser already holds every summary in
            # `data/index.json`, so embedding them again multiplied the
            # detail files by a factor of about three for nothing.
            "mentions": sorted(index.backlinks.get(goal.record_id, ())),
        }
    return payload


def overview_payload(index: ResearchIndex) -> dict[str, Any]:
    goals = index.goals
    active = [g for g in goals if g.status == "active"]

    by_status: dict[str, int] = {}
    for goal in goals:
        key = goal.status or "(unstated)"
        by_status[key] = by_status.get(key, 0) + 1

    hypothesis_status: dict[str, int] = {}
    for record in index.by_kind.get("H", []):
        key = record.status or "(unstated)"
        hypothesis_status[key] = hypothesis_status.get(key, 0) + 1

    run_status: dict[str, int] = {}
    for experiment in index.experiments:
        for run in experiment.runs:
            run_status[run["status"]] = run_status.get(run["status"], 0) + 1

    recent = sorted(
        (r for r in index.records.values()
         if r.date and r.kind in ("DEC", "EV", "TASK", "CORR")),
        key=lambda r: r.date, reverse=True)[:40]

    return {
        "counts": [
            {"key": k, "label": KIND_LABELS[k], "count": len(index.by_kind.get(k, []))}
            for k in KIND_ORDER],
        "goals": {
            "total": len(goals),
            "active": len(active),
            "ecc_active": len([g for g in active if g.ecc]),
            "terminal": len([g for g in goals if g.status in TERMINAL_GOAL_STATUSES]),
            "by_status": by_status,
        },
        "hypothesis_status": hypothesis_status,
        "run_status": run_status,
        "experiments": {
            "total": len(index.experiments),
            "with_runs": len([e for e in index.experiments if e.runs]),
            "runs": sum(len(e.runs) for e in index.experiments),
        },
        "ecc_first": [goal_payload(index, g) for g in active if g.ecc][:12],
        "attention": [goal_payload(index, g) for g in goals if g.flags or g.impediments][:12],
        "recent": [r.record_id for r in recent],
        "integrity_totals": integrity_totals(index),
    }


def integrity_totals(index: ResearchIndex) -> dict[str, Any]:
    return {
        "unparseable": len(index.integrity.get("unparseable", [])),
        "unparseable_state": index.integrity.get("unparseable_state"),
        "duplicate_ids": len(index.integrity.get("duplicate_ids", [])),
        "id_path_mismatch": len(index.integrity.get("id_path_mismatch", [])),
        "dangling_refs": index.integrity.get("dangling_refs_total", 0),
        "goal_flags": len(index.integrity.get("goal_flags", [])),
    }


def goals_payload(index: ResearchIndex) -> dict[str, Any]:
    return {"goals": [goal_payload(index, g) for g in index.goals]}


def experiments_payload(index: ResearchIndex) -> dict[str, Any]:
    return {"experiments": [
        {
            "id": e.record_id, "title": e.title, "status": e.status, "area": e.area,
            "path": e.path, "hypothesis_id": e.hypothesis_id, "question_id": e.question_id,
            "frozen": e.frozen, "execution_authorized": e.execution_authorized,
            "runs": e.runs, "run_count": len(e.runs),
            "ecc": e.area in index.ecc_areas if e.area else False,
        }
        for e in index.experiments]}


def record_payload(index: ResearchIndex, record_id: str,
                   include_raw: bool = True) -> dict[str, Any] | None:
    record = index.records.get(record_id)
    if record is None:
        return None
    parsed, error = index.full_record(record_id)
    body = parsed
    if isinstance(parsed, dict) and len(parsed) == 1:
        body = next(iter(parsed.values()))
    payload = {
        "summary": record.summary(index),
        "root_key": record.root_key,
        # tier-2 flag from ui/scan.py: true means `body` came from a real
        # YAML parse, not from the header scan that drives the lists.
        "verified": error is None and parsed is not None,
        "parse_error": error,
        "body": jsonable(body),
        "links": {
            "out": sorted(r for r in record.refs if r in index.records),
            "in": sorted(index.backlinks.get(record_id, ())),
        },
    }
    if include_raw:
        # The live server inlines the source; the static build does not.
        # 116 MB of source text is not worth shipping when the same bytes
        # are one click away on GitHub at the exact commit that was built.
        payload["raw"] = index.raw_text(record_id)
    return payload


def search_shards(index: ResearchIndex, excerpt_chars: int = 1200) -> dict[str, dict]:
    """Per-kind body excerpts, for full-text search.

    Sharded by kind and fetched only when a reader actually searches bodies:
    the whole set is ~3.8 MB gzipped and two thirds of it is the literature
    corpus, which most searches do not need. Loading that up front would tax
    every visitor for a feature many never use.
    """
    shards: dict[str, dict] = {}
    for kind, records in index.by_kind.items():
        shards[kind] = {
            "kind": kind,
            "ids": [r.record_id for r in records],
            "text": [r.haystack[:excerpt_chars].decode("utf-8", "replace") for r in records],
            "excerpt_chars": excerpt_chars,
        }
    return shards


def jsonable(value: Any, depth: int = 0) -> Any:
    """Coerce a parsed record to JSON.

    YAML dates, tuples and non-string keys all appear in this corpus.
    Rather than dropping them they are stringified: a reader looking at a
    detail view should see every field the record has.
    """
    if depth > 24:
        return "…"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(v, depth + 1) for v in value]
    return str(value)
