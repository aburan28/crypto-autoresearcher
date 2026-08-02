#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SOURCE_AWARE_SOURCE = SCRIPT_PATH.with_name("typed_tt_source_aware_skeleton_preflight.py")


def load_source_aware() -> Any:
    spec = importlib.util.spec_from_file_location("typed_source_aware_for_adaptive", SOURCE_AWARE_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load source-aware helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE_AWARE = load_source_aware()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def adaptive_build(oracle: Any, a_size: int, b_size: int) -> dict[str, Any]:
    suffixes = SOURCE_AWARE.suffix_indices(b_size)
    window = max(4, b_size // 2)
    basis_rows = []
    basis_prefixes = []
    echelon: dict[int, list[int]] = {}
    counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    examined = 0
    plateau = 0
    last_rank = 0
    for prefix in SOURCE_AWARE.prefix_order(a_size, b_size):
        examined += 1
        row = [oracle.value(prefix + suffix) for suffix in suffixes]
        if SOURCE_AWARE.row_reduce_add(row, echelon, oracle.p, counters):
            basis_rows.append(row)
            basis_prefixes.append(prefix)
            last_rank += 1
            plateau = 0
        else:
            plateau += 1
        if last_rank > 0 and plateau >= window:
            break
    if not basis_rows:
        raise ValueError("adaptive search found no nonzero row")
    pivot_columns, column_rank = SOURCE_AWARE.column_pivots(basis_rows, oracle.p, counters)
    if column_rank != last_rank:
        raise ValueError("adaptive basis column rank mismatch")
    cross = [[basis_rows[row][column] for column in pivot_columns] for row in range(last_rank)]
    inverse = SOURCE_AWARE.inverse_matrix(cross, oracle.p, counters)
    return {
        "rank": last_rank,
        "basis_rows": basis_rows,
        "basis_prefixes": basis_prefixes,
        "pivot_columns": pivot_columns,
        "inverse": inverse,
        "candidate_prefixes_examined": examined,
        "total_prefixes": a_size * b_size * b_size,
        "stability_window": window,
        "terminal_plateau": plateau,
        "stopping_reason": "dependent_prefix_plateau",
        "rank_counters": counters,
    }


def target_family(family: dict[str, Any], target: list[int]) -> dict[str, Any]:
    return SOURCE_AWARE.target_family(family, target)


def run_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    full_entries = a_size * b_size**4
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = SOURCE_AWARE.ORACLE_MODULE.Oracle(curve, target_family(family, base_target))
    skeleton = adaptive_build(base_oracle, a_size, b_size)
    target_results = []
    for label, target in SOURCE_AWARE.target_list(family):
        oracle = SOURCE_AWARE.ORACLE_MODULE.Oracle(curve, target_family(family, target))
        result = SOURCE_AWARE.reconstruct_target(oracle, skeleton, a_size, b_size, True)
        target_results.append({
            "label": label,
            "target": target,
            "mismatches": result["mismatches"],
            "specialization_queries": result["specialization_queries"],
            "validation_queries": result["validation_queries"],
            "oracle_ops": oracle.ops,
        })
    construction_queries = skeleton["candidate_prefixes_examined"] * b_size**2
    specialization_queries = a_size * b_size**2 * skeleton["rank"]
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "discovered_rank": skeleton["rank"],
        "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "total_prefixes": skeleton["total_prefixes"],
        "stability_window": skeleton["stability_window"],
        "terminal_plateau": skeleton["terminal_plateau"],
        "stopping_reason": skeleton["stopping_reason"],
        "basis_prefixes": skeleton["basis_prefixes"],
        "pivot_columns": skeleton["pivot_columns"],
        "construction_queries": construction_queries,
        "construction_query_count_matches": base_oracle.ops["unique_queries"] == construction_queries,
        "construction_oracle_ops": base_oracle.ops,
        "construction_query_ratio_full_tensor": construction_queries / max(1, full_entries),
        "specialization_queries_per_target": specialization_queries,
        "specialization_query_ratio_full_tensor": specialization_queries / max(1, full_entries),
        "full_tensor_entries": full_entries,
        "targets": target_results,
        "all_exact": all(item["mismatches"] == 0 for item in target_results),
        "enumerative_validation": True,
        "source_construction_non_enumerative": True,
        "rank_counters": skeleton["rank_counters"],
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve["id"], "family": family["family"], "rank": skeleton["rank"], "examined": skeleton["candidate_prefixes_examined"], "basis_prefixes": skeleton["basis_prefixes"], "pivot_columns": skeleton["pivot_columns"], "targets": [{key: value for key, value in item.items() if key != "oracle_ops"} for item in target_results]}),
    }


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adaptive-skeleton-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "source_aware_helper_sha256": sha256_file(SOURCE_AWARE_SOURCE), "input_sha256": sha256_file(input_path)},
        "config": {"families": families, "cut": 3, "stability_window": "max(4, floor(B/2))", "targets": "first eight relation plus held-out first", "rank_budget_input": False, "source_tuple_enumeration": False, "validation_full_tensor": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_adaptive": all(row["stopping_reason"] == "dependent_prefix_plateau" for row in rows),
            "all_exact_validation": all(row["all_exact"] for row in rows),
            "all_construction_query_counts_match": all(row["construction_query_count_matches"] for row in rows),
            "all_source_paths_non_enumerative": all(row["source_construction_non_enumerative"] for row in rows),
            "min_construction_query_ratio": min(row["construction_query_ratio_full_tensor"] for row in rows),
            "max_construction_query_ratio": max(row["construction_query_ratio_full_tensor"] for row in rows),
            "min_specialization_query_ratio": min(row["specialization_query_ratio_full_tensor"] for row in rows),
            "max_specialization_query_ratio": max(row["specialization_query_ratio_full_tensor"] for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Adaptive source-prefix skeleton with separately charged full validation; no generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
