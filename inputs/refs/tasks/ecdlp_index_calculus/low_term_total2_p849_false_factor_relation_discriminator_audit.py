#!/usr/bin/env python3
"""P849 false-factor/direct-relation discriminator audit.

P848 showed that the transfer-324 bridge needs a leaf rejected as a P843
factor false positive.  This audit tests the broader interpretation: rejected
factor-preservation false positives may still be useful direct relation leaves
when admitted only by public relation-equation verification.
"""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P843 = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p849_false_factor_relation_discriminator_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p849_false_factor_relation_discriminator_audit.md"
SCHEMA = "ecdlp.low_term_total2_p849_false_factor_relation_discriminator_audit.v1"


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


def source_cases_for_row(signature: dict[str, Any], row: dict[str, Any]) -> list[dict[str, Any]]:
    matches = []
    for case in signature.get("positive_cases") or []:
        if str(case.get("target")) != str(row.get("target")):
            continue
        if int_value(case.get("transfer_index")) != int_value(row.get("transfer_index")):
            continue
        if str(row.get("row_key")) not in {str(key) for key in case.get("row_keys") or []}:
            continue
        matches.append(case)
    return sorted(
        matches,
        key=lambda case: (
            int_value(case.get("selected_leaf_count"), 10**9),
            int_value(case.get("top_k"), 10**9),
            str(case.get("selector")),
            str(case.get("policy")),
        ),
    )


def candidate_surface_features(public_payload: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    if not chosen:
        return {}
    sage_source = Path((public_payload.get("parameters") or {}).get("sage_factor_source") or "")
    sage = load_json(sage_source)
    surfaces = {str(surface["surface_id"]): surface for surface in sage.get("surfaces") or []}
    surface = surfaces[str(row["surface_id"])]
    candidate = surface["sage_resultant_factor_candidates"][int_value(chosen.get("factor_index"))]
    return {
        "factor_index": int_value(chosen.get("factor_index")),
        "factor_monomials": int_value(chosen.get("factor_monomials")),
        "factor_root_scan_ops": int_value(candidate.get("factor_root_scan_ops")),
        "factor_total_degree": int_value(chosen.get("factor_total_degree")),
        "full_remainder_ffe_ops_over_rho": candidate.get("full_remainder_ffe_ops_over_rho"),
        "public_factor_quadratic_root_ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "remainder_monomials": int_value(candidate.get("remainder_monomials")),
        "surface_ffe_ops": int_value(candidate.get("surface_ffe_ops")),
    }


def nonempty_subsets(leaves: list[int]) -> list[list[int]]:
    out = []
    for size in range(1, len(leaves) + 1):
        for combo in itertools.combinations(leaves, size):
            out.append(list(combo))
    return out


def enumerate_variants(
    false_row_key: str,
    false_leaves: set[int],
    case_leaf_map: dict[str, list[int]],
) -> dict[str, dict[str, list[int]]]:
    variants: dict[str, dict[str, list[int]]] = {
        "false_leaf_only": {false_row_key: sorted(false_leaves)},
        "source_case_all": case_leaf_map,
        "source_case_without_false_leaf": {
            row_key: sorted(set(leaves) - (false_leaves if row_key == false_row_key else set()))
            for row_key, leaves in case_leaf_map.items()
        },
    }
    subset_options = {}
    for row_key, leaves in case_leaf_map.items():
        options = nonempty_subsets(sorted({int_value(leaf) for leaf in leaves}))
        if row_key == false_row_key:
            options = [option for option in options if false_leaves <= set(option)]
        subset_options[row_key] = options

    row_keys = sorted(case_leaf_map)
    index = 0
    for choice in itertools.product(*(subset_options[row_key] for row_key in row_keys)):
        leaf_map = {row_key: sorted(choice[pos]) for pos, row_key in enumerate(row_keys)}
        if leaf_map == variants["source_case_all"] or leaf_map == variants["false_leaf_only"]:
            continue
        if not false_leaves <= set(leaf_map.get(false_row_key, [])):
            continue
        total_leaves = sum(len(leaves) for leaves in leaf_map.values())
        if total_leaves <= len(false_leaves):
            continue
        index += 1
        variants[f"false_leaf_group_subset_{index:02d}"] = leaf_map
    return variants


def best_variant(variants: list[dict[str, Any]], *, require_verified: bool | None = None) -> dict[str, Any] | None:
    rows = variants
    if require_verified is not None:
        rows = [row for row in rows if bool(row.get("verified")) is require_verified]
    if not rows:
        return None
    return sorted(
        rows,
        key=lambda row: (
            not bool(row.get("verified")),
            float(row.get("ops_over_rho") or 10**9),
            sum(len(leaves) for leaves in (row.get("leaves_by_row") or {}).values()),
            str(row.get("name")),
        ),
    )[0]


def compact_variant(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "leaves_by_row": row.get("leaves_by_row"),
        "name": row.get("name"),
        "ops_over_rho": row.get("ops_over_rho"),
        "union": row.get("union"),
        "uses_known_false_positive_leaf": row.get("uses_known_false_positive_leaf"),
        "verified": row.get("verified"),
    }


def classify_relation_discriminator(variants: list[dict[str, Any]], false_row_key: str) -> str:
    false_only = next(row for row in variants if row["name"] == "false_leaf_only")
    if false_only["verified"]:
        return "standalone_direct_relation_verified"
    verified = [row for row in variants if row["verified"]]
    companion_verified = [
        row
        for row in verified
        if any(row_key != false_row_key for row_key in (row.get("leaves_by_row") or {}))
    ]
    if companion_verified:
        return "companion_group_relation_verified"
    return "not_relation_verified"


def analyze_false_row(
    verifier: Any,
    records: list[dict[str, Any]],
    public_payload: dict[str, Any],
    source_bank: dict[str, Any],
    row: dict[str, Any],
    guard_threshold: int,
) -> dict[str, Any]:
    signature = load_json(Path((public_payload.get("parameters") or {})["signature_source"]))
    cases = source_cases_for_row(signature, row)
    if not cases:
        return {
            "error": "no source case found",
            "row_key": row.get("row_key"),
            "target": row.get("target"),
            "transfer_index": row.get("transfer_index"),
        }
    source_case = cases[0]
    case_leaf_map = p848.leaf_map_from_case(source_case)
    false_row_key = str(row["row_key"])
    false_leaves = {int_value(leaf) for leaf in row.get("factor_zero_leaf_indices") or []}
    known_false_positive_leaves = {false_row_key: false_leaves}
    built_by_row, components_by_row, local_args_by_row = p848.build_context(
        verifier,
        records,
        public_payload,
        source_case,
    )
    variants = [
        p848.evaluate_variant(
            verifier,
            name,
            leaves_by_row,
            built_by_row,
            components_by_row,
            local_args_by_row,
            known_false_positive_leaves,
        )
        for name, leaves_by_row in enumerate_variants(false_row_key, false_leaves, case_leaf_map).items()
    ]
    candidate_features = candidate_surface_features(public_payload, row)
    relation_class = classify_relation_discriminator(variants, false_row_key)
    verified_variants = [variant for variant in variants if variant["verified"]]
    no_false_leaf_variants = [
        variant for variant in variants if not variant["uses_known_false_positive_leaf"]
    ]
    return {
        "bank_id": source_bank.get("bank_id"),
        "case_leaf_map": case_leaf_map,
        "candidate_features": candidate_features,
        "chosen_candidate": row.get("chosen_candidate"),
        "false_factor_reason": {
            "chosen_false_positive_source": bool(row.get("chosen_false_positive_source")),
            "missing_selected_root_pairs": row.get("missing_selected_root_pairs") or [],
            "quadratic_preserves_selected_root_pairs": bool(row.get("quadratic_preserves_selected_root_pairs")),
        },
        "false_factor_leaf_indices": sorted(false_leaves),
        "guard_decision": {
            "p845_surface_threshold": guard_threshold,
            "standalone_factor_packet_kept": int_value(candidate_features.get("surface_ffe_ops")) <= guard_threshold,
            "surface_ffe_ops": candidate_features.get("surface_ffe_ops"),
        },
        "relation_discriminator_class": relation_class,
        "row_key": row.get("row_key"),
        "source_case": {
            "below_rho": bool(source_case.get("below_rho")),
            "ops_over_rho": source_case.get("ops_over_rho"),
            "policy": source_case.get("policy"),
            "public_key_verified": bool(source_case.get("public_key_verified")),
            "rank": source_case.get("rank"),
            "relation_count": source_case.get("relation_count"),
            "row_keys": source_case.get("row_keys") or [],
            "selector": source_case.get("selector"),
            "top_k": source_case.get("top_k"),
        },
        "target": row.get("target"),
        "transfer_index": int_value(row.get("transfer_index")),
        "variant_summary": {
            "best_no_false_leaf_variant": compact_variant(best_variant(no_false_leaf_variants)),
            "best_verified_variant": compact_variant(best_variant(verified_variants)),
            "verified_variant_count": len(verified_variants),
            "verified_without_false_leaf_count": sum(
                1 for variant in variants if variant["verified"] and not variant["uses_known_false_positive_leaf"]
            ),
        },
        "variants": sorted(
            variants,
            key=lambda item: (
                not item["verified"],
                float(item.get("ops_over_rho") or 10**9),
                item["name"],
            ),
        ),
    }


def determine_claim(rows: list[dict[str, Any]]) -> str:
    valid = [row for row in rows if not row.get("error")]
    if (
        valid
        and all(not row["guard_decision"]["standalone_factor_packet_kept"] for row in valid)
        and all(row["relation_discriminator_class"] != "not_relation_verified" for row in valid)
    ):
        return "P849_REJECTED_FACTOR_FALSE_POSITIVES_RECOVER_AS_DIRECT_RELATION_LEAVES"
    if any(row.get("relation_discriminator_class") != "not_relation_verified" for row in valid):
        return "P849_REJECTED_FACTOR_FALSE_POSITIVES_PARTIALLY_RECOVER_AS_DIRECT_RELATIONS"
    return "NEGATIVE_RESULT_P849_FALSE_FACTOR_RELATION_DISCRIMINATOR_NOT_FOUND"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p843 = load_json(args.p843)
    p845 = load_json(args.p845)
    guard_threshold = int_value(p845["selected_guard"]["guard"]["threshold"])
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    rows = []
    selected_policy = str(p843["selected_policy"]["policy"])
    for source in p843["artifacts"]["sources"]:
        public_payload = load_json(Path(source["path"]))
        for row in (public_payload.get("policy_rows") or {}).get(selected_policy) or []:
            if not bool(row.get("chosen_false_positive_source")):
                continue
            rows.append(
                analyze_false_row(
                    verifier,
                    records,
                    public_payload,
                    source,
                    row,
                    guard_threshold,
                )
            )
    claim = determine_claim(rows)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p843_source": str(args.p843),
            "p845_source": str(args.p845),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "false_positive_rows": rows,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "VERIFIER-FACING DISCRIMINATOR: the proposed discriminator uses public relation-equation verification, not selected-root preservation labels.",
            "STANDALONE FACTOR GUARD PRESERVED: P845's surface_ffe_ops guard still rejects these rows as standalone factor packets.",
            "RELATION-LEAF REINTERPRETATION: P849 tests whether factor false positives are relation-useful, not whether they preserve the original selected-root pairs.",
            "FRESHNESS BOUNDARY: this is a backtest over the two known P843 heldout false positives, not a fresh disjoint-bank validation.",
            "POLLARD-RHO BOUNDARY: this is relation-equation bridge evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p849_false_factor_relation_discriminator_audit",
        "parameters": {
            "p843_claim": p843.get("claim_status"),
            "p845_claim": p845.get("claim_status"),
            "p845_surface_threshold": guard_threshold,
            "candidate_discriminator": (
                "keep P845 standalone factor rejection, but admit rejected factor leaves as direct relation leaves "
                "only if public relation-equation verification succeeds standalone or in a same-source-case group"
            ),
        },
        "red_team_handoff": {
            "assumptions": [
                "Public relation-equation verification is an acceptable discriminator for relation collection.",
                "A leaf can be false for selected-root preservation but still valid as a direct relation equation.",
                "Backtesting the two P843 false positives is enough to justify a fresh disjoint-bank discriminator validation.",
            ],
            "failure_modes": [
                "The verifier-facing discriminator may be too expensive or too late in the pipeline for large parameters.",
                "Fresh false positives may fail both standalone and grouped direct verification.",
                "A relation-valid false-factor leaf may hurt matrix rank or target descent after collection.",
            ],
            "next_concrete_action": (
                "Build P850 as a fresh disjoint-bank validation of the relation-verifier discriminator: keep P845 standalone "
                "factor rejection, route rejected factor leaves into direct relation verification, and measure verified "
                "relation gain, rank gain, and false relation spend."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P849_REJECTED") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "false_positive_row_count": len(rows),
            "relation_recovered_count": sum(
                1 for row in rows if row.get("relation_discriminator_class") != "not_relation_verified"
            ),
            "standalone_factor_reopened_count": sum(
                1 for row in rows if row.get("guard_decision", {}).get("standalone_factor_packet_kept")
            ),
            "standalone_relation_verified_count": sum(
                1 for row in rows if row.get("relation_discriminator_class") == "standalone_direct_relation_verified"
            ),
            "companion_relation_verified_count": sum(
                1 for row in rows if row.get("relation_discriminator_class") == "companion_group_relation_verified"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p843", type=Path, default=DEFAULT_P843)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
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
