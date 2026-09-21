#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
BASE_SOURCE = SCRIPT_PATH.with_name("elliptic_net_block_zero.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module("elliptic_net_block_zero_v2_base", BASE_SOURCE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def normalized_locator_value(
    output: tuple[int, int, int], target: tuple[int, int], p: int, nu: int
) -> int:
    """Evaluate the zero predicate after removing projective scale."""
    affine = BASE.TT.projective_to_affine(output, p)
    if affine is None:
        return 1
    x, y = affine
    xq, yq = target
    return ((x - xq) ** 2 - nu * (y - yq) ** 2) % p


def normalization_controls(source_path: Path) -> dict[str, Any]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    records = []
    for instance in source["instances"]:
        curve_record = instance["curve"]
        family_record = instance["families"][0]
        p = curve_record["p"]
        a = curve_record["a"]
        b = curve_record["b"]
        curve = BASE.TYPED.Curve(p, a, b)
        a_point = BASE.NORM.point_from_json(
            family_record["progression"]["p0"]
        )
        r_points = [
            BASE.NORM.point_from_json(value)
            for value in family_record["factor_base"]["points"][:4]
        ]
        inputs = [
            BASE.NORM.affine_to_projective(a_point),
            *(BASE.NORM.affine_to_projective(point) for point in r_points),
        ]
        target = BASE.NORM.sum_affine([a_point, *r_points], p, a)
        nu = BASE.NORM.nonsquare(p)
        outputs = [
            BASE.TT.sum_five(
                [inputs[0], *permuted], p, a, b
            )
            for permuted in (
                [inputs[index] for index in permutation]
                for permutation in itertools.permutations(range(1, 5))
            )
        ]
        affine_outputs = [
            BASE.TT.projective_to_affine(output, p) for output in outputs
        ]
        base_value = normalized_locator_value(outputs[0], target, p, nu)
        scaled_values = [
            normalized_locator_value(
                tuple((coordinate * scale) % p for coordinate in outputs[0]),
                target,
                p,
                nu,
            )
            for scale in (1, 2, 3, 5)
        ]
        records.append(
            {
                "curve_id": curve_record["id"],
                "permutation_count": len(outputs),
                "affine_permutation_equal": len(set(affine_outputs)) == 1,
                "normalized_permutation_equal": len(
                    {
                        normalized_locator_value(output, target, p, nu)
                        for output in outputs
                    }
                )
                == 1,
                "normalized_rescaling_equal": len(set(scaled_values)) == 1,
                "target_zero": base_value == 0,
                "zero_consistent": all(
                    (normalized_locator_value(output, target, p, nu) == 0)
                    == (BASE.TT.projective_to_affine(output, p) == target)
                    for output in outputs
                ),
                "digest": canonical_digest(
                    {
                        "affine": affine_outputs,
                        "values": scaled_values,
                    }
                ),
            }
        )
    return {
        "records": records,
        "all_pass": all(
            record["affine_permutation_equal"]
            and record["normalized_permutation_equal"]
            and record["normalized_rescaling_equal"]
            and record["zero_consistent"]
            for record in records
        ),
    }


def run(
    result_path: Path,
    families: list[str],
    length_multiplier: int,
) -> dict[str, Any]:
    original_locator = BASE.locator_value
    BASE.locator_value = normalized_locator_value
    try:
        result = BASE.run(result_path, families, length_multiplier)
    finally:
        BASE.locator_value = original_locator
    controls = normalization_controls(result_path)
    result["protocol"] = (
        "EXP-ECDLP-COORD-EXPANSION-001-elliptic-net-block-zero-v2"
    )
    result["claim_status"] = [
        "HYPOTHESIS",
        "TOY-EVIDENCE",
        "MODEL-BOUND",
        "NOVELTY-UNVERIFIED",
    ]
    result["source"] = {
        "wrapper_sha256": sha256_file(SCRIPT_PATH),
        "base_generator_sha256": sha256_file(BASE_SOURCE),
        "typed_s4_norm_rank_sha256": result["source"][
            "typed_s4_norm_rank_sha256"
        ],
        "typed_five_ec_sha256": result["source"]["typed_five_ec_sha256"],
        "tt_norm_rank_sha256": result["source"]["tt_norm_rank_sha256"],
        "input_result_sha256": result["source"]["input_result_sha256"],
    }
    result["config"]["normalization"] = (
        "affine_output_locator_with_infinity_sentinel"
    )
    result["normalization_controls"] = controls
    result["summary"]["normalization_controls_valid"] = controls["all_pass"]
    result["summary"]["constructible_implicit_state"] = False
    result["summary"]["algorithm_promotion_gate"] = False
    result["summary"]["breakthrough_claim"] = False
    result["summary"]["boundary"] = (
        "Affine-normalized locator diagnostic. A recurrence signal would "
        "authorize a separate implicit-state construction experiment; it "
        "would not establish sub-rho relation generation."
    )
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--length-multiplier", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(run(args.result, args.families, args.length_multiplier),
                     sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
