#!/usr/bin/env python3
"""Emit P561 low-cost row-pair leaf-pair sweep rows from the P553 scheduler."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SCHEDULER = STATE_DIR / "low_term_total2_order9887_source_row_anchor_scheduler_20544_20599_probe.json"
DEFAULT_PARAMS_SOURCE = STATE_DIR / "low_term_total2_order9887_p555_pinned_family_source_20544_20554_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p561_lowcost_rowpair_leafpair_sweep_source_20544_20597_probe.json"
DEFAULT_LEAF_INDICES = "0,3,5,6,7,8,9,11,12,13"


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


def parse_int_csv(raw: str) -> list[int]:
    return [int(item.strip()) for item in str(raw).split(",") if item.strip()]


def row_keys_from_pair_key(pair_key: str) -> list[str]:
    return sorted(part.strip() for part in pair_key.split(" + ") if part.strip())


def family_key(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def leaf_pair_selector(base_selector: str, left: int, right: int, transfer: int, pair_index: int) -> str:
    return f"{base_selector}__p561_pair{pair_index:02d}_leaf_{left:02d}_{right:02d}_t{transfer}"


def low_cost_items(scheduler: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[tuple[str, int, str, int]] = set()
    out: list[dict[str, Any]] = []
    for item in list_value(scheduler.get("top_work_items")):
        if not isinstance(item, dict) or item.get("action") != "LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP":
            continue
        case = dict_value(item.get("case"))
        pair_key = str(item.get("row_pair_key") or "")
        transfer = int_value(case.get("transfer_index") or item.get("transfer_index"))
        selector = str(case.get("selector") or item.get("selector") or "")
        top_k = int_value(case.get("top_k") or item.get("top_k"))
        key = (pair_key, transfer, selector, top_k)
        if not pair_key or not selector or key in seen:
            continue
        seen.add(key)
        out.append(item)
    out.sort(
        key=lambda item: (
            int_value(dict_value(item.get("case")).get("transfer_index") or item.get("transfer_index")),
            str(item.get("row_pair_key")),
            str(dict_value(item.get("case")).get("selector") or item.get("selector")),
            int_value(dict_value(item.get("case")).get("top_k") or item.get("top_k")),
        )
    )
    return out


def make_row(item: dict[str, Any], pair_index: int, left: int, right: int) -> dict[str, Any]:
    case = dict_value(item.get("case"))
    match = dict_value(item.get("best_family_match"))
    desired = list_value(match.get("family"))
    target = case.get("target") or item.get("target")
    transfer = int_value(case.get("transfer_index") or item.get("transfer_index"))
    base_selector = str(case.get("selector") or item.get("selector"))
    top_k = int_value(case.get("top_k") or item.get("top_k"))
    row_keys = row_keys_from_pair_key(str(item.get("row_pair_key")))
    if len(row_keys) != 2:
        raise ValueError(f"expected two row keys in {item.get('row_pair_key')!r}")
    selector = leaf_pair_selector(base_selector, left, right, transfer, pair_index)
    return {
        "base_selector": base_selector,
        "baseline_support": list_value(case.get("coeff_support")),
        "below_rho": False,
        "desired_family": desired,
        "desired_family_key": family_key(desired),
        "errors": [],
        "leaf_pair": [int(left), int(right)],
        "leaf_pair_key": f"{int(left)},{int(right)}",
        "ops_over_rho": None,
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "row_keys": row_keys,
        "row_leaf_keys": [
            {"leaf_indices": [int(left)], "row_key": row_keys[0]},
            {"leaf_indices": [int(right)], "row_key": row_keys[1]},
        ],
        "row_pair_index": pair_index,
        "row_pair_key": item.get("row_pair_key"),
        "row_selector": "p561_lowcost_rowpair_leafpair_sweep",
        "row_selector_public_key_verified": None,
        "scheduler_action": item.get("action"),
        "scheduler_score": item.get("score"),
        "selected_leaf_count": 2,
        "selected_row_count": 2,
        "selector": selector,
        "source_verified": True,
        "target": target,
        "top_k": top_k,
        "transfer_index": transfer,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_transfer = Counter(str(row.get("transfer_index")) for row in rows)
    by_pair = Counter(str(row.get("row_pair_key")) for row in rows)
    by_leaf_pair = Counter(str(row.get("leaf_pair_key")) for row in rows)
    return {
        "case_count": len(rows),
        "leaf_pair_count": len(by_leaf_pair),
        "row_pair_counts": dict(sorted(by_pair.items())),
        "row_pair_count": len(by_pair),
        "top_leaf_pair_counts": dict(by_leaf_pair.most_common(12)),
        "transfer_counts": dict(sorted(by_transfer.items(), key=lambda item: int(item[0]))),
        "transfer_count": len(by_transfer),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheduler", type=Path, default=DEFAULT_SCHEDULER)
    parser.add_argument("--params-source", type=Path, default=DEFAULT_PARAMS_SOURCE)
    parser.add_argument("--leaf-indices", default=DEFAULT_LEAF_INDICES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scheduler = load_json(args.scheduler)
    params_source = load_json(args.params_source)
    leaf_indices = parse_int_csv(args.leaf_indices)
    items = low_cost_items(scheduler)
    rows = [
        make_row(item, pair_index, left, right)
        for pair_index, item in enumerate(items)
        for left in leaf_indices
        for right in leaf_indices
    ]
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "MODEL-BOUND: row-pair swaps are replayed through the current low-term total-2 harness.",
            "HEURISTIC: this tests source-policy composition, not a complete target descent.",
            "NO SPEEDUP CLAIM: export, substitution, sparse-LA, target descent, and full rho accounting remain required.",
        ],
        "method": "order9887_p561_lowcost_rowpair_leafpair_sweep_source",
        "parameters": {
            **dict_value(params_source.get("parameters")),
            "leaf_indices": leaf_indices,
            "out": str(args.out),
            "params_source": str(args.params_source),
            "scheduler": str(args.scheduler),
        },
        "policies": {
            "p561_lowcost_rowpair_leafpair_sweep": {
                "row_selector": {
                    "selector": "p561_lowcost_rowpair_leafpair_sweep",
                    "spec": {
                        "leaf_indices": leaf_indices,
                        "scheduler": str(args.scheduler),
                        "work_item_action": "LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP",
                    },
                },
                "scheduler_items": items,
                "stress_leaf_results": rows,
                "stress_leaf_summary": summarize_rows(rows),
            }
        },
        "schema": "ecdlp.low_term_total2_order9887_p561_lowcost_rowpair_leafpair_sweep_source_probe.v1",
        "summary": {
            **summarize_rows(rows),
            "leaf_index_count": len(leaf_indices),
            "scheduler_item_count": len(items),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
