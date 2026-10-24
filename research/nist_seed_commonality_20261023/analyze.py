#!/usr/bin/env python3
"""Bounded, retrospective feature comparison specified in PROTOCOL.md."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016"
INPUTS = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
SMALL_INDICATORS = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
FEATURES = (
    "has_small_square_prime",
    "number_small_square_primes",
    "minimum_small_square_prime",
    "small_conductor_log2",
    "maximum_small_discriminant_valuation",
    *(f"conductor_divisible_by_{ell}" for ell in SMALL_INDICATORS),
    "absolute_normalized_trace",
    "signed_normalized_trace",
    "v2_n_minus_1",
    "v2_n_plus_1",
    "number_small_twist_primes",
    "b_bit_weight",
)


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p :: p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [p for p in range(3, limit + 1, 2) if sieve[p]]


def v2(n: int) -> int:
    assert n > 0
    return (n & -n).bit_length() - 1


def parse_hex(value: str) -> int:
    return int(value, 0)


def source_data() -> tuple[list[dict], dict[str, str]]:
    inputs = {}
    for name, digest in INPUTS.items():
        raw = (SOURCE / name).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != digest:
            raise ValueError(f"{name}: expected {digest}, got {actual}")
        inputs[name] = json.loads(raw)
    assessed = inputs["assessed.json"]["candidate_rows"]
    controls = inputs["traits.json"]["published_controls"]
    if len(assessed) != 11 or len(controls) != 10:
        raise ValueError("The expected 11 plus 10 seed-level classes are absent")
    rows = []
    for item in assessed:
        rows.append(row(item, "skipped", None))
    for name, item in controls.items():
        rows.append(row(item, "published", name))
    rows.sort(key=lambda x: (x["field_bits"], x["ordinal"], x["label"]))
    if len({r["curve_uid"] for r in rows}) != 21:
        raise ValueError("Duplicate EC1 identity")
    return rows, INPUTS


def row(item: dict, label: str, name: str | None) -> dict:
    p = parse_hex(item["p_hex"])
    n = parse_hex(item["n_hex"])
    t = parse_hex(item["trace_hex_signed"])
    delta = parse_hex(item["delta_pi_hex_signed"])
    twist = parse_hex(item["twist_order_hex"])
    b = parse_hex(item["b_hex"])
    c = parse_hex(item["ansi_c_hex"])
    if t != p + 1 - n or delta != t * t - 4 * p or twist != p + 1 + t:
        raise ValueError(f"Arithmetic mismatch at ordinal {item['seed_ordinal_one_based']}")
    if (c * b * b + 27) % p:
        raise ValueError(f"Seed coefficient relation mismatch at {item['seed_ordinal_one_based']}")
    if n % 2 != 1 or delta % 2 != 1:
        raise ValueError("Expected odd prime-order class and odd discriminant")

    remaining = abs(delta)
    valuations = []
    for ell in primes_through(10_000):
        if remaining % ell:
            continue
        exponent = 0
        while remaining % ell == 0:
            remaining //= ell
            exponent += 1
        if exponent:
            valuations.append([ell, exponent])
    square_primes = [[ell, exponent // 2] for ell, exponent in valuations if exponent >= 2]
    local_conductor = {ell: exponent for ell, exponent in square_primes}
    twist_factors = item["twist_small_factors_to_10000"]
    for ell, exponent in twist_factors:
        if twist % (int(ell) ** int(exponent)):
            raise ValueError("Archived twist factor is invalid")

    b_weight = b.bit_count()
    if p.bit_length() == 224:
        b_weight = min(b_weight, (p - b).bit_count())
    signed_normalized_trace = t / (2 * math.sqrt(p))
    features = {
        "has_small_square_prime": int(bool(square_primes)),
        "number_small_square_primes": len(square_primes),
        "minimum_small_square_prime": square_primes[0][0] if square_primes else 10_001,
        "small_conductor_log2": sum(v * math.log2(ell) for ell, v in square_primes),
        "maximum_small_discriminant_valuation": max((v for _, v in valuations), default=0),
        **{f"conductor_divisible_by_{ell}": int(ell in local_conductor) for ell in SMALL_INDICATORS},
        "absolute_normalized_trace": abs(signed_normalized_trace),
        "signed_normalized_trace": signed_normalized_trace,
        "v2_n_minus_1": v2(n - 1),
        "v2_n_plus_1": v2(n + 1),
        "number_small_twist_primes": len(twist_factors),
        "b_bit_weight": b_weight,
    }
    assert tuple(features) == FEATURES
    return {
        "label": label,
        "name": name or f"skip-{p.bit_length()}-{item['seed_ordinal_one_based']}",
        "field_bits": p.bit_length(),
        "field_hex": hex(p),
        "ordinal": item["seed_ordinal_one_based"],
        "seed_hex": item["seed_hex"],
        "curve_uid": item["identity"]["curve_uid"],
        "delta_small_factor_valuations": valuations,
        "delta_small_square_primes_with_local_conductor_valuation": square_primes,
        "delta_unfactored_after_trial_division_hex": hex(remaining),
        "features": features,
    }


def doubled_pair_score(rows: list[dict], assignments: tuple[tuple[int, ...], ...], feature: str,
                       groups: list[tuple[int, ...]]) -> int:
    total = 0
    for indices, chosen in zip(groups, assignments):
        published = set(chosen)
        for pi in published:
            for si in indices:
                if si in published:
                    continue
                a = rows[pi]["features"][feature]
                b = rows[si]["features"][feature]
                total += 2 if a < b else (1 if a == b else 0)
    return total


def compare(rows: list[dict]) -> dict:
    by_field: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        by_field.setdefault(r["field_hex"], []).append(i)
    groups = [tuple(v) for v in by_field.values()
              if any(rows[i]["label"] == "published" for i in v)
              and any(rows[i]["label"] == "skipped" for i in v)]
    groups.sort(key=lambda g: rows[g[0]]["field_bits"])
    choices = [list(itertools.combinations(g, sum(rows[i]["label"] == "published" for i in g)))
               for g in groups]
    allocations = list(itertools.product(*choices))
    if len(allocations) != 4480:
        raise ValueError(f"Expected 4480 allocations, got {len(allocations)}")
    observed = tuple(tuple(i for i in g if rows[i]["label"] == "published") for g in groups)
    scores = {f: [doubled_pair_score(rows, a, f, groups) for a in allocations] for f in FEATURES}
    observations = {f: doubled_pair_score(rows, observed, f, groups) for f in FEATURES}
    center = 25  # 25 pairs, doubled; 1/2 per pair under the allocation symmetry.
    feature_results = []
    p_by_score: dict[str, dict[int, int]] = {}
    for f in FEATURES:
        values = scores[f]
        tails = {score: sum(abs(other - center) >= abs(score - center) for other in values)
                 for score in set(values)}
        p_by_score[f] = tails
        observed_score = observations[f]
        pub = [r["features"][f] for r in rows if r["label"] == "published"]
        skip = [r["features"][f] for r in rows if r["label"] == "skipped"]
        global_split = max(pub) < min(skip) or max(skip) < min(pub)
        feature_results.append({
            "feature": f,
            "published_lower_pair_score_doubled": observed_score,
            "pairs": 25,
            "exact_two_sided_tail_numerator": tails[observed_score],
            "exact_two_sided_tail_denominator": len(allocations),
            "perfect_within_field_order": observed_score in (0, 50),
            "perfect_global_threshold": global_split,
            "published_values": pub,
            "skipped_values": skip,
        })
    best_num = min(x["exact_two_sided_tail_numerator"] for x in feature_results)
    family_num = sum(min(p_by_score[f][scores[f][i]] for f in FEATURES) <= best_num
                     for i in range(len(allocations)))
    return {
        "within_field_groups": [
            {"field_bits": rows[g[0]]["field_bits"],
             "published": sum(rows[i]["label"] == "published" for i in g),
             "skipped": sum(rows[i]["label"] == "skipped" for i in g)}
            for g in groups
        ],
        "allocation_count": len(allocations),
        "best_unadjusted_tail_numerator": best_num,
        "familywise_tail_numerator": family_num,
        "tail_denominator": len(allocations),
        "features": feature_results,
    }


def main() -> None:
    rows, digests = source_data()
    result = {
        "schema": "nist-seed-commonality/v1",
        "protocol": "PROTOCOL.md",
        "input_sha256": digests,
        "scope": "21 reported seed-level classes; 19 within-field comparison rows",
        "rows": rows,
        "comparison": compare(rows),
    }
    output = HERE / "analysis.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {output}; {len(rows)} rows, {result['comparison']['allocation_count']} allocations")
    for item in sorted(result["comparison"]["features"],
                       key=lambda x: (x["exact_two_sided_tail_numerator"], x["feature"]))[:5]:
        print(item["feature"], item["published_lower_pair_score_doubled"],
              item["exact_two_sided_tail_numerator"])
    print("familywise", result["comparison"]["familywise_tail_numerator"])


if __name__ == "__main__":
    main()
