#!/usr/bin/env python3
"""P711 relation-count-two source-neighborhood replay.

P710 found that filtering the existing P709 prefix mainly learned abstention.
This scout expands source replay around the only recurring public positive shape:
``mode_low_term_support_total1`` with one selected leaf, one selected row, and
relation-count two.  It replays all matching source rows in the P709-referenced
source artifacts and compares against relaxed/negative-control neighborhoods.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p709_source_replay_no_archive_oracle as p709


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p711_rel2_source_neighborhood_replay_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p709.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p709.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_int_list(raw: str) -> list[int | str]:
    values: list[int | str] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(item if item == "all" else int(item))
    return values


def selector_mode(selector: str | None) -> str:
    return str(selector or "").split("__", 1)[0]


def salt_from_row_key(row_key: str) -> str:
    match = re.search(r":salt(\d+)", row_key)
    return f"salt{match.group(1)}" if match else "unknown"


def row_pair(row_keys: list[Any]) -> str:
    salts = [salt_from_row_key(str(row_key)) for row_key in row_keys]
    return "_".join(sorted(salts)) if salts else "none"


def source_case_key(source_path: Path, row: dict[str, Any]) -> str:
    payload = {
        "row_keys": row.get("row_keys") or [],
        "selector": row.get("selector"),
        "source": str(source_path),
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def source_mapping(p709_payload: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = []
    for report in p709_payload.get("artifact_reports") or []:
        source = report.get("source")
        artifact = report.get("artifact")
        if source and artifact:
            mapping.append({"artifact": artifact, "source": source})
    mapping.sort(key=lambda item: (str(item["source"]), str(item["artifact"])))
    return mapping


def candidate_rows(source: dict[str, Any], source_path: Path, target: str) -> list[dict[str, Any]]:
    rows = []
    seen: set[str] = set()
    for policy_name, policy in (source.get("policies") or {}).items():
        if not isinstance(policy, dict):
            continue
        row_selector = (policy.get("row_selector") or {}).get("selector")
        for row_index, row in enumerate(policy.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            if str(row.get("target")) != target:
                continue
            if selector_mode(row.get("selector")) != "mode_low_term_support_total1":
                continue
            if int_value(row.get("selected_leaf_count")) != 1:
                continue
            if int_value(row.get("selected_row_count")) != 1:
                continue
            source_case = {
                **row,
                "source_policy": policy_name,
                "source_row_index": row_index,
                "row_selector": row.get("row_selector") or row_selector,
            }
            key = source_case_key(source_path, source_case)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "direct_ops_over_rho": float_value(row.get("ops_over_rho"), 999999.0),
                    "key": key,
                    "relation_count": int_value(row.get("relation_count")),
                    "row_pair": row_pair(row.get("row_keys") or []),
                    "source": str(source_path),
                    "source_case": source_case,
                    "source_public_key_verified_label": bool(row.get("public_key_verified")),
                }
            )
    rows.sort(
        key=lambda item: (
            int_value(item.get("relation_count")) != 2,
            float_value(item.get("direct_ops_over_rho"), 999999.0),
            int_value((item.get("source_case") or {}).get("source_row_index")),
            str(item.get("row_pair")),
        )
    )
    return rows


def policy_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "leaf1_rows1_rel2": lambda row: int_value(row.get("relation_count")) == 2,
        "leaf1_rows1_any_relation": lambda row: True,
        "leaf1_rows1_rel0_control": lambda row: int_value(row.get("relation_count")) == 0,
        "leaf1_rows1_rel2_positive_pairs": lambda row: (
            int_value(row.get("relation_count")) == 2
            and row.get("row_pair") in {"salt202_salt205", "salt204_salt209", "salt207_salt208"}
        ),
    }


def replay_candidate(source: dict[str, Any], source_path: Path, row: dict[str, Any]) -> dict[str, Any]:
    cert = p709.certificate_for_source_case(source, source_path, row["source_case"])
    selected = cert.get("selected") or {}
    return {
        "direct_ops_over_rho": selected.get("direct_ops_over_rho", row.get("direct_ops_over_rho")),
        "forms_count": cert.get("forms_count"),
        "rank": cert.get("rank"),
        "relation_count": row.get("relation_count"),
        "replay_public_key_verified": bool(cert.get("public_key_verified")),
        "row_keys": (row.get("source_case") or {}).get("row_keys") or [],
        "row_pair": row.get("row_pair"),
        "row_selector": (row.get("source_case") or {}).get("row_selector"),
        "selector": (row.get("source_case") or {}).get("selector"),
        "source": row.get("source"),
        "source_policy": (row.get("source_case") or {}).get("source_policy"),
        "source_public_key_verified_label": row.get("source_public_key_verified_label"),
        "source_row_index": int_value((row.get("source_case") or {}).get("source_row_index")),
        "top_k": int_value((row.get("source_case") or {}).get("top_k")),
        "transfer_index": int_value((row.get("source_case") or {}).get("transfer_index")),
    }


def build_artifact_reports(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p709_payload = load_json(Path(args.p709))
    mapping = source_mapping(p709_payload)
    source_cache: dict[str, dict[str, Any]] = {}
    candidate_cache: dict[str, list[dict[str, Any]]] = {}
    replay_cache: dict[str, dict[str, Any]] = {}
    replay_errors: dict[str, str] = {}
    for item in mapping:
        source_path = Path(item["source"])
        if str(source_path) not in source_cache:
            source_cache[str(source_path)] = load_json(source_path)
        if str(source_path) not in candidate_cache:
            candidate_cache[str(source_path)] = candidate_rows(source_cache[str(source_path)], source_path, args.target)
    reports = []
    predicates = policy_predicates()
    for item in mapping:
        source_path = Path(item["source"])
        source = source_cache[str(source_path)]
        rows = candidate_cache[str(source_path)]
        policy_rows: dict[str, list[dict[str, Any]]] = {}
        for policy, predicate in predicates.items():
            selected_rows = [row for row in rows if predicate(row)]
            policy_rows[policy] = selected_rows
            for row in selected_rows:
                key = row["key"]
                if key in replay_cache or key in replay_errors:
                    continue
                try:
                    replay_cache[key] = replay_candidate(source, source_path, row)
                except Exception as exc:  # noqa: BLE001 - preserve verifier failure in artifact.
                    replay_errors[key] = f"{type(exc).__name__}: {exc}"
        reports.append(
            {
                "artifact": item["artifact"],
                "policy_candidate_keys": {
                    policy: [row["key"] for row in rows_for_policy]
                    for policy, rows_for_policy in policy_rows.items()
                },
                "source": str(source_path),
            }
        )
    metadata = {
        "candidate_cache_count": sum(len(rows) for rows in candidate_cache.values()),
        "policy_candidate_counts_unique": {
            policy: len({
                key
                for report in reports
                for key in report["policy_candidate_keys"].get(policy, [])
            })
            for policy in predicates
        },
        "replay_cache": replay_cache,
        "replay_error_count": len(replay_errors),
        "replay_errors": replay_errors,
        "source_count": len(source_cache),
    }
    return reports, metadata


def first_hit(
    keys: list[str],
    replay_cache: dict[str, dict[str, Any]],
    budget: int | str,
) -> tuple[dict[str, Any] | None, float, int]:
    selected_keys = keys if budget == "all" else keys[: int_value(budget)]
    charge = 0.0
    attempted = 0
    for key in selected_keys:
        replay = replay_cache.get(key)
        if not replay:
            continue
        attempted += 1
        charge += float_value(replay.get("direct_ops_over_rho"))
        if replay.get("replay_public_key_verified"):
            return replay, charge, attempted
    return None, charge, attempted


def sample_replay(replay: dict[str, Any] | None) -> dict[str, Any] | None:
    if replay is None:
        return None
    return {
        "direct_ops_over_rho": replay.get("direct_ops_over_rho"),
        "forms_count": replay.get("forms_count"),
        "rank": replay.get("rank"),
        "relation_count": replay.get("relation_count"),
        "replay_public_key_verified": replay.get("replay_public_key_verified"),
        "row_keys": replay.get("row_keys"),
        "row_pair": replay.get("row_pair"),
        "row_selector": replay.get("row_selector"),
        "selector": replay.get("selector"),
        "source_policy": replay.get("source_policy"),
        "source_row_index": replay.get("source_row_index"),
        "transfer_index": replay.get("transfer_index"),
    }


def evaluate_policy(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    policy: str,
    budget: int | str,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    hit_count = 0
    attempted_charge = 0.0
    fallback_charge = 0.0
    attempted_count = 0
    no_candidate_count = 0
    samples = []
    misses = []
    for report in reports:
        keys = report["policy_candidate_keys"].get(policy, [])
        if not keys:
            no_candidate_count += 1
        hit, charge, attempted = first_hit(keys, replay_cache, budget)
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(samples) < sample_limit:
                samples.append(
                    {
                        "artifact": report["artifact"],
                        "replay": sample_replay(hit),
                        "source": report["source"],
                    }
                )
        else:
            fallback_charge += 1.0
            if len(misses) < sample_limit:
                misses.append(
                    {
                        "artifact": report["artifact"],
                        "candidate_count": len(keys),
                        "source": report["source"],
                    }
                )
    artifact_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "attempt_budget": budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(artifact_count and total < artifact_count),
        "candidate_absent_artifact_count": no_candidate_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / artifact_count, 8) if artifact_count else 0.0,
        "hit_samples": samples,
        "miss_samples": misses,
        "policy": policy,
        "source_replay_total_per_artifact_over_rho": round(total / artifact_count, 8) if artifact_count else None,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": artifact_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]]) -> str:
    if any(
        report.get("beats_rho_with_fallback") and float_value(report.get("hit_rate")) >= 0.5
        for report in policy_reports
    ):
        return "P711_REL2_SOURCE_NEIGHBORHOOD_BROAD_BELOW_RHO_WITH_FALLBACK"
    if any(report.get("beats_rho_with_fallback") for report in policy_reports):
        return "P711_REL2_SOURCE_NEIGHBORHOOD_SPARSE_BELOW_RHO_WITH_FALLBACK"
    strict = [
        report
        for report in policy_reports
        if report.get("policy") == "leaf1_rows1_rel2" and int_value(report.get("hit_count"))
    ]
    control = [
        report
        for report in policy_reports
        if report.get("policy") == "leaf1_rows1_rel0_control"
    ]
    if strict and control:
        best_strict = min(strict, key=lambda report: float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0))
        best_control = min(control, key=lambda report: float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0))
        if (
            int_value(best_strict.get("hit_count")) > int_value(best_control.get("hit_count"))
            or float_value(best_strict.get("source_replay_total_with_fallback_over_rho"), 999999.0)
            < float_value(best_control.get("source_replay_total_with_fallback_over_rho"), 999999.0)
        ):
            return "P711_REL2_SOURCE_NEIGHBORHOOD_PARTIAL_POSITIVE_STILL_ABOVE_RHO"
    if any(report.get("hit_count") for report in policy_reports):
        return "NEGATIVE_RESULT_P711_SOURCE_NEIGHBORHOOD_HITS_TOO_SPARSE"
    return "NEGATIVE_RESULT_P711_SOURCE_NEIGHBORHOOD_NO_VERIFIED_HITS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    reports, metadata = build_artifact_reports(args)
    budgets = parse_int_list(args.attempt_budgets)
    policies = sorted(policy_predicates())
    policy_reports = [
        evaluate_policy(
            reports,
            metadata["replay_cache"],
            policy,
            budget,
            factor_charge,
            int_value(args.sample_limit),
        )
        for policy in policies
        for budget in budgets
    ]
    policy_reports.sort(
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0),
            -float_value(report.get("hit_rate")),
            str(report.get("policy")),
            str(report.get("attempt_budget")),
        )
    )
    best = policy_reports[0] if policy_reports else None
    claim_status = determine_claim(policy_reports)
    return {
        "artifacts": {"p709": str(Path(args.p709))},
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows come from archived P709-referenced source artifacts, not a new live generator.",
            "NO LABEL-ONLY SCORING: selected source cases are direct-verifier replayed and charged before success classification.",
            "HEURISTIC: a source-neighborhood replay is not an asymptotic index-calculus theorem.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p711_rel2_source_neighborhood_replay",
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "policies": policies,
            "target": args.target,
        },
        "policy_reports": policy_reports,
        "replay_metadata": {
            key: value
            for key, value in metadata.items()
            if key != "replay_cache"
        },
        "schema": "ecdlp.low_term_total2_p711_rel2_source_neighborhood_replay.v1",
        "summary": {
            "artifact_count": len(reports),
            "best_hit_count": None if best is None else best.get("hit_count"),
            "best_hit_rate": None if best is None else best.get("hit_rate"),
            "best_policy": None if best is None else best.get("policy"),
            "best_source_replay_total_with_fallback_over_rho": (
                None if best is None else best.get("source_replay_total_with_fallback_over_rho")
            ),
            "policy_count": len(policy_reports),
            "source_count": metadata["source_count"],
            "unique_replayed_candidate_count": len(metadata["replay_cache"]),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2,4,all")
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy_reports": payload["policy_reports"][:8]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
