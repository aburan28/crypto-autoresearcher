#!/usr/bin/env python3
"""P856 variable-anchor pair-elimination audit.

P853/P855 showed that repeated support skeletons have a fixed non-anchor tail
and an unpredictable anchor coefficient at index 0.  This audit tests whether
the variable anchor can be used directly: inside one compatible challenge
group, subtract two forms with the same non-anchor tail.  The tail cancels and
the remaining one-variable equation can derive the challenge scalar when the
anchor-coefficient difference is invertible.

No cross-transfer forms are mixed.  Every derived scalar is verified against the
public key for that challenge group.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p856_variable_anchor_pair_elimination_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p856_variable_anchor_pair_elimination_audit.md"
SCHEMA = "ecdlp.low_term_total2_p856_variable_anchor_pair_elimination_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p851.int_value(value, default)


def group_tuple(target: Any, transfer_index: Any, challenge_seed: Any) -> tuple[str, int, str]:
    return str(target), int_value(transfer_index), str(challenge_seed)


def group_id(group: tuple[str, int, str]) -> str:
    return f"{group[0]}|transfer={group[1]}|{group[2]}"


def form_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    return p851.form_key(event)


def non_anchor_tail_key(coeffs: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple((index, int(coeff)) for index, coeff in enumerate(coeffs) if index != 0 and int(coeff) != 0)


def public_secret_matches(verifier: Any, candidate: int, built: dict[str, Any]) -> bool:
    order = int(built["order"])
    return (
        verifier.mul_point(int(candidate) % order, built["base"], built["ainvs"], int(built["p"]))
        == built["public"]
    )


def collect_group_forms(args: argparse.Namespace) -> tuple[dict[tuple[str, int, str], dict[str, Any]], list[dict[str, Any]]]:
    p850 = load_json(args.p850)
    p851_payload = load_json(args.p851)
    p851_groups = {
        group_tuple(group.get("target"), group.get("transfer_index"), group.get("challenge_seed")): {
            "below_rho": group.get("deduped_ops_over_rho") is not None
            and float(group["deduped_ops_over_rho"]) < 1.0,
            "deduped_ops_over_rho": group.get("deduped_ops_over_rho"),
            "hidden_false_candidate_count": group.get("hidden_false_candidate_count"),
            "p851_rank": (group.get("union") or {}).get("union_rank"),
            "p851_relation_count": (group.get("union") or {}).get("union_relation_count"),
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
            selected = sorted({int_value(leaf) for leaf in leaves})
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
            first_skey = scans[0][1]
            group_forms[group] = {
                "built": built_cache[first_skey],
                "forms": {},
                "meta": p851_groups.get(group, {}),
                "target": str(row.get("target")),
            }
        for selected_row_key, skey, scan in scans:
            for event in scan.get("relation_events") or []:
                key = form_key(event)
                if key in group_forms[group]["forms"]:
                    continue
                coeffs, rhs, terms = event["form"]
                coeffs_tuple = tuple(int(coeff) for coeff in coeffs)
                group_forms[group]["forms"][key] = {
                    "coeffs": coeffs_tuple,
                    "rhs": int(rhs),
                    "scan_key": skey,
                    "scan_ops": int_value(scan.get("preassociation_filter_ops")),
                    "scan_rho": int_value(built_cache[skey].get("generic_rho_steps")),
                    "selected_row_key": selected_row_key,
                    "support": tuple(index for index, coeff in enumerate(coeffs_tuple) if int(coeff) != 0),
                    "tail_key": non_anchor_tail_key(coeffs_tuple),
                    "terms": tuple(int(term) for term in terms),
                }
    return group_forms, errors


def derive_pair(verifier: Any, built: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    order = int(built["order"])
    delta_anchor = (int(left["coeffs"][0]) - int(right["coeffs"][0])) % order
    delta_rhs = (int(left["rhs"]) - int(right["rhs"])) % order
    gcd = math.gcd(delta_anchor, order)
    if gcd != 1:
        return {
            "candidate": None,
            "delta_anchor": delta_anchor,
            "delta_rhs": delta_rhs,
            "gcd_delta_anchor_order": gcd,
            "invertible": False,
            "verified": False,
        }
    candidate = (delta_rhs * pow(delta_anchor, -1, order)) % order
    return {
        "candidate": int(candidate),
        "delta_anchor": delta_anchor,
        "delta_rhs": delta_rhs,
        "gcd_delta_anchor_order": gcd,
        "invertible": True,
        "verified": public_secret_matches(verifier, candidate, built),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    group_forms, errors = collect_group_forms(args)
    verifier = p848.relation_probe.load_verifier_module()
    pair_rows = []
    group_rows = []
    for group, payload in sorted(group_forms.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        forms_by_tail: dict[tuple[tuple[int, int], ...], list[dict[str, Any]]] = defaultdict(list)
        for form in payload["forms"].values():
            if 0 in form["support"] and form["tail_key"]:
                forms_by_tail[form["tail_key"]].append(form)
        group_pairs = []
        for tail_key, forms in sorted(forms_by_tail.items(), key=lambda item: (-len(item[1]), item[0])):
            if len(forms) < 2:
                continue
            for left, right in itertools.combinations(forms, 2):
                derivation = derive_pair(verifier, payload["built"], left, right)
                scan_keys = {left["scan_key"], right["scan_key"]}
                ops = sum(
                    form["scan_ops"]
                    for skey, form in {
                        left["scan_key"]: left,
                        right["scan_key"]: right,
                    }.items()
                )
                rho = max(int_value(left.get("scan_rho")), int_value(right.get("scan_rho")))
                pair = {
                    **derivation,
                    "group_id": group_id(group),
                    "ops": ops,
                    "ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
                    "scan_count": len(scan_keys),
                    "tail_key": [list(item) for item in tail_key],
                    "target": payload["target"],
                    "transfer_index": group[1],
                }
                pair_rows.append(pair)
                group_pairs.append(pair)
        verified_pairs = [pair for pair in group_pairs if pair["verified"]]
        below_verified_pairs = [
            pair for pair in verified_pairs if pair.get("ops_over_rho") is not None and float(pair["ops_over_rho"]) < 1.0
        ]
        if group_pairs:
            best = sorted(
                group_pairs,
                key=lambda pair: (
                    not pair["verified"],
                    not (pair.get("ops_over_rho") is not None and float(pair["ops_over_rho"]) < 1.0),
                    float(pair.get("ops_over_rho") or 10**9),
                    pair["transfer_index"],
                    str(pair["tail_key"]),
                ),
            )[0]
            group_rows.append(
                {
                    "best_pair": {
                        "ops_over_rho": best.get("ops_over_rho"),
                        "tail_key": best.get("tail_key"),
                        "verified": best.get("verified"),
                    },
                    "below_rho_pair_count": len(below_verified_pairs),
                    "group_id": group_id(group),
                    "hidden_false_candidate_count": int_value((payload.get("meta") or {}).get("hidden_false_candidate_count")),
                    "invertible_pair_count": sum(1 for pair in group_pairs if pair["invertible"]),
                    "p851_ops_over_rho": (payload.get("meta") or {}).get("deduped_ops_over_rho"),
                    "p851_rank": (payload.get("meta") or {}).get("p851_rank"),
                    "pair_count": len(group_pairs),
                    "target": payload["target"],
                    "transfer_index": group[1],
                    "verified_pair_count": len(verified_pairs),
                }
            )
    claim = determine_claim(pair_rows, group_rows, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p851_source": str(args.p851),
            "script": str(Path(__file__)),
        },
        "challenge_groups": group_rows,
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "NO-CROSS-TRANSFER-MIXING: pair elimination is performed only inside identical target/transfer challenge groups.",
            "PAIR-SOURCE BOUNDARY: pairs are built from P850/P851 verified relation forms; this audit does not discover relation rows independently.",
            "COST BOUNDARY: pair costs charge the direct scans that produced the two forms, not the full upstream search pipeline.",
            "POLLARD-RHO BOUNDARY: this is a variable-anchor relation-use signal for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p856_variable_anchor_pair_elimination_audit",
        "parameters": {
            "pair_rule": "same challenge group and identical non-anchor coefficient tail",
            "derivation": "(rhs1-rhs2)/(anchor1-anchor2) mod order, verified against public key",
        },
        "pair_summary_sample": sorted(
            [pair for pair in pair_rows if pair["verified"]],
            key=lambda pair: (float(pair.get("ops_over_rho") or 10**9), pair["target"], pair["transfer_index"]),
        )[:20],
        "red_team_handoff": {
            "assumptions": [
                "Coefficient index 0 is the challenge scalar coefficient.",
                "Identical non-anchor tails can be safely cancelled inside the same challenge group.",
                "Verifier public-key equality is the right success criterion for the derived scalar.",
            ],
            "failure_modes": [
                "The pair source may rely on P850-selected relation rows and not provide an autonomous selector.",
                "The pair derivation may reduce relation use but not upstream relation-generation cost.",
                "A larger-parameter run may have fewer pairable tails or noninvertible anchor differences.",
            ],
            "next_concrete_action": (
                "Build P857 to turn the P856 pair rule into a public selector: predict pairable same-tail events from P850/P851 public features, "
                "charge relation discovery cost, and validate on fresh disjoint banks."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P856_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize(pair_rows, group_rows, errors),
    }


def determine_claim(pairs: list[dict[str, Any]], groups: list[dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P856_RECONSTRUCTION_ERRORS"
    if not pairs:
        return "NEGATIVE_RESULT_P856_NO_PAIRABLE_VARIABLE_ANCHOR_TAILS"
    verified = [pair for pair in pairs if pair["verified"]]
    below = [
        pair
        for pair in verified
        if pair.get("ops_over_rho") is not None and float(pair["ops_over_rho"]) < 1.0
    ]
    if below:
        return "P856_VARIABLE_ANCHOR_PAIRS_DERIVE_SECRETS_BELOW_RHO"
    if verified:
        return "P856_VARIABLE_ANCHOR_PAIRS_DERIVE_SECRETS_ABOVE_RHO_ONLY"
    return "NEGATIVE_RESULT_P856_VARIABLE_ANCHOR_PAIR_ELIMINATION_FAILS"


def summarize(
    pairs: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    verified = [pair for pair in pairs if pair["verified"]]
    below = [
        pair
        for pair in verified
        if pair.get("ops_over_rho") is not None and float(pair["ops_over_rho"]) < 1.0
    ]
    ops = [float(pair["ops_over_rho"]) for pair in below if pair.get("ops_over_rho") is not None]
    return {
        "below_rho_verified_pair_count": len(below),
        "claim_status": determine_claim(pairs, groups, errors),
        "error_count": len(errors),
        "group_count_with_pairs": len(groups),
        "group_count_with_verified_pair": len({pair["group_id"] for pair in verified}),
        "group_count_with_verified_pair_below_rho": len({pair["group_id"] for pair in below}),
        "invertible_pair_count": sum(1 for pair in pairs if pair["invertible"]),
        "max_below_rho_pair_ops_over_rho": max(ops) if ops else None,
        "mean_below_rho_pair_ops_over_rho": round(sum(ops) / len(ops), 8) if ops else None,
        "min_below_rho_pair_ops_over_rho": min(ops) if ops else None,
        "pair_count": len(pairs),
        "verified_pair_count": len(verified),
    }


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
