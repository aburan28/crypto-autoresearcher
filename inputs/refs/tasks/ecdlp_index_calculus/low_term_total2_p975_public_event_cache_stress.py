#!/usr/bin/env python3
"""P975 public-event selected signed-pair cache stress."""

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

import low_term_total2_p957_topk4_relation_matrix_sufficiency_audit as p957  # noqa: E402
import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p970_rank4_from_p969_seed as p970  # noqa: E402
import low_term_total2_p973_adjacent_source_charge_decomposition as p973  # noqa: E402
import low_term_total2_p974_signed_pair_cache_emulation as p974  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p975_public_event_cache_stress.md"
DEFAULT_P969 = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
DEFAULT_P972 = STATE_DIR / "low_term_total2_p972_adjacent_public_event_source_generation_probe.json"
DEFAULT_P974 = STATE_DIR / "low_term_total2_p974_signed_pair_cache_emulation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p975_public_event_cache_stress_probe.json"
SCHEMA = "ecdlp.low_term_total2_p975_public_event_cache_stress.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def salt_number(row_key: str) -> int | None:
    short = str(row_key).rsplit(":", 1)[-1]
    if not short.startswith("salt"):
        return None
    try:
        return int(short.removeprefix("salt"))
    except ValueError:
        return None


def selected_topk4_scope(args: argparse.Namespace) -> dict[str, Any]:
    target_counts: Counter[str] = Counter()
    target_salts: dict[str, set[int]] = defaultdict(set)
    source_paths: set[str] = set()
    artifact_count = 0
    selected_case_count = 0
    for _start, _end, path in p957.direct_artifact_paths(Path(args.state_dir), int(args.post_min)):
        artifact_count += 1
        payload = p957.load_json(path)
        if payload.get("source"):
            source_paths.add(str(payload.get("source")))
        for case in payload.get("cases") or []:
            if not case.get("public_low_prefix_gate_selected"):
                continue
            if not case.get("direct_union_public_key_verified") or not case.get("direct_below_rho"):
                continue
            if str(case.get("selector")) != "mode_low_term_span_total3":
                continue
            if p957.int_value(case.get("top_k")) != 4:
                continue
            target = str(case.get("target"))
            selected_case_count += 1
            target_counts[target] += 1
            for row_key in case.get("row_keys") or []:
                salt = salt_number(str(row_key))
                if salt is not None:
                    target_salts[target].add(salt)
    cases, pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    p959_salts = sorted(
        {
            salt
            for pair in pairs
            for row_key in pair.get("row_keys") or []
            for salt in [salt_number(str(row_key))]
            if salt is not None
        }
    )
    target_salt_summary = {
        target: {
            "count": len(values),
            "max": max(values) if values else None,
            "min": min(values) if values else None,
            "salts": sorted(values),
        }
        for target, values in sorted(target_salts.items())
    }
    expected_salts = set(range(int(args.salt_min), int(args.salt_max) + 1))
    available_targets = set(target_counts)
    target_values = set(target_salts.get(args.target, set()))
    wider_or_disjoint = bool(
        any(target != args.target for target in available_targets)
        or (target_values and target_values != expected_salts)
    )
    return {
        "artifact_count": artifact_count,
        "available_targets": sorted(available_targets),
        "p959_case_count": len(cases),
        "p959_pair_count": len(pairs),
        "p959_target_salts": p959_salts,
        "selected_case_count": selected_case_count,
        "source_path_count": len(source_paths),
        "target_counts": dict(sorted(target_counts.items())),
        "target_salts": target_salt_summary,
        "wider_or_disjoint_scope_available": wider_or_disjoint,
    }


def public_event_candidates(args: argparse.Namespace, p972_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p972_payload.get("candidate_results") or []:
        if int_value(row.get("seed_ops")) > int(args.max_seed_ops):
            continue
        if int_value(row.get("candidate_event_count")) < int(args.min_candidate_event_count):
            continue
        rows.append(row)
    rows.sort(
        key=lambda row: (
            int_value(row.get("candidate_event_count"), 0) * -1,
            int_value(row.get("source_non_event_ops"), 10**9),
            str(row.get("added_signature") or ""),
        )
    )
    return rows


def compact_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "added_signature": row.get("added_signature"),
        "candidate_event_count": row.get("candidate_event_count"),
        "early_ops": (row.get("early_stop") or {}).get("ops"),
        "early_rank": (row.get("early_stop") or {}).get("rank"),
        "full_source_ops": row.get("full_source_ops"),
        "pair_key": row.get("pair_key"),
        "rank4_verified": bool(row.get("rank4_verified")),
        "row_short": row.get("row_short"),
        "source_non_event_ops": row.get("source_non_event_ops"),
    }


def positive_controls(p972_payload: dict[str, Any], p974_payload: dict[str, Any]) -> dict[str, Any]:
    p972_summary = p972_payload.get("summary") or {}
    p974_summary = p974_payload.get("summary") or {}
    return {
        "p972_candidate_count_is_31": int_value(p972_summary.get("candidate_count")) == 31,
        "p972_event_count_is_3": int_value(p972_summary.get("event_count_ge4_count")) == 3,
        "p972_event_count_rank4_is_3": int_value(p972_summary.get("event_count_ge4_rank4_count")) == 3,
        "p974_event_cached_total_is_90": int_value(p974_summary.get("event_rank4_cached_total_ops")) == 90,
        "p974_event_cache_entries_is_1": int_value(p974_summary.get("signed_pair_cache_entry_count_event")) == 1,
        "p974_positive_control_pass": bool(p974_summary.get("positive_control_pass")),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p969_payload = load_json(Path(args.p969))
    p972_payload = load_json(Path(args.p972))
    p974_payload = load_json(Path(args.p974))
    controls = positive_controls(p972_payload, p974_payload)
    scope = selected_topk4_scope(args)
    reconstructed = p970.reconstruct_p969_seed(args, p969_payload)
    if not (reconstructed.get("control") or {}).get("control_pass"):
        raise ValueError(f"P969 reconstruction failed: {reconstructed.get('control')!r}")
    selected = public_event_candidates(args, p972_payload)
    materializer = p973.Materializer(args)
    selected_breakdowns = [
        p973.scan_leaf_candidate(args, materializer, reconstructed, candidate)
        for candidate in selected
    ]
    selected_groups = p973.group_candidates(args, materializer, reconstructed, selected_breakdowns)
    rho = int_value(reconstructed["compressed_seed"].get("generic_rho_steps"))
    portfolio = p974.portfolio(
        f"public_event_count_ge{int(args.min_candidate_event_count)}",
        selected_groups,
        len(selected),
        rho,
    )
    rank4_selected = [row for row in selected_breakdowns if row.get("rank4_verified")]
    false_positive_selected = [row for row in selected_breakdowns if not row.get("rank4_verified")]
    control_pass = all(bool(value) for value in controls.values())
    public_success = bool(
        control_pass
        and selected
        and rank4_selected
        and portfolio["cached_total_ops_below_source_rho"]
    )
    no_false_positives = not false_positive_selected
    if public_success and no_false_positives and not scope["wider_or_disjoint_scope_available"]:
        claim = "P975_PUBLIC_EVENT_SCREEN_CACHE_STRESS_CONFIRMS_P974_WITHOUT_RANK_LABEL_SELECTION_SCOPE_LIMITED"
    elif public_success and no_false_positives:
        claim = "P975_PUBLIC_EVENT_SCREEN_CACHE_STRESS_CONFIRMS_P974_WITHOUT_RANK_LABEL_SELECTION"
    elif public_success:
        claim = "P975_PUBLIC_EVENT_SCREEN_CACHE_STRESS_BELOW_RHO_WITH_FALSE_POSITIVES"
    elif not control_pass:
        claim = "NEGATIVE_RESULT_P975_PUBLIC_EVENT_CACHE_STRESS_FAILS_CONTROLS"
    else:
        claim = "NEGATIVE_RESULT_P975_PUBLIC_EVENT_SCREEN_CACHE_STRESS_NOT_BELOW_RHO"
    summary = {
        "cached_total_ops": portfolio["cached_total_ops"],
        "cached_total_ops_below_source_rho": portfolio["cached_total_ops_below_source_rho"],
        "cache_entry_count": portfolio["cache_entry_count"],
        "claim_status": claim,
        "false_positive_selected_count": len(false_positive_selected),
        "positive_control_pass": control_pass,
        "public_rank_label_free_selection": True,
        "rank4_selected_count": len(rank4_selected),
        "scope_limited_no_wider_or_disjoint_source": not scope["wider_or_disjoint_scope_available"],
        "selected_count": len(selected),
        "source_rho": rho,
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p969_result": str(args.p969),
            "p972_result": str(args.p972),
            "p974_result": str(args.p974),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "PUBLIC-SELECTION: candidate selection uses seed ops and public candidate-event count, not rank labels.",
            "SCOPE-LIMITED: the current P957/P959 source corpus exposes only target 67.a1@9803 and salts 201..209.",
            "CACHE-EMULATION: this uses P973 component ledgers and P974 cache accounting, not a new verifier backend.",
            "BATCH-SOURCE-NOT-ONE-SHOT: below-rho cached source cost is not a complete faster-than-rho ECDLP algorithm.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: matrix solving and individual logarithm descent remain open.",
        ],
        "method": "p975_public_event_cache_stress",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_seed_ops": int(args.max_seed_ops),
            "min_candidate_event_count": int(args.min_candidate_event_count),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "portfolio": portfolio,
        "positive_controls": controls,
        "public_selection": {
            "false_positive_selected": [compact_candidate(row) for row in false_positive_selected],
            "rank4_selected": [compact_candidate(row) for row in rank4_selected],
            "selected": [compact_candidate(row) for row in selected_breakdowns],
            "selection_rule": f"seed_ops <= {int(args.max_seed_ops)} and candidate_event_count >= {int(args.min_candidate_event_count)}",
        },
        "schema": SCHEMA,
        "source_scope": scope,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p969", type=Path, default=DEFAULT_P969)
    parser.add_argument("--p972", type=Path, default=DEFAULT_P972)
    parser.add_argument("--p974", type=Path, default=DEFAULT_P974)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--salt-min", type=int, default=201)
    parser.add_argument("--salt-max", type=int, default=209)
    parser.add_argument("--max-seed-ops", type=int, default=122)
    parser.add_argument("--min-candidate-event-count", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selected={summary['selected_count']} "
        f"rank4_selected={summary['rank4_selected_count']} "
        f"false_positive_selected={summary['false_positive_selected_count']} "
        f"cached_ops={summary['cached_total_ops']} "
        f"cache_entries={summary['cache_entry_count']} "
        f"below_source_rho={summary['cached_total_ops_below_source_rho']} "
        f"scope_limited={summary['scope_limited_no_wider_or_disjoint_source']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
