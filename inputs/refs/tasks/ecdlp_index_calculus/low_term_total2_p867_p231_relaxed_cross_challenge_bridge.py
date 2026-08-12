#!/usr/bin/env python3
"""P867 relaxed cross-challenge bridge audit for p231 full-form rows."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p867_p231_relaxed_cross_challenge_bridge.md"
DEFAULT_P866 = STATE_DIR / "low_term_total2_p866_p231_full_form_rank_target_join_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p867_p231_relaxed_cross_challenge_bridge_probe.json"
SCHEMA = "ecdlp.low_term_total2_p867_p231_relaxed_cross_challenge_bridge.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def round_float(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def normalize_offsets(values: list[int]) -> list[int]:
    if not values:
        return []
    base = min(values)
    return [int(value) - base for value in values]


def invertible(value: int, modulus: int) -> bool:
    return modulus > 1 and math.gcd(value % modulus, modulus) == 1


def normalized_tail_coeffs(tail_items: list[tuple[int, int]], modulus: int) -> list[int] | None:
    if not tail_items:
        return []
    first = tail_items[0][1] % modulus
    if not invertible(first, modulus):
        return None
    inv = pow(first, -1, modulus)
    return [(coeff * inv) % modulus for _index, coeff in tail_items]


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def context_key(group: dict[str, Any]) -> str:
    return json_key(
        {
            "base_hash": group.get("base_hash"),
            "challenge_seed": group.get("challenge_seed"),
            "order": group.get("order"),
            "p": group.get("p"),
            "public_hash": group.get("public_hash"),
        }
    )


def group_id(group: dict[str, Any]) -> str:
    return f"{group.get('window')}:{group.get('transfer_index')}:{group.get('target')}"


def flatten_records(p866: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in p866.get("full_form_groups") or []:
        order = int_value(group.get("order"))
        if order <= 1:
            errors.append({"group": group_id(group), "error": "missing_or_invalid_order"})
            continue
        expected_secret = (group.get("union") or {}).get("union_derived_secret")
        gid = group_id(group)
        ckey = context_key(group)
        for form_index, form in enumerate(group.get("form_records") or []):
            coeffs = [int_value(coeff) % order for coeff in form.get("coeffs") or []]
            rhs = int_value(form.get("rhs")) % order
            tail_items = [(idx, coeff) for idx, coeff in enumerate(coeffs) if idx != 0 and coeff % order != 0]
            tail_support = [idx for idx, _coeff in tail_items]
            terms = [int_value(term) for term in form.get("terms") or []]
            tail_gaps = normalize_offsets(tail_support)
            term_gaps = normalize_offsets(terms)
            normalized_coeffs = normalized_tail_coeffs(tail_items, order)
            if normalized_coeffs is None:
                errors.append(
                    {
                        "group": gid,
                        "form_index": form_index,
                        "error": "noninvertible_tail_coefficient",
                        "tail_items": tail_items,
                    }
                )
            tail_coeffs = [coeff for _idx, coeff in tail_items]
            exact_tail_expression = {
                "tail_coeffs": tail_coeffs,
                "tail_support": tail_support,
                "terms": terms,
            }
            skeleton = {
                "normalized_tail_coeffs": normalized_coeffs,
                "tail_support_gaps": tail_gaps,
                "term_gaps": term_gaps,
            }
            records.append(
                {
                    "anchor_coeff": coeffs[0] if coeffs else 0,
                    "challenge_seed": group.get("challenge_seed"),
                    "context_key": ckey,
                    "coeffs": coeffs,
                    "exact_tail_expression_key": json_key(exact_tail_expression),
                    "expected_secret": expected_secret,
                    "form_index": form_index,
                    "generic_rho_steps": group.get("generic_rho_steps"),
                    "group_id": gid,
                    "ops_over_rho": group.get("ops_over_rho"),
                    "order": order,
                    "projection_keys": {
                        "support_exact": json_key({"support": form.get("support") or []}),
                        "support_terms_exact": json_key(
                            {"support": form.get("support") or [], "terms": terms}
                        ),
                        "tail_coeff_skeleton": json_key(
                            {
                                "normalized_tail_coeffs": normalized_coeffs,
                                "tail_support_gaps": tail_gaps,
                            }
                        ),
                        "tail_skeleton": json_key(skeleton),
                        "tail_support_gaps": json_key({"tail_support_gaps": tail_gaps}),
                        "term_gaps": json_key({"term_gaps": term_gaps}),
                    },
                    "rhs": rhs,
                    "row_key": form.get("row_key"),
                    "skeleton": skeleton,
                    "support": form.get("support") or [],
                    "tail_coeffs": tail_coeffs,
                    "tail_support": tail_support,
                    "target": group.get("target"),
                    "terms": terms,
                    "transfer_index": group.get("transfer_index"),
                    "union_public_key_verified": (group.get("union") or {}).get("union_public_key_verified"),
                    "window": group.get("window"),
                }
            )
    return records, errors


def local_derivations(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_group_and_expr: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_group_and_expr[(record["group_id"], record["exact_tail_expression_key"])].append(record)

    derivations = []
    for (_gid, exact_key), items in sorted(by_group_and_expr.items()):
        if len(items) < 2:
            continue
        sorted_items = sorted(items, key=lambda item: (str(item.get("row_key")), item.get("anchor_coeff"), item.get("rhs")))
        for left_index, left in enumerate(sorted_items):
            for right in sorted_items[left_index + 1 :]:
                order = int_value(left.get("order"))
                anchor_delta = (int_value(left.get("anchor_coeff")) - int_value(right.get("anchor_coeff"))) % order
                rhs_delta = (int_value(left.get("rhs")) - int_value(right.get("rhs"))) % order
                if not invertible(anchor_delta, order):
                    derivations.append(
                        {
                            "anchor_delta": anchor_delta,
                            "candidate_secret": None,
                            "exact_tail_expression_key": exact_key,
                            "group_id": left["group_id"],
                            "invertible_anchor_delta": False,
                            "order": order,
                            "reason": "noninvertible_anchor_delta",
                            "rhs_delta": rhs_delta,
                        }
                    )
                    continue
                candidate = (rhs_delta * pow(anchor_delta, -1, order)) % order
                expected = left.get("expected_secret")
                derivations.append(
                    {
                        "anchor_delta": anchor_delta,
                        "anchors": [left.get("anchor_coeff"), right.get("anchor_coeff")],
                        "candidate_secret": candidate,
                        "challenge_seed": left.get("challenge_seed"),
                        "context_key": left.get("context_key"),
                        "exact_tail_expression_key": exact_key,
                        "expected_secret": expected,
                        "group_id": left["group_id"],
                        "invertible_anchor_delta": True,
                        "matches_expected_secret": expected is not None and int_value(expected) % order == candidate,
                        "ops_over_rho": round_float(left.get("ops_over_rho")),
                        "order": order,
                        "rhs_delta": rhs_delta,
                        "rhs_values": [left.get("rhs"), right.get("rhs")],
                        "row_keys": [left.get("row_key"), right.get("row_key")],
                        "support": left.get("support"),
                        "tail_coeffs": left.get("tail_coeffs"),
                        "tail_support": left.get("tail_support"),
                        "target": left.get("target"),
                        "terms": left.get("terms"),
                        "transfer_index": left.get("transfer_index"),
                        "union_public_key_verified": left.get("union_public_key_verified"),
                        "window": left.get("window"),
                    }
                )
    return derivations


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "anchor_coeff": record.get("anchor_coeff"),
        "group_id": record.get("group_id"),
        "rhs": record.get("rhs"),
        "row_key": record.get("row_key"),
        "support": record.get("support"),
        "tail_coeffs": record.get("tail_coeffs"),
        "tail_support": record.get("tail_support"),
        "terms": record.get("terms"),
        "transfer_index": record.get("transfer_index"),
        "window": record.get("window"),
    }


def analyze_projection(
    projection: str,
    records: list[dict[str, Any]],
    derivations: list[dict[str, Any]],
) -> dict[str, Any]:
    motifs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        motifs[record["projection_keys"][projection]].append(record)

    derivations_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for derivation in derivations:
        if derivation.get("candidate_secret") is not None:
            derivations_by_group[str(derivation.get("group_id"))].append(derivation)

    motif_rows = []
    for key, items in sorted(motifs.items(), key=lambda entry: entry[0]):
        contexts = sorted({str(item.get("context_key")) for item in items})
        groups = sorted({str(item.get("group_id")) for item in items})
        local = []
        for group in groups:
            group_items = [item for item in items if item.get("group_id") == group]
            exact_keys = {item.get("exact_tail_expression_key") for item in group_items}
            for derivation in derivations_by_group.get(group, []):
                if derivation.get("exact_tail_expression_key") in exact_keys:
                    local.append(derivation)
        matched_contexts = sorted(
            {
                str(derivation.get("context_key"))
                for derivation in local
                if derivation.get("matches_expected_secret")
            }
        )
        row = {
            "context_count": len(contexts),
            "form_count": len(items),
            "group_count": len(groups),
            "groups": groups,
            "key": key,
            "local_derivation_count": len(local),
            "matched_local_derivation_count": sum(1 for derivation in local if derivation.get("matches_expected_secret")),
            "matched_local_derivation_context_count": len(matched_contexts),
            "sample_forms": [compact_record(item) for item in items[:8]],
            "sample_local_derivations": local[:8],
        }
        motif_rows.append(row)

    top = sorted(
        motif_rows,
        key=lambda row: (
            -int_value(row.get("context_count")),
            -int_value(row.get("matched_local_derivation_context_count")),
            -int_value(row.get("local_derivation_count")),
            -int_value(row.get("form_count")),
            str(row.get("key")),
        ),
    )
    return {
        "cross_context_motif_count": sum(1 for row in motif_rows if int_value(row.get("context_count")) >= 2),
        "max_context_count": max((int_value(row.get("context_count")) for row in motif_rows), default=0),
        "motif_count": len(motif_rows),
        "motifs_with_local_derivations": sum(1 for row in motif_rows if int_value(row.get("local_derivation_count")) > 0),
        "projection": projection,
        "top_motifs": top[:12],
    }


def bridge_candidates(projection_audits: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for projection in ("tail_skeleton", "tail_coeff_skeleton", "tail_support_gaps", "term_gaps"):
        for motif in projection_audits[projection]["top_motifs"]:
            if (
                int_value(motif.get("context_count")) >= 2
                and int_value(motif.get("matched_local_derivation_context_count")) >= 2
            ):
                candidates.append(
                    {
                        **motif,
                        "projection": projection,
                    }
                )
    return sorted(
        candidates,
        key=lambda row: (
            -int_value(row.get("context_count")),
            -int_value(row.get("matched_local_derivation_context_count")),
            -int_value(row.get("matched_local_derivation_count")),
            str(row.get("projection")),
            str(row.get("key")),
        ),
    )


def determine_claim(errors: list[dict[str, Any]], candidates: list[dict[str, Any]], audits: dict[str, dict[str, Any]]) -> str:
    if errors:
        return "P867_RELAXED_BRIDGE_SIGNAL_WITH_NORMALIZATION_WARNINGS"
    if candidates:
        return "P867_RELAXED_TAIL_SKELETON_RECURS_WITH_VERIFIED_LOCAL_DERIVATIONS"
    if any(int_value(audit.get("cross_context_motif_count")) > 0 for audit in audits.values()):
        return "P867_RELAXED_PROJECTION_OVERLAP_WITHOUT_VERIFIED_DERIVATIONS"
    return "NEGATIVE_RESULT_P867_NO_RELAXED_CROSS_CONTEXT_BRIDGE"


def summarize(
    records: list[dict[str, Any]],
    derivations: list[dict[str, Any]],
    audits: dict[str, dict[str, Any]],
    candidates: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    claim: str,
) -> dict[str, Any]:
    groups = sorted({str(record.get("group_id")) for record in records})
    contexts = sorted({str(record.get("context_key")) for record in records})
    matched_derivations = [derivation for derivation in derivations if derivation.get("matches_expected_secret")]
    best = candidates[0] if candidates else None
    return {
        "best_bridge_context_count": int_value(best.get("context_count")) if best else 0,
        "best_bridge_key": best.get("key") if best else None,
        "best_bridge_local_derivation_context_count": (
            int_value(best.get("matched_local_derivation_context_count")) if best else 0
        ),
        "best_bridge_projection": best.get("projection") if best else None,
        "bridge_candidate_count": len(candidates),
        "claim_status": claim,
        "context_count": len(contexts),
        "error_count": len(errors),
        "exact_support_term_cross_context_motifs": audits["support_terms_exact"]["cross_context_motif_count"],
        "legal_cross_context_target_join_count": 0,
        "local_derivation_count": len(derivations),
        "matched_local_derivation_count": len(matched_derivations),
        "matched_local_derivation_group_count": len({str(item.get("group_id")) for item in matched_derivations}),
        "source_form_count": len(records),
        "source_group_count": len(groups),
        "tail_skeleton_cross_context_motifs": audits["tail_skeleton"]["cross_context_motif_count"],
        "tail_skeleton_max_context_count": audits["tail_skeleton"]["max_context_count"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p866 = load_json(args.p866)
    records, errors = flatten_records(p866)
    derivations = local_derivations(records)
    projection_names = [
        "support_exact",
        "support_terms_exact",
        "tail_support_gaps",
        "term_gaps",
        "tail_coeff_skeleton",
        "tail_skeleton",
    ]
    audits = {name: analyze_projection(name, records, derivations) for name in projection_names}
    candidates = bridge_candidates(audits)
    claim = determine_claim(errors, candidates, audits)
    summary = summarize(records, derivations, audits, candidates, errors, claim)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p866_source": str(args.p866),
            "script": str(Path(__file__)),
        },
        "bridge_candidates": candidates[:12],
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P867_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "PROJECTION BOUNDARY: relaxed motifs compare normalized form structure; they are not legal cross-context matrices.",
            "DERIVATION BOUNDARY: local derivations are computed only from same-context pairs with identical non-anchor expressions.",
            "TARGET-DESCENT BOUNDARY: recurring skeletons are target-descent leads, not solved individual logarithm descent.",
            "POLLARD-RHO BOUNDARY: this is index-calculus bridge evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "local_derivations": derivations,
        "method": "p867_p231_relaxed_cross_challenge_bridge",
        "projection_audits": audits,
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "P866 full-form rows are the complete source set for this bridge audit.",
                "A recurring normalized tail skeleton is only a construction target until fresh rows verify it.",
                "Same-target labels do not permit cross-context matrix mixing.",
            ],
            "claim_or_task": "Audit whether P866 forms expose a relaxed public skeleton for cross-challenge target descent.",
            "evidence_so_far": [
                f"Tail-skeleton cross-context motifs: {summary['tail_skeleton_cross_context_motifs']}.",
                f"Matched local derivation contexts in best bridge: {summary['best_bridge_local_derivation_context_count']}.",
                f"Exact support/term cross-context motifs: {summary['exact_support_term_cross_context_motifs']}.",
            ],
            "failure_modes": [
                "The recurring skeleton may be an artifact of adjacent frozen-prefix windows.",
                "A local same-skeleton derivation does not by itself give a cross-public-key bridge.",
                "The selector still depends on saved P866 rows and needs fresh public generation.",
            ],
            "next_concrete_action": (
                "Build P868 as a fresh-window public skeleton selector/generator for the recurring relaxed tail skeleton, then measure whether it emits same-motif local pairs below rho without using saved relation events."
            ),
            "status": "OBSERVATION" if claim.startswith("P867_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p866", type=Path, default=DEFAULT_P866)
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
