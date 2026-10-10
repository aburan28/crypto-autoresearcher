#!/usr/bin/env python3
"""Portfolio KPIs: the funnel, the approved-unrun backlog, and aged handoffs.

Read-only. One scan of ledger/ and experiments/ answers the questions the
track-record review (docs/track-record-review-20261006.md) found nobody was
asking at wake: how many approved contracts have never run, per goal; what
fraction of specified work ever produced evidence; which dispatched handoffs
never came back. `tools/ledger_summary.py` prints these for /research-status
and `tools/validate_ledger.py` reads `approved_unrun` for the approval
capacity gate (P0.1), so both see one definition of "unrun".

Definitions, stated once:

* An experiment is **approved** when its specification has `status: approved`.
* It is **unrun** when `runs/` holds nothing but `.gitkeep` and no run
  manifest or execution report cites it. A placeholder is not a run, and a
  prose report is not a run either.
* The backlog is keyed by `goal_id`; a specification without one falls back
  to its area (`EXP-<AREA>-...`), so an orphan contract still counts somewhere.
* An open handoff is one with no `archived_by`; it is **aged** when its id
  date is older than the threshold.

Usage:
    python3 tools/portfolio_kpis.py            # markdown
    python3 tools/portfolio_kpis.py --json
    python3 tools/portfolio_kpis.py --backlog  # per-goal approved-unrun table
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

try:  # the C loader is ~10x faster over 7k records; the pure one is the fallback
    from yaml import CSafeLoader as Loader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader as Loader  # type: ignore[assignment]

REPO = Path(__file__).resolve().parents[1]

# A goal may hold this many approved contracts with no run before another
# approval is refused (docs/track-record-review-20261006.md, P0.1). Three is
# enough for one lane to have a next contract queued while one runs and one is
# under review; the measured backlog that motivated the cap was 1,469.
APPROVAL_CAPACITY_CAP = 3

# Open handoffs older than this are reported as aged (P3.17). Two weeks is
# longer than any dispatched task budget in the ledger.
AGED_HANDOFF_DAYS = 14

_PLACEHOLDERS = {".gitkeep", ".keep"}
_DATE_IN_ID = re.compile(r"-(\d{8})-")
_AREA_IN_ID = re.compile(r"^EXP-([A-Za-z0-9]+)-")


def _load(path: Path, key: str) -> dict[str, Any] | None:
    try:
        doc = yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)
    except (OSError, ValueError, yaml.YAMLError):
        return None
    if not isinstance(doc, dict):
        return None
    body = doc.get(key, doc)
    return body if isinstance(body, dict) else None


def runs_present(exp_dir: Path) -> bool:
    """True when the experiment directory holds anything a run could have left."""
    runs = exp_dir / "runs"
    if runs.is_dir():
        for child in runs.iterdir():
            if child.name not in _PLACEHOLDERS:
                return True
    for name in ("execution-report.yaml", "execution_report.yaml"):
        if any(exp_dir.rglob(name)):
            return True
    return False


def goal_key(exp: dict[str, Any], exp_id: str) -> str:
    goal = exp.get("goal_id")
    if isinstance(goal, str) and goal.strip():
        return goal.strip()
    match = _AREA_IN_ID.match(exp_id)
    return f"area:{match.group(1)}" if match else "area:unknown"


def scan_experiments(root: Path) -> list[dict[str, Any]]:
    rows = []
    for spec in sorted((root / "experiments").glob("EXP-*/specification.yaml")):
        exp = _load(spec, "experiment")
        if exp is None:
            continue
        exp_id = str(exp.get("id") or spec.parent.name)
        rows.append({
            "id": exp_id,
            "status": exp.get("status"),
            "goal": goal_key(exp, exp_id),
            "hypothesis_id": exp.get("hypothesis_id"),
            "designed_at": str(exp.get("designed_at") or ""),
            "has_runs": runs_present(spec.parent),
        })
    return rows


def approved_unrun(root: Path = REPO, rows: list[dict[str, Any]] | None = None
                   ) -> dict[str, list[str]]:
    """goal key -> approved experiment ids with no run, sorted."""
    rows = scan_experiments(root) if rows is None else rows
    out: dict[str, list[str]] = collections.defaultdict(list)
    for row in rows:
        if row["status"] == "approved" and not row["has_runs"]:
            out[row["goal"]].append(row["id"])
    return {goal: sorted(ids) for goal, ids in sorted(out.items())}


def _count_dir(root: Path, sub: str) -> int:
    path = root / "ledger" / sub
    return len(list(path.glob("*.yaml"))) if path.is_dir() else 0


def _run_statuses(root: Path) -> collections.Counter:
    counts: collections.Counter = collections.Counter()
    for manifest in (root / "experiments").glob("EXP-*/runs/*/manifest.yaml"):
        body = _load(manifest, "run")
        counts[str((body or {}).get("status") or "unknown")] += 1
    for manifest in (root / "experiments").glob("EXP-*/runs/*/manifest.json"):
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            counts["unparseable"] += 1
            continue
        body = doc.get("run", doc) if isinstance(doc, dict) else {}
        counts[str(body.get("status") or "unknown")] += 1
    return counts


def _id_date(rec_id: str) -> dt.date | None:
    match = _DATE_IN_ID.search(rec_id or "")
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def aged_open_handoffs(root: Path = REPO, *, days: int = AGED_HANDOFF_DAYS,
                       today: dt.date | None = None) -> list[dict[str, Any]]:
    """Dispatched handoffs with no `archived_by` whose id date is older than `days`."""
    today = today or dt.date.today()
    out = []
    for path in sorted((root / "ledger" / "handoffs").glob("TASK-*.yaml")):
        body = _load(path, "handoff")
        if body is None or body.get("archived_by"):
            continue
        rec_id = str(body.get("id") or path.stem)
        when = _id_date(rec_id)
        if when is None:
            continue
        age = (today - when).days
        if age > days:
            out.append({"id": rec_id, "to": body.get("to"), "age_days": age})
    return out


def funnel(root: Path = REPO, rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = scan_experiments(root) if rows is None else rows
    by_status: collections.Counter = collections.Counter(str(r["status"]) for r in rows)
    backlog = approved_unrun(root, rows)
    runs = _run_statuses(root)
    ideas = _count_dir(root, "proposals")
    hyps = _count_dir(root, "hypotheses")
    evidence = _count_dir(root, "evidence")
    approved = by_status.get("approved", 0)
    unrun_total = sum(len(v) for v in backlog.values())
    with_runs = sum(1 for r in rows if r["has_runs"])

    def ratio(num: int, den: int) -> float | None:
        return round(num / den, 3) if den else None

    return {
        "ideas": ideas,
        "hypotheses": hyps,
        "experiments": len(rows),
        "experiments_by_status": dict(by_status.most_common()),
        "experiments_with_runs": with_runs,
        "approved": approved,
        "approved_unrun": unrun_total,
        "approved_unrun_goals_over_cap": sorted(
            g for g, ids in backlog.items() if len(ids) > APPROVAL_CAPACITY_CAP),
        "run_manifests_by_status": dict(runs.most_common()),
        "evidence": evidence,
        "conversion": {
            "idea_to_hypothesis": ratio(hyps, ideas),
            "hypothesis_to_experiment": ratio(len(rows), hyps),
            "approved_to_run": ratio(approved - unrun_total, approved),
            "experiment_to_evidence": ratio(evidence, len(rows)),
        },
        "capacity_cap": APPROVAL_CAPACITY_CAP,
    }


def build(root: Path = REPO, *, today: dt.date | None = None) -> dict[str, Any]:
    rows = scan_experiments(root)
    return {
        "funnel": funnel(root, rows),
        "approved_unrun_by_goal": approved_unrun(root, rows),
        "aged_open_handoffs": aged_open_handoffs(root, today=today),
        "aged_handoff_days": AGED_HANDOFF_DAYS,
    }


def render(report: dict[str, Any], *, backlog_rows: int = 10) -> str:
    f = report["funnel"]
    c = f["conversion"]

    def pct(value: float | None) -> str:
        return "—" if value is None else f"{value * 100:.0f}%"

    lines = ["## Portfolio KPIs", ""]
    lines.append(f"funnel: ideas {f['ideas']} → hypotheses {f['hypotheses']} "
                 f"→ experiments {f['experiments']} → with runs {f['experiments_with_runs']} "
                 f"→ evidence {f['evidence']}")
    lines.append(f"conversion: idea→H {pct(c['idea_to_hypothesis'])}, "
                 f"H→EXP {pct(c['hypothesis_to_experiment'])}, "
                 f"approved→run {pct(c['approved_to_run'])}, "
                 f"EXP→evidence {pct(c['experiment_to_evidence'])}")
    lines.append(f"approved without a run: {f['approved_unrun']} of {f['approved']} "
                 f"(cap {f['capacity_cap']} per goal; "
                 f"{len(f['approved_unrun_goals_over_cap'])} goal(s) over cap)")
    statuses = list(f["run_manifests_by_status"].items())
    runs = ", ".join(f"{k}:{v}" for k, v in statuses[:6]) or "—"
    if len(statuses) > 6:
        runs += f", +{len(statuses) - 6} other statuses ({sum(v for _, v in statuses[6:])})"
    lines.append(f"run manifests: {runs}")
    backlog = report["approved_unrun_by_goal"]
    if backlog:
        lines += ["", "largest approved-unrun backlogs:"]
        ranked = sorted(backlog.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        for goal, ids in ranked[:backlog_rows]:
            lines.append(f"  - {goal}: {len(ids)}  (e.g. {', '.join(ids[:3])})")
        if len(ranked) > backlog_rows:
            lines.append(f"  … +{len(ranked) - backlog_rows} more goals (--backlog)")
    aged = report["aged_open_handoffs"]
    lines += ["", f"handoffs open longer than {report['aged_handoff_days']} days: {len(aged)}"]
    for row in aged[:5]:
        lines.append(f"  - {row['id']} → {row['to']} ({row['age_days']} d)")
    if len(aged) > 5:
        lines.append(f"  … +{len(aged) - 5} more (--json lists all)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--backlog", action="store_true",
                        help="print the full per-goal approved-unrun table")
    parser.add_argument("--capacity", metavar="GOAL_OR_AREA",
                        help="approval headroom for one goal key (GOAL-... or "
                             "area:AREA); exit 1 when the goal is at the cap")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sparse_checkout
    if sparse_checkout.refuse_if_sparse("portfolio_kpis", args.repo_root):
        return 2
    if args.capacity:
        unrun = approved_unrun(args.repo_root).get(args.capacity, [])
        headroom = max(0, APPROVAL_CAPACITY_CAP - len(unrun))
        print(f"{args.capacity}\tapproved_unrun={len(unrun)}\t"
              f"cap={APPROVAL_CAPACITY_CAP}\theadroom={headroom}")
        for eid in unrun:
            print(f"  {eid}")
        return 0 if headroom else 1
    report = build(args.repo_root)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return 0
    if args.backlog:
        for goal, ids in sorted(report["approved_unrun_by_goal"].items(),
                                key=lambda kv: (-len(kv[1]), kv[0])):
            print(f"{goal}\t{len(ids)}\t{' '.join(ids)}")
        return 0
    print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
