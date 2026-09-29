#!/usr/bin/env python3
"""Frozen deterministic analysis for RUN-KIC-e3dbed.

This program consumes all 96 terminal process receipts, retains every failure
in the raw table, checks the mechanical calibration selection, and computes the
predeclared held-out paired statistics.  It reports finite observations only;
it does not change hypothesis or goal status.
"""

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
PROCESSES = ROOT / "processes.jsonl"
CASES = ROOT / "case_manifest.json"
SELECTION = ROOT / "calibration_selection.json"
ANALYSIS = ROOT / "analysis.json"
ANALYSIS_MD = ROOT / "analysis.md"
BOOTSTRAP_SEED = "CSIC53-BOOT-v1"
BOOTSTRAP_RESAMPLES = 10_000


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalysisError(message)


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_rows() -> list[dict[str, Any]]:
    require(PROCESSES.is_file(), "processes.jsonl is absent")
    rows = []
    for line_number, line in enumerate(PROCESSES.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        value = json.loads(line)
        require(isinstance(value, dict), f"line {line_number} is not an object")
        rows.append(value)
    return rows


def percentile(sorted_values: list[float], probability: float) -> float:
    require(bool(sorted_values), "percentile requires data")
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position); upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def bootstrap_median_interval(ratios: list[float]) -> dict[str, Any] | None:
    if not ratios:
        return None
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(ratios)
    estimates = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        estimates.append(statistics.median(ratios[rng.randrange(n)] for _ in range(n)))
    estimates.sort()
    return {
        "seed": BOOTSTRAP_SEED,
        "resamples": BOOTSTRAP_RESAMPLES,
        "method": "paired ratio resampling with replacement; linear-interpolated percentile endpoints",
        "lower_2_5_percent": percentile(estimates, 0.025),
        "upper_97_5_percent": percentile(estimates, 0.975),
    }


def verify_schedule(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    expected = manifest["calibration"] + manifest["heldout"]
    require(len(expected) == 96, "case manifest does not contain 96 cases")
    require(len(rows) == 96, f"analysis requires 96 terminal receipts, found {len(rows)}")
    for position, (row, case) in enumerate(zip(rows, expected), 1):
        require(row.get("ordinal") == position == case["ordinal"], f"ordinal mismatch at {position}")
        require(row.get("case_id") == case["id"], f"case id mismatch at {position}")
        require(row.get("scalar") == case["scalar"], f"scalar mismatch at {position}")
        require(row.get("seed_label") == case["seed_label"] and row.get("seed") == case["seed"], f"seed mismatch at {position}")
        require(row.get("terminal_state") in {
            "completed_valid", "completed_invalid", "failed_infrastructure",
            "failed_implementation", "resource_exhaustion", "cancelled_by_budget",
        }, f"non-terminal row at {position}")


def validate_selection(rows: list[dict[str, Any]], selection: dict[str, Any]) -> None:
    calibration = rows[:48]
    require(selection.get("input_processes_prefix_digest") == digest(calibration), "calibration selection input digest mismatch")
    medians = {}
    configurations = (
        "allocation_only_eta_1_128", "allocation_only_eta_1_256", "allocation_only_eta_1_512",
    )
    for configuration in configurations:
        group = [row for row in calibration if row.get("configuration") == configuration]
        require(len(group) == 12 and all(row.get("valid") is True for row in group), f"{configuration} lacks 12 valid calibration rows")
        medians[configuration] = statistics.median(row["wall_seconds"] for row in group)
    require(selection.get("candidate_median_wall_seconds") == medians, "stored calibration medians differ")
    winner = min(medians, key=lambda name: (medians[name], configurations.index(name)))
    denominator = {"allocation_only_eta_1_128": 128, "allocation_only_eta_1_256": 256, "allocation_only_eta_1_512": 512}[winner]
    require(selection.get("winner_configuration") == winner, "stored calibration winner differs")
    require(selection.get("winner_eta_denominator") == denominator, "stored denominator differs")
    require(selection.get("equivalence_gate", {}).get("passed") is True, "allocation equivalence gate not passed")


def analyze() -> dict[str, Any]:
    rows = load_rows()
    manifest = json.loads(CASES.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    verify_schedule(rows, manifest)
    validate_selection(rows, selection)

    heldout = rows[48:]
    pairs = []
    for scalar_index in range(1, 25):
        pair_rows = [row for row in heldout if row["scalar_index"] == scalar_index]
        require(len(pair_rows) == 2, f"held-out pair {scalar_index} has {len(pair_rows)} rows")
        direct_rows = [row for row in pair_rows if row["solver"] == "direct"]
        rho_rows = [row for row in pair_rows if row["solver"] == "rho"]
        require(len(direct_rows) == len(rho_rows) == 1, f"held-out pair {scalar_index} arm count mismatch")
        direct, rho = direct_rows[0], rho_rows[0]
        valid = direct["valid"] is True and rho["valid"] is True
        if valid:
            require(direct["scalar"] == rho["scalar"], f"held-out pair {scalar_index} scalar differs across arms")
            require(direct["parsed_receipt"]["published_fixture_scalar"] == direct["scalar"], f"held-out direct scalar mismatch at {scalar_index}")
            require(rho["parsed_receipt"]["published_fixture_scalar"] == rho["scalar"], f"held-out rho scalar mismatch at {scalar_index}")
            require(direct["parsed_receipt"]["published_q"] == rho["parsed_receipt"]["published_q"], f"held-out published_q differs across arms at {scalar_index}")
            require(direct["eta_denominator"] == selection["winner_eta_denominator"], f"held-out direct density differs at {scalar_index}")
        ratio = direct["wall_seconds"] / rho["wall_seconds"] if valid else None
        pairs.append({
            "scalar_index": scalar_index,
            "scalar": direct["scalar"],
            "direct_case_id": direct["case_id"],
            "rho_case_id": rho["case_id"],
            "direct_valid": direct["valid"],
            "rho_valid": rho["valid"],
            "direct_wall_seconds": direct["wall_seconds"],
            "rho_wall_seconds": rho["wall_seconds"],
            "ratio": ratio,
            "valid_pair": valid,
        })
    ratios = [pair["ratio"] for pair in pairs if pair["valid_pair"]]
    interval = bootstrap_median_interval(ratios)
    summaries = {
        "valid_pair_count": len(ratios),
        "invalid_pair_count": 24 - len(ratios),
        "median_ratio": statistics.median(ratios) if ratios else None,
        "arithmetic_mean_ratio": statistics.fmean(ratios) if ratios else None,
        "geometric_mean_ratio": math.exp(statistics.fmean(math.log(value) for value in ratios)) if ratios else None,
        "bootstrap_median_95_percentile_interval": interval,
        "direct_failure_count": sum(row["solver"] == "direct" and not row["valid"] for row in heldout),
        "rho_failure_count": sum(row["solver"] == "rho" and not row["valid"] for row in heldout),
    }
    eligible = (
        len(ratios) == 24
        and summaries["median_ratio"] < 0.95
        and interval is not None
        and interval["upper_97_5_percent"] < 1.0
    )
    return {
        "schema": "crypto.autoresearch.cold_single_ic_analysis.v1",
        "experiment_id": "RUN-KIC-e3dbed",
        "scope": "finite public-synthetic N=53 known-answer held-out process comparison",
        "inputs": {
            "processes_jsonl_sha256": sha256_file(PROCESSES),
            "case_manifest_sha256": sha256_file(CASES),
            "calibration_selection_sha256": sha256_file(SELECTION),
        },
        "calibration": {
            "winner_configuration": selection["winner_configuration"],
            "winner_eta_denominator": selection["winner_eta_denominator"],
            "winner_factor_base_k": selection["winner_factor_base_k"],
            "candidate_median_wall_seconds": selection["candidate_median_wall_seconds"],
            "allocation_equivalence_passed": True,
            "not_a_performance_claim": True,
        },
        "raw_process_table": rows,
        "heldout_pairs": pairs,
        "heldout_summary": summaries,
        "finite_signal_predicate": {
            "all_24_pairs_valid": len(ratios) == 24,
            "median_below_0_95": summaries["median_ratio"] is not None and summaries["median_ratio"] < 0.95,
            "bootstrap_upper_below_1_00": interval is not None and interval["upper_97_5_percent"] < 1.0,
            "eligible_for_independent_review": eligible,
        },
        "claim_boundary": "observation only; no asymptotic, SOTA, key-recovery, break, hypothesis-status, or goal-status conclusion",
    }


def render_markdown(result: dict[str, Any]) -> str:
    summary = result["heldout_summary"]
    predicate = result["finite_signal_predicate"]
    interval = summary["bootstrap_median_95_percentile_interval"]
    lines = [
        "# RUN-KIC-e3dbed finite analysis",
        "",
        "This report is a finite public-synthetic N=53 known-answer process comparison. It makes no asymptotic, SOTA, key-recovery, break, or research-status claim.",
        "",
        f"Calibration winner: `{result['calibration']['winner_configuration']}` (eta denominator {result['calibration']['winner_eta_denominator']}, K={result['calibration']['winner_factor_base_k']}).",
        f"Valid held-out pairs: {summary['valid_pair_count']} of 24.",
        f"Direct failures: {summary['direct_failure_count']}; rho failures: {summary['rho_failure_count']}.",
        f"Median ratio: {summary['median_ratio']!r}.",
        f"Arithmetic mean ratio: {summary['arithmetic_mean_ratio']!r}.",
        f"Geometric mean ratio: {summary['geometric_mean_ratio']!r}.",
        f"Bootstrap median 95% percentile interval: {interval!r}.",
        f"Finite predicate eligible for independent review: {predicate['eligible_for_independent_review']}.",
        "",
        "## Held-out pairs",
        "",
        "| index | scalar | direct seconds | rho seconds | ratio | valid |",
        "| ---: | ---: | ---: | ---: | ---: | :---: |",
    ]
    for pair in result["heldout_pairs"]:
        lines.append(f"| {pair['scalar_index']} | {pair['scalar']} | {pair['direct_wall_seconds']:.9f} | {pair['rho_wall_seconds']:.9f} | {pair['ratio']!r} | {pair['valid_pair']} |")
    return "\n".join(lines) + "\n"


def self_test() -> None:
    values = [0.5, 1.0, 2.0]
    require(percentile(values, 0.0) == 0.5 and percentile(values, 1.0) == 2.0, "percentile endpoints failed")
    first = bootstrap_median_interval(values)
    second = bootstrap_median_interval(values)
    require(first == second and first["resamples"] == 10_000, "bootstrap is not deterministic")
    print(json.dumps({"self_test": "PASS", "tests": 3}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); return
    result = analyze()
    ANALYSIS.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    ANALYSIS_MD.write_text(render_markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
