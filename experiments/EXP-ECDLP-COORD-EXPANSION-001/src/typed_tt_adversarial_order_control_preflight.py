#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ADAPTIVE_SOURCE = SCRIPT_PATH.with_name("typed_tt_adaptive_skeleton_preflight.py")


def load_adaptive() -> Any:
    spec = importlib.util.spec_from_file_location("typed_tt_adaptive_for_order_control", ADAPTIVE_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load adaptive producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ADAPTIVE = load_adaptive()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def unrank(value: int, dimensions: list[int]) -> tuple[int, ...]:
    result = [0] * len(dimensions)
    for index in range(len(dimensions) - 1, -1, -1):
        result[index] = value % dimensions[index]
        value //= dimensions[index]
    return tuple(result)


def prefix_order(a_size: int, b_size: int, mode: str) -> list[tuple[int, int, int]]:
    values = [unrank(value, [a_size, b_size, b_size]) for value in range(a_size * b_size * b_size)]
    if mode == "lexicographic":
        return values
    if mode == "reverse_lexicographic":
        return list(reversed(values))
    raise ValueError(f"unknown prefix order: {mode}")


def run(input_path: Path, families: list[str], mode: str) -> dict[str, Any]:
    original = ADAPTIVE.SOURCE_AWARE.prefix_order
    ADAPTIVE.SOURCE_AWARE.prefix_order = lambda a_size, b_size: prefix_order(a_size, b_size, mode)
    try:
        result = ADAPTIVE.run(input_path, families)
    finally:
        ADAPTIVE.SOURCE_AWARE.prefix_order = original
    result["protocol"] = "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-adversarial-order-control-preflight-v1"
    result["source"]["order_control_sha256"] = hashlib.sha256(SCRIPT_PATH.read_bytes()).hexdigest()
    result["config"]["prefix_order"] = mode
    result["config"]["control_boundary"] = "Schedule-only control; no generic ECDLP claim."
    result["summary"]["boundary"] = "Adversarial prefix-order control for adaptive source-prefix skeleton; no generic ECDLP claim."
    result["summary"]["breakthrough_claim"] = False
    result["summary"]["algorithm_promotion_gate"] = False
    result["result_digest"] = digest([{key: value for key, value in row.items() if key != "wall_seconds"} for row in result["rows"]])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--order", choices=("lexicographic", "reverse_lexicographic"), required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families, args.order), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
