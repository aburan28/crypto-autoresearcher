"""Read-only artifact verification, independent scalar roots and metric arithmetic.

This detects inconsistent software runs. It does not authenticate timings against
a malicious producer. Model replay uses the learning implementation by design.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import random
from statistics import median
import time

import numpy as np

from .instances import FEATURE_NAMES, features, generate_cases, original_roots
from .solver import ACTIONS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def reject_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")
    return json.loads(Path(path).read_text(), parse_constant=reject_constant)


def close(actual, expected, label):
    require(type(actual) in (int, float) and math.isfinite(actual), f"invalid {label}")
    require(math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12), f"inconsistent {label}")


def check_evaluation(record, cases, costs, choices):
    splits = ("train", "validation", "test", "test_unseen_family")
    require(set(record) == set(splits), "evaluation splits changed")
    for split in splits:
        indexes = [i for i, case in enumerate(cases) if case["split"] == split]
        data = record[split]
        require(data["count"] == len(indexes), "wrong split count")
        require(data["case_ids"] == [cases[i]["id"] for i in indexes], "evaluation case order changed")
        base = sum(float(costs[i, 0]) for i in indexes) / len(indexes)
        require(set(data["methods"]) == set(choices) | {"uniform_expected", "retrospective_oracle"},
                "missing or unexpected evaluation method")
        for name, actions in choices.items():
            values = [float(costs[i, int(actions[i])]) for i in indexes]
            observed = data["methods"][name]
            require(observed["actions"] == [int(actions[i]) for i in indexes], "selection replay mismatch")
            require(len(observed["case_costs_seconds"]) == len(values), "missing selected costs")
            for actual, expected in zip(observed["case_costs_seconds"], values):
                close(actual, expected, "selected case cost")
            mean = sum(values) / len(values)
            close(observed["mean_par2_seconds"], mean, "selected mean cost")
            close(observed["speedup_vs_fixed"], base / mean, "selected speedup")
        uniform = sum(float(v) for i in indexes for v in costs[i]) / (len(indexes) * len(ACTIONS))
        oracle = sum(min(float(v) for v in costs[i]) for i in indexes) / len(indexes)
        for name, mean in (("uniform_expected", uniform), ("retrospective_oracle", oracle)):
            close(data["methods"][name]["mean_par2_seconds"], mean, name)
            close(data["methods"][name]["speedup_vs_fixed"], base / mean, name + " speedup")
        require(data["methods"]["retrospective_oracle"]["deployable"] is False, "oracle mislabeled")


def verify_run(output):
    from . import learning
    start = time.monotonic()
    out = Path(output).resolve()
    manifest = read_json(out / "manifest.json")
    require(manifest["schema_version"] == 1 and manifest["kind"] == "software_benchmark_run", "wrong run schema")
    require(manifest["status"] == "completed" and manifest["failure"] is None, "run did not complete")
    paths = [p for p in out.rglob("*") if p.is_file() and p != out / "manifest.json"]
    require(not any(p.is_symlink() for p in out.rglob("*")), "symlink artifact is unsupported")
    actual_hashes = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    require(actual_hashes == manifest["artifact_sha256"], "artifact hash mismatch")
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob("*.py")}
    require(sources == manifest["source_sha256"], "source hash mismatch; verify with the recorded source version")
    config = read_json(out / "config.json")
    require(config["schema_version"] == 1, "config schema changed")
    require(config["actions"] == list(ACTIONS), "action definitions changed")
    require(config["feature_names"] == list(FEATURE_NAMES), "feature definitions changed")
    require(config["repetitions"] == (1 if config["profile"] == "quick" else 2), "wrong repetitions")
    limit = config["action_timeout_seconds"]
    require(0.1 <= limit <= 10 and 1 <= config["budget_seconds"] <= 600, "invalid run limits")
    require(0 < manifest["elapsed_wall_seconds"] <= config["budget_seconds"] + 2, "run exceeded budget")
    cases = read_json(out / "cases.json")
    require(cases == generate_cases(config["profile"], config["seed"]), "case regeneration mismatch")
    train = [i for i, case in enumerate(cases) if case["split"] == "train"]
    train_primes = {cases[i]["prime"] for i in train}
    require(not train_primes & {c["prime"] for c in cases if c["split"] != "train"}, "prime split leakage")
    roots = {c["id"]: original_roots(c) for c in cases}
    require(all(c["planted_root"] in roots[c["id"]] for c in cases), "planted solution invalid")
    labels = [json.loads(line) for line in (out / "labels.jsonl").read_text().splitlines()]
    expected = len(cases) * len(ACTIONS)
    require(len(labels) == expected == manifest["measured_actions"] == manifest["expected_actions"], "incomplete labels")
    order = [(c["id"], a) for c in cases for a in range(len(ACTIONS))]
    random.Random(config["seed"]).shuffle(order)
    require(read_json(out / "measurement_order.json") == [list(pair) for pair in order], "measurement order changed")
    require([(r["case_id"], r["action_id"]) for r in labels] == order, "label order or coverage mismatch")
    indexes = {c["id"]: i for i, c in enumerate(cases)}
    costs = np.full((len(cases), len(ACTIONS)), np.nan)
    completed_cases = set()
    for row in labels:
        a = row["action_id"]
        require(type(a) is int and 0 <= a < len(ACTIONS), "invalid action identifier")
        require(row["limit_seconds"] == limit and row["process_wall_seconds"] > 0, "invalid process measurement")
        dt.datetime.fromisoformat(row["recorded_at"])
        logbase = f"logs/{row['case_id']}-{a}"
        require(row["stdout_path"] == logbase + ".stdout.txt" and row["stderr_path"] == logbase + ".stderr.txt",
                "unexpected log path")
        require(row["stdout_path"] in actual_hashes and row["stderr_path"] in actual_hashes, "missing child logs")
        if row["status"] == "timed_out":
            require(row["censored"] is True and row["roots"] is None and row["return_code"] is None,
                    "timeout mislabeled")
            close(row["cost_seconds"], 2 * limit, "PAR-2 timeout cost")
        else:
            require(row["status"] == "completed" and row["censored"] is False and row["return_code"] == 0,
                    "failed solver mislabeled")
            require(row["roots"] == roots[row["case_id"]], "root set differs from original equations")
            require(row["root_count"] == len(row["roots"]), "wrong root count")
            require(0 < row["peak_rss_bytes"] <= 2 * 1024**3, "invalid measured memory")
            require(row["intermediate_degree_measured"] is False, "unsupported intermediate-degree claim")
            require(row["basis_size"] > 0 and row["output_basis_max_degree"] >= 0, "invalid basis summary")
            require(len(row["timings"]) == config["repetitions"], "missing repetitions")
            for timing in row["timings"]:
                parts = [timing[k] for k in ("construction_seconds", "groebner_seconds", "root_seconds")]
                require(all(type(v) in (int, float) and v >= 0 and math.isfinite(v) for v in parts), "invalid component timing")
                close(timing["total_seconds"], sum(parts), "total solve time")
            close(row["cost_seconds"], median(t["total_seconds"] for t in row["timings"]), "median solve cost")
            raw = read_json(out / row["stdout_path"])
            require(all(row.get(k) == v for k, v in raw.items()), "child output differs from label")
            completed_cases.add(row["case_id"])
        cost = row["cost_seconds"]
        require(type(cost) in (int, float) and math.isfinite(cost) and cost > 0, "invalid cost")
        costs[indexes[row["case_id"]], a] = cost
    require(len(completed_cases) == len(cases), "a case has no completed solver action")
    require(np.isfinite(costs).all(), "missing action costs")
    x = np.asarray([features(c) for c in cases])
    model = read_json(out / "models.json")
    require(model["training_case_ids"] == [cases[i]["id"] for i in train], "training identity leakage")
    require(model["feature_names"] == list(FEATURE_NAMES), "model feature mismatch")
    # Deterministic refit binds the checkpoint to training rows alone. This is
    # reproducibility of the software fit, not a second learning algorithm.
    replay = learning.train(x[train], costs[train], seed=config["fit_seed"], steps=config["steps"])
    replay.update(training_case_ids=[cases[i]["id"] for i in train], feature_names=list(FEATURE_NAMES))
    require(model == replay, "checkpoint does not replay from training rows alone")
    choices = learning.select(model, x)
    choices["fixed"] = np.zeros(len(cases), dtype=int)
    choices["train_best_fixed"] = np.full(len(cases), int(np.argmin(costs[train].mean(axis=0))))
    choices["uniform_seeded"] = np.random.default_rng(config["fit_seed"]).integers(len(ACTIONS), size=len(cases))
    check_evaluation(read_json(out / "evaluation.json"), cases, costs, choices)
    control = read_json(out / "controls.json")
    replay_control = learning.controls(seed=config["fit_seed"])
    require(all(control.get(k) == v for k, v in replay_control.items()), "software control replay mismatch")
    require(control["positive_passed"] is True and control["constant_passed"] is True, "software control failed")
    shuffled = costs[train].copy()
    rng = np.random.default_rng(config["fit_seed"] + 1)
    for row in shuffled:
        rng.shuffle(row)
    null_model = learning.train(x[train], shuffled, seed=config["fit_seed"], steps=config["steps"])
    check_evaluation(control["shuffled_training_labels"]["evaluation"], cases, costs, learning.select(null_model, x))
    return {"verified": True, "cases": len(cases), "actions": len(labels),
            "completed_actions": sum(r["status"] == "completed" for r in labels),
            "censored_actions": sum(r["status"] == "timed_out" for r in labels),
            "manifest_sha256": hashlib.sha256((out / "manifest.json").read_bytes()).hexdigest(),
            "verification_seconds": time.monotonic() - start,
            "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "checks": ["artifact/source hashes", "regenerated cases", "complete original roots",
                       "timing arithmetic", "training-only checkpoint replay", "metric arithmetic", "controls"],
            "scope": "Software integrity; self-produced timing measurements, no authenticated speedup claim."}
