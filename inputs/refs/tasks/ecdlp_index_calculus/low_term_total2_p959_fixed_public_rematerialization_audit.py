#!/usr/bin/env python3
"""P959 fixed-public rematerialization audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_dependency_circuit_probe as dependency_circuit_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_public_probe as leaf_public_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe  # noqa: E402
import low_term_total2_p957_topk4_relation_matrix_sufficiency_audit as p957  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p959_fixed_public_rematerialization_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p959_fixed_public_rematerialization_probe.json"
SCHEMA = "ecdlp.low_term_total2_p959_fixed_public_rematerialization.v1"
DEFAULT_FIXED_TRANSFER = 8543
DEFAULT_SELECTOR = "mode_low_term_span_total3"
DEFAULT_RESIDUE_MODULUS = 16


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def selector_spec(raw: str) -> leaf_public_probe.LeafSelectorSpec:
    if not raw.startswith("mode_"):
        raise ValueError(f"unsupported selector {raw!r}")
    # Reuse the established encoded form: mode_<public_mode>_(total|perrow)<cap>.
    import re

    match = re.fullmatch(r"mode_([a-z0-9_]+)_(total|perrow)([0-9]+)", raw)
    if not match:
        raise ValueError(f"unsupported selector {raw!r}")
    mode, cap_mode, cap_raw = match.groups()
    cap = int(cap_raw)
    return leaf_public_probe.LeafSelectorSpec(
        name=raw,
        scope="mode",
        selection_mode="case_total" if cap_mode == "total" else "per_row",
        cap_per_row=cap if cap_mode == "perrow" else 0,
        total_leaf_cap=cap if cap_mode == "total" else 0,
        token_weight=0.0,
        leaf_index_weight=0.0,
        residue_weight=0.0,
        low_index_weight=0.0,
        public_mode=mode,
    )


def empty_profiles() -> dict[str, Any]:
    return {
        "target_tokens": {},
        "global_tokens": Counter(),
        "target_leaf_indices": {},
        "global_leaf_indices": Counter(),
        "target_residues": {},
        "global_residues": Counter(),
    }


def row_pair_key(row_keys: list[str]) -> tuple[str, ...]:
    return tuple(sorted(str(key) for key in row_keys))


def source_row_pairs(state_dir: Path, post_min: int, target: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases = p957.selected_topk4_cases(state_dir, post_min, target)
    counts: Counter[tuple[str, ...]] = Counter(row_pair_key(case.get("row_keys") or []) for case in cases)
    examples: dict[tuple[str, ...], dict[str, Any]] = {}
    for case in cases:
        key = row_pair_key(case.get("row_keys") or [])
        examples.setdefault(key, case)
    pairs = [
        {
            "example_source": examples[key].get("source"),
            "example_transfer_index": examples[key].get("transfer_index"),
            "row_keys": list(key),
            "source_support_count": count,
            "target": target,
        }
        for key, count in counts.items()
        if len(key) == 2
    ]
    pairs.sort(key=lambda row: (-int(row["source_support_count"]), row["row_keys"]))
    return cases, pairs


def choose_source(cases: list[dict[str, Any]], fixed_transfer: int) -> Path:
    for case in cases:
        if p957.int_value(case.get("transfer_index")) == fixed_transfer and case.get("source"):
            return Path(str(case["source"]))
    for case in cases:
        if case.get("source"):
            return Path(str(case["source"]))
    raise ValueError("no source path found in selected cases")


def event_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    coeffs, rhs, _terms = event["form"]
    return tuple(int(value) for value in coeffs), int(rhs)


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


def compact_scan(scan: dict[str, Any]) -> dict[str, Any]:
    return direct_witness_probe.compact_scan(scan)


def scan_pair(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    pair: dict[str, Any],
    fixed_transfer: int,
    top_k: int,
    spec: leaf_public_probe.LeafSelectorSpec,
    residue_modulus: int,
    probe_args: argparse.Namespace,
) -> dict[str, Any]:
    target = str(pair["target"])
    selected_rows, built_by_row, components_by_row, local_args_by_row, feature_rows_by_row, errors = (
        leaf_trim_probe.scan_selected_rows(
            verifier,
            records,
            config_source,
            specs_by_target.get(target, {}),
            [str(key) for key in pair.get("row_keys") or []],
            fixed_transfer,
            top_k,
            probe_args,
        )
    )
    leaves_by_row = leaf_public_probe.select_public_leaves_by_row(
        selected_rows,
        feature_rows_by_row,
        target,
        empty_profiles(),
        spec,
        residue_modulus,
    )
    public_rows = []
    events = []
    public_values = set()
    for row in selected_rows:
        key = leaf_trim_probe.row_key(row)
        built = built_by_row.get(key)
        if built:
            public_values.add(tuple(int(value) for value in built.get("public") or []))
        leaves = leaves_by_row.get(key, set())
        if not leaves:
            continue
        scan = direct_witness_probe.scan_selected(
            verifier,
            built_by_row[key],
            components_by_row[key],
            leaves,
            local_args_by_row[key],
        )
        for event in scan.get("relation_events") or []:
            coeffs, rhs, terms = event["form"]
            events.append(
                {
                    "form": (
                        tuple(int(value) for value in coeffs),
                        int(rhs),
                        [int(value) for value in terms],
                    ),
                    "leaf_index": event.get("leaf_index"),
                    "row_key": key,
                    "row_pair": list(pair.get("row_keys") or []),
                }
            )
        public_rows.append(
            {
                **row,
                "public_leaf_indices": sorted(int(leaf) for leaf in leaves),
                "ranked_prefix": compact_scan(scan),
                "_public_leaf": scan,
            }
        )
    union = direct_witness_probe.union_derive(verifier, public_rows, built_by_row, "_public_leaf")
    generic_rho = max((int(row.get("generic_rho_steps") or 0) for row in selected_rows), default=0)
    ops = sum(
        int((row.get("ranked_prefix") or {}).get("preassociation_filter_ops") or 0)
        for row in public_rows
    )
    first_built = next(iter(built_by_row.values()), {})
    challenge_seeds = sorted(
        {
            str(getattr(local_args, "challenge_seed", ""))
            for local_args in local_args_by_row.values()
            if getattr(local_args, "challenge_seed", "")
        }
    )
    for row in public_rows:
        row.pop("_public_leaf", None)
    return {
        "below_rho": bool(generic_rho and ops < generic_rho),
        "challenge_seeds": challenge_seeds,
        "derived_secret": union.get("union_derived_secret"),
        "errors": errors,
        "events": events,
        "fixed_transfer_index": fixed_transfer,
        "generic_rho_steps": generic_rho,
        "ops": ops,
        "ops_over_rho": round(ops / max(1, generic_rho), 8) if generic_rho else None,
        "public": list(next(iter(public_values), ())),
        "public_consistent": len(public_values) <= 1,
        "public_key_verified": bool(union.get("union_public_key_verified")),
        "rank": int(union.get("union_rank") or 0),
        "relation_count": int(union.get("union_relation_count") or 0),
        "row_keys": list(pair.get("row_keys") or []),
        "row_results": [
            {
                "public_leaf_indices": row.get("public_leaf_indices") or [],
                "rank": int((row.get("ranked_prefix") or {}).get("rank") or 0),
                "relation_count": int((row.get("ranked_prefix") or {}).get("relation_count") or 0),
                "row_key": row.get("row_key"),
            }
            for row in public_rows
        ],
        "selected_leaf_count": sum(len(row.get("public_leaf_indices") or []) for row in public_rows),
        "selected_row_count": len(public_rows),
        "source_support_count": int(pair.get("source_support_count") or 0),
        "target": pair.get("target"),
        "_built": first_built,
    }


def accumulate(verifier: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [row for row in rows if row.get("events") and row.get("_built")]
    if not usable:
        return {
            "cumulative_ops": 0,
            "cumulative_ops_over_rho": None,
            "final_rank": 0,
            "first_public_key_verified_at": None,
            "first_rank_gt3_at": None,
            "rank_curve": [],
            "unique_form_count": 0,
        }
    built = usable[0]["_built"]
    rho = max(int(row.get("generic_rho_steps") or 0) for row in usable)
    seen: set[tuple[tuple[int, ...], int]] = set()
    events = []
    cumulative_ops = 0
    rank_curve = []
    first_rank_gt3_at = None
    first_public_key_verified_at = None
    for index, row in enumerate(usable, start=1):
        cumulative_ops += int(row.get("ops") or 0)
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
            "cumulative_ops_over_rho": round(cumulative_ops / max(1, rho), 8) if rho else None,
            "derived_secret": derived.get("derived_secret"),
            "new_unique_forms": len(events) - before,
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": int(derived.get("rank") or 0),
            "row_keys": row.get("row_keys") or [],
            "unique_form_count": len(events),
        }
        if first_rank_gt3_at is None and int(curve_row["rank"]) > 3:
            first_rank_gt3_at = curve_row
        if first_public_key_verified_at is None and curve_row["public_key_verified"]:
            first_public_key_verified_at = curve_row
        rank_curve.append(curve_row)
    final = public_derive(verifier, built, events)
    return {
        "cumulative_ops": cumulative_ops,
        "cumulative_ops_over_rho": round(cumulative_ops / max(1, rho), 8) if rho else None,
        "final_derived_secret": final.get("derived_secret"),
        "final_public_key_verified": bool(final.get("public_key_verified")),
        "final_rank": int(final.get("rank") or 0),
        "first_public_key_verified_at": first_public_key_verified_at,
        "first_rank_gt3_at": first_rank_gt3_at,
        "rank_curve": rank_curve,
        "rho": rho,
        "unique_form_count": len(events),
    }


def strip_private(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in {"_built", "events"}}


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    cases, pairs = source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    if int(args.max_row_pairs) > 0:
        pairs = pairs[: int(args.max_row_pairs)]
    source_path = choose_source(cases, int(args.fixed_transfer))
    source = p957.load_json(source_path)
    params = repair_probe.source_parameters(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    probe_args = repair_probe.probe_args_from_source(source)
    spec = selector_spec(args.selector)
    rows = [
        scan_pair(
            verifier,
            records,
            config_source,
            specs_by_target,
            pair,
            int(args.fixed_transfer),
            int(args.top_k),
            spec,
            int(args.residue_modulus),
            probe_args,
        )
        for pair in pairs
    ]
    rows.sort(
        key=lambda row: (
            not bool(row.get("public_key_verified")),
            -int(row.get("rank") or 0),
            p957.float_value(row.get("ops_over_rho"), 10**18),
            -int(row.get("source_support_count") or 0),
            row.get("row_keys") or [],
        )
    )
    accumulation = accumulate(verifier, rows)
    verified = [row for row in rows if row.get("public_key_verified")]
    below = [row for row in rows if row.get("below_rho")]
    public_values = {tuple(int(value) for value in row.get("public") or []) for row in rows if row.get("public")}
    first_rank_gt3 = accumulation.get("first_rank_gt3_at") or {}
    claim = (
        "P959_FIXED_PUBLIC_RANK_GT3_BELOW_RHO"
        if first_rank_gt3 and p957.float_value(first_rank_gt3.get("cumulative_ops_over_rho"), 10**18) <= 1.0
        else "P959_FIXED_PUBLIC_RANK_GROWS_AFTER_RHO"
        if first_rank_gt3
        else "NEGATIVE_RESULT_P959_FIXED_PUBLIC_REMAINS_RANK3"
    )
    summary = {
        "below_rho_row_pair_count": len(below),
        "claim_status": claim,
        "fixed_challenge_seed": f"{probe_args.seed}:shared-transfer:{int(args.fixed_transfer)}:{args.target}",
        "fixed_public_consistent": len(public_values) <= 1,
        "fixed_public_count": len(public_values),
        "fixed_transfer_index": int(args.fixed_transfer),
        "first_rank_gt3_at": first_rank_gt3 or None,
        "final_cumulative_ops_over_rho": accumulation.get("cumulative_ops_over_rho"),
        "final_rank": accumulation.get("final_rank"),
        "matrix_ready": bool(
            first_rank_gt3 and p957.float_value(first_rank_gt3.get("cumulative_ops_over_rho"), 10**18) <= 1.0
        ),
        "max_row_pair_rank": max((int(row.get("rank") or 0) for row in rows), default=0),
        "relation_form_count": sum(len(row.get("events") or []) for row in rows),
        "scanned_row_pair_count": len(rows),
        "selected_case_count": len(cases),
        "unique_form_count": accumulation.get("unique_form_count"),
        "unique_source_row_pair_count": len(pairs),
        "verified_row_pair_count": len(verified),
    }
    return {
        "accumulation": accumulation,
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source": str(source_path),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: all row pairs are rematerialized under one fixed transfer challenge.",
            "PUBLIC-SELECTOR: leaves are recomputed under the fixed challenge by the public low-term-span total-cap rule.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this tests same-public relation accumulation, not full deployed-curve complexity.",
        ],
        "method": "p959_fixed_public_rematerialization",
        "parameters": {
            "fixed_transfer": int(args.fixed_transfer),
            "max_row_pairs": int(args.max_row_pairs),
            "post_min": int(args.post_min),
            "selector": args.selector,
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "row_pair_results": [strip_private(row) for row in rows],
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
    parser.add_argument("--fixed-transfer", type=int, default=DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--selector", default=DEFAULT_SELECTOR)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--max-row-pairs", type=int, default=0, help="0 means all unique P957 row pairs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"pairs={summary['scanned_row_pair_count']} "
        f"verified={summary['verified_row_pair_count']} "
        f"below={summary['below_rho_row_pair_count']} "
        f"forms={summary['relation_form_count']} "
        f"unique_forms={summary['unique_form_count']} "
        f"final_rank={summary['final_rank']} "
        f"first_rank_gt3={summary['first_rank_gt3_at']} "
        f"ops_over_rho={summary['final_cumulative_ops_over_rho']} "
        f"matrix_ready={summary['matrix_ready']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
