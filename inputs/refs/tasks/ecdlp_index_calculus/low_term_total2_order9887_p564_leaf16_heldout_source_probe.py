#!/usr/bin/env python3
"""Emit P564 held-out leaf-16 direct-selector rows for order-9887 scouting.

This is the first red-team follow-up to P563.  It freezes the public leaf-16
shape but excludes the calibrated P562/P563 row pair and transfer.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PARAMS_SOURCE = (
    STATE_DIR
    / "low_term_total2_order9887_p563_public_leaf16_repair_selector_source_20597_probe.json"
)
DEFAULT_OUT = (
    STATE_DIR
    / "low_term_total2_order9887_p564_leaf16_heldout_source_20592_20604_probe.json"
)
DEFAULT_BASE_SELECTORS = (
    "mode_cost_hybrid_support_monic_b_total2,"
    "mode_cost_low_leaf_index_total2,"
    "mode_hybrid_support_monic_b_total2,"
    "mode_low_leaf_index_total2"
)
DEFAULT_EXTENSION_SELECTORS = (
    "mode_cost_hybrid_support_monic_b_total2,"
    "mode_cost_low_leaf_index_total2,"
    "mode_hybrid_support_monic_b_total2"
)
DEFAULT_PRIMARY_RIGHT_ANCHORS = "3,6,7,8,9,11"
DEFAULT_EXTENSION_RIGHT_ANCHORS = "12"
DEFAULT_CONTROL_RIGHT_ANCHORS = "13"
DEFAULT_TRANSFERS = "20592,20593,20594,20595,20596,20598,20599,20600,20601,20602,20603,20604"
DEFAULT_ROW_PAIRS = "203+207;203+208;204+206;204+208;205+207;205+208;206+207;206+208"


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


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip()]


def parse_int_csv(raw: str) -> list[int]:
    return [int(item.strip()) for item in str(raw).split(",") if item.strip()]


def parse_row_pairs(raw: str, target: str) -> list[tuple[str, list[str]]]:
    pairs: list[tuple[str, list[str]]] = []
    for chunk in str(raw).split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = [part.strip() for part in chunk.replace(",", "+").split("+") if part.strip()]
        if len(parts) != 2:
            raise ValueError(f"row pair must look like A+B, got {chunk!r}")
        salts = [int(part) for part in parts]
        pair_id = f"salt{salts[0]}_salt{salts[1]}"
        row_keys = [f"{target}:uniform:256:salt{salt}" for salt in salts]
        pairs.append((pair_id, row_keys))
    return pairs


def leaf_key(values: list[int]) -> str:
    return "-".join(f"{value:02d}" for value in values)


def selector_for(
    base_selector: str,
    transfer_index: int,
    pair_id: str,
    right_anchor: int,
    left: list[int],
    right: list[int],
) -> str:
    return (
        f"{base_selector}__p564_holdout_t{transfer_index}_{pair_id}_"
        f"ra{right_anchor:02d}_L{leaf_key(left)}_R{leaf_key(right)}"
    )


def make_row(
    policy_name: str,
    policy_role: str,
    base_selector: str,
    target: str,
    transfer_index: int,
    pair_id: str,
    row_keys: list[str],
    top_k: int,
    left_leaf: int,
    right_anchor: int,
    extra_leaf: int,
) -> dict[str, Any]:
    left = [int(left_leaf)]
    right = sorted({int(right_anchor), int(extra_leaf)})
    selector = selector_for(base_selector, transfer_index, pair_id, int(right_anchor), left, right)
    return {
        "base_selector": base_selector,
        "below_rho": False,
        "errors": [],
        "left_leaf_indices": left,
        "mutation_kind": "right_extra",
        "mutation_key": (
            f"p564_leaf16_heldout:{policy_role}:t={int(transfer_index)}:"
            f"pair={pair_id}:ra={int(right_anchor)}:L={','.join(map(str, left))}:"
            f"R={','.join(map(str, right))}"
        ),
        "ops_over_rho": None,
        "policy_role": policy_role,
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "right_anchor": int(right_anchor),
        "right_leaf_indices": right,
        "row_keys": row_keys,
        "row_leaf_keys": [
            {"leaf_indices": left, "row_key": row_keys[0]},
            {"leaf_indices": right, "row_key": row_keys[1]},
        ],
        "row_pair_key": " + ".join(row_keys),
        "row_pair_public_id": pair_id,
        "row_selector": policy_name,
        "row_selector_public_key_verified": None,
        "selected_leaf_count": len(set(left)) + len(set(right)),
        "selected_row_count": 2,
        "selector": selector,
        "source_verified": True,
        "target": target,
        "top_k": int(top_k),
        "transfer_index": int(transfer_index),
    }


def rows_for_role(
    policy_name: str,
    policy_role: str,
    base_selectors: list[str],
    right_anchors: list[int],
    target: str,
    transfers: list[int],
    row_pairs: list[tuple[str, list[str]]],
    top_k: int,
    left_leaf: int,
    extra_leaf: int,
) -> list[dict[str, Any]]:
    rows = []
    for transfer_index in transfers:
        for pair_id, row_keys in row_pairs:
            for right_anchor in right_anchors:
                for base_selector in base_selectors:
                    rows.append(
                        make_row(
                            policy_name,
                            policy_role,
                            base_selector,
                            target,
                            transfer_index,
                            pair_id,
                            row_keys,
                            top_k,
                            left_leaf,
                            right_anchor,
                            extra_leaf,
                        )
                    )
    rows.sort(
        key=lambda row: (
            int_value(row.get("transfer_index")),
            str(row.get("row_pair_public_id")),
            int_value(row.get("right_anchor")),
            str(row.get("selector")),
        )
    )
    return rows


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_role = Counter(str(row.get("policy_role")) for row in rows)
    by_anchor = Counter(str(row.get("right_anchor")) for row in rows)
    by_pair = Counter(str(row.get("row_pair_public_id")) for row in rows)
    by_transfer = Counter(str(row.get("transfer_index")) for row in rows)
    return {
        "case_count": len(rows),
        "policy_role_counts": dict(sorted(by_role.items())),
        "right_anchor_counts": dict(sorted(by_anchor.items(), key=lambda item: int(item[0]))),
        "row_pair_counts": dict(sorted(by_pair.items())),
        "selected_leaf_count_counts": dict(
            sorted(Counter(str(row.get("selected_leaf_count")) for row in rows).items())
        ),
        "transfer_counts": dict(sorted(by_transfer.items(), key=lambda item: int(item[0]))),
    }


def policy_payload(policy_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_selector": {
            "selector": policy_name,
            "spec": {
                "excluded_calibration_pair": "salt204_salt207",
                "excluded_calibration_transfer": 20597,
                "extra_leaf": 16,
                "left_leaf": 9,
                "selection_rule": "held-out public right-extra leaf-16 direct selector",
            },
        },
        "stress_leaf_results": rows,
        "stress_leaf_summary": summarize_rows(rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params-source", type=Path, default=DEFAULT_PARAMS_SOURCE)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--row-pairs", default=DEFAULT_ROW_PAIRS)
    parser.add_argument("--transfers", default=DEFAULT_TRANSFERS)
    parser.add_argument("--base-selectors", default=DEFAULT_BASE_SELECTORS)
    parser.add_argument("--extension-selectors", default=DEFAULT_EXTENSION_SELECTORS)
    parser.add_argument("--primary-right-anchors", default=DEFAULT_PRIMARY_RIGHT_ANCHORS)
    parser.add_argument("--extension-right-anchors", default=DEFAULT_EXTENSION_RIGHT_ANCHORS)
    parser.add_argument("--control-right-anchors", default=DEFAULT_CONTROL_RIGHT_ANCHORS)
    parser.add_argument("--left-leaf", type=int, default=9)
    parser.add_argument("--extra-leaf", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    params_source = load_json(args.params_source)
    base_selectors = parse_csv(args.base_selectors)
    extension_selectors = parse_csv(args.extension_selectors)
    transfers = parse_int_csv(args.transfers)
    row_pairs = parse_row_pairs(args.row_pairs, args.target)

    policies: dict[str, dict[str, Any]] = {}
    primary_rows = rows_for_role(
        "p564_leaf16_heldout_primary",
        "primary",
        base_selectors,
        parse_int_csv(args.primary_right_anchors),
        args.target,
        transfers,
        row_pairs,
        args.top_k,
        args.left_leaf,
        args.extra_leaf,
    )
    extension_rows = rows_for_role(
        "p564_leaf16_heldout_extension",
        "extension",
        extension_selectors,
        parse_int_csv(args.extension_right_anchors),
        args.target,
        transfers,
        row_pairs,
        args.top_k,
        args.left_leaf,
        args.extra_leaf,
    )
    control_rows = rows_for_role(
        "p564_leaf16_heldout_control",
        "above_rho_control",
        base_selectors,
        parse_int_csv(args.control_right_anchors),
        args.target,
        transfers,
        row_pairs,
        args.top_k,
        args.left_leaf,
        args.extra_leaf,
    )
    for name, rows in [
        ("p564_leaf16_heldout_primary", primary_rows),
        ("p564_leaf16_heldout_extension", extension_rows),
        ("p564_leaf16_heldout_control", control_rows),
    ]:
        if rows:
            policies[name] = policy_payload(name, rows)

    all_rows = primary_rows + extension_rows + control_rows
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: held-out scout targets order-9887 toy harness only.",
            "HEURISTIC: leaf-16 shape is frozen from P563 but row pairs/transfers are held out.",
            "PUBLIC-SELECTION BOUNDARY: source rows contain public row keys, transfer, leaf indices, anchors, top_k, and base selector names only.",
            "NO SPEEDUP CLAIM: this scout only asks whether the direct selector transfers beyond the calibrated pair/transfer.",
        ],
        "method": "order9887_p564_leaf16_heldout_source",
        "parameters": {
            **dict_value(params_source.get("parameters")),
            "base_selectors": base_selectors,
            "control_right_anchors": parse_int_csv(args.control_right_anchors),
            "excluded_calibration_pair": "salt204_salt207",
            "excluded_calibration_transfer": 20597,
            "extra_leaf": int(args.extra_leaf),
            "extension_right_anchors": parse_int_csv(args.extension_right_anchors),
            "extension_selectors": extension_selectors,
            "left_leaf": int(args.left_leaf),
            "out": str(args.out),
            "params_source": str(args.params_source),
            "primary_right_anchors": parse_int_csv(args.primary_right_anchors),
            "row_pairs": [pair_id for pair_id, _row_keys in row_pairs],
            "target": args.target,
            "top_k": int(args.top_k),
            "transfers": transfers,
        },
        "policies": policies,
        "schema": "ecdlp.low_term_total2_order9887_p564_leaf16_heldout_source_probe.v1",
        "summary": {
            **summarize_rows(all_rows),
            "control_case_count": len(control_rows),
            "extension_case_count": len(extension_rows),
            "primary_case_count": len(primary_rows),
            "right_extra_leaf": int(args.extra_leaf),
            "row_pair_count": len(row_pairs),
            "top_k": int(args.top_k),
            "transfer_count": len(transfers),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
