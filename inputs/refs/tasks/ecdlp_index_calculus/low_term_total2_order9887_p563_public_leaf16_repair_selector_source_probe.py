#!/usr/bin/env python3
"""Emit P563 public leaf-16 repair selector rows for the order-9887 toy target.

P562 found that right-extra leaf 16 often repairs verifier survival for the
salt204+salt207 row pair at transfer 20597.  This source artifact narrows that
observation into a public selector: pick the row pair, left leaf 9, and right
leaf {anchor, 16} before replaying rank, support, derived secret, or rho status.
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
    / "low_term_total2_order9887_p562_exact_family_companion_leaf_repair_source_20597_probe.json"
)
DEFAULT_OUT = (
    STATE_DIR
    / "low_term_total2_order9887_p563_public_leaf16_repair_selector_source_20597_probe.json"
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


def leaf_key(values: list[int]) -> str:
    return "-".join(f"{value:02d}" for value in values)


def selector_for(base_selector: str, right_anchor: int, left: list[int], right: list[int]) -> str:
    return (
        f"{base_selector}__p563_public_right16_ra{right_anchor:02d}_"
        f"L{leaf_key(left)}_R{leaf_key(right)}"
    )


def make_row(
    policy_name: str,
    policy_role: str,
    base_selector: str,
    top_k: int,
    transfer_index: int,
    row_keys: list[str],
    left_leaf: int,
    right_anchor: int,
    extra_leaf: int,
) -> dict[str, Any]:
    left = [int(left_leaf)]
    right = sorted({int(right_anchor), int(extra_leaf)})
    selector = selector_for(base_selector, int(right_anchor), left, right)
    return {
        "base_selector": base_selector,
        "below_rho": False,
        "errors": [],
        "left_leaf_indices": left,
        "mutation_kind": "right_extra",
        "mutation_key": (
            f"p563_public_leaf16_right_extra:{policy_role}:"
            f"ra={int(right_anchor)}:L={','.join(map(str, left))}:R={','.join(map(str, right))}"
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
        "row_selector": policy_name,
        "row_selector_public_key_verified": None,
        "selected_leaf_count": len(set(left)) + len(set(right)),
        "selected_row_count": 2,
        "selector": selector,
        "source_verified": True,
        "target": "67.a1@9803",
        "top_k": int(top_k),
        "transfer_index": int(transfer_index),
    }


def rows_for_policy(
    policy_name: str,
    policy_role: str,
    base_selectors: list[str],
    right_anchors: list[int],
    top_k: int,
    transfer_index: int,
    row_keys: list[str],
    left_leaf: int,
    extra_leaf: int,
) -> list[dict[str, Any]]:
    rows = [
        make_row(
            policy_name,
            policy_role,
            base_selector,
            top_k,
            transfer_index,
            row_keys,
            left_leaf,
            right_anchor,
            extra_leaf,
        )
        for right_anchor in right_anchors
        for base_selector in base_selectors
    ]
    rows.sort(key=lambda row: (int_value(row.get("right_anchor")), str(row.get("selector"))))
    return rows


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_role = Counter(str(row.get("policy_role")) for row in rows)
    by_anchor = Counter(str(row.get("right_anchor")) for row in rows)
    by_selector = Counter(str(row.get("base_selector")) for row in rows)
    return {
        "case_count": len(rows),
        "base_selector_counts": dict(sorted(by_selector.items())),
        "policy_role_counts": dict(sorted(by_role.items())),
        "right_anchor_counts": dict(sorted(by_anchor.items(), key=lambda item: int(item[0]))),
        "selected_leaf_count_counts": dict(
            sorted(Counter(str(row.get("selected_leaf_count")) for row in rows).items())
        ),
    }


def policy_payload(policy_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_selector": {
            "selector": policy_name,
            "spec": {
                "extra_leaf": 16,
                "left_leaf": 9,
                "right_anchors": sorted({int_value(row.get("right_anchor")) for row in rows}),
                "selection_rule": "public right-extra leaf-16 selector calibrated from P562",
            },
        },
        "stress_leaf_results": rows,
        "stress_leaf_summary": summarize_rows(rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params-source", type=Path, default=DEFAULT_PARAMS_SOURCE)
    parser.add_argument("--base-selectors", default=DEFAULT_BASE_SELECTORS)
    parser.add_argument("--extension-selectors", default=DEFAULT_EXTENSION_SELECTORS)
    parser.add_argument("--primary-right-anchors", default=DEFAULT_PRIMARY_RIGHT_ANCHORS)
    parser.add_argument("--extension-right-anchors", default=DEFAULT_EXTENSION_RIGHT_ANCHORS)
    parser.add_argument("--control-right-anchors", default=DEFAULT_CONTROL_RIGHT_ANCHORS)
    parser.add_argument("--left-leaf", type=int, default=9)
    parser.add_argument("--extra-leaf", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--transfer-index", type=int, default=20597)
    parser.add_argument(
        "--row-keys",
        default="67.a1@9803:uniform:256:salt204,67.a1@9803:uniform:256:salt207",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    params_source = load_json(args.params_source)
    base_selectors = parse_csv(args.base_selectors)
    extension_selectors = parse_csv(args.extension_selectors)
    row_keys = parse_csv(args.row_keys)
    if len(row_keys) != 2:
        raise ValueError("--row-keys must contain exactly two row keys")

    policies: dict[str, dict[str, Any]] = {}
    primary_rows = rows_for_policy(
        "p563_public_leaf16_right_extra_primary",
        "primary",
        base_selectors,
        parse_int_csv(args.primary_right_anchors),
        args.top_k,
        args.transfer_index,
        row_keys,
        args.left_leaf,
        args.extra_leaf,
    )
    extension_rows = rows_for_policy(
        "p563_public_leaf16_right_extra_extension",
        "extension",
        extension_selectors,
        parse_int_csv(args.extension_right_anchors),
        args.top_k,
        args.transfer_index,
        row_keys,
        args.left_leaf,
        args.extra_leaf,
    )
    control_rows = rows_for_policy(
        "p563_public_leaf16_right_extra_control",
        "above_rho_control",
        base_selectors,
        parse_int_csv(args.control_right_anchors),
        args.top_k,
        args.transfer_index,
        row_keys,
        args.left_leaf,
        args.extra_leaf,
    )
    for name, rows in [
        ("p563_public_leaf16_right_extra_primary", primary_rows),
        ("p563_public_leaf16_right_extra_extension", extension_rows),
        ("p563_public_leaf16_right_extra_control", control_rows),
    ]:
        if rows:
            policies[name] = policy_payload(name, rows)

    all_rows = primary_rows + extension_rows + control_rows
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "HEURISTIC: the selector was calibrated from P562; it is not a held-out novelty result.",
            "PUBLIC-SELECTION BOUNDARY: source rows use row keys, leaf indices, anchors, top_k, and base selector names only.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and full rho accounting remain required.",
        ],
        "method": "order9887_p563_public_leaf16_repair_selector_source",
        "parameters": {
            **dict_value(params_source.get("parameters")),
            "base_selectors": base_selectors,
            "control_right_anchors": parse_int_csv(args.control_right_anchors),
            "extra_leaf": int(args.extra_leaf),
            "extension_right_anchors": parse_int_csv(args.extension_right_anchors),
            "extension_selectors": extension_selectors,
            "left_leaf": int(args.left_leaf),
            "out": str(args.out),
            "params_source": str(args.params_source),
            "primary_right_anchors": parse_int_csv(args.primary_right_anchors),
            "row_keys": row_keys,
            "top_k": int(args.top_k),
            "transfer_index": int(args.transfer_index),
        },
        "policies": policies,
        "schema": "ecdlp.low_term_total2_order9887_p563_public_leaf16_repair_selector_source_probe.v1",
        "summary": {
            **summarize_rows(all_rows),
            "base_selector_count": len(set(base_selectors + extension_selectors)),
            "control_case_count": len(control_rows),
            "extension_case_count": len(extension_rows),
            "primary_case_count": len(primary_rows),
            "right_extra_leaf": int(args.extra_leaf),
            "top_k": int(args.top_k),
            "transfer_index": int(args.transfer_index),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
