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
  analysis/semaev-degree-five-quotient-lift/reports/highmem-progress-*/progress.json
                                             reported continuation input/stage counts
  experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/verification.json
                                             completed finite Prym census counts/ranks
  experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/verification.json
                                             completed width16 Prym counts/ranks
Run: python3 tools/progress_metrics.py [--ref origin/main] [--since YYYY-MM-DD]
"""
# ---- committed-state progress-metrics exporter contract ----
# Contract: print one JSON object per line to stdout. Fields: metric, value, date (YYYY-MM-DD),
# problem, unit, better (higher|lower|neutral), kind (gauge|event), label, source.
# Reads committed state at --ref via `git show`; never the working tree. stdlib only.
import argparse
import hashlib
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
import hashlib
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


ICPERF_RUNS = {
    "EXP-ICPERF-283a70": {
        "RUN-ICPERF-0ef41e": "ctl-neg-wrong-triple",
        "RUN-ICPERF-74e9a2": "ctl-neg-support-zero",
        "RUN-ICPERF-f21eb1": "geometric-probe-sample",
    },
    "EXP-ICPERF-284bc4": {
        "RUN-ICPERF-2c627f": "ctl-consistency-r-change",
        "RUN-ICPERF-2d715d": "ctl-consistency-a-change",
        "RUN-ICPERF-30596e": "ctl-neg-perturbed-price",
        "RUN-ICPERF-779d41": "ctl-bsgs-enumeration",
        "RUN-ICPERF-850008": "ctl-neg-precomputation-model",
        "RUN-ICPERF-8e3acd": "price-ratio-identity",
    },
}


def icperf_trials(ref, since):
    """Export only ICPERF rows whose committed raw output and receipt agree."""
    all_rows = []
    for exp_id, expected_runs in ICPERF_RUNS.items():
        schema = f"crypto.autoresearch.{exp_id.lower()}.stage0.v2"
        rows = []
        for run_id, trial_id in expected_runs.items():
            base = f"experiments/{exp_id}/runs/{run_id}"
            raw_path = f"{base}/raw-result.json"
            receipt_path = f"{base}/execution-receipt.json"
            manifest_path = f"{base}/manifest.yaml"
            raw_text, receipt_text, manifest_text = (show(ref, p) for p in (raw_path, receipt_path, manifest_path))
            if None in (raw_text, receipt_text, manifest_text):
                return
            try:
                raw = json.loads(raw_text)
                receipt = json.loads(receipt_text)
            except (ValueError, TypeError):
                return
            hashes = receipt.get("artifact_sha256") if isinstance(receipt, dict) else None
            completion = receipt.get("manifest_completion") if isinstance(receipt, dict) else None
            if (not isinstance(raw, dict) or raw.get("schema") != schema or raw.get("experiment_id") != exp_id
                    or raw.get("run_id") != run_id or raw.get("trial_id") != trial_id
                    or raw.get("attack_claimed") is not False
                    or not isinstance(receipt, dict) or receipt.get("schema") != "crypto.autoresearch.trial_receipt.v1"
                    or receipt.get("run_id") != run_id or receipt.get("trial_id") != trial_id
                    or receipt.get("status") != "output_validated" or receipt.get("returncode") != 0
                    or receipt.get("check_returncode") != 0 or not isinstance(hashes, dict)
                    or hashes.get("raw-result.json") != hashlib.sha256(raw_text.encode()).hexdigest()
                    or hashes.get("manifest.yaml") != hashlib.sha256(manifest_text.encode()).hexdigest()
                    or not isinstance(completion, dict)
                    or completion.get("driver_manifest_sha256") != hashes.get("manifest.yaml")):
                return
            required_fields = (("n_targets", "sample_sum", "median") if exp_id == "EXP-ICPERF-283a70"
                               else ("states", "c_probe_ns", "c_state_ns", "c_step_ns"))
            if any(type(raw.get(field)) not in (int, float) or not math.isfinite(raw[field])
                   for field in required_fields):
                return
            finished = receipt.get("finished_at")
            if not isinstance(finished, str) or len(finished) < 10:
                return
            day = finished[:10]
            try:
                dt.date.fromisoformat(day)
            except ValueError:
                return
            rows.append((exp_id, run_id, trial_id, raw, day, raw_path, receipt_path))
        all_rows.extend(rows)

    # Validate the complete nine-row cohort before emitting any partial counts.
    if len(all_rows) != sum(len(x) for x in ICPERF_RUNS.values()):
        return
    for exp_id, run_id, trial_id, raw, day, raw_path, receipt_path in all_rows:
        if day < since:
            continue
        source = f"{raw_path} + {receipt_path}@{ref}"
        emit(f"icperf.{exp_id}.validated_trials", 1, date=day, problem="icperf", unit="trial records",
             kind="event", label=f"{exp_id} validated completed trial {trial_id}", source=source)
        if exp_id == "EXP-ICPERF-283a70":
            fields = (("n_targets", "target samples"), ("sample_sum", "probe-count sum"),
                      ("median", "probes per target"))
        else:
            fields = (("states", "model states"), ("c_probe_ns", "nanoseconds per probe"),
                      ("c_state_ns", "nanoseconds per state"), ("c_step_ns", "nanoseconds per step"),
                      ("price_ratio_num", "dimensionless ratio numerator"),
                      ("price_ratio_den", "dimensionless ratio denominator"))
        for field, unit in fields:
            value = raw.get(field)
            if type(value) in (int, float) and math.isfinite(value):
                emit(f"icperf.{exp_id}.{trial_id}.{field}", value, date=day, problem="icperf", unit=unit,
                     better="neutral", label=f"{exp_id} {trial_id}: {field}", source=source)


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


def prime_field_direct_panel(ref, since):
    """A3 exact relation equivalence; enumerate descriptors and table queries separately."""
    date='2026-10-30'
    if date<since:return
    path='research/prime_field_a3_execution_20261030/runs/a3-fixed-panel-0cddd8/analysis.json'
    raw=show(ref,path)
    if raw is None:return
    try:
        data=json.loads(raw);cells=data['cells']
        expected={(b,a) for b in ('b13','b16') for a in ('enumeration','pair_table')}
        if data['panel_complete']is not True or len(cells)!=4 or {(c['cell_id'],c['arm']) for c in cells}!=expected:return
        for cell in cells:
            if cell['verified']is not True or cell['status']!='verified':return
            for key in ('accepted_witnesses','distinct_equations','new_rank','combined_rank','rank_gain','attempts'):
                if type(cell[key])is not int or cell[key]<0:return
            if (cell['distinct_equations']>cell['accepted_witnesses'] or cell['new_rank']>15 or cell['combined_rank']>15 or
                cell['rank_gain']>cell['combined_rank'] or cell['attempts']!=(286720 if cell['arm']=='enumeration' else 2048)):return
        for case in ('b13','b16'):
            selected=[c for c in cells if c['cell_id']==case]
            if any(selected[0][key]!=selected[1][key] for key in ('accepted_witnesses','distinct_equations','new_rank','combined_rank','rank_gain')):return
    except (ValueError,KeyError,TypeError):return
    common=dict(date=date,problem='prime-field-factor-bases',better='neutral',source=f'{path}@{ref}')
    prefix='prym.prime_field.a3'
    for arm,unit in (('enumeration','descriptors'),('pair_table','queries')):
        emit(prefix+'.'+arm+'.collection_'+unit,sum(c['attempts'] for c in cells if c['arm']==arm),unit=unit,
             label='Complete direct collection; enumeration descriptors and table queries are different units',**common)
    emit(prefix+'.verified_cells',len(cells),unit='cells',label='Four matched arm/curve observations in one physical execution',**common)
    for cell in cells:
        for key,unit in (('distinct_equations','equations'),('rank_gain','dimensions')):
            emit(prefix+'.'+cell['cell_id']+'.'+cell['arm']+'.'+key,cell[key],unit=unit,label='Exact original-base direct relation observation',**common)


def prime_field_holdout_panel(ref, since):
    """A4 verified holdouts; shared collection once, prefix recoveries separately."""
    date='2026-10-30'
    if date<since:return
    path='research/prime_field_a4_execution_20261030/runs/a4-holdout-panel-c47bc8/analysis.json';raw=show(ref,path)
    if raw is None:return
    try:
        data=json.loads(raw);cells=data['cells'];ids=[f'p{p}-i{i}' for p in (8191,65537) for i in (0,1)]
        expected={(i,n) for i in ids for n in (0,16,64)}
        if data['panel_complete']is not True or len(cells)!=12 or {(c['cell_id'],c['prefix']) for c in cells}!=expected:return
        for c in cells:
            if c['verified']is not True or c['status']!='verified':return
            for k in ('base_columns','base_rank','base_nullity','single_targets','joint_targets','early_joint_targets','source_queries','target_queries','pair_entries'):
                if type(c[k])is not int or c[k]<0:return
            n=16 if c['cell_id'].startswith('p8191-') else 32
            if (c['base_rank']+c['base_nullity']!=c['base_columns'] or c['base_columns']>n or max(c['single_targets'],c['joint_targets'])>8 or
                c['early_joint_targets']>c['joint_targets'] or (c['source_queries'],c['target_queries'],c['pair_entries'])!=(64*n*2,8*n*2,n*(n-1)*2)):return
    except (ValueError,KeyError,TypeError):return
    common=dict(date=date,problem='prime-field-factor-bases',better='neutral',source=f'{path}@{ref}');prefix='prym.prime_field.a4'
    for k,unit in (('source_queries','queries'),('target_queries','queries'),('pair_entries','entries')):
        emit(prefix+'.'+k,sum(c[k] for c in cells if c['prefix']==0),unit=unit,label='Shared physical collection counted once, not once per prefix',**common)
    for c in cells:
        for k,unit in (('base_rank','dimensions'),('single_targets','targets'),('joint_targets','targets'),('early_joint_targets','targets')):
            emit(prefix+'.'+c['cell_id']+'.prefix'+str(c['prefix'])+'.'+k,c[k],unit=unit,label='Exact held-out curve/prefix observation',**common)


def degree_five_continuation(ref, since):
    """Latest committed high-memory snapshot per day, including capped inputs.

    Count reported records only: this does not replay certificates, infer a
    solving-degree result from a cap, or turn pending work into an observation.
    """
    root = "analysis/semaev-degree-five-quotient-lift/reports/"
    latest = {}
    for path in ls(ref, root):
        if not re.fullmatch(re.escape(root) + r"highmem-progress-\d+/progress\.json", path):
            continue
        try:
            data = json.loads(show(ref, path))
            stamp = dt.datetime.fromisoformat(data["created_at"])
            if stamp.tzinfo is None:
                return
            stamp = stamp.astimezone(dt.timezone.utc)
        except (ValueError, TypeError, KeyError):
            return
        date = stamp.date().isoformat()
        if date < since:
            continue
        old = latest.get(date)
        if old is not None and stamp == old[0] and data != old[2]:
            return  # Ambiguous same-time snapshots are not a choice of evidence.
        if old is None or stamp > old[0]:
            latest[date] = (stamp, path, data)
    terminal_statuses = {"certificate_verified", "projection_kills_one", "resource_capped"}
    for date, (_, path, data) in sorted(latest.items()):
        try:
            rows = data["rows"]
            if not isinstance(rows, list) or data["missing_publications"] != []:
                continue
            if type(data["planned"]) is not int or data["planned"] != len(rows):
                continue
            if (any(not isinstance(row["id"], str) or not row["id"] for row in rows)
                    or len({row["id"] for row in rows}) != len(rows)):
                continue
            counts = collections.Counter(row["status"] for row in rows)
            if set(counts) - terminal_statuses - {"pending"}:
                continue
            if (any(type(v) is not int for v in data["statuses"].values())
                    or dict(counts) != data["statuses"]
                    or type(data["terminal"]) is not int
                    or data["terminal"] != sum(counts[s] for s in terminal_statuses)):
                continue
            stages = []
            for row in rows:
                if not isinstance(row["stages"], list):
                    raise ValueError("invalid stage records")
                if row["status"] == "pending" and row["stages"]:
                    raise ValueError("pending input has reported stages")
                for stage in row["stages"]:
                    if (type(stage["degree"]) is not int or stage["degree"] < 0
                            or type(stage["certified_codimension"]) is not int
                            or stage["certified_codimension"] < 0
                            or type(stage["exact_solutions"]) is not int
                            or stage["exact_solutions"] < 0
                            or not isinstance(stage["certificate_sha256"], str)
                            or re.fullmatch(r"[0-9a-f]{64}", stage["certificate_sha256"]) is None):
                        raise ValueError("invalid reported certificate record")
                    stages.append(stage)
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        common = dict(date=date, problem="semaev-degree-five-quotient-lift", better="neutral",
                      source=f"{path}@{ref}")
        prefix = "semaev.degree_five.highmem."
        emit(prefix + "terminal_inputs", data["terminal"], unit="inputs",
             label="Reported terminal inputs, including resource caps", **common)
        for status in sorted(terminal_statuses | {"pending"}):
            emit(prefix + status + "_inputs", counts[status], unit="inputs",
                 label=f"Reported continuation inputs: {status}", **common)
        for degree in (4, 5):
            emit(prefix + f"degree{degree}_certificate_records",
                 sum(stage["degree"] == degree for stage in stages), unit="stage records",
                 label=f"Reported degree-{degree} certificate records; not a fresh replay", **common)


def semaev_panel_snapshots(ref, since):
    """Report hash-bound panel inventories; never replay or infer upper bounds."""
    root = "analysis/semaev-degree-five-quotient-lift/"
    latest = {}
    ambiguous = set()
    for path in ls(ref, root + "runtime/"):
        if not re.fullmatch(re.escape(root) + r"runtime/panel-remaining-after-local\d+\.json", path):
            continue
        try:
            d = json.loads(show(ref, path))
            stamp = dt.datetime.fromisoformat(d["created_at"])
            if stamp.tzinfo is None:
                continue
            stamp = stamp.astimezone(dt.timezone.utc)
            date = stamp.date().isoformat()
            if date < since:
                continue
            if date in latest and stamp == latest[date][0]:
                ambiguous.add(date)  # Refuse a tie only if it remains newest.
            if date not in latest or stamp > latest[date][0]:
                latest[date] = (stamp, path, d)
                ambiguous.discard(date)
        except (ValueError, TypeError, KeyError):
            continue
    for date, (_, path, d) in sorted(latest.items()):
        if date in ambiguous:
            continue
        try:
            parent = show(ref, root + d["parent_inventory"])
            if hashlib.sha256(parent.encode()).hexdigest() != d["parent_sha256"]:
                continue
            planned = [x["prior_id"] for x in json.loads(parent)["items"]]
            pending = [x["prior_id"] for x in d["items"]]
            terminal = d["terminal_inputs"]
            if (len(set(planned)) != len(planned) or len(set(pending)) != len(pending)
                    or set(pending) & set(terminal)
                    or set(planned) != set(pending) | set(terminal)):
                continue
            certified = 0
            for name, entry in terminal.items():
                raw = show(ref, root + entry["path"])
                if hashlib.sha256(raw.encode()).hexdigest() != entry["result_sha256"]:
                    raise ValueError("result hash mismatch")
                result = json.loads(raw)
                if result["prior_id"] != name or result["status"] != entry["status"]:
                    raise ValueError("result identity mismatch")
                if result["status"] not in {"certificate_verified", "producer_contains_one", "resource_capped"}:
                    raise ValueError("not a terminal panel result")
                bound = result.get("last_fall_degree_lower_bound")
                if bound != entry.get("last_fall_degree_lower_bound"):
                    raise ValueError("bound mismatch")
                if bound is not None:
                    q, count = result["certified_codimension_lower_bound"], result["exact_solutions"]
                    if (bound != 5 or result["status"] != "certificate_verified"
                            or type(q) is not int or type(count) is not int or not q > count >= 0):
                        raise ValueError("reported lower bound is unsupported")
                    certified += 1
            if d["terminal_count"] != len(terminal) or d["certified_lfd_at_least5"] != certified:
                continue
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        for suffix, value, label in [
            ("terminal_inputs", len(terminal), "Reported terminal original panel inputs, including caps"),
            ("pending_inputs", len(pending), "Original panel inputs without terminal records"),
            ("certified_lfd_at_least5_inputs", certified, "Reported checked named-instance lower bounds; not a fresh certificate replay"),
        ]:
            emit("semaev.degree_four.panel." + suffix, value, date=date,
                 problem="semaev-degree-five-quotient-lift", unit="inputs", better="neutral",
                 label=label, source=f"{path}@{ref}")


def main():
    a = args()
    census(a.ref, a.since)
    receipts(a.ref, a.since)
    runs(a.ref)
    icperf_trials(a.ref, a.since)
    prym_census(a.ref)
    prym_width(a.ref)
    prym_equation_diversity(a.ref)
    funnel(a.ref, a.since)
    claims(a.ref)
    p256_factor_base_checks(a.ref, a.since)
    p256_factor_base_pass2_preparation(a.ref, a.since)
    prime_field_fixed_panels(a.ref, a.since)
    prime_field_residual_panels(a.ref, a.since)
    prime_field_direct_panel(a.ref, a.since)
    prime_field_holdout_panel(a.ref, a.since)
    degree_five_continuation(a.ref, a.since)
    semaev_panel_snapshots(a.ref, a.since)


if __name__ == "__main__":
    main()
