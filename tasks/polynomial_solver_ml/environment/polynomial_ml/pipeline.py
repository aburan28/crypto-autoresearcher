"""Generate, measure, train, evaluate and retain a complete bounded software run."""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

import numpy as np

from .instances import FEATURE_NAMES, canonical, features, generate_cases, original_roots
from .solver import ACTIONS

run_child = subprocess.run


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def source_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob("*.py"))}


def artifact_hashes(out):
    return {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"}


def cost_table(cases, labels):
    indexes = {c["id"]: i for i, c in enumerate(cases)}
    table = np.full((len(cases), len(ACTIONS)), np.nan)
    for label in labels:
        i, a = indexes[label["case_id"]], label["action_id"]
        if type(a) is not int or not 0 <= a < len(ACTIONS) or np.isfinite(table[i, a]):
            raise ValueError("duplicate or invalid action label")
        if label["status"] not in ("completed", "timed_out"):
            raise ValueError("implementation failures are not training costs")
        table[i, a] = label["cost_seconds"]
    if not np.isfinite(table).all() or (table <= 0).any():
        raise ValueError("missing, nonfinite, or nonpositive costs")
    return table


def evaluate(cases, costs, choices):
    costs = np.asarray(costs, dtype=float)
    if costs.shape != (len(cases), len(ACTIONS)) or not np.isfinite(costs).all() or (costs <= 0).any():
        raise ValueError("invalid evaluation cost table")
    for selected in choices.values():
        selected = np.asarray(selected)
        if (selected.shape != (len(cases),) or selected.dtype.kind not in "iu"
                or (selected < 0).any() or (selected >= len(ACTIONS)).any()):
            raise ValueError("invalid action selections")
    result = {}
    for split in ("train", "validation", "test", "test_unseen_family"):
        indexes = np.array([i for i, c in enumerate(cases) if c["split"] == split], dtype=int)
        if not len(indexes):
            continue
        base = float(costs[indexes, 0].mean())
        methods = {}
        for name, selected in choices.items():
            selected = np.asarray(selected, dtype=int)
            values = costs[indexes, selected[indexes]]
            mean = float(values.mean())
            methods[name] = {"mean_par2_seconds": mean, "speedup_vs_fixed": base / mean,
                             "actions": selected[indexes].tolist(), "case_costs_seconds": values.tolist()}
        uniform = float(costs[indexes].mean())
        oracle = float(costs[indexes].min(axis=1).mean())
        methods["uniform_expected"] = {"mean_par2_seconds": uniform, "speedup_vs_fixed": base / uniform}
        methods["retrospective_oracle"] = {"mean_par2_seconds": oracle, "speedup_vs_fixed": base / oracle,
                                           "deployable": False}
        result[split] = {"count": len(indexes), "case_ids": [cases[i]["id"] for i in indexes], "methods": methods}
    return result


def report_markdown(evaluation, overhead, labels, controls):
    lines = ["# Polynomial solver selection — software run", "",
             "Measured costs on generated, bounded polynomial systems. No elliptic-curve or cryptanalytic task.", "",
             "| Split | Selector | Mean PAR-2 cost (ms) | Speedup vs fixed |", "|---|---|---:|---:|"]
    for split, data in evaluation.items():
        for method, stats in data["methods"].items():
            lines.append(f"| {split} | {method} | {stats['mean_par2_seconds'] * 1000:.3f} | {stats['speedup_vs_fixed']:.3f}× |")
    lines += ["", "## What the numbers mean", "",
              "The RL learner is a one-step contextual bandit trained offline on a fully measured training table. "
              "The retrospective oracle uses outcomes and cannot be deployed as a selector. "
              "PAR-2 charges a timeout twice its configured limit. Failed solves are never counted as fast.", "",
              "Root extraction exhaustively evaluates the output basis over a small field grid. "
              "Output basis degree is recorded; intermediate degree, operation counts, and degree of regularity are not measured. "
              "Microbenchmark timing and a single fit seed do not establish an asymptotic result or broad generalization.", "",
              f"Completed actions: {sum(r['status'] == 'completed' for r in labels)} / {len(labels)}. "
              f"Censored actions: {sum(r['status'] == 'timed_out' for r in labels)}.", "",
              "## Full cost accounting", ""]
    for name, seconds in overhead.items():
        lines.append(f"- {name}: {seconds:.6f} seconds")
    peaks = [r["peak_rss_bytes"] for r in labels if r["status"] == "completed"]
    lines += [f"- Largest measured solver subprocess RSS: {max(peaks, default=0)} bytes.", "",
              "Controls and raw per-action observations are in controls.json and labels.jsonl. "
              "A valid learner may be slower than a fixed configuration. Timings exclude neither "
              "label acquisition nor fitting from the reported full-run overhead.", ""]
    return "\n".join(lines)


def run(out, profile="quick", seed=20260904, fit_seed=0, action_timeout=5.0, budget_seconds=600.0, steps=1200):
    from . import learning
    out = Path(out).resolve()
    if not 0.1 <= action_timeout <= 10 or not 1 <= budget_seconds <= 600:
        raise ValueError("action timeout must be 0.1..10s and run budget 1..600s")
    if not 1 <= steps <= 5000 or not 0 <= seed < 2**32 or not 0 <= fit_seed < 2**32:
        raise ValueError("invalid training steps or seed")
    started, start_clock = timestamp(), time.monotonic()
    generation_start = time.monotonic()
    cases = generate_cases(profile, seed)
    generation_seconds = time.monotonic() - generation_start
    repetitions = 1 if profile == "quick" else 2
    out.mkdir(parents=True, exist_ok=False)
    (out / "logs").mkdir()
    deadline = start_clock + budget_seconds
    config = {"schema_version": 1, "profile": profile, "seed": seed, "fit_seed": fit_seed,
              "steps": steps, "action_timeout_seconds": action_timeout, "budget_seconds": budget_seconds,
              "repetitions": repetitions, "actions": ACTIONS, "feature_names": FEATURE_NAMES,
              "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd())}
    write_json(out / "config.json", config)
    write_json(out / "cases.json", cases)
    overhead = {"input_generation": generation_seconds}
    labels = []
    status, failure = "failed", None
    frozen_sources = source_hashes()
    try:
        oracle_start = time.monotonic()
        roots = {case["id"]: original_roots(case) for case in cases}
        overhead["independent_root_oracle"] = time.monotonic() - oracle_start
        jobs = [(c, a) for c in cases for a in range(len(ACTIONS))]
        random.Random(seed).shuffle(jobs)
        write_json(out / "measurement_order.json", [[c["id"], a] for c, a in jobs])
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent)
        for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
            env[key] = "1"
        measure_start = time.monotonic()
        with (out / "labels.jsonl").open("x") as stream:
            for j, (case, action) in enumerate(jobs):
                if deadline - time.monotonic() < action_timeout:
                    raise TimeoutError("global run budget exhausted before next action")
                payload = {"case": case, "action_id": action, "repetitions": repetitions}
                t0 = time.monotonic()
                return_code = None
                try:
                    completed = run_child([sys.executable, "-m", "polynomial_ml", "worker"],
                                               input=json.dumps(payload), capture_output=True, text=True,
                                               timeout=action_timeout, env=env)
                    stdout, stderr = completed.stdout, completed.stderr
                    return_code = completed.returncode
                    outcome = "returned"
                except subprocess.TimeoutExpired as error:
                    stdout, stderr = error.stdout or b"", error.stderr or b""
                    stdout = stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout
                    stderr = stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr
                    outcome = "timed_out"
                elapsed = time.monotonic() - t0
                logbase = f"logs/{case['id']}-{action}"
                (out / (logbase + ".stdout.txt")).write_text(stdout)
                (out / (logbase + ".stderr.txt")).write_text(stderr)
                if outcome == "timed_out":
                    label = {"case_id": case["id"], "action_id": action, "status": "timed_out",
                             "cost_seconds": 2 * action_timeout, "censored": True, "roots": None}
                else:
                    if return_code != 0:
                        raise RuntimeError(f"solver child exited {return_code}; see {logbase}.stderr.txt")
                    label = json.loads(stdout)
                    if label["case_id"] != case["id"] or label["action_id"] != action:
                        raise ValueError("solver returned wrong case/action identity")
                    if label["roots"] != roots[case["id"]]:
                        raise ValueError("solver roots disagree with independent complete enumeration")
                    label["censored"] = False
                label.update({"process_wall_seconds": elapsed, "limit_seconds": action_timeout,
                              "return_code": return_code, "stdout_path": logbase + ".stdout.txt",
                              "stderr_path": logbase + ".stderr.txt", "recorded_at": timestamp()})
                labels.append(label)
                stream.write(json.dumps(label, allow_nan=False) + "\n")
                stream.flush()
                if j % 12 == 0 or j + 1 == len(jobs):
                    print(f"measured {j + 1}/{len(jobs)} actions ({time.monotonic() - start_clock:.1f}s)", flush=True)
        overhead["label_acquisition_including_subprocess_startup"] = time.monotonic() - measure_start
        costs = cost_table(cases, labels)
        if any(all(r["status"] != "completed" for r in labels if r["case_id"] == c["id"]) for c in cases):
            raise ValueError("at least one case has no completed solver action")
        t0 = time.monotonic()
        x = np.asarray([features(c) for c in cases], dtype=float)
        overhead["input_feature_extraction"] = time.monotonic() - t0
        train_mask = np.array([c["split"] == "train" for c in cases])
        t0 = time.monotonic()
        model = learning.train(x[train_mask], costs[train_mask], seed=fit_seed, steps=steps)
        model["training_case_ids"] = [c["id"] for c in cases if c["split"] == "train"]
        model["feature_names"] = list(FEATURE_NAMES)
        write_json(out / "models.json", model)
        overhead["model_fitting"] = time.monotonic() - t0
        t0 = time.monotonic()
        choices = learning.select(model, x)
        overhead["model_selection"] = time.monotonic() - t0
        choices["fixed"] = np.zeros(len(cases), dtype=int)
        choices["train_best_fixed"] = np.full(len(cases), int(np.argmin(costs[train_mask].mean(axis=0))))
        choices["uniform_seeded"] = np.random.default_rng(fit_seed).integers(len(ACTIONS), size=len(cases))
        evaluation = evaluate(cases, costs, choices)
        write_json(out / "evaluation.json", evaluation)
        t0 = time.monotonic()
        controls = learning.controls(seed=fit_seed)
        shuffled = costs[train_mask].copy()
        rng = np.random.default_rng(fit_seed + 1)
        for row in shuffled:
            rng.shuffle(row)
        null_model = learning.train(x[train_mask], shuffled, seed=fit_seed, steps=steps)
        null_choices = learning.select(null_model, x)
        controls["shuffled_training_labels"] = {
            "scope": "Diagnostic only; no finite-sample null-performance threshold.",
            "evaluation": evaluate(cases, costs, null_choices)}
        write_json(out / "controls.json", controls)
        overhead["controls_including_separate_null_fit"] = time.monotonic() - t0
        if not controls["positive_passed"] or not controls["constant_passed"]:
            raise ValueError("learner software control failed")
        if time.monotonic() > deadline:
            raise TimeoutError("global run budget exhausted")
        if source_hashes() != frozen_sources:
            raise RuntimeError("source files changed during run")
        overhead["pipeline_wall_total"] = time.monotonic() - start_clock
        (out / "report.md").write_text(report_markdown(evaluation, overhead, labels, controls))
        status = "completed"
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error)}
    finally:
        versions = {name: importlib.metadata.version(name) for name in ("numpy", "sympy")}
        write_json(out / "manifest.json", {"schema_version": 1, "kind": "software_benchmark_run",
                   "status": status, "failure": failure, "started_at": started, "finished_at": timestamp(),
                   "elapsed_wall_seconds": time.monotonic() - start_clock, "python": sys.version,
                   "platform": platform.platform(), "dependencies": versions, "source_sha256": frozen_sources,
                   "artifact_sha256": artifact_hashes(out), "measured_actions": len(labels),
                   "expected_actions": len(cases) * len(ACTIONS), "overhead_seconds": overhead,
                   "scope": "Synthetic general polynomial systems; no research ledger promotion.",
                   "timing_authentication": "Self-produced measurements; hashes detect corruption, not a malicious producer."})
    if failure:
        raise RuntimeError(f"run failed; artifacts preserved at {out}: {failure['message']}")
    return out
