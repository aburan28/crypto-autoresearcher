#!/usr/bin/env python3
"""P708 ordered stop-after-first selector audit.

P707 charged every descriptor-matching heldout certificate.  This audit tests a
bounded ordered policy: train public feature-value priorities without the
heldout artifact, select matching heldout certificates, sort by feature priority
and public direct charge, and charge only the first selected certificate.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p707_public_certificate_selector_cost as p707


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p708_ordered_stop_first_selector_probe.json"
DEFAULT_P707 = STATE_DIR / "low_term_total2_p707_public_certificate_selector_cost_probe.json"
DEFAULT_P705 = p707.DEFAULT_P705
DEFAULT_CERT_GLOB = p707.DEFAULT_CERT_GLOB


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p707.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p707.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def first_selection_for_holdout(
    heldout_candidates: list[dict[str, Any]],
    training_candidates: list[dict[str, Any]],
    feature_family: str,
    top_n: int,
) -> dict[str, Any] | None:
    stats = p707.feature_stats(training_candidates, feature_family)
    ranked_values = {str(item["value"]): rank for rank, item in enumerate(stats[:top_n])}
    selected = [
        candidate
        for candidate in heldout_candidates
        if candidate["features"].get(feature_family) in ranked_values
    ]
    if not selected:
        return None
    selected.sort(
        key=lambda candidate: (
            ranked_values[str(candidate["features"].get(feature_family))],
            float_value(candidate.get("cost_over_rho")),
            int_value(candidate.get("certificate_index")),
        )
    )
    chosen = selected[0]
    return {
        "candidate_pool_count": len(selected),
        "chosen": chosen,
        "feature_rank": ranked_values[str(chosen["features"].get(feature_family))],
        "feature_value": chosen["features"].get(feature_family),
    }


def evaluate_policy(
    candidates_by_artifact: dict[str, list[dict[str, Any]]],
    feature_family: str,
    top_n: int,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    heldout_count = len(candidates_by_artifact)
    hit_count = 0
    selected_charge = 0.0
    fallback_charge = 0.0
    selected_pool_total = 0
    samples = []
    misses = []
    for artifact, heldout_candidates in sorted(candidates_by_artifact.items()):
        training = [
            candidate
            for other_artifact, candidates in candidates_by_artifact.items()
            if other_artifact != artifact
            for candidate in candidates
        ]
        selected = first_selection_for_holdout(heldout_candidates, training, feature_family, top_n)
        if selected is None:
            fallback_charge += 1.0
            if len(misses) < sample_limit:
                misses.append(artifact)
            continue
        hit_count += 1
        chosen = selected["chosen"]
        charge = float_value(chosen.get("cost_over_rho"))
        selected_charge += charge
        selected_pool_total += int_value(selected.get("candidate_pool_count"))
        if len(samples) < sample_limit:
            samples.append(
                {
                    "artifact": artifact,
                    "candidate_pool_count": selected["candidate_pool_count"],
                    "chosen_cost_over_rho": round(charge, 8),
                    "expected_secret": chosen.get("expected_secret"),
                    "feature_rank": selected["feature_rank"],
                    "feature_value": selected["feature_value"],
                    "selected": chosen["selected"],
                }
            )
    solved_total = factor_charge + selected_charge
    fallback_total = factor_charge + selected_charge + fallback_charge
    return {
        "beats_rho_on_hit_set": bool(hit_count and solved_total < hit_count),
        "beats_rho_with_fallback": bool(heldout_count and fallback_total < heldout_count),
        "candidate_pool_total": selected_pool_total,
        "feature_family": feature_family,
        "hit_count": hit_count,
        "hit_rate": round(hit_count / heldout_count, 8) if heldout_count else 0.0,
        "heldout_count": heldout_count,
        "missed_artifact_samples": misses,
        "policy": f"{feature_family}:top{top_n}:ordered_stop_first",
        "sample_selections": samples,
        "selected_charge_per_hit_over_rho": round(selected_charge / hit_count, 8) if hit_count else None,
        "selected_charge_total_over_rho": round(selected_charge, 8),
        "selected_with_fallback_total_over_rho": round(fallback_total, 8),
        "solved_total_charge_over_rho": round(solved_total, 8),
        "solved_total_per_hit_over_rho": round(solved_total / hit_count, 8) if hit_count else None,
        "top_n": top_n,
        "vs_independent_rho_hit_set_over_rho": hit_count,
        "vs_independent_rho_with_fallback_over_rho": heldout_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]]) -> str:
    if any(
        report["beats_rho_with_fallback"] and float_value(report["hit_rate"]) >= 0.5
        for report in policy_reports
    ):
        return "P708_ORDERED_PUBLIC_SELECTOR_AMORTIZED_BELOW_RHO_WITH_FALLBACK"
    if any(
        report["beats_rho_on_hit_set"] and float_value(report["hit_rate"]) >= 0.5
        for report in policy_reports
    ):
        return "P708_ORDERED_PUBLIC_SELECTOR_HIT_SET_BELOW_RHO_ONLY"
    if any(report["hit_count"] for report in policy_reports):
        return "P708_ORDERED_PUBLIC_SELECTOR_RECALL_WITH_COST_OPEN"
    return "NEGATIVE_RESULT_P708_NO_ORDERED_PUBLIC_SELECTOR_RECALL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p705 = load_json(Path(args.p705))
    factor_charge = float_value((p705.get("summary") or {}).get("factor_bank_charge_over_rho"), 0.992)
    paths = [Path(path) for path in sorted(glob.glob(args.certificate_glob))]
    candidates = p707.load_candidates(paths)
    by_artifact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_artifact[candidate["artifact"]].append(candidate)
    feature_families = sorted({
        family
        for candidate in candidates
        for family in candidate.get("features", {})
    })
    top_values = p707.parse_top_values(args.top_values)
    reports = [
        evaluate_policy(by_artifact, family, top_n, factor_charge, int_value(args.sample_limit))
        for family in feature_families
        for top_n in top_values
    ]
    reports.sort(
        key=lambda report: (
            not bool(report["beats_rho_with_fallback"]),
            -float_value(report["hit_rate"]),
            float_value(report.get("selected_with_fallback_total_over_rho"), 999999.0)
            / max(1, int_value(report.get("heldout_count"))),
            float_value(report.get("selected_charge_per_hit_over_rho"), 999999.0),
            str(report["policy"]),
        )
    )
    best = reports[0] if reports else None
    claim_status = determine_claim(reports)
    return {
        "artifacts": {
            "certificate_glob": args.certificate_glob,
            "p705": str(Path(args.p705)),
            "p707": str(Path(args.p707)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: ordered selector validation is offline over archived direct-certificate artifacts.",
            "HEURISTIC: stop-after-first assumes the first archived selected certificate is obtainable by the same public descriptor path in fresh runs.",
            "NO FRESH SOURCE-GENERATION THEOREM: this is a selector-cost audit, not an asymptotic ECDLP algorithm.",
        ],
        "method": "p708_ordered_stop_first_selector",
        "parameters": {
            "factor_bank_charge_over_rho": factor_charge,
            "feature_family_count": len(feature_families),
            "top_values": top_values,
        },
        "policy_reports": reports,
        "schema": "ecdlp.low_term_total2_p708_ordered_stop_first_selector.v1",
        "summary": {
            "artifact_count": len(by_artifact),
            "best_policy": None if best is None else best["policy"],
            "best_policy_beats_rho_with_fallback": None if best is None else best["beats_rho_with_fallback"],
            "best_policy_hit_rate": None if best is None else best["hit_rate"],
            "best_policy_selected_with_fallback_total_over_rho": (
                None if best is None else best["selected_with_fallback_total_over_rho"]
            ),
            "candidate_count": len(candidates),
            "factor_bank_charge_over_rho": factor_charge,
            "policy_count": len(reports),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate-glob", default=DEFAULT_CERT_GLOB)
    parser.add_argument("--p705", default=str(DEFAULT_P705))
    parser.add_argument("--p707", default=str(DEFAULT_P707))
    parser.add_argument("--top-values", default="1,3,5,10")
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy": payload["policy_reports"][:1]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
