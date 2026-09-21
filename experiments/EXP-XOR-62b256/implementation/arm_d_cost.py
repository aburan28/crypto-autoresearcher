#!/usr/bin/env python3
"""Coverage-matched Arm D control for EXP-XOR-62b256.

This reuses the frozen curve/factor-base and A/B implementations from
EXP-SEMAEV-f48dd1 and adds only the uniform-query null and charged analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import statistics
import time
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py"
BASELINE_SHA256 = hashlib.sha256(BASELINE.read_bytes()).hexdigest()
EXPECTED_BASELINE_SHA256 = "64d682e56e28472987ebd319f6250a09620c566ab7a881701d53acce3300a540"


def load_baseline():
    if BASELINE_SHA256 != EXPECTED_BASELINE_SHA256:
        raise RuntimeError(
            f"baseline hash mismatch: {BASELINE_SHA256} != {EXPECTED_BASELINE_SHA256}")
    spec = importlib.util.spec_from_file_location("semaev_full_grid", BASELINE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def deterministic_uniform(p: int, seed: int, cell: str, source_index: int,
                          query_index: int) -> int:
    payload = f"EXP-XOR-62b256|{seed}|{cell}|{source_index}|{query_index}"
    return int.from_bytes(hashlib.sha256(payload.encode()).digest(), "big") % p


def arm_d(module, curve, factor_base, seed: int, q: int, kappa: int,
          cell: str) -> dict:
    table = {}
    table_adds = 0
    for p2 in factor_base:
        for p3 in factor_base:
            table_adds += 1
            total = curve.add(p2, p3)
            if total is not None:
                table.setdefault(total[0], []).append((p2, p3))

    candidates = 0
    valid_relation_tuples = set()
    queries = 0
    started = time.perf_counter()
    for source_index, p1 in enumerate(factor_base):
        for query_index in range(q):
            queries += 1
            x_query = deterministic_uniform(
                curve.p, seed, cell, source_index, query_index)
            for p2, p3 in table.get(x_query, []):
                candidates += 1
                total = curve.add(curve.add(p1, p2), p3)
                if total is None:
                    valid_relation_tuples.add((p1, p2, p3))
    verify_adds = 2 * candidates
    query_charge = kappa * queries
    return {
        "q": q,
        "queries": queries,
        "kappa_add_equivalents": kappa,
        "table_adds": table_adds,
        "candidates_verified": candidates,
        "verification_adds": verify_adds,
        "query_charge": query_charge,
        "charged_cost": table_adds + verify_adds + query_charge,
        "unique_valid_relations": len(valid_relation_tuples),
        "wall_clock_seconds": time.perf_counter() - started,
        "table_total_bucket_size": sum(len(bucket) for bucket in table.values()),
        "table_distinct_keys": len(table),
    }


def mean(values):
    return statistics.fmean(values)


def run(output: Path) -> None:
    module = load_baseline()
    kappa = 1
    seeds = [1, 2, 3, 4, 5]
    cells = []
    for p in [101, 103, 107, 211]:
        for b in [0.4, 0.5]:
            curve = module.find_curve(p)
            base_size = int(math.floor(p ** b))
            factor_base, x_coords = module.build_factor_base(curve, base_size)
            n = len(factor_base)
            cell = f"p{p}-b{b}"
            arm_a = module.arm_a_no_oracle(curve, factor_base, 3)
            arm_b = module.arm_b_x_oracle(curve, factor_base, 3)
            arm_b_cost = (arm_b["right_half_pairs"]
                          + kappa * arm_b["oracle_queries"]
                          + 2 * arm_b["candidates_verified"])
            relation_total = arm_a["relations_found"]
            q50 = math.ceil(math.log(1 - 0.50) / math.log(1 - 1 / p))
            q90 = math.ceil(math.log(1 - 0.90) / math.log(1 - 1 / p))
            q_grid = [1, q50, q90]
            d_runs = []
            for seed in seeds:
                for q in q_grid:
                    record = arm_d(module, curve, factor_base, seed, q, kappa, cell)
                    record["seed"] = seed
                    record["predicted_candidate_verifications"] = (
                        q * n * record["table_total_bucket_size"] / p)
                    record["predicted_unique_coverage"] = 1 - (1 - 1 / p) ** q
                    record["measured_unique_coverage"] = (
                        record["unique_valid_relations"] / relation_total
                        if relation_total else None)
                    record["cost_per_unique_relation"] = (
                        record["charged_cost"] / record["unique_valid_relations"]
                        if record["unique_valid_relations"] else None)
                    d_runs.append(record)
            cells.append({
                "cell": cell, "p": p, "b": b, "curve": {
                    "a": curve.a, "b": curve.b, "order": curve.order()},
                "factor_base_x_size": base_size,
                "factor_base_point_size_N": n,
                "factor_base_x_coordinates": x_coords,
                "relation_total": relation_total,
                "arm_a": {**arm_a, "charged_cost": arm_a["field_operations"]},
                "arm_b": {**arm_b, "charged_cost": arm_b_cost,
                          "kappa_add_equivalents": kappa,
                          "unique_coverage": 1.0},
                "q_grid": q_grid,
                "arm_d": d_runs,
            })

    summaries = []
    for cell in cells:
        for q in cell["q_grid"]:
            rows = [row for row in cell["arm_d"] if row["q"] == q]
            summaries.append({
                "cell": cell["cell"], "q": q,
                "predicted_coverage": rows[0]["predicted_unique_coverage"],
                "mean_measured_coverage": mean(
                    row["measured_unique_coverage"] for row in rows),
                "mean_candidates": mean(row["candidates_verified"] for row in rows),
                "mean_predicted_candidates": mean(
                    row["predicted_candidate_verifications"] for row in rows),
                "mean_charged_cost": mean(row["charged_cost"] for row in rows),
                "mean_unique_relations": mean(
                    row["unique_valid_relations"] for row in rows),
            })
    raw = {
        "schema": "exp-xor-62b256-raw-v1",
        "experiment_id": "EXP-XOR-62b256",
        "baseline_path": str(BASELINE.relative_to(ROOT)),
        "baseline_sha256": BASELINE_SHA256,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "kappa_add_equivalents": kappa,
        "cells": cells,
    }
    analysis = {
        "schema": "exp-xor-62b256-analysis-v1",
        "experiment_id": "EXP-XOR-62b256",
        "summaries": summaries,
        "controls": {
            "baseline_hash_match": BASELINE_SHA256 == EXPECTED_BASELINE_SHA256,
            "arm_a_equals_arm_b_relations_all_cells": all(
                cell["arm_a"]["relations_found"]
                == cell["arm_b"]["relations_found"] for cell in cells),
            "query_counts_exact": all(
                row["queries"] == row["q"] * cell["factor_base_point_size_N"]
                for cell in cells for row in cell["arm_d"]),
        },
        "scope": "toy only; no asymptotic or cryptographic-scale inference",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "raw-result.json").write_text(
        json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8")
    (output / "analysis.yaml").write_text(
        yaml.safe_dump(analysis, sort_keys=False), encoding="utf-8")
    (output / "environment.json").write_text(json.dumps({
        "python": platform.python_version(), "platform": platform.platform(),
        "baseline_sha256": BASELINE_SHA256,
    }, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
