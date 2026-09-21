#!/usr/bin/env python3
"""P955 post-1144 target-67 materialization boundary audit.

This audit separates three claims:

1. whether P954-compatible post-1144 fresh quadratic-root rows exist;
2. whether the materialized post-1144 target-67 direct-gate stream verifies
   selected relation groups below rho;
3. whether those positives are in the P954 low-term-support family or in a
   distinct low-term-span family.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p955_post1144_target67_materialization_boundary_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p955_post1144_target67_materialization_boundary_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p955_post1144_target67_materialization_boundary_audit.v1"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_POST_MIN = 1144

FRESH_RE = re.compile(
    r"low_term_total2_ffe_public_factor_quadratic_root_fresh_(\d+)_(\d+)_expanded_probe\.json$"
)
DIRECT_RE = re.compile(
    r"low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_(\d+)_(\d+)_probe\.json$"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
    }


def window_for(path: Path, regex: re.Pattern[str]) -> tuple[int, int] | None:
    match = regex.search(path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def post_window_paths(state_dir: Path, pattern: str, regex: re.Pattern[str], post_min: int) -> list[tuple[int, int, Path]]:
    paths: list[tuple[int, int, Path]] = []
    for path in state_dir.glob(pattern):
        if path.name.startswith("._"):
            continue
        window = window_for(path, regex)
        if window is None:
            continue
        start, end = window
        if start >= post_min:
            paths.append((start, end, path))
    return sorted(paths)


def source_clean(row: dict[str, Any]) -> bool:
    return bool(
        row.get("public_factor_quadratic_root_beats_rho")
        and row.get("quadratic_preserves_selected_root_pairs")
        and not row.get("chosen_false_positive_source")
    )


def summarize_fresh_stream(paths: list[tuple[int, int, Path]], target: str) -> dict[str, Any]:
    target_rows = 0
    target_clean_rows = 0
    surfaces: set[str] = set()
    clean_surfaces: set[str] = set()
    by_window: list[dict[str, Any]] = []
    policies = Counter()
    for start, end, path in paths:
        payload = load_json(path)
        policy_rows = payload.get("policy_rows") or {}
        window_target_rows = 0
        window_clean_rows = 0
        window_surfaces: set[str] = set()
        window_clean_surfaces: set[str] = set()
        for policy, rows in sorted(policy_rows.items()):
            for row in rows or []:
                if str(row.get("target")) != target:
                    continue
                policies[str(policy)] += 1
                window_target_rows += 1
                target_rows += 1
                surface_id = str(row.get("surface_id") or "")
                if surface_id:
                    surfaces.add(surface_id)
                    window_surfaces.add(surface_id)
                if source_clean(row):
                    target_clean_rows += 1
                    window_clean_rows += 1
                    if surface_id:
                        clean_surfaces.add(surface_id)
                        window_clean_surfaces.add(surface_id)
        by_window.append(
            {
                "artifact": str(path),
                "policy_count": len(policy_rows),
                "target_clean_row_count": window_clean_rows,
                "target_policy_row_count": window_target_rows,
                "target_unique_clean_surface_count": len(window_clean_surfaces),
                "target_unique_surface_count": len(window_surfaces),
                "window": f"{start}_{end}",
            }
        )
    return {
        "artifact_count": len(paths),
        "by_window": by_window,
        "policy_target_row_counts": dict(sorted(policies.items())),
        "target_clean_row_count": target_clean_rows,
        "target_policy_row_count": target_rows,
        "target_unique_clean_surface_count": len(clean_surfaces),
        "target_unique_surface_count": len(surfaces),
        "window_count": len(paths),
        "window_range": [f"{paths[0][0]}_{paths[0][1]}", f"{paths[-1][0]}_{paths[-1][1]}"] if paths else [],
    }


def p954_family_selector(selector: str) -> bool:
    return "low_term_support" in selector


def compact_direct_case(row: dict[str, Any], path: Path, start: int, end: int) -> dict[str, Any]:
    return {
        "artifact": str(path),
        "direct_union_derived_secret": row.get("direct_union_derived_secret"),
        "direct_union_rank": int_value(row.get("direct_union_rank")),
        "direct_union_relation_count": int_value(row.get("direct_union_relation_count")),
        "direct_verifier_replay_ops": int_value(row.get("direct_verifier_replay_ops")),
        "direct_verifier_replay_ops_over_rho": row.get("direct_verifier_replay_ops_over_rho"),
        "gate_name": row.get("gate_name"),
        "p954_family_selector": p954_family_selector(str(row.get("selector"))),
        "public_features": row.get("public_features"),
        "rho": int_value(row.get("rho")),
        "row_keys": row.get("row_keys") or [],
        "selector": row.get("selector"),
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
        "window": f"{start}_{end}",
    }


def summarize_direct_stream(
    paths: list[tuple[int, int, Path]],
    target: str,
    best_limit: int,
) -> dict[str, Any]:
    selector_counts: dict[str, Counter[str]] = defaultdict(Counter)
    gate_counts = Counter()
    selected_cases: list[dict[str, Any]] = []
    selected_verified: list[dict[str, Any]] = []
    selected_below: list[dict[str, Any]] = []
    selected_unverified: list[dict[str, Any]] = []
    selected_above: list[dict[str, Any]] = []
    direct_below_all: list[dict[str, Any]] = []
    p954_selected_below: list[dict[str, Any]] = []
    target_case_count = 0
    all_case_count = 0
    target_artifacts_with_cases = 0
    by_window: list[dict[str, Any]] = []

    for start, end, path in paths:
        payload = load_json(path)
        cases = payload.get("cases") or []
        all_case_count += len(cases)
        window_target_cases = [case for case in cases if str(case.get("target")) == target]
        if window_target_cases:
            target_artifacts_with_cases += 1
        window_selected = 0
        window_verified = 0
        window_below = 0
        window_unverified = 0
        for case in window_target_cases:
            target_case_count += 1
            selector = str(case.get("selector"))
            selected = bool(case.get("public_low_prefix_gate_selected"))
            verified = bool(case.get("direct_union_public_key_verified"))
            below = bool(case.get("direct_below_rho"))
            ratio = float_value(case.get("direct_verifier_replay_ops_over_rho"))
            selector_counts[selector]["target_case_count"] += 1
            if selected:
                selector_counts[selector]["selected_count"] += 1
                selected_cases.append(compact_direct_case(case, path, start, end))
                window_selected += 1
                gate_counts[str(case.get("gate_name"))] += 1
            if selected and verified:
                selector_counts[selector]["selected_verified_count"] += 1
                selected_verified.append(compact_direct_case(case, path, start, end))
                window_verified += 1
            if selected and verified and below:
                selector_counts[selector]["selected_below_rho_verified_count"] += 1
                compact = compact_direct_case(case, path, start, end)
                selected_below.append(compact)
                window_below += 1
                if p954_family_selector(selector):
                    p954_selected_below.append(compact)
            if selected and verified and not below:
                selected_above.append(compact_direct_case(case, path, start, end))
            if selected and not verified:
                selector_counts[selector]["selected_unverified_count"] += 1
                selected_unverified.append(compact_direct_case(case, path, start, end))
                window_unverified += 1
            if verified and below:
                direct_below_all.append(compact_direct_case(case, path, start, end))
            if ratio is not None:
                selector_counts[selector]["ratio_observation_count"] += 1
        if window_target_cases:
            by_window.append(
                {
                    "artifact": str(path),
                    "selected_below_rho_verified_count": window_below,
                    "selected_count": window_selected,
                    "selected_unverified_count": window_unverified,
                    "selected_verified_count": window_verified,
                    "target_case_count": len(window_target_cases),
                    "window": f"{start}_{end}",
                }
            )

    best_selected_below = sorted(
        selected_below,
        key=lambda row: (
            float_value(row.get("direct_verifier_replay_ops_over_rho"), 10**18),
            int_value(row.get("transfer_index")),
            str(row.get("artifact")),
        ),
    )[:best_limit]
    selected_ratios = [
        float_value(row.get("direct_verifier_replay_ops_over_rho"))
        for row in selected_verified
        if float_value(row.get("direct_verifier_replay_ops_over_rho")) is not None
    ]
    below_ratios = [
        float_value(row.get("direct_verifier_replay_ops_over_rho"))
        for row in selected_below
        if float_value(row.get("direct_verifier_replay_ops_over_rho")) is not None
    ]
    selector_summary = {
        selector: dict(counts)
        for selector, counts in sorted(
            selector_counts.items(),
            key=lambda item: (
                -item[1]["selected_below_rho_verified_count"],
                -item[1]["selected_verified_count"],
                item[0],
            ),
        )
    }
    return {
        "all_case_count": all_case_count,
        "artifact_count": len(paths),
        "best_selected_below_rho_verified_cases": best_selected_below,
        "by_window_positive_sample": [
            row
            for row in by_window
            if int_value(row.get("selected_below_rho_verified_count")) > 0
        ][:best_limit],
        "direct_below_rho_verified_count": len(direct_below_all),
        "gate_selected_counts": dict(sorted(gate_counts.items())),
        "p954_family_selected_below_rho_verified_count": len(p954_selected_below),
        "selector_summary": selector_summary,
        "selected_below_rho_verified_count": len(selected_below),
        "selected_direct_verified_count": len(selected_verified),
        "selected_direct_verified_ops_over_rho": stats([value for value in selected_ratios if value is not None]),
        "selected_direct_below_rho_ops_over_rho": stats([value for value in below_ratios if value is not None]),
        "selected_unverified_count": len(selected_unverified),
        "selected_verified_above_rho_count": len(selected_above),
        "target_artifacts_with_cases": target_artifacts_with_cases,
        "target_case_count": target_case_count,
        "window_count": len(paths),
        "window_range": [f"{paths[0][0]}_{paths[0][1]}", f"{paths[-1][0]}_{paths[-1][1]}"] if paths else [],
    }


def determine_claim(fresh: dict[str, Any], direct: dict[str, Any]) -> str:
    if int_value(direct.get("p954_family_selected_below_rho_verified_count")) > 0:
        return "P955_POST1144_P954_FAMILY_SELECTED_BELOW_RHO"
    if int_value(direct.get("selected_below_rho_verified_count")) > 0:
        return "P955_POST1144_ALTERNATE_PUBLIC_DIRECT_GATE_BELOW_RHO"
    if int_value(fresh.get("target_policy_row_count")) == 0 and int_value(direct.get("target_case_count")) > 0:
        return "NEGATIVE_RESULT_P955_P954_FRESH_ABSENT_DIRECT_GATE_NO_SELECTED_BELOW_RHO"
    if int_value(fresh.get("target_policy_row_count")) == 0:
        return "NEGATIVE_RESULT_P955_NO_POST1144_TARGET67_MATERIALIZATION"
    return "NEGATIVE_RESULT_P955_POST1144_NO_SELECTED_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = Path(args.state_dir)
    fresh_paths = post_window_paths(
        state_dir,
        "low_term_total2_ffe_public_factor_quadratic_root_fresh_*_expanded_probe.json",
        FRESH_RE,
        int(args.post_min),
    )
    direct_paths = post_window_paths(
        state_dir,
        "low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_*_probe.json",
        DIRECT_RE,
        int(args.post_min),
    )
    fresh_summary = summarize_fresh_stream(fresh_paths, args.target)
    direct_summary = summarize_direct_stream(direct_paths, args.target, int(args.best_limit))
    claim = determine_claim(fresh_summary, direct_summary)
    p954_status = (
        "validated"
        if int_value(direct_summary.get("p954_family_selected_below_rho_verified_count")) > 0
        else "not_validated_post1144"
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "direct_gate_summary": direct_summary,
        "fresh_stream_summary": fresh_summary,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "POLLARD-RHO BOUNDARY: below-rho claims compare verifier component ops against toy rho, not an end-to-end deployed-curve algorithm.",
            "P954-FAMILY BOUNDARY: post-1144 positives are not credited to the P954 low-term-support family unless the selector name contains low_term_support.",
            "MATERIALIZATION BOUNDARY: direct-gate artifacts verify selected relation groups, while full relation collection and target descent remain open.",
        ],
        "method": "p955_post1144_target67_materialization_boundary_audit",
        "parameters": {
            "direct_pattern": "low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_*_probe.json",
            "fresh_pattern": "low_term_total2_ffe_public_factor_quadratic_root_fresh_*_expanded_probe.json",
            "p954_family_marker": "selector contains low_term_support",
            "post_min": int(args.post_min),
            "target": args.target,
        },
        "p954_family_boundary": {
            "direct_p954_family_selected_below_rho_verified_count": direct_summary.get(
                "p954_family_selected_below_rho_verified_count"
            ),
            "fresh_post1144_target_policy_row_count": fresh_summary.get("target_policy_row_count"),
            "p954_frozen_family_post1144_status": p954_status,
            "selected_below_rho_verified_count_all_families": direct_summary.get(
                "selected_below_rho_verified_count"
            ),
        },
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=DEFAULT_POST_MIN)
    parser.add_argument("--best-limit", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    direct = payload["direct_gate_summary"]
    fresh = payload["fresh_stream_summary"]
    boundary = payload["p954_family_boundary"]
    print(
        f"claim={payload['claim_status']} "
        f"fresh_target_rows={fresh['target_policy_row_count']} "
        f"direct_artifacts={direct['artifact_count']} "
        f"target_cases={direct['target_case_count']} "
        f"selected={direct['selected_direct_verified_count']} "
        f"selected_below={direct['selected_below_rho_verified_count']} "
        f"selected_unverified={direct['selected_unverified_count']} "
        f"p954_family_selected_below={boundary['direct_p954_family_selected_below_rho_verified_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
