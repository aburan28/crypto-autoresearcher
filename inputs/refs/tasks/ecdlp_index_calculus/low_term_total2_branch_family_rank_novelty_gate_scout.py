#!/usr/bin/env python3
"""Gate branch-family duplicate hits by marginal factor-row rank.

The support-novelty gate asks whether a duplicate-hit stop emits a new
target-eliminated relation key.  Fresh validation showed that a new key can
still be linearly dependent.  This scout asks the stricter post-hit question:
does the candidate increase the rank of the current target-eliminated factor
rowspace?

This is still a toy-prime, model-bound diagnostic.  It is a rank-frontier
collector objective, not target descent and not a deployed-curve speedup claim.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_branch_family_certificate_exporter as branch_exporter
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


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


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def branch_results_by_key(attempt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = [item for item in attempt.get("branch_results") or [] if isinstance(item, dict)]
    best = attempt.get("best_branch")
    if isinstance(best, dict):
        results.append(best)
    by_key: dict[str, dict[str, Any]] = {}
    for result in results:
        key = str(result.get("branch_key"))
        current = by_key.get(key)
        if current is None or int_value(result.get("rank")) > int_value(current.get("rank")):
            by_key[key] = result
    return by_key


def relation_summaries(cert: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        rows.append(
            {
                "canonical_coeffs": relation.get("canonical_coeffs"),
                "canonical_rhs": relation.get("canonical_rhs"),
                "factor_support": relation.get("factor_support"),
                "factor_support_size": relation.get("factor_support_size"),
                "pair": relation.get("pair"),
            }
        )
    return rows


def build_candidate_certificates(
    sweep_paths: list[Path],
    order: int,
    factor_count: int,
    min_forms: int,
) -> list[dict[str, Any]]:
    certificates: list[dict[str, Any]] = []
    for path in sweep_paths:
        payload = load_json(path)
        for group in payload.get("groups") or []:
            if not isinstance(group, dict):
                continue
            for attempt in group.get("attempts") or []:
                if not isinstance(attempt, dict):
                    continue
                branch_keys = sorted({str(hit.get("branch_key")) for hit in attempt.get("hit_records") or []})
                results = branch_results_by_key(attempt)
                for branch_key in branch_keys:
                    hits = branch_exporter.unique_hits_for_branch(attempt, branch_key)
                    if len(hits) < min_forms:
                        continue
                    forms = [branch_exporter.form_from_hit(hit, order, factor_count) for hit in hits]
                    result = results.get(branch_key) or {}
                    selected = {
                        "branch_key": branch_key,
                        "clause": "branch_family_rank_novelty",
                        "target": "22050.cf1@11731",
                        "transfer_index": int_value(attempt.get("transfer_index")),
                        "window": group.get("window"),
                    }
                    cert = {
                        "_artifact": str(path),
                        "_artifact_offset": len(certificates),
                        "_global_index": len(certificates),
                        "branch_key": branch_key,
                        "clause": "branch_family_rank_novelty",
                        "derived_secret": result.get("derived_secret"),
                        "forms": forms,
                        "forms_count": len(forms),
                        "order": order,
                        "public_key_verified_rank2": bool(
                            result.get("public_key_verified") and int_value(result.get("rank")) >= 2
                        ),
                        "rank": int_value(result.get("rank")),
                        "selected": selected,
                        "transfer_index": int_value(attempt.get("transfer_index")),
                        "window": group.get("window"),
                    }
                    cert["target_eliminated_relations"] = relation_summaries(cert)
                    certificates.append(cert)
    return certificates


def rank_summary(base: list[dict[str, Any]], order: int) -> dict[str, Any]:
    if not base:
        return {
            "deficiency": 0,
            "rank": 0,
            "unique_factor_relation_count": 0,
        }
    return factor_bank.audit_order(base, order)


def score_candidates(
    base_certificates: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    order: int,
) -> list[dict[str, Any]]:
    base_order = rank_summary(base_certificates, order)
    scores: list[dict[str, Any]] = []
    for cert in candidates:
        after_order = factor_bank.audit_order(base_certificates + [cert], order)
        rank_gain = int_value(after_order.get("rank")) - int_value(base_order.get("rank"))
        unique_gain = int_value(after_order.get("unique_factor_relation_count")) - int_value(
            base_order.get("unique_factor_relation_count")
        )
        deficiency_delta = int_value(after_order.get("deficiency")) - int_value(base_order.get("deficiency"))
        scores.append(
            {
                "artifact": cert.get("_artifact"),
                "branch_key": cert.get("branch_key"),
                "claim_status": (
                    "MARGINAL_FACTOR_RANK_GAIN"
                    if rank_gain > 0
                    else "DEPENDENT_NEW_FACTOR_RELATION"
                    if unique_gain > 0
                    else "NO_NEW_FACTOR_RELATION"
                ),
                "deficiency_delta": deficiency_delta,
                "derived_secret": cert.get("derived_secret"),
                "forms_count": int_value(cert.get("forms_count")),
                "public_key_verified_rank2": bool(cert.get("public_key_verified_rank2")),
                "rank": int_value(cert.get("rank")),
                "rank_after": int_value(after_order.get("rank")),
                "rank_before": int_value(base_order.get("rank")),
                "rank_gain": rank_gain,
                "target_eliminated_relations": cert.get("target_eliminated_relations") or [],
                "transfer_index": int_value(cert.get("transfer_index")),
                "unique_factor_relation_count_after": int_value(
                    after_order.get("unique_factor_relation_count")
                ),
                "unique_factor_relation_count_before": int_value(
                    base_order.get("unique_factor_relation_count")
                ),
                "unique_factor_relation_gain": unique_gain,
                "window": cert.get("window"),
            }
        )
    scores.sort(
        key=lambda item: (
            -int_value(item.get("rank_gain")),
            -int_value(item.get("unique_factor_relation_gain")),
            not bool(item.get("public_key_verified_rank2")),
            int_value(item.get("transfer_index")),
            str(item.get("branch_key")),
        )
    )
    return scores


def summarize(scores: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [score for score in scores if int_value(score.get("rank_gain")) > 0]
    verified = [score for score in scores if score.get("public_key_verified_rank2")]
    false_selected = [score for score in selected if not score.get("public_key_verified_rank2")]
    missed_verified = [score for score in verified if int_value(score.get("rank_gain")) <= 0]
    branch_counts = Counter(str(score.get("branch_key")) for score in selected)
    return {
        "candidate_count": len(scores),
        "dependent_unique_gain_candidate_count": sum(
            1
            for score in scores
            if int_value(score.get("rank_gain")) <= 0
            and int_value(score.get("unique_factor_relation_gain")) > 0
        ),
        "false_selected_count": len(false_selected),
        "max_rank_gain": max([int_value(score.get("rank_gain")) for score in scores] or [0]),
        "max_unique_factor_relation_gain": max(
            [int_value(score.get("unique_factor_relation_gain")) for score in scores] or [0]
        ),
        "missed_verified_rank2_count": len(missed_verified),
        "rank_gain_candidate_count": len(selected),
        "selected_branch_counts": dict(sorted(branch_counts.items())),
        "selected_count": len(selected),
        "selected_verified_rank2_count": sum(1 for score in selected if score.get("public_key_verified_rank2")),
        "unique_gain_candidate_count": sum(
            1 for score in scores if int_value(score.get("unique_factor_relation_gain")) > 0
        ),
        "verified_rank2_count": len(verified),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-certificates", required=True)
    parser.add_argument("--sweep-artifacts", required=True)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--factor-count", type=int, default=16)
    parser.add_argument("--min-forms", type=int, default=2)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_paths = parse_paths(args.base_certificates)
    sweep_paths = parse_paths(args.sweep_artifacts)
    base_certificates = factor_bank.load_certificates(base_paths)
    candidates = build_candidate_certificates(sweep_paths, args.order, args.factor_count, args.min_forms)
    scores = score_candidates(base_certificates, candidates, args.order)
    summary = summarize(scores)
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "sweep_artifacts": [str(path) for path in sweep_paths],
        },
        "claim_status": (
            "RANK_NOVELTY_GATE_SELECTS_MARGINAL_RANK_CANDIDATES"
            if summary["selected_verified_rank2_count"]
            else "RANK_NOVELTY_GATE_SELECTS_ONLY_UNVERIFIED_OR_NONE"
            if summary["selected_count"]
            else "RANK_NOVELTY_GATE_NO_MARGINAL_RANK_GAIN"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rank novelty is measured in the current order-specific factor-column namespace.",
            "HEURISTIC: this is a post-hit collector objective, not a pre-setup scheduler.",
            "OPEN: target descent still requires factor-variable derivability or a public fresh-target mapping.",
        ],
        "parameters": {
            "factor_count": args.factor_count,
            "min_forms": args.min_forms,
            "order": args.order,
        },
        "schema": "ecdlp.low_term_total2_branch_family_rank_novelty_gate_scout.v1",
        "scores": scores,
        "selected_candidates": [score for score in scores if int_value(score.get("rank_gain")) > 0],
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
