#!/usr/bin/env python3
"""P709 source replay without an archive-candidate oracle.

P708 ordered archived certificates and charged only the first selected
certificate.  This audit applies the same leave-one-artifact-out descriptor
priority directly to the held-out source rows.  Selection ignores source
verification labels and archived passing-certificate membership; verification is
performed only after the source row is selected.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_direct_source_relation_equation_certificate as direct_source
import low_term_total2_p707_public_certificate_selector_cost as p707


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
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


def parse_int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def first_source_for_artifact(path: Path, target: str) -> str | None:
    payload = load_json(path)
    for cert in payload.get("certificates") or []:
        if int_value(cert.get("order")) != p707.ORDER:
            continue
        selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
        if target and str(selected.get("target")) != target:
            continue
        source = cert.get("source")
        if source:
            return str(source)
    return None


def candidate_training_pool(
    candidates_by_artifact: dict[str, list[dict[str, Any]]],
    heldout_artifact: str,
) -> list[dict[str, Any]]:
    return [
        candidate
        for artifact, candidates in candidates_by_artifact.items()
        if artifact != heldout_artifact
        for candidate in candidates
    ]


def ranked_feature_values(
    training_candidates: list[dict[str, Any]],
    feature_family: str,
    top_n: int,
) -> dict[str, int]:
    stats = p707.feature_stats(training_candidates, feature_family)
    return {str(item["value"]): rank for rank, item in enumerate(stats[:top_n])}


def row_features(row: dict[str, Any]) -> dict[str, str]:
    return p707.candidate_features(
        {
            "row_keys": row.get("row_keys") or [],
            "selector": row.get("selector"),
            "target": row.get("target"),
            "top_k": int_value(row.get("top_k")),
            "transfer_index": int_value(row.get("transfer_index")),
        }
    )


def source_rows(
    source: dict[str, Any],
    source_path: Path,
    target: str,
    feature_family: str,
    feature_ranks: dict[str, int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for policy_name, policy in (source.get("policies") or {}).items():
        if not isinstance(policy, dict):
            continue
        row_selector = (policy.get("row_selector") or {}).get("selector")
        for row_index, row in enumerate(policy.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            if target and str(row.get("target")) != target:
                continue
            features = row_features(row)
            feature_value = features.get(feature_family)
            if feature_value not in feature_ranks:
                continue
            source_case = {
                **row,
                "source_policy": policy_name,
                "source_row_index": row_index,
                "row_selector": row.get("row_selector") or row_selector,
            }
            key = (
                source_case.get("target"),
                int_value(source_case.get("transfer_index")),
                source_case.get("selector"),
                int_value(source_case.get("top_k")),
                tuple(str(item) for item in source_case.get("row_keys") or []),
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "feature_rank": feature_ranks[str(feature_value)],
                    "feature_value": feature_value,
                    "features": features,
                    "ops_over_rho": float_value(row.get("ops_over_rho"), 999999.0),
                    "source": str(source_path),
                    "source_case": source_case,
                    "source_public_key_verified_label": bool(row.get("public_key_verified")),
                    "source_source_verified_label": bool(row.get("source_verified")),
                }
            )
    rows.sort(
        key=lambda item: (
            int_value(item.get("feature_rank")),
            float_value(item.get("ops_over_rho"), 999999.0),
            int_value((item.get("source_case") or {}).get("transfer_index")),
            str((item.get("source_case") or {}).get("selector")),
            int_value((item.get("source_case") or {}).get("top_k")),
            tuple(str(part) for part in (item.get("source_case") or {}).get("row_keys") or []),
        )
    )
    return rows


def certificate_for_source_case(source: dict[str, Any], source_path: Path, source_case: dict[str, Any]) -> dict[str, Any]:
    verifier, contexts, product_factor, _max_relations = direct_source.timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows, direct_ops, rho, _row_profiles = direct_source.timing_probe.direct_witness_rows(
        verifier,
        contexts,
    )
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = direct_source.direct_witness_probe.union_derive(verifier, direct_rows, built_by_row, "_scan")
    if not contexts:
        raise ValueError(
            "no selected contexts for "
            f"{source_case.get('target')} {source_case.get('transfer_index')} "
            f"{source_case.get('selector')} top{source_case.get('top_k')}"
        )
    order = int(contexts[0]["built"]["order"])
    events = direct_source.direct_unique_events(direct_rows)
    public_key_verified = bool(direct_union.get("union_public_key_verified"))
    derived_secret = direct_union.get("union_derived_secret")
    return {
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if public_key_verified
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW"
        ),
        "clause": "direct_source",
        "derived_secret": derived_secret,
        "expected_secret": derived_secret if public_key_verified else None,
        "forms_count": len(events),
        "order": order,
        "product_factor": product_factor,
        "public_key_verified": public_key_verified,
        "rank": int_value(direct_union.get("union_rank")),
        "scan_row_count": len(direct_rows),
        "selected": {
            "clause": "direct_source",
            "direct_ops": direct_ops,
            "direct_ops_over_rho": direct_source.ratio(direct_ops, rho),
            "rho": rho,
            "row_keys": source_case.get("row_keys") or [],
            "secret": derived_secret if public_key_verified else None,
            "selector": source_case.get("selector"),
            "shared_ops": None,
            "shared_ops_over_rho": None,
            "target": source_case.get("target"),
            "top_k": int_value(source_case.get("top_k")),
            "transfer_index": int_value(source_case.get("transfer_index")),
        },
        "source": str(source_path),
        "source_case_selector": {
            "selector": source_case.get("selector"),
            "source_policy": source_case.get("source_policy"),
            "source_row_index": int_value(source_case.get("source_row_index")),
            "target": source_case.get("target"),
            "top_k": int_value(source_case.get("top_k")),
            "transfer_index": int_value(source_case.get("transfer_index")),
        },
    }


def compact_attempt(attempt_index: int, row: dict[str, Any], cert: dict[str, Any] | None, error: str | None) -> dict[str, Any]:
    source_case = row.get("source_case") or {}
    selected = (cert or {}).get("selected") or {}
    return {
        "attempt_index": attempt_index,
        "direct_ops_over_rho": selected.get("direct_ops_over_rho", row.get("ops_over_rho")),
        "error": error,
        "feature_rank": int_value(row.get("feature_rank")),
        "feature_value": row.get("feature_value"),
        "forms_count": (cert or {}).get("forms_count"),
        "rank": (cert or {}).get("rank"),
        "relation_count": int_value(source_case.get("relation_count")),
        "replay_public_key_verified": bool((cert or {}).get("public_key_verified")),
        "row_keys": source_case.get("row_keys") or [],
        "row_selector": source_case.get("row_selector"),
        "selector": source_case.get("selector"),
        "selected_leaf_count": int_value(source_case.get("selected_leaf_count")),
        "selected_row_count": int_value(source_case.get("selected_row_count")),
        "source_public_key_verified_label": bool(row.get("source_public_key_verified_label")),
        "source_policy": source_case.get("source_policy"),
        "source_row_index": int_value(source_case.get("source_row_index")),
        "source_verified_label": bool(row.get("source_source_verified_label")),
        "target": source_case.get("target"),
        "top_k": int_value(source_case.get("top_k")),
        "transfer_index": int_value(source_case.get("transfer_index")),
    }


def replay_artifact(
    artifact: str,
    source_path: Path,
    source: dict[str, Any],
    feature_ranks: dict[str, int],
    args: argparse.Namespace,
) -> dict[str, Any]:
    rows = source_rows(source, source_path, args.target, args.feature_family, feature_ranks)
    max_attempt = max(parse_int_list(args.attempt_budgets), default=1)
    attempts = []
    for index, row in enumerate(rows[:max_attempt], start=1):
        cert = None
        error = None
        try:
            cert = certificate_for_source_case(source, source_path, row["source_case"])
        except Exception as exc:  # noqa: BLE001 - preserve verifier failure in artifact.
            error = f"{type(exc).__name__}: {exc}"
        attempts.append(compact_attempt(index, row, cert, error))
    return {
        "artifact": artifact,
        "attempts": attempts,
        "ordered_source_candidate_count": len(rows),
        "source": str(source_path),
    }


def first_hit_within(report: dict[str, Any], budget: int) -> tuple[dict[str, Any] | None, float]:
    charge = 0.0
    for attempt in report.get("attempts") or []:
        if int_value(attempt.get("attempt_index")) > budget:
            break
        charge += float_value(attempt.get("direct_ops_over_rho"))
        if attempt.get("replay_public_key_verified"):
            return attempt, charge
    return None, charge


def budget_report(artifact_reports: list[dict[str, Any]], budget: int, factor_charge: float) -> dict[str, Any]:
    hit_count = 0
    attempted_charge = 0.0
    fallback_charge = 0.0
    no_candidate_count = 0
    replay_error_count = 0
    hit_samples = []
    miss_samples = []
    for report in artifact_reports:
        attempts = report.get("attempts") or []
        if not attempts:
            no_candidate_count += 1
        replay_error_count += sum(1 for attempt in attempts[:budget] if attempt.get("error"))
        hit, charge = first_hit_within(report, budget)
        attempted_charge += charge
        if hit:
            hit_count += 1
            if len(hit_samples) < 6:
                hit_samples.append(
                    {
                        "artifact": report.get("artifact"),
                        "attempt": hit,
                        "source": report.get("source"),
                    }
                )
        else:
            fallback_charge += 1.0
            if len(miss_samples) < 6:
                miss_samples.append(
                    {
                        "artifact": report.get("artifact"),
                        "attempt_count": min(len(attempts), budget),
                        "ordered_source_candidate_count": report.get("ordered_source_candidate_count"),
                        "source": report.get("source"),
                    }
                )
    artifact_count = len(artifact_reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "attempt_budget": budget,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(artifact_count and total < artifact_count),
        "factor_bank_charge_over_rho": round(factor_charge, 8),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / artifact_count, 8) if artifact_count else 0.0,
        "hit_samples": hit_samples,
        "miss_samples": miss_samples,
        "no_candidate_count": no_candidate_count,
        "replay_error_count": replay_error_count,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "source_replay_total_per_artifact_over_rho": round(total / artifact_count, 8) if artifact_count else None,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "vs_independent_rho_with_fallback_over_rho": artifact_count,
    }


def determine_claim(budget_reports: list[dict[str, Any]]) -> str:
    if any(
        report["beats_rho_with_fallback"] and float_value(report["hit_rate"]) >= 0.5
        for report in budget_reports
    ):
        return "P709_SOURCE_REPLAY_NO_ARCHIVE_ORACLE_BELOW_RHO_WITH_FALLBACK"
    if any(
        report["beats_rho_on_hit_set"] and float_value(report["hit_rate"]) >= 0.5
        for report in budget_reports
    ):
        return "P709_SOURCE_REPLAY_HIT_SET_BELOW_RHO_ONLY"
    if any(report["hit_count"] for report in budget_reports):
        return "NEGATIVE_RESULT_P709_SOURCE_REPLAY_RECALL_COST_ABOVE_RHO"
    return "NEGATIVE_RESULT_P709_NO_SOURCE_REPLAY_VERIFIED_HITS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p705 = load_json(Path(args.p705))
    factor_charge = float_value((p705.get("summary") or {}).get("factor_bank_charge_over_rho"), 0.992)
    paths = [Path(path) for path in sorted(glob.glob(args.certificate_glob))]
    if args.artifact_limit:
        paths = paths[: int_value(args.artifact_limit)]
    candidates = p707.load_candidates(paths)
    candidates_by_artifact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        candidates_by_artifact[candidate["artifact"]].append(candidate)
    artifact_reports = []
    missing_sources = []
    for path in paths:
        artifact = str(path)
        source_name = first_source_for_artifact(path, args.target)
        if not source_name:
            missing_sources.append(artifact)
            continue
        source_path = Path(source_name)
        source = load_json(source_path)
        if not source:
            missing_sources.append(artifact)
            continue
        training = candidate_training_pool(candidates_by_artifact, artifact)
        feature_ranks = ranked_feature_values(training, args.feature_family, int_value(args.top_n))
        artifact_reports.append(replay_artifact(artifact, source_path, source, feature_ranks, args))
    budgets = parse_int_list(args.attempt_budgets)
    reports = [budget_report(artifact_reports, budget, factor_charge) for budget in budgets]
    reports.sort(
        key=lambda report: (
            not bool(report["beats_rho_with_fallback"]),
            float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0),
            -float_value(report.get("hit_rate")),
            int_value(report.get("attempt_budget")),
        )
    )
    best = reports[0] if reports else None
    claim_status = determine_claim(reports)
    return {
        "artifact_reports": artifact_reports,
        "artifacts": {
            "certificate_glob": args.certificate_glob,
            "p705": str(Path(args.p705)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows are replayed from archived source artifacts, not regenerated by a new live harvester.",
            "NO ARCHIVE-CANDIDATE ORACLE: selection orders held-out source rows before verification and does not use archived passing-certificate membership.",
            "HEURISTIC: this tests a concrete source-row replay gate for the P708 selector, not an asymptotic index-calculus theorem.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p709_source_replay_no_archive_oracle",
        "missing_source_artifacts": missing_sources,
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "feature_family": args.feature_family,
            "target": args.target,
            "top_n": int_value(args.top_n),
        },
        "policy_reports": reports,
        "schema": "ecdlp.low_term_total2_p709_source_replay_no_archive_oracle.v1",
        "summary": {
            "artifact_count": len(artifact_reports),
            "best_attempt_budget": None if best is None else best["attempt_budget"],
            "best_hit_count": None if best is None else best["hit_count"],
            "best_hit_rate": None if best is None else best["hit_rate"],
            "best_source_replay_total_with_fallback_over_rho": (
                None if best is None else best["source_replay_total_with_fallback_over_rho"]
            ),
            "certificate_artifact_count": len(paths),
            "missing_source_artifact_count": len(missing_sources),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-limit", type=int, default=0)
    parser.add_argument("--attempt-budgets", default="1,2,4,8")
    parser.add_argument("--certificate-glob", default=DEFAULT_CERT_GLOB)
    parser.add_argument("--feature-family", default="top_k")
    parser.add_argument("--p705", default=str(DEFAULT_P705))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy_reports": payload["policy_reports"][:4]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
