#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ADAPTIVE_SOURCE = SCRIPT_PATH.with_name("typed_tt_adaptive_skeleton_preflight.py")


def load_adaptive() -> Any:
    spec = importlib.util.spec_from_file_location("typed_tt_adaptive_for_binding", ADAPTIVE_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load adaptive producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ADAPTIVE = load_adaptive()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def supported_descent_targets(family: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item for item in family["held_out_descent"]["transcript"]
        if item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]
    ]


def run_row(curve: dict[str, Any], family: dict[str, Any], adaptive_row: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = ADAPTIVE.SOURCE_AWARE.ORACLE_MODULE.Oracle(curve, ADAPTIVE.target_family(family, base_target))
    skeleton = ADAPTIVE.adaptive_build(base_oracle, a_size, b_size)

    relation_targets = [item["target"] for item in family["relations"]["target_transcript"][:8]]
    held_out_supported = supported_descent_targets(family)
    binding_targets = [(f"relation_{index}", target) for index, target in enumerate(relation_targets)]
    binding_targets.extend((f"held_out_supported_{index}", item["target"]) for index, item in enumerate(held_out_supported))
    results = []
    for label, target in binding_targets:
        oracle = ADAPTIVE.SOURCE_AWARE.ORACLE_MODULE.Oracle(curve, ADAPTIVE.target_family(family, target))
        reconstructed = ADAPTIVE.SOURCE_AWARE.reconstruct_target(oracle, skeleton, a_size, b_size, True)
        results.append({
            "label": label,
            "target": target,
            "mismatches": reconstructed["mismatches"],
            "specialization_queries": reconstructed["specialization_queries"],
            "validation_queries": reconstructed["validation_queries"],
            "oracle_ops": oracle.ops,
        })

    adaptive_targets = {item["label"]: item["target"] for item in adaptive_row["targets"]}
    relation_target_binding = all(adaptive_targets.get(f"relation_{index}") == target for index, target in enumerate(relation_targets))
    held_out_target_binding = adaptive_targets.get("held_out_first") == family["held_out_descent"]["transcript"][0]["target"]
    witness_rows = family["relations"]["independent_equations"]
    witnesses_present = bool(witness_rows) and all(row.get("r_witness") for row in witness_rows)
    relation_results = [item for item in results if item["label"].startswith("relation_")]
    descent_results = [item for item in results if item["label"].startswith("held_out_supported_")]
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "adaptive_rank": skeleton["rank"],
        "adaptive_candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "relation_equations": len(witness_rows),
        "relation_target_count": len(relation_targets),
        "supported_descent_target_count": len(held_out_supported),
        "relation_target_binding": relation_target_binding,
        "held_out_target_binding": held_out_target_binding,
        "independent_relation_witnesses_present": witnesses_present,
        "relation_results": relation_results,
        "descent_results": descent_results,
        "all_relation_targets_exact": all(item["mismatches"] == 0 for item in relation_results),
        "all_supported_descent_targets_exact": all(item["mismatches"] == 0 for item in descent_results),
        "validation_queries_total": sum(item["validation_queries"] for item in results),
        "specialization_queries_total": sum(item["specialization_queries"] for item in results),
        "descent_success_probability": family["held_out_descent"]["success_probability"],
        "relation_independent_equations": family["relations"]["independent_equations"],
        "wall_seconds": time.perf_counter() - started,
    }


def run(input_path: Path, adaptive_path: Path, families: list[str]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    adaptive = json.loads(adaptive_path.read_text(encoding="utf-8"))
    adaptive_by_key = {(row["curve_id"], row["family"]): row for row in adaptive["rows"]}
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            family = by_family[family_name]
            key = (instance["curve"]["id"], family_name)
            rows.append(run_row(instance["curve"], family, adaptive_by_key[key]))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-relation-descent-binding-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "adaptive_result_sha256": sha256_file(adaptive_path),
            "input_sha256": sha256_file(input_path),
        },
        "config": {
            "families": families,
            "relation_targets": "first eight relation transcript targets",
            "descent_targets": "all held-out transcript entries supported by both descent paths",
            "validation_full_tensor": True,
        },
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_relation_target_bindings": all(row["relation_target_binding"] for row in rows),
            "all_held_out_target_bindings": all(row["held_out_target_binding"] for row in rows),
            "all_relation_witnesses_present": all(row["independent_relation_witnesses_present"] for row in rows),
            "all_relation_targets_exact": all(row["all_relation_targets_exact"] for row in rows),
            "all_supported_descent_targets_exact": all(row["all_supported_descent_targets_exact"] for row in rows),
            "all_supported_descent_targets_replayed": all(row["supported_descent_target_count"] > 0 for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Exact tensor replay is bound to typed relation targets and supported held-out descent targets; no relation-matrix solve or generic ECDLP claim.",
        },
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("adaptive_result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.adaptive_result, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
