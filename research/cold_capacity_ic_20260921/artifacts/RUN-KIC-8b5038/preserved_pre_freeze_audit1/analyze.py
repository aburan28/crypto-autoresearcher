#!/usr/bin/env python3
"""Frozen deterministic analysis for RUN-KIC-8b5038."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROCESSES = ROOT / "receipts/processes.jsonl"
CASES = ROOT / "case_manifest.json"
ANALYSIS = ROOT / "analysis.json"
ANALYSIS_MD = ROOT / "analysis.md"
SEED = "CSIC53-CAPACITY-BOOT-v1"
RESAMPLES = 10_000


def require(condition: bool, message: str) -> None:
    if not condition: raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def percentile(values: list[float], probability: float) -> float:
    position = (len(values) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    return values[lower] if lower == upper else values[lower] * (upper - position) + values[upper] * (position - lower)


def bootstrap(values: list[float]) -> dict[str, Any] | None:
    if not values: return None
    rng = random.Random(SEED); n = len(values)
    medians = sorted(statistics.median(values[rng.randrange(n)] for _ in range(n)) for _ in range(RESAMPLES))
    return {"seed": SEED, "resamples": RESAMPLES, "draws_per_resample": n,
            "method": "paired resampling with replacement; Hyndman-Fan type-7 endpoints",
            "lower_2_5_percent": percentile(medians, .025), "upper_97_5_percent": percentile(medians, .975),
            "sorted_medians_sha256": hashlib.sha256(json.dumps(medians, separators=(",", ":")).encode()).hexdigest()}


def load_rows() -> list[dict[str, Any]]:
    return [json.loads(line) for line in PROCESSES.read_text().splitlines() if line]


def arm_cpu(row: dict[str, Any]) -> float:
    return row["user_cpu_seconds"] + row["system_cpu_seconds"]


def ratio(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator in (None, 0): return None
    return float(numerator) / float(denominator)


def analyze() -> dict[str, Any]:
    rows = load_rows(); manifest = json.loads(CASES.read_text()); cases = manifest["cases"]
    require(len(rows) == len(cases) == 72, "analysis requires exact 72 rows")
    for index, (row, case) in enumerate(zip(rows, cases), 1):
        require((row["ordinal"], row["case_id"], row["arm"], row["scalar"], row["seed"]) == (index, case["id"], case["arm"], case["scalar"], case["seed"]), f"schedule mismatch at {index}")
    paired = []
    for case_index in range(1, 25):
        group = [row for row in rows if row["case_index"] == case_index]
        require(len(group) == 3, f"case {case_index} arm count mismatch")
        arms = {row["arm"]: row for row in group}; require(set(arms) == {"baseline", "candidate", "rho"}, f"case {case_index} arms mismatch")
        valid = all(row["valid"] is True for row in arms.values())
        if valid:
            require(len({row["scalar"] for row in arms.values()}) == 1, f"case {case_index} scalar mismatch")
            require(len({tuple(row["parsed_receipt"]["published_q"]) for row in arms.values()}) == 1, f"case {case_index} public point mismatch")
        baseline, candidate, rho = arms["baseline"], arms["candidate"], arms["rho"]
        q = ratio(candidate["wall_seconds"], rho["wall_seconds"]) if valid else None
        paired.append({
            "case_index": case_index, "scalar": candidate["scalar"], "valid_triplet": valid,
            "order": [row["arm"] for row in sorted(group, key=lambda row: row["position"])],
            "wall_seconds": {arm: arms[arm]["wall_seconds"] for arm in arms},
            "cpu_seconds": {arm: arm_cpu(arms[arm]) for arm in arms},
            "wait4_peak_rss": {arm: arms[arm]["wait4_ru_maxrss"] for arm in arms},
            "sampled_peak_bytes": {arm: arms[arm]["memory_sampling"]["sampled_peak_bytes"] for arm in arms},
            "candidate_over_rho_wall": q,
            "baseline_over_rho_wall": ratio(baseline["wall_seconds"], rho["wall_seconds"]) if valid else None,
            "candidate_over_baseline_wall": ratio(candidate["wall_seconds"], baseline["wall_seconds"]) if valid else None,
            "candidate_over_baseline_cpu": ratio(arm_cpu(candidate), arm_cpu(baseline)) if valid else None,
            "candidate_over_baseline_wait4_rss": ratio(candidate["wait4_ru_maxrss"], baseline["wait4_ru_maxrss"]) if valid else None,
            "candidate_over_baseline_sampled_peak": ratio(candidate["memory_sampling"]["sampled_peak_bytes"], baseline["memory_sampling"]["sampled_peak_bytes"]) if valid else None,
            "direct_stages_ms": {arm: {key: arms[arm]["parsed_receipt"].get(key) for key in ("setup_ms", "collection_ms", "query_ms", "linear_solve_ms", "solution_validation_ms", "charged_total_ms")} for arm in ("baseline", "candidate")},
        })
    q_values = [row["candidate_over_rho_wall"] for row in paired if row["valid_triplet"]]
    interval = bootstrap(q_values)
    def values(key: str) -> list[float]: return [row[key] for row in paired if row["valid_triplet"] and row[key] is not None]
    summary = {
        "valid_triplets": len(q_values), "invalid_triplets": 24 - len(q_values),
        "candidate_rho_median_wall_ratio": statistics.median(q_values) if q_values else None,
        "candidate_rho_arithmetic_mean_wall_ratio": statistics.fmean(q_values) if q_values else None,
        "candidate_rho_geometric_mean_wall_ratio": math.exp(statistics.fmean(math.log(value) for value in q_values)) if q_values else None,
        "candidate_rho_bootstrap_median_95_percentile_interval": interval,
        "baseline_rho_median_wall_ratio": statistics.median(values("baseline_over_rho_wall")) if q_values else None,
        "candidate_baseline_median_wall_ratio": statistics.median(values("candidate_over_baseline_wall")) if q_values else None,
        "candidate_baseline_median_cpu_ratio": statistics.median(values("candidate_over_baseline_cpu")) if q_values else None,
        "candidate_baseline_median_wait4_rss_ratio": statistics.median(values("candidate_over_baseline_wait4_rss")) if q_values else None,
        "candidate_baseline_median_sampled_peak_ratio": statistics.median(values("candidate_over_baseline_sampled_peak")) if q_values else None,
        "failures": {arm: sum(row["arm"] == arm and not row["valid"] for row in rows) for arm in ("baseline", "candidate", "rho")},
    }
    eligible = len(q_values) == 24 and summary["candidate_rho_median_wall_ratio"] < .95 and interval is not None and interval["upper_97_5_percent"] < 1
    return {
        "schema": "crypto.autoresearch.cold_capacity_analysis.v1", "experiment_id": "RUN-KIC-8b5038",
        "scope": "finite public-synthetic N=53 explicit-known-answer capacity-only process comparison",
        "inputs": {"processes_sha256": sha256_file(PROCESSES), "case_manifest_sha256": sha256_file(CASES)},
        "raw_process_table": rows, "paired_cases": paired, "summary": summary,
        "primary_finite_signal_predicate": {"all_24_triplets_valid": len(q_values) == 24,
            "median_candidate_rho_below_0_95": summary["candidate_rho_median_wall_ratio"] is not None and summary["candidate_rho_median_wall_ratio"] < .95,
            "bootstrap_upper_below_1_00": interval is not None and interval["upper_97_5_percent"] < 1,
            "eligible_for_independent_review": eligible},
        "no_selection_or_old_pooling": True,
        "claim_boundary": "observation only; no asymptotic, SOTA, security, break, hypothesis, or goal-status conclusion",
    }


def markdown(result: dict[str, Any]) -> str:
    summary, predicate = result["summary"], result["primary_finite_signal_predicate"]
    lines = ["# RUN-KIC-8b5038 finite analysis", "", result["claim_boundary"], "",
             f"Valid triplets: {summary['valid_triplets']} of 24.",
             f"Candidate/rho median wall ratio: {summary['candidate_rho_median_wall_ratio']!r}.",
             f"Candidate/rho bootstrap interval: {summary['candidate_rho_bootstrap_median_95_percentile_interval']!r}.",
             f"Candidate/baseline median wall ratio: {summary['candidate_baseline_median_wall_ratio']!r}.",
             f"Candidate/baseline median CPU ratio: {summary['candidate_baseline_median_cpu_ratio']!r}.",
             f"Candidate/baseline median wait4 RSS ratio: {summary['candidate_baseline_median_wait4_rss_ratio']!r}.",
             f"Finite predicate eligible: {predicate['eligible_for_independent_review']}.", "", "## Per-target ratios", "",
             "| case | scalar | order | candidate/rho wall | candidate/baseline wall | candidate/baseline CPU | candidate/baseline RSS | valid |",
             "| ---: | ---: | --- | ---: | ---: | ---: | ---: | :---: |"]
    for row in result["paired_cases"]:
        lines.append(f"| {row['case_index']} | {row['scalar']} | {','.join(row['order'])} | {row['candidate_over_rho_wall']!r} | {row['candidate_over_baseline_wall']!r} | {row['candidate_over_baseline_cpu']!r} | {row['candidate_over_baseline_wait4_rss']!r} | {row['valid_triplet']} |")
    return "\n".join(lines) + "\n"


def self_test() -> None:
    values = [.5, 1., 2.]; first = bootstrap(values); second = bootstrap(values)
    require(first == second and first["resamples"] == 10000, "bootstrap determinism failed")
    require(percentile(values, 0) == .5 and percentile(values, 1) == 2., "percentile endpoints failed")
    print(json.dumps({"self_test": "PASS", "tests": 3}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    if args.self_test: self_test(); return
    result = analyze(); ANALYSIS.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n"); ANALYSIS_MD.write_text(markdown(result))


if __name__ == "__main__": main()
