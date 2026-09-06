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

from collections import Counter
from dataclasses import asdict
from datetime import date, datetime, timezone
from typing import Any

from .index import (KIND_LABELS, KIND_ORDER, TERMINAL_GOAL_STATUSES, Finding, OpenProblem,
                    ResearchIndex, _neg_date)
from .scan import RECORD_ID_RE, STRUCTURED, id_kind

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
        "findings": len(index.findings),
        "open_problems": len(index.open_problems),
        "git": git_status(index),
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

    evidence = evidence_rows(index)
    verdicts = hypothesis_verdicts(index)
    decisions = sorted(index.by_kind.get("DEC", []),
                       key=lambda r: (_neg_date(r.date), r.record_id))
    findings = [finding_summary(index, f) for f in index.findings]
    current = [f for f in findings if f["status"] == "current"]
    areas = directions(index, findings, verdicts, evidence)

    return {
        # What the program has established, for the reader who asks that
        # first. The full board is `findings.json`; this is its headline.
        "findings": {
            "total": len(findings),
            "current": len(current),
            "by_proof_status": _count(current, "proof_status"),
            "by_claim_tier": _count(current, "claim_tier"),
            "added_last_7_days": added_within(index, 7),
            "added_last_30_days": added_within(index, 30),
            "latest": current[:6],
        },
        # The program by research area. The full map (`findings.json`) sorts
        # ECC first; this panel answers "where did the results come from",
        # so it takes the dozen areas with most established.
        "directions": {
            "total": len(areas),
            "top": sorted(areas, key=lambda r: (
                -r["findings"], not r["ecc"], -r["active_goals"], r["area"]))[:12],
        },
        "open_problems": {
            "total": len(index.open_problems),
            "open": sum(1 for p in index.open_problems if p.status == "open"),
            "latest": [
                {"id": p.record_id, "title": p.title, "status": p.status, "added": p.added}
                for p in index.open_problems if p.status == "open"][:6],
        },
        "hypothesis_verdicts": _count(verdicts, "verdict"),
        "evidence_polarity": _count(evidence, "polarity"),
        "evidence_direction": _top_counts(evidence, "direction"),
        "decision_verdicts": _top_counts([{"decision": r.status} for r in decisions], "decision"),
        "recent_decisions": [r.record_id for r in decisions[:12]],
        "pipeline": pipeline_counts(index, evidence, verdicts),
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
    rows = []
    for e in index.experiments:
        first_run, last_run = e.run_span
        measured = [r["duration_seconds"] for r in e.runs if r.get("duration_seconds")]
        rows.append({
            "id": e.record_id, "title": e.title, "status": e.status, "area": e.area,
            "path": e.path, "hypothesis_id": e.hypothesis_id, "question_id": e.question_id,
            "frozen": e.frozen, "execution_authorized": e.execution_authorized,
            "contract": e.contract,
            "runs": e.runs, "run_count": len(e.runs),
            "ecc": e.area in index.ecc_areas if e.area else False,
            # Declared by the contract, under the name it used.
            "dated": e.dated, "date_field": e.date_field,
            # Observed by git. Never merged with the above.
            "committed": e.committed, "last_commit": e.last_commit,
            "first_run": first_run, "last_run": last_run,
            "runs_timed": sum(1 for r in e.runs if r.get("started")),
            "total_seconds": round(sum(measured), 3) if measured else None,
            "runs_measured": len(measured),
        })
    return {"experiments": rows, "timing": experiment_timing(index)}


def experiment_timing(index: ResearchIndex) -> dict[str, Any]:
    """What is actually known about when this program ran, stated exactly.

    Every number here is a count of records, not an estimate. The point of
    the block is that a reader can see the coverage of the timing beside the
    timing itself: 99 self-reported start times out of 2,313 runs is the
    real state of the corpus, and a page that showed only the 99 would imply
    the rest never happened.
    """
    runs = [r for e in index.experiments for r in e.runs]
    stamps = [t for r in runs for t in (r.get("started_epoch"), r.get("committed")) if t]
    measured = [r["duration_seconds"] for r in runs if r.get("duration_seconds")]
    return {
        "runs": len(runs),
        "runs_with_declared_start": sum(1 for r in runs if r.get("started")),
        "runs_with_declared_finish": sum(1 for r in runs if r.get("finished")),
        "runs_with_duration": len(measured),
        "runs_with_any_time": sum(1 for r in runs if r.get("started") or r.get("committed")),
        "total_measured_seconds": round(sum(measured), 3) if measured else None,
        "longest_run_seconds": max(measured) if measured else None,
        "earliest": min(stamps) if stamps else None,
        "latest": max(stamps) if stamps else None,
        "experiments": len(index.experiments),
        "experiments_with_runs": sum(1 for e in index.experiments if e.runs),
        "experiments_dated": sum(1 for e in index.experiments if e.dated),
        "experiments_without_contract": sum(1 for e in index.experiments if not e.contract),
        "experiments_json_contract": sum(
            1 for e in index.experiments if e.contract == "specification.json"),
        "git": git_status(index),
    }


def git_status(index: ResearchIndex) -> dict[str, Any]:
    """Whether commit dates are available, and if not, exactly why."""
    return {
        "available": index.git.available,
        "error": index.git.error,
        "paths": len(index.git.first),
        "commits": index.git.commits,
        "seconds": round(index.git.seconds, 2),
    }


# ---------------------------------------------------------------------------
# Findings: what the program has established, and what still stands against it.
#
# `data/findings.json` is one file because every part of it is small and a
# reader who opens the board wants all of it: the promoted findings, the
# hypotheses that reached a verdict, the evidence that points somewhere, the
# obstructions measured along the way, and the problems still open. Nothing
# here is computed by the browser that could not be checked against the
# records: every row carries the identifiers it was derived from.
# ---------------------------------------------------------------------------

# A hypothesis "verdict" is a status past the design stages. Longest first,
# because `supported_scoped` must not read as `supported`.
HYPOTHESIS_VERDICTS = (
    "supported_scoped", "supported", "weakened", "rejected_scoped", "rejected",
    "refuted", "contradicted", "inconclusive", "superseded",
)

# Evidence whose `direction` says nothing about any hypothesis. Most of the
# corpus is here, and the board says so rather than hiding it: the honest
# state of a research program is mostly "measured, and it did not point".
NEUTRAL_DIRECTIONS = {"", "neutral", "inconclusive", "n/a", "none", "not_applicable", "null"}


def hypothesis_verdict(status: str) -> str | None:
    key = (status or "").strip().lower()
    for verdict in HYPOTHESIS_VERDICTS:
        if key == verdict or key.startswith(verdict + "_"):
            return verdict
    return None


def direction_polarity(direction: str) -> str:
    """Fold the corpus's forty spellings of a direction into four.

    The schema names four values; the records use `supports_with_caveat`,
    `weakening_scoped`, `refutes_own_prior_reading` and so on. The exact
    string is kept on every row -- this is only how the board groups and
    colours them, and the reader always sees the author's own word.
    """
    key = (direction or "").strip().lower()
    if key in NEUTRAL_DIRECTIONS:
        return "neutral"
    if key.startswith(("weaken", "contradict", "refute", "negative", "against", "adverse")):
        return "weakens"
    if key.startswith(("support", "confirm", "corroborat", "positive", "strengthen", "enabling")):
        return "supports"
    return "mixed"


def _top_counts(rows, key: str, keep: int = 9) -> dict[str, int]:
    """`_count`, with a long tail folded into one row. Decision labels run to
    hundreds of one-off spellings; a distribution with 190 bars says nothing."""
    counts = _count(rows, key)
    if len(counts) <= keep + 1:
        return counts
    items = list(counts.items())
    head = dict(items[:keep])
    head[f"other ({len(items) - keep} labels)"] = sum(n for _, n in items[keep:])
    return head


def _scalar(fields: dict[str, str], name: str, limit: int = 60) -> str:
    value = fields.get(name, "")
    return "" if value == STRUCTURED else value[:limit]


def _id_field(fields: dict[str, str], name: str) -> str:
    """A field that should hold one identifier, or '' -- the shallow scan
    leaves a literal `null` as the string "null", which is not one."""
    value = fields.get(name, "")
    return value if value and value != STRUCTURED and RECORD_ID_RE.fullmatch(value) else ""


def _count(rows, key: str) -> dict[str, int]:
    counter = Counter((row.get(key) or "(unstated)") for row in rows)
    return dict(sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])))


def finding_summary(index: ResearchIndex, finding: Finding) -> dict[str, Any]:
    return {
        "id": finding.record_id,
        "title": finding.title,
        "path": finding.path,
        "added": finding.added,
        "status": finding.status,
        "proof_status": finding.proof_status,
        "proof_refs": finding.proof_refs,
        "confidence": finding.confidence,
        "evidence_level": finding.evidence_level,
        "claim_tier": finding.claim_tier,
        "tags": finding.tags,
        "superseded_by": finding.superseded_by,
        "withdrawn_by": finding.withdrawn_by,
        "refs": finding.refs,
        "goal_ids": finding.goal_ids,
        "areas": finding.areas,
        "area": finding.area,
        "ecc": any(a in index.ecc_areas for a in finding.areas),
        "excerpt": finding.excerpt,
        "non_claim": finding.non_claim,
        "error": finding.error,
        "cited_by": len(index.backlinks.get(finding.record_id, ())),
    }


def _iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "")[:10])
    except ValueError:
        return None


def added_within(index: ResearchIndex, days: int, today: date | None = None) -> int:
    """Current findings added in the last `days` days, relative to the build
    (static) or the request (live) -- the same clock `meta.built_at` uses."""
    today = today or datetime.now(timezone.utc).date()
    return sum(
        1 for f in index.findings
        if f.status == "current" and (added := _iso_date(f.added)) and (today - added).days <= days)


def directions(index: ResearchIndex, findings: list[dict], verdicts: list[dict],
               evidence: list[dict]) -> list[dict[str, Any]]:
    """One row per research area: what the program has done there.

    The area is the token in the middle of a record identifier
    (`GOAL-PFDR-…`) and is the closest thing the corpus has to a research
    direction. Goals, hypotheses, experiments and evidence carry their own;
    a finding or open problem is filed under one -- its goal's, or the first
    record it cites -- so nothing is counted twice. ECC areas sort first
    (CLAUDE.md rule 11), then whatever has established the most.
    """
    rows: dict[str, dict[str, Any]] = {}

    def row(area: str) -> dict[str, Any]:
        if area not in rows:
            rows[area] = {
                "area": area, "ecc": area in index.ecc_areas,
                "goals": [], "active_goals": 0,
                "findings": 0, "findings_total": 0, "latest_finding": None,
                "verdicts": {}, "evidence": {"supports": 0, "weakens": 0, "mixed": 0, "neutral": 0},
                "open_problems": 0, "hypotheses": 0, "experiments": 0,
            }
        return rows[area]

    for goal in index.goals:                           # already ECC-first, active-first
        if goal.area:
            r = row(goal.area)
            r["goals"].append({"id": goal.record_id, "title": goal.title, "status": goal.status})
            r["active_goals"] += goal.status == "active"
    for f in findings:                                 # newest first
        if f["area"]:
            r = row(f["area"])
            r["findings_total"] += 1
            if f["status"] == "current":
                r["findings"] += 1
                r["latest_finding"] = r["latest_finding"] or {
                    "id": f["id"], "title": f["title"], "added": f["added"]}
    for v in verdicts:
        if v["area"]:
            counts = row(v["area"])["verdicts"]
            counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    for e in evidence:
        if e["area"]:
            row(e["area"])["evidence"][e["polarity"]] += 1
    for problem in index.open_problems:
        if problem.area and problem.status == "open":
            row(problem.area)["open_problems"] += 1
    for record in index.by_kind.get("H", []):
        if record.area:
            row(record.area)["hypotheses"] += 1
    for experiment in index.experiments:
        if experiment.area:
            row(experiment.area)["experiments"] += 1
    return sorted(rows.values(), key=lambda r: (
        not r["ecc"], -r["findings"], -r["active_goals"], -r["hypotheses"], r["area"]))


def open_problem_summary(index: ResearchIndex, problem: OpenProblem) -> dict[str, Any]:
    return asdict(problem) | {
        "id": problem.record_id,
        "cited_by": len(index.backlinks.get(problem.record_id, ())),
    }


def hypothesis_verdicts(index: ResearchIndex) -> list[dict[str, Any]]:
    out = []
    for record in index.by_kind.get("H", []):
        raw = record.fields.get("status", "")
        verdict = hypothesis_verdict(raw)
        if not verdict:
            continue
        citing = sorted(index.backlinks.get(record.record_id, ()))
        out.append({
            "id": record.record_id,
            "verdict": verdict,
            "status": raw[:80],
            "statement": record.title[:600],
            "date": record.date,
            "area": record.area,
            "ecc": record.area in index.ecc_areas if record.area else False,
            "question_id": _id_field(record.fields, "question_id"),
            "goal_id": _id_field(record.fields, "goal_id"),
            "evidence_ids": [c for c in citing if id_kind(c) == "EV"],
            "decision_ids": [c for c in citing if id_kind(c) == "DEC"],
            "finding_ids": [c for c in citing if c.startswith("KN-FIND-")],
        })
    order = {v: i for i, v in enumerate(HYPOTHESIS_VERDICTS)}
    out.sort(key=lambda h: (order[h["verdict"]], _neg_date(h["date"]), h["id"]))
    return out


def evidence_rows(index: ResearchIndex) -> list[dict[str, Any]]:
    """Every evidence record with the fields that say what it found.

    All of them, neutral included: the board filters, the reader decides.
    Direction, strength, tier and proof status are second-level scalars and
    come from the shallow scan, like every other list in the dashboard.
    """
    rows = []
    for record in index.by_kind.get("EV", []):
        fields = record.fields
        direction = _scalar(fields, "direction", 40)
        polarity = direction_polarity(direction)
        rows.append({
            "id": record.record_id,
            "date": record.date,
            "area": record.area,
            "ecc": record.area in index.ecc_areas if record.area else False,
            "title": record.title[:INDEX_TITLE_CHARS],
            "direction": direction,
            "polarity": polarity,
            "neutral": polarity == "neutral",
            "strength": _scalar(fields, "strength", 40),
            "claim_tier": _scalar(fields, "claim_tier", 60),
            "proof_status": _scalar(fields, "proof_status", 40),
            "type": _scalar(fields, "type", 40),
            "hypothesis_id": _id_field(fields, "hypothesis_id"),
            "goal_id": _id_field(fields, "goal_id"),
            "experiment_ids": [r for r in sorted(record.refs) if id_kind(r) == "EXP"][:8],
            "finding_ids": [c for c in sorted(index.backlinks.get(record.record_id, ()))
                            if c.startswith("KN-FIND-")],
        })
    rows.sort(key=lambda r: (_neg_date(r["date"]), r["id"]))
    return rows


def pipeline_counts(index: ResearchIndex, evidence: list[dict], verdicts: list[dict]) -> list[dict]:
    """The program's own loop (CLAUDE.md "Typical loop") as a row of counts.

    Read left to right it says how much of what went in came out the other
    end. Each note carries the qualifier that keeps its count honest: how
    many hypotheses actually reached a verdict, how many experiments actually
    ran, how much evidence actually points somewhere.
    """
    def n(kind: str) -> int:
        return len(index.by_kind.get(kind, []))

    with_runs = sum(1 for e in index.experiments if e.runs)
    runs = sum(len(e.runs) for e in index.experiments)
    directional = sum(1 for row in evidence if not row["neutral"])
    current = sum(1 for f in index.findings if f.status == "current")
    retired = len(index.findings) - current
    return [
        {"key": "RQ", "label": "questions", "count": n("RQ"), "note": None},
        {"key": "IDEA", "label": "proposals", "count": n("IDEA"), "note": None},
        {"key": "H", "label": "hypotheses", "count": n("H"),
         "note": f"{len(verdicts)} with a verdict"},
        {"key": "EXP", "label": "experiments", "count": len(index.experiments),
         "note": f"{with_runs} with runs"},
        {"key": "RUN", "label": "runs", "count": runs, "note": None},
        {"key": "EV", "label": "evidence", "count": n("EV"),
         "note": f"{directional} with a direction"},
        {"key": "DEC", "label": "decisions", "count": n("DEC"), "note": None},
        {"key": "FIND", "label": "findings", "count": current,
         "note": f"{retired} superseded or withdrawn" if retired else None},
    ]


def findings_payload(index: ResearchIndex) -> dict[str, Any]:
    findings = [finding_summary(index, f) for f in index.findings]
    evidence = evidence_rows(index)
    verdicts = hypothesis_verdicts(index)
    return {
        "findings": findings,
        "directions": directions(index, findings, verdicts, evidence),
        "counts": {
            "findings": len(findings),
            "current": sum(1 for f in findings if f["status"] == "current"),
            "by_status": _count(findings, "status"),
            "by_proof_status": _count(findings, "proof_status"),
            "by_claim_tier": _count(findings, "claim_tier"),
            "by_confidence": _count(findings, "confidence"),
        },
        "hypothesis_verdicts": verdicts,
        "evidence": evidence,
        "evidence_counts": {
            "polarity": _count(evidence, "polarity"),
            "direction": _count(evidence, "direction"),
            "strength": _count(evidence, "strength"),
            "claim_tier": _count(evidence, "claim_tier"),
            "proof_status": _count(evidence, "proof_status"),
        },
        "obstructions": [
            asdict(o) | {"date": index.records[o.evidence_id].date}
            for o in index.obstructions],
        "open_problems": [open_problem_summary(index, p) for p in index.open_problems],
    }


def record_payload(index: ResearchIndex, record_id: str,
                   include_raw: bool = True) -> dict[str, Any] | None:
    record = index.records.get(record_id)
    if record is None:
        return None
    parsed, error = index.full_record(record_id)
    body = parsed
    markdown = None
    if isinstance(parsed, dict) and record.path.endswith(".md") and "markdown" in parsed:
        # A knowledge entry: the front matter is its structured part and the
        # body IS the entry. Without the body a finding's page was a title
        # and a link to GitHub, which is not a page.
        markdown, body = parsed["markdown"], parsed["front_matter"]
    elif isinstance(parsed, dict) and len(parsed) == 1:
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
    if markdown is not None:
        payload["markdown"] = markdown
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
