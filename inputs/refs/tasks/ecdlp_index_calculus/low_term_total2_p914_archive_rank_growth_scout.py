#!/usr/bin/env python3
"""P914 archive rank-growth scout for the frozen P913 public family."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p901_frozen_direct_generator_validation as p901
import low_term_total2_p903_relaxed_family_grid_validation as p903
import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p906_p905_first_stop_certificate_rank_audit as p906
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p914_archive_rank_growth_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P913_SOURCE = STATE_DIR / "low_term_total2_p913_min_cost_public_representative_rank_filter_probe.json"
SCHEMA = "ecdlp.low_term_total2_p914_archive_rank_growth_scout.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p905.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p905.float_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p905.ratio(numerator, denominator)


def archive_source_paths(state_dir: Path) -> list[Path]:
    paths: list[tuple[int, int, Path]] = []
    pattern = "frontier_public_leaf_policy_low_term_total2_fixed_row_*_expanded_probe.json"
    for path in state_dir.glob(pattern):
        match = re.search(r"_(\d+)_(\d+)_expanded_probe\.json$", path.name)
        if not match:
            continue
        paths.append((int(match.group(1)), int(match.group(2)), path))
    return [path for _start, _end, path in sorted(paths)]


def row_salts(case: dict[str, Any]) -> list[int]:
    return [
        p901.p900.row_salt(str(row.get("row_key")))
        for row in case.get("row_leaf_keys") or []
    ]


def salt_gap(case: dict[str, Any]) -> int:
    salts = row_salts(case)
    if len(salts) != 2:
        return -1
    return abs(int(salts[0]) - int(salts[1]))


def selector_group(case: dict[str, Any]) -> str:
    return p901.p900.selector_group(str(case.get("selector")))


def augment_case(case: dict[str, Any], source_path: Path, archive_ordinal: int) -> dict[str, Any]:
    out = dict(case)
    out["archive_stream_ordinal"] = archive_ordinal
    out["leaf_signature"] = p903.leaf_signature(out)
    out["row_salts"] = row_salts(out)
    out["salt_gap"] = salt_gap(out)
    out["selector_group"] = selector_group(out)
    out["source"] = str(source_path)
    out["source_path"] = str(source_path)
    return out


def matching_clause(case: dict[str, Any]) -> str | None:
    if str(case.get("target")) != p905.TARGET:
        return None
    for name, clause in p905.clause_by_name().items():
        if p905.matches_clause({"case": case}, clause):
            return str(name)
    return None


def p913_frozen_archive_policy(clause_name: str, case: dict[str, Any]) -> bool:
    gap = salt_gap(case)
    source_ops = float_value(case.get("ops_over_rho"))
    if clause_name.startswith("c8_"):
        return gap >= 8 and source_ops <= 0.70072993
    if clause_name.startswith("c90_"):
        return gap <= 4
    if clause_name.startswith("c19_"):
        return gap <= 1 or gap >= 5
    return False


def relation_rowset_key(case: dict[str, Any], clause_name: str) -> tuple[Any, ...]:
    return (
        int_value(case.get("transfer_index")),
        str(clause_name),
        str(case.get("leaf_signature")),
        p906.normalize_row_leaf_keys(case.get("row_leaf_keys") or []),
    )


def all_candidates(source_paths: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    archive_ordinal = 0
    for source_path in source_paths:
        for source_case in p901.p899.cases_for_expanded_source(source_path):
            case = augment_case(source_case, source_path, archive_ordinal)
            archive_ordinal += 1
            clause_name = matching_clause(case)
            if not clause_name:
                continue
            candidates.append(
                {
                    "clause": clause_name,
                    "policy_selected": p913_frozen_archive_policy(clause_name, case),
                    "rowset_key": relation_rowset_key(case, clause_name),
                    "source_case": case,
                    "source_path": str(source_path),
                }
            )
    return candidates


def evaluate_candidates(candidates: list[dict[str, Any]], max_factor_degree: int) -> list[dict[str, Any]]:
    evaluated_rows = p903.evaluate_source_cases(
        [candidate["source_case"] for candidate in candidates],
        max_factor_degree,
    )
    out: list[dict[str, Any]] = []
    for index, (candidate, evaluated) in enumerate(zip(candidates, evaluated_rows)):
        case = evaluated.get("case") if isinstance(evaluated.get("case"), dict) else {}
        case.update(
            {
                "archive_stream_ordinal": candidate["source_case"].get("archive_stream_ordinal"),
                "leaf_signature": candidate["source_case"].get("leaf_signature"),
                "row_salts": candidate["source_case"].get("row_salts"),
                "salt_gap": candidate["source_case"].get("salt_gap"),
                "selector_group": candidate["source_case"].get("selector_group"),
                "source_path": candidate["source_path"],
            }
        )
        evaluated["case"] = case
        evaluated["p914_candidate_index"] = index
        evaluated["p914_clause"] = candidate["clause"]
        evaluated["p914_policy_selected"] = bool(candidate["policy_selected"])
        evaluated["p914_rowset_key"] = candidate["rowset_key"]
        evaluated["_source_case"] = candidate["source_case"]
        evaluated["_source_path"] = candidate["source_path"]
        out.append(evaluated)
    return out


def public_rowset_representatives(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(row["p914_rowset_key"])
        current = best.get(key)
        if current is None or representative_order_key(row) < representative_order_key(current):
            best[key] = row
    return sorted(best.values(), key=representative_order_key)


def representative_order_key(row: dict[str, Any]) -> tuple[Any, ...]:
    case = row.get("case") or {}
    return (
        int_value(row.get("generator_case_cost_ops"), 10**12),
        float_value(case.get("ops_over_rho"), 10**12),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
    )


def known_p913_control_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = {
        (1005, "c90_top7_lowterm_opsge0p70"),
        (992, "c19_top4_lowleaf_hybrid_opsge0p70"),
        (1058, "c90_top7_lowterm_opsge0p70"),
        (1071, "c19_top4_lowleaf_hybrid_opsge0p70"),
        (1104, "c8_gap8_top7_lowleaf_hybrid_opsge0p70"),
        (1109, "c90_top7_lowterm_opsge0p70"),
        (1123, "c19_top4_lowleaf_hybrid_opsge0p70"),
    }
    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    for row in rows:
        case = row.get("case") or {}
        key = (int_value(case.get("transfer_index")), str(row.get("p914_clause")))
        if key not in wanted:
            continue
        current = by_key.get(key)
        if current is None or representative_order_key(row) < representative_order_key(current):
            by_key[key] = row
    return [by_key[key] for key in sorted(by_key)]


def stop_from_row(row: dict[str, Any]) -> dict[str, Any]:
    case = row.get("case") or {}
    return {
        "archive_stream_ordinal": case.get("archive_stream_ordinal"),
        "clause": row.get("p914_clause"),
        "generator_case_cost_ops": int_value(row.get("generator_case_cost_ops"), 1),
        "leaf_signature": case.get("leaf_signature"),
        "ops_over_rho": case.get("ops_over_rho"),
        "public_key_verified": row.get("public_key_verified"),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "row_leaf_keys": case.get("row_leaf_keys") or [],
        "row_salts": case.get("row_salts") or [],
        "salt_gap": case.get("salt_gap"),
        "selector": case.get("selector"),
        "selector_group": case.get("selector_group"),
        "source_path": row.get("_source_path"),
        "strict_below_rho": row.get("strict_below_rho"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
    }


def export_certificates(rows: list[dict[str, Any]], out_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    certificates: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    source_cache: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        source_path = Path(str(row.get("_source_path")))
        stop = stop_from_row(row)
        try:
            source = source_cache.get(str(source_path))
            if source is None:
                source = load_json(source_path)
                source_cache[str(source_path)] = source
            cert = p906.certificate_for_source_case(
                source,
                source_path,
                row["_source_case"],
                "archive",
                stop,
                index,
            )
            cert["_artifact"] = str(out_path)
            cert["_artifact_offset"] = index
            cert["_global_index"] = index
            cert["direct_export_route"] = "direct_source_exact_p914_archive_rank_scout"
            cert["p914_selection"] = {
                "archive_stream_ordinal": stop.get("archive_stream_ordinal"),
                "charged_candidate_cost_ops": 1 + int_value(row.get("generator_case_cost_ops"), 1),
                "clause": row.get("p914_clause"),
                "generator_case_cost_ops": int_value(row.get("generator_case_cost_ops"), 1),
                "leaf_signature": stop.get("leaf_signature"),
                "policy_selected": bool(row.get("p914_policy_selected")),
                "selector": stop.get("selector"),
                "source_path": str(source_path),
                "transfer_index": stop.get("transfer_index"),
            }
            certificates.append(cert)
        except Exception as exc:  # noqa: BLE001 - preserve failed certificate exports as data.
            errors.append(
                {
                    "clause": row.get("p914_clause"),
                    "error": repr(exc),
                    "source_path": str(source_path),
                    "transfer_index": stop.get("transfer_index"),
                }
            )
    return certificates, errors


def audit_certificates(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    audits = p908.order_audits(certificates)
    return {
        "matrix_consistent": all(bool(audit.get("matrix_consistent")) for audit in audits.values()) if audits else True,
        "order_audits": audits,
        "summary": p908.audit_summary(audits),
        "usable_certificate_count": sum(1 for cert in certificates if p908.usable(cert)),
    }


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    case = row.get("case") or {}
    return {
        "archive_stream_ordinal": case.get("archive_stream_ordinal"),
        "charged_candidate_cost_ops": 1 + int_value(row.get("generator_case_cost_ops"), 1),
        "clause": row.get("p914_clause"),
        "generator_case_cost_ops": row.get("generator_case_cost_ops"),
        "leaf_signature": case.get("leaf_signature"),
        "ops_over_rho": case.get("ops_over_rho"),
        "public_key_verified": row.get("public_key_verified"),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "salt_gap": case.get("salt_gap"),
        "selector": case.get("selector"),
        "selector_group": case.get("selector_group"),
        "source_path": row.get("_source_path"),
        "strict_below_rho": row.get("strict_below_rho"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
    }


def determine_claim(audit: dict[str, Any], baseline_rank: int) -> str:
    if not bool(audit.get("matrix_consistent")):
        return "NEGATIVE_RESULT_P914_ARCHIVE_FACTOR_BANK_INCONSISTENT"
    rank = int_value((audit.get("summary") or {}).get("total_factor_rank"))
    if rank > baseline_rank:
        return "P914_ARCHIVE_PUBLIC_POLICY_GROWS_FACTOR_RANK"
    if rank == baseline_rank:
        return "NEGATIVE_RESULT_P914_ARCHIVE_POLICY_DUPLICATES_CURRENT_RANK"
    return "NEGATIVE_RESULT_P914_ARCHIVE_POLICY_UNDER_RECOVERS_CURRENT_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p913_payload = load_json(args.p913_source)
    baseline_rank = int_value(((p913_payload.get("summary") or {}).get("best_public_policy") or {}).get("total_factor_rank"), 5)
    sources = archive_source_paths(STATE_DIR)
    candidates = all_candidates(sources)
    frozen_candidates = [candidate for candidate in candidates if candidate["policy_selected"]]
    evaluated = evaluate_candidates(frozen_candidates, int(args.max_factor_degree))
    representatives = public_rowset_representatives(evaluated)
    selected = representatives[: int(args.max_selected)]
    control_rows = known_p913_control_rows(evaluated)
    control_certificates, control_errors = export_certificates(control_rows, args.out)
    selected_certificates, selected_errors = export_certificates(selected, args.out)
    control_audit = audit_certificates(control_certificates)
    selected_audit = audit_certificates(selected_certificates)
    selected_cost = sum(1 + int_value(row.get("generator_case_cost_ops"), 1) for row in selected)
    control_cost = sum(1 + int_value(row.get("generator_case_cost_ops"), 1) for row in control_rows)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p913_source": str(args.p913_source),
            "script": str(Path(__file__)),
        },
        "certificates": selected_certificates,
        "claim_status": determine_claim(selected_audit, baseline_rank),
        "created_at": now_iso(),
        "export_errors": selected_errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this reuses compatible historical source windows and is not fresh validation.",
            "PUBLIC-PRE-REPLAY: the frozen policy uses target, clause, leaf signature, selector group, top-k, source ops, and salt gap.",
            "COST-MODEL-SPLIT: archive direct-generator costs are reported separately from P913 charged source-window costs.",
            "RANK-SIGNAL-NOT-DESCENT: rank growth is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "known_p913_control": {
            "audit": control_audit,
            "certificate_count": len(control_certificates),
            "charged_candidate_cost_ops": control_cost,
            "errors": control_errors,
            "rows": [compact_row(row) for row in control_rows],
        },
        "method": "p914_archive_rank_growth_scout",
        "parameters": {
            "baseline_p913_rank": baseline_rank,
            "max_factor_degree": int(args.max_factor_degree),
            "max_selected": int(args.max_selected),
            "rho_estimate": p905.RHO_ESTIMATE,
            "source_count": len(sources),
            "target": p905.TARGET,
        },
        "policy": {
            "c8": "P905 c8 clause plus source_ops <= 0.70072993",
            "c19": "P905 c19 clause plus salt_gap <= 1 or salt_gap >= 5",
            "c90": "P905 c90 clause plus salt_gap <= 4",
            "representative_rule": "evaluate frozen candidates, then choose min generator_case_cost_ops per public transfer/clause/leaf/rowset key",
        },
        "schema": SCHEMA,
        "selected_audit": selected_audit,
        "selected_rows": [compact_row(row) for row in selected],
        "source_paths": [str(path) for path in sources],
        "summary": {
            "candidate_count": len(candidates),
            "charged_candidate_cost_ops": selected_cost,
            "control_rank": (control_audit.get("summary") or {}).get("total_factor_rank"),
            "control_row_count": len(control_rows),
            "evaluated_frozen_candidate_count": len(evaluated),
            "export_error_count": len(selected_errors),
            "frozen_candidate_count": len(frozen_candidates),
            "frozen_candidate_count_by_clause": dict(Counter(str(candidate["clause"]) for candidate in frozen_candidates)),
            "representative_count": len(representatives),
            "selected_certificate_count": len(selected_certificates),
            "selected_count": len(selected),
            "selected_public_key_verified_count": sum(1 for cert in selected_certificates if cert.get("public_key_verified")),
            "selected_rank": (selected_audit.get("summary") or {}).get("total_factor_rank"),
            "selected_unique_factor_relation_count": (selected_audit.get("summary") or {}).get("total_unique_factor_relation_count"),
            "selected_usable_certificate_count": selected_audit.get("usable_certificate_count"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--max-selected", type=int, default=96)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p913-source", type=Path, default=P913_SOURCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
