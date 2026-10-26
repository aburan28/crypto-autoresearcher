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
  experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/verification.json
                                             completed finite Prym census counts/ranks
Run: python3 tools/progress_metrics.py [--ref origin/main] [--since YYYY-MM-DD]
"""
# ---- committed-state progress-metrics exporter contract ----
# Contract: print one JSON object per line to stdout. Fields: metric, value, date (YYYY-MM-DD),
# problem, unit, better (higher|lower|neutral), kind (gauge|event), label, source.
# Reads committed state at --ref via `git show`; never the working tree. stdlib only.
import argparse
import datetime as dt
import json
import math
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
    return [l for l in _git("ls-tree", "-r", "--name-only", ref, "--", path).splitlines() if l]


def file_history(ref, path, since):
    """Yield (date, commit, text) for the newest commit per day touching `path`, newest first."""
    out = _git("log", "--first-parent", ref, f"--since={since}", "--format=%H %cs", "--", path)
    seen = set()
    for line in out.splitlines():
        h, d = line.split()
        if d in seen:
            continue
        seen.add(d)
        txt = show(h, path)
        if txt is not None:
            yield d, h, txt


def emit(metric, value, *, date=None, problem="misc", unit="", better="neutral", kind="gauge", label="", source=""):
    if value is None or isinstance(value, bool):
        return
    try:
        v = float(value)
    except (TypeError, ValueError, OverflowError):
        return
    if not math.isfinite(v):
        return
    print(json.dumps({"metric": metric, "value": v, "date": date or TODAY, "problem": problem, "unit": unit,
                      "better": better, "kind": kind, "label": label or metric, "source": source}, allow_nan=False))


def default_ref():
    explicit = os.environ.get("PM_REF")
    if explicit:
        return explicit
    return _git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False).strip() or "origin/main"


def args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=default_ref())
    ap.add_argument("--since", default=os.environ.get("PM_SINCE") or (dt.date.today() - dt.timedelta(days=90)).isoformat())
    a = ap.parse_args()
    try:
        a.since = dt.date.fromisoformat(a.since).isoformat()
        # Every source in an export uses one immutable snapshot, even if a
        # concurrent fetch moves the requested remote-tracking branch.
        a.ref = _git("rev-parse", "--verify", "--end-of-options", a.ref + "^{commit}").strip()
    except (ValueError, RuntimeError) as exc:
        ap.error(str(exc))
    return a
# ---- end exporter helpers ----

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
            try:
                dt.date.fromisoformat(day)
            except ValueError:
                continue
            if day >= since:
                per_day[day][area] += 1
    for area in AREAS:
        if area not in per_area:
            continue
        emit(f"ledger.{area}.total", per_area.get(area, 0), problem=P, unit="count", better="neutral",
             label=f"ledger records: {area}", source=f"ledger/{area}/ (ls-tree)@{ref}")
    for day, c in per_day.items():
        for area in ("decisions", "handoffs", "corrections"):
            if area not in per_area:
                continue
            emit(f"ledger.{area}.per_day", c.get(area, 0), date=day, problem=P, unit="count/day", kind="event",
                 label=f"ledger {area} filed (by id date)", source=f"ledger/{area}/ ids@{ref}")


def receipts(ref, since):
    paths = [p for p in ls(ref, "coordination/sessions/receipts") if p.endswith(".yaml")]
    if not paths:
        return
    per_day = collections.Counter()
    for p in paths:
        m = re.search(r"/(\d{4})(\d{2})(\d{2})/", p)
        if m:
            day = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            try:
                dt.date.fromisoformat(day)
            except ValueError:
                continue
            if day >= since:
                per_day[day] += 1
    for day, n in per_day.items():
        emit("sessions.receipts", n, date=day, problem=P, unit="count/day", kind="event", better="neutral",
             label="agent session receipts written", source=f"coordination/sessions/receipts/@{ref}")
    emit("sessions.receipts_total", len(paths), problem=P, unit="count", better="neutral",
         label="agent session receipts, total", source=f"coordination/sessions/receipts/@{ref}")


def runs(ref):
    paths = [p for p in ls(ref, "experiments") if p.endswith("/manifest.json") and "/runs/" in p]
    if not paths:
        return
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
        if not isinstance(d, dict):
            status["unparseable"] += 1
            continue
        nested = d.get("run")
        nested = nested if isinstance(nested, dict) else {}
        s = d.get("status") or d.get("terminal_status") or nested.get("status") or "unknown"
        if not isinstance(s, str):
            s = "unknown"
        status[str(s)] += 1
    emit("runs.manifests_total", len(paths), problem=P, unit="count", better="higher",
         label="experiment run manifests", source=f"experiments/*/runs/*/manifest.json@{ref}")
    emit("runs.completed_valid", status.get("completed_valid", 0), problem=P, unit="count", better="higher",
         label="run manifests with status completed_valid", source=f"experiments/*/runs/*/manifest.json@{ref}")
    failed = sum(v for k, v in status.items() if {"failed", "invalid"}.intersection(k.split("_")))
    emit("runs.failed_or_invalid", failed, problem=P, unit="count", better="lower",
         label="run manifests failed / invalid", source=f"experiments/*/runs/*/manifest.json@{ref}")


def prym_census(ref):
    """Neutral observations from the committed checker, never planned workloads."""
    path = "experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/verification.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return
    if (not isinstance(data, dict) or data.get("schema") != "prym-rank-census-independent/v1"
            or data.get("status") != "passed" or data.get("failed_checks") != []
            or not isinstance(data.get("cells"), list) or not data["cells"]):
        return
    fields = {"attempts": "attempts_replayed", "accepted_rows": "rows_verified",
              "rank": "rank", "unknown_columns": "U"}
    seen = set()
    # Validate the entire source before emitting any gauges from it.
    for cell in data["cells"]:
        if (not isinstance(cell, dict) or not isinstance(cell.get("curve_uid"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", cell["curve_uid"])
                or cell.get("arm") not in {"sample64", "full3584"}
                or type(cell.get("seed")) is not int or cell["seed"] < 0
                or any(type(cell.get(key)) is not int or cell[key] < 0 for key in fields.values())):
            return
        identity = (cell["curve_uid"], cell["seed"], cell["arm"])
        if (identity in seen or cell["rank"] > min(cell["U"], cell["rows_verified"])
                or cell["rows_verified"] > cell["attempts_replayed"]):
            return
        seen.add(identity)
    for cell in data["cells"]:
        identity = f"{cell['curve_uid']}.s{cell['seed']}.{cell['arm']}"
        label = f"RUN-ECDLP-ea49a6 fixture {identity}"
        for name, key in fields.items():
            emit(f"prym.census.ea49a6.{identity}.{name}", cell[key],
                 problem="ecdlp-prym-relations", unit="count", better="neutral",
                 label=f"{label}: {name}", source=f"{path}@{ref}")


def funnel(ref, since):
    for date, commit, txt in file_history(ref, "coordination/portfolio_health/latest.json", since):
        try:
            d = json.loads(txt)
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue
        kpis = d.get("kpis")
        k = kpis.get("funnel") if isinstance(kpis, dict) else None
        k = k if isinstance(k, dict) else {}
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
        approved, unrun = k.get("approved"), k.get("approved_unrun")
        try:
            approved, unrun = (float(v) if type(v) in (int, float) else math.nan for v in (approved, unrun))
        except OverflowError:
            approved = unrun = math.nan
        if (math.isfinite(approved) and math.isfinite(unrun)
                and approved > 0 and 0 <= unrun <= approved):
            emit("funnel.approved_to_run_pct", 100.0 * (1.0 - unrun / approved),
                 date=date, problem=P, unit="%", better="higher", label="approved contracts that have run (%)", source=src)
        b = d.get("buckets") or {}
        b = b if isinstance(b, dict) else {}
        for name in ("ready", "batch_complete", "blocked", "needs_repair"):
            if isinstance(b.get(name), list):
                emit(f"goals.{name}", len(b[name]), date=date, problem=P, unit="count",
                     better="lower" if name == "needs_repair" else "neutral",
                     label=f"active goals classified {name}", source=src)
        emit("goals.active", d.get("active_goals"), date=date, problem=P, unit="count", label="active goals", source=src)


def claims(ref):
    paths = [p for p in ls(ref, "claims") if p.endswith(".json") and len(p.split("/")) == 2]
    if not paths:
        return
    n = len(paths)
    emit("claims.records", n, problem=P, unit="count", better="higher",
         label="structured speedup claims (progress-fidelity)", source=f"claims/*.json@{ref}")


def main():
    a = args()
    census(a.ref, a.since)
    receipts(a.ref, a.since)
    runs(a.ref)
    prym_census(a.ref)
    funnel(a.ref, a.since)
    claims(a.ref)


if __name__ == "__main__":
    main()
