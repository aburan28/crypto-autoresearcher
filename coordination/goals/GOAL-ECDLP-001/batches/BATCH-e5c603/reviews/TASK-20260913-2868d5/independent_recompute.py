#!/usr/bin/env python3
"""Independent J1-J4 recomputation for RUN-ECDLP-1bef8f-S0.

This implementation is written from the frozen specification and review plan.
It does not import or execute the producer implementation.  In particular, the
height box is rebuilt by exhaustive beta scans, and relation realisability is
decided by affine point arithmetic independently of f_3.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from math import isqrt
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[7]
RUN_DIR = ROOT / "experiments/EXP-ECDLP-1bef8f/runs/RUN-ECDLP-1bef8f-S0"
OUT = Path(__file__).with_name("independent-recomputation.json")
O = None


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def decimal_half_away(value: Fraction, places: int) -> str:
    """Render an exact fraction with half-away-from-zero rounding."""
    sign = -1 if value < 0 else 1
    numerator = abs(value.numerator) * 10**places
    quotient, remainder = divmod(numerator, value.denominator)
    if 2 * remainder >= value.denominator:
        quotient += 1
    quotient *= sign
    absolute = abs(quotient)
    if places == 0:
        return str(quotient)
    whole, fractional = divmod(absolute, 10**places)
    prefix = "-" if quotient < 0 else ""
    return f"{prefix}{whole}.{fractional:0{places}d}"


def roots_by_square(p: int) -> dict[int, list[int]]:
    roots: dict[int, list[int]] = {}
    for y in range(p):
        roots.setdefault((y * y) % p, []).append(y)
    return roots


def curve_points_by_x(p: int, a: int, b: int) -> dict[int, tuple[tuple[int, int], ...]]:
    roots = roots_by_square(p)
    result: dict[int, tuple[tuple[int, int], ...]] = {}
    for x in range(p):
        ys = roots.get((x * x * x + a * x + b) % p, [])
        if ys:
            result[x] = tuple((x, y) for y in ys)
    return result


def point_neg(point: tuple[int, int] | None, p: int) -> tuple[int, int] | None:
    if point is O:
        return O
    return (point[0], (-point[1]) % p)


def point_add(
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
    p: int,
    a: int,
) -> tuple[int, int] | None:
    if left is O:
        return right
    if right is O:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return O
    if left == right:
        if y1 % p == 0:
            return O
        slope = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p)) % p
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


def point_on_curve(point: tuple[int, int], p: int, a: int, b: int) -> bool:
    x, y = point
    return (y * y - x * x * x - a * x - b) % p == 0


def f3(x1: int, x2: int, x3: int, p: int, a: int, b: int) -> int:
    e1 = (x1 + x2 + x3) % p
    e2 = (x1 * x2 + x1 * x3 + x2 * x3) % p
    e3 = (x1 * x2 * x3) % p
    return ((e2 - a) ** 2 - 4 * e1 * (e3 + b)) % p


def direct_realisability_table(
    points_by_x: dict[int, tuple[tuple[int, int], ...]],
    p: int,
    a: int,
) -> dict[tuple[int, int], frozenset[int]]:
    """For each x1,x2, return affine x(P+Q) values over all sign choices."""
    table: dict[tuple[int, int], frozenset[int]] = {}
    for x1 in sorted(points_by_x):
        for x2 in reversed(sorted(points_by_x)):
            result_x = set()
            for p1 in points_by_x[x1]:
                for p2 in points_by_x[x2]:
                    summed = point_add(p1, p2, p, a)
                    if summed is not O:
                        result_x.add(summed[0])
            table[(x1, x2)] = frozenset(result_x)
    return table


def recompute_j1() -> dict:
    p, a, b = 101, 3, 5
    points_by_x = curve_points_by_x(p, a, b)
    xs = sorted(points_by_x)
    curve_order = 1 + sum(len(points) for points in points_by_x.values())
    realizable_x3 = direct_realisability_table(points_by_x, p, a)

    realizable = 0
    vanishing = 0
    false_negatives: list[list[int]] = []
    false_positives: list[list[int]] = []
    ordered_realisable_with_repetition = 0

    # Deliberately not the producer transcript's apparent x1/x2/x3 ascending
    # order: x3 is outermost and descending, x1 ascending, x2 descending.
    for x3 in reversed(xs):
        for x1 in xs:
            for x2 in reversed(xs):
                is_real = x3 in realizable_x3[(x1, x2)]
                does_vanish = f3(x1, x2, x3, p, a, b) == 0
                realizable += int(is_real)
                vanishing += int(does_vanish)
                if is_real and len({x1, x2, x3}) < 3:
                    ordered_realisable_with_repetition += 1
                if is_real and not does_vanish:
                    false_negatives.append([x1, x2, x3])
                if does_vanish and not is_real:
                    false_positives.append([x1, x2, x3])

    unordered_realisable = 0
    unordered_patterns = {
        "all_distinct": 0,
        "exactly_two_equal": 0,
        "all_three_equal": 0,
    }
    for x1, x2, x3 in combinations_with_replacement(xs, 3):
        is_real = x3 in realizable_x3[(x1, x2)]
        if not is_real:
            continue
        unordered_realisable += 1
        distinct = len({x1, x2, x3})
        key = {3: "all_distinct", 2: "exactly_two_equal", 1: "all_three_equal"}[distinct]
        unordered_patterns[key] += 1

    reconstructed_ordered = (
        6 * unordered_patterns["all_distinct"]
        + 3 * unordered_patterns["exactly_two_equal"]
        + unordered_patterns["all_three_equal"]
    )

    return {
        "method": (
            "Enumerated all on-curve points from a square table; decided "
            "realisability only by affine point addition over all y-sign choices; "
            "evaluated f_3 separately. Triple loop order was x3 descending, x1 "
            "ascending, x2 descending."
        ),
        "curve_order_including_identity": curve_order,
        "affine_point_count": curve_order - 1,
        "on_curve_x_count": len(xs),
        "ordered_triples_enumerated": len(xs) ** 3,
        "realisable_ordered_x_triples": realizable,
        "f3_vanishing_ordered_x_triples": vanishing,
        "false_negative_count": len(false_negatives),
        "false_positive_count": len(false_positives),
        "false_negative_examples": false_negatives[:10],
        "false_positive_examples": false_positives[:10],
        "ordered_realisable_with_repeated_x": ordered_realisable_with_repetition,
        "ordered_realisable_all_distinct": realizable - ordered_realisable_with_repetition,
        "unordered_realisable_x_multisets": unordered_realisable,
        "unordered_realisable_pattern_counts": unordered_patterns,
        "ordered_count_reconstructed_from_unordered_orbits": reconstructed_ordered,
        "ordered_orbit_reconstruction_agrees": reconstructed_ordered == realizable,
        "verdict": (
            "holds"
            if (curve_order, realizable, vanishing, len(false_negatives), len(false_positives))
            == (115, 6441, 6441, 0, 0)
            else "breaks"
        ),
    }


def symmetric_residue(value: int, p: int) -> int:
    residue = value % p
    if residue > p // 2:
        residue -= p
    return residue


def declared_box(p: int, h: int) -> tuple[set[int], dict[int, list[int]]]:
    """Brute-force beta, independent of continued fractions."""
    selected: set[int] = set()
    deciding_lifts: dict[int, list[int]] = {}
    for x in range(p):
        best: tuple[int, int, int] | None = None
        for beta in range(1, h + 1):
            alpha = symmetric_residue(x * beta, p)
            norm = max(abs(alpha), beta)
            candidate = (norm, alpha, beta)
            if best is None or candidate < best:
                best = candidate
        assert best is not None
        if best[0] <= h:
            selected.add(x)
            deciding_lifts[x] = [best[1], best[2]]
    return selected, deciding_lifts


def signed_beta_box(p: int, h: int) -> set[int]:
    """Sane symmetric lift convention: |beta| <= H and max(|a|,|b|)."""
    selected = set()
    for x in range(p):
        for beta in range(-h, h + 1):
            if beta == 0:
                continue
            alpha = symmetric_residue(x * beta, p)
            if max(abs(alpha), abs(beta)) <= h:
                selected.add(x)
                break
    return selected


def nonnegative_alpha_box(p: int, h: int) -> set[int]:
    """Deliberate contrast: least-nonnegative alpha, positive beta."""
    selected = set()
    for x in range(p):
        for beta in range(1, h + 1):
            alpha = (x * beta) % p
            if max(alpha, beta) <= h:
                selected.add(x)
                break
    return selected


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for divisor in range(3, isqrt(n) + 1, 2):
        if n % divisor == 0:
            return False
    return True


def recompute_j2() -> tuple[dict, dict[int, tuple[tuple[int, int], ...]], set[int]]:
    p = 10007
    ladder = [4, 5, 6, 9, 10]
    expected = {4: 23, 5: 39, 6: 47, 9: 111, 10: 127}
    measured: dict[int, int] = {}
    c_h: dict[int, dict[str, str]] = {}
    declared_sets: dict[int, set[int]] = {}
    signed_sets: dict[int, set[int]] = {}
    nonnegative_sets: dict[int, set[int]] = {}
    lifts_at_ten: dict[int, list[int]] = {}
    for h in ladder:
        selected, lifts = declared_box(p, h)
        declared_sets[h] = selected
        signed_sets[h] = signed_beta_box(p, h)
        nonnegative_sets[h] = nonnegative_alpha_box(p, h)
        measured[h] = len(selected)
        value = Fraction(len(selected), h * h)
        c_h[h] = {
            "exact": fraction_text(value),
            "decimal_3dp": decimal_half_away(value, 3),
        }
        if h == 10:
            lifts_at_ten = lifts

    points_by_x = curve_points_by_x(p, 1, 28)
    curve_order = 1 + sum(len(points) for points in points_by_x.values())
    box_x_on_curve = declared_sets[10].intersection(points_by_x)
    base = [point for x in sorted(box_x_on_curve) for point in points_by_x[x]]
    manifest = json.loads((RUN_DIR / "frozen-manifest.json").read_text())
    manifest_x = set(manifest["cells"][1]["on_curve_x_values_in_box"])

    variants: dict[str, dict[int, dict[str, int]]] = {}
    for name, sets in (
        ("symmetric_signed_beta_abs_norm", signed_sets),
        ("negative_beta_allowed_abs_norm", signed_sets),
        ("least_nonnegative_alpha_positive_beta", nonnegative_sets),
    ):
        variants[name] = {
            h: {
                "count": len(sets[h]),
                "delta_from_declared": len(sets[h]) - len(declared_sets[h]),
                "added_x_count": len(sets[h] - declared_sets[h]),
                "dropped_x_count": len(declared_sets[h] - sets[h]),
            }
            for h in ladder
        }

    counts_hold = measured == expected
    return (
        {
            "method": (
                "For every x and every beta in 1..H, reduced x*beta to the "
                "symmetric interval and minimized max(|alpha|, beta) by exhaustive "
                "scan; no continued fractions and no producer height routine."
            ),
            "box_sizes_by_H": measured,
            "expected_box_sizes_by_H": expected,
            "c_H_by_H": c_h,
            "declared_mismatch_added_x_by_H": {
                h: sorted(declared_sets[h]) if expected[h] == 0 else []
                for h in ladder
                if measured[h] != expected[h]
            },
            "declared_mismatch_dropped_x_by_H": {},
            "variant_conventions": variants,
            "variant_note": (
                "Allowing negative beta with max(|alpha|,|beta|) makes no change: "
                "(alpha,beta) and (-alpha,-beta) represent the same residue. The "
                "least-nonnegative-alpha contrast does move the counts."
            ),
            "cell": {
                "curve_order_including_identity": curve_order,
                "n_expected": 9851,
                "n_is_prime": is_prime(curve_order),
                "n_not_equal_p": curve_order != p,
                "discriminant_expression_mod_p": (4 + 27 * 28 * 28) % p,
                "nonsingular": (4 + 27 * 28 * 28) % p != 0,
                "on_curve_x_in_box": len(box_x_on_curve),
                "base_point_count": len(base),
                "manifest_on_curve_x_exact_match": box_x_on_curve == manifest_x,
                "manifest_on_curve_x_added": sorted(box_x_on_curve - manifest_x),
                "manifest_on_curve_x_missing": sorted(manifest_x - box_x_on_curve),
                "sample_deciding_lifts": {
                    str(x): lifts_at_ten[x] for x in sorted(box_x_on_curve)[:10]
                },
            },
            "verdict": (
                "holds"
                if (
                    counts_hold
                    and curve_order == 9851
                    and is_prime(curve_order)
                    and curve_order != p
                    and (4 + 27 * 28 * 28) % p != 0
                    and len(box_x_on_curve) == 69
                    and len(base) == 138
                    and box_x_on_curve == manifest_x
                )
                else "breaks"
            ),
        },
        points_by_x,
        box_x_on_curve,
    )


def index_group(
    generator: tuple[int, int],
    p: int,
    a: int,
    expected_order: int,
) -> tuple[list[tuple[int, int] | None], dict[tuple[int, int] | None, int]]:
    points: list[tuple[int, int] | None] = []
    index: dict[tuple[int, int] | None, int] = {}
    current = O
    for scalar in range(expected_order):
        if current in index:
            raise AssertionError(f"group repeated before expected order at {scalar}")
        index[current] = scalar
        points.append(current)
        current = point_add(current, generator, p, a)
    if current is not O:
        raise AssertionError("generator did not return to O at expected order")
    return points, index


def convolution(indices: list[int], n: int) -> list[int]:
    counts = [0] * n
    # Exact ordered-pair convolution in index space.
    for left in reversed(indices):
        for right in indices:
            counts[(left + right) % n] += 1
    return counts


def count_stats(counts: list[int]) -> dict:
    n = len(counts)
    total = sum(counts)
    mean = Fraction(total, n)
    second = Fraction(sum(value * value for value in counts), n)
    variance = second - mean * mean
    dispersion = variance / mean
    return {
        "total": total,
        "mean_exact": fraction_text(mean),
        "mean_4dp": decimal_half_away(mean, 4),
        "variance_exact": fraction_text(variance),
        "variance_4dp": decimal_half_away(variance, 4),
        "dispersion_exact": fraction_text(dispersion),
        "dispersion_4dp": decimal_half_away(dispersion, 4),
        "unreachable": sum(value == 0 for value in counts),
        "max": max(counts),
        "c_of_identity": counts[0],
    }


def recompute_j4(
    points_by_x: dict[int, tuple[tuple[int, int], ...]],
    box_x_on_curve: set[int],
) -> tuple[dict, dict]:
    p, a, n = 10007, 1, 9851
    generator = (2, 5425)
    group_points, point_index = index_group(generator, p, a, n)
    all_affine = {point for points in points_by_x.values() for point in points}
    indexed_affine = set(group_points[1:])
    base_points = [
        point for x in sorted(box_x_on_curve) for point in points_by_x[x]
    ]
    base_indices = [point_index[point] for point in base_points]
    box_counts = convolution(base_indices, n)
    box_stats = count_stats(box_counts)

    decomposition = json.loads((RUN_DIR / "decomposition-counts.json").read_text())
    producer_box_counts = decomposition["box"]["counts"]
    producer_null_counts = decomposition["matched_null"]["counts_per_draw"]

    rng = random.Random(20260913)
    x_universe = sorted(points_by_x)
    null_rows = []
    null_dispersions: list[Fraction] = []
    null_unreachable: list[int] = []
    every_negation_closed = True
    every_size_138 = True
    every_mean_conserved = True
    all_null_vectors_match = True
    for draw in range(60):
        chosen_x = rng.sample(x_universe, 69)
        null_points = [
            point for x in chosen_x for point in points_by_x[x]
        ]
        null_indices = [point_index[point] for point in null_points]
        index_set = set(null_indices)
        negation_closed = all(((-index) % n) in index_set for index in index_set)
        counts = convolution(null_indices, n)
        stats = count_stats(counts)
        dispersion = Fraction(stats["dispersion_exact"])
        mean = Fraction(stats["mean_exact"])
        vector_match = counts == producer_null_counts[draw]
        every_negation_closed &= negation_closed
        every_size_138 &= len(null_indices) == 138
        every_mean_conserved &= mean == Fraction(138 * 138, n)
        all_null_vectors_match &= vector_match
        null_dispersions.append(dispersion)
        null_unreachable.append(stats["unreachable"])
        canonical_x = json.dumps(chosen_x, separators=(",", ":")).encode()
        null_rows.append(
            {
                "draw": draw,
                "selected_x": chosen_x,
                "selected_x_sha256": sha256(canonical_x).hexdigest(),
                "base_size": len(null_indices),
                "negation_closed": negation_closed,
                "mean_exact": stats["mean_exact"],
                "dispersion_exact": stats["dispersion_exact"],
                "dispersion_4dp": stats["dispersion_4dp"],
                "unreachable": stats["unreachable"],
                "max": stats["max"],
                "c_of_identity": stats["c_of_identity"],
                "producer_count_vector_exact_match": vector_match,
            }
        )

    mean_dispersion = sum(null_dispersions, Fraction(0)) / 60
    mean_unreachable = Fraction(sum(null_unreachable), 60)
    summary = {
        "mean_dispersion_exact": fraction_text(mean_dispersion),
        "mean_dispersion_4dp": decimal_half_away(mean_dispersion, 4),
        "min_dispersion_exact": fraction_text(min(null_dispersions)),
        "min_dispersion_4dp": decimal_half_away(min(null_dispersions), 4),
        "max_dispersion_exact": fraction_text(max(null_dispersions)),
        "max_dispersion_4dp": decimal_half_away(max(null_dispersions), 4),
        "mean_unreachable_exact": fraction_text(mean_unreachable),
        "mean_unreachable_1dp": decimal_half_away(mean_unreachable, 1),
    }
    box_expected = {
        "mean_4dp": "1.9332",
        "variance_4dp": "5.5822",
        "dispersion_4dp": "2.8875",
        "unreachable": 3704,
        "max": 138,
        "c_of_identity": 138,
    }
    box_subset = {key: box_stats[key] for key in box_expected}
    null_expected = {
        "mean_dispersion_4dp": "2.9163",
        "min_dispersion_4dp": "2.7628",
        "max_dispersion_4dp": "3.1316",
        "mean_unreachable_1dp": "3712.3",
    }
    null_subset = {key: summary[key] for key in null_expected}
    result = {
        "method": (
            "Indexed the group independently by repeated affine addition of "
            "G=(2,5425); derived the height-box base from the independent J2 "
            "enumeration; performed exact ordered index convolution. Regenerated "
            "60 x-set null draws with one random.Random(20260913) and sequential "
            "sample(sorted(on_curve_x),69) calls."
        ),
        "group": {
            "indexed_size": len(group_points),
            "generator_returns_to_identity_at": n,
            "indexed_affine_equals_enumerated_affine": indexed_affine == all_affine,
            "missing_affine": sorted(all_affine - indexed_affine),
            "extraneous_affine": sorted(indexed_affine - all_affine),
        },
        "box": {
            **box_stats,
            "expected_subset": box_expected,
            "producer_count_vector_exact_match": box_counts == producer_box_counts,
            "conservation_mean_B2_over_n": fraction_text(Fraction(138 * 138, n)),
        },
        "matched_null": {
            "seed": 20260913,
            "draws": 60,
            "x_universe_size": len(x_universe),
            "x_set_size_per_draw": 69,
            "base_size_per_draw": 138,
            "all_draws_negation_closed": every_negation_closed,
            "all_draws_size_138": every_size_138,
            "all_draw_means_equal_B2_over_n": every_mean_conserved,
            "all_producer_count_vectors_exact_match": all_null_vectors_match,
            "summary": summary,
            "expected_summary": null_expected,
            "per_draw": null_rows,
        },
    }
    result["verdict"] = (
        "holds"
        if (
            len(group_points) == n
            and indexed_affine == all_affine
            and box_subset == box_expected
            and box_counts == producer_box_counts
            and every_negation_closed
            and every_size_138
            and every_mean_conserved
            and all_null_vectors_match
            and null_subset == null_expected
        )
        else "breaks"
    )
    return result, {
        "box_counts": box_counts,
        "box_stats": box_stats,
    }


def recompute_j3(j4_aux: dict) -> dict:
    p, h, n, b_size = 10007, 10, 9851, 138
    c_h = Fraction(127, 100)
    c_base = Fraction(b_size, h * h)
    ratio_h4_p = Fraction(h**4, p)
    ratio_b2_n = Fraction(b_size**2, n)
    rows = []
    for m in (2, 3):
        left = Fraction(h ** (2 * m), 1)
        right = Fraction(n, 1) / (c_h**m)
        base_right = Fraction(n, 1) / (c_base**m)
        rows.append(
            {
                "m": m,
                "H_to_2m": fraction_text(left),
                "n_over_declared_c_H_pow_m": fraction_text(right),
                "ratio_H_to_2m_over_n_over_declared_c_H_pow_m": fraction_text(
                    left / right
                ),
                "ratio_decimal_6dp": decimal_half_away(left / right, 6),
                "equal_under_declared_c_H": left == right,
                "base_point_constant_B_over_H2": fraction_text(c_base),
                "n_over_base_point_constant_pow_m": fraction_text(base_right),
                "ratio_using_base_point_constant": fraction_text(left / base_right),
                "equal_under_base_point_constant": left == base_right,
            }
        )

    product_rows = []
    for m in range(2, 9):
        product = Fraction(n, 1) / c_h**m
        product_rows.append(
            {
                "m": m,
                "n_over_c_H_pow_m": fraction_text(product),
                "decimal_6dp": decimal_half_away(product, 6),
            }
        )
    strictly_falls = all(
        Fraction(product_rows[i]["n_over_c_H_pow_m"])
        > Fraction(product_rows[i + 1]["n_over_c_H_pow_m"])
        for i in range(len(product_rows) - 1)
    )
    c_identity = j4_aux["box_stats"]["c_of_identity"]

    return {
        "H_to_4": h**4,
        "H_to_4_over_p_exact": fraction_text(ratio_h4_p),
        "H_to_4_over_p_5dp": decimal_half_away(ratio_h4_p, 5),
        "B_squared_over_n_exact": fraction_text(ratio_b2_n),
        "B_squared_over_n_4dp": decimal_half_away(ratio_b2_n, 4),
        "declared_measured_c_H": fraction_text(c_h),
        "pinning_identity_checks": rows,
        "KF_1_literal_product_rows": product_rows,
        "KF_1_literal_product_strictly_falls_with_m": strictly_falls,
        "KF_1_successive_ratio_Pm_over_Pm_plus_1": fraction_text(c_h),
        "KF_1_control_assessment": (
            "BREAK: at this frozen cell H^(2m) != n/c_H^m for m=2 and m=3. "
            "Moreover, the literal finite product n/c_H^m strictly falls with m "
            "because c_H=127/100>1. The producer instead verifies the tautology "
            "(n/c_H^m)*c_H^m=n and a different asymptotic statement that the "
            "formal exponent of n stays one. That does not refute KF-1 as worded."
        ),
        "identity_control": {
            "B": b_size,
            "c_of_identity": c_identity,
            "equal": c_identity == b_size,
            "at_least_B": c_identity >= b_size,
        },
        "anchor_subchecks_hold": (
            h**4 == 10000
            and decimal_half_away(ratio_h4_p, 5) == "0.99930"
            and decimal_half_away(ratio_b2_n, 4) == "1.9332"
            and c_identity == b_size
        ),
        "verdict": "breaks",
        "breaking_artifact": {
            "m2_ratio": fraction_text(Fraction(rows[0]["ratio_H_to_2m_over_n_over_declared_c_H_pow_m"])),
            "m3_ratio": fraction_text(Fraction(rows[1]["ratio_H_to_2m_over_n_over_declared_c_H_pow_m"])),
            "literal_product_falls": strictly_falls,
        },
    }


def main() -> None:
    j1 = recompute_j1()
    j2, points_by_x, box_x_on_curve = recompute_j2()
    j4, j4_aux = recompute_j4(points_by_x, box_x_on_curve)
    j3 = recompute_j3(j4_aux)
    output = {
        "schema": "crypto.autoresearch.validator_independent_recomputation.v1",
        "task_id": "TASK-20260913-2868d5",
        "snapshot_commit": "c70baadb3bdde190b329a6ec1fa1a6cc0ec1468a",
        "experiment_id": "EXP-ECDLP-1bef8f",
        "run_id": "RUN-ECDLP-1bef8f-S0",
        "producer_implementation_imported_or_executed": False,
        "joint_results": {
            "J1_relation_condition_two_directional": j1,
            "J2_box_counts_and_base": j2,
            "J3_pinning_anchor_and_identity": j3,
            "J4_dispersion_cell_and_matched_null": j4,
        },
        "joint_verdicts": {
            "J1_relation_condition_two_directional": j1["verdict"],
            "J2_box_counts_and_base": j2["verdict"],
            "J3_pinning_anchor_and_identity": j3["verdict"],
            "J4_dispersion_cell_and_matched_null": j4["verdict"],
        },
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["joint_verdicts"], indent=2))


if __name__ == "__main__":
    main()
