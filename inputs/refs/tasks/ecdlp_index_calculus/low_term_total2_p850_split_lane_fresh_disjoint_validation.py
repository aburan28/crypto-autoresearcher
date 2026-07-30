#!/usr/bin/env python3
"""P850 split-lane fresh disjoint validation audit.

P849 showed, on two known P843 heldout false positives, that rows rejected as
standalone factor packets can still be useful direct relation leaves.  This
audit validates that split-lane interpretation on fresh disjoint public-factor
banks: select rows by the frozen P845 public surface-cost rejection, then score
whether direct relation-equation verification recovers them standalone, by
same-row leaf expansion, or in a same-source-case companion group.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p849_false_factor_relation_discriminator_audit as p849


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P843 = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p850_split_lane_fresh_disjoint_validation.md"
SCHEMA = "ecdlp.low_term_total2_p850_split_lane_fresh_disjoint_validation.v1"


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


def bank_id(path: Path) -> str:
    match = re.search(r"fresh_([0-9]+_[0-9]+(?:_[a-z0-9]+)*)_probe", path.name)
    if match:
        return f"fresh_{match.group(1)}"
    return path.stem


def normalized_name(path_text: str) -> str:
    return Path(path_text).name


def source_paths(args: argparse.Namespace, p843: dict[str, Any]) -> list[Path]:
    excluded_names = {
        normalized_name(str(source.get("path") or ""))
        for source in (p843.get("artifacts") or {}).get("sources") or []
    }
    paths = []
    for path in sorted(args.state_dir.glob(args.probe_glob)):
        name = path.name
        if "structural_policy" in name:
            continue
        if "nativefp" in name and not args.include_nativefp:
            continue
        if name in excluded_names:
            continue
        paths.append(path)
    return paths


def load_signature(public_payload: dict[str, Any], cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path = str(Path((public_payload.get("parameters") or {})["signature_source"]))
    if path not in cache:
        cache[path] = load_json(Path(path))
    return cache[path]


def candidate_surface_features(
    public_payload: dict[str, Any],
    row: dict[str, Any],
    sage_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    if not chosen:
        return {}
    sage_path = str(Path((public_payload.get("parameters") or {})["sage_factor_source"]))
    if sage_path not in sage_cache:
        sage_cache[sage_path] = load_json(Path(sage_path))
    surfaces = {str(surface["surface_id"]): surface for surface in sage_cache[sage_path].get("surfaces") or []}
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


def source_case_key(public_path: Path, source_case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(public_path),
        str(source_case.get("target")),
        int_value(source_case.get("transfer_index")),
        tuple(str(key) for key in source_case.get("row_keys") or []),
        int_value(source_case.get("top_k")),
        str(source_case.get("selector")),
        str(source_case.get("policy")),
    )


def nonempty_subsets(leaves: list[int]) -> list[list[int]]:
    out = []
    for size in range(1, len(leaves) + 1):
        for combo in itertools.combinations(leaves, size):
            out.append(list(combo))
    return out


def case_leaf_map_with_candidate(
    case_leaf_map: dict[str, list[int]],
    candidate_row_key: str,
    candidate_leaves: set[int],
) -> dict[str, list[int]]:
    out = {row_key: sorted({int_value(leaf) for leaf in leaves}) for row_key, leaves in case_leaf_map.items()}
    out[candidate_row_key] = sorted(set(out.get(candidate_row_key, [])) | candidate_leaves)
    return out


def enumerate_relation_variants(
    candidate_row_key: str,
    candidate_leaves: set[int],
    case_leaf_map: dict[str, list[int]],
    max_variants: int,
) -> dict[str, dict[str, list[int]]]:
    variants: dict[str, dict[str, list[int]]] = {
        "candidate_leaf_only": {candidate_row_key: sorted(candidate_leaves)},
        "same_row_source_case_leaves": {candidate_row_key: case_leaf_map.get(candidate_row_key, [])},
        "source_case_all": case_leaf_map,
        "source_case_without_candidate_leaf": {
            row_key: sorted(set(leaves) - (candidate_leaves if row_key == candidate_row_key else set()))
            for row_key, leaves in case_leaf_map.items()
        },
    }
    subset_options = {}
    for row_key, leaves in sorted(case_leaf_map.items()):
        options = nonempty_subsets(sorted({int_value(leaf) for leaf in leaves}))
        if row_key == candidate_row_key:
            options = [option for option in options if candidate_leaves <= set(option)]
        subset_options[row_key] = options

    row_keys = sorted(case_leaf_map)
    index = 0
    for choice in itertools.product(*(subset_options[row_key] for row_key in row_keys)):
        leaf_map = {row_key: sorted(choice[pos]) for pos, row_key in enumerate(row_keys)}
        if not candidate_leaves <= set(leaf_map.get(candidate_row_key, [])):
            continue
        if sum(len(leaves) for leaves in leaf_map.values()) <= len(candidate_leaves):
            continue
        if leaf_map in variants.values():
            continue
        index += 1
        variants[f"candidate_group_subset_{index:02d}"] = leaf_map
        if max_variants and len(variants) >= max_variants:
            break
    return variants


def compact_variant(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    union = row.get("union") or {}
    return {
        "leaves_by_row": row.get("leaves_by_row"),
        "name": row.get("name"),
        "ops_over_rho": row.get("ops_over_rho"),
        "union": union,
        "uses_candidate_factor_leaf": row.get("uses_known_false_positive_leaf"),
        "verified": row.get("verified"),
    }


def rank_of(row: dict[str, Any] | None) -> int:
    if not row:
        return 0
    return int_value((row.get("union") or {}).get("union_rank"))


def relation_count_of(row: dict[str, Any] | None) -> int:
    if not row:
        return 0
    return int_value((row.get("union") or {}).get("union_relation_count"))


def best_verified_with_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return (row.get("variant_summary") or {}).get("best_verified_with_candidate_leaf")


def verified_with_candidate(row: dict[str, Any]) -> bool:
    return bool(best_verified_with_candidate(row))


def below_rho_verified_with_candidate(row: dict[str, Any]) -> bool:
    best = best_verified_with_candidate(row)
    if not best or best.get("ops_over_rho") is None:
        return False
    return float(best["ops_over_rho"]) < 1.0


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


def classify_relation(
    variants: list[dict[str, Any]],
    candidate_row_key: str,
    candidate_leaves: set[int],
) -> str:
    candidate_only = next((row for row in variants if row["name"] == "candidate_leaf_only"), None)
    if candidate_only and candidate_only["verified"]:
        return "standalone_direct_relation_verified"
    verified_with_candidate = [
        row
        for row in variants
        if row["verified"] and row["uses_known_false_positive_leaf"]
    ]
    if any(any(row_key != candidate_row_key for row_key in row.get("leaves_by_row") or {}) for row in verified_with_candidate):
        return "companion_group_relation_verified"
    if any(
        set((row.get("leaves_by_row") or {}).get(candidate_row_key, [])) > candidate_leaves
        for row in verified_with_candidate
    ):
        return "same_row_expanded_relation_verified"
    return "not_relation_verified"


def analyze_rejected_row(
    verifier: Any,
    records: list[dict[str, Any]],
    public_path: Path,
    public_payload: dict[str, Any],
    row: dict[str, Any],
    candidate_features: dict[str, Any],
    signature_cache: dict[str, dict[str, Any]],
    context_cache: dict[tuple[Any, ...], tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]],
    max_variants: int,
) -> dict[str, Any]:
    signature = load_signature(public_payload, signature_cache)
    cases = p849.source_cases_for_row(signature, row)
    candidate_row_key = str(row["row_key"])
    candidate_leaves = {int_value(leaf) for leaf in row.get("factor_zero_leaf_indices") or []}
    base = {
        "bank_id": bank_id(public_path),
        "candidate_features": candidate_features,
        "candidate_factor_leaf_indices": sorted(candidate_leaves),
        "chosen_candidate": row.get("chosen_candidate"),
        "hidden_factor_labels": {
            "chosen_false_positive_source": bool(row.get("chosen_false_positive_source")),
            "chosen_preserves_selected_root_pairs_source": bool(row.get("chosen_preserves_selected_root_pairs_source")),
            "missing_selected_root_pairs": row.get("missing_selected_root_pairs") or [],
            "quadratic_preserves_selected_root_pairs": bool(row.get("quadratic_preserves_selected_root_pairs")),
        },
        "public_source": str(public_path),
        "row_key": candidate_row_key,
        "target": row.get("target"),
        "transfer_index": int_value(row.get("transfer_index")),
    }
    if not candidate_leaves:
        return {**base, "error": "no candidate factor-zero leaves"}
    if not cases:
        return {**base, "error": "no source case found"}

    source_case = cases[0]
    case_leaf_map = case_leaf_map_with_candidate(
        p848.leaf_map_from_case(source_case),
        candidate_row_key,
        candidate_leaves,
    )
    key = source_case_key(public_path, source_case)
    if key not in context_cache:
        context_cache[key] = p848.build_context(verifier, records, public_payload, source_case)
    built_by_row, components_by_row, local_args_by_row = context_cache[key]

    variants = [
        p848.evaluate_variant(
            verifier,
            name,
            leaves_by_row,
            built_by_row,
            components_by_row,
            local_args_by_row,
            {candidate_row_key: candidate_leaves},
        )
        for name, leaves_by_row in enumerate_relation_variants(
            candidate_row_key,
            candidate_leaves,
            case_leaf_map,
            max_variants,
        ).items()
    ]
    candidate_only = next((variant for variant in variants if variant["name"] == "candidate_leaf_only"), None)
    verified_with_candidate = [
        variant for variant in variants if variant["verified"] and variant["uses_known_false_positive_leaf"]
    ]
    best_verified_with_candidate = best_variant(verified_with_candidate)
    best_verified = best_variant([variant for variant in variants if variant["verified"]])
    best_no_candidate_leaf = best_variant(
        [variant for variant in variants if not variant["uses_known_false_positive_leaf"]]
    )
    relation_class = classify_relation(variants, candidate_row_key, candidate_leaves)
    return {
        **base,
        "case_leaf_map": case_leaf_map,
        "relation_discriminator_class": relation_class,
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
        "variant_summary": {
            "best_no_candidate_leaf_variant": compact_variant(best_no_candidate_leaf),
            "best_verified_variant": compact_variant(best_verified),
            "best_verified_with_candidate_leaf": compact_variant(best_verified_with_candidate),
            "candidate_leaf_only": compact_variant(candidate_only),
            "marginal_rank_gain_over_candidate_only": max(0, rank_of(best_verified_with_candidate) - rank_of(candidate_only)),
            "marginal_relation_gain_over_candidate_only": max(
                0,
                relation_count_of(best_verified_with_candidate) - relation_count_of(candidate_only),
            ),
            "verified_variant_count": sum(1 for variant in variants if variant["verified"]),
            "verified_with_candidate_leaf_count": len(verified_with_candidate),
            "verified_without_candidate_leaf_count": sum(
                1 for variant in variants if variant["verified"] and not variant["uses_known_false_positive_leaf"]
            ),
        },
        "variants": sorted(
            [compact_variant(variant) for variant in variants],
            key=lambda item: (
                not bool(item["verified"]),
                float(item.get("ops_over_rho") or 10**9),
                str(item.get("name")),
            ),
        ),
    }


def determine_claim(rows: list[dict[str, Any]]) -> str:
    valid = [row for row in rows if not row.get("error")]
    hidden_false = [
        row
        for row in valid
        if (row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")
    ]
    recovered_hidden_false = [row for row in hidden_false if verified_with_candidate(row)]
    below_hidden_false = [row for row in hidden_false if below_rho_verified_with_candidate(row)]
    recovered_any = [row for row in valid if verified_with_candidate(row)]
    below_any = [row for row in valid if below_rho_verified_with_candidate(row)]
    if hidden_false and len(below_hidden_false) == len(hidden_false):
        return "P850_FRESH_REJECTED_FALSE_FACTORS_ALL_RECOVER_BELOW_RHO_AS_DIRECT_RELATIONS"
    if hidden_false and len(recovered_hidden_false) == len(hidden_false) and below_hidden_false:
        return "P850_FRESH_REJECTED_FALSE_FACTORS_ALL_VERIFY_WITH_ABOVE_RHO_OUTLIERS"
    if below_hidden_false:
        return "P850_FRESH_REJECTED_FALSE_FACTORS_PARTIALLY_RECOVER_BELOW_RHO_AS_DIRECT_RELATIONS"
    if recovered_hidden_false:
        return "P850_FRESH_REJECTED_FALSE_FACTORS_VERIFY_ONLY_ABOVE_RHO"
    if below_any:
        return "P850_FRESH_REJECTED_FACTOR_ROWS_HAVE_RELATION_SIGNAL_BUT_NOT_ON_FALSE_FACTORS"
    if recovered_any:
        return "P850_FRESH_REJECTED_FACTOR_ROWS_VERIFY_ONLY_ABOVE_RHO"
    return "NEGATIVE_RESULT_P850_SPLIT_LANE_FRESH_VALIDATION_NOT_FOUND"


def summarize(rows: list[dict[str, Any]], source_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if not row.get("error")]
    hidden_false = [
        row
        for row in valid
        if (row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")
    ]
    recovered = [row for row in valid if verified_with_candidate(row)]
    below_recovered = [row for row in valid if below_rho_verified_with_candidate(row)]
    recovered_hidden_false = [row for row in hidden_false if verified_with_candidate(row)]
    below_recovered_hidden_false = [
        row for row in hidden_false if below_rho_verified_with_candidate(row)
    ]
    return {
        "above_rho_verified_count": len(recovered) - len(below_recovered),
        "claim_status": determine_claim(rows),
        "errors": len(rows) - len(valid),
        "fresh_source_count": len(source_summaries),
        "hidden_false_factor_below_rho_verified_count": len(below_recovered_hidden_false),
        "hidden_false_factor_relation_verified_count": len(recovered_hidden_false),
        "hidden_false_factor_rejected_count": len(hidden_false),
        "relation_lane_below_rho_verified_count": len(below_recovered),
        "relation_lane_candidate_rows": len(rows),
        "relation_lane_verified_count": len(recovered),
        "same_row_expanded_relation_verified_count": sum(
            1 for row in recovered if row.get("relation_discriminator_class") == "same_row_expanded_relation_verified"
        ),
        "companion_relation_verified_count": sum(
            1 for row in recovered if row.get("relation_discriminator_class") == "companion_group_relation_verified"
        ),
        "standalone_relation_verified_count": sum(
            1 for row in recovered if row.get("relation_discriminator_class") == "standalone_direct_relation_verified"
        ),
        "unverified_relation_spend_count": len(valid) - len(recovered),
        "unverified_hidden_false_spend_count": len(hidden_false) - len(recovered_hidden_false),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p843 = load_json(args.p843)
    p845 = load_json(args.p845)
    guard_threshold = int_value(p845["selected_guard"]["guard"]["threshold"])
    selected_policy = args.policy or str(p843["selected_policy"]["policy"])
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    signature_cache: dict[str, dict[str, Any]] = {}
    sage_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[tuple[Any, ...], tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    for public_path in source_paths(args, p843):
        public_payload = load_json(public_path)
        policy_rows = (public_payload.get("policy_rows") or {}).get(selected_policy) or []
        source_summary = {
            "active_rows": 0,
            "bank_id": bank_id(public_path),
            "hidden_false_factor_rows": 0,
            "hidden_false_rejected_rows": 0,
            "public_source": str(public_path),
            "rejected_rows": 0,
            "total_rows": len(policy_rows),
        }
        for row in policy_rows:
            if not row.get("chosen_candidate"):
                continue
            source_summary["active_rows"] += 1
            if bool(row.get("chosen_false_positive_source")):
                source_summary["hidden_false_factor_rows"] += 1
            features = candidate_surface_features(public_payload, row, sage_cache)
            rejected = int_value(features.get("surface_ffe_ops")) > guard_threshold
            if not rejected:
                continue
            source_summary["rejected_rows"] += 1
            if bool(row.get("chosen_false_positive_source")):
                source_summary["hidden_false_rejected_rows"] += 1
            if args.hidden_false_only and not bool(row.get("chosen_false_positive_source")):
                continue
            rows.append(
                analyze_rejected_row(
                    verifier,
                    records,
                    public_path,
                    public_payload,
                    row,
                    features,
                    signature_cache,
                    context_cache,
                    args.max_variants,
                )
            )
            if args.max_rows and len(rows) >= args.max_rows:
                source_summaries.append(source_summary)
                break
        else:
            source_summaries.append(source_summary)
            continue
        break
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
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PUBLIC-SELECTION BOUNDARY: relation-lane candidates are selected by frozen P845 public surface-cost rejection, not by hidden false-positive labels.",
            "HIDDEN-LABEL BOUNDARY: chosen_false_positive_source is reported only to stratify outcomes after public selection.",
            "VERIFIER-FACING DISCRIMINATOR: admission to the relation lane is scored by public direct relation-equation verification.",
            "SOURCE-CASE BOUNDARY: companion leaves come from same-source-case public row groups; this validates a relation-collection subproblem, not a full target-descent pipeline.",
            "POLLARD-RHO BOUNDARY: this is relation-equation bridge evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p850_split_lane_fresh_disjoint_validation",
        "parameters": {
            "excluded_p843_source_count": len((p843.get("artifacts") or {}).get("sources") or []),
            "hidden_false_only": bool(args.hidden_false_only),
            "max_rows": args.max_rows,
            "max_variants": args.max_variants,
            "p843_claim": p843.get("claim_status"),
            "p845_claim": p845.get("claim_status"),
            "p845_surface_threshold": guard_threshold,
            "policy": selected_policy,
            "probe_glob": args.probe_glob,
        },
        "red_team_handoff": {
            "assumptions": [
                "Rows rejected by P845's public factor guard can be routed to a second-stage direct relation lane without reopening standalone factor-packet promotion.",
                "Same-source-case companion groups are a legitimate public validation search space for relation-equation recovery.",
                "Fresh-bank hidden false-positive labels are used only as outcome strata, not as operational selection inputs.",
            ],
            "failure_modes": [
                "The relation verifier may be too expensive or too late for large-parameter relation collection.",
                "Verified relation rows may have poor sparse-matrix rank contribution after deduplication.",
                "Same-source-case grouping may be exploiting toy-harness structure that does not survive a larger sweep.",
                "Target descent and individual logarithms are not measured in this audit.",
            ],
            "next_concrete_action": (
                "Build P851 to aggregate P850 verified relation rows into a sparse matrix/rank-growth audit, charge duplicate compression, "
                "and compare relation yield against Pollard-rho-normalized collection cost before any stronger index-calculus claim."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P850_FRESH") else "NEGATIVE RESULT",
        },
        "relation_lane_rows": rows,
        "schema": SCHEMA,
        "source_summaries": source_summaries,
        "summary": summarize(rows, source_summaries),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p843", type=Path, default=DEFAULT_P843)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument(
        "--probe-glob",
        default="*public_factor_quadratic_root_fresh_*_expanded_probe.json",
    )
    parser.add_argument("--policy", default="")
    parser.add_argument("--include-nativefp", action="store_true")
    parser.add_argument("--hidden-false-only", action="store_true")
    parser.add_argument("--max-rows", type=int, default=0)
    parser.add_argument("--max-variants", type=int, default=96)
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
