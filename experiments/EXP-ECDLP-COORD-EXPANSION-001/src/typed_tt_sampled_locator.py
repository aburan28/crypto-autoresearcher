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
BATCH_SOURCE = SCRIPT_PATH.with_name("typed_tt_batched_source_sum.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BATCH = load("typed_tt_batching_for_sampled_locator", BATCH_SOURCE)
ROWSPACE = BATCH.ROWSPACE
ADAPTIVE = BATCH.ADAPTIVE
STREAMING = BATCH.STREAMING
TF = BATCH.TF


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ops(total: dict[str, int], extra: dict[str, int]) -> None:
    for key, value in extra.items():
        total[key] = total.get(key, 0) + int(value)


def zero_ops() -> dict[str, int]:
    return BATCH.zero_ops()


def parse_budget(value: str, b_size: int) -> int:
    if value == "full":
        return b_size * b_size
    budget = int(value)
    if budget < 1:
        raise ValueError("budgets must be positive or full")
    return min(budget, b_size * b_size)


def sampled_columns(b_size: int, budget: int, seed: int) -> list[int]:
    count = b_size * b_size
    if budget >= count:
        return list(range(count))
    ranked = sorted(
        range(count),
        key=lambda index: hashlib.sha256(f"TYPED-TT-SAMPLED-LOCATOR|{seed}|{index}".encode("ascii")).digest(),
    )
    return sorted(ranked[:budget])


def locate(
    predicates: Any,
    target_index: int,
    skeleton: dict[str, Any],
    a_size: int,
    b_size: int,
    columns: list[int],
) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    rank = skeleton["rank"]
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction_ops = zero_ops()
    hits = []
    predicted_mismatches = 0
    sampled_entries = 0
    for prefix in prefixes:
        sampled = [predicates.value(target_index, prefix + suffixes[column]) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, predicates.p)
        reconstruction_ops["field_multiplications"] += rank * rank
        reconstruction_ops["field_additions"] += rank * max(0, rank - 1)
        for column in columns:
            indices = prefix + suffixes[column]
            actual = predicates.value(target_index, indices)
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % predicates.p
            predicted_mismatches += int(predicted != actual)
            sampled_entries += 1
            reconstruction_ops["field_multiplications"] += rank
            reconstruction_ops["field_additions"] += max(0, rank - 1)
            if predicted == 0:
                hits.append({"indices": list(indices), "a_index": indices[0], "suffix_column": column})
    return {
        "hits": hits,
        "sampled_entries": sampled_entries,
        "predicted_mismatches": predicted_mismatches,
        "reconstruction_ops": reconstruction_ops,
    }


def valid_witness(curve: Any, a_points: list[Any], r_points: list[Any], indices: tuple[int, ...], target: Any, ops: Any) -> bool:
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index], ops)
    return total == target


def hit_indices(hit: dict[str, Any]) -> tuple[int, ...]:
    if "indices" in hit:
        return tuple(int(value) for value in hit["indices"])
    return (int(hit["a_index"]), *[int(value) for value in hit["r_witness"]])


def run_budget(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    transcript: dict[str, Any],
    budget_label: str,
    budget: int,
) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    curve = TF.Curve(p, curve_record["a"], curve_record["b"])
    a_points = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    a_size = len(a_points)
    b_size = len(r_points)
    targets = [tuple(int(value) for value in item["target"]) for item in transcript["shared_candidate"]["transcripts"]]
    baseline_transcripts = transcript["shared_candidate"]["transcripts"]
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    source = BATCH.SourceSumCache(advice, True)
    predicates = BATCH.BatchedPredicates(source, targets, p)
    skeleton = ADAPTIVE.adaptive_build(predicates.target_view(0), a_size, b_size)
    columns = sampled_columns(b_size, budget, family["run_seed"] ^ 0x5A17C0DE)
    matrix = TF.IncrementalBasis(b_size + 1, q)
    relation_equations: list[dict[str, Any]] = []
    reconstruction_ops = zero_ops()
    witness_ops = TF.Ops()
    target_records = []
    for target_index, baseline in enumerate(baseline_transcripts):
        located = locate(predicates, target_index, skeleton, a_size, b_size, columns)
        target_point = TF.point_from_json(list(targets[target_index]))
        candidate_set = {tuple(item["indices"]) for item in located["hits"]}
        baseline_set = {hit_indices(item) for item in baseline["baseline_hits"]}
        candidate_a = {indices[0] for indices in candidate_set}
        baseline_a = {indices[0] for indices in baseline_set}
        false_positives = sorted(candidate_a - baseline_a)
        missed_support = sorted(baseline_a - candidate_a)
        extra_witnesses = sorted(candidate_set - baseline_set)
        expected = baseline.get("expected_witness")
        expected_indices = None
        if expected is not None:
            expected_indices = (int(expected["a_index"]), *[int(value) for value in expected["r_witness"]])
        candidate_witnesses_valid = all(
            valid_witness(curve, a_points, r_points, indices, target_point, witness_ops)
            for indices in candidate_set
        )
        for item in located["hits"]:
            indices = tuple(item["indices"])
            coefficients = TF.quotient_relation_coefficients(indices[0], indices[1:], b_size)
            equation = {
                "coefficients": coefficients,
                "rhs": int(baseline["scalar"]),
                "a_index": indices[0],
                "r_witness": list(indices[1:]),
            }
            if matrix.insert(coefficients, equation["rhs"]):
                relation_equations.append(equation)
        add_ops(reconstruction_ops, located["reconstruction_ops"])
        target_records.append({
            "target_index": target_index,
            "target": list(targets[target_index]),
            "label": baseline.get("label"),
            "held_out_supported": baseline.get("held_out_supported", False),
            "candidate_hits": located["hits"],
            "candidate_hit_count": len(candidate_set),
            "baseline_hit_count": len(baseline_set),
            "support_recall": len(candidate_a & baseline_a) / max(1, len(baseline_a)),
            "false_positive_count": len(false_positives),
            "missed_support_count": len(missed_support),
            "false_positives": list(false_positives),
            "missed_support": list(missed_support),
            "extra_valid_witness_count": len(extra_witnesses),
            "candidate_contains_expected_witness": expected_indices is None or expected_indices in candidate_set,
            "candidate_witnesses_valid": candidate_witnesses_valid,
            "predicted_mismatches": located["predicted_mismatches"],
            "sampled_entries": located["sampled_entries"],
            "candidate_rank_after_target": matrix.rank,
        })
    source.update_peak()
    return {
        "budget_label": budget_label,
        "budget": budget,
        "sample_columns": columns,
        "sample_column_fraction": len(columns) / max(1, b_size * b_size),
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_count": len(targets),
        "rowspace_rank": skeleton["rank"],
        "rowspace_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "rowspace_stopping_reason": skeleton["stopping_reason"],
        "candidate_rank": matrix.rank,
        "candidate_full_rank": matrix.rank == b_size + 1,
        "candidate_source_ops": dict(source.ops),
        "candidate_advice_build_ops": dict(advice.ops),
        "candidate_advice": {
            "retained_bytes": advice.retained_bytes(),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "source_cache_peak_bytes": source.peak_cache_bytes,
            "source_cache_peak_entries": source.peak_cache_entries,
            "source_cache_logical_payload_bytes": source.peak_cache_entries * advice.point_payload_bytes,
        },
        "candidate_reconstruction_ops": reconstruction_ops,
        "candidate_witness_ops": TF.asdict(witness_ops),
        "candidate_relation_matrix_ops": TF.asdict(matrix.ops),
        "candidate_predicted_entries": sum(item["sampled_entries"] for item in target_records),
        "full_predicted_entries": len(targets) * a_size * b_size**4,
        "target_records": target_records,
        "all_candidate_witnesses_valid": all(item["candidate_witnesses_valid"] for item in target_records),
        "all_support_exact": all(item["missed_support_count"] == 0 and item["false_positive_count"] == 0 for item in target_records),
        "all_held_out_support_exact": all(
            not item["held_out_supported"] or (
                item["missed_support_count"] == 0
                and item["false_positive_count"] == 0
                and item["candidate_contains_expected_witness"]
            )
            for item in target_records
        ),
        "total_missed_support": sum(item["missed_support_count"] for item in target_records),
        "total_false_positives": sum(item["false_positive_count"] for item in target_records),
        "total_predicted_mismatches": sum(item["predicted_mismatches"] for item in target_records),
        "row_digest": digest({"budget": budget, "rank": skeleton["rank"], "candidate_rank": matrix.rank, "targets": target_records}),
    }


def run(relation_inputs: list[Path], fixture_path: Path, families: list[str], budget_labels: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    relation_rows = []
    relation_hashes = []
    for path in relation_inputs:
        payload = json.loads(path.read_text(encoding="utf-8"))
        relation_rows.extend(payload["rows"])
        relation_hashes.append(sha256_file(path))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture_by_curve = {instance["curve"]["id"]: instance for instance in fixture["instances"]}
    rows = []
    for transcript in relation_rows:
        if transcript["family"] not in families:
            continue
        instance = fixture_by_curve[transcript["curve_id"]]
        family = next(item for item in instance["families"] if item["family"] == transcript["family"])
        b_size = len(family["factor_base"]["points"])
        budgets = [run_budget(instance["curve"], family, transcript, label, parse_budget(label, b_size)) for label in budget_labels]
        rows.append({"curve_id": transcript["curve_id"], "family": transcript["family"], "budgets": budgets})
    normalized = [{key: value for key, value in row.items()} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-sampled-locator-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "batch_source_sha256": sha256_file(BATCH_SOURCE),
            "relation_input_sha256": relation_hashes,
            "fixture_sha256": sha256_file(fixture_path),
        },
        "config": {
            "families": families,
            "budgets": budget_labels,
            "locator": "deterministic hash-ranked sampled predicted suffix columns",
            "shared_mode": "source sums keyed by indices",
            "baseline": "committed materialized D4 support in relation transcript",
            "source_tuple_enumeration": False,
            "full_predicted_suffix_scan": False,
        },
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "full_budget_exact": all(row["budgets"][-1]["all_support_exact"] for row in rows),
            "full_budget_witnesses_valid": all(row["budgets"][-1]["all_candidate_witnesses_valid"] for row in rows),
            "subfull_exact_budgets": {
                row["curve_id"] + ":" + row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"]]
                for row in rows
            },
            "known_p4027_source_prf_rank_deficient": any(
                row["curve_id"] == "recursive-toy-p4027-a2225-b3340-q4129"
                and row["family"] == "source_prf_x"
                and all(item["candidate_rank"] < item["dimensions"][1] + 1 for item in row["budgets"])
                for row in rows
            ),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Sampled suffix locator on two fixed generated toy relation transcripts; no generic ECDLP, exponent, deployed, descent, or asymptotic claim.",
        },
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("relation_inputs", nargs="+", type=Path)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--budgets", nargs="+", required=True)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.relation_inputs, args.fixture, args.families, args.budgets), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
