#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def add_shape(left: list[int], right: list[int]) -> list[int]:
    if len(left) != len(right) or left[0] != 1 or left[-1] != 1 or right[0] != 1 or right[-1] != 1:
        raise ValueError("incompatible TT shapes")
    return [1, *(a + b for a, b in zip(left[1:-1], right[1:-1])), 1]


def multiply_shape(left: list[int], right: list[int]) -> list[int]:
    if len(left) != len(right) or left[0] != 1 or left[-1] != 1 or right[0] != 1 or right[-1] != 1:
        raise ValueError("incompatible TT shapes")
    return [1, *(a * b for a, b in zip(left[1:-1], right[1:-1])), 1]


def scalar_shape(shape: list[int]) -> list[int]:
    return list(shape)


def rcb_shape(left: tuple[list[int], list[int], list[int]], right: tuple[list[int], list[int], list[int]], counters: dict[str, int]) -> tuple[list[int], list[int], list[int]]:
    x1, y1, z1 = left
    x2, y2, z2 = right

    def add(left_shape: list[int], right_shape: list[int]) -> list[int]:
        counters["tt_additions"] += 1
        return add_shape(left_shape, right_shape)

    def mul(left_shape: list[int], right_shape: list[int]) -> list[int]:
        counters["tt_multiplications"] += 1
        return multiply_shape(left_shape, right_shape)

    t0 = mul(x1, x2)
    t1 = mul(y1, y2)
    t2 = mul(z1, z2)
    t3 = mul(add(x1, y1), add(x2, y2))
    t3 = add(t3, t0)
    t3 = add(t3, t1)
    t4 = mul(add(x1, z1), add(x2, z2))
    t4 = add(t4, t0)
    t4 = add(t4, t2)
    t5 = mul(add(y1, z1), add(y2, z2))
    t5 = add(t5, t1)
    t5 = add(t5, t2)
    z3 = add(t4, t2)
    x3 = add(t1, z3)
    z3 = add(t1, z3)
    y3 = mul(x3, z3)
    t1 = add(t0, t0)
    t1 = add(t1, t0)
    t2 = scalar_shape(t2)
    t4 = scalar_shape(t4)
    t1 = add(t1, t2)
    t2 = add(t0, t2)
    t2 = scalar_shape(t2)
    t4 = add(t4, t2)
    t0 = mul(t1, t4)
    y3 = add(y3, t0)
    t0 = mul(t5, t4)
    x3 = add(mul(t3, x3), t0)
    t0 = mul(t3, t1)
    z3 = add(mul(t5, z3), t0)
    return x3, y3, z3


def variable_shapes(mode: int) -> tuple[list[int], list[int], list[int]]:
    shape = [1, 1, 1, 1, 1, 1]
    return [list(shape), list(shape), list(shape)]


def raw_core_entries(shape: list[int], b_size: int) -> int:
    return b_size * sum(left * right for left, right in zip(shape[:-1], shape[1:]))


def norm_shape(source: tuple[list[int], list[int], list[int]], counters: dict[str, int]) -> tuple[list[int], list[int], list[int], list[int]]:
    x, y, z = source
    def add(left: list[int], right: list[int]) -> list[int]:
        counters["tt_additions"] += 1
        return add_shape(left, right)
    def mul(left: list[int], right: list[int]) -> list[int]:
        counters["tt_multiplications"] += 1
        return multiply_shape(left, right)
    ex = add(x, z)
    ey = add(y, z)
    return (*source, add(mul(ex, ex), mul(ey, ey)))


def run_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    b_size = len(family["factor_base"]["points"])
    counters = {"tt_additions": 0, "tt_multiplications": 0}
    source = variable_shapes(0)
    stages = []
    for mode in range(1, 5):
        source = rcb_shape(source, variable_shapes(mode), counters)
        stages.append({
            "stage": mode + 1,
            "bond_ranks": source[0],
            "max_bond": max(source[0]),
            "raw_core_entries": sum(raw_core_entries(component, b_size) for component in source),
        })
    _, _, _, norm = norm_shape(source, counters)
    norm_record = {
        "bond_ranks": norm,
        "max_bond": max(norm),
        "raw_core_entries": raw_core_entries(norm, b_size),
    }
    sqrt_q = curve["q"] ** 0.5
    return {
        "curve_id": curve["id"],
        "q": curve["q"],
        "family": family["family"],
        "b_size": b_size,
        "stages": stages,
        "norm": norm_record,
        "counters": dict(counters),
        "ratios": {
            "norm_max_bond_over_b": norm_record["max_bond"] / max(1, b_size),
            "norm_core_entries_over_b5": norm_record["raw_core_entries"] / max(1, b_size**5),
            "norm_core_entries_over_sqrt_q": norm_record["raw_core_entries"] / max(1.0, sqrt_q),
        },
        "non_enumerative_source_path": True,
    }


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    raw_entries = [row["norm"]["raw_core_entries"] for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-raw-circuit-tt-preflight-v1",
        "claim_status": ["HYPOTHESIS", "OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)},
        "config": {"input_result": str(input_path.resolve()), "families": families, "mode_order": ["A", "R0", "R1", "R2", "R3"], "closure": ["direct_sum_addition", "kronecker_pointwise_multiplication"], "source_tuple_enumeration": False},
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "min_norm_core_entries": min(raw_entries),
            "max_norm_core_entries": max(raw_entries),
            "all_non_enumerative": all(row["non_enumerative_source_path"] for row in rows),
            "raw_closure_advice_gate": False,
            "breakthrough_claim": False,
            "boundary": "Raw direct-sum/Kronecker circuit-TT preflight only; no minimal-rank claim and no generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
