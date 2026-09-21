#!/usr/bin/env python3
"""P851 relation-matrix/rank-growth audit for P850 verified rows.

P850 validates a split lane: rows rejected by the standalone public factor
guard can still verify as direct relation equations.  This audit reconstructs
the P850 best verified row/leaf variants, deduplicates exact linear forms inside
each compatible challenge group, and measures rank growth plus verifier cost.

Challenge groups are kept separate by target and transfer/challenge seed.  That
avoids mixing relation forms from different public keys.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p851_relation_matrix_rank_growth_audit.md"
SCHEMA = "ecdlp.low_term_total2_p851_relation_matrix_rank_growth_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p848.int_value(value, default)


def compact_source_case(row: dict[str, Any]) -> dict[str, Any]:
    case = dict(row.get("source_case") or {})
    case["target"] = row.get("target")
    case["transfer_index"] = row.get("transfer_index")
    return case


def context_key(public_source: str, source_case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        public_source,
        str(source_case.get("target")),
        int_value(source_case.get("transfer_index")),
        tuple(str(key) for key in source_case.get("row_keys") or []),
        int_value(source_case.get("top_k")),
        str(source_case.get("selector")),
        str(source_case.get("policy")),
    )


def scan_key(
    public_source: str,
    source_case: dict[str, Any],
    row_key: str,
    leaves: list[int],
) -> tuple[Any, ...]:
    return (
        *context_key(public_source, source_case),
        str(row_key),
        tuple(sorted({int_value(leaf) for leaf in leaves})),
    )


def form_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    coeffs, rhs, _terms = event["form"]
    return tuple(int(coeff) for coeff in coeffs), int(rhs)


def derive_forms(verifier: Any, built: dict[str, Any], forms: list[tuple[Any, int, list[int]]]) -> dict[str, Any]:
    if not forms:
        return {
            "union_derived_secret": None,
            "union_public_key_verified": False,
            "union_rank": 0,
            "union_relation_count": 0,
        }
    derived = p848.direct_witness_probe.dependency_circuit_probe.public_derive_from_events(
        verifier,
        [{"form": form} for form in forms],
        int(built["order"]),
        built["base"],
        built["public"],
        built["ainvs"],
        int(built["p"]),
    )
    return {
        "union_derived_secret": derived.get("derived_secret"),
        "union_public_key_verified": bool(derived.get("public_key_verified")),
        "union_rank": int_value(derived.get("rank")),
        "union_relation_count": len(forms),
    }


def best_variant(row: dict[str, Any]) -> dict[str, Any] | None:
    return (row.get("variant_summary") or {}).get("best_verified_with_candidate_leaf")


def below_rho(ops_over_rho: Any) -> bool:
    return ops_over_rho is not None and float(ops_over_rho) < 1.0


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p850 = load_json(args.p850)
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    public_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    group_data: dict[tuple[Any, ...], dict[str, Any]] = {}
    candidate_rows = []
    errors = []

    for index, row in enumerate(p850.get("relation_lane_rows") or []):
        variant = best_variant(row)
        if not variant or not variant.get("verified"):
            errors.append({"index": index, "row_key": row.get("row_key"), "error": "missing verified P850 variant"})
            continue
        public_source = str(row["public_source"])
        if public_source not in public_cache:
            public_cache[public_source] = load_json(Path(public_source))
        public_payload = public_cache[public_source]
        source_case = compact_source_case(row)
        ckey = context_key(public_source, source_case)
        if ckey not in context_cache:
            context_cache[ckey] = p848.build_context(verifier, records, public_payload, source_case)
        built_by_row, components_by_row, local_args_by_row = context_cache[ckey]

        scan_rows = []
        raw_scan_ops = 0
        raw_rho = 0
        challenge_seeds = set()
        for selected_row_key, leaves in sorted((variant.get("leaves_by_row") or {}).items()):
            selected = sorted({int_value(leaf) for leaf in leaves})
            if not selected:
                continue
            skey = scan_key(public_source, source_case, selected_row_key, selected)
            if skey not in scan_cache:
                scan_cache[skey] = p848.direct_witness_probe.scan_selected(
                    verifier,
                    built_by_row[selected_row_key],
                    components_by_row[selected_row_key],
                    set(selected),
                    local_args_by_row[selected_row_key],
                )
                built_cache[skey] = built_by_row[selected_row_key]
            scan = scan_cache[skey]
            built = built_cache[skey]
            scan_rows.append(
                {
                    "row_key": selected_row_key,
                    "scan_key": skey,
                    "_scan": scan,
                }
            )
            raw_scan_ops += int_value(scan.get("preassociation_filter_ops"))
            raw_rho = max(raw_rho, int_value(built.get("generic_rho_steps")))
            challenge_seeds.add(str(built.get("challenge_seed")))

        if len(challenge_seeds) != 1:
            errors.append(
                {
                    "index": index,
                    "row_key": row.get("row_key"),
                    "error": "variant spans multiple challenge seeds",
                    "challenge_seeds": sorted(challenge_seeds),
                }
            )
            continue
        challenge_seed = next(iter(challenge_seeds))
        group_key = (str(row.get("target")), int_value(row.get("transfer_index")), challenge_seed)
        if group_key not in group_data:
            group_data[group_key] = {
                "bank_ids": set(),
                "candidate_indices": [],
                "candidate_row_keys": [],
                "challenge_seed": challenge_seed,
                "form_records": {},
                "hidden_false_candidate_count": 0,
                "public_sources": set(),
                "raw_variant_relation_count": 0,
                "raw_variant_rank_sum": 0,
                "scan_keys": {},
                "target": row.get("target"),
                "transfer_index": int_value(row.get("transfer_index")),
            }
        group = group_data[group_key]
        group["candidate_indices"].append(index)
        group["candidate_row_keys"].append(str(row.get("row_key")))
        group["bank_ids"].add(str(row.get("bank_id")))
        group["public_sources"].add(public_source)
        if bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")):
            group["hidden_false_candidate_count"] += 1
        group["raw_variant_relation_count"] += int_value((variant.get("union") or {}).get("union_relation_count"))
        group["raw_variant_rank_sum"] += int_value((variant.get("union") or {}).get("union_rank"))

        for scan_row in scan_rows:
            skey = scan_row["scan_key"]
            scan = scan_row["_scan"]
            if skey not in group["scan_keys"]:
                group["scan_keys"][skey] = {
                    "ops": int_value(scan.get("preassociation_filter_ops")),
                    "rho": int_value(built_cache[skey].get("generic_rho_steps")),
                    "row_key": scan_row["row_key"],
                    "selected_leaf_indices": scan.get("selected_leaf_indices") or [],
                }
            for event in scan.get("relation_events") or []:
                key = form_key(event)
                if key not in group["form_records"]:
                    coeffs, rhs, terms = event["form"]
                    group["form_records"][key] = {
                        "form": (tuple(int(coeff) for coeff in coeffs), int(rhs), [int(term) for term in terms]),
                        "row_key": scan_row["row_key"],
                        "scan_key": skey,
                        "terms": [int(term) for term in terms],
                    }

        candidate_rows.append(
            {
                "bank_id": row.get("bank_id"),
                "best_variant": {
                    "name": variant.get("name"),
                    "ops_over_rho": variant.get("ops_over_rho"),
                    "union": variant.get("union"),
                },
                "challenge_seed": challenge_seed,
                "hidden_false_factor": bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")),
                "raw_reconstructed_ops": raw_scan_ops,
                "raw_reconstructed_ops_over_rho": round(raw_scan_ops / max(1, raw_rho), 8) if raw_rho else None,
                "row_key": row.get("row_key"),
                "target": row.get("target"),
                "transfer_index": int_value(row.get("transfer_index")),
            }
        )

    groups = []
    for group_key, group in sorted(group_data.items(), key=lambda item: (str(item[0][0]), item[0][1], item[0][2])):
        scan_infos = list(group["scan_keys"].values())
        ops = sum(int_value(scan.get("ops")) for scan in scan_infos)
        rho = max((int_value(scan.get("rho")) for scan in scan_infos), default=0)
        first_scan_key = next(iter(group["scan_keys"]))
        built = built_cache[first_scan_key]
        forms = [record["form"] for record in group["form_records"].values()]
        union = derive_forms(verifier, built, forms)
        relation_term_count = sum(len(set(record["terms"])) for record in group["form_records"].values())
        coeff_width = max((len(record["form"][0]) for record in group["form_records"].values()), default=0)
        groups.append(
            {
                "bank_ids": sorted(group["bank_ids"]),
                "candidate_count": len(group["candidate_indices"]),
                "candidate_row_keys": sorted(set(group["candidate_row_keys"])),
                "challenge_seed": group["challenge_seed"],
                "deduped_ops": ops,
                "deduped_ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
                "duplicate_relation_count_removed": max(
                    0,
                    int_value(group["raw_variant_relation_count"]) - int_value(union["union_relation_count"]),
                ),
                "hidden_false_candidate_count": int_value(group["hidden_false_candidate_count"]),
                "matrix_coeff_width": coeff_width,
                "matrix_nonzero_terms": relation_term_count,
                "public_sources": sorted(group["public_sources"]),
                "raw_variant_rank_sum": int_value(group["raw_variant_rank_sum"]),
                "raw_variant_relation_count": int_value(group["raw_variant_relation_count"]),
                "scan_count": len(group["scan_keys"]),
                "scan_leaf_count": sum(len(scan.get("selected_leaf_indices") or []) for scan in scan_infos),
                "target": group["target"],
                "transfer_index": group["transfer_index"],
                "union": union,
            }
        )

    claim = determine_claim(groups, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "script": str(Path(__file__)),
        },
        "candidate_rows": candidate_rows,
        "challenge_groups": groups,
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "GROUP-SEPARATION BOUNDARY: rank is aggregated only inside identical target/transfer challenge seeds; cross-transfer forms are not mixed.",
            "P850-SELECTION BOUNDARY: this audits P850's best verified variants and does not discover new row selectors.",
            "MATRIX BOUNDARY: this is duplicate compression and per-challenge rank growth, not a global sparse linear algebra solve over a reusable factor base.",
            "TARGET-DESCENT BOUNDARY: individual-log target descent and many-target amortization are not measured here.",
            "POLLARD-RHO BOUNDARY: this is relation-matrix evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p851_relation_matrix_rank_growth_audit",
        "parameters": {
            "p850_claim": p850.get("claim_status"),
            "p850_summary": p850.get("summary"),
        },
        "red_team_handoff": {
            "assumptions": [
                "Exact-form deduplication inside each challenge seed is the correct first matrix compression metric.",
                "P850 verified row/leaf variants are a valid relation source to audit for rank growth.",
                "Per-challenge rank growth is useful even though it is not yet a reusable global factor-base matrix.",
            ],
            "failure_modes": [
                "Most challenge groups may be single-candidate groups, limiting matrix compression value.",
                "Per-challenge derivations may not translate into target descent or reusable factor-base relations.",
                "Verifier-facing relation admission may dominate cost at larger parameters.",
            ],
            "next_concrete_action": (
                "Build P852 to search for transfer-invariant relation signatures or reusable factor-base rows across P850 challenge groups, "
                "while preserving the no-cross-transfer-rank-mixing boundary."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P851_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize(groups, candidate_rows, errors),
    }


def determine_claim(groups: list[dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P851_RECONSTRUCTION_ERRORS"
    verified = [group for group in groups if (group.get("union") or {}).get("union_public_key_verified")]
    below = [group for group in verified if below_rho(group.get("deduped_ops_over_rho"))]
    hidden_false_groups = [group for group in groups if int_value(group.get("hidden_false_candidate_count"))]
    hidden_false_below = [group for group in hidden_false_groups if below_rho(group.get("deduped_ops_over_rho"))]
    if groups and len(verified) == len(groups) and len(below) == len(groups):
        return "P851_P850_RELATIONS_DEDUP_TO_ALL_BELOW_RHO_CHALLENGE_GROUPS"
    if groups and len(verified) == len(groups):
        return "P851_P850_RELATIONS_DEDUP_TO_VERIFIED_GROUPS_WITH_ABOVE_RHO_OUTLIERS"
    if hidden_false_groups and len(hidden_false_below) == len(hidden_false_groups):
        return "P851_P850_HIDDEN_FALSE_GROUPS_ALL_DEDUP_BELOW_RHO"
    if below:
        return "P851_P850_RELATIONS_PARTIALLY_DEDUP_TO_BELOW_RHO_GROUPS"
    return "NEGATIVE_RESULT_P851_P850_RELATION_RANK_GROWTH_NOT_FOUND"


def summarize(
    groups: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    verified = [group for group in groups if (group.get("union") or {}).get("union_public_key_verified")]
    below = [group for group in verified if below_rho(group.get("deduped_ops_over_rho"))]
    above = [group for group in verified if not below_rho(group.get("deduped_ops_over_rho"))]
    hidden_false_groups = [group for group in groups if int_value(group.get("hidden_false_candidate_count"))]
    hidden_false_below = [group for group in hidden_false_groups if below_rho(group.get("deduped_ops_over_rho"))]
    raw_relations = sum(int_value(group.get("raw_variant_relation_count")) for group in groups)
    deduped_relations = sum(int_value((group.get("union") or {}).get("union_relation_count")) for group in groups)
    group_ops = [float(group["deduped_ops_over_rho"]) for group in groups if group.get("deduped_ops_over_rho") is not None]
    return {
        "above_rho_verified_group_count": len(above),
        "candidate_row_count": len(candidate_rows),
        "challenge_group_count": len(groups),
        "claim_status": determine_claim(groups, errors),
        "deduped_relation_count": deduped_relations,
        "duplicate_relation_count_removed": max(0, raw_relations - deduped_relations),
        "error_count": len(errors),
        "hidden_false_below_rho_group_count": len(hidden_false_below),
        "hidden_false_group_count": len(hidden_false_groups),
        "max_group_ops_over_rho": max(group_ops) if group_ops else None,
        "mean_group_ops_over_rho": round(sum(group_ops) / len(group_ops), 8) if group_ops else None,
        "min_group_ops_over_rho": min(group_ops) if group_ops else None,
        "raw_variant_relation_count": raw_relations,
        "scan_count_after_dedup": sum(int_value(group.get("scan_count")) for group in groups),
        "total_group_rank": sum(int_value((group.get("union") or {}).get("union_rank")) for group in groups),
        "verified_below_rho_group_count": len(below),
        "verified_group_count": len(verified),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
