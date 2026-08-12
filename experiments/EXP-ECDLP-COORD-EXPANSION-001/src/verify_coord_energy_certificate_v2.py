#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("coord_energy_certificate_v2.py")
RECURSIVE_PATH = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)
CONTRACT_PATH = (
    SCRIPT_PATH.parents[1]
    / "development"
    / "COORD-ENERGY-CERT-V2"
    / "contract.md"
)
Point = tuple[int, int] | None
CANDIDATES = (
    "coset_prefix_chain",
    "quartic_composition_chain",
    "reciprocal_denominator_chain",
)
CONFIRMATORY_CONFIG = {
    "bits": [10, 12, 14],
    "curve_seeds": [101, 211, 307],
    "null_draws": 2047,
    "predictor_permutations": 127,
}


def load_recursive() -> Any:
    spec = importlib.util.spec_from_file_location(
        "recursive_expansion_coord_energy_v2_verifier", RECURSIVE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {RECURSIVE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RECURSIVE = load_recursive()


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    ).hexdigest()


def stable_seed(*parts: Any) -> int:
    encoded = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")


def encode_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def decode_point(point: list[int] | None) -> Point:
    return None if point is None else (int(point[0]), int(point[1]))


def add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        numerator = (3 * x1 * x1 + a) % p
        denominator = 2 * y1 % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def negate(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def census(
    generator: Point, q: int, p: int, a: int
) -> tuple[list[Point], dict[Point, int]]:
    points = []
    inverse = {}
    current: Point = None
    for scalar in range(q):
        if current in inverse:
            raise ValueError("early generator cycle")
        points.append(current)
        inverse[current] = scalar
        current = add(current, generator, p, a)
    if current is not None:
        raise ValueError("generator order mismatch")
    return points, inverse


def curve_point(curve: dict[str, Any], x_coord: int) -> Point:
    p, a, b = curve["p"], curve["a"], curve["b"]
    rhs = (x_coord**3 + a * x_coord + b) % p
    y_coord = pow(rhs, (p + 1) // 4, p)
    if y_coord * y_coord % p != rhs:
        return None
    return x_coord, min(y_coord, (-y_coord) % p)


def append_x(
    curve: dict[str, Any],
    x_coord: int,
    source: dict[str, Any],
    selected: list[dict[str, Any]],
    seen_x: set[int],
) -> None:
    if x_coord in seen_x:
        return
    seen_x.add(x_coord)
    point = curve_point(curve, x_coord)
    if point is not None:
        selected.append({"point": encode_point(point), "source": source})


def reconstruct_factor_base(
    row: dict[str, Any], curve: dict[str, Any]
) -> dict[str, Any]:
    factor = row["factor_base"]
    family = factor["family"]
    b_size = factor["b_size"]
    params = factor["public_parameters"]
    selected: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    p = curve["p"]
    if family == "coset_prefix_chain":
        subgroup_generator = params["subgroup_generator"]
        order = params["subgroup_order"]
        for coset in params["visited_cosets"]:
            current = coset["representative"]
            for subgroup_rank in range(order):
                append_x(
                    curve,
                    current,
                    {
                        "coset_rank": coset["rank"],
                        "coset_index": coset["index"],
                        "subgroup_rank": subgroup_rank,
                        "coset_tag": coset["tag"],
                        "x": current,
                    },
                    selected,
                    seen_x,
                )
                if len(selected) == b_size:
                    break
                current = current * subgroup_generator % p
            if len(selected) == b_size:
                break
    elif family == "quartic_composition_chain":
        for t_value in range(params["truncation_t"] + 1):
            u_value = (t_value + params["c"]) % p
            v_value = (u_value * u_value + params["d"]) % p
            x_coord = (v_value * v_value + params["e"]) % p
            append_x(
                curve,
                x_coord,
                {
                    "t": t_value,
                    "u": u_value,
                    "v": v_value,
                    "x": x_coord,
                },
                selected,
                seen_x,
            )
    elif family == "reciprocal_denominator_chain":
        for t_value in range(params["truncation_t"] + 1):
            u_value = (t_value + params["c"]) % p
            denominator = (t_value + params["d"]) % p
            if denominator == 0:
                continue
            character = legendre(denominator, p)
            if character != params["denominator_character_stratum"]:
                continue
            inverse = pow(denominator, -1, p)
            numerator = u_value * u_value % p
            x_coord = (numerator * inverse + params["e"]) % p
            append_x(
                curve,
                x_coord,
                {
                    "t": t_value,
                    "u": u_value,
                    "numerator": numerator,
                    "denominator": denominator,
                    "denominator_inverse": inverse,
                    "denominator_character": character,
                    "x": x_coord,
                },
                selected,
                seen_x,
            )
    else:
        raise ValueError(f"unknown family: {family}")
    return {
        "points": [record["point"] for record in selected[:b_size]],
        "sources": [record["source"] for record in selected[:b_size]],
    }


def random_null(
    q: int,
    b_size: int,
    p: int,
    points: list[Point],
    inverse: dict[Point, int],
    seed: int,
) -> tuple[tuple[int, ...], int]:
    rng = random.Random(seed)
    result: set[int] = set()
    attempts = 0
    while len(result) < b_size:
        attempts += 1
        scalar = rng.randrange(1, q)
        point = points[scalar]
        assert point is not None
        canonical = (point[0], min(point[1], (-point[1]) % p))
        result.add(inverse[canonical])
    return tuple(sorted(result)), attempts


def direct_d4(
    scalars: tuple[int, ...], q: int
) -> tuple[Counter[int], Counter[int]]:
    d2 = Counter(
        (left + right) % q for left in scalars for right in scalars
    )
    d4: Counter[int] = Counter()
    for a_value in scalars:
        for b_value in scalars:
            for c_value in scalars:
                for d_value in scalars:
                    d4[(a_value + b_value + c_value + d_value) % q] += 1
    return d2, d4


def numerical_fourier(scalars: tuple[int, ...], q: int) -> dict[str, Any]:
    indicator = np.zeros(q, dtype=np.float64)
    indicator[list(scalars)] = 1.0
    transform = np.fft.fft(indicator)
    magnitudes = np.abs(transform[1 : (q + 1) // 2])
    frequency = int(np.argmax(magnitudes)) + 1
    coefficient = transform[frequency]
    conjugate = transform[q - frequency]
    return {
        "frequency": frequency,
        "real": round(float(coefficient.real), 12),
        "imag": round(float(coefficient.imag), 12),
        "magnitude": round(float(abs(coefficient)), 12),
        "magnitude_normalized": round(
            float(abs(coefficient)) / len(scalars), 12
        ),
        "conjugate_real": round(float(conjugate.real), 12),
        "conjugate_imag": round(float(conjugate.imag), 12),
        "conjugate_error": round(
            float(abs(conjugate - coefficient.conjugate())), 15
        ),
    }


def relation_data(
    scalars: tuple[int, ...], q: int
) -> tuple[set[tuple[int, ...]], int]:
    pair_vectors: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    b_size = len(scalars)
    for left in range(b_size):
        for right in range(left, b_size):
            vector = [0] * b_size
            vector[left] += 1
            vector[right] += 1
            pair_vectors[(scalars[left] + scalars[right]) % q].append(
                tuple(vector)
            )
    relations: set[tuple[int, ...]] = set()
    for vectors in pair_vectors.values():
        if len(vectors) < 2:
            continue
        anchor = vectors[0]
        for vector in vectors[1:]:
            relation = tuple(
                left - right for left, right in zip(vector, anchor)
            )
            first = next(value for value in relation if value)
            if first < 0:
                relation = tuple(-value for value in relation)
            relations.add(relation)
    rows = [[Fraction(value) for value in relation] for relation in relations]
    rank = 0
    columns = b_size
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for index in range(len(rows)):
            if index != rank and rows[index][column]:
                factor = rows[index][column]
                rows[index] = [
                    value - factor * base
                    for value, base in zip(rows[index], rows[rank])
                ]
        rank += 1
    return relations, rank


def public_differences(
    scalars: tuple[int, ...], q: int, points: list[Point]
) -> dict[str, Any]:
    counts: Counter[int] = Counter()
    for left in scalars:
        for right in scalars:
            if left != right:
                counts[(left - right) % q] += 1
    top = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            -1 if points[item[0]] is None else 0,
            0 if points[item[0]] is None else points[item[0]][0],
            0 if points[item[0]] is None else points[item[0]][1],
        ),
    )[: len(scalars)]
    return {
        "top": [
            {
                "difference_point": encode_point(points[difference]),
                "count": count,
            }
            for difference, count in top
        ],
        "count_sum": sum(count for _, count in top),
    }


def compact_metrics(
    scalars: tuple[int, ...],
    q: int,
    group_points: list[Point],
) -> tuple[dict[str, Any], Counter[int]]:
    d2, d4 = direct_d4(scalars, q)
    relations, rank = relation_data(scalars, q)
    fourier = numerical_fourier(scalars, q)
    differences = public_differences(scalars, q, group_points)
    return {
        "d2_support": len(d2),
        "d4_support": len(d4),
        "d2_energy": sum(value * value for value in d2.values()),
        "d4_energy": sum(value * value for value in d4.values()),
        "d4_normalized_energy": round(
            sum(value * value for value in d4.values())
            / len(scalars) ** 7,
            12,
        ),
        "fourier": fourier,
        "popular_count_sum": differences["count_sum"],
        "popular_density": round(
            differences["count_sum"]
            / (len(scalars) * (len(scalars) - 1)),
            12,
        ),
        "popular_top": differences["top"],
        "relation_count": len(relations),
        "relation_rank": rank,
        "freiman_dimension": len(scalars) - rank - 1,
        "scalar_set_digest": digest(list(scalars)),
    }, d4


def verify_public_certificate(
    factor_points: list[Point],
    raw_metrics: dict[str, Any],
    curve: dict[str, Any],
    expected_top: list[dict[str, Any]],
) -> bool:
    certificate = raw_metrics["certificates"]
    if [
        {
            "difference_point": row["difference_point"],
            "count": row["count"],
        }
        for row in certificate["popular_difference"]["top_differences"]
    ] != expected_top:
        return False
    recorded_top = certificate["popular_difference"]["top_differences"]
    p, a = curve["p"], curve["a"]
    for left_index, right_index, difference_rank in certificate[
        "popular_difference"
    ]["edges"]:
        difference = add(
            factor_points[left_index],
            negate(factor_points[right_index], p),
            p,
            a,
        )
        if encode_point(difference) != recorded_top[difference_rank][
            "difference_point"
        ]:
            return False
    for relation in certificate["freiman"]["basis"]:
        total: Point = None
        for point, coefficient in zip(factor_points, relation):
            signed = point if coefficient >= 0 else negate(point, p)
            for _ in range(abs(coefficient)):
                total = add(total, signed, p, a)
        if total is not None:
            return False
    return True


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def features(
    point: Point,
    curve: dict[str, Any],
    factor: dict[str, Any],
) -> dict[str, str]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    factor_points = [decode_point(value) for value in factor["points"]]
    factor_x = {
        value[0] for value in factor_points if value is not None
    }
    if point is None:
        return {
            "infinity": "1",
            "x_bin_8": "O",
            "y_bin_8": "O",
            "chi_x": "O",
            "chi_x_minus_1": "O",
            "chi_x_minus_a": "O",
            "chi_x_minus_b": "O",
            "x_mod_3": "O",
            "x_mod_5": "O",
            "x_mod_7": "O",
            "in_factor_x": "0",
            "anchor_denominator_pattern": "OOO",
            "family_target_stratum": "O",
        }
    x_coord, y_coord = point

    def chi(value: int) -> str:
        return {1: "+", 0: "0", -1: "-"}[legendre(value, p)]

    anchors = [
        value[0] for value in factor_points[:3] if value is not None
    ]
    anchor_pattern = "".join(
        chi(x_coord - anchor) for anchor in anchors
    ).ljust(3, "O")
    params = factor["public_parameters"]
    if factor["family"] == "coset_prefix_chain":
        tags = {row["tag"] for row in params["visited_cosets"]}
        if x_coord == 0:
            family_stratum = "zero"
        else:
            family_stratum = (
                "member"
                if pow(x_coord, params["subgroup_order"], p) in tags
                else "other"
            )
    elif factor["family"] == "quartic_composition_chain":
        family_stratum = chi(x_coord - params["e"]) + chi(
            x_coord - params["d"]
        )
    else:
        family_stratum = (
            chi(x_coord - params["e"])
            + ":"
            + str(params["denominator_character_stratum"])
        )
    return {
        "infinity": "0",
        "x_bin_8": str(min(7, 8 * x_coord // p)),
        "y_bin_8": str(min(7, 8 * y_coord // p)),
        "chi_x": chi(x_coord),
        "chi_x_minus_1": chi(x_coord - 1),
        "chi_x_minus_a": chi(x_coord - a),
        "chi_x_minus_b": chi(x_coord - b),
        "x_mod_3": str(x_coord % 3),
        "x_mod_5": str(x_coord % 5),
        "x_mod_7": str(x_coord % 7),
        "in_factor_x": "1" if x_coord in factor_x else "0",
        "anchor_denominator_pattern": anchor_pattern,
        "family_target_stratum": family_stratum,
    }


def target_rows(
    curve_index: int,
    curve: dict[str, Any],
    group_points: list[Point],
    d4: Counter[int],
    factor: dict[str, Any],
) -> list[dict[str, Any]]:
    multiplicities = [d4.get(value, 0) for value in range(curve["q"])]
    ordered = sorted(multiplicities)
    threshold = max(
        1, ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]
    )
    return [
        {
            "curve_index": curve_index,
            "features": features(point, curve, factor),
            "multiplicity": multiplicities[scalar],
            "positive": multiplicities[scalar] >= threshold,
        }
        for scalar, point in enumerate(group_points)
    ]


def model_metrics(
    rows: list[dict[str, Any]], feature: str, bucket: str
) -> dict[str, Any]:
    predicted = [
        row for row in rows if row["features"][feature] == bucket
    ]
    positives = [row for row in rows if row["positive"]]
    true_positive = sum(row["positive"] for row in predicted)
    base_mean = sum(row["multiplicity"] for row in rows) / len(rows)
    predicted_mean = (
        sum(row["multiplicity"] for row in predicted) / len(predicted)
        if predicted
        else base_mean
    )
    oracle_mean = (
        sum(row["multiplicity"] for row in positives) / len(positives)
        if positives
        else base_mean
    )
    denominator = oracle_mean - base_mean
    retained = (
        (predicted_mean - base_mean) / denominator
        if denominator > 0
        else 0.0
    )
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(positives) if positives else 0.0
    zero_rows = [row for row in rows if row["multiplicity"] == 0]
    zero_predicted = sum(
        row["features"][feature] == bucket for row in zero_rows
    )
    return {
        "rows": len(rows),
        "predicted": len(predicted),
        "positives": len(positives),
        "true_positive": true_positive,
        "precision": round(precision, 12),
        "recall": round(recall, 12),
        "f1": round(
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0,
            12,
        ),
        "base_mean_multiplicity": round(base_mean, 12),
        "predicted_mean_multiplicity": round(predicted_mean, 12),
        "oracle_mean_multiplicity": round(oracle_mean, 12),
        "retained_oracle_enrichment": round(retained, 12),
        "zero_support_rows": len(zero_rows),
        "zero_support_false_positive_rate": round(
            zero_predicted / len(zero_rows) if zero_rows else 0.0, 12
        ),
    }


def fit(
    training: list[dict[str, Any]], heldout: list[dict[str, Any]]
) -> dict[str, Any]:
    candidates = []
    for feature in sorted(training[0]["features"]):
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in training:
            buckets[row["features"][feature]].append(row)
        bucket = min(
            buckets,
            key=lambda value: (
                -sum(row["multiplicity"] for row in buckets[value])
                / len(buckets[value]),
                value,
            ),
        )
        metrics = model_metrics(training, feature, bucket)
        candidates.append(
            (
                metrics["retained_oracle_enrichment"],
                metrics["f1"],
                feature,
                [bucket],
                metrics,
            )
        )
    _, _, feature, selected, training_metrics = max(
        candidates, key=lambda item: (item[0], item[1], item[2], item[3])
    )
    return {
        "feature": feature,
        "selected_buckets": selected,
        "training": training_metrics,
        "heldout": model_metrics(heldout, feature, selected[0]),
        "feature_values_depend_only_on_target_coordinates": True,
    }


def permute_rows(
    rows: list[dict[str, Any]], seed: int
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["curve_index"]].append(row)
    result = []
    for curve_index in sorted(groups):
        group = groups[curve_index]
        labels = [
            (row["multiplicity"], row["positive"]) for row in group
        ]
        rng.shuffle(labels)
        for row, (multiplicity, positive) in zip(group, labels):
            result.append(
                {
                    **row,
                    "multiplicity": multiplicity,
                    "positive": positive,
                }
            )
    return result


def predictor(
    family: str,
    training: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    permutations: int,
) -> dict[str, Any]:
    observed = fit(training, heldout)
    observed_score = max(
        0.0, observed["heldout"]["retained_oracle_enrichment"]
    ) * observed["heldout"]["recall"]
    null_values = []
    for permutation in range(permutations):
        seed = stable_seed(
            "coord-energy-cert-v2-predictor", family, permutation
        )
        null = fit(
            permute_rows(training, seed),
            permute_rows(heldout, seed ^ 0x9E3779B97F4A7C15),
        )
        null_values.append(
            max(0.0, null["heldout"]["retained_oracle_enrichment"])
            * null["heldout"]["recall"]
        )
    p_value = (
        1 + sum(value >= observed_score for value in null_values)
    ) / (1 + permutations)
    by_curve: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in heldout:
        by_curve[row["curve_index"]].append(row)
    per_curve = []
    for curve_index in sorted(by_curve):
        metrics = model_metrics(
            by_curve[curve_index],
            observed["feature"],
            observed["selected_buckets"][0],
        )
        coverage = metrics["predicted"] / metrics["rows"]
        per_curve.append(
            {
                "curve_index": curve_index,
                "predicted_coverage": round(coverage, 12),
                "metrics": metrics,
                "passes": (
                    coverage >= 0.01
                    and metrics["recall"] >= 0.1
                    and metrics["precision"] > 0
                    and metrics["retained_oracle_enrichment"] >= 0.8
                ),
            }
        )
    return {
        **observed,
        "permutation_test": {
            "draws": permutations,
            "statistic": "max(0,retained_oracle_enrichment)*recall",
            "observed_score": round(observed_score, 12),
            "extreme_or_tied": sum(
                value >= observed_score for value in null_values
            ),
            "rank_p": round(p_value, 12),
            "null_min": min(null_values),
            "null_median": sorted(null_values)[permutations // 2],
            "null_max": max(null_values),
            "null_digest": digest(null_values),
        },
        "bonferroni_critical_value": round(0.05 / len(CANDIDATES), 12),
        "heldout_per_curve": per_curve,
        "passes": (
            observed["heldout"]["retained_oracle_enrichment"] >= 0.8
            and observed["heldout"]["precision"] > 0
            and observed["heldout"]["recall"] >= 0.1
            and all(row["passes"] for row in per_curve)
            and p_value <= 0.05 / len(CANDIDATES)
        ),
    }


def empirical_rank(
    candidate: float | int,
    null_values: list[float | int],
    direction: str,
) -> dict[str, Any]:
    if direction == "high":
        extreme = sum(value >= candidate for value in null_values)
        ties = sum(value == candidate for value in null_values)
        wins = sum(candidate > value for value in null_values)
    else:
        extreme = sum(value <= candidate for value in null_values)
        ties = sum(value == candidate for value in null_values)
        wins = sum(candidate < value for value in null_values)
    rank = round((1 + extreme) / (1 + len(null_values)), 12)
    return {
        "candidate": candidate,
        "direction": direction,
        "null_draws": len(null_values),
        "extreme_or_tied": extreme,
        "ties": ties,
        "rank_p": rank,
        "reference_tail_rank": rank,
        "interpretation": (
            "canonical_random_reference_tail_not_exchangeability_p_value"
        ),
        "tie_aware_auc": round(
            (wins + 0.5 * ties) / len(null_values), 12
        ),
        "null_min": min(null_values),
        "null_median": sorted(null_values)[len(null_values) // 2],
        "null_max": max(null_values),
        "null_values_digest": digest(null_values),
    }


def holm(tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(tests, key=lambda row: (row["p"], row["id"]))
    previous = 0.0
    rejecting = True
    results = []
    for index, row in enumerate(ordered):
        multiplier = len(ordered) - index
        adjusted = min(1.0, max(previous, multiplier * row["p"]))
        critical = 0.05 / multiplier
        reject = rejecting and row["p"] <= critical
        if not reject:
            rejecting = False
        previous = adjusted
        results.append(
            {
                **row,
                "holm_rank": index + 1,
                "critical_value": round(critical, 12),
                "adjusted_p": round(adjusted, 12),
                "reject": reject,
            }
        )
    return results


def verify(
    raw: dict[str, Any], allow_development: bool = False
) -> tuple[dict[str, Any], dict[str, Any]]:
    config = raw["config"]
    strict_config = (
        config["bits"] == CONFIRMATORY_CONFIG["bits"]
        and config["curve_seeds"] == CONFIRMATORY_CONFIG["curve_seeds"]
        and config["null_draws"] == CONFIRMATORY_CONFIG["null_draws"]
        and config["predictor_permutations"]
        == CONFIRMATORY_CONFIG["predictor_permutations"]
        and not config["development_mode"]
    )
    configuration_valid = strict_config or (
        allow_development
        and config["development_mode"]
        and len(config["bits"]) >= 3
        and config["bits"] == sorted(set(config["bits"]))
        and len(config["curve_seeds"])
        == len(set(config["curve_seeds"]))
    )
    source_checks = {
        "producer_hash": (
            raw["source"]["producer_sha256"] == file_hash(PRODUCER_PATH)
        ),
        "contract_hash": (
            raw["source"]["contract_sha256"] == file_hash(CONTRACT_PATH)
        ),
        "recursive_hash": (
            raw["source"]["recursive_source_sha256"]
            == file_hash(RECURSIVE_PATH)
        ),
        "coordinate_energy_hash": (
            raw["source"]["coordinate_energy_source_sha256"]
            == file_hash(Path(RECURSIVE.ENERGY_SOURCE_PATH))
        ),
    }
    telemetry_valid = raw["telemetry_digest"] == digest(
        {
            "peak_rss_bytes": raw["peak_rss_bytes"],
            "started_unix_seconds": raw["started_unix_seconds"],
            "finished_unix_seconds": raw["finished_unix_seconds"],
            "total_wall_seconds": raw["total_wall_seconds"],
        }
    )
    candidate_by_cell = {
        (row["curve_index"], row["family"]): row
        for row in raw["candidates"]
    }
    null_by_curve = {
        row["curve_index"]: row for row in raw["nulls"]
    }
    curve_state = {}
    null_expected = {}
    candidate_expected = {}
    predictor_inputs: dict[str, dict[str, list[dict[str, Any]]]] = {
        family: {"training": [], "heldout": []} for family in CANDIDATES
    }
    candidate_public_valid = True
    null_valid = True
    curve_valid = True
    for curve_row in raw["curves"]:
        curve_index = curve_row["curve_index"]
        regenerated = RECURSIVE.generate_prime_order_curve(
            curve_row["bits"], curve_row["curve_seed"]
        )
        if regenerated != curve_row["curve"]:
            curve_valid = False
        curve = curve_row["curve"]
        group_points, inverse = census(
            decode_point(curve["generator"]),
            curve["q"],
            curve["p"],
            curve["a"],
        )
        if (
            digest([encode_point(point) for point in group_points])
            != curve_row["census_digest"]
        ):
            curve_valid = False
        curve_state[curve_index] = (curve, group_points, inverse)
        null_record = null_by_curve[curve_index]
        expected_draws = []
        for draw in null_record["draws"]:
            scalars, attempts = random_null(
                curve["q"],
                curve_row["b_size"],
                curve["p"],
                group_points,
                inverse,
                draw["seed"],
            )
            metrics, _ = compact_metrics(
                scalars, curve["q"], group_points
            )
            expected = {
                "draw": draw["draw"],
                "seed": draw["seed"],
                "sampling_attempts": attempts,
                "canonicalizations": attempts,
                "d2_support": metrics["d2_support"],
                "d4_support": metrics["d4_support"],
                "d4_energy_ordered": metrics["d4_energy"],
                "d4_normalized_energy": metrics[
                    "d4_normalized_energy"
                ],
                "fourier_magnitude": metrics["fourier"][
                    "magnitude_normalized"
                ],
                "popular_difference_top_b_count_sum": metrics[
                    "popular_count_sum"
                ],
                "popular_difference_density": metrics[
                    "popular_density"
                ],
                "freiman_dimension": metrics["freiman_dimension"],
                "freiman_relation_rank": metrics["relation_rank"],
                "freiman_relation_count": metrics["relation_count"],
                "scalar_set_digest": metrics["scalar_set_digest"],
            }
            for key, value in expected.items():
                if draw[key] != value:
                    null_valid = False
            expected_draws.append(expected)
        null_expected[curve_index] = expected_draws
        if digest(null_record["draws"]) != null_record["draws_digest"]:
            null_valid = False
        for family in CANDIDATES:
            row = candidate_by_cell[(curve_index, family)]
            reconstructed = reconstruct_factor_base(row, curve)
            if reconstructed["points"] != row["factor_base"]["points"]:
                candidate_public_valid = False
            if reconstructed["sources"] != row["factor_base"]["sources"]:
                candidate_public_valid = False
            factor_points = [
                decode_point(value) for value in reconstructed["points"]
            ]
            scalars = tuple(inverse[point] for point in factor_points)
            metrics, d4 = compact_metrics(
                scalars, curve["q"], group_points
            )
            raw_metrics = row["metrics"]
            exact_pairs = {
                "d2_support": raw_metrics["d2"]["support"],
                "d4_support": raw_metrics["d4"]["support"],
                "d2_energy": raw_metrics["d2"]["energy"],
                "d4_energy": raw_metrics["d4"]["energy"],
                "d4_normalized_energy": raw_metrics["d4"][
                    "normalized_energy_e4_over_b7"
                ],
                "fourier": {
                    key: raw_metrics["certificates"]["fourier"][key]
                    for key in metrics["fourier"]
                },
                "popular_count_sum": raw_metrics[
                    "popular_difference_top_b_count_sum"
                ],
                "popular_density": raw_metrics[
                    "popular_difference_density"
                ],
                "popular_top": [
                    {
                        "difference_point": item["difference_point"],
                        "count": item["count"],
                    }
                    for item in raw_metrics["certificates"][
                        "popular_difference"
                    ]["top_differences"]
                ],
                "relation_count": raw_metrics[
                    "freiman_relation_count"
                ],
                "relation_rank": raw_metrics["freiman_relation_rank"],
                "freiman_dimension": raw_metrics["freiman_dimension"],
                "scalar_set_digest": raw_metrics["scalar_set_digest"],
            }
            if metrics != exact_pairs:
                candidate_public_valid = False
            if not verify_public_certificate(
                factor_points,
                raw_metrics,
                curve,
                metrics["popular_top"],
            ):
                candidate_public_valid = False
            candidate_expected[(curve_index, family)] = {
                "metrics": metrics,
                "d4": d4,
            }
            rows = target_rows(
                curve_index, curve, group_points, d4, row["factor_base"]
            )
            split = (
                "heldout"
                if curve_row["bits"] == max(config["bits"])
                else "training"
            )
            predictor_inputs[family][split].extend(rows)
    rank_tests_expected = {}
    energy_inputs = []
    certificate_inputs = []
    rank_valid = True
    for (curve_index, family), expected in candidate_expected.items():
        nulls = null_expected[curve_index]
        fields = {
            "d4_energy_ordered": (
                expected["metrics"]["d4_energy"],
                [row["d4_energy_ordered"] for row in nulls],
                "high",
            ),
            "fourier_magnitude": (
                expected["metrics"]["fourier"]["magnitude_normalized"],
                [row["fourier_magnitude"] for row in nulls],
                "high",
            ),
            "popular_difference_top_b_count_sum": (
                expected["metrics"]["popular_count_sum"],
                [
                    row["popular_difference_top_b_count_sum"]
                    for row in nulls
                ],
                "high",
            ),
            "freiman_dimension": (
                expected["metrics"]["freiman_dimension"],
                [row["freiman_dimension"] for row in nulls],
                "low",
            ),
        }
        tests = {
            name: empirical_rank(value, values, direction)
            for name, (value, values, direction) in fields.items()
        }
        rank_tests_expected[(curve_index, family)] = tests
        if candidate_by_cell[(curve_index, family)]["rank_tests"] != tests:
            rank_valid = False
        cell = f"{curve_index}:{family}"
        energy_inputs.append(
            {
                "id": f"{cell}:d4",
                "curve_index": curve_index,
                "family": family,
                "metric": "d4_energy_ordered",
                "p": tests["d4_energy_ordered"]["rank_p"],
            }
        )
        for metric in (
            "fourier_magnitude",
            "popular_difference_top_b_count_sum",
            "freiman_dimension",
        ):
            certificate_inputs.append(
                {
                    "id": f"{cell}:{metric}",
                    "curve_index": curve_index,
                    "family": family,
                    "metric": metric,
                    "p": tests[metric]["rank_p"],
                }
            )
    energy_holm = holm(energy_inputs)
    certificate_holm = holm(certificate_inputs)
    holm_valid = (
        raw["multiple_testing"]["primary_energy_holm"] == energy_holm
        and raw["multiple_testing"]["certificate_holm"]
        == certificate_holm
    )
    predictors_expected = {
        family: predictor(
            family,
            predictor_inputs[family]["training"],
            predictor_inputs[family]["heldout"],
            config["predictor_permutations"],
        )
        for family in CANDIDATES
    }
    predictor_valid = all(
        raw["predictors"][family] == predictors_expected[family]
        for family in CANDIDATES
    )
    control_rows_by_curve = {
        row["curve_index"]: row for row in raw["controls"]["curve_rows"]
    }
    control_arithmetic_valid = True
    true_ap_pass = True
    signed_ap_pass = True
    for curve_row in raw["curves"]:
        curve_index = curve_row["curve_index"]
        curve, group_points, _ = curve_state[curve_index]
        control = control_rows_by_curve[curve_index]
        nulls = null_expected[curve_index]
        for name in ("true_ap", "signed_ap"):
            scalars = tuple(control[name]["scalars"])
            metrics, _ = compact_metrics(
                scalars, curve["q"], group_points
            )
            recorded = control[name]["metrics"]
            core = {
                "d2_support": recorded["d2"]["support"],
                "d4_support": recorded["d4"]["support"],
                "d2_energy": recorded["d2"]["energy"],
                "d4_energy": recorded["d4"]["energy"],
                "d4_normalized_energy": recorded["d4"][
                    "normalized_energy_e4_over_b7"
                ],
                "fourier": {
                    key: recorded["certificates"]["fourier"][key]
                    for key in metrics["fourier"]
                },
                "popular_count_sum": recorded[
                    "popular_difference_top_b_count_sum"
                ],
                "popular_density": recorded[
                    "popular_difference_density"
                ],
                "popular_top": [
                    {
                        "difference_point": item["difference_point"],
                        "count": item["count"],
                    }
                    for item in recorded["certificates"][
                        "popular_difference"
                    ]["top_differences"]
                ],
                "relation_count": recorded[
                    "freiman_relation_count"
                ],
                "relation_rank": recorded["freiman_relation_rank"],
                "freiman_dimension": recorded["freiman_dimension"],
                "scalar_set_digest": recorded["scalar_set_digest"],
            }
            if metrics != core:
                control_arithmetic_valid = False
            if not verify_public_certificate(
                [group_points[scalar] for scalar in scalars],
                recorded,
                curve,
                metrics["popular_top"],
            ):
                control_arithmetic_valid = False
        true_expected_d4 = empirical_rank(
            control["true_ap"]["metrics"]["d4"]["energy"],
            [row["d4_energy_ordered"] for row in nulls],
            "high",
        )
        true_expected_fourier = empirical_rank(
            control["true_ap"]["metrics"][
                "fourier_magnitude_normalized"
            ],
            [row["fourier_magnitude"] for row in nulls],
            "high",
        )
        signed_expected_d4 = empirical_rank(
            control["signed_ap"]["metrics"]["d4"]["energy"],
            [row["d4_energy_ordered"] for row in nulls],
            "high",
        )
        if control["true_ap"]["d4_rank"] != true_expected_d4:
            control_arithmetic_valid = False
        if control["true_ap"]["fourier_rank"] != true_expected_fourier:
            control_arithmetic_valid = False
        if control["signed_ap"]["d4_rank"] != signed_expected_d4:
            control_arithmetic_valid = False
        true_ap_pass = true_ap_pass and (
            control["true_ap"]["exact_progression_verified"]
            and control["true_ap"]["metrics"]["freiman_dimension"] == 1
            and true_expected_d4["rank_p"] <= 0.01
            and true_expected_fourier["rank_p"] <= 0.01
            and control["true_ap"]["public_certificate_replay"]["valid"]
        )
        signed_ap_pass = signed_ap_pass and (
            signed_expected_d4["rank_p"] <= 0.01
            and control["signed_ap"]["public_certificate_replay"]["valid"]
        )
    planted_rows = []
    heldout_bits = max(config["bits"])
    for curve_row in raw["curves"]:
        curve_index = curve_row["curve_index"]
        curve, group_points, _ = curve_state[curve_index]
        dummy = {
            "family": "quartic_composition_chain",
            "points": [],
            "public_parameters": {"d": 0, "e": 0},
        }
        for point in group_points:
            feature_row = features(point, curve, dummy)
            positive = feature_row["chi_x_minus_1"] == "+"
            planted_rows.append(
                {
                    "curve_index": curve_index,
                    "bits": curve_row["bits"],
                    "features": feature_row,
                    "multiplicity": int(positive),
                    "positive": positive,
                }
            )
    planted_training = [
        row for row in planted_rows if row["bits"] < heldout_bits
    ]
    planted_heldout = [
        row for row in planted_rows if row["bits"] == heldout_bits
    ]
    control_positive = predictor(
        "public-coordinate-positive-control",
        planted_training,
        planted_heldout,
        config["predictor_permutations"],
    )
    control_negative = predictor(
        "permuted-coordinate-negative-control",
        permute_rows(
            planted_training,
            stable_seed("coord-energy-cert-v2-control", "training"),
        ),
        permute_rows(
            planted_heldout,
            stable_seed("coord-energy-cert-v2-control", "heldout"),
        ),
        config["predictor_permutations"],
    )
    control_predictor_valid = (
        raw["controls"]["predictor"]["positive"] == control_positive
        and raw["controls"]["predictor"]["negative"] == control_negative
    )
    positive_control_pass = (
        control_positive["feature"] == "chi_x_minus_1"
        and control_positive["heldout"][
            "retained_oracle_enrichment"
        ]
        >= 0.95
        and control_positive["passes"]
    )
    negative_control_pass = (
        not control_negative["passes"]
        and control_negative["heldout"][
            "retained_oracle_enrichment"
        ]
        <= 0.2
    )
    controls_expected = (
        true_ap_pass
        and signed_ap_pass
        and positive_control_pass
        and negative_control_pass
    )
    control_flags_valid = (
        raw["controls"]["true_ap_pass"] == true_ap_pass
        and raw["controls"]["signed_ap_pass"] == signed_ap_pass
        and raw["controls"]["predictor"]["positive_pass"]
        == positive_control_pass
        and raw["controls"]["predictor"]["negative_pass"]
        == negative_control_pass
        and raw["controls"]["all_pass"] == controls_expected
    )
    energy_lookup = {row["id"]: row for row in energy_holm}
    certificate_lookup = {row["id"]: row for row in certificate_holm}
    expected_family_gates = {}
    for family in CANDIDATES:
        cells = [
            row
            for row in raw["candidates"]
            if row["family"] == family
        ]
        energy_pass = all(
            energy_lookup[
                f"{row['curve_index']}:{family}:d4"
            ]["reject"]
            and rank_tests_expected[(row["curve_index"], family)][
                "d4_energy_ordered"
            ]["tie_aware_auc"]
            >= 0.65
            for row in cells
        )
        certificate_pass = all(
            any(
                certificate_lookup[
                    f"{row['curve_index']}:{family}:{metric}"
                ]["reject"]
                and rank_tests_expected[(row["curve_index"], family)][
                    metric
                ]["tie_aware_auc"]
                >= 0.65
                for metric in (
                    "popular_difference_top_b_count_sum",
                    "freiman_dimension",
                )
            )
            for row in cells
        )
        public_all = all(
            row["public_certificate_replay"]["valid"] for row in cells
        )
        before_controls = (
            energy_pass
            and certificate_pass
            and predictors_expected[family]["passes"]
            and public_all
        )
        expected_family_gates[family] = {
            "energy_all_nine": energy_pass,
            "certificate_each_curve": certificate_pass,
            "predictor_pass": predictors_expected[family]["passes"],
            "public_producer_replay_all_cells": public_all,
            "screening_signal_before_controls_and_verification": (
                before_controls
            ),
            "positive_signal": False,
            "controls_pass": controls_expected,
            "strict_confirmatory_configuration": strict_config,
            "construction_scalar_free": True,
            "producer_screening_signal": (
                before_controls and controls_expected and strict_config
            ),
            "awaiting_independent_verification": True,
        }
    family_gates_valid = raw["family_gates"] == expected_family_gates
    projection = {
        "protocol": raw["protocol"],
        "config": raw["config"],
        "source": raw["source"],
        "telemetry_digest": raw["telemetry_digest"],
        "peak_rss_bytes": raw["peak_rss_bytes"],
        "candidate_points": {
            f"{curve}:{family}": candidate_by_cell[(curve, family)][
                "factor_base"
            ]["points"]
            for curve, family in candidate_by_cell
        },
        "candidate_public_certificates": {
            f"{curve}:{family}": candidate_by_cell[(curve, family)][
                "metrics"
            ]["certificates"]
            for curve, family in candidate_by_cell
        },
        "candidate_public_replays": {
            f"{row['curve_index']}:{row['family']}": row[
                "public_certificate_replay"
            ]
            for row in raw["candidates"]
        },
        "nulls": raw["nulls"],
        "multiple_testing": raw["multiple_testing"],
        "predictors": raw["predictors"],
        "controls": raw["controls"],
        "summary": raw["summary"],
    }
    checks = {
        "configuration": configuration_valid,
        **source_checks,
        "telemetry_digest": telemetry_valid,
        "curves": curve_valid,
        "nulls": null_valid,
        "candidate_public_construction_and_certificates": (
            candidate_public_valid
        ),
        "exact_reference_ranks": rank_valid,
        "holm": holm_valid,
        "predictors": predictor_valid,
        "control_arithmetic_and_public_replay": control_arithmetic_valid,
        "control_predictors": control_predictor_valid,
        "control_flags": control_flags_valid,
        "family_gates": family_gates_valid,
        "producer_positive_signals_zero": (
            raw["summary"]["candidate_positive_signals"] == 0
        ),
        "development_cannot_screen": (
            not config["development_mode"]
            or raw["summary"]["producer_screening_signals"] == 0
        ),
        "scalar_free_construction": (
            raw["summary"]["construction_scalar_free"]
            and all(
                not row["factor_base"][
                    "construction_used_scalar_census"
                ]
                for row in raw["candidates"]
            )
        ),
    }
    receipt = {
        "valid": all(checks.values()),
        "checks": checks,
        "projection_digest": digest(projection),
        "curves_reconstructed": len(raw["curves"]),
        "null_sets_reconstructed": sum(
            len(row["draws"]) for row in raw["nulls"]
        ),
        "candidate_cells_reconstructed": len(raw["candidates"]),
        "target_rows_reconstructed": sum(
            curve["curve"]["q"] * len(CANDIDATES)
            for curve in raw["curves"]
        ),
        "independent_d4_method": "direct_ordered_four_loop",
        "producer_sha256": file_hash(PRODUCER_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
    }
    return receipt, projection


def mutation_results(
    raw: dict[str, Any], projection: dict[str, Any]
) -> dict[str, bool]:
    expected_digest = digest(projection)

    def rejected(mutated: dict[str, Any]) -> bool:
        candidate_projection = {
            "protocol": mutated["protocol"],
            "config": mutated["config"],
            "source": mutated["source"],
            "telemetry_digest": mutated["telemetry_digest"],
            "peak_rss_bytes": mutated["peak_rss_bytes"],
            "candidate_points": {
                f"{row['curve_index']}:{row['family']}": row[
                    "factor_base"
                ]["points"]
                for row in mutated["candidates"]
            },
            "candidate_public_certificates": {
                f"{row['curve_index']}:{row['family']}": row["metrics"][
                    "certificates"
                ]
                for row in mutated["candidates"]
            },
            "candidate_public_replays": {
                f"{row['curve_index']}:{row['family']}": row[
                    "public_certificate_replay"
                ]
                for row in mutated["candidates"]
            },
            "nulls": mutated["nulls"],
            "multiple_testing": mutated["multiple_testing"],
            "predictors": mutated["predictors"],
            "controls": mutated["controls"],
            "summary": mutated["summary"],
        }
        telemetry_ok = mutated["telemetry_digest"] == digest(
            {
                "peak_rss_bytes": mutated["peak_rss_bytes"],
                "started_unix_seconds": mutated["started_unix_seconds"],
                "finished_unix_seconds": mutated["finished_unix_seconds"],
                "total_wall_seconds": mutated["total_wall_seconds"],
            }
        )
        return digest(candidate_projection) != expected_digest or not telemetry_ok

    mutations = {}
    candidate_point = copy.deepcopy(raw)
    candidate_point["candidates"][0]["factor_base"]["points"][0][0] += 1
    mutations["candidate_point"] = candidate_point
    difference_point = copy.deepcopy(raw)
    difference_point["candidates"][0]["metrics"]["certificates"][
        "popular_difference"
    ]["top_differences"][0]["difference_point"][0] += 1
    mutations["difference_point"] = difference_point
    edge = copy.deepcopy(raw)
    edge["candidates"][0]["metrics"]["certificates"][
        "popular_difference"
    ]["edges"][0][0] = (
        edge["candidates"][0]["metrics"]["certificates"][
            "popular_difference"
        ]["edges"][0][0]
        + 1
    ) % edge["candidates"][0]["metrics"]["b_size"]
    mutations["difference_edge"] = edge
    freiman = copy.deepcopy(raw)
    freiman["controls"]["curve_rows"][0]["true_ap"]["metrics"][
        "certificates"
    ]["freiman"]["basis"][0][0] += 1
    mutations["freiman_basis"] = freiman
    null_value = copy.deepcopy(raw)
    null_value["nulls"][0]["draws"][0]["d4_energy_ordered"] += 1
    mutations["null_value"] = null_value
    holm_order = copy.deepcopy(raw)
    holm_order["multiple_testing"]["primary_energy_holm"].reverse()
    mutations["holm_order"] = holm_order
    predictor_bucket = copy.deepcopy(raw)
    predictor_bucket["predictors"][CANDIDATES[0]][
        "selected_buckets"
    ][0] += "x"
    mutations["predictor_bucket"] = predictor_bucket
    control = copy.deepcopy(raw)
    control["controls"]["all_pass"] = not control["controls"]["all_pass"]
    mutations["control"] = control
    telemetry_positive = copy.deepcopy(raw)
    telemetry_positive["peak_rss_bytes"] += 1
    mutations["telemetry_positive"] = telemetry_positive
    telemetry_negative = copy.deepcopy(raw)
    telemetry_negative["total_wall_seconds"] = -1
    mutations["telemetry_negative"] = telemetry_negative
    source_hash = copy.deepcopy(raw)
    source_hash["source"]["producer_sha256"] = "0" * 64
    mutations["source_hash"] = source_hash
    config = copy.deepcopy(raw)
    config["config"]["null_draws"] -= 1
    mutations["config"] = config
    summary = copy.deepcopy(raw)
    summary["summary"]["breakthrough_claim"] = True
    mutations["summary"] = summary
    scalar_boundary = copy.deepcopy(raw)
    scalar_boundary["summary"]["construction_scalar_free"] = False
    mutations["scalar_boundary"] = scalar_boundary
    return {name: rejected(value) for name, value in mutations.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.raw_result.read_text(encoding="utf-8"))
    receipt, projection = verify(raw, args.development)
    mutations = mutation_results(raw, projection)
    receipt["mutation_rejections"] = mutations
    receipt["all_mutations_rejected"] = all(mutations.values())
    receipt["raw_result_sha256"] = file_hash(args.raw_result)
    receipt["verified_provisional_signals"] = (
        sum(
            gate["producer_screening_signal"]
            for gate in raw["family_gates"].values()
        )
        if receipt["valid"] and receipt["all_mutations_rejected"]
        else 0
    )
    receipt["verified_positive_signals"] = 0
    receipt["boundary"] = (
        "Independent curve/candidate/null replay, direct D4, public EC "
        "certificate replay, exact ranks, predictor replay, and mutations. "
        "A verified provisional signal is not an ECDLP improvement."
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] and receipt["all_mutations_rejected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
