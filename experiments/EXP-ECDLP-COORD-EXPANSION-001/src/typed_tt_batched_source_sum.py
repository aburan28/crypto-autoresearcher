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
ROWSPACE_SOURCE = SCRIPT_PATH.with_name("typed_tt_rowspace_witness_locator.py")
SCALE_SOURCE = SCRIPT_PATH.with_name("typed_tt_rowspace_scale_probe.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ROWSPACE = load("typed_tt_rowspace_for_batched_source_sum", ROWSPACE_SOURCE)
SCALE = load("typed_tt_scale_for_batched_source_sum", SCALE_SOURCE)
ADAPTIVE = ROWSPACE.ADAPTIVE
STREAMING = ROWSPACE.STREAMING
TF = ROWSPACE.TF
ORACLE = ROWSPACE.ORACLE


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_ops() -> dict[str, int]:
    return {
        **ROWSPACE.zero_ops(),
        "predicate_field_multiplications": 0,
        "predicate_field_subtractions": 0,
    }


def add_ops(total: dict[str, int], extra: dict[str, int]) -> None:
    for key, value in extra.items():
        total[key] = total.get(key, 0) + int(value)


def snapshot(value: dict[str, int]) -> dict[str, int]:
    return {key: int(item) for key, item in value.items()}


class SourceSumCache:
    """Cache target-independent source points, or isolate them per target."""

    def __init__(self, advice: Any, share_across_targets: bool) -> None:
        self.advice = advice
        self.share_across_targets = share_across_targets
        self.cache: dict[Any, tuple[int, int] | None] = {}
        self.ops = zero_ops()
        self.peak_cache_bytes = 0
        self.peak_cache_entries = 0

    def _key(self, target_index: int, indices: tuple[int, ...]) -> Any:
        return indices if self.share_across_targets else (target_index, indices)

    def total(self, target_index: int, indices: tuple[int, ...]) -> tuple[int, int] | None:
        key = self._key(target_index, indices)
        if key in self.cache:
            self.ops["cache_hits"] += 1
            return self.cache[key]
        prefix = self.advice.prefix_for(indices[:3], self.ops)
        suffix = self.advice.suffix[indices[3:]]
        total = self.advice.curve.add(prefix, suffix, self.ops)
        self.ops["source_advice_reads"] += 2
        self.ops["logical_source_read_bytes"] += 2 * self.advice.point_payload_bytes
        self.cache[key] = total
        self.ops["unique_queries"] += 1
        return total

    def update_peak(self) -> None:
        self.peak_cache_bytes = max(self.peak_cache_bytes, STREAMING.CN.deep_size(self.cache))
        self.peak_cache_entries = max(self.peak_cache_entries, len(self.cache))

    def discard_target(self, target_index: int) -> None:
        if self.share_across_targets:
            return
        for key in [key for key in self.cache if key[0] == target_index]:
            del self.cache[key]

    def cache_bytes(self) -> int:
        return STREAMING.CN.deep_size(self.cache)


class BatchedPredicates:
    def __init__(self, source: SourceSumCache, targets: list[tuple[int, int]], p: int) -> None:
        self.source = source
        self.targets = targets
        self.p = p
        self.nu = ORACLE.nonsquare(p)
        self.caches = [dict() for _ in targets]
        self.ops = [zero_ops() for _ in targets]

    def value(self, target_index: int, indices: tuple[int, ...]) -> int:
        cache = self.caches[target_index]
        if indices in cache:
            self.ops[target_index]["cache_hits"] += 1
            return cache[indices]
        total = self.source.total(target_index, indices)
        if total is None:
            result = 1
        else:
            x, y = total
            tx, ty = self.targets[target_index]
            dx = (x - tx) % self.p
            dy = (y - ty) % self.p
            result = (dx * dx - self.nu * dy * dy) % self.p
            self.ops[target_index]["predicate_field_multiplications"] += 2
            self.ops[target_index]["predicate_field_subtractions"] += 1
        cache[indices] = result
        self.ops[target_index]["unique_queries"] += 1
        self.ops[target_index]["zero_hits"] += int(result == 0)
        return result

    def target_view(self, target_index: int) -> Any:
        parent = self

        class View:
            @property
            def ops(self) -> dict[str, int]:
                return parent.ops[target_index]

            @property
            def p(self) -> int:
                return parent.p

            def value(self, indices: tuple[int, ...]) -> int:
                return parent.value(target_index, indices)

        return View()

    def discard_target(self, target_index: int) -> None:
        self.caches[target_index].clear()


def evaluate_target(
    value: Any,
    reference: Any,
    skeleton: dict[str, Any],
    prefixes: list[tuple[int, int, int]],
    b_size: int,
    sample_columns: list[int],
) -> dict[str, Any]:
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    rank = skeleton["rank"]
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction = zero_ops()
    reference_cache: dict[tuple[int, ...], int] = {}
    mismatches = 0
    direct_mismatches = 0
    sampled_entries = 0
    for prefix in prefixes:
        sampled = [value.value(prefix + suffixes[column]) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, value.p)
        reconstruction["field_multiplications"] += rank * rank
        reconstruction["field_additions"] += rank * max(0, rank - 1)
        for column in sample_columns:
            indices = prefix + suffixes[column]
            actual = value.value(indices)
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % value.p
            reconstruction["field_multiplications"] += rank
            reconstruction["field_additions"] += max(0, rank - 1)
            mismatches += int(predicted != actual)
            if indices not in reference_cache:
                reference_cache[indices] = reference.value(indices)
            direct_mismatches += int(actual != reference_cache[indices])
            sampled_entries += 1
    return {
        "sampled_entries": sampled_entries,
        "mismatches": mismatches,
        "direct_reference_mismatches": direct_mismatches,
        "reconstruction_ops": reconstruction,
        "reference_unique_queries": len(reference_cache),
    }


def run_mode(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    targets: list[tuple[int, int]],
    sample_columns: list[int],
    validation_prefixes: list[tuple[int, int, int]],
    max_prefixes: int,
    share_across_targets: bool,
) -> dict[str, Any]:
    p = curve_record["p"]
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    source = SourceSumCache(advice, share_across_targets)
    predicates = BatchedPredicates(source, targets, p)
    build_view = predicates.target_view(0)
    skeleton = SCALE.bounded_adaptive_build(build_view, a_size, b_size, max_prefixes)
    source.update_peak()
    rank_ops = snapshot(skeleton["rank_counters"])
    reference_build_target = targets[0]
    source_snapshots = [snapshot(source.ops)]
    predicate_snapshots = [zero_ops()]
    for record in predicates.ops[:1]:
        add_ops(predicate_snapshots[0], record)
    target_results = []
    cache_peak_by_target = [source.peak_cache_bytes]
    for target_index, target in enumerate(targets):
        reference = ORACLE.Oracle(
            curve_record,
            ROWSPACE.target_family(family, list(target)),
        )
        result = evaluate_target(
            predicates.target_view(target_index),
            reference,
            skeleton,
            validation_prefixes,
            b_size,
            sample_columns,
        )
        target_results.append({
            "target_index": target_index,
            "target": list(target),
            "mismatches": result["mismatches"],
            "direct_reference_mismatches": result["direct_reference_mismatches"],
            "sampled_entries": result["sampled_entries"],
            "reference_unique_queries": result["reference_unique_queries"],
            "predicate_ops": snapshot(predicates.ops[target_index]),
            "reconstruction_ops": result["reconstruction_ops"],
        })
        source_snapshots.append(snapshot(source.ops))
        cumulative_predicate = zero_ops()
        for record in predicates.ops[: target_index + 1]:
            add_ops(cumulative_predicate, record)
        predicate_snapshots.append(cumulative_predicate)
        source.update_peak()
        cache_peak_by_target.append(source.peak_cache_bytes)
        if not share_across_targets:
            source.discard_target(target_index)
            predicates.discard_target(target_index)

    batch_widths = [1, 2, 4, 8, len(targets)]
    batches = []
    for width in batch_widths:
        width = min(width, len(targets))
        source_ops = snapshot(source_snapshots[width])
        add_ops(source_ops, advice.ops)
        source_ops["cache_bytes"] = max(cache_peak_by_target[: width + 1])
        source_ops["cache_entries"] = source.peak_cache_entries
        source_ops["logical_cache_payload_bytes"] = source.peak_cache_entries * advice.point_payload_bytes
        source_ops["advice_bytes"] = advice.retained_bytes()
        predicate_ops = snapshot(predicate_snapshots[width])
        reconstruction_ops = zero_ops()
        for item in target_results[:width]:
            add_ops(reconstruction_ops, item["reconstruction_ops"])
        batches.append({
            "width": width,
            "source_ops": source_ops,
            "predicate_ops": predicate_ops,
            "reconstruction_ops": reconstruction_ops,
            "rowspace_rank": skeleton["rank"],
            "all_sample_matches": all(item["mismatches"] == 0 for item in target_results[:width]),
            "all_direct_reference_exact": all(item["direct_reference_mismatches"] == 0 for item in target_results[:width]),
            "sampled_entries": sum(item["sampled_entries"] for item in target_results[:width]),
            "total_mismatches": sum(item["mismatches"] for item in target_results[:width]),
            "total_direct_reference_mismatches": sum(item["direct_reference_mismatches"] for item in target_results[:width]),
        })
    return {
        "mode": "shared_source_sums" if share_across_targets else "target_separated_control",
        "share_across_targets": share_across_targets,
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_count": len(targets),
        "target_stream_first": list(reference_build_target),
        "rowspace_rank": skeleton["rank"],
        "rowspace_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "rowspace_stopping_reason": skeleton["stopping_reason"],
        "sample_columns": len(sample_columns),
        "validation_prefixes": len(validation_prefixes),
        "source_advice": {
            "retained_bytes": advice.retained_bytes(),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "suffix_entries": len(advice.suffix),
            "build_ops": snapshot(advice.ops),
        },
        "source_cache": {
            "retained_bytes_after_run": source.cache_bytes(),
            "peak_bytes": source.peak_cache_bytes,
            "entries_peak": source.peak_cache_entries,
            "logical_payload_bytes_peak": source.peak_cache_entries * advice.point_payload_bytes,
            "entries_after_run": len(source.cache),
            "shared_key_shape": "indices" if share_across_targets else "target_and_indices",
        },
        "rank_ops": rank_ops,
        "targets": target_results,
        "batches": batches,
        "all_sample_matches": all(item["mismatches"] == 0 for item in target_results),
        "all_direct_reference_exact": all(item["direct_reference_mismatches"] == 0 for item in target_results),
        "source_ops_final": snapshot(source.ops),
        "predicate_ops_final": snapshot(predicate_snapshots[-1]),
        "row_digest": digest({
            "mode": "shared_source_sums" if share_across_targets else "target_separated_control",
            "rank": skeleton["rank"],
            "prefixes": skeleton["candidate_prefixes_examined"],
            "batches": batches,
        }),
    }


def validation_prefix_sample(a_size: int, b_size: int, limit: int, seed: int) -> list[tuple[int, int, int]]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    if limit >= len(prefixes):
        return prefixes
    ranked = sorted(
        range(len(prefixes)),
        key=lambda index: hashlib.sha256(f"ROWSPACE-BATCH-PREFIX|{seed}|{index}".encode("ascii")).digest(),
    )
    selected = set(ranked[:limit])
    return [prefix for index, prefix in enumerate(prefixes) if index in selected]


def run_row(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    sample_limit: int,
    target_budget_factor: int,
    max_prefixes: int,
    validation_prefix_limit: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    p = curve_record["p"]
    q = curve_record["q"]
    curve = TF.Curve(p, curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    seed = family["run_seed"] ^ 0x13198A2E
    target_limit = min(q - 1, target_budget_factor * (len(family["factor_base"]["points"]) + 1))
    targets = []
    for index, scalar in enumerate(TF.nonzero_scalar_stream(q, seed)):
        if index == target_limit:
            break
        point = curve.mul(scalar, generator, TF.Ops())
        targets.append(TF.point_from_json(TF.point_json(point)))
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    columns = SCALE.sample_columns(b_size, sample_limit, family["run_seed"] ^ 0xA5A5A5A5)
    prefixes = validation_prefix_sample(a_size, b_size, validation_prefix_limit, family["run_seed"] ^ 0x5A5A5A5A)
    target_tuples = [(int(x), int(y)) for x, y in targets]
    separated = run_mode(curve_record, family, target_tuples, columns, prefixes, max_prefixes, False)
    shared = run_mode(curve_record, family, target_tuples, columns, prefixes, max_prefixes, True)
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "dimensions": shared["dimensions"],
        "target_budget": target_limit,
        "targets_attempted": len(target_tuples),
        "sample_columns": columns,
        "validation_prefixes": prefixes,
        "separated_control": separated,
        "shared_candidate": shared,
        "same_rank": separated["rowspace_rank"] == shared["rowspace_rank"],
        "same_target_stream": [item["target"] for item in separated["targets"]] == [item["target"] for item in shared["targets"]],
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "separated": separated["row_digest"], "shared": shared["row_digest"]}),
    }


def run(input_path: Path, families: list[str], sample_limit: int, target_budget_factor: int, max_prefixes: int, validation_prefix_limit: int) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], sample_limit, target_budget_factor, max_prefixes, validation_prefix_limit))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-source-sum-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "rowspace_sha256": sha256_file(ROWSPACE_SOURCE),
            "scale_probe_sha256": sha256_file(SCALE_SOURCE),
            "input_sha256": sha256_file(input_path),
        },
        "config": {
            "families": families,
            "sample_limit": sample_limit,
            "target_budget_factor": target_budget_factor,
            "max_prefixes": max_prefixes,
            "validation_prefix_limit": validation_prefix_limit,
            "batch_widths": [1, 2, 4, 8, "all"],
            "positive_control": "shared source sums keyed only by indices",
            "negative_control": "source sums keyed by target and indices",
            "source_tuple_enumeration": False,
            "suffix_reconstruction_enumeration": False,
            "validation": "sampled direct source values plus independent Oracle reference",
        },
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_same_rank": all(row["same_rank"] for row in rows),
            "all_same_target_stream": all(row["same_target_stream"] for row in rows),
            "all_shared_sample_matches": all(row["shared_candidate"]["all_sample_matches"] for row in rows),
            "all_shared_direct_reference_exact": all(row["shared_candidate"]["all_direct_reference_exact"] for row in rows),
            "all_control_direct_reference_exact": all(row["separated_control"]["all_direct_reference_exact"] for row in rows),
            "shared_source_add_saving_observed": any(
                batch["source_ops"]["point_add_calls"] < row["separated_control"]["batches"][index]["source_ops"]["point_add_calls"]
                for row in rows
                for index, batch in enumerate(row["shared_candidate"]["batches"])
            ),
            "max_shared_cache_bytes": max(row["shared_candidate"]["source_cache"]["peak_bytes"] for row in rows),
            "max_shared_source_sums": max(row["shared_candidate"]["source_ops_final"]["unique_queries"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Fixed-curve target batching of sampled row-space source sums; no full support, relation, descent, exponent, or generic ECDLP claim.",
        },
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--target-budget-factor", type=int, default=1)
    parser.add_argument("--max-prefixes", type=int, default=64)
    parser.add_argument("--validation-prefix-limit", type=int, default=256)
    args = parser.parse_args()
    if args.sample_limit < 1 or args.target_budget_factor < 1 or args.max_prefixes < 1 or args.validation_prefix_limit < 1:
        raise SystemExit("sample-limit, target-budget-factor, max-prefixes, and validation-prefix-limit must be positive")
    print(json.dumps(run(args.input, args.families, args.sample_limit, args.target_budget_factor, args.max_prefixes, args.validation_prefix_limit), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
