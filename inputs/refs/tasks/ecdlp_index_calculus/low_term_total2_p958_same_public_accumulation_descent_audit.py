#!/usr/bin/env python3
"""P958 same-public accumulation/descent audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_dependency_circuit_probe as dependency_circuit_probe  # noqa: E402
import low_term_total2_fixed_leaf_shared_product_gate_probe as product_gate  # noqa: E402
import low_term_total2_p957_topk4_relation_matrix_sufficiency_audit as p957  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p958_same_public_accumulation_descent_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p958_same_public_accumulation_descent_probe.json"
SCHEMA = "ecdlp.low_term_total2_p958_same_public_accumulation_descent.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def event_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    coeffs, rhs, _terms = event["form"]
    return tuple(int(value) for value in coeffs), int(rhs)


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    return {
        "case_key": event.get("case_key"),
        "coeffs": [int(value) for value in coeffs],
        "rhs": int(rhs),
        "row_key": event.get("row_key"),
        "terms": [int(value) for value in terms],
        "transfer_index": event.get("transfer_index"),
    }


def public_derive(verifier: Any, built: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    return dependency_circuit_probe.public_derive_from_events(
        verifier,
        [{"form": event["form"]} for event in events],
        int(built["order"]),
        built["base"],
        built["public"],
        built["ainvs"],
        int(built["p"]),
    )


def replay_case_full(
    case: dict[str, Any],
    source_cache: dict[str, dict[str, Any]],
    spec_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]]]],
) -> dict[str, Any]:
    source_path = str(case.get("source") or "")
    if not source_path:
        return {**case, "replay_error": "missing source path"}
    if source_path not in source_cache:
        source_cache[source_path] = product_gate.load_json(Path(source_path))
    source = source_cache[source_path]
    if source_path not in spec_cache:
        spec_cache[source_path] = repair_probe.build_specs(repair_probe.source_parameters(source))
    verifier, records, config_source, specs_by_target = spec_cache[source_path]
    probe_args = repair_probe.probe_args_from_source(source)
    source_case = p957.find_source_case(source, str(case.get("target")), case)
    if source_case is None:
        return {**case, "replay_error": "source case not found"}

    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    contexts = product_gate.build_case_contexts(
        source,
        source_case,
        verifier,
        records,
        config_source,
        specs_by_target,
        probe_args,
        context_cache,
    )
    direct_rows, direct_ops, rho, _profiles, union = product_gate.direct_profiles(verifier, contexts)
    first_built = contexts[0]["built"] if contexts else {}
    case_key = f"{case.get('window')}:{case.get('transfer_index')}:{p957.row_salt_signature(case.get('row_keys') or [])}"
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for direct_row in direct_rows:
        scan = direct_row["_scan"]
        for event in scan.get("relation_events") or []:
            coeffs, rhs, terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(
                {
                    "case_key": case_key,
                    "form": (key[0], key[1], [int(term) for term in terms]),
                    "leaf_index": event.get("leaf_index"),
                    "row_key": str(direct_row["row_key"]),
                    "transfer_index": p957.int_value(case.get("transfer_index")),
                }
            )
    order = p957.int_value(first_built.get("order"))
    replay = {
        **case,
        "case_key": case_key,
        "challenge_seed": first_built.get("challenge_seed"),
        "coefficient_rank": p957.modular_rank([event["form"][0] for event in events], order) if order else 0,
        "events": events,
        "form_count": len(events),
        "order": order,
        "p": p957.int_value(first_built.get("p")),
        "public": list(first_built.get("public") or []),
        "replay_direct_ops": int(direct_ops),
        "replay_direct_ops_over_rho": p957.ratio(direct_ops, rho) if rho else None,
        "replay_rho": int(rho),
        "replay_union_derived_secret": union.get("union_derived_secret"),
        "replay_union_public_key_verified": bool(union.get("union_public_key_verified")),
        "replay_union_rank": p957.int_value(union.get("union_rank")),
        "replay_union_relation_count": p957.int_value(union.get("union_relation_count")),
        "_built": first_built,
        "_verifier": verifier,
    }
    replay["matches_stored"] = bool(
        replay["replay_union_public_key_verified"]
        and replay["replay_union_derived_secret"] == case.get("direct_union_derived_secret")
        and replay["replay_union_rank"] == p957.int_value(case.get("direct_union_rank"))
        and replay["replay_union_relation_count"] == p957.int_value(case.get("direct_union_relation_count"))
    )
    return replay


def compact_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_key": row.get("case_key"),
        "coefficient_rank": row.get("coefficient_rank"),
        "form_count": row.get("form_count"),
        "ops": row.get("replay_direct_ops"),
        "ops_over_rho": row.get("replay_direct_ops_over_rho"),
        "row_keys": row.get("row_keys"),
        "secret": row.get("replay_union_derived_secret"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }


def analyze_public_group(public: tuple[int, ...], rows: list[dict[str, Any]], rank_threshold: int) -> dict[str, Any]:
    rows = sorted(
        rows,
        key=lambda row: (
            p957.float_value(row.get("replay_direct_ops_over_rho"), 10**18),
            p957.int_value(row.get("transfer_index")),
            str(row.get("case_key")),
        ),
    )
    first = rows[0]
    built = first["_built"]
    verifier = first["_verifier"]
    order = p957.int_value(first.get("order"))
    rho = max(p957.int_value(row.get("replay_rho")) for row in rows)
    seen: set[tuple[tuple[int, ...], int]] = set()
    events: list[dict[str, Any]] = []
    cumulative_ops = 0
    rank_curve = []
    first_derived_at: dict[str, Any] | None = None
    max_rank_at: dict[str, Any] | None = None
    for index, row in enumerate(rows, start=1):
        cumulative_ops += p957.int_value(row.get("replay_direct_ops"))
        before = len(events)
        for event in row.get("events") or []:
            key = event_key(event)
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
        derived = public_derive(verifier, built, events)
        curve_row = {
            "case_count": index,
            "cumulative_ops": cumulative_ops,
            "cumulative_ops_over_rho": p957.ratio(cumulative_ops, rho),
            "derived_secret": derived.get("derived_secret"),
            "new_unique_forms": len(events) - before,
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": p957.int_value(derived.get("rank")),
            "transfer_index": p957.int_value(row.get("transfer_index")),
            "unique_form_count": len(events),
        }
        rank_curve.append(curve_row)
        if curve_row["public_key_verified"] and first_derived_at is None:
            first_derived_at = curve_row
        if max_rank_at is None or curve_row["rank"] > p957.int_value(max_rank_at.get("rank")):
            max_rank_at = curve_row

    final_derived = public_derive(verifier, built, events)
    single_ranks = [p957.int_value(row.get("coefficient_rank")) for row in rows]
    single_form_counts = [p957.int_value(row.get("form_count")) for row in rows]
    single_ops = [p957.int_value(row.get("replay_direct_ops")) for row in rows]
    row_pair_counts = Counter(tuple(sorted(str(value) for value in row.get("row_keys") or [])) for row in rows)
    final_rank = p957.int_value(final_derived.get("rank"))
    rank_gain = final_rank - max(single_ranks, default=0)
    cumulative_ops_over_rho = p957.ratio(sum(single_ops), rho)
    return {
        "case_count": len(rows),
        "cumulative_ops": sum(single_ops),
        "cumulative_ops_over_rho": cumulative_ops_over_rho,
        "derived_secret": final_derived.get("derived_secret"),
        "first_derived_at": first_derived_at,
        "max_rank_at": max_rank_at,
        "matrix_ready": bool(final_rank >= rank_threshold and (cumulative_ops_over_rho or 10**18) <= 1.0),
        "max_single_form_count": max(single_form_counts, default=0),
        "max_single_rank": max(single_ranks, default=0),
        "public": list(public),
        "public_key_verified": bool(final_derived.get("public_key_verified")),
        "rank": final_rank,
        "rank_curve": rank_curve,
        "rank_gain_over_best_single": rank_gain,
        "rho": rho,
        "row_pair_reuse": [
            {"count": count, "row_keys": list(row_keys)}
            for row_keys, count in row_pair_counts.most_common(5)
        ],
        "sample_cases": [compact_case(row) for row in rows[:5]],
        "secrets": sorted({p957.int_value(row.get("replay_union_derived_secret")) for row in rows}),
        "transfer_indices": [p957.int_value(row.get("transfer_index")) for row in rows],
        "unique_form_count": len(events),
        "unique_form_gain_over_best_single": len(events) - max(single_form_counts, default=0),
    }


def summarize(groups: list[dict[str, Any]], replayed: list[dict[str, Any]], selected_total: int) -> dict[str, Any]:
    ok = [row for row in replayed if not row.get("replay_error")]
    matching = [row for row in ok if row.get("matches_stored")]
    multi = [group for group in groups if p957.int_value(group.get("case_count")) > 1]
    rank_gain = [group for group in groups if p957.int_value(group.get("rank_gain_over_best_single")) > 0]
    matrix_ready = [group for group in groups if group.get("matrix_ready")]
    max_rank = max((p957.int_value(group.get("rank")) for group in groups), default=0)
    max_forms = max((p957.int_value(group.get("unique_form_count")) for group in groups), default=0)
    largest_group = max((p957.int_value(group.get("case_count")) for group in groups), default=0)
    best_rank_group = max(
        groups,
        key=lambda group: (
            p957.int_value(group.get("rank")),
            p957.int_value(group.get("unique_form_count")),
            -p957.float_value(group.get("cumulative_ops_over_rho"), 10**18),
        ),
        default={},
    )
    best_rank_gain_group = max(
        groups,
        key=lambda group: (
            p957.int_value(group.get("rank_gain_over_best_single")),
            p957.int_value(group.get("rank")),
            -p957.float_value(group.get("cumulative_ops_over_rho"), 10**18),
        ),
        default={},
    )
    claim = (
        "P958_SAME_PUBLIC_MATRIX_READY"
        if matrix_ready
        else "P958_SAME_PUBLIC_RANK_GROWTH_THIN_COST_BOUNDARY"
        if rank_gain
        else "NEGATIVE_RESULT_P958_SAME_PUBLIC_ACCUMULATION_NO_RANK_GAIN"
    )
    return {
        "best_rank_group_public": best_rank_group.get("public"),
        "best_rank_group_rank": best_rank_group.get("rank"),
        "best_rank_group_cumulative_ops_over_rho": best_rank_group.get("cumulative_ops_over_rho"),
        "best_rank_gain_group_public": best_rank_gain_group.get("public"),
        "best_rank_gain_over_best_single": best_rank_gain_group.get("rank_gain_over_best_single"),
        "claim_status": claim,
        "largest_same_public_group_size": largest_group,
        "matching_replay_count": len(matching),
        "matrix_ready_group_count": len(matrix_ready),
        "max_same_public_rank": max_rank,
        "max_same_public_unique_forms": max_forms,
        "multi_case_same_public_group_count": len(multi),
        "rank_gain_same_public_group_count": len(rank_gain),
        "replay_error_count": len([row for row in replayed if row.get("replay_error")]),
        "replayed_count": len(replayed),
        "same_public_group_count": len(groups),
        "selected_topk4_below_rho_total": selected_total,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    cases = p957.selected_topk4_cases(Path(args.state_dir), int(args.post_min), args.target)
    if int(args.max_cases) > 0:
        cases = cases[: int(args.max_cases)]
    source_cache: dict[str, dict[str, Any]] = {}
    spec_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]]]] = {}
    replayed = [replay_case_full(case, source_cache, spec_cache) for case in cases]
    ok = [row for row in replayed if not row.get("replay_error")]
    grouped: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in ok:
        grouped[tuple(int(value) for value in row.get("public") or [])].append(row)
    groups = [analyze_public_group(public, rows, int(args.rank_threshold)) for public, rows in grouped.items()]
    groups.sort(
        key=lambda group: (
            -p957.int_value(group.get("rank_gain_over_best_single")),
            -p957.int_value(group.get("rank")),
            -p957.int_value(group.get("case_count")),
            p957.float_value(group.get("cumulative_ops_over_rho"), 10**18),
        )
    )
    summary = summarize(groups, replayed, len(cases))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p957_source": str(p957.DEFAULT_OUT),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "groups": groups[: int(args.group_limit)],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "SAME-PUBLIC-SCOPE: rank/cost credit is granted only inside exact public-key groups.",
            "NO-CROSS-PUBLIC-MATRIX-CREDIT: aggregate P957 rank across different public challenges remains a boundary, not a matrix step.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this tests relation accumulation and descent readiness, not full relation collection or deployed-curve complexity.",
        ],
        "method": "p958_same_public_accumulation_descent_audit",
        "parameters": {
            "max_cases": int(args.max_cases),
            "post_min": int(args.post_min),
            "rank_threshold": int(args.rank_threshold),
            "target": args.target,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p957.DEFAULT_POST_MIN)
    parser.add_argument("--rank-threshold", type=int, default=8)
    parser.add_argument("--max-cases", type=int, default=0, help="0 means replay all selected cases")
    parser.add_argument("--group-limit", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selected={summary['selected_topk4_below_rho_total']} "
        f"replayed={summary['replayed_count']} "
        f"matches={summary['matching_replay_count']} "
        f"errors={summary['replay_error_count']} "
        f"groups={summary['same_public_group_count']} "
        f"multi_groups={summary['multi_case_same_public_group_count']} "
        f"rank_gain_groups={summary['rank_gain_same_public_group_count']} "
        f"max_rank={summary['max_same_public_rank']} "
        f"max_forms={summary['max_same_public_unique_forms']} "
        f"matrix_ready_groups={summary['matrix_ready_group_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
