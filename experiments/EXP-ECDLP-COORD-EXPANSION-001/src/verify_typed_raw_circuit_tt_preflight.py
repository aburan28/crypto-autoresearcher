#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("typed_raw_circuit_tt_preflight.py")


def load_producer() -> Any:
    spec = importlib.util.spec_from_file_location("raw_tt_for_verification", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load raw TT producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def expected_shape() -> list[int]:
    return [1, 1, 1, 1, 1, 1]


def direct_sum(left: list[int], right: list[int]) -> list[int]:
    return [1, *(a + b for a, b in zip(left[1:-1], right[1:-1])), 1]


def kron(left: list[int], right: list[int]) -> list[int]:
    return [1, *(a * b for a, b in zip(left[1:-1], right[1:-1])), 1]


def rcb_shape(left: tuple[list[int], list[int], list[int]], right: tuple[list[int], list[int], list[int]]) -> tuple[list[int], list[int], list[int]]:
    x1, y1, z1 = left
    x2, y2, z2 = right
    t0 = kron(x1, x2)
    t1 = kron(y1, y2)
    t2 = kron(z1, z2)
    t3 = direct_sum(x1, y1)
    t3 = kron(t3, direct_sum(x2, y2))
    t3 = direct_sum(t3, t0)
    t3 = direct_sum(t3, t1)
    t4 = kron(direct_sum(x1, z1), direct_sum(x2, z2))
    t4 = direct_sum(direct_sum(t4, t0), t2)
    t5 = kron(direct_sum(y1, z1), direct_sum(y2, z2))
    t5 = direct_sum(direct_sum(t5, t1), t2)
    z3 = direct_sum(t4, t2)
    x3 = direct_sum(t1, z3)
    z3 = direct_sum(t1, z3)
    y3 = kron(x3, z3)
    t1 = direct_sum(t0, direct_sum(t0, t0))
    t1 = direct_sum(t1, t2)
    t2 = direct_sum(t0, t2)
    t4 = direct_sum(t4, t2)
    t0 = kron(t1, t4)
    y3 = direct_sum(y3, t0)
    t0 = kron(t5, t4)
    x3 = direct_sum(kron(t3, x3), t0)
    t0 = kron(t3, t1)
    z3 = direct_sum(kron(t5, z3), t0)
    return x3, y3, z3


def norm_shape(source: tuple[list[int], list[int], list[int]]) -> list[int]:
    x, y, z = source
    ex = direct_sum(x, z)
    ey = direct_sum(y, z)
    return direct_sum(kron(ex, ex), kron(ey, ey))[0:]


def core_entries(shape: list[int], b_size: int) -> int:
    return b_size * sum(a * b for a, b in zip(shape[:-1], shape[1:]))


def expected_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    b_size = len(family["factor_base"]["points"])
    source = expected_shape(), expected_shape(), expected_shape()
    stages = []
    for stage in range(2, 6):
        source = rcb_shape(source, (expected_shape(), expected_shape(), expected_shape()))
        stages.append({"stage": stage, "bond_ranks": source[0], "max_bond": max(source[0]), "raw_core_entries": sum(core_entries(component, b_size) for component in source)})
    norm = norm_shape(source)
    return {"curve_id": curve["id"], "q": curve["q"], "family": family["family"], "b_size": b_size, "stages": stages, "norm": {"bond_ranks": norm, "max_bond": max(norm), "raw_core_entries": core_entries(norm, b_size)}}


def check(raw: dict[str, Any], input_path: Path) -> dict[str, bool]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    expected = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in raw["config"]["families"]:
            expected.append(expected_row(instance["curve"], by_family[family_name]))
    actual = [{key: row[key] for key in ("curve_id", "q", "family", "b_size", "stages", "norm")} for row in raw["rows"]]
    return {
        "protocol": raw.get("protocol") == "EXP-ECDLP-COORD-EXPANSION-001-typed-raw-circuit-tt-preflight-v1",
        "input_hash": raw["source"]["input_sha256"] == sha256_file(input_path),
        "config": raw["config"]["source_tuple_enumeration"] is False and raw["config"]["closure"] == ["direct_sum_addition", "kronecker_pointwise_multiplication"],
        "independent_shape_replay": actual == expected,
        "row_count": raw["summary"]["family_rows"] == len(expected),
        "non_enumerative": raw["summary"]["all_non_enumerative"] is True,
        "promotion_false": raw["summary"]["raw_closure_advice_gate"] is False,
        "breakthrough_false": raw["summary"]["breakthrough_claim"] is False,
        "digest": raw["result_digest"] == digest(raw["rows"]),
    }


def mutation_checks(raw: dict[str, Any], input_path: Path, checks: dict[str, bool]) -> dict[str, bool]:
    mutations = []
    changed = copy.deepcopy(raw); changed["rows"][0]["norm"]["max_bond"] += 1; mutations.append(changed)
    changed = copy.deepcopy(raw); changed["config"]["source_tuple_enumeration"] = True; mutations.append(changed)
    changed = copy.deepcopy(raw); changed["summary"]["breakthrough_claim"] = True; mutations.append(changed)
    results = []
    for candidate in mutations:
        results.append(not all(check(candidate, input_path).values()))
    return {"mutations_rejected": all(results), "mutation_count": len(results)}


def verify(raw_path: Path, input_override: Path | None = None) -> dict[str, Any]:
    producer = load_producer()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    input_path = input_override if input_override is not None else Path(raw["config"]["input_result"])
    checks = check(raw, input_path)
    mutations = mutation_checks(raw, input_path, checks)
    checks.update(mutations)
    rerun = producer.run(input_path, raw["config"]["families"])
    rerun_rows = [{key: row[key] for key in ("curve_id", "q", "family", "b_size", "stages", "norm")} for row in rerun["rows"]]
    raw_rows = [{key: row[key] for key in ("curve_id", "q", "family", "b_size", "stages", "norm")} for row in raw["rows"]]
    checks["producer_rerun_exact"] = raw_rows == rerun_rows
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-raw-circuit-tt-preflight-verifier",
        "raw_result_sha256": sha256_file(raw_path),
        "input_result_sha256": sha256_file(input_path),
        "producer_sha256": sha256_file(PRODUCER_PATH),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "checks": checks,
        "rows_replayed": len(rerun["rows"]),
        "valid": all(checks.values()),
        "boundary": "Independent rank-shape replay and mutation checks; raw TT closure only, no generic ECDLP claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    receipt = verify(args.raw_result, args.input)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
