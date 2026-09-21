#!/usr/bin/env python3
"""Render the `/research-status` snapshot without reading the ledger into context.

WHY THIS EXISTS
---------------
`/research-status` step 1 says "Scan the ledger" across six directories, and
step 2 says scan every experiment specification and count runs by terminal
status. Followed literally that is roughly:

    questions      135 files  ~0.19M tokens      handoffs    1,256 files  ~1.27M
    hypotheses     434 files  ~1.86M tokens      proposals   1,620 files  ~10.5M
    decisions      848 files  ~2.51M tokens      evidence      543 files  ~1.75M

-- about 18 million tokens for a read-only overview, against a session context
that holds a small fraction of one of those directories. No agent has ever
actually done it. Each one improvises instead (grep, `head -n`, sampling a few
files), gets a different and unreproducible answer, and the next session pays
the same improvisation cost again.

The counts are cheap to compute and tiny to report; only the reading was
expensive. This tool does the scan HERE, where bytes are free, and emits the
report step 4 asks for in ~1k tokens.

WHAT THIS TOOL DOES NOT DO
--------------------------
It does not check integrity. `/research-status` step 3 (dangling references,
approved-with-null-fields, runs missing artifacts) is already implemented, far
more thoroughly, by `tools/validate_ledger.py`; a second half-implementation
would drift from it and quietly disagree. This tool reports inventory and
status and points at that one.

Counts here are a census of records on disk, not a claim about research
results. A record's presence says a session wrote it; nothing more.

READ-ONLY: writes nothing under `ledger/`, `experiments/`, or `coordination/`.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any

import yaml

try:  # libyaml is ~10x faster and the ledger is ~60 MB of YAML
    from yaml import CSafeLoader as Loader
except ImportError:  # pragma: no cover - fallback when libyaml is absent
    from yaml import SafeLoader as Loader  # type: ignore[assignment]

# Ledger areas: directory -> (root key in each record, label).
AREAS = {
    "questions": ("research_question", "questions"),
    "proposals": ("idea", "proposals"),
    "hypotheses": ("hypothesis", "hypotheses"),
    "evidence": ("evidence", "evidence"),
    "decisions": ("coordinator_decision", "decisions"),
    "handoffs": ("handoff", "handoffs"),
}


def load_record(path: Path, root_key: str) -> dict[str, Any] | None:
    """Parse one ledger record and return its inner mapping.

    Unparseable records are returned as ``None`` and counted separately: a
    record that will not parse is an integrity signal (the thing
    `.github/workflows/main-health.yml` sweeps for), and silently dropping it
    would understate the ledger.
    """
    try:
        doc = yaml.load(path.read_text(), Loader=Loader)
    except Exception:  # noqa: BLE001 - counted as unparseable, never raised
        return None
    if not isinstance(doc, dict):
        return None
    record = doc.get(root_key, doc)
    return record if isinstance(record, dict) else None


def scan_area(root: Path, area: str, root_key: str, *, keep: bool = False) -> dict[str, Any]:
    """Count one ledger area, retaining parsed records only when asked.

    `keep` matters: `ledger/proposals/` alone is 42 MB of YAML and only its
    status tally is ever used, so holding those records would cost hundreds of
    megabytes to produce a dozen integers.
    """
    directory = root / "ledger" / area
    paths = sorted(p for p in directory.rglob("*.yaml") if p.is_file())
    statuses: collections.Counter[str] = collections.Counter()
    unparseable: list[str] = []
    records: list[dict[str, Any]] = []
    for path in paths:
        record = load_record(path, root_key)
        if record is None:
            unparseable.append(str(path.relative_to(root)))
            continue
        statuses[str(record.get("status") or "—")] += 1
        if keep:
            records.append(record)
    return {"area": area, "files": len(paths), "statuses": dict(statuses),
            "unparseable": unparseable, "_records": records}


def scan_experiments(root: Path) -> dict[str, Any]:
    """Experiment specifications by status, and run manifests by terminal status."""
    specs: collections.Counter[str] = collections.Counter()
    runs: collections.Counter[str] = collections.Counter()
    in_flight: list[dict[str, Any]] = []
    run_by_exp: collections.Counter[str] = collections.Counter()

    for manifest in (root / "experiments").rglob("manifest.json"):
        try:
            doc = json.loads(manifest.read_text())
        except Exception:  # noqa: BLE001
            runs["unparseable"] += 1
            continue
        run = doc.get("run", doc)
        if not isinstance(run, dict):
            runs["unparseable"] += 1
            continue
        runs[str(run.get("status") or "—")] += 1
        if run.get("experiment_id"):
            run_by_exp[str(run["experiment_id"])] += 1

    for spec_path in sorted((root / "experiments").rglob("specification.yaml")):
        record = load_record(spec_path, "experiment")
        if record is None:
            specs["unparseable"] += 1
            continue
        status = str(record.get("status") or "—")
        specs[status] += 1
        # "In flight" is the lifecycle gap /research-status step 4 asks about:
        # approved to run, but no run recorded yet.
        exp_id = str(record.get("id") or spec_path.parent.name)
        if status in {"approved", "running"} and run_by_exp[exp_id] == 0:
            in_flight.append({"id": exp_id, "status": status,
                              "hypothesis_id": record.get("hypothesis_id"),
                              "runs": 0})
    return {"specifications": dict(specs), "runs": dict(runs),
            "in_flight": sorted(in_flight, key=lambda r: r["id"])}


def _one_line(value: Any, limit: int = 150) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit].rstrip() + " …"


def recent_decisions(records: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """The n most recent decisions with their next actions.

    Ordered by `recorded_at`/`added`/`date` when present, else by id. IDs no
    longer sort into creation order (CLAUDE.md, "Conventions": the random-token
    scheme), so a date field is the only real ordering and id is a last resort.
    """
    def key(r: dict[str, Any]) -> tuple[str, str]:
        date = r.get("recorded_at") or r.get("added") or r.get("date") or ""
        return (str(date), str(r.get("id") or ""))
    out = []
    for record in sorted(records, key=key, reverse=True)[:n]:
        actions = record.get("next_actions") or []
        if isinstance(actions, str):
            actions = [actions]
        out.append({
            "id": record.get("id"),
            "date": record.get("recorded_at") or record.get("added") or record.get("date"),
            "decision": record.get("decision"),
            "targets": record.get("target_ids") or [],
            "next_actions": [_one_line(a) for a in actions[:3]],
            "next_actions_total": len(actions),
        })
    return out


def open_handoffs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Handoffs with no `archived_by` -- dispatched work with no recorded return."""
    out = []
    for record in records:
        if record.get("archived_by"):
            continue
        out.append({"id": record.get("id"), "to": record.get("to"),
                    "objective": _one_line(record.get("objective") or "", 110)})
    return sorted(out, key=lambda r: str(r["id"]))


def build(root: Path, recent: int) -> dict[str, Any]:
    # Only decisions and handoffs are read past their status tally.
    detailed = {"decisions", "handoffs"}
    areas = {a: scan_area(root, a, key, keep=a in detailed)
             for a, (key, _) in AREAS.items()}
    report: dict[str, Any] = {
        "areas": {a: {k: v for k, v in d.items() if k != "_records"}
                  for a, d in areas.items()},
        "experiments": scan_experiments(root),
        "recent_decisions": recent_decisions(areas["decisions"]["_records"], recent),
        "open_handoffs": open_handoffs(areas["handoffs"]["_records"]),
    }
    return report


def render(report: dict[str, Any], recent: int, max_open: int) -> str:
    lines: list[str] = ["# Research status — ledger census", ""]
    lines.append("| area | records | statuses |")
    lines.append("| --- | ---: | --- |")
    for area, data in report["areas"].items():
        statuses = ", ".join(f"{k}:{v}" for k, v in
                             sorted(data["statuses"].items(), key=lambda kv: -kv[1]))
        lines.append(f"| {area} | {data['files']} | {statuses or '—'} |")

    exp = report["experiments"]
    lines += ["", "## Experiments", ""]
    lines.append("specifications: " + (", ".join(
        f"{k}:{v}" for k, v in sorted(exp["specifications"].items(), key=lambda kv: -kv[1])) or "—"))
    lines.append("run manifests:  " + (", ".join(
        f"{k}:{v}" for k, v in sorted(exp["runs"].items(), key=lambda kv: -kv[1])) or "—"))
    flight = exp["in_flight"]
    lines.append("")
    lines.append(f"approved/running with no run recorded ({len(flight)}):")
    for row in flight[:max_open]:
        lines.append(f"  - {row['id']} [{row['status']}] hypothesis={row['hypothesis_id']}")
    if len(flight) > max_open:
        lines.append(f"  … +{len(flight) - max_open} more (--max-open)")

    lines += ["", f"## Latest decisions ({recent})", ""]
    for row in report["recent_decisions"]:
        lines.append(f"- {row['id']} ({row['date']}) → {row['decision']}"
                     f"  targets={', '.join(map(str, row['targets'][:4])) or '—'}")
        for action in row["next_actions"]:
            lines.append(f"    next: {action}")
        if row["next_actions_total"] > len(row["next_actions"]):
            lines.append(f"    … +{row['next_actions_total'] - len(row['next_actions'])} more next_actions")

    openh = report["open_handoffs"]
    lines += ["", f"## Handoffs with no recorded return ({len(openh)})", ""]
    for row in openh[:max_open]:
        lines.append(f"- {row['id']} → {row['to']}: {row['objective']}")
    if len(openh) > max_open:
        lines.append(f"… +{len(openh) - max_open} more (--max-open)")

    bad = {a: d["unparseable"] for a, d in report["areas"].items() if d["unparseable"]}
    lines += ["", "## Unparseable records", ""]
    if bad:
        for area, paths in bad.items():
            lines.append(f"- {area}: {len(paths)} — {', '.join(paths[:5])}")
    else:
        lines.append("none")

    lines += ["", "## Integrity", "",
              "Not checked here. Run `python3 tools/validate_ledger.py` for dangling",
              "references, null approved fields, and run-artifact completeness —",
              "`/research-status` step 3 is that tool, not this census.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compact ledger census for /research-status (read-only).")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--recent", type=int, default=8,
                        help="most recent decisions to detail (default 8)")
    parser.add_argument("--max-open", type=int, default=15,
                        help="rows per open-item list (default 15)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.repo_root
    if not (root / "ledger").is_dir():
        print(f"error: no ledger/ under {root}", file=sys.stderr)
        return 2
    report = build(root, args.recent)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(render(report, args.recent, args.max_open))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
