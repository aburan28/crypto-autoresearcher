#!/usr/bin/env python3
"""List newest approved experiments that still appear runnable.

Selection is cheap and deterministic: parse only top-level specification.yaml
files, enforce the approval/frozen/execution gates, skip experiments that
already contain an execution-report.yaml, preserve ECC-first policy from
orchestration/research-priority.yaml, then sort newest-first by designed_at
with experiment id as the deterministic tie-break.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import ecc_priority  # noqa: E402


def _load(path: Path) -> dict[str, Any] | None:
    try:
        doc = yaml.safe_load(path.read_text()) or {}
    except Exception:
        return None
    exp = doc.get("experiment", doc)
    return exp if isinstance(exp, dict) else None


def _completed(exp_dir: Path) -> bool:
    """An experiment has already been executed once its own `runs/` directory
    holds anything, or an execution report exists under it by either naming
    convention. `runs/RUN-*/` is the actual, universal signal this repo's own
    executor writes; a bare `execution-report.yaml`/`execution_report.yaml`
    directly under the experiment is a narrower, defensive fallback (the
    program's own convention nests the real report under
    coordination/**/tasks/*/execution_report.yaml, which is per-batch and not
    reachable from the experiment directory alone -- runs/ is the reliable
    signal from here)."""
    runs_dir = exp_dir / "runs"
    if runs_dir.is_dir() and any(runs_dir.iterdir()):
        return True
    return (any(exp_dir.rglob("execution-report.yaml"))
            or any(exp_dir.rglob("execution_report.yaml")))


def newest_runnable(repo: Path = REPO) -> list[dict[str, Any]]:
    policy = ecc_priority.load_policy(repo / "orchestration" / "research-priority.yaml")
    rows: list[dict[str, Any]] = []
    for spec in sorted((repo / "experiments").glob("EXP-*/specification.yaml")):
        exp = _load(spec)
        if not exp:
            continue
        exp_id = str(exp.get("id") or spec.parent.name)
        if exp.get("status") != "approved":
            continue
        if not exp.get("approved_by") or exp.get("frozen") is not True:
            continue
        if exp.get("execution_authorized") is False:
            continue
        if _completed(spec.parent):
            continue
        rows.append({
            "id": exp_id,
            "designed_at": str(exp.get("designed_at") or ""),
            "goal_id": exp.get("goal_id"),
            "hypothesis_id": exp.get("hypothesis_id"),
            "specification": str(spec.relative_to(repo)),
            "ecc": ecc_priority.is_ecc(exp_id, policy),
        })

    # Standing policy says ECC first at every selection point. Within each
    # policy class, newest designed_at wins; id makes same-day ordering stable.
    ecc = [r for r in rows if r["ecc"]]
    non = [r for r in rows if not r["ecc"]]
    ecc.sort(key=lambda r: (r["designed_at"], r["id"]), reverse=True)
    non.sort(key=lambda r: (r["designed_at"], r["id"]), reverse=True)
    return ecc + non


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rows = newest_runnable()
    shown = rows[: max(args.limit, 0)] if args.limit else rows
    if args.json:
        print(json.dumps(shown, indent=2))
    else:
        for row in shown:
            print(f"{row['id']}\t{row['designed_at']}\t{'ECC' if row['ecc'] else 'non-ECC'}\t{row['specification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
