#!/usr/bin/env python3
"""Select ECC-first/newest-first execution work without mistaking attempts for completion.

Only explicit trial-plan coverage establishes measurement completion. Legacy
activity without a plan is surfaced by --include-blocked for reconciliation,
not silently called complete and not automatically rerun. Selection never
replaces the dispatcher, committed approval, claim or archive gates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import ecc_priority  # noqa: E402
from experiment_execution import coverage  # noqa: E402

_EXP_ID_RE = re.compile(r"EXP-[A-Za-z0-9]+-(?:[0-9a-fA-F]{6}|\d{3})")


def _load(path: Path) -> dict[str, Any] | None:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            return None
        exp = doc.get("experiment", doc)
        return exp if isinstance(exp, dict) else None
    except (OSError, ValueError, yaml.YAMLError):
        return None


def execution_progress(exp_dir: Path, repo: Path) -> dict[str, Any]:
    plan = exp_dir / "trial-plan.json"
    if plan.exists() or plan.is_symlink():
        try:
            report = coverage(repo, plan)
            state = ("measurement_complete" if report["measurement_complete"] else
                     "ready" if report["planned"] else "needs_reconciliation")
            return {"execution_state": state, "trial_plan": str(plan.relative_to(repo)),
                    "coverage": report}
        except (OSError, ValueError, TypeError) as error:
            return {"execution_state": "needs_plan_repair", "reason": str(error)}
    runs = exp_dir / "runs"
    activity = runs.is_dir() and any(runs.iterdir())
    activity = activity or any(exp_dir.rglob("execution-report.yaml")) or any(
        exp_dir.rglob("execution_report.yaml"))
    if activity:
        return {"execution_state": "needs_reconciliation",
                "reason": "legacy attempts/reports exist without explicit trial coverage; do not rerun blindly"}
    return {"execution_state": "needs_implementation_or_plan",
            "reason": "no trial plan; arrange scoped implementation/contract preparation before execution"}


def _completed(exp_dir: Path) -> bool:
    """Compatibility helper: populated directories and prose reports are not completion."""
    return execution_progress(exp_dir, exp_dir.parent.parent)["execution_state"] == "measurement_complete"


def _superseded_ids(specs: list[tuple[Path, dict[str, Any]]]) -> set[str]:
    superseded: set[str] = set()
    for _, exp in specs:
        raw = exp.get("supersedes")
        if raw:
            text = raw if isinstance(raw, str) else " ".join(str(x) for x in raw)
            superseded.update(_EXP_ID_RE.findall(text))
    return superseded


def newest_runnable(repo: Path = REPO, *, include_blocked: bool = False,
                    goal: str | None = None, experiment_ids: set[str] | None = None) -> list[dict[str, Any]]:
    repo = repo.resolve()
    policy = ecc_priority.load_policy(repo / "orchestration" / "research-priority.yaml")
    specs = [(spec, exp) for spec in sorted((repo / "experiments").glob("EXP-*/specification.yaml"))
             if (exp := _load(spec)) is not None]
    superseded = _superseded_ids(specs)
    rows: list[dict[str, Any]] = []
    for spec, exp in specs:
        exp_id = str(exp.get("id") or spec.parent.name)
        if (exp.get("status") != "approved" or not exp.get("approved_by")
                or exp.get("frozen") is not True or exp.get("execution_authorized") is False
                or exp_id in superseded):
            continue
        if goal is not None and exp.get("goal_id") != goal:
            continue
        if experiment_ids is not None and exp_id not in experiment_ids:
            continue
        progress = execution_progress(spec.parent, repo)
        if progress["execution_state"] == "measurement_complete":
            continue
        if not include_blocked and progress["execution_state"] not in ("ready", "needs_implementation_or_plan"):
            continue
        rows.append({"id": exp_id, "designed_at": str(exp.get("designed_at") or ""),
                     "goal_id": exp.get("goal_id"), "hypothesis_id": exp.get("hypothesis_id"),
                     "specification": str(spec.relative_to(repo)),
                     "ecc": ecc_priority.is_ecc(exp_id, policy), **progress})
    ecc = [r for r in rows if r["ecc"]]
    non = [r for r in rows if not r["ecc"]]
    for group in (ecc, non):
        group.sort(key=lambda r: (r["designed_at"], r["id"]), reverse=True)
    return ecc + non


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1, help="0 means all eligible work")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-blocked", action="store_true")
    parser.add_argument("--goal")
    parser.add_argument("--experiment", action="append")
    args = parser.parse_args(argv)
    rows = newest_runnable(include_blocked=args.include_blocked, goal=args.goal,
                           experiment_ids=set(args.experiment) if args.experiment else None)
    shown = rows[:max(args.limit, 0)] if args.limit else rows
    if args.json:
        print(json.dumps(shown, indent=2))
    else:
        for row in shown:
            print(f"{row['id']}\t{row['designed_at']}\t{'ECC' if row['ecc'] else 'non-ECC'}"
                  f"\t{row['execution_state']}\t{row['specification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
