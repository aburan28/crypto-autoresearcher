#!/usr/bin/env python3
"""Emit P562 companion-leaf repair rows for the P561 exact [1,6,13] candidates."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PARAMS_SOURCE = STATE_DIR / "low_term_total2_order9887_p561_lowcost_rowpair_leafpair_sweep_source_20544_20597_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p562_exact_family_companion_leaf_repair_source_20597_probe.json"
DEFAULT_BASE_SELECTORS = (
    "mode_cost_hybrid_support_monic_b_total2,"
    "mode_cost_low_leaf_index_total2,"
    "mode_hybrid_support_monic_b_total2,"
    "mode_low_leaf_index_total2"
)
DEFAULT_RIGHT_ANCHORS = "3,6,7,8,9,11,12,13"
DEFAULT_EXTRA_LEAF_INDICES = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"


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
    return [int(item.strip()) for item in str(raw).split(",") if item.strip()]


def unique_sorted(values: list[int]) -> list[int]:
    return sorted({int(value) for value in values})


def leaf_key(values: list[int]) -> str:
    return "-".join(f"{value:02d}" for value in values)


def selector_for(base_selector: str, kind: str, right_anchor: int, left: list[int], right: list[int]) -> str:
    return (
        f"{base_selector}__p562_{kind}_ra{right_anchor:02d}_"
        f"L{leaf_key(left)}_R{leaf_key(right)}"
    )


def mutation_key(kind: str, right_anchor: int, left: list[int], right: list[int]) -> str:
    return f"{kind}:ra={right_anchor}:L={','.join(map(str, left))}:R={','.join(map(str, right))}"


def build_mutations(left_anchor: int, right_anchors: list[int], extras: list[int]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []

    def add(kind: str, right_anchor: int, left_values: list[int], right_values: list[int]) -> None:
        left = unique_sorted(left_values)
        right = unique_sorted(right_values)
        mutations.append(
            {
                "kind": kind,
                "left_leaf_indices": left,
                "mutation_key": mutation_key(kind, right_anchor, left, right),
                "right_anchor": int(right_anchor),
                "right_leaf_indices": right,
            }
        )

    for right_anchor in right_anchors:
        add("anchor_control", right_anchor, [left_anchor], [right_anchor])
        for extra in extras:
            if extra != left_anchor:
                add("left_extra", right_anchor, [left_anchor, extra], [right_anchor])
            if extra != right_anchor:
                add("right_extra", right_anchor, [left_anchor], [right_anchor, extra])
            add("shared_extra", right_anchor, [left_anchor, extra], [right_anchor, extra])

    seen: set[tuple[str, int, tuple[int, ...], tuple[int, ...]]] = set()
    out: list[dict[str, Any]] = []
    for mutation in mutations:
        key = (
            str(mutation["kind"]),
            int_value(mutation["right_anchor"]),
            tuple(int_value(value) for value in list_value(mutation["left_leaf_indices"])),
            tuple(int_value(value) for value in list_value(mutation["right_leaf_indices"])),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(mutation)
    out.sort(key=lambda item: (int_value(item["right_anchor"]), str(item["kind"]), str(item["mutation_key"])))
    return out


def make_row(
    base_selector: str,
    top_k: int,
    mutation: dict[str, Any],
    transfer_index: int,
    row_keys: list[str],
) -> dict[str, Any]:
    left = [int_value(value) for value in list_value(mutation.get("left_leaf_indices"))]
    right = [int_value(value) for value in list_value(mutation.get("right_leaf_indices"))]
    selector = selector_for(
        base_selector,
        str(mutation["kind"]),
        int_value(mutation["right_anchor"]),
        left,
        right,
    )
    return {
        "base_selector": base_selector,
        "baseline_support": [1, 6, 13],
        "below_rho": False,
        "desired_family": [1, 6, 13],
        "desired_family_key": "1,6,13",
        "errors": [],
        "left_leaf_indices": left,
        "mutation_kind": mutation.get("kind"),
        "mutation_key": mutation.get("mutation_key"),
        "ops_over_rho": None,
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "right_anchor": int_value(mutation.get("right_anchor")),
        "right_leaf_indices": right,
        "row_keys": row_keys,
        "row_leaf_keys": [
            {"leaf_indices": left, "row_key": row_keys[0]},
            {"leaf_indices": right, "row_key": row_keys[1]},
        ],
        "row_pair_key": " + ".join(row_keys),
        "row_selector": "p562_exact_family_companion_leaf_repair",
        "row_selector_public_key_verified": None,
        "selected_leaf_count": len(set(left)) + len(set(right)),
        "selected_row_count": 2,
        "selector": selector,
        "source_verified": True,
        "target": "67.a1@9803",
        "top_k": int(top_k),
        "transfer_index": int(transfer_index),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind = Counter(str(row.get("mutation_kind")) for row in rows)
    by_right_anchor = Counter(str(row.get("right_anchor")) for row in rows)
    by_selected_leaf_count = Counter(str(row.get("selected_leaf_count")) for row in rows)
    return {
        "case_count": len(rows),
        "mutation_kind_counts": dict(sorted(by_kind.items())),
        "right_anchor_counts": dict(sorted(by_right_anchor.items(), key=lambda item: int(item[0]))),
        "right_anchor_count": len(by_right_anchor),
        "selected_leaf_count_counts": dict(sorted(by_selected_leaf_count.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params-source", type=Path, default=DEFAULT_PARAMS_SOURCE)
    parser.add_argument("--base-selectors", default=DEFAULT_BASE_SELECTORS)
    parser.add_argument("--extra-leaf-indices", default=DEFAULT_EXTRA_LEAF_INDICES)
    parser.add_argument("--left-anchor", type=int, default=9)
    parser.add_argument("--right-anchors", default=DEFAULT_RIGHT_ANCHORS)
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
    extras = parse_int_csv(args.extra_leaf_indices)
    right_anchors = parse_int_csv(args.right_anchors)
    row_keys = parse_csv(args.row_keys)
    if len(row_keys) != 2:
        raise ValueError("--row-keys must contain exactly two row keys")
    mutations = build_mutations(args.left_anchor, right_anchors, extras)
    rows = [
        make_row(selector, args.top_k, mutation, args.transfer_index, row_keys)
        for mutation in mutations
        for selector in base_selectors
    ]
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "MODEL-BOUND: companion-leaf repairs are replayed through the current low-term total-2 harness.",
            "HEURISTIC: this tests verifier survival for a source-family candidate, not target descent.",
            "NO SPEEDUP CLAIM: export, substitution, sparse-LA, target descent, and full rho accounting remain required.",
        ],
        "method": "order9887_p562_exact_family_companion_leaf_repair_source",
        "parameters": {
            **dict_value(params_source.get("parameters")),
            "base_selectors": base_selectors,
            "extra_leaf_indices": extras,
            "left_anchor": int(args.left_anchor),
            "out": str(args.out),
            "params_source": str(args.params_source),
            "right_anchors": right_anchors,
            "row_keys": row_keys,
            "top_k": int(args.top_k),
            "transfer_index": int(args.transfer_index),
        },
        "policies": {
            "p562_exact_family_companion_leaf_repair": {
                "row_selector": {
                    "selector": "p562_exact_family_companion_leaf_repair",
                    "spec": {
                        "base_selectors": base_selectors,
                        "left_anchor": int(args.left_anchor),
                        "right_anchors": right_anchors,
                        "row_keys": row_keys,
                        "top_k": int(args.top_k),
                        "transfer_index": int(args.transfer_index),
                    },
                },
                "stress_leaf_results": rows,
                "stress_leaf_summary": summarize_rows(rows),
            }
        },
        "schema": "ecdlp.low_term_total2_order9887_p562_exact_family_companion_leaf_repair_source_probe.v1",
        "summary": {
            **summarize_rows(rows),
            "base_selector_count": len(base_selectors),
            "extra_leaf_index_count": len(extras),
            "left_anchor": int(args.left_anchor),
            "mutation_count": len(mutations),
            "top_k": int(args.top_k),
            "transfer_index": int(args.transfer_index),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
