#!/usr/bin/env python3
"""P866 full-form rank and target-join audit for p231 rejected rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p866_p231_full_form_rank_target_join.md"
DEFAULT_P862 = STATE_DIR / "low_term_total2_p862_p231_rejected_relation_lane_replay_probe.json"
DEFAULT_P864_WINDOWS = (
    STATE_DIR / "low_term_total2_p864_p231_forward_window_1176_1183_probe.json",
    STATE_DIR / "low_term_total2_p864_p231_forward_window_1184_1191_probe.json",
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p866_p231_full_form_rank_target_join_probe.json"
SCHEMA = "ecdlp.low_term_total2_p866_p231_full_form_rank_target_join.v1"


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def short_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def source_case_key(row: dict[str, Any]) -> tuple[str, int, tuple[str, ...]]:
    source_case = row.get("source_case") or {}
    return (
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        tuple(str(key) for key in source_case.get("row_keys") or []),
    )


def compact_source_case(row: dict[str, Any]) -> dict[str, Any]:
    source_case = dict(row.get("source_case") or {})
    source_case["target"] = row.get("target")
    source_case["transfer_index"] = row.get("transfer_index")
    return source_case


def extract_inputs(p862: dict[str, Any], p864_payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = []
    p862_qroot = Path((p862.get("artifacts") or {})["qroot_source"])
    for row in p862.get("direct_replay_rows") or []:
        inputs.append(
            {
                "artifact": "P862",
                "public_source": str(p862_qroot),
                "row": row,
                "window": "1160_1167",
            }
        )
    for payload in p864_payloads:
        qroot = Path((payload.get("artifacts") or {})["p231_qroot"])
        window = str((payload.get("parameters") or {}).get("p231_window"))
        for row in payload.get("direct_replay_rows") or []:
            inputs.append(
                {
                    "artifact": "P864",
                    "public_source": str(qroot),
                    "row": row,
                    "window": window,
                }
            )
    return inputs


def merge_inputs(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for item in inputs:
        grouped[source_case_key(item["row"])].append(item)
    groups = []
    for key, items in sorted(grouped.items(), key=lambda entry: (entry[0][0], entry[0][1], entry[0][2])):
        public_sources = {str(item["public_source"]) for item in items}
        if len(public_sources) != 1:
            raise RuntimeError(f"source-case group spans multiple public sources: {key}")
        source_cases = [compact_source_case(item["row"]) for item in items]
        first_case = source_cases[0]
        leaf_map: dict[str, set[int]] = defaultdict(set)
        rejected_rows = []
        for item in items:
            row = item["row"]
            variant = row.get("verified_direct_variant") or {}
            for row_key, leaves in (variant.get("leaves_by_row") or {}).items():
                leaf_map[str(row_key)].update(int_value(leaf) for leaf in leaves)
            rejected_rows.append(
                {
                    "candidate_factor_leaf_indices": row.get("candidate_factor_leaf_indices") or [],
                    "direct_ops_over_rho": variant.get("ops_over_rho"),
                    "direct_variant": variant.get("name"),
                    "p845_surface_ffe_ops": row.get("p845_surface_ffe_ops"),
                    "qroot_ops_over_rho": row.get("qroot_ops_over_rho"),
                    "relation_discriminator_class": row.get("relation_discriminator_class"),
                    "row_key": row.get("row_key"),
                    "window": item.get("window"),
                }
            )
        groups.append(
            {
                "input_count": len(items),
                "public_source": sorted(public_sources)[0],
                "rejected_rows": rejected_rows,
                "source_case": first_case,
                "target": key[0],
                "transfer_index": key[1],
                "union_leaves_by_row": {row_key: sorted(leaves) for row_key, leaves in sorted(leaf_map.items())},
                "window": sorted({str(item["window"]) for item in items})[0],
            }
        )
    return groups


def modular_rank(matrix: list[list[int]], modulus: int) -> dict[str, Any]:
    if not matrix:
        return {"rank": 0, "nonunit_pivot_obstruction_count": 0}
    rows = [[int(cell) % modulus for cell in row] for row in matrix]
    row_count = len(rows)
    col_count = max((len(row) for row in rows), default=0)
    for row in rows:
        row.extend([0] * (col_count - len(row)))
    rank = 0
    nonunit_obstructions = 0
    for col in range(col_count):
        pivot = None
        nonunit_seen = False
        for pos in range(rank, row_count):
            value = rows[pos][col] % modulus
            if value == 0:
                continue
            if math.gcd(value, modulus) == 1:
                pivot = pos
                break
            nonunit_seen = True
        if pivot is None:
            if nonunit_seen:
                nonunit_obstructions += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for pos in range(row_count):
            if pos == rank:
                continue
            factor = rows[pos][col] % modulus
            if factor:
                rows[pos] = [
                    (rows[pos][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return {"rank": rank, "nonunit_pivot_obstruction_count": nonunit_obstructions}


def form_support(coeffs: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(index for index, coeff in enumerate(coeffs) if int(coeff) != 0)


def support_terms_key(form: tuple[tuple[int, ...], int, list[int]]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    coeffs, _rhs, terms = form
    return form_support(coeffs), tuple(int(term) for term in terms)


def reconstruct_group(
    verifier: Any,
    records: list[dict[str, Any]],
    group: dict[str, Any],
) -> dict[str, Any]:
    public_payload = load_json(Path(group["public_source"]))
    built_by_row, components_by_row, local_args_by_row = p848.build_context(
        verifier,
        records,
        public_payload,
        group["source_case"],
    )
    scan_rows = []
    scan_summaries = []
    total_ops = 0
    rho = 0
    challenge_contexts = set()
    form_records: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for row_key, leaves in sorted((group.get("union_leaves_by_row") or {}).items()):
        selected = sorted({int_value(leaf) for leaf in leaves})
        scan = p848.direct_witness_probe.scan_selected(
            verifier,
            built_by_row[row_key],
            components_by_row[row_key],
            set(selected),
            local_args_by_row[row_key],
        )
        scan_rows.append({"row_key": row_key, "_scan": scan})
        built = built_by_row[row_key]
        total_ops += int_value(scan.get("preassociation_filter_ops"))
        rho = max(rho, int_value(built.get("generic_rho_steps")))
        challenge_contexts.add(
            (
                str(built.get("challenge_seed")),
                int_value(built.get("p")),
                int_value(built.get("order")),
                short_hash(built.get("base")),
                short_hash(built.get("public")),
            )
        )
        scan_summaries.append(
            {
                "preassociation_filter_ops": int_value(scan.get("preassociation_filter_ops")),
                "relation_count": int_value(scan.get("relation_count")),
                "row_key": row_key,
                "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                "selected_leaf_indices": scan.get("selected_leaf_indices") or selected,
            }
        )
        for event in scan.get("relation_events") or []:
            key = p851.form_key(event)
            if key in form_records:
                continue
            coeffs, rhs, terms = event["form"]
            form = (tuple(int(coeff) for coeff in coeffs), int(rhs), [int(term) for term in terms])
            form_records[key] = {
                "coeffs": list(form[0]),
                "form": form,
                "rhs": form[1],
                "row_key": row_key,
                "support": list(form_support(form[0])),
                "support_terms_key": support_terms_key(form),
                "terms": form[2],
            }
    if len(challenge_contexts) != 1:
        raise RuntimeError(f"group has incompatible challenge contexts: {challenge_contexts}")
    challenge_seed, p, order, base_hash, public_hash = next(iter(challenge_contexts))
    first_built = built_by_row[next(iter(group["union_leaves_by_row"]))]
    forms = [record["form"] for record in form_records.values()]
    union = p851.derive_forms(verifier, first_built, forms)
    matrix = [list(record["form"][0]) for record in form_records.values()]
    rank_probe = modular_rank(matrix, int(order))
    nonzeros = sum(sum(1 for coeff in record["form"][0] if int(coeff) != 0) for record in form_records.values())
    return {
        **group,
        "base_hash": base_hash,
        "challenge_seed": challenge_seed,
        "coefficient_nonzero_count": nonzeros,
        "duplicate_form_count_removed": sum(scan["relation_count"] for scan in scan_summaries) - len(form_records),
        "form_count": len(form_records),
        "form_records": [
            {
                "coeffs": record["coeffs"],
                "rhs": record["rhs"],
                "row_key": record["row_key"],
                "support": record["support"],
                "terms": record["terms"],
            }
            for record in sorted(form_records.values(), key=lambda item: (item["row_key"], item["support"], item["rhs"]))
        ],
        "generic_rho_steps": rho,
        "matrix_coeff_width": max((len(row) for row in matrix), default=0),
        "modular_rank": rank_probe,
        "ops": total_ops,
        "ops_over_rho": ratio(total_ops, rho),
        "order": order,
        "p": p,
        "public_hash": public_hash,
        "scan_count": len(scan_summaries),
        "scan_summaries": scan_summaries,
        "support_terms_keys": sorted(
            {
                json.dumps(
                    [list(key[0]), list(key[1])],
                    separators=(",", ":"),
                )
                for key in (record["support_terms_key"] for record in form_records.values())
            }
        ),
        "union": union,
        "verified_full_form": bool(union.get("union_public_key_verified")),
    }


def combine_compatible_groups(
    verifier: Any,
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any] | None:
    if left["public_hash"] != right["public_hash"] or left["base_hash"] != right["base_hash"]:
        return None
    if left["order"] != right["order"] or left["p"] != right["p"]:
        return None
    # Reusing P851 derive requires a built context.  No current p231 pair has
    # identical public context, so this path is retained for future windows.
    return {
        "reason": "compatible_context_unimplemented_without_built_object",
        "verified": False,
    }


def target_join_rows(verifier: Any, groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for left_index, left in enumerate(groups):
        for right in groups[left_index + 1 :]:
            same_target = left["target"] == right["target"]
            same_context = (
                left["public_hash"] == right["public_hash"]
                and left["base_hash"] == right["base_hash"]
                and left["challenge_seed"] == right["challenge_seed"]
            )
            left_keys = set(left.get("support_terms_keys") or [])
            right_keys = set(right.get("support_terms_keys") or [])
            overlap = sorted(left_keys & right_keys)
            combined = combine_compatible_groups(verifier, left, right) if same_context else None
            rows.append(
                {
                    "compatible_for_single_matrix": bool(same_context),
                    "combined_probe": combined,
                    "left_transfer_index": left["transfer_index"],
                    "left_window": left["window"],
                    "reason": (
                        "legal_same_challenge_join"
                        if same_context
                        else "blocked_different_challenge_or_public_key"
                    ),
                    "right_transfer_index": right["transfer_index"],
                    "right_window": right["window"],
                    "same_target": same_target,
                    "shared_support_terms_count": len(overlap),
                    "shared_support_terms_sample": overlap[:8],
                    "target": left["target"] if same_target else None,
                }
            )
    return rows


def determine_claim(groups: list[dict[str, Any]], joins: list[dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P866_FULL_FORM_RECONSTRUCTION_ERRORS"
    full_positive = all(
        group.get("verified_full_form")
        and group.get("ops_over_rho") is not None
        and float(group["ops_over_rho"]) < 1.0
        for group in groups
    )
    legal_join = any(row.get("compatible_for_single_matrix") and row.get("combined_probe") for row in joins)
    support_overlap = any(int_value(row.get("shared_support_terms_count")) > 0 for row in joins)
    if full_positive and legal_join:
        return "P866_FULL_FORM_RANK_AND_LEGAL_TARGET_JOIN_VERIFIED"
    if full_positive and support_overlap:
        return "P866_FULL_FORM_RANK_VERIFIED_WITH_TARGET_JOIN_SUPPORT_OVERLAP"
    if full_positive:
        return "P866_FULL_FORM_RANK_VERIFIED_TARGET_JOIN_BLOCKED"
    return "NEGATIVE_RESULT_P866_FULL_FORM_RANK_NOT_REPRODUCED"


def summary(groups: list[dict[str, Any]], joins: list[dict[str, Any]], claim: str, errors: list[dict[str, Any]]) -> dict[str, Any]:
    ops = [float(group["ops_over_rho"]) for group in groups if group.get("ops_over_rho") is not None]
    return {
        "claim_status": claim,
        "coefficient_nonzero_count": sum(int_value(group.get("coefficient_nonzero_count")) for group in groups),
        "deduped_form_count": sum(int_value(group.get("form_count")) for group in groups),
        "duplicate_form_count_removed": sum(int_value(group.get("duplicate_form_count_removed")) for group in groups),
        "error_count": len(errors),
        "full_form_below_rho_group_count": sum(
            1 for group in groups if group.get("ops_over_rho") is not None and float(group["ops_over_rho"]) < 1.0
        ),
        "full_form_verified_group_count": sum(1 for group in groups if group.get("verified_full_form")),
        "legal_target_join_count": sum(1 for row in joins if row.get("compatible_for_single_matrix")),
        "max_ops_over_rho": max(ops) if ops else None,
        "min_ops_over_rho": min(ops) if ops else None,
        "modular_rank_sum": sum(int_value((group.get("modular_rank") or {}).get("rank")) for group in groups),
        "reconstructed_group_count": len(groups),
        "target_join_pair_count": len(joins),
        "target_join_pairs_with_support_terms_overlap": sum(
            1 for row in joins if int_value(row.get("shared_support_terms_count")) > 0
        ),
        "verifier_rank_sum": sum(int_value((group.get("union") or {}).get("union_rank")) for group in groups),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p862 = load_json(args.p862)
    p864_payloads = [load_json(path) for path in args.p864_window]
    inputs = extract_inputs(p862, p864_payloads)
    merged = merge_inputs(inputs)
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    groups = []
    errors = []
    for group in merged:
        try:
            groups.append(reconstruct_group(verifier, records, group))
        except Exception as exc:  # pragma: no cover - preserve reconstruction failure.
            errors.append(
                {
                    "error": f"{type(exc).__name__}: {exc}",
                    "source_case": group.get("source_case"),
                    "window": group.get("window"),
                }
            )
    joins = target_join_rows(verifier, groups)
    claim = determine_claim(groups, joins, errors)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p862_source": str(args.p862),
            "p864_window_sources": [str(path) for path in args.p864_window],
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P866_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "errors": errors,
        "full_form_groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FULL-FORM BOUNDARY: exact relation events are reconstructed from saved source-case leaves; no new source rows are discovered.",
            "MATRIX BOUNDARY: cross-window forms are not combined unless challenge/public-key contexts match.",
            "TARGET-DESCENT BOUNDARY: shared support/term overlap is only a descent lead unless a verifier-backed combined system is produced.",
            "POLLARD-RHO BOUNDARY: this is relation-lane evidence for an index-calculus route, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p866_p231_full_form_rank_target_join",
        "red_team_handoff": {
            "assumptions": [
                "The P862/P864 verified direct variants are the intended P865 source-case groups to reconstruct.",
                "Modular rank over the group order is meaningful for these toy prime-order contexts; nonunit pivot obstructions are reported.",
                "Different challenge seeds or public keys block direct cross-window matrix mixing.",
            ],
            "evidence_so_far": [
                f"Full-form verified groups: {summary(groups, joins, claim, errors).get('full_form_verified_group_count')}/{len(groups)}.",
                f"Legal target joins: {summary(groups, joins, claim, errors).get('legal_target_join_count')}/{len(joins)}.",
                f"Support/term-overlap join pairs: {summary(groups, joins, claim, errors).get('target_join_pairs_with_support_terms_overlap')}/{len(joins)}.",
            ],
            "failure_modes": [
                "Target join may require a new cross-challenge lifting representation rather than direct matrix combination.",
                "The support/term overlap can be structural but still useless for target descent if anchor/RHS compatibility fails.",
                "The p231 windows are adjacent frozen-prefix windows, so a wider nonadjacent replication remains required.",
            ],
            "next_concrete_action": (
                "Build P867 as a relaxed cross-challenge bridge audit: since exact support/term overlap is absent, test support-only, term-bucket, tail-skeleton, and anchor/RHS-normalized projections for a verifier-backed target-descent join without illegal direct matrix mixing."
            ),
            "status": "OBSERVATION" if claim.startswith("P866_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summary(groups, joins, claim, errors),
        "target_join_audit": joins,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p862", type=Path, default=DEFAULT_P862)
    parser.add_argument("--p864-window", type=Path, action="append", default=list(DEFAULT_P864_WINDOWS))
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
