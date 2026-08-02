#!/usr/bin/env python3
from __future__ import annotations

import argparse
import cmath
import copy
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("coord_energy_certificate.py")
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


def expected_seed(*parts: Any) -> int:
    data = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


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
        top = (3 * x1 * x1 + a) % p
        bottom = 2 * y1 % p
    else:
        top = (y2 - y1) % p
        bottom = (x2 - x1) % p
    slope = top * pow(bottom, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def census(
    generator: Point, q: int, p: int, a: int
) -> tuple[list[Point], dict[Point, int]]:
    sequence = []
    inverse = {}
    current: Point = None
    for scalar in range(q):
        if current in inverse:
            raise ValueError("early subgroup repetition")
        sequence.append(current)
        inverse[current] = scalar
        current = add(current, generator, p, a)
    if current is not None or len(inverse) != q:
        raise ValueError("invalid recorded subgroup order")
    return sequence, inverse


def d2_counts(values: tuple[int, ...], q: int) -> Counter[int]:
    result: Counter[int] = Counter()
    for left in values:
        for right in values:
            result[(left + right) % q] += 1
    return result


def d4_counts(values: tuple[int, ...], q: int) -> Counter[int]:
    result: Counter[int] = Counter()
    for route in itertools.product(values, repeat=4):
        result[sum(route) % q] += 1
    return result


def histogram(counts: Counter[int]) -> dict[str, int]:
    frequencies = Counter(counts.values())
    return {
        str(value): frequencies[value] for value in sorted(frequencies)
    }


def fourier_max(values: tuple[int, ...], q: int) -> float:
    factor = 2.0 * math.pi / q
    best = 0.0
    for frequency in range(1, (q + 1) // 2):
        real = 0.0
        imaginary = 0.0
        for value in values:
            phase = factor * frequency * value
            term = cmath.exp(1j * phase)
            real += term.real
            imaginary += term.imag
        best = max(best, math.hypot(real, imaginary))
    return round(best / len(values), 12)


def difference_concentration(
    values: tuple[int, ...], q: int
) -> float:
    counts: Counter[int] = Counter()
    for left in values:
        for right in values:
            if left != right:
                counts[(left - right) % q] += 1
    total = len(values) * (len(values) - 1)
    if total == 0:
        return 0.0
    return round(
        sum(sorted(counts.values(), reverse=True)[: len(values)])
        / total,
        12,
    )


def progression_cover(
    values: tuple[int, ...], q: int
) -> tuple[int, int, int]:
    support = set(values)
    width = len(values)
    best = (1, min(support), 1)
    for left, right in itertools.permutations(values, 2):
        for left_pos, right_pos in itertools.permutations(
            range(width), 2
        ):
            denominator = (left_pos - right_pos) % q
            step = (left - right) * pow(denominator, q - 2, q) % q
            if step == 0:
                continue
            start = (left - left_pos * step) % q
            cover = sum(
                (start + index * step) % q in support
                for index in range(width)
            )
            candidate = (cover, start, step)
            if candidate[0] > best[0] or (
                candidate[0] == best[0]
                and candidate[1:] < best[1:]
            ):
                best = candidate
    return best


def independent_metrics(
    raw_values: tuple[int, ...], q: int
) -> dict[str, Any]:
    values = tuple(sorted(value % q for value in raw_values))
    if len(values) != len(set(values)):
        raise ValueError("duplicate scalar")
    width = len(values)
    d2 = d2_counts(values, q)
    d4 = d4_counts(values, q)
    energy2 = sum(count * count for count in d2.values())
    energy4 = sum(count * count for count in d4.values())
    cover, start, step = progression_cover(values, q)
    return {
        "b_size": width,
        "scalar_set_digest": digest(list(values)),
        "d2": {
            "representation_total": sum(d2.values()),
            "support": len(d2),
            "energy": energy2,
            "normalized_energy": round(energy2 / width**2, 12),
            "maximum_multiplicity": max(d2.values()),
            "histogram": histogram(d2),
        },
        "d4": {
            "representation_total": sum(d4.values()),
            "support": len(d4),
            "energy": energy4,
            "normalized_energy": round(energy4 / width**4, 12),
            "maximum_multiplicity": max(d4.values()),
            "histogram": histogram(d4),
        },
        "max_nontrivial_fourier_normalized": fourier_max(values, q),
        "spectral_l4_mass_normalized": round(
            energy2 / width**4, 12
        ),
        "popular_difference_top_b_concentration": (
            difference_concentration(values, q)
        ),
        "best_length_b_progression": {
            "cover": cover,
            "fraction": round(cover / width, 12),
            "start_scalar": start,
            "step_scalar": step,
        },
        "diagnostic_classification": (
            "DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE"
        ),
    }


def scalar_null(
    q: int,
    width: int,
    seed: int,
    sequence: list[Point],
    inverse: dict[Point, int],
    p: int,
) -> tuple[int, ...]:
    rng = random.Random(seed)
    values: set[int] = set()
    attempts = 0
    while len(values) < width:
        attempts += 1
        if attempts > 1000 * width:
            raise RuntimeError("scalar null exhausted")
        sampled = sequence[rng.randrange(1, q)]
        if sampled is None:
            continue
        x_coord, y_coord = sampled
        canonical = (x_coord, min(y_coord, (-y_coord) % p))
        values.add(inverse[canonical])
    return tuple(sorted(values))


def x_null(
    curve: dict[str, Any],
    width: int,
    seed: int,
    inverse: dict[Point, int],
) -> tuple[int, ...]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    if p % 4 != 3:
        raise ValueError("unsupported null square-root branch")
    rng = random.Random(seed)
    seen_x: set[int] = set()
    values: set[int] = set()
    attempts = 0
    while len(values) < width:
        attempts += 1
        if attempts > width * 1000:
            raise RuntimeError("random-x verifier exhausted")
        x_coord = rng.randrange(p)
        if x_coord in seen_x:
            continue
        rhs = (x_coord**3 + a * x_coord + b) % p
        y_coord = pow(rhs, (p + 1) // 4, p)
        if y_coord * y_coord % p != rhs:
            continue
        y_coord = min(y_coord, (-y_coord) % p)
        candidate = (x_coord, y_coord)
        if candidate not in inverse:
            continue
        seen_x.add(x_coord)
        values.add(inverse[candidate])
    return tuple(sorted(values))


def percentile99(values: list[float | int]) -> float | int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.99 * len(ordered)) - 1)]


def features(
    value: Point, p: int, a: int, b: int
) -> dict[str, str]:
    names = [
        "x_bin_8",
        "y_bin_8",
        "chi_x",
        "chi_x_minus_1",
        "chi_x_minus_a",
        "chi_x_minus_b",
        "x_mod_3",
        "x_mod_5",
        "x_mod_7",
    ]
    if value is None:
        return {name: "O" for name in names}
    x_coord, y_coord = value

    def character(number: int) -> str:
        number %= p
        if number == 0:
            return "0"
        return "+" if pow(number, (p - 1) // 2, p) == 1 else "-"

    return {
        "x_bin_8": str(min(7, 8 * x_coord // p)),
        "y_bin_8": str(min(7, 8 * y_coord // p)),
        "chi_x": character(x_coord),
        "chi_x_minus_1": character(x_coord - 1),
        "chi_x_minus_a": character(x_coord - a),
        "chi_x_minus_b": character(x_coord - b),
        "x_mod_3": str(x_coord % 3),
        "x_mod_5": str(x_coord % 5),
        "x_mod_7": str(x_coord % 7),
    }


def d4_labeled(
    values: tuple[int, ...],
    q: int,
    sequence: list[Point],
    curve: dict[str, Any],
) -> list[dict[str, Any]]:
    counts = d4_counts(values, q)
    ordered_counts = sorted(counts.values())
    threshold = ordered_counts[
        max(0, math.ceil(0.8 * len(ordered_counts)) - 1)
    ]
    return [
        {
            "features": features(
                sequence[scalar],
                curve["p"],
                curve["a"],
                curve["b"],
            ),
            "multiplicity": count,
            "positive": count >= threshold,
        }
        for scalar, count in sorted(counts.items())
    ]


def evaluate_model(
    rows: list[dict[str, Any]],
    feature: str,
    buckets: set[str],
) -> dict[str, float | int]:
    selected = [
        row for row in rows if row["features"][feature] in buckets
    ]
    true_positive = sum(row["positive"] for row in selected)
    positives = sum(row["positive"] for row in rows)
    precision = true_positive / len(selected) if selected else 0.0
    recall = true_positive / positives if positives else 0.0
    base = sum(row["multiplicity"] for row in rows) / len(rows)
    predicted = (
        sum(row["multiplicity"] for row in selected) / len(selected)
        if selected
        else base
    )
    positive_rows = [row for row in rows if row["positive"]]
    oracle = (
        sum(row["multiplicity"] for row in positive_rows)
        / len(positive_rows)
        if positive_rows
        else base
    )
    gain = oracle - base
    retained = (predicted - base) / gain if gain > 0 else 0.0
    return {
        "rows": len(rows),
        "predicted": len(selected),
        "positives": positives,
        "true_positive": true_positive,
        "precision": round(precision, 12),
        "recall": round(recall, 12),
        "base_mean_multiplicity": round(base, 12),
        "predicted_mean_multiplicity": round(predicted, 12),
        "oracle_mean_multiplicity": round(oracle, 12),
        "retained_oracle_enrichment": round(retained, 12),
    }


def independent_fit(
    training: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
) -> dict[str, Any]:
    global_rate = sum(row["positive"] for row in training) / len(training)
    options = []
    for feature in sorted(training[0]["features"]):
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in training:
            groups[row["features"][feature]].append(row)
        ranked = sorted(
            groups,
            key=lambda bucket: (
                -sum(row["positive"] for row in groups[bucket])
                / len(groups[bucket]),
                bucket,
            ),
        )
        buckets = {
            bucket
            for bucket in ranked
            if (
                sum(row["positive"] for row in groups[bucket])
                / len(groups[bucket])
            )
            >= max(global_rate, 0.5)
        }
        if not buckets:
            buckets = {ranked[0]}
        metrics = evaluate_model(training, feature, buckets)
        denominator = metrics["precision"] + metrics["recall"]
        f1 = (
            2 * metrics["precision"] * metrics["recall"] / denominator
            if denominator > 0
            else 0.0
        )
        options.append(
            (round(f1, 12), feature, sorted(buckets), metrics)
        )
    _, selected_feature, selected_buckets, train_metrics = max(
        options, key=lambda item: (item[0], item[1], item[2])
    )
    heldout_metrics = evaluate_model(
        heldout, selected_feature, set(selected_buckets)
    )
    return {
        "feature": selected_feature,
        "selected_buckets": selected_buckets,
        "training": train_metrics,
        "heldout": heldout_metrics,
        "uses_scalar_feature": False,
        "passes_80_percent_enrichment": (
            heldout_metrics["retained_oracle_enrichment"] >= 0.8
            and heldout_metrics["precision"] > 0
            and heldout_metrics["recall"] > 0
        ),
    }


def reconstruct(
    typed: dict[str, Any], null_draws: int
) -> dict[str, Any]:
    curve_rows = []
    candidate_rows = []
    null_rows = []
    predictor_data: dict[str, list[tuple[int, list[dict[str, Any]]]]] = (
        defaultdict(list)
    )
    for curve_index, instance in enumerate(typed["instances"]):
        curve = instance["curve"]
        sequence, inverse = census(
            point(curve["generator"]),
            curve["q"],
            curve["p"],
            curve["a"],
        )
        families = {
            family["family"]: family for family in instance["families"]
        }
        width = len(families["random_x"]["factor_base"]["points"])
        curve_rows.append(
            {
                "curve_index": curve_index,
                "curve_id": curve["id"],
                "p": curve["p"],
                "q": curve["q"],
                "b_size": width,
                "census_digest": digest(
                    [point_json(value) for value in sequence]
                ),
                "census_entries": len(sequence),
            }
        )
        for null_kind in NULL_KINDS:
            for draw in range(null_draws):
                seed = expected_seed(
                    "coord-energy-cert-v1",
                    curve["id"],
                    null_kind,
                    draw,
                )
                values = (
                    scalar_null(
                        curve["q"],
                        width,
                        seed,
                        sequence,
                        inverse,
                        curve["p"],
                    )
                    if null_kind == "random_scalar"
                    else x_null(curve, width, seed, inverse)
                )
                null_rows.append(
                    {
                        "curve_index": curve_index,
                        "curve_id": curve["id"],
                        "null_kind": null_kind,
                        "draw": draw,
                        "seed": seed,
                        "metrics": independent_metrics(
                            values, curve["q"]
                        ),
                    }
                )
        for family_name in [*CANDIDATES, *FIXTURE_CONTROLS]:
            family = families[family_name]
            family_points = tuple(
                point(value) for value in family["factor_base"]["points"]
            )
            values = tuple(
                sorted(inverse[value] for value in family_points)
            )
            if tuple(sequence[value] for value in values) != tuple(
                sorted(family_points, key=lambda value: inverse[value])
            ):
                raise ValueError("candidate scalar replay failed")
            metrics = independent_metrics(values, curve["q"])
            candidate_rows.append(
                {
                    "curve_index": curve_index,
                    "curve_id": curve["id"],
                    "family": family_name,
                    "eligible_candidate": family_name in CANDIDATES,
                    "point_set_digest": digest(
                        [point_json(value) for value in family_points]
                    ),
                    "metrics": metrics,
                }
            )
            if family_name in CANDIDATES:
                predictor_data[family_name].append(
                    (
                        curve_index,
                        d4_labeled(
                            values, curve["q"], sequence, curve
                        ),
                    )
                )
    null_cells: dict[tuple[int, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for row in null_rows:
        null_cells[(row["curve_index"], row["null_kind"])].append(
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
            nulls = null_cells[(row["curve_index"], null_kind)]
            fields = {
                "d2_normalized_energy": (
                    metrics["d2"]["normalized_energy"],
                    [
                        value["metrics"]["d2"]["normalized_energy"]
                        for value in nulls
                    ],
                ),
                "d4_normalized_energy": (
                    metrics["d4"]["normalized_energy"],
                    [
                        value["metrics"]["d4"]["normalized_energy"]
                        for value in nulls
                    ],
                ),
                "max_fourier": (
                    metrics["max_nontrivial_fourier_normalized"],
                    [
                        value["metrics"][
                            "max_nontrivial_fourier_normalized"
                        ]
                        for value in nulls
                    ],
                ),
                "popular_difference": (
                    metrics[
                        "popular_difference_top_b_concentration"
                    ],
                    [
                        value["metrics"][
                            "popular_difference_top_b_concentration"
                        ]
                        for value in nulls
                    ],
                ),
                "progression_fraction": (
                    metrics["best_length_b_progression"]["fraction"],
                    [
                        value["metrics"]["best_length_b_progression"][
                            "fraction"
                        ]
                        for value in nulls
                    ],
                ),
            }
            receipt["nulls"][null_kind] = {}
            for name, (candidate, values) in fields.items():
                p99 = percentile99(values)
                receipt["nulls"][null_kind][name] = {
                    "candidate": candidate,
                    "p99": p99,
                    "exceeds_p99": candidate > p99,
                }
        receipt["energy_extreme"] = any(
            all(
                receipt["nulls"][kind][metric]["exceeds_p99"]
                for kind in NULL_KINDS
            )
            for metric in [
                "d2_normalized_energy",
                "d4_normalized_energy",
            ]
        )
        receipt["certificate_extreme"] = any(
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
        receipt["cell_extreme"] = (
            receipt["energy_extreme"]
            and receipt["certificate_extreme"]
        )
        comparisons.append(receipt)
    predictors = {}
    for family, values in predictor_data.items():
        ordered = sorted(values)
        training = [
            row for _, rows in ordered[:2] for row in rows
        ]
        predictors[family] = independent_fit(
            training, ordered[2][1]
        )
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in comparisons:
        by_family[row["family"]].append(row)
    family_gates = {}
    for family in CANDIDATES:
        all_sizes = all(row["cell_extreme"] for row in by_family[family])
        predictor_pass = predictors[family][
            "passes_80_percent_enrichment"
        ]
        family_gates[family] = {
            "all_sizes_extreme": all_sizes,
            "predictor_pass": predictor_pass,
            "positive_signal": all_sizes and predictor_pass,
        }
    summary = {
        "curves": len(curve_rows),
        "candidate_and_fixture_rows": len(candidate_rows),
        "null_rows": len(null_rows),
        "candidate_positive_signals": sum(
            value["positive_signal"] for value in family_gates.values()
        ),
        "scalar_positive_control_pass": all(
            row["cell_extreme"]
            for row in by_family["scalar_progression_control"]
        ),
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
    }
    return {
        "curves": curve_rows,
        "candidate_rows": candidate_rows,
        "null_rows": null_rows,
        "comparisons": comparisons,
        "predictors": predictors,
        "family_gates": family_gates,
        "summary": summary,
    }


def document_checks(
    raw: dict[str, Any],
    expected: dict[str, Any],
    typed_path: Path,
) -> dict[str, bool]:
    return {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "coord-energy-cert-v1"
        ),
        "claim_status": raw.get("claim_status")
        == [
            "HYPOTHESIS",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "producer_hash": raw["source"]["generator_sha256"]
        == file_hash(PRODUCER_PATH),
        "input_hash": raw["source"]["typed_input_sha256"]
        == file_hash(typed_path),
        "configured_input_path": (
            Path(raw["config"]["typed_input"]).resolve()
            == typed_path.resolve()
        ),
        "config_exact": raw["config"]
        == {
            "typed_input": str(typed_path.resolve()),
            "null_draws": 31,
            "candidate_families": CANDIDATES,
            "fixture_controls": FIXTURE_CONTROLS,
            "null_kinds": NULL_KINDS,
            "heldout_curve_index": 2,
        },
        "curves": raw["curves"] == expected["curves"],
        "candidate_rows": (
            raw["candidate_rows"] == expected["candidate_rows"]
        ),
        "null_rows": raw["null_rows"] == expected["null_rows"],
        "comparisons": raw["comparisons"] == expected["comparisons"],
        "predictors": raw["predictors"] == expected["predictors"],
        "family_gates": raw["family_gates"] == expected["family_gates"],
        "summary": raw["summary"] == expected["summary"],
        "telemetry_nonnegative": (
            raw["peak_rss_bytes"] >= 0
            and raw["total_wall_seconds"] >= 0
        ),
    }


def accepted(
    raw: dict[str, Any],
    expected: dict[str, Any],
    typed_path: Path,
) -> bool:
    try:
        return all(
            document_checks(raw, expected, typed_path).values()
        )
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def mutation_suite(
    raw: dict[str, Any],
    expected: dict[str, Any],
    typed_path: Path,
) -> dict[str, bool]:
    candidates = {}
    dropped_candidate = copy.deepcopy(raw)
    dropped_candidate["candidate_rows"].pop()
    candidates["dropped_candidate"] = dropped_candidate
    duplicate_null = copy.deepcopy(raw)
    duplicate_null["null_rows"].append(
        copy.deepcopy(duplicate_null["null_rows"][0])
    )
    candidates["duplicate_null"] = duplicate_null
    seed = copy.deepcopy(raw)
    seed["null_rows"][0]["seed"] += 1
    candidates["null_seed"] = seed
    energy = copy.deepcopy(raw)
    energy["candidate_rows"][0]["metrics"]["d4"]["energy"] += 1
    candidates["candidate_energy"] = energy
    fourier = copy.deepcopy(raw)
    fourier["null_rows"][0]["metrics"][
        "max_nontrivial_fourier_normalized"
    ] = 0.0
    candidates["null_fourier"] = fourier
    percentile = copy.deepcopy(raw)
    percentile["comparisons"][0]["nulls"]["random_scalar"][
        "d4_normalized_energy"
    ]["p99"] = -1
    candidates["percentile"] = percentile
    predictor = copy.deepcopy(raw)
    predictor["predictors"]["x_interval"]["feature"] = "scalar"
    candidates["predictor_feature"] = predictor
    gate = copy.deepcopy(raw)
    gate["family_gates"]["x_interval"]["positive_signal"] = True
    candidates["family_gate"] = gate
    summary = copy.deepcopy(raw)
    summary["summary"]["candidate_positive_signals"] += 1
    candidates["summary"] = summary
    advice = copy.deepcopy(raw)
    advice["summary"]["scalar_labels_attack_advice"] = True
    candidates["scalar_advice_boundary"] = advice
    promotion = copy.deepcopy(raw)
    promotion["summary"]["algorithm_promotion_gate"] = True
    candidates["promotion_gate"] = promotion
    source = copy.deepcopy(raw)
    source["source"]["generator_sha256"] = "0" * 64
    candidates["source_hash"] = source
    configured = copy.deepcopy(raw)
    configured["config"]["typed_input"] = "/tmp/false-input.json"
    candidates["configured_input"] = configured
    telemetry = copy.deepcopy(raw)
    telemetry["total_wall_seconds"] = -1
    candidates["telemetry"] = telemetry
    return {
        name: not accepted(candidate, expected, typed_path)
        for name, candidate in candidates.items()
    }


def verify(
    raw_path: Path, typed_override: Path | None
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    expected = reconstruct(typed, raw["config"]["null_draws"])
    checks = document_checks(raw, expected, typed_path)
    mutations = mutation_suite(raw, expected, typed_path)
    valid = all(checks.values()) and all(mutations.values())
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "coord-energy-cert-v1-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "producer_sha256": file_hash(PRODUCER_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "top_checks": checks,
        "mutation_rejections": mutations,
        "independent_d4_method": "direct_ordered_four_loop",
        "candidate_rows_reconstructed": len(expected["candidate_rows"]),
        "null_rows_reconstructed": len(expected["null_rows"]),
        "valid": valid,
        "boundary": (
            "Independent toy scalar-census, direct D4, Fourier, null, "
            "percentile, and coordinate-only predictor replay. No scalar "
            "label is certified as attack advice and no ECDLP improvement "
            "is claimed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--typed-input", type=Path)
    args = parser.parse_args()
    result = verify(args.raw_result, args.typed_input)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
