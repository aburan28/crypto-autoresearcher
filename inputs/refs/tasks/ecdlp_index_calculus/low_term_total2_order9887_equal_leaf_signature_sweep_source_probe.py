#!/usr/bin/env python3
"""Emit transfer-local equal-leaf signature sweep rows for P554 pinned pairs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P555_SOURCE = STATE_DIR / "low_term_total2_order9887_p555_pinned_family_source_20544_20554_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p558_equal_leaf_signature_sweep_source_20544_20554_probe.json"
DEFAULT_SELECTORS = "mode_cost_low_term_support_total2,mode_double_pair_first_total2,mode_low_term_support_total2"
DEFAULT_TOP_KS = "4,7,12,16"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip()]


def parse_int_csv(raw: str) -> list[int]:
    return [int(item) for item in parse_csv(raw)]


def parse_leaf_indices(raw: str) -> list[int]:
    raw = str(raw).strip()
    if ":" in raw:
        start, end = raw.split(":", 1)
        return list(range(int(start), int(end) + 1))
    return parse_int_csv(raw)


def desired_family_key(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def load_lanes(source: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for policy in (source.get("policies") or {}).values():
        lane = policy.get("lane")
        if isinstance(lane, dict) and lane.get("lane_id"):
            lanes.append(lane)
    lanes.sort(key=lambda lane: str(lane.get("lane_id")))
    return lanes


def forced_selector(base_selector: str, leaf_index: int) -> str:
    return f"{base_selector}__force_equal_leaf_{leaf_index:02d}"


def make_row(
    lane: dict[str, Any],
    base_selector: str,
    top_k: int,
    leaf_index: int,
) -> dict[str, Any]:
    base_case = dict_value(lane.get("base_case"))
    spec = dict_value(lane.get("source_policy_mutation"))
    row_keys = [str(item) for item in list_value(spec.get("pin_row_keys"))]
    desired = list_value(lane.get("desired_family"))
    row_leaf_keys = [
        {"leaf_indices": [int(leaf_index)], "row_key": row_key}
        for row_key in sorted(row_keys)
    ]
    return {
        "base_selector": base_selector,
        "below_rho": False,
        "desired_family": desired,
        "desired_family_key": desired_family_key(desired),
        "errors": [],
        "forced_equal_leaf_index": int(leaf_index),
        "forced_leaf_signature": [int(leaf_index), int(leaf_index)],
        "forced_leaf_signature_key": f"{leaf_index},{leaf_index}",
        "lane_id": lane.get("lane_id"),
        "ops_over_rho": None,
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "row_keys": row_keys,
        "row_leaf_keys": row_leaf_keys,
        "row_selector": f"{lane.get('lane_id')}_equal_leaf_sweep",
        "row_selector_public_key_verified": None,
        "selected_leaf_count": len(row_leaf_keys),
        "selected_row_count": len(row_keys),
        "selector": forced_selector(base_selector, int(leaf_index)),
        "source_verified": True,
        "target": base_case.get("target"),
        "top_k": int(top_k),
        "transfer_index": int_value(base_case.get("transfer_index")),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_lane: dict[str, list[dict[str, Any]]] = defaultdict(list)
    leaf_counts = Counter()
    top_k_counts = Counter()
    for row in rows:
        by_lane[str(row.get("lane_id"))].append(row)
        leaf_counts[str(row.get("forced_equal_leaf_index"))] += 1
        top_k_counts[str(row.get("top_k"))] += 1
    return {
        "case_count": len(rows),
        "leaf_index_counts": {key: int(value) for key, value in sorted(leaf_counts.items(), key=lambda item: int(item[0]))},
        "lane_counts": {key: len(value) for key, value in sorted(by_lane.items())},
        "top_k_counts": {key: int(value) for key, value in sorted(top_k_counts.items(), key=lambda item: int(item[0]))},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p555-source", type=Path, default=DEFAULT_P555_SOURCE)
    parser.add_argument("--leaf-indices", default="0:16")
    parser.add_argument("--selectors", default=DEFAULT_SELECTORS)
    parser.add_argument("--top-ks", default=DEFAULT_TOP_KS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p555_source = load_json(args.p555_source)
    leaf_indices = parse_leaf_indices(args.leaf_indices)
    selectors = parse_csv(args.selectors)
    top_ks = parse_int_csv(args.top_ks)
    policies: dict[str, dict[str, Any]] = {}
    all_rows: list[dict[str, Any]] = []
    for lane in load_lanes(p555_source):
        rows = [
            make_row(lane, selector, top_k, leaf_index)
            for leaf_index in leaf_indices
            for selector in selectors
            for top_k in top_ks
        ]
        policy_name = f"{lane.get('lane_id')}_equal_leaf_sweep"
        policies[policy_name] = {
            "lane": lane,
            "row_selector": {
                "selector": policy_name,
                "spec": {
                    "desired_family": lane.get("desired_family"),
                    "leaf_indices": leaf_indices,
                    "selectors": selectors,
                    "top_ks": top_ks,
                    "pin_row_keys": dict_value(lane.get("source_policy_mutation")).get("pin_row_keys"),
                },
            },
            "stress_leaf_results": rows,
            "stress_leaf_summary": summarize_rows(rows),
        }
        all_rows.extend(rows)
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "MODEL-BOUND: equal-leaf signatures use the current low-term total-2 selected-leaf replay harness.",
            "HEURISTIC: this is a bounded transfer-local source search, not a relation certificate.",
            "NO SPEEDUP CLAIM: sweep cost, direct export, substitution, sparse-LA, target descent, and rho accounting remain required.",
        ],
        "method": "order9887_transfer_local_equal_leaf_signature_sweep_source",
        "parameters": {
            **dict_value(p555_source.get("parameters")),
            "leaf_indices": leaf_indices,
            "out": str(args.out),
            "p555_source": str(args.p555_source),
            "selectors": selectors,
            "top_ks": top_ks,
        },
        "policies": policies,
        "schema": "ecdlp.low_term_total2_order9887_equal_leaf_signature_sweep_source_probe.v1",
        "summary": {
            **summarize_rows(all_rows),
            "lane_count": len(policies),
            "selector_count": len(selectors),
            "sweep_leaf_index_count": len(leaf_indices),
            "sweep_top_k_count": len(top_ks),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
