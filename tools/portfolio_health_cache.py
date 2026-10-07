#!/usr/bin/env python3
"""Cache the portfolio health sweep so sessions read it instead of recomputing it.

`tools/goal_portfolio_health.py` renders every active goal's dispatch queue,
which takes two to three minutes and ~200 KB of output, most of it `next_action`
prose. Every Coordinator wake was paying that to learn a bucket count. This
tool writes one compact JSON file, `coordination/portfolio_health/latest.json`,
that `main-health.yml` refreshes on every merge to `main` and hourly:

    generated_at   when the sweep ran (UTC)
    commit         the `main` commit it describes
    buckets        goal ids per bucket (ready / batch_complete / blocked / needs_repair)
    goals          id, bucket, current batch, ready task ids, next_action
                   truncated to NEXT_ACTION_EXCERPT characters (the full text is
                   in the goal head when a session actually needs it)
    kpis           tools/portfolio_kpis.py build(): funnel, approved-unrun per
                   goal, aged handoffs -- the P3.17 handoff-return bucket lives
                   here as `kpis.aged_open_handoffs`

`--show` prints the summary and the cache's age, so a session can tell whether
the file is older than the merge digest it just read and decide to re-sweep.

The cache is derived state, like the merge digests: it is rebuilt by CI, never
edited, and a stale or missing cache is a reason to run the sweep, never an
error. It is committed (unlike `ledger/.index/`) because the point is to hand a
freshly cloned session the number without the sweep.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import goal_portfolio_health as health  # noqa: E402
import portfolio_kpis  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path("coordination") / "portfolio_health" / "latest.json"
NEXT_ACTION_EXCERPT = 240
BUCKETS = ("ready", "batch_complete", "blocked", "needs_repair")


def _head_commit(repo_root: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def build(repo_root: Path, *, now: datetime | None = None,
          goals: list[dict] | None = None) -> dict:
    """Sweep and summarise. `goals` lets tests inject classified rows."""
    now = now or datetime.now(timezone.utc)
    if goals is None:
        active = health.discover_active_goals(repo_root)
        with tempfile.TemporaryDirectory(prefix="portfolio_health_cache_") as tmp:
            goals = [health.classify(repo_root, g, Path(tmp)) for g in active]
    buckets: dict[str, list[str]] = {b: [] for b in BUCKETS}
    rows = []
    for g in goals:
        buckets.setdefault(g["bucket"], []).append(g["id"])
        action = g.get("next_action")
        if isinstance(action, str) and len(action) > NEXT_ACTION_EXCERPT:
            action = action[:NEXT_ACTION_EXCERPT].rstrip() + " …"
        rows.append({
            "id": g["id"],
            "bucket": g["bucket"],
            "current_batch_id": g.get("current_batch_id"),
            "ready_task_ids": list(g.get("ready_task_ids") or []),
            "next_action_excerpt": action,
        })
    for key in buckets:
        buckets[key].sort()
    rows.sort(key=lambda r: (BUCKETS.index(r["bucket"]) if r["bucket"] in BUCKETS else 9, r["id"]))
    return {
        "schema": "crypto.autoresearch.portfolio_health_cache.v1",
        "generated_at": now.replace(microsecond=0).isoformat(),
        "commit": _head_commit(repo_root),
        "shallow_clone": health.is_shallow_clone(repo_root),
        "active_goals": len(rows),
        "buckets": buckets,
        "goals": rows,
        "kpis": portfolio_kpis.build(repo_root),
    }


def age_hours(cache: dict, *, now: datetime | None = None) -> float | None:
    now = now or datetime.now(timezone.utc)
    try:
        stamp = datetime.fromisoformat(cache["generated_at"])
    except (KeyError, TypeError, ValueError):
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return round((now - stamp).total_seconds() / 3600, 2)


def render(cache: dict, *, now: datetime | None = None) -> str:
    age = age_hours(cache, now=now)
    commit = (cache.get("commit") or "unknown")[:12]
    lines = [f"# Portfolio health cache ({cache.get('generated_at')}, commit {commit}, "
             f"age {age if age is not None else '?'} h)"]
    if cache.get("shallow_clone"):
        lines.append("warning: swept on a shallow clone; needs_repair is untrustworthy")
    buckets = cache.get("buckets") or {}
    lines.append("buckets: " + ", ".join(f"{b} {len(buckets.get(b, []))}" for b in BUCKETS))
    ready = [g for g in cache.get("goals", []) if g["bucket"] == "ready"]
    for g in ready:
        lines.append(f"  ready {g['id']} ({g.get('current_batch_id') or '-'}): "
                     f"{', '.join(g.get('ready_task_ids') or []) or '-'}")
    kpis = cache.get("kpis")
    if kpis:
        lines.append("")
        lines.append(portfolio_kpis.render(kpis))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="cache path, relative to the repository root")
    parser.add_argument("--show", action="store_true",
                        help="print the existing cache's summary and age; sweep nothing")
    parser.add_argument("--max-age-hours", type=float,
                        help="with --show: exit 3 when the cache is older than this")
    args = parser.parse_args(argv)
    out = args.out if args.out.is_absolute() else args.repo_root / args.out
    if args.show:
        if not out.exists():
            print(f"no cache at {out}; run tools/portfolio_health_cache.py to build one",
                  file=sys.stderr)
            return 2
        cache = json.loads(out.read_text(encoding="utf-8"))
        print(render(cache))
        age = age_hours(cache)
        if args.max_age_hours is not None and (age is None or age > args.max_age_hours):
            print(f"cache is {age} h old, older than --max-age-hours {args.max_age_hours}",
                  file=sys.stderr)
            return 3
        return 0
    cache = build(args.repo_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cache, indent=1, sort_keys=True, default=str) + "\n",
                   encoding="utf-8")
    print(render(cache))
    print(f"\nwrote {out.relative_to(args.repo_root) if out.is_relative_to(args.repo_root) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
