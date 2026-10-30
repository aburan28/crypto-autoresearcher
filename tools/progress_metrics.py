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
  experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/verification.json
                                             completed width16 Prym counts/ranks
  experiments/EXP-ECDLP-2b4ff1/reports/run-20261027T1934Z/data.json
                                             endpoint-reuse execution/public-witness observations
  experiments/EXP-ECDLP-f50061/reports/run-20261027T2311Z/observations.json
                                             parameter-sweep counts, retaining censored cases
  experiments/EXP-ECDLP-c45dd8/reports/run-20261027T2329Z/observations.json
                                             fixed NG screen counts, including covariance views
  experiments/EXP-ECDLP-8dc19d/reports/run-20261028T1728Z/observations.json
                                             fresh transfer counts, events and distinct target-arm pairs
  docs/reports/classical-ecdlp-controlled-followup-20261029/observations/observations.json
                                             source-bound failed-run operational/coverage counts
Run: python3 tools/progress_metrics.py [--ref origin/main] [--since YYYY-MM-DD]
"""
# ---- committed-state progress-metrics exporter contract ----
# Contract: print one JSON object per line to stdout. Fields: metric, value, date (YYYY-MM-DD),
# problem, unit, better (higher|lower|neutral), kind (gauge|event), label, source.
# Reads committed state at --ref via `git show`; never the working tree. stdlib only.
import argparse
import datetime as dt
import json
import hashlib
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


def prym_width(ref):
    """Counted width16 observations from its committed native replay only."""
    path = "experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/verification.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return
    if (not isinstance(data, dict) or data.get("schema") != "prym-width-independent/v1"
            or data.get("status") != "passed" or data.get("failed_checks") != []
            or not isinstance(data.get("cells"), list) or not data["cells"]):
        return
    fields = {"attempts": "attempts_replayed", "accepted_rows": "rows_verified",
              "rank": "rank", "unknown_columns": "U"}
    seen = set()
    for cell in data["cells"]:
        if (not isinstance(cell, dict) or not isinstance(cell.get("curve_uid"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", cell["curve_uid"])
                or any(type(cell.get(key)) is not int or cell[key] < 0 for key in fields.values())):
            return
        if (cell["curve_uid"] in seen or cell["rank"] > min(cell["U"], cell["rows_verified"])
                or cell["rows_verified"] > cell["attempts_replayed"]):
            return
        seen.add(cell["curve_uid"])
    for cell in data["cells"]:
        identity = f"{cell['curve_uid']}.m16_full35840"
        for name, key in fields.items():
            emit(f"prym.width.967315.{identity}.{name}", cell[key],
                 problem="ecdlp-prym-relations", unit="count", better="neutral",
                 label=f"RUN-ECDLP-967315 fixture {identity}: {name}", source=f"{path}@{ref}")


def prym_equation_diversity(ref):
    """Exploratory retained-data counts, distinct from new trial results."""
    path = "research/prym_leads_20261027/derived/matrix-duplicate-review.json"
    try:
        data = json.loads(show(ref, path))
        if (data.get("schema") != "prym-retained-duplicate-explanation/v1"
                or type(data.get("new_scientific_trials")) is not int
                or data["new_scientific_trials"] != 0
                or data.get("source_logical_sha256") !=
                "8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007"
                or not isinstance(data.get("cells"), list) or not data["cells"]):
            return
        seen = set()
        for cell in data["cells"]:
            uid = cell["ec1_curve_uid"]
            counts = [cell[k] for k in ["native_witnesses", "distinct_projected_affine_rows",
                                        "rank_of_distinct_rows", "dependencies_among_distinct_rows"]]
            groups = cell["groups"]
            if (not isinstance(uid, str) or not re.fullmatch(r"urn:ec-record:1:sha256:[0-9a-f]{64}", uid)
                    or uid in seen or any(type(n) is not int or n < 0 for n in counts)
                    or not isinstance(groups, list)
                    or counts[1] != len(groups) or counts[2] != counts[1] or counts[3] != 0
                    or counts[0] < counts[1]):
                return
            seen.add(uid)
            for group in groups:
                if (type(group["native_witness_count"]) is not int or group["native_witness_count"] < 1
                        or type(group["admissible_constraint_triples"]) is not int
                        or group["native_witness_count"] != group["admissible_constraint_triples"]
                        or group["exact_constraint_subset_match"] is not True):
                    return
            if sum(group["native_witness_count"] for group in groups) != counts[0]:
                return
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    for cell in data["cells"]:
        identity = cell["ec1_curve_uid"].rsplit(":", 1)[-1]
        distinct = cell["distinct_projected_affine_rows"]
        values = {"distinct_affine_rows": distinct, "duplicate_witnesses": cell["native_witnesses"]-distinct}
        for name, value in values.items():
            emit(f"prym.exploratory.967315.{identity}.{name}", value,
                 problem="ecdlp-prym-relations", unit="count", better="neutral",
                 label=f"Post-data RUN-ECDLP-967315 {identity}: {name}", source=f"{path}@{ref}")


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


def endpoint_reuse_observations(ref, since):
    """Actual process/public-witness counts; no native-cost qualification."""
    path = "experiments/EXP-ECDLP-2b4ff1/reports/run-20261027T1934Z/data.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.descriptive-run-report-data/v1"
                or data.get("experiment_id") != "EXP-ECDLP-2b4ff1"
                or data.get("run_id") != "RUN-ECDLP-b883bf" or date < since):
            return
        flow, verification = data["flow"], data["verification"]
        if verification.get("status") != "public_equations_and_trace_pass":
            return
        values = {
            "completed_children": flow["completed"],
            "public_fixtures": verification["public_fixtures"],
            "public_target_ids": verification["public_target_ids"],
            "verified_case_witnesses": verification["verified_case_witnesses"],
        }
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    if any(type(value) is not int or value < 0 for value in values.values()):
        return
    labels = {
        "completed_children": "completed native children (execution observation)",
        "public_fixtures": "public fixtures checked",
        "public_target_ids": "public target identities checked",
        "verified_case_witnesses": "public-equation witnesses verified (native counters not replayed)",
    }
    for name, value in values.items():
        emit(f"endpoint_reuse.b883bf.{name}", value, date=date,
             problem="ecdlp-endpoint-reuse", unit="count", better="neutral",
             label=f"RUN-ECDLP-b883bf: {labels[name]}", source=f"{path}@{ref}")


def endpoint_reuse_sweep_observations(ref, since):
    """Actual sweep counts, including censoring; no cost or clock qualification."""
    path = "experiments/EXP-ECDLP-f50061/reports/run-20261027T2311Z/observations.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.parameter-sweep.observations/v1"
                or data.get("experiment_id") != "EXP-ECDLP-f50061"
                or data.get("run_id") != "RUN-ECDLP-e69a23"
                or data.get("protocol_sha256") != "f882380374559faae1b50d86c1583c06c36738fc5dce43d2861fadaa6204b812"
                or data.get("public_equation_verification") != "passed"
                or data.get("all_clocks_wall_valid") is not False
                or data.get("native_counter_replay_verified") is not False or date < since):
            return
        labels = {
            "completed_children": "completed native children (execution observation)",
            "public_fixtures": "public fixtures checked",
            "public_target_ids": "unique public target identities checked",
            "observed_target_arm_cases": "observed target-arm cases, including censoring",
            "verified_case_witnesses": "solved public-equation witnesses verified (native counters not replayed)",
            "censored_target_arm_cases": "retained censored target-arm cases",
        }
        values = {name: data[name] for name in labels}
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    if (any(type(value) is not int or value < 0 for value in values.values())
            or values["observed_target_arm_cases"] != values["verified_case_witnesses"] + values["censored_target_arm_cases"]):
        return
    for name, value in values.items():
        emit(f"endpoint_reuse.e69a23.{name}", value, date=date,
             problem="ecdlp-endpoint-reuse", unit="count", better="neutral",
             label=f"RUN-ECDLP-e69a23: {labels[name]}", source=f"{path}@{ref}")


def nongeneric_screen_observations(ref, since):
    """Neutral fixed-screen counts; repeated coordinate views remain counted."""
    path = "experiments/EXP-ECDLP-c45dd8/reports/run-20261027T2329Z/observations.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.nongeneric-screen.observations/v1"
                or data.get("experiment_id") != "EXP-ECDLP-c45dd8"
                or data.get("run_id") != "RUN-ECDLP-a11661"
                or data.get("protocol_sha256") != "31d6425d88c3217ddab47fe3fbc295a6ec6b0af3513942f0fc2a9156ccea7d3d"
                or data.get("verification_status") != "passed"
                or data.get("all_clocks_wall_valid") is not False
                or data.get("candidate_counter_execution_replayed") is not False or date < since):
            return
        labels = {
            "observed_cases": "retained fixed-screen cases, including undefined outcomes and covariance views",
            "candidate_cases": "retained candidate-template cases, including covariance views",
            "control_cases": "retained control-arm cases, including covariance views",
            "passing_groups": "base/view groups passing the fixed public gate",
            "templates_with_passing_groups": "templates with one or more passing base/view groups",
            "verified_recovered_targets": "verified fresh recovery targets across repeated coordinate views",
            "fresh_predicate_evaluations": "executed fresh recovery predicate evaluations",
        }
        values = {name: data[name] for name in labels}
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    if (any(type(value) is not int or value < 0 for value in values.values())
            or values["observed_cases"] != values["candidate_cases"] + values["control_cases"]
            or values["templates_with_passing_groups"] > 40):
        return
    for name, value in values.items():
        emit(f"nongeneric.a11661.{name}", value, date=date,
             problem="ecdlp-nongeneric-screen", unit="count", better="neutral",
             label=f"RUN-ECDLP-a11661: {labels[name]}", source=f"{path}@{ref}")


def transfer_study_observations(ref, since):
    """Neutral actual counts; successful attempt events and recovered pairs differ."""
    path = "experiments/EXP-ECDLP-8dc19d/reports/run-20261028T1728Z/observations.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.transfer-study.observations/v1"
                or data.get("experiment_id") != "EXP-ECDLP-8dc19d"
                or data.get("run_id") != "RUN-ECDLP-994f70"
                or data.get("protocol_sha256") != "fa961d179668d86e1dfcdc393d80c60e4f6a6f3ac541b9015f6011beba050c71"
                or data.get("verification_status") != "passed"
                or data.get("cohort_complete") is not True
                or data.get("all_clocks_wall_valid") is not False
                or data.get("counter_execution_replayed") is not False or date < since):
            return
        labels = {
            "fresh_curves": "distinct fresh public curves retained",
            "target_ids": "distinct fresh public target identities retained",
            "attempt_rows": "retained primary attempt rows, including failed and undefined outcomes",
            "checked_attempt_rows": "primary attempt rows checked by the independent verifier",
            "working_baseline_verified_target_ids": "unique targets verified by the working BSGS reference",
            "candidate_success_events": "verified candidate attempt success events, including repeated successes",
            "unique_target_arm_pairs_recovered": "distinct recovered target-arm pairs, with retries deduplicated",
        }
        values = {name: data[name] for name in labels}
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    if (any(type(value) is not int or value < 0 for value in values.values())
            or values["checked_attempt_rows"] > values["attempt_rows"]
            or values["working_baseline_verified_target_ids"] > values["target_ids"]
            or values["unique_target_arm_pairs_recovered"] > values["candidate_success_events"]):
        return
    for name, value in values.items():
        emit(f"transfer.994f70.{name}", value, date=date,
             problem="ecdlp-fixed-circuit-transfer", unit="count", better="neutral",
             label=f"RUN-ECDLP-994f70: {labels[name]}", source=f"{path}@{ref}")


def controlled_followup_observations(ref, since):
    """Source-bound operational counts from the retained failed attempt.

    A failed infrastructure attempt is an observation. Missing scientific
    measurements are never zero recoveries, predicate calls, or solver results.
    Read each payload at the same committed ref, even with a dirty checkout.
    """
    path = "docs/reports/classical-ecdlp-controlled-followup-20261029/observations/observations.json"
    text = show(ref, path)
    if text is None:
        return
    run = "experiments/EXP-ECDLP-956f81/runs/RUN-ECDLP-c8d9b0/"
    post = "experiments/EXP-ECDLP-956f81/postrun/"
    roles = {
        "receipt": run + "execution-receipt.json",
        "raw": run + "raw-result.json",
        "postrun": post + "postrun-result.json",
        "export": post + "export.canonical-paths.json",
        "validation": post + "export.validation.json",
        "protocol": "experiments/EXP-ECDLP-956f81/protocol.json",
    }
    try:
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.controlled-followup.failed-observations/v1"
                or data.get("experiment_id") != "EXP-ECDLP-956f81"
                or data.get("run_id") != "RUN-ECDLP-c8d9b0"
                or data.get("native_status") != "infrastructure_error"
                or data.get("postrun_status") != "incomplete"
                or data.get("scientific_validity") != "not_assessed"
                or data.get("wall_valid") is not False
                or data.get("counter_replay_qualified") is not False or date < since):
            return
        bindings = data["metric_source_sha256"]
        if set(bindings) != set(roles.values()):
            return
        docs = {}
        for role, source_path in roles.items():
            blob = show(ref, source_path)
            if (blob is None or not isinstance(bindings[source_path], str)
                    or hashlib.sha256(blob.encode()).hexdigest() != bindings[source_path]):
                return
            docs[role] = json.loads(blob)
        receipt, raw, postrun = docs["receipt"], docs["raw"], docs["postrun"]
        export, validation = docs["export"], docs["validation"]
        controller = raw["controller"]
        if (bindings[roles["protocol"]] != "0b6e90a9cf9d79dd40fc43966c8aefd15cd6007feeb8ebf76f5ced3bb3149636"
                or receipt.get("schema") != "crypto.autoresearch.trial_receipt.v1"
                or receipt.get("run_id") != data["run_id"]
                or receipt.get("status") != data["native_status"]
                or type(receipt.get("returncode")) is not int or receipt.get("returncode") != 1
                or receipt.get("check_returncode") is not None
                or receipt["artifact_sha256"].get("raw-result.json") != bindings[roles["raw"]]
                or raw.get("experiment_id") != data["experiment_id"] or raw.get("run_id") != data["run_id"]
                or raw.get("operational_status") != "failed" or controller.get("status") != "failed"
                or controller.get("collection_complete") is not False or controller.get("files") != []
                or raw.get("scientific_validity") != "not_assessed"
                or postrun.get("status") != "incomplete" or postrun.get("wall_valid") is not False
                or postrun.get("scientific_validity") != "not_assessed"
                or postrun.get("counter_replay_qualified") is not False
                or export.get("schema") != "experiment.export/v1" or not isinstance(export.get("runs"), list)
                or validation.get("schema_compliant") is not True
                or validation.get("protocol_qualified") is not False
                or not isinstance(validation.get("findings"), list)
                or not all(isinstance(x, str) for x in validation["findings"])
                or validation["findings"] != postrun.get("export_findings")):
            return
        values = {
            "attempted_trials": 1,  # One actual native receipt, not protocol.planned.
            "completed_trials": 0,  # Retained native infrastructure_error terminal status.
            "failed_infrastructure_trials": 1,
            "timed_out_trials": 0,
            "vm_creates_recorded": controller["vm_creates"],
            "candidate_engine_execs_recorded": controller["engine_execs"],
            "retained_logical_evaluator_rows": len(export["runs"]),
            "missing_coverage_findings": len(validation["findings"]),
        }
        if (any(type(v) is not int or v < 0 for v in values.values())
                or values["candidate_engine_execs_recorded"] > values["vm_creates_recorded"]
                or values["retained_logical_evaluator_rows"] != 0
                or data["measured_counts"] != values
                or any(type(v) is not int for v in data["measured_counts"].values())):
            return
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    for name, value in values.items():
        emit(f"controlled.c8d9b0.{name}", value, date=date,
             problem="ecdlp-controlled-followup", unit="count", better="neutral",
             label=f"RUN-ECDLP-c8d9b0: {name.replace('_', ' ')} (operational/coverage only)",
             source=f"{path}@{ref}")


def controlled_followup_080f41_observations(ref, since):
    """Retained successor counts, with native failure and two shared rows.

    Resolve every source at the same committed ref. Large export payloads are
    identity blob pointers in Git: authenticate their identities and the plain
    verification/report/review facts, without a GET or pretending the payload
    is a plain Git JSON blob. This is descriptive custody, not reference replay.
    """
    path = "docs/reports/classical-ecdlp-controlled-followup-20261029/observations-080f41/observations.json"
    run = "experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237/"
    post = "experiments/EXP-ECDLP-080f41/postrun-from-view-346631/"
    reviews = "coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/reviews/"
    roles = {
        "receipt": run + "execution-receipt.json",
        "raw": run + "raw-result.json",
        "verification": post + "verification.json",
        "postrun": post + "postrun-result.json",
        "validation": post + "export.validation.json",
        "protocol": "experiments/EXP-ECDLP-080f41/protocol.json",
        "native_report": "experiments/EXP-ECDLP-080f41/reports/run-20261029T2258Z/observations.json",
        "source_export_pointer": post + "export.json.blob.json",
        "root_export_pointer": "experiments/EXP-ECDLP-080f41/export.json.blob.json",
        "integrity_review": reviews + "TASK-20261029-830629/experiment.review.json",
        "blind_review": reviews + "TASK-20261029-fe803f/experiment.review.json",
        "integrity_checks": reviews + "TASK-20261029-830629/checks.json",
    }
    try:
        text = show(ref, path)
        if text is None:
            return
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.controlled-followup.reviewed-observations/v1"
                or data.get("experiment_id") != "EXP-ECDLP-080f41"
                or data.get("run_id") != "RUN-ECDLP-939237" or date < since
                or data.get("native_status") != "invalid_output"
                or data.get("postrun_status") != "complete"
                or data.get("scientific_validity") != "not_assessed"
                or data.get("wall_valid") is not False
                or data.get("counter_replay_qualified") is not False):
            return
        bindings = data["metric_source_sha256"]
        if set(bindings) != set(roles.values()):
            return
        docs = {}
        for role, source in roles.items():
            blob = show(ref, source)
            if (blob is None or not isinstance(bindings[source], str)
                    or hashlib.sha256(blob.encode()).hexdigest() != bindings[source]):
                return
            docs[role] = json.loads(blob)
        receipt, raw = docs["receipt"], docs["raw"]
        verify, postrun, valid = docs["verification"], docs["postrun"], docs["validation"]
        native, integrity = docs["native_report"], docs["integrity_checks"]
        controller = raw["controller"]
        if (receipt.get("schema") != "crypto.autoresearch.trial_receipt.v1"
                or receipt.get("run_id") != data["run_id"]
                or receipt.get("status") != "invalid_output"
                or type(receipt.get("returncode")) is not int or receipt["returncode"] != 0
                or type(receipt.get("check_returncode")) is not int or receipt["check_returncode"] != 1
                or receipt.get("published") is not False
                or receipt["artifact_sha256"].get("raw-result.json") != bindings[roles["raw"]]
                or raw.get("run_id") != data["run_id"]
                or raw.get("experiment_id") != data["experiment_id"]
                or controller.get("status") != "complete"
                or controller.get("collection_complete") is not True
                or controller.get("vm_creates") != 1 or controller.get("engine_execs") != 1
                or native.get("run_id") != data["run_id"]
                or native.get("experiment_id") != data["experiment_id"]
                or native["controller"] != {k: controller[k] for k in (
                    "collection_complete", "engine_execs", "engine_returncode", "sandbox_id",
                    "status", "termination_ack", "uid1000_quiescent", "vm_creates")}
                or native.get("host_postrun_status") != "complete"
                or native.get("host_postrun_errors") != []
                or verify.get("status") != "checked"
                or verify.get("observed") != integrity["raw"]["counts"]
                or postrun.get("status") != "complete" or postrun.get("errors") != []
                or postrun.get("scientific_validity") != "not_assessed"
                or postrun.get("export_findings") != []
                or postrun.get("wall_valid") is not False
                or postrun.get("counter_replay_qualified") is not False
                or verify.get("wall_valid") is not False
                or verify.get("counter_replay_qualified") is not False
                or valid != {"findings": [], "protocol_qualified": True, "schema_compliant": True}
                or docs["protocol"].get("protocol_id") != data["experiment_id"]
                or docs["protocol"].get("freeze", {}).get("status") != "frozen"
                or docs["protocol"]["freeze"].get("protocol_sha256") != data["protocol_semantic_sha256"]):
            return
        views = data["export_views"]
        for view, role, review in (("source", "source_export_pointer", "integrity_review"),
                                   ("root_derivative", "root_export_pointer", "blind_review")):
            pointer, binding = docs[role], views[view]
            if (pointer.get("schema") != "crypto.autoresearch.blob_pointer.v1"
                    or pointer.get("encoding") != "identity"
                    or pointer.get("sha256") != binding["payload_sha256"]
                    or pointer.get("content_sha256") != binding["payload_sha256"]
                    or type(pointer.get("size")) is not int
                    or pointer["size"] != binding["payload_bytes"]
                    or pointer.get("content_size") != pointer["size"]
                    or pointer.get("uri") != ("s3://setec-astronomy-artifacts/store/sha256/"
                        + binding["payload_sha256"][:2] + "/" + binding["payload_sha256"])
                    or docs[review].get("schema") != "experiment.review/v1"
                    or docs[review]["export"]["sha256"] != binding["payload_sha256"]
                    or docs[review]["protocol_sha256"] != data["protocol_semantic_sha256"]):
                return
        rows = native["logical_evaluator_rows"]
        if (len(rows) != 2 or {row["run_id"] for row in rows} !=
                {data["run_id"] + ".original", data["run_id"] + ".incremental"}
                or any(row["instance_id"] != "candidate-vm" or row["replicate"] != 0
                       or row["status"] != "succeeded" for row in rows)):
            return
        by_arm = {row["arm"]: row["measurements"]["counted"] for row in rows}
        for arm, method in (("confirmation_original", "original"),
                            ("confirmation_incremental", "incremental")):
            if by_arm[arm] != integrity["raw"]["methods"][method]:
                return
        coverage, counted = native["coverage"], verify["observed"]
        summaries = native["recorded_summaries"]
        primary = next(x for x in summaries["six_cell_totals"] if x["cell"] == "t1.e2")
        if (coverage["retained_decoder_cells"] != counted["cells"]
                or coverage["retained_physical_trace_records"] != counted["traces"]
                or primary["candidate_events"] != integrity["raw"]["cell_summary"]["t1.e2"]["successes"]):
            return
        values = {
            "native_attempts": len([receipt]),
            "native_invalid_output_trials": int(receipt["status"] == "invalid_output"),
            "native_completed_trials": int(receipt["status"] == "output_validated"),
            "vm_creates_recorded": controller["vm_creates"],
            "candidate_engine_execs_recorded": controller["engine_execs"],
            "logical_evaluator_rows": len(rows),
            "retained_curves": coverage["retained_curves"],
            "retained_decoder_cells": counted["cells"],
            "retained_physical_traces": counted["traces"],
            "retained_single_records": counted["singles"],
            "retained_setups": counted["setups"],
            "paired_confirmation_attempts": integrity["raw"]["paired"],
            "original_strict_recovery_events": by_arm["confirmation_original"]["strict_recovered_events"],
            "incremental_strict_recovery_events": by_arm["confirmation_incremental"]["strict_recovered_events"],
            "primary_t1e2_recovery_events": primary["candidate_events"],
            "primary_t1e2_recovered_targets": primary["candidate_curve_target_pairs"],
            "primary_t1e2_recorded_uniform_events": primary["uniform_events"],
            "calibration_arm_records": summaries["calibration_summary"]["arm_records"],
            "calibration_undefined_draws": summaries["calibration_summary"]["undefined_draws"],
        }
        if (any(type(v) is not int or v < 0 for v in values.values())
                or data["measured_counts"] != values
                or any(type(v) is not int for v in data["measured_counts"].values())):
            return
    except (KeyError, TypeError, ValueError, AttributeError, StopIteration):
        return
    for name, value in values.items():
        emit(f"controlled.939237.{name}", value, date=date,
             problem="ecdlp-controlled-followup", unit="count", better="neutral",
             label=f"RUN-ECDLP-939237: {name.replace('_', ' ')} (retained observations; shared population)",
             source=f"{path}@{ref}")


def p256_factor_base_checks(ref, since):
    """Count completed engineering packages; this is no scientific verdict.

    Like the other exporters, read only committed bytes. Missing or malformed
    sources produce no sample, rather than an invented zero.
    """
    path = "research/p256_factor_base_parallel_20261025/status.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        record = json.loads(text)
        date = dt.date.fromisoformat(record["date"]).isoformat()
        tracks = record["tracks"]
    except (ValueError, KeyError, TypeError):
        return
    if date < since or not isinstance(tracks, list):
        return
    expected = {f"F{i}" for i in range(1, 9)}
    if (len(tracks) != 8 or any(not isinstance(t, dict) for t in tracks)
            or any(not isinstance(t.get("id"), str) for t in tracks)
            or {t.get("id") for t in tracks} != expected):
        return
    if any(not isinstance(t.get("implementation_status"), str) or
           t["implementation_status"] not in
           {"pending", "complete", "needs_correction"} for t in tracks):
        return
    complete = sum(t["implementation_status"] == "complete" for t in tracks)
    emit("p256.factor_base.implementation_packages", complete, date=date,
         problem="p256-factor-bases", unit="packages", better="neutral",
         label="P-256 direction packages with completed implementation checks (no scientific verdict)",
         source=f"{path}@{ref}")


def p256_factor_base_pass2_preparation(ref, since):
    """Committed source-readiness metadata; never an executed research result."""
    path = "research/p256_factor_base_parallel_20261026/status.json"
    text = show(ref, path)
    if text is None:
        return
    try:
        record = json.loads(text)
        date = dt.date.fromisoformat(record["date"]).isoformat()
        tracks = record["tracks"]
        allowed = {"pending", "in_progress", "needs_correction",
                   "source_and_draft_prepared_unexecuted",
                   "partial_source_preserved_after_platform_halt"}
        if not isinstance(tracks, list) or len(tracks) != 8 or date < since:
            return
        if not all(isinstance(t, dict) and isinstance(t.get("id"), str)
                   and isinstance(t.get("phase_a_status"), str)
                   and t["phase_a_status"] in allowed for t in tracks):
            return
        if {t["id"] for t in tracks} != {f"F{i}" for i in range(1, 9)}:
            return
    except (KeyError, TypeError, ValueError):
        return
    prepared = sum(t["phase_a_status"] == "source_and_draft_prepared_unexecuted"
                   for t in tracks)
    emit("p256.factor_base.pass2_source_packages", prepared, date=date,
         problem="p256-factor-bases", unit="packages", better="neutral",
         label="P-256 second-pass source packages prepared (no execution or scientific verdict)",
         source=f"{path}@{ref}")


def host_reference_audit_observations(ref, since):
    """Neutral retained-audit coverage, authenticated entirely at one Git ref.

    Read the small law/truth counts directly. Authenticate the large cost
    payload through its completed release and committed identity pointer plus
    modern manifest; never fetch or fall back to hydrated/worktree bytes.
    Coverage describes inspected records, never algorithm performance.
    """
    base = "coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/"
    path = "experiments/EXP-ECDLP-080f41/reports/review-DEC-20261030-c55f30/observations.json"
    owners = {"law": "TASK-20261030-3393bd", "truth": "TASK-20261030-88d5bd", "cost": "TASK-20261030-f55ebb"}
    def record(name, expected_sha):
        text = show(ref, name)
        if text is None or hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_sha:
            raise ValueError("missing or changed committed source")
        return json.loads(text)
    def count(value):
        if type(value) is not int or value < 0:
            raise ValueError("coverage must be a measured integer")
        return value
    try:
        text = show(ref, path)
        if text is None:
            return
        data = json.loads(text)
        date = dt.date.fromisoformat(data["recorded_at"][:10]).isoformat()
        if (data.get("schema") != "classical.ecdlp.host-reference-audit.observations/v1"
                or data.get("run_id") != "RUN-ECDLP-939237"
                or data.get("experiment_id") != "EXP-ECDLP-080f41"
                or data.get("batch_id") != "BATCH-128d4e" or date < since
                or data.get("source_launch_status") != "invalid_output"
                or data.get("check_returncode") != 1 or data.get("published") is not False
                or data.get("wall_valid") is not False
                or data.get("native_counter_replay_qualified") is not False
                or data.get("scientific_status_changed") is not False):
            return
        sources = data["metric_sources"]
        if set(sources) != set(owners):
            return
        plain = {}
        for role, task in owners.items():
            source = sources[role]
            logical = base + "reviews/" + task + "/checks.json"
            if source.get("task_id") != task or source.get("joint_id") != "J-" + role or source.get("path") != logical:
                return
            release_path = source["release_path"]
            prefix = base + "claims/" + task + "."
            epoch = release_path[len(prefix):-len(".release.json")] if release_path.startswith(prefix) and release_path.endswith(".release.json") else ""
            if not epoch.isdigit() or int(epoch) < 1:
                return
            release = record(release_path, source["release_sha256"])
            if (release.get("task_id") != task or release.get("outcome") != "completed"
                    or release.get("epoch") != int(epoch)
                    or release.get("artifact_sha256", {}).get(logical) != source["payload_sha256"]):
                return
            stored = source["stored_path"]
            if stored == logical:
                value = record(stored, source["stored_sha256"])
                if source["stored_sha256"] != source["payload_sha256"]:
                    return
                if value.get("task_id") != task:
                    return
                plain[role] = value
            elif stored == logical + ".blob.json":
                pointer = record(stored, source["stored_sha256"])
                digest = source["payload_sha256"]
                if (pointer.get("schema") != "crypto.autoresearch.blob_pointer.v1"
                        or pointer.get("encoding") != "identity"
                        or pointer.get("sha256") != digest or pointer.get("content_sha256") != digest
                        or pointer.get("size") != source["payload_bytes"]
                        or pointer.get("content_size") != source["payload_bytes"]
                        or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                        or pointer.get("uri") != "s3://setec-astronomy-artifacts/store/sha256/" + digest[:2] + "/" + digest):
                    return
                modern_path = base + "reviews/" + task + "/.artifacts.json"
                if source.get("modern_manifest_path") != modern_path:
                    return
                modern = record(modern_path, source["modern_manifest_sha256"])
                entry = modern.get("files", {}).get("checks.json", {})
                if modern.get("schema") != "artifacts.manifest/v1" or entry.get("sha256") != digest or entry.get("bytes") != source["payload_bytes"]:
                    return
            else:
                return
        if not {"law", "truth"} <= set(plain):
            return
        law = plain["law"]["phase2_retained_audit"]["totals"]
        truth = plain["truth"]["coverage"]
        checks = {
            "curves_checked": count(truth["curves"]),
            "orientation_draws_checked": count(law["null_draws"]),
            "uniform_rows_checked": count(truth["uniform_rows"]),
            "decoder_word_records_checked": count(truth["decoder_words"]),
            "decoder_public_equations_checked": count(truth["decoder_public_equations"]),
            "bsgs_final_equations_checked": count(truth["BSGS_targets"]),
            "prepared_setup_equations_checked": count(truth["setup_base_equations"]),
            "zero_budget_rows_checked": count(truth["uniform_M0_rows"]),
        }
        if (checks["uniform_rows_checked"] != count(law["uniform_rows"])
                or checks["decoder_word_records_checked"] != count(law["reconstructed_decoder_words"])
                or checks["zero_budget_rows_checked"] != count(law["uniform_zero_M"])):
            return
        values = data["audit_coverage"]
        if not isinstance(values, dict) or set(values) - set(checks):
            return
        output = []
        for name, expected in checks.items():
            actual = values.get(name)
            if actual is None:
                continue  # Unknown or missing is omitted, never zero-filled.
            if count(actual) != expected:
                return
            output.append((name, actual))
    except (KeyError, TypeError, ValueError, OverflowError, AttributeError):
        return
    for name, value in output:
        emit("audit.939237." + name, value, date=date, problem="ecdlp-host-reference-audit",
             unit="count", better="neutral", kind="gauge",
             label="RUN-ECDLP-939237: inspected " + name.replace("_", " "), source=path + "@" + ref)

def prime_field_fixed_panels(ref, since):
    """Exact completed-panel observations; method references are never summed."""
    date = '2026-10-30'
    if date < since:
        return
    for study, run, expected in [('b2', 'b2-fixed-panel-802e2a', 10),
                                  ('d1', 'd1-fixed-panel-a91d96', 8)]:
        path = f'research/prime_field_{study}_execution_20261030/runs/{run}/analysis.json'
        raw = show(ref, path)
        if raw is None:
            continue
        try:
            data = json.loads(raw)
            cells = data['cells']
            if data['panel_complete'] is not True or len(cells) != expected:
                continue
            if any(c['verified'] is not True or c['status'] != 'verified' for c in cells):
                continue
            if any(type(c['attempts']) is not int or c['attempts'] <= 0 for c in cells):
                continue
            if len({(c['cell_id'], c['arm']) if study == 'b2' else
                    (c['curve_uid'], c['target_index']) for c in cells}) != expected:
                continue
            if study == 'b2':
                gains = [(c['cell_id'], c['rank_gain']) for c in cells if c['arm'] == 'shifted']
                if len(gains) != 5 or any(type(g) is not int or not 0 <= g <= 15 for _, g in gains):
                    continue
            else:
                recoveries = [c['identified_target'] for c in cells]
                if any(type(v) is not int or v not in (0, 1) for v in recoveries):
                    continue
        except (ValueError, KeyError, TypeError):
            continue
        common = dict(date=date, problem='prime-field-factor-bases', better='neutral', source=f'{path}@{ref}')
        prefix = f'prym.prime_field.{study}'
        emit(prefix+'.collection_branches', sum(c['attempts'] for c in cells), unit='branches',
             label=f'{study.upper()} complete fixed panel, collection only; separate replay excluded', **common)
        emit(prefix+'.verified_cells', expected, unit='cells', label='Fixed cells with complete separate replay', **common)
        if study == 'b2':
            for name, gain in gains:
                emit(prefix+'.'+name+'.rank_gain', gain, unit='dimensions',
                     label='Additional rank on original15 columns, one fixed shifted subset', **common)
        else:
            emit(prefix+'.identified_targets', sum(recoveries), unit='targets',
                 label='Identified targets in frozen eight-target census; includes all coincidences', **common)


def prime_field_residual_panels(ref, since):
    """Completed A1/A2 observations; charge shared streams once per panel."""
    date='2026-10-30'
    if date<since:return
    for study,run,arms in [('a1','a1-fixed-panel-8e34c5',('smooth','pool16','pool32')),
                           ('a2','a2-fixed-panel-56d50d',('smooth','norm_completed'))]:
        path=f'research/prime_field_{study}_execution_20261030/runs/{run}/analysis.json';raw=show(ref,path)
        if raw is None:continue
        try:
            data=json.loads(raw);cells=data['cells'];expected={(b,a) for b in ('b13','b16') for a in arms}
            if data['panel_complete'] is not True or len(cells)!=len(expected) or {(c['cell_id'],c['arm']) for c in cells}!=expected:continue
            if any(c['verified'] is not True or c['status']!='verified' for c in cells):continue
            collection=data['physical_collection_attempts_observed'];replay=data['physical_replay_attempts_observed']
            if type(collection) is not int or type(replay) is not int or collection!=4587520 or replay!=collection:continue
            gain_key='delta' if study=='a1' else 'rank_gain'
            if any(type(c[gain_key]) is not int or not 0<=c[gain_key]<=15 for c in cells):continue
            if study=='a1' and any(type(c['direct_base_gain']) is not int or type(c['cross_row_cancellation_gain']) is not int or
                c['direct_base_gain']<0 or c['cross_row_cancellation_gain']<0 or c['direct_base_gain']+c['cross_row_cancellation_gain']!=c['delta'] or
                c['stacked_rank']-c['outside_rank']-c['base_rank_before']!=c['delta'] for c in cells):continue
        except (ValueError,KeyError,TypeError):continue
        common=dict(date=date,problem='prime-field-factor-bases',better='neutral',source=f'{path}@{ref}')
        prefix='prym.prime_field.'+study
        emit(prefix+'.collection_branches',collection,unit='branches',label='Shared complete physical collection, not sum of nested arm counts',**common)
        emit(prefix+'.replay_branches',replay,unit='branches',label='Separate complete branch replay',**common)
        emit(prefix+'.verified_cells',len(cells),unit='cells',label='Verified fixed arm/curve observations, not physical executions',**common)
        for c in cells:
            emit(prefix+'.'+c['cell_id']+'.'+c['arm']+'.base_rank_gain',c[gain_key],unit='dimensions',label='Additional rank on original15 base columns after any outside elimination',**common)



def exact_density_787704_observations(ref, since):
    """Exact fixed-population census; neutral counts, not an attack-cost claim.

    Only the two committed, small summaries are read. Missing, malformed or
    inconsistent sources emit no gauges (unknown), never fabricated zeroes.
    """
    import gzip
    import io
    from fractions import Fraction

    raw_path = "experiments/EXP-ECDLP-787704/runs/RUN-ECDLP-53b08d/summary.json.gz"
    review_path = ("coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-f7bbdf/"
                   "reviews/TASK-20261030-cd89e7/independent-summary.json")
    day = "2026-10-30"
    if day < since:
        return

    def read_committed(path, compressed=False):
        result = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"],
                                capture_output=True, timeout=10)
        if result.returncode or len(result.stdout) > 2 * 1024 * 1024:
            raise ValueError("missing/oversized committed source")
        data = result.stdout
        if compressed:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                data = stream.read(2 * 1024 * 1024 + 1)
        if len(data) > 2 * 1024 * 1024:
            raise ValueError("oversized decoded source")
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError("duplicate JSON key")
                value[key] = item
            return value
        def finite(value):
            raise ValueError("non-finite JSON")
        return json.loads(data, object_pairs_hook=unique, parse_constant=finite)

    def count(value):
        return type(value) is int and value >= 0

    try:
        raw = read_committed(raw_path, True)
        review = read_committed(review_path)
        if (not isinstance(raw, dict) or raw.get("status") != "complete"
                or raw.get("mode") != "census" or raw.get("attack_claimed") is not False
                or raw.get("wall_valid") is not False
                or review.get("schema") != "independent.exact-density.full-review-summary/v1"
                or review.get("run_id") != "RUN-ECDLP-53b08d"
                or review.get("experiment_id") != "EXP-ECDLP-787704"
                or review.get("no_advantage_cost_family_or_status_claim") is not True
                or review.get("joint_verdicts") != {"J-predicate": "holds",
                    "J-list-density-reference": "holds", "J-blinding": "holds", "J-integrity": "breaks"}):
            return
        curves = raw["curves"]
        certificates = review["curve_certificates"]
        if not isinstance(curves, list) or len(curves) != 48 or len(certificates) != 48:
            return
        domains = {}
        for i, (curve, certificate) in enumerate(zip(curves, certificates)):
            if (curve["curve_index"] != i or certificate["curve_index"] != i
                    or not isinstance(curve["curve_id"], str) or curve["curve_id"] in domains
                    or not count(curve["states"]) or curve["states"] == 0
                    or certificate["curve_id"] != curve["curve_id"]
                    or certificate["orbit_points"] != curve["states"] + 1
                    or certificate["python_native_query_equations"] != curve["states"] + 1
                    or not re.fullmatch(r"[0-9a-f]{64}", curve["sha256"])
                    or certificate["state_stream_sha256"] != curve["sha256"]):
                return
            domains[curve["curve_id"]] = (i, curve["states"])
        if len(raw["rows"]) != 288 or len(review["rows"]) != 288:
            return
        checked = {}
        totals = {(t, e): {"successes": 0, "positive": 0, "zero": 0, "M": 0}
                  for t in (0, 1, 2) for e in (0, 2)}
        raw_rows = {}
        for row in raw["rows"]:
            key = (row["curve_id"], row["radius"], row["erasure_cap"])
            if key in raw_rows:
                return
            raw_rows[key] = row
        for row in review["rows"]:
            key = (row["curve_id"], row["radius"], row["erasure_cap"])
            if key in checked or key not in raw_rows or key[1:] not in totals:
                return
            source = raw_rows[key]
            i, states = domains[key[0]]
            success = row["success_numerator"]
            size = row["sum_M"]
            if (not count(success) or success > states or not count(size)
                    or row["curve_index"] != i or row["states"] != states
                    or source["states"] != states or row["arm_id"] != "circuit2.a1"
                    or source["arm_id"] != "circuit2.a1"
                    or row["success_denominator"] != states
                    or row["uniform_numerator"] != size
                    or row["uniform_denominator"] != states ** 2
                    or source["q"] != [success, states]
                    or source["uniform_reference"] != [size, states ** 2]
                    or list(Fraction(success, states).as_integer_ratio()) != row["q_reduced"]
                    or list(Fraction(size, states ** 2).as_integer_ratio()) != row["uniform_reduced"]
                    or source["histograms"] != row["histograms"]):
                return
            fields = {"word_count": "words", "legal_count": "legal", "empty_count": "empty",
                      "zero_candidate_checks": "zero_checks", "M": "sumM", "success": "successes"}
            if any(not count(row["totals"][a]) or row["totals"][a] != source["totals"][b]
                   for a, b in fields.items()):
                return
            status = row["histograms"]["status"]
            if (any(not count(n) for n in status.values()) or sum(status.values()) != states
                    or status.get("RECOVERED", 0) != success):
                return
            checked[key] = (success, states, size)
            cell = totals[key[1:]]
            cell["successes"] += success
            cell["M"] += size
            cell["positive"] += int(success > 0)
            cell["zero"] += int(success == 0)
        if set(checked) != {(c, t, e) for c in domains for t, e in totals}:
            return
        states = sum(n for _, n in domains.values())
        if review["new_counts"] != {"new_states": states, "new_scalar_cells": states * 6,
                                     "orbit_points_including_identity": states + len(domains)}:
            return
        descriptive = review["descriptive_cell_totals"]
        if len(descriptive) != 6:
            return
        seen = set()
        for cell in descriptive:
            key = (cell["radius"], cell["erasure_cap"])
            if key in seen or key not in totals:
                return
            seen.add(key)
            exact = totals[key]
            if (cell["curves_with_zero_q"] != exact["zero"]
                    or cell["sum_successes"] != exact["successes"] or cell["sum_M"] != exact["M"]):
                return
        integrity = review["integrity"]
        if (integrity["native_returncode"] != 0 or integrity["native_check_returncode"] != 0
                or integrity["frozen_protocol_export_returncode"] != 1
                or len(integrity["findings"]) != 7):
            return
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OSError,
            EOFError, subprocess.TimeoutExpired):
        return

    common = dict(date=day, problem="ecdlp-coordinate-predicate", better="neutral",
                  source=f"{raw_path}@{ref}; {review_path}@{ref}")
    prefix = "ecdlp.exact_density.787704"
    for suffix, value, unit, label in [
        ("curves", len(domains), "curves", "Fixed functions enumerated and independently reconciled"),
        ("nonzero_states", states, "states", "Complete nonzero scalar domain; identity excluded"),
        ("scalar_cells", states * 6, "scalar/cells", "Six dependent cells, not independent trials"),
        ("orbit_points", states + len(domains), "points", "Orbit/query equations including all identities"),
        ("per_curve_cell_rows", len(checked), "rows", "Exact separate q and conditional-reference laws"),
        ("export_findings", len(integrity["findings"]), "findings", "Open historical frozen export defects; no mathematical verdict")]:
        emit(prefix + "." + suffix, value, unit=unit, label=label, **common)
    for (radius, cap), cell in sorted(totals.items()):
        cell_id = f"t{radius}.e{cap}"
        for suffix, value, unit, label in [
            ("curves_positive_q", cell["positive"], "curves", "Curves with exact q > 0; no transfer claim"),
            ("curves_zero_q", cell["zero"], "curves", "Curves with exact q = 0; tested functions only"),
            ("successful_states_sum", cell["successes"], "states", "Descriptive sum; not a pooled probability"),
            ("list_sizes_sum", cell["M"], "scalars", "Sum of retained nonzero list sizes; not primitive work")]:
            emit(prefix + "." + cell_id + "." + suffix, value, unit=unit,
                 label=f"{cell_id}: {label}", **common)


def main():
    a = args()
    census(a.ref, a.since)
    receipts(a.ref, a.since)
    runs(a.ref)
    prym_census(a.ref)
    prym_width(a.ref)
    prym_equation_diversity(a.ref)
    funnel(a.ref, a.since)
    claims(a.ref)
    endpoint_reuse_observations(a.ref, a.since)
    endpoint_reuse_sweep_observations(a.ref, a.since)
    nongeneric_screen_observations(a.ref, a.since)
    transfer_study_observations(a.ref, a.since)
    controlled_followup_observations(a.ref, a.since)
    controlled_followup_080f41_observations(a.ref, a.since)
    host_reference_audit_observations(a.ref, a.since)
    p256_factor_base_checks(a.ref, a.since)
    p256_factor_base_pass2_preparation(a.ref, a.since)
    prime_field_fixed_panels(a.ref, a.since)
    prime_field_residual_panels(a.ref, a.since)
    exact_density_787704_observations(a.ref, a.since)


if __name__ == "__main__":
    main()
