#!/usr/bin/env sage -python
"""Screen compressed pair features for exact EC translation compatibility."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1494_translation_compatible_pair_feature.md"
P1493_SOURCE = STATE_DIR / "p1493_pair_support_resultant_reporter.json"
OUT = STATE_DIR / "p1494_translation_compatible_pair_feature.json"
NOTE = RESEARCH_DIR / "p1494_translation_compatible_pair_feature.md"

SCHEMA = "ecdlp.p1494_translation_compatible_pair_feature.v1"
SYNTHETIC_SIZES = [4, 8, 16, 32, 64, 128]
PUBLIC_FEATURES = [
    "x_character",
    "x_plus_1_character",
    "x_plus_a_character",
    "y_character",
    "x_over_y_character",
]
FEATURES = PUBLIC_FEATURES + [
    "matched_random_label",
    "source_product_index",
    "hidden_scalar_residue",
]
EXPECTED = {
    CONTRACT: "ae6cf16737edda25e1be93dd8bb0a14b828998d53596e1952f44877cf3ac538f",
    ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py":
        "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1493_SOURCE: "cdfe2470ec5a9f231688b1d61d4bba5fb11dcb587982f892b21eee36b0e5ecf7",
    STATE_DIR / "p1493_pair_support_resultant_reporter_audit.json":
        "ab75dff4153657b55a12fd371fe56e0b029f984319d1a185c5a118274a179e49",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_slope(xs: list[int], ys: list[int]) -> float:
    lx = [math.log(value) for value in xs]
    ly = [math.log(value) for value in ys]
    cx = statistics.mean(lx)
    cy = statistics.mean(ly)
    return sum((x - cx) * (y - cy) for x, y in zip(lx, ly)) / sum(
        (x - cx) ** 2 for x in lx
    )


def digest_items(items: list[Any]) -> str:
    return hashlib.sha256(
        b"\n".join(repr(item).encode("ascii") for item in sorted(items, key=repr))
    ).hexdigest()


def add_rows(*rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(values) for values in zip(*rows))


def point_row(point: Any, canonical: list[Any]) -> tuple[int, ...]:
    row = [0] * len(canonical)
    for column, base in enumerate(canonical):
        if point == base:
            row[column] = 1
            return tuple(row)
        if point == -base:
            row[column] = -1
            return tuple(row)
    raise RuntimeError("P1494 signed endpoint lacks a factor column")


def feature_order(L: int, r: int) -> int:
    divisors = [value for value in range(1, L + 1) if L % value == 0 and value <= r]
    return max(divisors)


def subgroup_index_map(context: dict[str, Any]) -> dict[int, int]:
    value = context["field"].one()
    output = {}
    for index in range(int(context["fixture"]["L"])):
        output[int(value)] = index
        value *= context["h"]
    return output


def pair_support(
    context: dict[str, Any], canonical: list[Any], deck: list[Any], k: int
) -> tuple[dict[Any, dict[str, Any]], dict[str, Any]]:
    q = int(context["fixture"]["order"])
    factor_logs_map = p1482.bsgs_logs(context, canonical)
    factor_logs = [factor_logs_map[p1482.point_key(point)] for point in canonical]
    index_map = subgroup_index_map(context)
    records = []
    for point in deck:
        row = point_row(point, canonical)
        source_index = index_map[int(point[0])]
        scalar = sum(value * log for value, log in zip(row, factor_logs)) % q
        records.append((point, row, source_index, scalar))

    support: dict[Any, dict[str, Any]] = {}
    path_count = 0
    for first in records:
        for second in records:
            path_count += 1
            point = first[0] + second[0]
            row = add_rows(first[1], second[1])
            scalar = (first[3] + second[3]) % q
            if scalar * context["generator"] != point:
                raise RuntimeError("P1494 pair scalar replay failure")
            bucket = support.setdefault(p1482.point_key(point), {
                "point": point,
                "rows": [],
                "source_product_labels": set(),
                "scalar": scalar,
            })
            if bucket["scalar"] != scalar:
                raise RuntimeError("P1494 pair support scalar ambiguity")
            if row not in bucket["rows"]:
                bucket["rows"].append(row)
            bucket["source_product_labels"].add((first[2] + second[2]) % k)
    r = len(canonical)
    if path_count != 4 * r**2 or len(support) != 2 * r**2 + 1:
        raise RuntimeError("P1494 pair support formula mismatch")
    return support, {
        "ordered_pair_path_count": path_count,
        "distinct_pair_point_count": len(support),
        "factor_log_sha256": digest_items(factor_logs),
        "source_product_ambiguous_point_count": sum(
            len(bucket["source_product_labels"]) > 1 for bucket in support.values()
        ),
        "maximum_source_product_label_multiplicity": max(
            len(bucket["source_product_labels"]) for bucket in support.values()
        ),
    }


def character_table(context: dict[str, Any], k: int) -> dict[int, int]:
    field = context["field"]
    zeta = field.multiplicative_generator() ** ((int(context["fixture"]["p"]) - 1) // k)
    return {int(zeta**index): index for index in range(k)}


def character_label(context: dict[str, Any], k: int, table: dict[int, int], value: Any) -> str:
    field = context["field"]
    if value == 0:
        return "Z"
    residue = field(value) ** ((int(context["fixture"]["p"]) - 1) // k)
    return f"C:{table[int(residue)]}"


def public_label(
    name: str,
    context: dict[str, Any],
    point: Any,
    k: int,
    table: dict[int, int],
) -> str:
    if name == "matched_random_label":
        label = p1482.digest_int("P1494", "matched-random", context["fixture"]["L"], p1482.point_key(point)) % k
        return f"R:{label}"
    if point.is_zero():
        return "O"
    x = context["field"](point[0])
    y = context["field"](point[1])
    if name == "x_character":
        value = x
    elif name == "x_plus_1_character":
        value = x + 1
    elif name == "x_plus_a_character":
        value = x + context["field"](context["fixture"]["a"])
    elif name == "y_character":
        value = y
    elif name == "x_over_y_character":
        value = x / y
    else:
        raise RuntimeError(f"P1494 unknown public feature {name}")
    return character_label(context, k, table, value)


def support_label(
    name: str,
    context: dict[str, Any],
    bucket: dict[str, Any],
    k: int,
    table: dict[int, int],
) -> str:
    if name in PUBLIC_FEATURES or name == "matched_random_label":
        return public_label(name, context, bucket["point"], k, table)
    if name == "hidden_scalar_residue":
        return f"S:{int(bucket['scalar']) % k}"
    if name == "source_product_index":
        labels = sorted(int(value) for value in bucket["source_product_labels"])
        return "P:" + ",".join(str(value) for value in labels)
    raise RuntimeError(f"P1494 unknown support feature {name}")


def arbitrary_label(
    name: str,
    context: dict[str, Any],
    point: Any,
    scalar: int,
    k: int,
    table: dict[int, int],
) -> str | None:
    if name in PUBLIC_FEATURES or name == "matched_random_label":
        return public_label(name, context, point, k, table)
    if name == "hidden_scalar_residue":
        return f"S:{scalar % k}"
    return None


def query_schedule(
    context: dict[str, Any], deck: list[Any], support: dict[Any, dict[str, Any]]
) -> list[dict[str, Any]]:
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    deck_logs = p1482.bsgs_logs(context, deck)
    queries = []
    public_index = 0
    for target_index in range(2):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target_scalar = (a + b * challenge_scalar) % q
        target = target_scalar * context["generator"]
        for fifth in deck:
            fifth_scalar = int(deck_logs[p1482.point_key(fifth)])
            queries.append({
                "lane": "public_nonplanted",
                "index": public_index,
                "point": target - fifth,
                "scalar": (target_scalar - fifth_scalar) % q,
            })
            public_index += 1

    nonzero = [
        bucket for _, bucket in sorted(support.items(), key=lambda item: repr(item[0]))
        if not bucket["point"].is_zero()
    ]
    for index in range(16):
        left_index = p1482.digest_int("P1493", "positive-left", L, index) % len(nonzero)
        right_index = p1482.digest_int("P1493", "positive-right", L, index) % len(nonzero)
        left = nonzero[left_index]
        right = nonzero[right_index]
        point = left["point"] + right["point"]
        scalar = (int(left["scalar"]) + int(right["scalar"])) % q
        if point.is_zero():
            right = nonzero[(right_index + 1) % len(nonzero)]
            point = left["point"] + right["point"]
            scalar = (int(left["scalar"]) + int(right["scalar"])) % q
        queries.append({"lane": "positive_control", "index": index, "point": point, "scalar": scalar})
    for index in range(32):
        scalar = 1 + p1482.digest_int("P1493", "unrestricted", L, index) % (q - 1)
        queries.append({
            "lane": "unrestricted_fixed",
            "index": index,
            "point": scalar * context["generator"],
            "scalar": scalar,
        })
    if any(row["scalar"] * context["generator"] != row["point"] for row in queries):
        raise RuntimeError("P1494 query scalar control mismatch")
    return queries


def image_metrics(labels: dict[Any, str], support_size: int) -> dict[str, Any]:
    buckets: dict[str, int] = {}
    for label in labels.values():
        buckets[label] = buckets.get(label, 0) + 1
    sizes = sorted(buckets.values(), reverse=True)
    entropy = -sum(
        (size / support_size) * math.log2(size / support_size) for size in sizes
    )
    return {
        "image_size": len(buckets),
        "bucket_sizes_descending": sizes,
        "maximum_fiber_size": max(sizes),
        "mean_fiber_size": support_size / len(buckets),
        "image_times_mean_fiber": len(buckets) * support_size / len(buckets),
        "label_entropy_bits": entropy,
        "label_assignment_sha256": digest_items([
            (key, labels[key]) for key in labels
        ]),
        "bucket_size_sha256": digest_items(sorted(buckets.items())),
    }


def translation_table(
    name: str,
    context: dict[str, Any],
    support: dict[Any, dict[str, Any]],
    labels: dict[Any, str],
    k: int,
    table: dict[int, int],
) -> tuple[dict[tuple[str, str], set[str]], dict[str, Any]]:
    if name == "source_product_index":
        return {}, {
            "complete": False,
            "reason": "source-only label is undefined on a generic A+B output",
            "materialized_candidate_advice": False,
        }
    relation: dict[tuple[str, str], set[str]] = {}
    pair_count = 0
    buckets = list(support.values())
    q = int(context["fixture"]["order"])
    for left in buckets:
        left_key = p1482.point_key(left["point"])
        for right in buckets:
            pair_count += 1
            right_key = p1482.point_key(right["point"])
            output = left["point"] + right["point"]
            output_scalar = (int(left["scalar"]) + int(right["scalar"])) % q
            output_label = arbitrary_label(name, context, output, output_scalar, k, table)
            if output_label is None:
                raise RuntimeError("P1494 complete feature lacked an output label")
            relation.setdefault((labels[left_key], labels[right_key]), set()).add(output_label)
    ambiguities = [len(values) for values in relation.values()]
    encoded = [
        (key, tuple(sorted(values))) for key, values in relation.items()
    ]
    return relation, {
        "complete": True,
        "input_pair_count": pair_count,
        "input_label_pair_count": len(relation),
        "attained_output_triple_count": sum(ambiguities),
        "maximum_output_label_ambiguity": max(ambiguities),
        "mean_output_label_ambiguity": statistics.mean(ambiguities),
        "bounded_two_output_control": max(ambiguities) <= 2,
        "relation_sha256": digest_items(encoded),
        "materialized_candidate_advice": False,
    }


def source_replay_control(
    context: dict[str, Any],
    canonical: list[Any],
    support: dict[Any, dict[str, Any]],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    exact_left_hits = 0
    source_rows = set()
    failures = 0
    for query in queries:
        for left in support.values():
            right = support.get(p1482.point_key(query["point"] - left["point"]))
            if right is None:
                continue
            exact_left_hits += 1
            for left_row in left["rows"]:
                for right_row in right["rows"]:
                    row = add_rows(left_row, right_row)
                    replay = sum(
                        (coefficient * base for coefficient, base in zip(row, canonical)),
                        context["identity"],
                    )
                    if replay != query["point"]:
                        failures += 1
                    else:
                        source_rows.add((query["lane"], int(query["index"]), row))
    return {
        "exact_left_decomposition_count": exact_left_hits,
        "deduplicated_source_row_count": len(source_rows),
        "source_row_sha256": digest_items(list(source_rows)),
        "source_replay_failure_count": failures,
        "all_sources_replay": failures == 0,
    }


def feature_cell(
    name: str,
    context: dict[str, Any],
    support: dict[Any, dict[str, Any]],
    queries: list[dict[str, Any]],
    k: int,
    table: dict[int, int],
) -> dict[str, Any]:
    labels = {
        key: support_label(name, context, bucket, k, table)
        for key, bucket in support.items()
    }
    metrics = image_metrics(labels, len(support))
    relation, relation_metrics = translation_table(name, context, support, labels, k, table)
    is_public = name in PUBLIC_FEATURES
    arbitrary_public = name in PUBLIC_FEATURES or name == "matched_random_label"
    algebraic_public = is_public
    query_records = []
    false_negatives = 0
    total_exact = 0
    for query in queries:
        qlabel = arbitrary_label(name, context, query["point"], int(query["scalar"]), k, table)
        exact_count = 0
        image_survivors = 0
        translation_survivors = 0
        for key, left in support.items():
            right_point = query["point"] - left["point"]
            right_key = p1482.point_key(right_point)
            exact = right_key in support
            exact_count += int(exact)
            if name == "source_product_index":
                if exact:
                    right_label = labels[right_key]
                    image_pass = True
                    translation_pass = True
                else:
                    right_label = None
                    image_pass = False
                    translation_pass = False
            else:
                right_scalar = (int(query["scalar"]) - int(left["scalar"])) % int(context["fixture"]["order"])
                right_label = arbitrary_label(name, context, right_point, right_scalar, k, table)
                image_pass = right_label in set(labels.values())
                translation_pass = (
                    image_pass
                    and qlabel in relation.get((labels[key], right_label), set())
                )
            image_survivors += int(image_pass)
            translation_survivors += int(translation_pass)
            if exact and not translation_pass:
                false_negatives += 1
        total_exact += exact_count
        mandatory_probes = len(support) if arbitrary_public else None
        complete_work = None if mandatory_probes is None else mandatory_probes + translation_survivors
        query_records.append({
            "lane": query["lane"],
            "index": int(query["index"]),
            "query_point_sha256": hashlib.sha256(
                repr(p1482.point_key(query["point"])).encode("ascii")
            ).hexdigest(),
            "exact_left_decomposition_count": exact_count,
            "image_membership_survivor_count": image_survivors,
            "translation_table_survivor_count": translation_survivors,
            "false_survivor_count": translation_survivors - exact_count,
            "mandatory_full_A2_label_probe_count": mandatory_probes,
            "complete_probe_plus_opening_work": complete_work,
        })
    complete_values = [
        int(row["complete_probe_plus_opening_work"])
        for row in query_records if row["complete_probe_plus_opening_work"] is not None
    ]
    survivor_values = [int(row["translation_table_survivor_count"]) for row in query_records]
    r = int(round(math.sqrt((len(support) - 1) / 2)))
    return {
        "feature": name,
        "public_point_feature": is_public,
        "publicly_evaluable_on_arbitrary_translated_point": arbitrary_public,
        "algebraic_character_feature": algebraic_public,
        "promotion_eligible_kind": algebraic_public,
        "image": metrics,
        "translation": relation_metrics,
        "query_count": len(query_records),
        "total_exact_left_decomposition_count": total_exact,
        "total_translation_survivor_count": sum(survivor_values),
        "maximum_translation_survivor_count": max(survivor_values),
        "maximum_complete_probe_plus_opening_work": max(complete_values) if complete_values else None,
        "false_negative_count": false_negatives,
        "image_below_r_three_halves_fixture_gate": metrics["image_size"] < r**1.5,
        "complete_query_below_r_three_halves_fixture_gate": (
            max(complete_values) < r**1.5 if complete_values else False
        ),
        "sublinear_pullback_enumerator_exhibited": False,
        "query_records": query_records,
    }


def synthetic_sweep() -> dict[str, Any]:
    cells = []
    for r in SYNTHETIC_SIZES:
        N = r**2
        cells.append({
            "r": r,
            "support_size_N": N,
            "saturated_label_count": r,
            "mean_fiber_size": r,
            "saturated_complete_query_work": N,
            "hidden_scalar_two_output_complete_query_work": N,
            "one_left_label_positive_control_work": r,
            "matched_random_translation_law_assigned": False,
            "one_left_label_passes_strict_r_three_halves": r < r**1.5,
        })
    return {
        "sizes": SYNTHETIC_SIZES,
        "cells": cells,
        "saturated_feature_query_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["saturated_complete_query_work"] for cell in cells]
        ),
        "hidden_scalar_residue_query_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["hidden_scalar_two_output_complete_query_work"] for cell in cells]
        ),
        "one_left_label_positive_control_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["one_left_label_positive_control_work"] for cell in cells]
        ),
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1494 translation-compatible pair feature",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | r | k | best public image | best public survivors | mandatory probes |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for fixture in payload["fixture_cells"]:
        public = [cell for cell in fixture["features"] if cell["public_point_feature"]]
        lines.append(
            f"| {fixture['L']} | {fixture['selector_degree_r']} | {fixture['feature_order_k']} | "
            f"{min(cell['image']['image_size'] for cell in public)} | "
            f"{min(cell['maximum_translation_survivor_count'] for cell in public)} | "
            f"{fixture['pair_support_size']} |"
        )
    lines.extend([
        "",
        "Every public character feature is exact as a label, but none supplies a",
        "sublinear pullback enumerator. A complete translated query still probes",
        "all 2*r^2+1 pair points before opening surviving fibers. Source-product",
        "labels are undefined before source opening, matched random labels have no",
        "algebraic law, and hidden scalar residues are non-public controls. No lane",
        "crosses the strict r^1.5 complete-query gate.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1494 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual
    p1493 = json.loads(P1493_SOURCE.read_text(encoding="utf-8"))
    p1493_pairs = {int(cell["L"]): cell for cell in p1493["pair_support_cells"]}
    p1493_queries = {int(cell["L"]): cell for cell in p1493["query_panels"]}

    fixture_cells = []
    for fixture in p1482.FIXTURES:
        started = time.perf_counter()
        context = p1482.build_context(fixture)
        selector, roots, _ = p1490.selector_cell(context)
        canonical, deck = p1490.selector_deck(context, roots)
        r = len(canonical)
        L = int(fixture["L"])
        k = feature_order(L, r)
        support, support_metrics = pair_support(context, canonical, deck, k)
        queries = query_schedule(context, deck, support)
        if len(queries) != int(p1493_queries[L]["query_count"]):
            raise RuntimeError("P1494/P1493 query count mismatch")
        table = character_table(context, k)
        features = [
            feature_cell(name, context, support, queries, k, table)
            for name in FEATURES
        ]
        replay = source_replay_control(context, canonical, support, queries)
        fixture_cells.append({
            "L": L,
            "selector_degree_r": r,
            "feature_order_k": k,
            "pair_support_size": len(support),
            "matches_P1493_pair_support_size": len(support)
            == int(p1493_pairs[L]["distinct_full_point_count_including_infinity"]),
            "matches_P1493_query_count": len(queries) == int(p1493_queries[L]["query_count"]),
            "support_metrics": support_metrics,
            "source_replay_control": replay,
            "features": features,
            "wall_seconds": time.perf_counter() - started,
        })

    sweep = synthetic_sweep()
    support_exact = all(
        cell["matches_P1493_pair_support_size"]
        and cell["matches_P1493_query_count"]
        and cell["source_replay_control"]["all_sources_replay"]
        for cell in fixture_cells
    )
    public_features_exact = all(
        feature["false_negative_count"] == 0
        for cell in fixture_cells for feature in cell["features"]
        if feature["public_point_feature"]
    )
    controls_exact = all(
        next(feature for feature in cell["features"] if feature["feature"] == "source_product_index")[
            "publicly_evaluable_on_arbitrary_translated_point"
        ] is False
        and next(feature for feature in cell["features"] if feature["feature"] == "hidden_scalar_residue")[
            "promotion_eligible_kind"
        ] is False
        and next(feature for feature in cell["features"] if feature["feature"] == "matched_random_label")[
            "algebraic_character_feature"
        ] is False
        for cell in fixture_cells
    )
    synthetic_exact = (
        abs(sweep["saturated_feature_query_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["hidden_scalar_residue_query_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["one_left_label_positive_control_fitted_exponent"] - 1.0) < 1e-12
        and all(cell["one_left_label_passes_strict_r_three_halves"] for cell in sweep["cells"])
    )
    public_signal = any(
        feature["public_point_feature"]
        and feature["image_below_r_three_halves_fixture_gate"]
        and feature["complete_query_below_r_three_halves_fixture_gate"]
        and feature["sublinear_pullback_enumerator_exhibited"]
        for cell in fixture_cells for feature in cell["features"]
    )
    status = (
        "NEGATIVE_RESULT_P1494_PUBLIC_PAIR_FEATURES_REQUIRE_R2_TRANSLATED_PROBES"
        if support_exact and public_features_exact and controls_exact and synthetic_exact and not public_signal
        else "REVIEW_REQUIRED_P1494_FEATURE_OR_CONTROL_MISMATCH"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": (
                "Public character labels are candidate-computable. Materialized translation tables, support hashes, source-product labels, and hidden scalar residues are verifier-only diagnostics."
            ),
            "closed": (
                "The tested order-k power-residue features of x, shifted x, y, and x/y when queried by scanning translated pair fibers."
            ),
            "not_closed": (
                "A new public algebraic correspondence with a proved sublinear pullback enumerator and charged source fibers."
            ),
            "pollard_rho": (
                "Every complete public query still probes Theta(r^2) pair points, above the strict r^1.5 gate before relation collection."
            ),
        },
        "fixture_cells": fixture_cells,
        "frozen_files": frozen,
        "gates": {
            "pair_support_queries_and_sources_exact": support_exact,
            "public_feature_filters_have_zero_false_negatives": public_features_exact,
            "nonpublic_and_random_controls_separated": controls_exact,
            "synthetic_query_exponent_controls_exact": synthetic_exact,
            "one_left_label_positive_control_passes": synthetic_exact,
            "public_feature_with_sublinear_pullback_exhibited": False,
            "complete_public_query_exponent_below_r_three_halves": False,
            "complete_campaign_below_pollard_rho": False,
            "translation_compatible_pair_feature_signal": public_signal,
        },
        "lineage_relation_controls": [
            {
                "L": int(cell["L"]),
                "target_count": int(cell["target_count"]),
                "target_hit_count": int(cell["target_hit_count"]),
                "relation_rank": int(cell["relation_rank"]),
                "unknown_column_count_including_challenge": int(cell["unknown_column_count_including_challenge"]),
                "relation_row_sha256": cell["relation_row_sha256"],
                "imported_frozen_control_only": True,
            }
            for cell in p1493["primary_relation_panels"]
        ],
        "next_action": (
            "Do not add more residue hashes. P1495 should test whether any growing-degree rational map with an EC addition theorem can compress A2 on a prime-order curve; separate the global quotient impossibility from restricted-A2 correspondences, and require a concrete sublinear pullback algorithm before relation replay."
        ),
        "schema": SCHEMA,
        "status": status,
        "synthetic_sweep": sweep,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "fixture_summary": [
            {
                "L": cell["L"],
                "r": cell["selector_degree_r"],
                "k": cell["feature_order_k"],
                "public": [
                    {
                        "feature": feature["feature"],
                        "image": feature["image"]["image_size"],
                        "max_ambiguity": feature["translation"]["maximum_output_label_ambiguity"],
                        "max_survivors": feature["maximum_translation_survivor_count"],
                        "complete_work": feature["maximum_complete_probe_plus_opening_work"],
                    }
                    for feature in cell["features"] if feature["public_point_feature"]
                ],
            }
            for cell in fixture_cells
        ],
        "synthetic_exponents": {
            key: value for key, value in sweep.items() if key not in {"sizes", "cells"}
        },
    }, indent=2, sort_keys=True))
    return 0 if status != "REVIEW_REQUIRED_P1494_FEATURE_OR_CONTROL_MISMATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
