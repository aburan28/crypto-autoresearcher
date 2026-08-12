#!/usr/bin/env python3
"""Gate branch-family duplicate hits by target-eliminated support novelty.

The duplicate-hit selector is good at finding rank-2 local relation stops, but
some stops repeat the same target-eliminated factor relation.  This scout asks a
narrower index-calculus question: before using a derived-secret label, do the
public compact hit forms imply a factor-only relation that is new relative to an
existing certificate bank?

This is a post-hit, pre-rank diagnostic.  It is still toy-prime and model-bound:
it operates inside the verifier's current factor-column namespace and does not
implement fresh-target descent.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
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


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
        "sum": round(sum(values), 8),
    }


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


def relation_key(relation: dict[str, Any], factor_count: int, order: int) -> tuple[tuple[int, ...], int]:
    coeffs = [int_value(value) % order for value in relation.get("canonical_coeffs") or []]
    coeffs = coeffs + [0] * max(0, factor_count - len(coeffs))
    return tuple(coeffs[:factor_count]), int_value(relation.get("canonical_rhs")) % order


def relation_keys_for_certificates(
    certificates: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> set[tuple[tuple[int, ...], int]]:
    keys: set[tuple[tuple[int, ...], int]] = set()
    for cert in certificates:
        if int_value(cert.get("order")) != order:
            continue
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            keys.add(relation_key(relation, factor_count, order))
    return keys


def iter_attempts(paths: list[Path]) -> list[tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for path in paths:
        payload = load_json(path)
        for group in payload.get("groups") or []:
            if not isinstance(group, dict):
                continue
            for attempt in group.get("attempts") or []:
                if isinstance(attempt, dict):
                    rows.append((path, payload, group, attempt))
    return rows


def branch_results_by_key(attempt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = [
        result
        for result in attempt.get("branch_results") or []
        if isinstance(result, dict)
    ]
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


def candidate_for_branch(
    path: Path,
    group: dict[str, Any],
    attempt: dict[str, Any],
    branch_key: str,
    branch_result: dict[str, Any] | None,
    base_keys: set[tuple[tuple[int, ...], int]],
    order: int,
    factor_count: int,
    min_forms: int,
) -> dict[str, Any] | None:
    hits = branch_exporter.unique_hits_for_branch(attempt, branch_key)
    if len(hits) < min_forms:
        return None
    forms = [branch_exporter.form_from_hit(hit, order, factor_count) for hit in hits]
    cert = {
        "forms": forms,
        "order": order,
        "selected": {
            "target": "22050.cf1@11731",
            "transfer_index": int_value(attempt.get("transfer_index")),
            "window": group.get("window"),
        },
    }
    relations = [
        relation
        for relation in factor_bank.target_eliminated_rows(cert)
        if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"
    ]
    keys = [relation_key(relation, factor_count, order) for relation in relations]
    new_keys = [key for key in keys if key not in base_keys]
    supports = [
        sorted(int(index) for index in relation.get("factor_support") or [])
        for relation in relations
    ]
    new_supports = [
        supports[index]
        for index, key in enumerate(keys)
        if key not in base_keys
    ]
    verified_rank2 = bool(
        branch_result
        and branch_result.get("public_key_verified")
        and int_value(branch_result.get("rank")) >= 2
    )
    return {
        "artifact": str(path),
        "branch_key": branch_key,
        "derived_secret": (branch_result or {}).get("derived_secret"),
        "forms_count": len(forms),
        "new_relation_count": len(new_keys),
        "new_relation_keys": [
            {"canonical_coeffs": list(coeffs), "canonical_rhs": rhs}
            for coeffs, rhs in new_keys
        ],
        "new_supports": new_supports,
        "public_key_verified_rank2": verified_rank2,
        "rank": int_value((branch_result or {}).get("rank")),
        "relation_count": len(relations),
        "selected": len(new_keys) > 0,
        "supports": supports,
        "transfer_index": int_value(attempt.get("transfer_index")),
        "window": group.get("window"),
    }


def build_candidates(
    sweep_paths: list[Path],
    base_keys: set[tuple[tuple[int, ...], int]],
    order: int,
    factor_count: int,
    min_forms: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path, _payload, group, attempt in iter_attempts(sweep_paths):
        branch_keys = sorted({str(hit.get("branch_key")) for hit in attempt.get("hit_records") or []})
        results = branch_results_by_key(attempt)
        for branch_key in branch_keys:
            candidate = candidate_for_branch(
                path,
                group,
                attempt,
                branch_key,
                results.get(branch_key),
                base_keys,
                order,
                factor_count,
                min_forms,
            )
            if candidate is not None:
                candidates.append(candidate)
    candidates.sort(
        key=lambda item: (
            -int_value(item.get("new_relation_count")),
            not bool(item.get("public_key_verified_rank2")),
            int_value(item.get("transfer_index")),
            str(item.get("branch_key")),
        )
    )
    return candidates


def summarize(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [candidate for candidate in candidates if candidate.get("selected")]
    verified = [candidate for candidate in candidates if candidate.get("public_key_verified_rank2")]
    selected_verified = [candidate for candidate in selected if candidate.get("public_key_verified_rank2")]
    missed_verified = [candidate for candidate in verified if not candidate.get("selected")]
    false_selected = [candidate for candidate in selected if not candidate.get("public_key_verified_rank2")]
    branch_counts = Counter(str(candidate.get("branch_key")) for candidate in selected)
    return {
        "candidate_count": len(candidates),
        "false_selected_count": len(false_selected),
        "missed_verified_rank2_count": len(missed_verified),
        "new_relation_count": sum(int_value(candidate.get("new_relation_count")) for candidate in selected),
        "selected_branch_counts": dict(sorted(branch_counts.items())),
        "selected_count": len(selected),
        "selected_new_relation_count": stat([int_value(candidate.get("new_relation_count")) for candidate in selected]),
        "selected_verified_rank2_count": len(selected_verified),
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
    base_keys = relation_keys_for_certificates(base_certificates, args.order, args.factor_count)
    candidates = build_candidates(sweep_paths, base_keys, args.order, args.factor_count, args.min_forms)
    summary = summarize(candidates)
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "sweep_artifacts": [str(path) for path in sweep_paths],
        },
        "base_relation_count": len(base_keys),
        "candidates": candidates,
        "claim_status": (
            "SUPPORT_NOVELTY_GATE_SELECTS_RANK_FRONTIER_CANDIDATES"
            if summary["selected_verified_rank2_count"]
            else "SUPPORT_NOVELTY_GATE_SELECTS_ONLY_UNVERIFIED_OR_NONE"
            if summary["selected_count"]
            else "SUPPORT_NOVELTY_GATE_NO_NEW_RELATIONS"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: support novelty is measured in the current order-specific factor-column namespace.",
            "HEURISTIC: this is a post-hit rank-frontier gate, not a pre-row-scan scheduler and not target descent.",
            "OPEN: a complete improvement still needs pre-setup prediction and enough independent factor rank for fresh-target recovery.",
        ],
        "parameters": {
            "factor_count": args.factor_count,
            "min_forms": args.min_forms,
            "order": args.order,
        },
        "schema": "ecdlp.low_term_total2_branch_family_support_novelty_gate_scout.v1",
        "selected_candidates": [candidate for candidate in candidates if candidate.get("selected")],
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
