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


def main():
    a = args()
    census(a.ref, a.since)
    receipts(a.ref, a.since)
    runs(a.ref)
    prym_census(a.ref)
    prym_width(a.ref)
    funnel(a.ref, a.since)
    claims(a.ref)
    endpoint_reuse_observations(a.ref, a.since)
    endpoint_reuse_sweep_observations(a.ref, a.since)
    nongeneric_screen_observations(a.ref, a.since)
    transfer_study_observations(a.ref, a.since)
    controlled_followup_observations(a.ref, a.since)
    p256_factor_base_checks(a.ref, a.since)
    p256_factor_base_pass2_preparation(a.ref, a.since)


if __name__ == "__main__":
    main()
