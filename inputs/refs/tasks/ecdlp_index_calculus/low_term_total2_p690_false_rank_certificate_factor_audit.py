#!/usr/bin/env python3
"""P690 certificate-level audit for P689 false-rank rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_candidate_scorer as scorer
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p690_false_rank_certificate_factor_audit_probe.json"
DEFAULT_CERTIFICATE_PATHS = [
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p658_verified_phase3_right207_salt207_postquiet_22330_22342_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p659_verified_salt204_right206_anchor11_right208_22343_22355_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p661_verified_right207_salt207_p659_branch_22356_22368_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p663_verified_p661_drift_surfaces_22369_22381_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p665_verified_phase0_salt204_drift_22382_22394_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p666_verified_right207_salt207_offbranch_22395_22407_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p669_verified_phase5_mod7_6_second_repeat_22548_22560_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p674_verified_exact_rank_surface_22722_22723_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p676_verified_adjacent_below_rho_surface_22724_22736_probe.json",
    STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p681_verified_anchor11_salt203_right208_backward_22711_22723_probe.json",
]
ORDER = 9887
CANDIDATE_KEYS = [
    {
        "row_id": "67.a1@9803|22333|mode_cost_hybrid_support_monic_b_total2__p564_holdout_t22333_salt205_salt208_ra11_L09_R11-16|16",
        "selector": "mode_cost_hybrid_support_monic_b_total2__p564_holdout_t22333_salt205_salt208_ra11_L09_R11-16",
        "target": "67.a1@9803",
        "top_k": 16,
        "transfer_index": 22333,
    },
    {
        "row_id": "67.a1@9803|22550|mode_cost_hybrid_support_monic_b_total2__p564_holdout_t22550_salt206_salt208_ra07_L09_R07-16|16",
        "selector": "mode_cost_hybrid_support_monic_b_total2__p564_holdout_t22550_salt206_salt208_ra07_L09_R07-16",
        "target": "67.a1@9803",
        "top_k": 16,
        "transfer_index": 22550,
    },
]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def selected_key(cert: dict[str, Any]) -> tuple[str, int, str, int]:
    row = selected(cert)
    return (
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        str(row.get("selector")),
        int_value(row.get("top_k")),
    )


def target_key(candidate: dict[str, Any]) -> tuple[str, int, str, int]:
    return (
        str(candidate["target"]),
        int_value(candidate["transfer_index"]),
        str(candidate["selector"]),
        int_value(candidate["top_k"]),
    )


def selected_info(cert: dict[str, Any]) -> dict[str, Any]:
    row = selected(cert)
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "certificate_status": cert.get("certificate_status"),
        "direct_ops_over_rho": row.get("direct_ops_over_rho"),
        "expected_secret": cert.get("expected_secret"),
        "forms_count": int_value(cert.get("forms_count")),
        "order": int_value(cert.get("order")),
        "public_key_verified": bool(cert.get("public_key_verified")),
        "rank": int_value(cert.get("rank")),
        "selector": row.get("selector"),
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
        "window": cert.get("window"),
    }


def audit_order(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    return factor_bank.audit_order(certificates, ORDER)


def audit_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "augmented_rank_gain": int_value(after.get("augmented_rank")) - int_value(before.get("augmented_rank")),
        "deficiency_delta": int_value(after.get("deficiency")) - int_value(before.get("deficiency")),
        "factor_relation_count_gain": int_value(after.get("factor_relation_count"))
        - int_value(before.get("factor_relation_count")),
        "factor_variables_derivable_gain": int_value(after.get("factor_variables_derivable_count"))
        - int_value(before.get("factor_variables_derivable_count")),
        "rank_gain": int_value(after.get("rank")) - int_value(before.get("rank")),
        "unique_factor_relation_gain": int_value(after.get("unique_factor_relation_count"))
        - int_value(before.get("unique_factor_relation_count")),
    }


def find_candidates(certificates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    wanted = {target_key(candidate): candidate for candidate in CANDIDATE_KEYS}
    found: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for cert in certificates:
        key = selected_key(cert)
        if key in wanted:
            item = dict(cert)
            item["_candidate_row_id"] = wanted[key]["row_id"]
            found.append(item)
    found_keys = {selected_key(cert) for cert in found}
    for key, candidate in wanted.items():
        if key not in found_keys:
            missing.append(candidate)
    found.sort(key=lambda cert: (int_value(selected(cert).get("transfer_index")), str(selected(cert).get("selector"))))
    return found, missing


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["candidate_missing_count"]:
        return "P690_FALSE_RANK_CERTIFICATE_MATCH_INCOMPLETE"
    if summary["group_rank_gain"] > 0:
        return "P690_FALSE_RANK_CERTIFICATES_ADD_FACTOR_RANK"
    if summary["group_unique_factor_relation_gain"] > 0:
        return "P690_FALSE_RANK_CERTIFICATES_ADD_UNIQUE_FACTOR_RELATIONS_NO_RANK"
    if summary["candidate_count"]:
        return "NEGATIVE_RESULT_P690_FALSE_RANK_CERTIFICATES_NO_FACTOR_GAIN"
    return "NEGATIVE_RESULT_P690_NO_FALSE_RANK_CANDIDATES"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", action="append", default=None, help="Certificate artifact to include.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    paths = [Path(path) for path in (args.certificate or [str(path) for path in DEFAULT_CERTIFICATE_PATHS])]
    certificates = factor_bank.load_certificates(paths)
    candidates, missing = find_candidates(certificates)
    candidate_keys = {selected_key(cert) for cert in candidates}
    base = [cert for cert in certificates if selected_key(cert) not in candidate_keys]
    base_audit = audit_order(base)
    candidate_only_audit = audit_order(candidates) if candidates else audit_order([])
    with_candidates_audit = audit_order(base + candidates)
    group_delta = audit_delta(base_audit, with_candidates_audit)
    scores, greedy_selected, score_summary = scorer.candidate_scores(base, candidates) if candidates else ([], [], {})
    summary = {
        "base_certificate_count": len(base),
        "base_rank": int_value(base_audit.get("rank")),
        "base_unique_factor_relation_count": int_value(base_audit.get("unique_factor_relation_count")),
        "candidate_count": len(candidates),
        "candidate_missing_count": len(missing),
        "candidate_only_rank": int_value(candidate_only_audit.get("rank")),
        "candidate_only_unique_factor_relation_count": int_value(
            candidate_only_audit.get("unique_factor_relation_count")
        ),
        "group_factor_relation_count_gain": group_delta["factor_relation_count_gain"],
        "group_factor_variables_derivable_gain": group_delta["factor_variables_derivable_gain"],
        "group_rank_gain": group_delta["rank_gain"],
        "group_unique_factor_relation_gain": group_delta["unique_factor_relation_gain"],
        "with_candidates_rank": int_value(with_candidates_audit.get("rank")),
        "with_candidates_unique_factor_relation_count": int_value(
            with_candidates_audit.get("unique_factor_relation_count")
        ),
    }
    claim_status = determine_claim(summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p690_false_rank_certificate_factor_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p690_false_rank_certificate_factor_audit",
        "claim_status": claim_status,
        "artifacts": {"certificates": [str(path) for path in paths]},
        "parameters": {
            "candidate_keys": CANDIDATE_KEYS,
            "base_rule": "all listed direct certificate artifacts excluding exact candidate selected rows",
            "order": ORDER,
        },
        "summary": summary,
        "candidate_certificates": [selected_info(cert) | {"candidate_row_id": cert.get("_candidate_row_id")} for cert in candidates],
        "missing_candidates": missing,
        "base_audit": base_audit,
        "candidate_only_audit": candidate_only_audit,
        "with_candidates_audit": with_candidates_audit,
        "group_delta": group_delta,
        "per_candidate_scores": scores,
        "greedy_selected": greedy_selected,
        "score_summary": score_summary,
        "honesty_boundary": [
            "This audit tests exact P689 false-rank certificates against the current toy-prime order-9887 factor-bank representation.",
            "A unique-relation gain without rank gain is still dependent under the current base bank.",
            "A rank gain would remain an index-calculus precursor and would still require source-generation, matrix, and target-descent accounting.",
            "A no-gain result narrows these two rows only; it does not rule out other false-rank rows or other representations.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, "summary": summary, "group_delta": group_delta}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
