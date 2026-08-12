#!/usr/bin/env python3
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import platform
import random
import resource
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None
CANDIDATES = ["x_interval", "source_prf_x", "rational_union"]
FIXTURE_CONTROLS = ["random_x", "scalar_progression_control"]
NULL_KINDS = ["random_scalar", "random_x"]


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


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def decode_point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def encode_point(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def ec_add(left: Point, right: Point, p: int, a: int) -> Point:
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
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def subgroup_census(
    generator: Point, q: int, p: int, a: int
) -> tuple[list[Point], dict[Point, int]]:
    points: list[Point] = []
    by_point: dict[Point, int] = {}
    current: Point = None
    for scalar in range(q):
        if current in by_point:
            raise ValueError("generator repeated before q")
        points.append(current)
        by_point[current] = scalar
        current = ec_add(current, generator, p, a)
    if current is not None or len(points) != q:
        raise ValueError("generator does not have recorded prime order")
    return points, by_point


def ordered_d2(scalars: tuple[int, ...], q: int) -> Counter[int]:
    return Counter((left + right) % q for left in scalars for right in scalars)


def ordered_d4(d2: Counter[int], q: int) -> Counter[int]:
    result: Counter[int] = Counter()
    for left, left_count in d2.items():
        for right, right_count in d2.items():
            result[(left + right) % q] += left_count * right_count
    return result


def representation_histogram(counts: Counter[int]) -> dict[str, int]:
    return {
        str(multiplicity): frequency
        for multiplicity, frequency in sorted(
            Counter(counts.values()).items()
        )
    }


def max_fourier_normalized(
    scalars: tuple[int, ...], q: int
) -> float:
    maximum = 0.0
    tau_over_q = 2.0 * math.pi / q
    for frequency in range(1, (q + 1) // 2):
        value = sum(
            cmath.exp(1j * tau_over_q * frequency * scalar)
            for scalar in scalars
        )
        maximum = max(maximum, abs(value))
    return round(maximum / len(scalars), 12)


def popular_difference_concentration(
    scalars: tuple[int, ...], q: int
) -> float:
    counts = Counter(
        (left - right) % q
        for left in scalars
        for right in scalars
        if left != right
    )
    denominator = len(scalars) * (len(scalars) - 1)
    if denominator == 0:
        return 0.0
    top = sorted(counts.values(), reverse=True)[: len(scalars)]
    return round(sum(top) / denominator, 12)


def best_progression_cover(
    scalars: tuple[int, ...], q: int
) -> tuple[int, int, int]:
    values = set(scalars)
    b_size = len(scalars)
    best = (1, min(values), 1)
    if b_size < 2:
        return best
    positions = range(b_size)
    for left in scalars:
        for right in scalars:
            if left == right:
                continue
            for left_pos in positions:
                for right_pos in positions:
                    if left_pos == right_pos:
                        continue
                    denominator = (left_pos - right_pos) % q
                    step = (left - right) * pow(denominator, -1, q) % q
                    if step == 0:
                        continue
                    start = (left - left_pos * step) % q
                    cover = sum(
                        (start + index * step) % q in values
                        for index in positions
                    )
                    candidate = (cover, start, step)
                    if candidate[0] > best[0] or (
                        candidate[0] == best[0]
                        and candidate[1:] < best[1:]
                    ):
                        best = candidate
    return best


def set_metrics(scalars: Iterable[int], q: int) -> dict[str, Any]:
    ordered = tuple(sorted(int(value) % q for value in scalars))
    if len(set(ordered)) != len(ordered):
        raise ValueError("factor-base scalars must be distinct")
    b_size = len(ordered)
    d2 = ordered_d2(ordered, q)
    d4 = ordered_d4(d2, q)
    d2_energy = sum(value * value for value in d2.values())
    d4_energy = sum(value * value for value in d4.values())
    cover, start, step = best_progression_cover(ordered, q)
    return {
        "b_size": b_size,
        "scalar_set_digest": digest(list(ordered)),
        "d2": {
            "representation_total": sum(d2.values()),
            "support": len(d2),
            "energy": d2_energy,
            "normalized_energy": round(
                d2_energy / (b_size**2), 12
            ),
            "maximum_multiplicity": max(d2.values()),
            "histogram": representation_histogram(d2),
        },
        "d4": {
            "representation_total": sum(d4.values()),
            "support": len(d4),
            "energy": d4_energy,
            "normalized_energy": round(
                d4_energy / (b_size**4), 12
            ),
            "maximum_multiplicity": max(d4.values()),
            "histogram": representation_histogram(d4),
        },
        "max_nontrivial_fourier_normalized": (
            max_fourier_normalized(ordered, q)
        ),
        "spectral_l4_mass_normalized": round(
            d2_energy / (b_size**4), 12
        ),
        "popular_difference_top_b_concentration": (
            popular_difference_concentration(ordered, q)
        ),
        "best_length_b_progression": {
            "cover": cover,
            "fraction": round(cover / b_size, 12),
            "start_scalar": start,
            "step_scalar": step,
        },
        "diagnostic_classification": (
            "DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE"
        ),
    }


def random_scalar_set(
    q: int,
    b_size: int,
    seed: int,
    census: list[Point],
    by_point: dict[Point, int],
    p: int,
) -> tuple[int, ...]:
    rng = random.Random(seed)
    scalars: set[int] = set()
    attempts = 0
    while len(scalars) < b_size:
        attempts += 1
        if attempts > 1000 * b_size:
            raise RuntimeError("random-scalar control exhausted attempts")
        scalar = rng.randrange(1, q)
        sampled = census[scalar]
        if sampled is None:
            continue
        x_coord, y_coord = sampled
        canonical = (x_coord, min(y_coord, (-y_coord) % p))
        scalars.add(by_point[canonical])
    return tuple(sorted(scalars))


def random_x_set(
    curve: dict[str, Any],
    b_size: int,
    seed: int,
    by_point: dict[Point, int],
) -> tuple[int, ...]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    if p % 4 != 3:
        raise ValueError("registered random-x control expects p mod 4 = 3")
    rng = random.Random(seed)
    selected_x: set[int] = set()
    scalars: set[int] = set()
    attempts = 0
    while len(scalars) < b_size:
        attempts += 1
        if attempts > 1000 * b_size:
            raise RuntimeError("random-x control exhausted attempts")
        x_coord = rng.randrange(p)
        if x_coord in selected_x:
            continue
        rhs = (x_coord**3 + a * x_coord + b) % p
        y_coord = pow(rhs, (p + 1) // 4, p)
        if y_coord * y_coord % p != rhs:
            continue
        y_coord = min(y_coord, (-y_coord) % p)
        candidate = (x_coord, y_coord)
        if candidate not in by_point:
            continue
        selected_x.add(x_coord)
        scalars.add(by_point[candidate])
    return tuple(sorted(scalars))


def nearest_rank_p99(values: list[float | int]) -> float | int:
    if not values:
        raise ValueError("empty percentile")
    ordered = sorted(values)
    index = max(0, math.ceil(0.99 * len(ordered)) - 1)
    return ordered[index]


def feature_map(
    point: Point, p: int, a: int, b: int
) -> dict[str, str]:
    if point is None:
        return {
            "x_bin_8": "O",
            "y_bin_8": "O",
            "chi_x": "O",
            "chi_x_minus_1": "O",
            "chi_x_minus_a": "O",
            "chi_x_minus_b": "O",
            "x_mod_3": "O",
            "x_mod_5": "O",
            "x_mod_7": "O",
        }
    x_coord, y_coord = point

    def chi(value: int) -> str:
        value %= p
        if value == 0:
            return "0"
        return "+" if pow(value, (p - 1) // 2, p) == 1 else "-"

    return {
        "x_bin_8": str(min(7, 8 * x_coord // p)),
        "y_bin_8": str(min(7, 8 * y_coord // p)),
        "chi_x": chi(x_coord),
        "chi_x_minus_1": chi(x_coord - 1),
        "chi_x_minus_a": chi(x_coord - a),
        "chi_x_minus_b": chi(x_coord - b),
        "x_mod_3": str(x_coord % 3),
        "x_mod_5": str(x_coord % 5),
        "x_mod_7": str(x_coord % 7),
    }


def labeled_d4_rows(
    scalars: tuple[int, ...],
    q: int,
    census: list[Point],
    curve: dict[str, Any],
) -> list[dict[str, Any]]:
    counts = ordered_d4(ordered_d2(scalars, q), q)
    multiplicities = sorted(counts.values())
    threshold = multiplicities[
        max(0, math.ceil(0.8 * len(multiplicities)) - 1)
    ]
    rows = []
    for scalar, multiplicity in sorted(counts.items()):
        rows.append(
            {
                "features": feature_map(
                    census[scalar],
                    curve["p"],
                    curve["a"],
                    curve["b"],
                ),
                "multiplicity": multiplicity,
                "positive": multiplicity >= threshold,
            }
        )
    return rows


def model_metrics(
    rows: list[dict[str, Any]],
    feature: str,
    buckets: set[str],
) -> dict[str, float | int]:
    predicted = [
        row for row in rows if row["features"][feature] in buckets
    ]
    true_positive = sum(row["positive"] for row in predicted)
    positives = sum(row["positive"] for row in rows)
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / positives if positives else 0.0
    base_mean = sum(row["multiplicity"] for row in rows) / len(rows)
    predicted_mean = (
        sum(row["multiplicity"] for row in predicted) / len(predicted)
        if predicted
        else base_mean
    )
    oracle = [row for row in rows if row["positive"]]
    oracle_mean = (
        sum(row["multiplicity"] for row in oracle) / len(oracle)
        if oracle
        else base_mean
    )
    denominator = oracle_mean - base_mean
    retained = (
        (predicted_mean - base_mean) / denominator
        if denominator > 0
        else 0.0
    )
    return {
        "rows": len(rows),
        "predicted": len(predicted),
        "positives": positives,
        "true_positive": true_positive,
        "precision": round(precision, 12),
        "recall": round(recall, 12),
        "base_mean_multiplicity": round(base_mean, 12),
        "predicted_mean_multiplicity": round(predicted_mean, 12),
        "oracle_mean_multiplicity": round(oracle_mean, 12),
        "retained_oracle_enrichment": round(retained, 12),
    }


def fit_predictor(
    training: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
) -> dict[str, Any]:
    feature_names = sorted(training[0]["features"])
    candidates = []
    global_rate = sum(row["positive"] for row in training) / len(training)
    for feature in feature_names:
        by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in training:
            by_bucket[row["features"][feature]].append(row)
        ranked = sorted(
            by_bucket,
            key=lambda bucket: (
                -sum(row["positive"] for row in by_bucket[bucket])
                / len(by_bucket[bucket]),
                bucket,
            ),
        )
        selected = {
            bucket
            for bucket in ranked
            if (
                sum(row["positive"] for row in by_bucket[bucket])
                / len(by_bucket[bucket])
            )
            >= max(global_rate, 0.5)
        }
        if not selected:
            selected = {ranked[0]}
        metrics = model_metrics(training, feature, selected)
        f1 = (
            2
            * metrics["precision"]
            * metrics["recall"]
            / (metrics["precision"] + metrics["recall"])
            if metrics["precision"] + metrics["recall"] > 0
            else 0.0
        )
        candidates.append(
            (round(f1, 12), feature, sorted(selected), metrics)
        )
    _, feature, buckets, training_metrics = max(
        candidates, key=lambda item: (item[0], item[1], item[2])
    )
    heldout_metrics = model_metrics(
        heldout, feature, set(buckets)
    )
    return {
        "feature": feature,
        "selected_buckets": buckets,
        "training": training_metrics,
        "heldout": heldout_metrics,
        "uses_scalar_feature": False,
        "passes_80_percent_enrichment": (
            heldout_metrics["retained_oracle_enrichment"] >= 0.8
            and heldout_metrics["precision"] > 0
            and heldout_metrics["recall"] > 0
        ),
    }


def run(typed_path: Path, null_draws: int) -> dict[str, Any]:
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    curve_rows = []
    candidate_rows = []
    null_rows = []
    predictor_inputs: dict[str, list[tuple[int, list[dict[str, Any]]]]] = (
        defaultdict(list)
    )
    for curve_index, instance in enumerate(typed["instances"]):
        curve = instance["curve"]
        p, q, a = curve["p"], curve["q"], curve["a"]
        census, by_point = subgroup_census(
            decode_point(curve["generator"]), q, p, a
        )
        by_family = {
            family["family"]: family for family in instance["families"]
        }
        b_size = len(by_family["random_x"]["factor_base"]["points"])
        curve_rows.append(
            {
                "curve_index": curve_index,
                "curve_id": curve["id"],
                "p": p,
                "q": q,
                "b_size": b_size,
                "census_digest": digest(
                    [encode_point(point) for point in census]
                ),
                "census_entries": len(census),
            }
        )
        for null_kind in NULL_KINDS:
            for draw in range(null_draws):
                seed = stable_seed(
                    "coord-energy-cert-v1",
                    curve["id"],
                    null_kind,
                    draw,
                )
                scalars = (
                    random_scalar_set(
                        q,
                        b_size,
                        seed,
                        census,
                        by_point,
                        p,
                    )
                    if null_kind == "random_scalar"
                    else random_x_set(
                        curve, b_size, seed, by_point
                    )
                )
                null_rows.append(
                    {
                        "curve_index": curve_index,
                        "curve_id": curve["id"],
                        "null_kind": null_kind,
                        "draw": draw,
                        "seed": seed,
                        "metrics": set_metrics(scalars, q),
                    }
                )
        for family_name in [*CANDIDATES, *FIXTURE_CONTROLS]:
            family = by_family[family_name]
            points = tuple(
                decode_point(value)
                for value in family["factor_base"]["points"]
            )
            scalars = tuple(sorted(by_point[point] for point in points))
            if tuple(census[scalar] for scalar in scalars) != tuple(
                sorted(points, key=lambda point: by_point[point])
            ):
                raise ValueError("point/scalar census replay failed")
            metrics = set_metrics(scalars, q)
            row = {
                "curve_index": curve_index,
                "curve_id": curve["id"],
                "family": family_name,
                "eligible_candidate": family_name in CANDIDATES,
                "point_set_digest": digest(
                    [encode_point(point) for point in points]
                ),
                "metrics": metrics,
            }
            candidate_rows.append(row)
            if family_name in CANDIDATES:
                predictor_inputs[family_name].append(
                    (
                        curve_index,
                        labeled_d4_rows(
                            scalars, q, census, curve
                        ),
                    )
                )
        print(
            f"measured {curve['id']} B={b_size}",
            file=sys.stderr,
            flush=True,
        )
    null_by_cell: dict[tuple[int, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for row in null_rows:
        null_by_cell[(row["curve_index"], row["null_kind"])].append(
            row
        )
    comparisons = []
    for row in candidate_rows:
        metrics = row["metrics"]
        receipt: dict[str, Any] = {
            "curve_index": row["curve_index"],
            "family": row["family"],
            "eligible_candidate": row["eligible_candidate"],
            "nulls": {},
        }
        for null_kind in NULL_KINDS:
            nulls = null_by_cell[(row["curve_index"], null_kind)]
            fields = {
                "d2_normalized_energy": (
                    metrics["d2"]["normalized_energy"],
                    [
                        item["metrics"]["d2"]["normalized_energy"]
                        for item in nulls
                    ],
                ),
                "d4_normalized_energy": (
                    metrics["d4"]["normalized_energy"],
                    [
                        item["metrics"]["d4"]["normalized_energy"]
                        for item in nulls
                    ],
                ),
                "max_fourier": (
                    metrics["max_nontrivial_fourier_normalized"],
                    [
                        item["metrics"][
                            "max_nontrivial_fourier_normalized"
                        ]
                        for item in nulls
                    ],
                ),
                "popular_difference": (
                    metrics[
                        "popular_difference_top_b_concentration"
                    ],
                    [
                        item["metrics"][
                            "popular_difference_top_b_concentration"
                        ]
                        for item in nulls
                    ],
                ),
                "progression_fraction": (
                    metrics["best_length_b_progression"]["fraction"],
                    [
                        item["metrics"]["best_length_b_progression"][
                            "fraction"
                        ]
                        for item in nulls
                    ],
                ),
            }
            receipt["nulls"][null_kind] = {
                name: {
                    "candidate": value,
                    "p99": nearest_rank_p99(null_values),
                    "exceeds_p99": value
                    > nearest_rank_p99(null_values),
                }
                for name, (value, null_values) in fields.items()
            }
        energy_extreme = any(
            all(
                receipt["nulls"][kind][metric]["exceeds_p99"]
                for kind in NULL_KINDS
            )
            for metric in [
                "d2_normalized_energy",
                "d4_normalized_energy",
            ]
        )
        certificate_extreme = any(
            all(
                receipt["nulls"][kind][metric]["exceeds_p99"]
                for kind in NULL_KINDS
            )
            for metric in [
                "max_fourier",
                "popular_difference",
                "progression_fraction",
            ]
        )
        receipt["energy_extreme"] = energy_extreme
        receipt["certificate_extreme"] = certificate_extreme
        receipt["cell_extreme"] = energy_extreme and certificate_extreme
        comparisons.append(receipt)
    predictors = {}
    for family, inputs in predictor_inputs.items():
        ordered = sorted(inputs)
        training = [
            row
            for curve_index, rows in ordered[:2]
            for row in rows
        ]
        heldout = ordered[2][1]
        predictors[family] = fit_predictor(training, heldout)
    comparison_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in comparisons:
        comparison_by_family[row["family"]].append(row)
    family_gates = {}
    for family in CANDIDATES:
        all_sizes_extreme = all(
            row["cell_extreme"]
            for row in comparison_by_family[family]
        )
        predictor_pass = predictors[family][
            "passes_80_percent_enrichment"
        ]
        family_gates[family] = {
            "all_sizes_extreme": all_sizes_extreme,
            "predictor_pass": predictor_pass,
            "positive_signal": all_sizes_extreme and predictor_pass,
        }
    scalar_control_pass = all(
        row["cell_extreme"]
        for row in comparison_by_family[
            "scalar_progression_control"
        ]
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "coord-energy-cert-v1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "generator_sha256": file_hash(SCRIPT_PATH),
            "typed_input_sha256": file_hash(typed_path),
        },
        "config": {
            "typed_input": str(typed_path.resolve()),
            "null_draws": null_draws,
            "candidate_families": CANDIDATES,
            "fixture_controls": FIXTURE_CONTROLS,
            "null_kinds": NULL_KINDS,
            "heldout_curve_index": 2,
        },
        "curves": curve_rows,
        "candidate_rows": candidate_rows,
        "null_rows": null_rows,
        "comparisons": comparisons,
        "predictors": predictors,
        "family_gates": family_gates,
        "summary": {
            "curves": len(curve_rows),
            "candidate_and_fixture_rows": len(candidate_rows),
            "null_rows": len(null_rows),
            "candidate_positive_signals": sum(
                gate["positive_signal"]
                for gate in family_gates.values()
            ),
            "scalar_positive_control_pass": scalar_control_pass,
            "all_representation_totals_valid": all(
                row["metrics"]["d2"]["representation_total"]
                == row["metrics"]["b_size"] ** 2
                and row["metrics"]["d4"]["representation_total"]
                == row["metrics"]["b_size"] ** 4
                for row in [*candidate_rows, *null_rows]
            ),
            "scalar_labels_attack_advice": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("typed_result", type=Path)
    parser.add_argument("--null-draws", type=int, default=31)
    args = parser.parse_args()
    result = run(args.typed_result, args.null_draws)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return (
        0
        if result["summary"]["all_representation_totals_valid"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
