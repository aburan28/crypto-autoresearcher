#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
COORD_ROOT = SCRIPT_PATH.parents[2] / "EXP-ECDLP-COORD-EXPANSION-001" / "src"
BATCH_SOURCE = COORD_ROOT / "typed_tt_batched_source_sum.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BATCH = load("orbit_quotient_batched_source_sum", BATCH_SOURCE)
ADAPTIVE = BATCH.ADAPTIVE
STREAMING = BATCH.STREAMING
TF = BATCH.TF
ORACLE = BATCH.ORACLE


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_ops() -> dict[str, int]:
    return {
        **BATCH.zero_ops(),
        "quotient_point_additions": 0,
        "quotient_point_doublings": 0,
        "quotient_field_multiplications": 0,
        "quotient_field_inversions": 0,
        "quotient_field_subtractions": 0,
        "lift_queries": 0,
        "lift_zero_hits": 0,
        "lift_false_quotient_zeros": 0,
    }


def add_ops(total: dict[str, int], extra: dict[str, int]) -> None:
    for key, value in extra.items():
        total[key] = total.get(key, 0) + int(value)


def charged_cost(*vectors: dict[str, int]) -> dict[str, int]:
    keys = {key for vector in vectors for key in vector}
    return {key: sum(int(vector.get(key, 0)) for vector in vectors) for key in sorted(keys)}


def suffix_indices(b_size: int) -> list[tuple[int, int]]:
    return [(left, right) for left in range(b_size) for right in range(b_size)]


def class_key(point: tuple[int, int] | None) -> int | None:
    return None if point is None else int(point[0])


def build_orbit_classes(advice: Any) -> tuple[list[dict[str, Any]], dict[tuple[int, int], int], dict[str, int]]:
    grouped: dict[int | None, list[tuple[int, int]]] = {}
    for pair, point in advice.suffix.items():
        grouped.setdefault(class_key(point), []).append(pair)
    classes = []
    pair_to_class: dict[tuple[int, int], int] = {}
    for class_index, key in enumerate(sorted(grouped, key=lambda value: (-1 if value is None else value))):
        members = sorted(grouped[key])
        representative = members[0]
        point = advice.suffix[representative]
        record = {
            "class_index": class_index,
            "x_orbit_key": key,
            "representative": list(representative),
            "members": [list(item) for item in members],
            "member_count": len(members),
            "representative_point": None if point is None else list(point),
        }
        classes.append(record)
        for pair in members:
            pair_to_class[pair] = class_index
    summary = {
        "class_count": len(classes),
        "suffix_pair_count": len(advice.suffix),
        "duplicate_or_negation_pair_count": len(advice.suffix) - len(classes),
        "max_class_size": max((item["member_count"] for item in classes), default=0),
    }
    return classes, pair_to_class, summary


def predicate(value: tuple[int, int] | None, target: tuple[int, int], p: int, nu: int, ops: dict[str, int]) -> int:
    if value is None:
        return 1
    dx = (value[0] - target[0]) % p
    dy = (value[1] - target[1]) % p
    ops["quotient_field_multiplications"] += 2
    ops["quotient_field_subtractions"] += 1
    return (dx * dx - nu * dy * dy) % p


def neg_point(value: tuple[int, int] | None, p: int, ops: dict[str, int]) -> tuple[int, int] | None:
    if value is None:
        return None
    ops["quotient_field_subtractions"] += 1
    return value[0], (-value[1]) % p


class OrbitPredicates:
    """Target-specific norm predicates over source-derived suffix orbits."""

    def __init__(self, advice: Any, classes: list[dict[str, Any]], targets: list[tuple[int, int]], p: int) -> None:
        self.advice = advice
        self.classes = classes
        self.targets = targets
        self.p = p
        self.nu = ORACLE.nonsquare(p)
        self.cache = [dict() for _ in targets]
        self.ops = [zero_ops() for _ in targets]
        self.source_cache: dict[tuple[tuple[int, int, int], int], tuple[tuple[int, int] | None, tuple[int, int] | None]] = {}
        self.original_cache: dict[tuple[int, ...], tuple[int, int] | None] = {}
        self.source_ops = zero_ops()

    def source_pair(self, prefix: tuple[int, int, int], class_index: int) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
        key = (prefix, class_index)
        if key in self.source_cache:
            self.source_ops["cache_hits"] += 1
            return self.source_cache[key]
        point_prefix = self.advice.prefix_for(prefix, self.source_ops)
        representative = tuple(self.classes[class_index]["representative"])
        suffix = self.advice.suffix[representative]
        plus = self.advice.curve.add(point_prefix, suffix, self.source_ops)
        minus = self.advice.curve.add(point_prefix, neg_point(suffix, self.p, self.source_ops), self.source_ops)
        self.source_ops["quotient_point_additions"] += 2
        self.source_ops["unique_queries"] += 1
        self.source_cache[key] = (plus, minus)
        return plus, minus

    def value(self, target_index: int, prefix: tuple[int, int, int], class_index: int) -> int:
        key = prefix + (class_index,)
        cache = self.cache[target_index]
        if key in cache:
            self.ops[target_index]["cache_hits"] += 1
            return cache[key]
        ops = self.ops[target_index]
        plus, minus = self.source_pair(prefix, class_index)
        first = predicate(plus, self.targets[target_index], self.p, self.nu, ops)
        second = predicate(minus, self.targets[target_index], self.p, self.nu, ops)
        result = (first * second) % self.p
        ops["quotient_field_multiplications"] += 1
        ops["unique_queries"] += 1
        ops["zero_hits"] += int(result == 0)
        cache[key] = result
        return result

    def original_value(self, target_index: int, indices: tuple[int, ...]) -> int:
        ops = self.ops[target_index]
        if indices in self.original_cache:
            total = self.original_cache[indices]
            self.source_ops["cache_hits"] += 1
        else:
            prefix = self.advice.prefix_for(indices[:3], self.source_ops)
            suffix = self.advice.suffix[indices[3:]]
            total = self.advice.curve.add(prefix, suffix, self.source_ops)
            self.source_ops["unique_queries"] += 1
            self.original_cache[indices] = total
        ops["lift_queries"] += 1
        ops["source_advice_reads"] += 2
        ops["logical_source_read_bytes"] += 2 * self.advice.point_payload_bytes
        result = predicate(total, self.targets[target_index], self.p, self.nu, ops)
        ops["lift_zero_hits"] += int(result == 0)
        return result


def build_skeleton(predicates: OrbitPredicates, target_index: int, a_size: int, b_size: int, classes: list[dict[str, Any]]) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    class_count = len(classes)
    counters = zero_ops()
    basis_rows: list[list[int]] = []
    basis_prefixes = []
    echelon: dict[int, list[int]] = {}
    examined = 0
    for prefix in prefixes:
        examined += 1
        row = [predicates.value(target_index, prefix, index) for index in range(class_count)]
        if ADAPTIVE.SOURCE_AWARE.row_reduce_add(row, echelon, predicates.p, counters):
            basis_rows.append(row)
            basis_prefixes.append(prefix)
            if len(basis_rows) == class_count:
                break
    rank = len(basis_rows)
    pivot_columns, column_rank = ADAPTIVE.SOURCE_AWARE.column_pivots(basis_rows, predicates.p, counters) if rank else ([], 0)
    inverse = []
    if rank and column_rank == rank:
        cross = [[basis_rows[row][column] for column in pivot_columns] for row in range(rank)]
        inverse = ADAPTIVE.SOURCE_AWARE.inverse_matrix(cross, predicates.p, counters)
    add_ops(predicates.ops[target_index], counters)
    return {
        "rank": rank,
        "basis_rows": basis_rows,
        "basis_prefixes": basis_prefixes,
        "pivot_columns": pivot_columns,
        "inverse": inverse,
        "candidate_prefixes_examined": examined,
        "class_count": class_count,
        "full_class_rank": rank == class_count and column_rank == rank,
        "construction_ops": counters,
    }


def parse_budget(label: str, class_count: int) -> int:
    if label == "full":
        return class_count
    return min(class_count, max(1, int(label)))


def class_columns(class_count: int, budget: int) -> list[int]:
    if budget >= class_count:
        return list(range(class_count))
    return list(range(budget))


def valid_witness(curve: Any, a_points: list[Any], r_points: list[Any], indices: tuple[int, ...], target: Any, ops: Any) -> bool:
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index], ops)
    return total == target


def locate(predicates: OrbitPredicates, target_index: int, skeleton: dict[str, Any], a_size: int, b_size: int, classes: list[dict[str, Any]], columns: list[int]) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    rank = skeleton["rank"]
    if rank == 0 or not skeleton["inverse"]:
        return {"hits": [], "sampled_entries": 0, "predicted_mismatches": 0, "lift_queries": 0, "lift_false_quotient_zeros": 0, "reconstruction_ops": zero_ops()}
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction_ops = zero_ops()
    hits = []
    predicted_mismatches = 0
    sampled_entries = 0
    lift_queries = 0
    false_quotient_zeros = 0
    for prefix in prefixes:
        sampled = [predicates.value(target_index, prefix, column) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, predicates.p)
        reconstruction_ops["field_multiplications"] += rank * rank
        reconstruction_ops["field_additions"] += rank * max(0, rank - 1)
        for column in columns:
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % predicates.p
            actual = predicates.value(target_index, prefix, column)
            predicted_mismatches += int(predicted != actual)
            sampled_entries += 1
            reconstruction_ops["field_multiplications"] += rank
            reconstruction_ops["field_additions"] += max(0, rank - 1)
            if predicted != 0:
                continue
            members = [tuple(item) for item in classes[column]["members"]]
            for suffix in members:
                indices = prefix + suffix
                value = predicates.original_value(target_index, indices)
                lift_queries += 1
                if value == 0:
                    hits.append({"indices": list(indices), "a_index": indices[0], "suffix_class": column})
                else:
                    false_quotient_zeros += 1
    return {
        "hits": hits,
        "sampled_entries": sampled_entries,
        "predicted_mismatches": predicted_mismatches,
        "lift_queries": lift_queries,
        "lift_false_quotient_zeros": false_quotient_zeros,
        "reconstruction_ops": reconstruction_ops,
    }


def run_budget(curve_record: dict[str, Any], family: dict[str, Any], transcript: dict[str, Any], budget_label: str) -> dict[str, Any]:
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
    classes, pair_to_class, class_summary = build_orbit_classes(advice)
    budget = parse_budget(budget_label, len(classes))
    predicates = OrbitPredicates(advice, classes, targets, p)
    skeleton = build_skeleton(predicates, 0, a_size, b_size, classes)
    columns = class_columns(len(classes), budget)
    matrix = TF.IncrementalBasis(b_size + 1, q)
    relation_equations: list[dict[str, Any]] = []
    reconstruction_ops = zero_ops()
    witness_ops = TF.Ops()
    target_records = []
    for target_index, baseline in enumerate(baseline_transcripts):
        located = locate(predicates, target_index, skeleton, a_size, b_size, classes, columns)
        target_point = TF.point_from_json(list(targets[target_index]))
        candidate_set = {tuple(item["indices"]) for item in located["hits"]}
        baseline_set = {tuple([int(item["a_index"]), *[int(value) for value in item["r_witness"]]]) for item in baseline["baseline_hits"]}
        candidate_a = {indices[0] for indices in candidate_set}
        baseline_a = {indices[0] for indices in baseline_set}
        false_positives = sorted(candidate_a - baseline_a)
        missed_support = sorted(baseline_a - candidate_a)
        extra_witnesses = sorted(candidate_set - baseline_set)
        expected = baseline.get("expected_witness")
        expected_indices = None if expected is None else (int(expected["a_index"]), *[int(value) for value in expected["r_witness"]])
        candidate_witnesses_valid = all(valid_witness(curve, a_points, r_points, indices, target_point, witness_ops) for indices in candidate_set)
        for item in located["hits"]:
            indices = tuple(item["indices"])
            coefficients = TF.quotient_relation_coefficients(indices[0], indices[1:], b_size)
            equation = {"coefficients": coefficients, "rhs": int(baseline["scalar"]), "a_index": indices[0], "r_witness": list(indices[1:]), "suffix_class": int(item["suffix_class"])}
            if matrix.insert(coefficients, equation["rhs"]):
                relation_equations.append(equation)
        add_ops(reconstruction_ops, located["reconstruction_ops"])
        target_records.append({
            "target_index": target_index, "target": list(targets[target_index]), "label": baseline.get("label"),
            "held_out_supported": baseline.get("held_out_supported", False), "candidate_hits": located["hits"],
            "candidate_hit_count": len(candidate_set), "baseline_hit_count": len(baseline_set),
            "support_recall": len(candidate_a & baseline_a) / max(1, len(baseline_a)),
            "false_positive_count": len(false_positives), "missed_support_count": len(missed_support),
            "false_positives": list(false_positives), "missed_support": list(missed_support),
            "extra_valid_witness_count": len(extra_witnesses), "candidate_contains_expected_witness": expected_indices is None or expected_indices in candidate_set,
            "candidate_witnesses_valid": candidate_witnesses_valid, "predicted_mismatches": located["predicted_mismatches"],
            "sampled_entries": located["sampled_entries"], "lift_queries": located["lift_queries"],
            "lift_false_quotient_zeros": located["lift_false_quotient_zeros"], "candidate_rank_after_target": matrix.rank,
        })
    add_ops(reconstruction_ops, skeleton["construction_ops"])
    predicates_ops = zero_ops()
    for ops in predicates.ops:
        add_ops(predicates_ops, ops)
    add_ops(predicates_ops, predicates.source_ops)
    charged = charged_cost(predicates_ops, advice.ops, reconstruction_ops, TF.asdict(witness_ops), TF.asdict(matrix.ops))
    return {
        "budget_label": budget_label, "budget": budget, "sample_classes": columns,
        "sample_class_fraction": len(columns) / max(1, len(classes)), "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_count": len(targets), "quotient_class_summary": class_summary, "quotient_class_digest": digest(classes),
        "rowspace_rank": skeleton["rank"], "rowspace_class_count": len(classes), "rowspace_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "rowspace_full_class_rank": skeleton["full_class_rank"], "candidate_rank": matrix.rank, "candidate_full_rank": matrix.rank == b_size + 1,
        "candidate_advice_build_ops": dict(advice.ops), "candidate_quotient_ops": predicates_ops,
        "candidate_advice": {"retained_bytes": advice.retained_bytes(), "logical_payload_bytes": advice.logical_payload_bytes, "source_orbit_cache_entries": len(predicates.source_cache), "source_orbit_cache_bytes": STREAMING.CN.deep_size(predicates.source_cache), "original_lift_cache_entries": len(predicates.original_cache), "original_lift_cache_bytes": STREAMING.CN.deep_size(predicates.original_cache)},
        "candidate_reconstruction_ops": reconstruction_ops, "candidate_witness_ops": TF.asdict(witness_ops),
        "candidate_relation_matrix_ops": TF.asdict(matrix.ops), "candidate_predicted_entries": sum(item["sampled_entries"] for item in target_records),
        "candidate_lift_queries": sum(item["lift_queries"] for item in target_records), "full_quotient_entries": len(targets) * a_size * b_size * b_size * len(classes),
        "full_original_entries": len(targets) * a_size * b_size**4, "relation_equations": relation_equations,
        "charged_cost": charged,
        "target_records": target_records, "all_candidate_witnesses_valid": all(item["candidate_witnesses_valid"] for item in target_records),
        "all_support_exact": all(item["missed_support_count"] == 0 and item["false_positive_count"] == 0 for item in target_records),
        "all_held_out_support_exact": all(not item["held_out_supported"] or (item["missed_support_count"] == 0 and item["false_positive_count"] == 0 and item["candidate_contains_expected_witness"]) for item in target_records),
        "total_missed_support": sum(item["missed_support_count"] for item in target_records), "total_false_positives": sum(item["false_positive_count"] for item in target_records),
        "total_predicted_mismatches": sum(item["predicted_mismatches"] for item in target_records), "total_lift_false_quotient_zeros": sum(item["lift_false_quotient_zeros"] for item in target_records),
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
        budgets = [run_budget(instance["curve"], family, transcript, label) for label in budget_labels]
        rows.append({"curve_id": transcript["curve_id"], "family": transcript["family"], "budgets": budgets})
    return {
        "protocol": "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001-locator-v1", "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "batch_source_sha256": sha256_file(BATCH_SOURCE), "relation_input_sha256": relation_hashes, "fixture_sha256": sha256_file(fixture_path)},
        "config": {"families": families, "budgets": budget_labels, "locator": "source-derived x-orbit quotient with exact member lift", "shared_mode": "suffix source orbits keyed by x(R2+R3)", "baseline": "committed materialized D4 support in relation transcript", "selection_uses_targets": False, "selection_uses_relations": False},
        "rows": rows,
        "summary": {
            "rows": len(rows), "full_budget_exact": all(row["budgets"][-1]["all_support_exact"] for row in rows), "full_budget_witnesses_valid": all(row["budgets"][-1]["all_candidate_witnesses_valid"] for row in rows),
            "subfull_exact_budgets": {row["curve_id"] + ":" + row["family"]: [item["budget_label"] for item in row["budgets"][:-1] if item["all_support_exact"] and item["all_held_out_support_exact"] and item["candidate_full_rank"]] for row in rows},
            "breakthrough_claim": False, "algorithm_promotion_gate": False,
            "boundary": "Source-derived negation-orbit quotient on two fixed generated toy curves with charged member lift and matched rho; no generic ECDLP or exponent claim.",
        },
        "total_wall_seconds": time.perf_counter() - started, "result_digest": digest(rows),
    }
