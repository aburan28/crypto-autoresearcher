#!/usr/bin/env python3
"""P841 held-out global public slice-policy audit.

P840 ruled out simple support-pair predicates.  The quotient/slice branch has a
strong oracle-selected slice-quadratic signal, but the existing public-slice
probe still reports per-surface best public selections.  This audit chooses a
single public rule/top-k policy on calibration surfaces and evaluates that same
policy on held-out surfaces.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PUBLIC_SLICE = (
    STATE_DIR
    / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_slice_predictor_probe.json"
)
DEFAULT_SLICE_QUADRATIC = (
    STATE_DIR
    / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_slice_quadratic_root_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p841_public_slice_policy_holdout_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p841_public_slice_policy_holdout_audit.md"
SCHEMA = "ecdlp.low_term_total2_p841_public_slice_policy_holdout_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def transfer_index(surface: dict[str, Any]) -> int:
    text = str(surface.get("surface_id") or "") + "|" + str(surface.get("challenge_seed") or "")
    match = re.search(r"shared-transfer:(\d+)", text)
    if match:
        return int(match.group(1))
    return 10**9


def selection_key(selection: dict[str, Any]) -> tuple[str, int]:
    return (str(selection["rule"]), int(selection["top_k"]))


def compact_selection(selection: dict[str, Any] | None) -> dict[str, Any] | None:
    if selection is None:
        return None
    keep = [
        "rule",
        "top_k",
        "preserves_selected_root_pairs",
        "same_selected_root_pairs",
        "public_slice_quadratic_beats_rho",
        "public_slice_quadratic_ops",
        "public_slice_quadratic_ops_over_rho",
        "selected_root_pair_count",
        "original_selected_root_pair_count",
        "recovered_root_count",
        "relevant_leaf_evals",
        "factor_zero_leaf_evals",
        "factor_work",
        "quadratic_root_work",
    ]
    return {key: selection.get(key) for key in keep}


def metrics_for(selections: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [
        float(item["public_slice_quadratic_ops_over_rho"])
        for item in selections
        if item.get("public_slice_quadratic_ops_over_rho") is not None
    ]
    preserving = [item for item in selections if item.get("preserves_selected_root_pairs")]
    below = [item for item in selections if item.get("public_slice_quadratic_beats_rho")]
    preserving_below = [
        item
        for item in selections
        if item.get("preserves_selected_root_pairs") and item.get("public_slice_quadratic_beats_rho")
    ]
    missing_pairs = sum(len(item.get("missing_selected_root_pairs") or []) for item in selections)
    return {
        "surface_count": len(selections),
        "preserving_count": len(preserving),
        "below_rho_count": len(below),
        "preserving_below_rho_count": len(preserving_below),
        "same_selected_pair_count": sum(1 for item in selections if item.get("same_selected_root_pairs")),
        "missing_pair_event_count": int(missing_pairs),
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_ops_over_rho": round(min(ratios), 8) if ratios else None,
        "max_ops_over_rho": round(max(ratios), 8) if ratios else None,
        "preserving_rate": ratio(len(preserving), len(selections)),
        "preserving_below_rho_rate": ratio(len(preserving_below), len(selections)),
    }


def split_surfaces(surfaces: list[dict[str, Any]], calibration_fraction: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ordered = sorted(
        surfaces,
        key=lambda surface: (
            transfer_index(surface),
            str(surface.get("target")),
            str(surface.get("surface_id")),
        ),
    )
    split = max(1, min(len(ordered) - 1, round(len(ordered) * float(calibration_fraction))))
    return ordered[:split], ordered[split:]


def selections_by_policy(surfaces: list[dict[str, Any]]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    out: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for surface in surfaces:
        for selection in surface.get("selection_results") or []:
            out[selection_key(selection)].append(selection)
    return out


def surface_selection(surface: dict[str, Any], policy: tuple[str, int]) -> dict[str, Any] | None:
    rule, top_k = policy
    for selection in surface.get("selection_results") or []:
        if str(selection.get("rule")) == rule and int(selection.get("top_k") or -1) == int(top_k):
            return selection
    return None


def summarize_policy_candidates(calibration: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    by_policy = selections_by_policy(calibration)
    candidates = []
    for policy, selections in by_policy.items():
        metrics = metrics_for(selections)
        candidates.append(
            {
                "metrics": metrics,
                "policy": {"rule": policy[0], "top_k": policy[1]},
            }
        )
    candidates.sort(
        key=lambda item: (
            int(item["metrics"]["preserving_below_rho_count"]),
            int(item["metrics"]["preserving_count"]),
            -int(item["metrics"]["missing_pair_event_count"]),
            -(float(item["metrics"]["mean_ops_over_rho"]) if item["metrics"]["mean_ops_over_rho"] is not None else 10**9),
            -int(item["policy"]["top_k"]),
            item["policy"]["rule"],
        ),
        reverse=True,
    )
    return candidates[: int(top_n)]


def oracle_comparison(public_slice: dict[str, Any], slice_quadratic: dict[str, Any]) -> dict[str, Any]:
    public_summary = public_slice["summary"]
    quadratic_summary = slice_quadratic["summary"]
    return {
        "oracle_slice_quadratic_all_hit_below_rho_count": int(
            quadratic_summary["slice_quadratic_all_hit_below_rho_count"]
        ),
        "oracle_slice_quadratic_min_all_hit_ops_over_rho": quadratic_summary[
            "min_slice_quadratic_all_hit_ops_over_rho"
        ],
        "oracle_slice_quadratic_surfaces_with_preserving": int(
            quadratic_summary["surfaces_with_preserving_slice_quadratic"]
        ),
        "public_per_surface_preserving_count": int(public_summary["surfaces_with_public_preserving_selection"]),
        "public_per_surface_below_rho_count": int(public_summary["public_preserving_selection_below_rho_count"]),
        "public_per_surface_min_ops_over_rho": public_summary["min_public_slice_quadratic_ops_over_rho"],
        "surface_count": int(public_summary["surface_count"]),
    }


def determine_claim(heldout_metrics: dict[str, Any]) -> str:
    if int(heldout_metrics["preserving_below_rho_count"]) > 0:
        return "P841_HELDOUT_PUBLIC_SLICE_POLICY_BELOW_RHO_SIGNAL"
    if int(heldout_metrics["preserving_count"]) > 0:
        return "P841_HELDOUT_PUBLIC_SLICE_POLICY_PRESERVES_ABOVE_RHO"
    if int(heldout_metrics["below_rho_count"]) > 0:
        return "P841_HELDOUT_PUBLIC_SLICE_POLICY_CHEAP_BUT_MISSES_ROOTS"
    return "NEGATIVE_RESULT_P841_HELDOUT_PUBLIC_SLICE_POLICY_NO_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    public_slice = load_json(args.public_slice)
    slice_quadratic = load_json(args.slice_quadratic)
    surfaces = [surface for surface in public_slice.get("surfaces") or [] if surface.get("selection_results")]
    calibration, heldout = split_surfaces(surfaces, float(args.calibration_fraction))
    candidates = summarize_policy_candidates(calibration, int(args.top_policy_count))
    if not candidates:
        raise RuntimeError("no public slice policy candidates found")
    selected_policy = candidates[0]["policy"]
    selected_tuple = (str(selected_policy["rule"]), int(selected_policy["top_k"]))
    heldout_rows = []
    heldout_selections = []
    for surface in heldout:
        selection = surface_selection(surface, selected_tuple)
        if selection is None:
            continue
        heldout_selections.append(selection)
        heldout_rows.append(
            {
                "surface_id": surface.get("surface_id"),
                "target": surface.get("target"),
                "row_key": surface.get("row_key"),
                "transfer_index": transfer_index(surface),
                "selection": compact_selection(selection),
                "missing_selected_root_pairs": selection.get("missing_selected_root_pairs") or [],
            }
        )
    heldout_metrics = metrics_for(heldout_selections)
    claim_status = determine_claim(heldout_metrics)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "public_slice_source": str(args.public_slice),
            "script": str(Path(__file__)),
            "slice_quadratic_source": str(args.slice_quadratic),
        },
        "calibration": {
            "fraction": float(args.calibration_fraction),
            "surface_count": len(calibration),
            "transfer_range": [
                min(transfer_index(surface) for surface in calibration),
                max(transfer_index(surface) for surface in calibration),
            ],
            "top_policy_candidates": candidates,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "heldout": {
            "metrics": heldout_metrics,
            "selected_policy": selected_policy,
            "surface_count": len(heldout),
            "surface_results": heldout_rows,
            "transfer_range": [
                min(transfer_index(surface) for surface in heldout),
                max(transfer_index(surface) for surface in heldout),
            ],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "GLOBAL-POLICY GATE: one public rule/top-k policy is chosen on calibration surfaces and reused on heldout surfaces.",
            "NO PER-SURFACE ORACLE: heldout scoring does not choose each surface's best public selection.",
            "SLICE-ORACLE BOUNDARY: oracle slice-quadratic remains a separate diagnostic baseline.",
            "POLLARD-RHO BOUNDARY: this tests a relation-generation subproblem and is not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p841_public_slice_policy_holdout_audit",
        "oracle_comparison": oracle_comparison(public_slice, slice_quadratic),
        "parameters": {
            "calibration_fraction": float(args.calibration_fraction),
            "top_policy_count": int(args.top_policy_count),
        },
        "red_team_handoff": {
            "assumptions": [
                "Chronological transfer-index split is a useful first heldout split for public slice policies.",
                "A single global rule/top-k policy is stricter than per-surface public best selection.",
                "The public-slice artifact's selection_results are sufficient to evaluate heldout policies without rerunning surface materialization.",
            ],
            "failure_modes": [
                "The split is small and toy-scale; a policy can fail here while another feature family might still work.",
                "The selected policy may preserve roots above rho, which is not enough for a promoted relation-generation algorithm.",
                "A below-rho non-preserving policy is a cheap miss, not a useful relation.",
            ],
            "next_concrete_action": (
                "If no heldout preserving-below-rho policy appears, add a public motif feature family or true bivariate factor backend; "
                "if one appears, replicate on disjoint signature banks before residual-gap accounting."
            ),
        },
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-slice", type=Path, default=DEFAULT_PUBLIC_SLICE)
    parser.add_argument("--slice-quadratic", type=Path, default=DEFAULT_SLICE_QUADRATIC)
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
    parser.add_argument("--top-policy-count", type=int, default=8)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "calibration_top_policy": payload["calibration"]["top_policy_candidates"][0],
                "claim_status": payload["claim_status"],
                "heldout_metrics": payload["heldout"]["metrics"],
                "oracle_comparison": payload["oracle_comparison"],
                "selected_policy": payload["heldout"]["selected_policy"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
