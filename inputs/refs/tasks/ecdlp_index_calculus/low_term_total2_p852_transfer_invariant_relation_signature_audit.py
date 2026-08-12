#!/usr/bin/env python3
"""P852 transfer-invariant relation signature audit.

P851 keeps relation rank aggregation inside compatible challenge seeds.  This
audit asks the next reusability question without violating that boundary: do
the verified relation forms show repeated signatures across transfers?

Exact coefficient-vector reuse would be a stronger reusable-relation signal.
Repeated support/term shapes without exact coefficient reuse is weaker but
actionable: it suggests a stable row/term skeleton whose coefficients still
need normalization or prediction.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p852_transfer_invariant_relation_signature_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p852_transfer_invariant_relation_signature_audit.md"
SCHEMA = "ecdlp.low_term_total2_p852_transfer_invariant_relation_signature_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def group_tuple(target: Any, transfer_index: Any, challenge_seed: Any) -> tuple[str, int, str]:
    return str(target), p851.int_value(transfer_index), str(challenge_seed)


def group_id(group: tuple[str, int, str]) -> str:
    return f"{group[0]}|transfer={group[1]}|{group[2]}"


def signature_key(target: str, values: tuple[int, ...]) -> str:
    return f"{target}|{','.join(str(value) for value in values)}"


def compact_signature_record(record: dict[str, Any]) -> dict[str, Any]:
    groups = sorted(record["groups"])
    return {
        "below_rho_group_count": record["below_rho_group_count"],
        "form_count": record["form_count"],
        "group_count": len(groups),
        "groups": groups[:12],
        "hidden_false_group_count": record["hidden_false_group_count"],
        "signature": record["signature"],
        "target": record["target"],
    }


def add_signature(
    table: dict[str, dict[str, Any]],
    target: str,
    values: tuple[int, ...],
    group: tuple[str, int, str],
    group_meta: dict[str, Any],
) -> None:
    key = signature_key(target, values)
    if key not in table:
        table[key] = {
            "below_rho_groups": set(),
            "form_count": 0,
            "groups": set(),
            "hidden_false_groups": set(),
            "signature": list(values),
            "target": target,
        }
    record = table[key]
    gid = group_id(group)
    record["form_count"] += 1
    record["groups"].add(gid)
    if group_meta.get("below_rho"):
        record["below_rho_groups"].add(gid)
    if p851.int_value(group_meta.get("hidden_false_candidate_count")):
        record["hidden_false_groups"].add(gid)


def finalize_table(table: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for record in table.values():
        out.append(
            compact_signature_record(
                {
                    "below_rho_group_count": len(record["below_rho_groups"]),
                    "form_count": record["form_count"],
                    "groups": record["groups"],
                    "hidden_false_group_count": len(record["hidden_false_groups"]),
                    "signature": record["signature"],
                    "target": record["target"],
                }
            )
        )
    return sorted(out, key=lambda row: (-row["group_count"], -row["form_count"], row["target"], row["signature"]))


def reconstruct_group_forms(args: argparse.Namespace) -> tuple[dict[tuple[str, int, str], dict[str, Any]], list[dict[str, Any]]]:
    p850 = load_json(args.p850)
    p851_payload = load_json(args.p851)
    p851_groups = {
        group_tuple(group.get("target"), group.get("transfer_index"), group.get("challenge_seed")): {
            "below_rho": group.get("deduped_ops_over_rho") is not None
            and float(group["deduped_ops_over_rho"]) < 1.0,
            "deduped_ops_over_rho": group.get("deduped_ops_over_rho"),
            "hidden_false_candidate_count": group.get("hidden_false_candidate_count"),
        }
        for group in p851_payload.get("challenge_groups") or []
    }
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    public_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    group_forms: dict[tuple[str, int, str], dict[str, Any]] = {}
    errors = []

    for index, row in enumerate(p850.get("relation_lane_rows") or []):
        variant = p851.best_variant(row)
        if not variant or not variant.get("verified"):
            errors.append({"index": index, "row_key": row.get("row_key"), "error": "missing verified P850 variant"})
            continue
        public_source = str(row["public_source"])
        if public_source not in public_cache:
            public_cache[public_source] = load_json(Path(public_source))
        source_case = p851.compact_source_case(row)
        ckey = p851.context_key(public_source, source_case)
        if ckey not in context_cache:
            context_cache[ckey] = p848.build_context(verifier, records, public_cache[public_source], source_case)
        built_by_row, components_by_row, local_args_by_row = context_cache[ckey]
        challenge_seeds = set()
        scans = []
        for selected_row_key, leaves in sorted((variant.get("leaves_by_row") or {}).items()):
            selected = sorted({p851.int_value(leaf) for leaf in leaves})
            if not selected:
                continue
            skey = p851.scan_key(public_source, source_case, selected_row_key, selected)
            if skey not in scan_cache:
                scan_cache[skey] = p848.direct_witness_probe.scan_selected(
                    verifier,
                    built_by_row[selected_row_key],
                    components_by_row[selected_row_key],
                    set(selected),
                    local_args_by_row[selected_row_key],
                )
                built_cache[skey] = built_by_row[selected_row_key]
            challenge_seeds.add(str(built_cache[skey].get("challenge_seed")))
            scans.append((selected_row_key, skey, scan_cache[skey]))
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
        group = group_tuple(row.get("target"), row.get("transfer_index"), next(iter(challenge_seeds)))
        if group not in group_forms:
            group_forms[group] = {
                "forms": {},
                "meta": p851_groups.get(group, {}),
                "target": str(row.get("target")),
            }
        for _selected_row_key, _skey, scan in scans:
            for event in scan.get("relation_events") or []:
                key = p851.form_key(event)
                if key in group_forms[group]["forms"]:
                    continue
                coeffs, rhs, terms = event["form"]
                coeffs_tuple = tuple(int(coeff) for coeff in coeffs)
                group_forms[group]["forms"][key] = {
                    "coeffs": coeffs_tuple,
                    "rhs": int(rhs),
                    "support": tuple(index for index, coeff in enumerate(coeffs_tuple) if coeff != 0),
                    "terms": tuple(int(term) for term in terms),
                }
    return group_forms, errors


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    group_forms, errors = reconstruct_group_forms(args)
    exact_coefficients: dict[str, dict[str, Any]] = {}
    supports: dict[str, dict[str, Any]] = {}
    terms: dict[str, dict[str, Any]] = {}

    deduped_form_count = 0
    for group, payload in group_forms.items():
        target = payload["target"]
        meta = payload.get("meta") or {}
        for form in payload["forms"].values():
            deduped_form_count += 1
            add_signature(exact_coefficients, target, form["coeffs"], group, meta)
            add_signature(supports, target, form["support"], group, meta)
            add_signature(terms, target, form["terms"], group, meta)

    tables = {
        "exact_coefficients": finalize_table(exact_coefficients),
        "support": finalize_table(supports),
        "terms": finalize_table(terms),
    }
    claim = determine_claim(tables, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p851_source": str(args.p851),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "NO-CROSS-TRANSFER-RANK-MIXING: repeated signatures are counted as motifs only; they are not combined as one linear system.",
            "EXACT-COEFFICIENT BOUNDARY: support/term repeats are weaker than reusable exact coefficient vectors.",
            "P850/P851-SELECTION BOUNDARY: this audits existing verified rows and does not discover a new public selector.",
            "POLLARD-RHO BOUNDARY: this is relation-structure evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p852_transfer_invariant_relation_signature_audit",
        "parameters": {
            "deduped_form_source": "P851-compatible exact forms reconstructed from P850 best verified variants",
            "signature_families": ["exact_coefficients", "support", "terms"],
        },
        "red_team_handoff": {
            "assumptions": [
                "Repeated support or term signatures across transfers indicate reusable structure worth targeting.",
                "Exact coefficient-vector absence means this is not yet a reusable relation matrix.",
                "P851 group metadata is sufficient to stratify repeated signatures by below-rho and hidden-false groups.",
            ],
            "failure_modes": [
                "Support repeats may be an artifact of fixed toy factor-base width or row generator constraints.",
                "Coefficient values may remain transfer-random even when support shapes repeat.",
                "A support-shape generator may not reduce target descent or matrix cost after full charging.",
            ],
            "next_concrete_action": (
                "Build P853 to learn a public support-shape generator for the top repeated signatures and test whether coefficient normalization "
                "or row-context features predict exact coefficients better than chance."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P852_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "signature_tables": {
            key: {
                "repeated": [row for row in rows if row["group_count"] >= 2],
                "top": rows[:20],
            }
            for key, rows in tables.items()
        },
        "summary": summarize(group_forms, deduped_form_count, tables, errors),
    }


def determine_claim(tables: dict[str, list[dict[str, Any]]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P852_RECONSTRUCTION_ERRORS"
    exact_repeats = [row for row in tables["exact_coefficients"] if row["group_count"] >= 2]
    support_repeats = [row for row in tables["support"] if row["group_count"] >= 2]
    if exact_repeats:
        return "P852_EXACT_COEFFICIENT_SIGNATURES_REPEAT_ACROSS_TRANSFERS"
    if support_repeats:
        return "P852_TRANSFER_SUPPORT_SHAPES_REPEAT_WITHOUT_EXACT_COEFFICIENT_REUSE"
    return "NEGATIVE_RESULT_P852_TRANSFER_SIGNATURE_REUSE_NOT_FOUND"


def summarize(
    group_forms: dict[tuple[str, int, str], dict[str, Any]],
    deduped_form_count: int,
    tables: dict[str, list[dict[str, Any]]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    out = {
        "challenge_group_count": len(group_forms),
        "claim_status": determine_claim(tables, errors),
        "deduped_form_count": deduped_form_count,
        "error_count": len(errors),
    }
    for family, rows in tables.items():
        repeated = [row for row in rows if row["group_count"] >= 2]
        out[f"{family}_unique_count"] = len(rows)
        out[f"{family}_repeated_count"] = len(repeated)
        out[f"{family}_max_group_count"] = max((row["group_count"] for row in rows), default=0)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--p851", type=Path, default=DEFAULT_P851)
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
