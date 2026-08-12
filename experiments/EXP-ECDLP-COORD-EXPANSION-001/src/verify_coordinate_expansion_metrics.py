#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
BASE_VERIFIER_PATH = SCRIPT_PATH.with_name("verify_coordinate_expansion.py")


def load_base_verifier() -> Any:
    spec = importlib.util.spec_from_file_location(
        "coordinate_expansion_base_verifier", BASE_VERIFIER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base_verifier()


def positive_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for suffix in positive_compositions(total - first, parts - 1):
            yield (first,) + suffix


def signed_counter(
    oriented_scalars: list[int], q: int, depth: int
) -> Counter[int]:
    counter: Counter[int] = Counter()
    if depth % 2 == 0:
        counter[0] += 1
    for l1_norm in range(depth % 2 or 2, depth + 1, 2):
        for support_size in range(
            1, min(len(oriented_scalars), l1_norm) + 1
        ):
            for support in itertools.combinations(
                range(len(oriented_scalars)), support_size
            ):
                for magnitudes in positive_compositions(
                    l1_norm, support_size
                ):
                    for signs in itertools.product(
                        (-1, 1), repeat=support_size
                    ):
                        total = sum(
                            signs[index]
                            * magnitudes[index]
                            * oriented_scalars[support[index]]
                            for index in range(support_size)
                        )
                        counter[total % q] += 1
    return counter


def canonical_counter(
    scalars: list[int], q: int, depth: int, symmetry: str
) -> Counter[int]:
    if symmetry == "sign_canonical":
        return Counter(
            sum(scalars[index] for index in indices) % q
            for indices in itertools.combinations_with_replacement(
                range(len(scalars)), depth
            )
        )
    if len(scalars) % 2:
        raise AssertionError("odd sign-complete scalar count")
    assert all(
        (scalars[index] + scalars[index + 1]) % q == 0
        for index in range(0, len(scalars), 2)
    )
    return signed_counter(scalars[::2], q, depth)


def ordered_counter(
    scalars: list[int], q: int, previous: Counter[int]
) -> Counter[int]:
    result: Counter[int] = Counter()
    for partial, multiplicity in previous.items():
        for scalar in scalars:
            result[(partial + scalar) % q] += multiplicity
    return result


def verify_metrics(raw_path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    assert BASE.sha256_file(BASE_VERIFIER_PATH) == manifest[
        "independent_verifier_sha256"
    ]
    assert BASE.sha256_file(raw_path) == manifest["raw_result_sha256"]
    base_receipt_path = manifest_path.with_name("verifier-receipt.json")
    assert BASE.sha256_file(base_receipt_path) == manifest[
        "verifier_receipt_sha256"
    ]
    base_receipt = json.loads(base_receipt_path.read_text())
    assert base_receipt["valid"] is True
    assert base_receipt["raw_result_sha256"] == manifest[
        "raw_result_sha256"
    ]
    assert base_receipt["source_sha256"] == manifest["source_sha256"]
    assert base_receipt["configurations_verified"] == 582
    result = json.loads(raw_path.read_text())
    records_verified = 0
    profiles_verified = 0
    for instance in result["instances"]:
        q = instance["curve"]["q"]
        for record in instance["configurations"]:
            scalars = record["factor_base_scalars_diagnostic"]
            ordered = Counter({0: 1})
            for depth, profile in enumerate(
                record["audit"]["profiles"], 1
            ):
                ordered = ordered_counter(scalars, q, ordered)
                canonical = canonical_counter(
                    scalars, q, depth, record["symmetry_mode"]
                )
                assert set(ordered) == set(canonical)
                assert profile["support_size"] == len(canonical)
                assert profile["canonical_formal_class_total"] == sum(
                    canonical.values()
                )
                assert profile["canonical_formal_defect"] == (
                    sum(canonical.values()) - len(canonical)
                )
                assert profile["canonical_collision_energy"] == sum(
                    value * value for value in canonical.values()
                )
                assert profile["canonical_maximum_multiplicity"] == max(
                    canonical.values()
                )
                assert profile["ordered_representation_total"] == sum(
                    ordered.values()
                )
                assert profile["ordered_collision_energy"] == sum(
                    value * value for value in ordered.values()
                )
                assert profile["ordered_maximum_multiplicity"] == max(
                    ordered.values()
                )
                profiles_verified += 1
            records_verified += 1
    assert records_verified == 582
    assert profiles_verified == 2910
    return {
        **base_receipt,
        "expanded_metric_verification": True,
        "canonical_records_verified": records_verified,
        "canonical_profiles_verified": profiles_verified,
        "base_verifier_sha256": manifest["independent_verifier_sha256"],
        "breakthrough_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            verify_metrics(args.raw_result, args.manifest),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
