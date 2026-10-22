#!/usr/bin/env python3
"""Progress-metrics exporter for `crypto-autoresearcher` (the agent research program).

Sources (committed, read at --ref):
  ledger/<area>/*.yaml                      record census per area (filenames only; no YAML parsing)
  ledger/decisions/DEC-YYYYMMDD-*.yaml       decisions per day (date in the id)
  ledger/handoffs/TASK-YYYYMMDD-*.yaml       handoffs per day
  coordination/sessions/receipts/YYYYMMDD/   session receipts per day (process records, not evidence)
  experiments/*/runs/*/manifest.json         run manifests by status
  coordination/portfolio_health/latest.json  funnel KPIs (approved-unrun, conversions); history via git log
  claims/*.json                              structured speedup claims (progress-fidelity)
Run: python3 tools/progress_metrics.py [--ref origin/main] [--since YYYY-MM-DD]
"""
# ---- progress-metrics exporter boilerplate (copied verbatim into each repo's tools/progress_metrics.py) ----
# Contract: print one JSON object per line to stdout. Fields: metric, value, date (YYYY-MM-DD),
# problem, unit, better (higher|lower|neutral), kind (gauge|event), label, source.
# Reads committed state at --ref via `git show`; never the working tree. stdlib only.
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(os.environ.get("PM_REPO_PATH") or Path(__file__).resolve().parents[1])
TODAY = dt.date.today().isoformat()


def _git(*args, check=True):
    p = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()[:200]}")
    return p.stdout


def show(ref, path):
    p = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def ls(ref, path=""):
    return [l for l in _git("ls-tree", "-r", "--name-only", ref, "--", path, check=False).splitlines() if l]


def file_history(ref, path, since):
    """Yield (date, commit, text) for the newest commit per day touching `path`, newest first."""
    out = _git("log", "--first-parent", ref, f"--since={since}", "--format=%H %cs", "--", path, check=False)
    seen = set()
    for line in out.splitlines():
        h, d = line.split()
        if d in seen:
            continue
        seen.add(d)
        txt = show(h, path)
        if txt is not None:
            yield d, h[:12], txt


def emit(metric, value, *, date=None, problem="misc", unit="", better="neutral", kind="gauge", label="", source=""):
    if value is None:
        return
    try:
        v = float(value)
    except (TypeError, ValueError):
        return
    if v != v:
        return
    print(json.dumps({"metric": metric, "value": v, "date": date or TODAY, "problem": problem, "unit": unit,
                      "better": better, "kind": kind, "label": label or metric, "source": source}))


def args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=os.environ.get("PM_REF", "origin/main"))
    ap.add_argument("--since", default=os.environ.get("PM_SINCE") or (dt.date.today() - dt.timedelta(days=90)).isoformat())
    return ap.parse_args()
# ---- end boilerplate ----

import collections
import re

P = "research-program"
AREAS = ("goals", "questions", "proposals", "hypotheses", "evidence", "decisions", "handoffs", "corrections")
DATED = re.compile(r"-(\d{4})(\d{2})(\d{2})-")


def census(ref, since):
    paths = ls(ref, "ledger")
    per_area = collections.Counter()
    per_day = collections.defaultdict(collections.Counter)
    for p in paths:
        parts = p.split("/")
        if len(parts) < 3 or not p.endswith(".yaml"):
            continue
        area = parts[1]
        per_area[area] += 1
        m = DATED.search(parts[-1])
        if m:
            day = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            if day >= since:
                per_day[day][area] += 1
    for area in AREAS:
        emit(f"ledger.{area}.total", per_area.get(area, 0), problem=P, unit="count", better="neutral",
             label=f"ledger records: {area}", source=f"ledger/{area}/ (ls-tree)")
    for day, c in per_day.items():
        for area in ("decisions", "handoffs", "corrections"):
            emit(f"ledger.{area}.per_day", c.get(area, 0), date=day, problem=P, unit="count/day", kind="event",
                 label=f"ledger {area} filed (by id date)", source=f"ledger/{area}/ ids")


def receipts(ref, since):
    paths = [p for p in ls(ref, "coordination/sessions/receipts") if p.endswith(".yaml")]
    per_day = collections.Counter()
    for p in paths:
        m = re.search(r"/(\d{4})(\d{2})(\d{2})/", p)
        if m:
            day = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            if day >= since:
                per_day[day] += 1
    for day, n in per_day.items():
        emit("sessions.receipts", n, date=day, problem=P, unit="count/day", kind="event", better="neutral",
             label="agent session receipts written", source="coordination/sessions/receipts/")
    emit("sessions.receipts_total", len(paths), problem=P, unit="count", better="neutral",
         label="agent session receipts, total", source="coordination/sessions/receipts/")


def runs(ref):
    paths = [p for p in ls(ref, "experiments") if p.endswith("/manifest.json") and "/runs/" in p]
    status = collections.Counter()
    for p in paths:
        txt = show(ref, p)
        if not txt:
            continue
        try:
            d = json.loads(txt)
        except json.JSONDecodeError:
            status["unparseable"] += 1
            continue
        s = d.get("status") or d.get("terminal_status") or (d.get("run") or {}).get("status") or "unknown"
        status[str(s)] += 1
    emit("runs.manifests_total", len(paths), problem=P, unit="count", better="higher",
         label="experiment run manifests", source="experiments/*/runs/*/manifest.json")
    emit("runs.completed_valid", status.get("completed_valid", 0), problem=P, unit="count", better="higher",
         label="run manifests with status completed_valid", source="experiments/*/runs/*/manifest.json")
    failed = sum(v for k, v in status.items() if k.startswith("failed") or k.endswith("invalid"))
    emit("runs.failed_or_invalid", failed, problem=P, unit="count", better="lower",
         label="run manifests failed / invalid", source="experiments/*/runs/*/manifest.json")


def funnel(ref, since):
    for date, commit, txt in file_history(ref, "coordination/portfolio_health/latest.json", since):
        try:
            d = json.loads(txt)
        except json.JSONDecodeError:
            continue
        k = (d.get("kpis") or {}).get("funnel") or {}
        src = f"coordination/portfolio_health/latest.json@{commit}"
        for key, better, label in (
            ("ideas", "neutral", "funnel: ideas"), ("hypotheses", "neutral", "funnel: hypotheses"),
            ("experiments", "neutral", "funnel: experiments"), ("approved", "neutral", "funnel: approved contracts"),
            ("experiments_with_runs", "higher", "funnel: experiments with runs"),
            ("evidence", "higher", "funnel: evidence records"),
            ("approved_unrun", "lower", "approved contracts never run (backlog)"),
        ):
            emit(f"funnel.{key}", k.get(key), date=date, problem=P, unit="count", better=better, label=label, source=src)
        over = k.get("approved_unrun_goals_over_cap")
        if isinstance(over, list):
            emit("funnel.goals_over_capacity_cap", len(over), date=date, problem=P, unit="count", better="lower",
                 label="goals over the approval capacity cap", source=src)
        if k.get("approved") and k.get("experiments_with_runs") is not None:
            emit("funnel.approved_to_run_pct", 100.0 * (k["approved"] - (k.get("approved_unrun") or 0)) / k["approved"],
                 date=date, problem=P, unit="%", better="higher", label="approved contracts that have run (%)", source=src)
        b = d.get("buckets") or {}
        for name in ("ready", "batch_complete", "blocked", "needs_repair"):
            if isinstance(b.get(name), list):
                emit(f"goals.{name}", len(b[name]), date=date, problem=P, unit="count",
                     better="lower" if name == "needs_repair" else "neutral",
                     label=f"active goals classified {name}", source=src)
        emit("goals.active", d.get("active_goals"), date=date, problem=P, unit="count", label="active goals", source=src)


def claims(ref):
    n = len([p for p in ls(ref, "claims") if p.endswith(".json")])
    emit("claims.records", n, problem=P, unit="count", better="higher",
         label="structured speedup claims (progress-fidelity)", source="claims/*.json")


def main():
    a = args()
    census(a.ref, a.since)
    receipts(a.ref, a.since)
    runs(a.ref)
    funnel(a.ref, a.since)
    claims(a.ref)


if __name__ == "__main__":
    main()
