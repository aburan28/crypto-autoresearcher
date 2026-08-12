#!/usr/bin/env python3
"""P857 public event pair-selector audit.

P856 showed that same-challenge forms with the same non-anchor coefficient tail
can eliminate the variable anchor and derive the challenge scalar.  This audit
tests whether those pairs can be selected from public relation-event features
before using the anchor coefficient, RHS, verifier outcome, derived scalar, or
hidden labels.

The selector is still relation-event-level: it assumes the P850/P851 relation
events have been extracted.  It does not claim an upstream row generator or
target-descent algorithm.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p856_variable_anchor_pair_elimination_audit as p856


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p857_public_event_pair_selector_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p857_public_event_pair_selector_audit.md"
SCHEMA = "ecdlp.low_term_total2_p857_public_event_pair_selector_audit.v1"
POLICIES = (
    "same_tail_event",
    "same_support_event",
    "same_terms_event",
    "same_support_terms_event",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p856.int_value(value, default)


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def selector_key(form: dict[str, Any], policy: str) -> tuple[Any, ...] | None:
    support = tuple(int(index) for index in form.get("support") or ())
    terms = tuple(int(term) for term in form.get("terms") or ())
    tail = tuple((int(index), int(coeff)) for index, coeff in form.get("tail_key") or ())
    if 0 not in support:
        return None
    if policy == "same_tail_event":
        if not tail:
            return None
        return ("tail", tail)
    if policy == "same_support_event":
        return ("support", support)
    if policy == "same_terms_event":
        return ("terms", terms)
    if policy == "same_support_terms_event":
        return ("support_terms", support, terms)
    raise ValueError(f"unknown policy {policy}")


def public_form_sort_key(form: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int_value(form.get("_public_order")),
        str(form.get("selected_row_key")),
    )


def pair_scan_cost(left: dict[str, Any], right: dict[str, Any]) -> tuple[int, int, int]:
    scans: dict[str, dict[str, Any]] = {}
    for form in (left, right):
        scans[str(form["scan_key"])] = form
    ops = sum(int_value(form.get("scan_ops")) for form in scans.values())
    rho = max((int_value(form.get("scan_rho")) for form in scans.values()), default=0)
    return ops, rho, len(scans)


def evaluate_selected_pair(
    verifier: Any,
    built: dict[str, Any],
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    tail_equal = tuple(left.get("tail_key") or ()) == tuple(right.get("tail_key") or ())
    if not tail_equal:
        return {
            "candidate": None,
            "delta_anchor": None,
            "delta_rhs": None,
            "gcd_delta_anchor_order": None,
            "invertible": False,
            "tail_equal": False,
            "verified": False,
        }
    return {
        **p856.derive_pair(verifier, built, left, right),
        "tail_equal": True,
    }


def stream_select_pair(
    group_payload: dict[str, Any],
    policy: str,
) -> dict[str, Any] | None:
    forms = []
    for public_order, form in enumerate(group_payload["forms"].values()):
        row = dict(form)
        row["_public_order"] = public_order
        forms.append(row)

    scans: dict[str, dict[str, Any]] = {}
    for form in forms:
        scan_id = repr(form["scan_key"])
        scan = scans.setdefault(
            scan_id,
            {
                "forms": [],
                "ops": int_value(form.get("scan_ops")),
                "rho": int_value(form.get("scan_rho")),
                "scan_key": form["scan_key"],
                "selected_row_key": str(form.get("selected_row_key")),
            },
        )
        scan["forms"].append(form)

    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    cumulative_ops = 0
    cumulative_rho = 0
    for scan in sorted(
        scans.values(),
        key=lambda item: (
            int_value(item.get("ops")),
            str(item.get("selected_row_key")),
            repr(item.get("scan_key")),
        ),
    ):
        cumulative_ops += int_value(scan.get("ops"))
        cumulative_rho = max(cumulative_rho, int_value(scan.get("rho")))
        for form in sorted(scan["forms"], key=public_form_sort_key):
            key = selector_key(form, policy)
            if key is None:
                continue
            buckets[key].append(form)
        ready = [
            (key, sorted(bucket, key=public_form_sort_key)[:2])
            for key, bucket in buckets.items()
            if len(bucket) >= 2
        ]
        if not ready:
            continue
        ready.sort(key=lambda item: (str(item[0]), public_form_sort_key(item[1][0]), public_form_sort_key(item[1][1])))
        key, pair = ready[0]
        left, right = pair
        selected_ops, selected_rho, selected_scan_count = pair_scan_cost(left, right)
        return {
            "cumulative_ops": cumulative_ops,
            "cumulative_ops_over_rho": round(cumulative_ops / max(1, cumulative_rho), 8) if cumulative_rho else None,
            "policy_key": public_key_for_json(key),
            "processed_scan_count": sum(
                1
                for item in scans.values()
                if (
                    int_value(item.get("ops")),
                    str(item.get("selected_row_key")),
                    repr(item.get("scan_key")),
                )
                <= (
                    int_value(scan.get("ops")),
                    str(scan.get("selected_row_key")),
                    repr(scan.get("scan_key")),
                )
            ),
            "selected_ops": selected_ops,
            "selected_ops_over_rho": round(selected_ops / max(1, selected_rho), 8) if selected_rho else None,
            "selected_scan_count": selected_scan_count,
            "left": left,
            "right": right,
        }
    return None


def public_key_for_json(key: tuple[Any, ...]) -> list[Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return [convert(item) for item in key]


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    group_forms, errors = p856.collect_group_forms(args)
    verifier = p848.relation_probe.load_verifier_module()
    policy_groups: dict[str, list[dict[str, Any]]] = {policy: [] for policy in POLICIES}

    for group, payload in sorted(group_forms.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        gid = p856.group_id(group)
        for policy in POLICIES:
            selected = stream_select_pair(payload, policy)
            if selected is None:
                policy_groups[policy].append(
                    {
                        "group_id": gid,
                        "hidden_false_candidate_count": int_value((payload.get("meta") or {}).get("hidden_false_candidate_count")),
                        "p851_ops_over_rho": (payload.get("meta") or {}).get("deduped_ops_over_rho"),
                        "policy": policy,
                        "selected": False,
                        "target": payload["target"],
                        "transfer_index": group[1],
                    }
                )
                continue

            derivation = evaluate_selected_pair(verifier, payload["built"], selected["left"], selected["right"])
            row = {
                **{key: value for key, value in selected.items() if key not in {"left", "right"}},
                **derivation,
                "group_id": gid,
                "hidden_false_candidate_count": int_value((payload.get("meta") or {}).get("hidden_false_candidate_count")),
                "p851_ops_over_rho": (payload.get("meta") or {}).get("deduped_ops_over_rho"),
                "p851_rank": (payload.get("meta") or {}).get("p851_rank"),
                "policy": policy,
                "selected": True,
                "support_equal": tuple(selected["left"].get("support") or ()) == tuple(selected["right"].get("support") or ()),
                "target": payload["target"],
                "transfer_index": group[1],
            }
            policy_groups[policy].append(row)

    policy_summaries = {
        policy: summarize_policy(rows, group_count=len(group_forms), policy=policy)
        for policy, rows in policy_groups.items()
    }
    claim = determine_claim(policy_summaries, errors)
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
            "RELATION-EVENT-LEVEL SELECTOR: selectors consume P850/P851 extracted relation events; this does not discover rows independently.",
            "FORBIDDEN INPUT BOUNDARY: selectors do not use anchor coefficient, RHS, verifier outcome, derived scalar, or hidden labels before pair choice.",
            "NO-CROSS-TRANSFER-MIXING: pairs are selected only inside identical target/transfer/challenge-seed groups.",
            "COST BOUNDARY: streaming cost charges scans processed until a public bucket becomes pairable; it still excludes the broader P850 source-discovery campaign.",
            "POLLARD-RHO BOUNDARY: this is a public pair-use selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p857_public_event_pair_selector_audit",
        "parameters": {
            "policies": list(POLICIES),
            "forbidden_selector_inputs": [
                "anchor coefficient index 0",
                "rhs",
                "derived scalar",
                "public-key verifier result",
                "hidden false-factor labels",
            ],
            "stream_order": "scan_ops, selected_row_key, scan_key; event insertion order inside scan",
        },
        "policy_results_sample": {
            policy: sorted(
                [row for row in rows if row.get("selected")],
                key=lambda row: (
                    not row.get("verified"),
                    not below_rho(row.get("selected_ops_over_rho")),
                    float(row.get("selected_ops_over_rho") or 10**9),
                    row.get("target"),
                    int_value(row.get("transfer_index")),
                ),
            )[:12]
            for policy, rows in policy_groups.items()
        },
        "policy_outlier_rows": {
            policy: sorted(
                [
                    row
                    for row in rows
                    if row.get("selected")
                    and (
                        not row.get("verified")
                        or not below_rho(row.get("cumulative_ops_over_rho"))
                        or (row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0)
                    )
                ],
                key=lambda row: (
                    not row.get("verified"),
                    float(row.get("cumulative_ops_over_rho") or 10**9),
                    row.get("target"),
                    int_value(row.get("transfer_index")),
                ),
            )
            for policy, rows in policy_groups.items()
        },
        "policy_summaries": policy_summaries,
        "red_team_handoff": {
            "assumptions": [
                "Relation-event coefficients other than the anchor are public after the P850/P851 event extraction stage.",
                "Streaming scan order by public scan cost and row key is a fair selector schedule.",
                "Public-key equality after pair selection is the right verification criterion for the derived scalar.",
            ],
            "failure_modes": [
                "The selector may only be public after relation-event extraction, leaving upstream row discovery as the dominant unsolved cost.",
                "Support-only or term-only policies may collapse because they do not guarantee tail cancellation.",
                "The signal may not replicate on prospectively generated fresh banks or larger parameter regimes.",
            ],
            "next_concrete_action": (
                "Build P858 to push the selector one stage upstream: predict same-tail pairable relation events from row/leaf public features before relation-event extraction, "
                "then validate on fresh disjoint banks with the same streaming cost accounting."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P857_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize_all(policy_summaries, errors),
    }


def summarize_policy(rows: list[dict[str, Any]], group_count: int, policy: str) -> dict[str, Any]:
    selected = [row for row in rows if row.get("selected")]
    tail_equal = [row for row in selected if row.get("tail_equal")]
    invertible = [row for row in selected if row.get("invertible")]
    verified = [row for row in selected if row.get("verified")]
    selected_below = [row for row in verified if below_rho(row.get("selected_ops_over_rho"))]
    streaming_below = [row for row in verified if below_rho(row.get("cumulative_ops_over_rho"))]
    full_cost_below = [row for row in verified if below_rho(row.get("p851_ops_over_rho"))]
    false_selected = [row for row in selected if not row.get("tail_equal") or not row.get("verified")]
    selected_ops = [float(row["selected_ops_over_rho"]) for row in selected_below if row.get("selected_ops_over_rho") is not None]
    streaming_ops = [float(row["cumulative_ops_over_rho"]) for row in streaming_below if row.get("cumulative_ops_over_rho") is not None]
    p851_above_to_selected_below = [
        row
        for row in selected_below
        if row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0
    ]
    p851_above_to_stream_below = [
        row
        for row in streaming_below
        if row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0
    ]
    return {
        "false_selected_pair_count": len(false_selected),
        "full_p851_cost_below_rho_verified_group_count": len({row["group_id"] for row in full_cost_below}),
        "group_count": group_count,
        "groups_with_selected_pair": len({row["group_id"] for row in selected}),
        "groups_with_streaming_below_rho_verified_pair": len({row["group_id"] for row in streaming_below}),
        "groups_with_tail_equal_pair": len({row["group_id"] for row in tail_equal}),
        "groups_with_verified_pair": len({row["group_id"] for row in verified}),
        "groups_with_verified_pair_selected_cost_below_rho": len({row["group_id"] for row in selected_below}),
        "invertible_pair_count": len(invertible),
        "max_selected_ops_over_rho": max(selected_ops) if selected_ops else None,
        "max_streaming_ops_over_rho": max(streaming_ops) if streaming_ops else None,
        "mean_selected_ops_over_rho": round(sum(selected_ops) / len(selected_ops), 8) if selected_ops else None,
        "mean_streaming_ops_over_rho": round(sum(streaming_ops) / len(streaming_ops), 8) if streaming_ops else None,
        "min_selected_ops_over_rho": min(selected_ops) if selected_ops else None,
        "min_streaming_ops_over_rho": min(streaming_ops) if streaming_ops else None,
        "p851_above_to_selected_below_rho_count": len(p851_above_to_selected_below),
        "p851_above_to_streaming_below_rho_count": len(p851_above_to_stream_below),
        "policy": policy,
        "selected_pair_count": len(selected),
        "streaming_below_rho_verified_pair_count": len(streaming_below),
        "tail_equal_pair_count": len(tail_equal),
        "verified_pair_count": len(verified),
        "verified_pair_selected_cost_below_rho_count": len(selected_below),
    }


def determine_claim(policy_summaries: dict[str, dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P857_RECONSTRUCTION_ERRORS"
    tail = policy_summaries["same_tail_event"]
    support = policy_summaries["same_support_event"]
    support_terms = policy_summaries["same_support_terms_event"]
    if (
        support_terms["groups_with_verified_pair_selected_cost_below_rho"] == support_terms["group_count"]
        and support_terms["false_selected_pair_count"] == 0
    ):
        if support_terms["groups_with_streaming_below_rho_verified_pair"] == support_terms["group_count"]:
            return "P857_PUBLIC_SUPPORT_TERMS_SELECTOR_MATCHES_P856_BELOW_RHO"
        return "P857_PUBLIC_SUPPORT_TERMS_SELECTOR_SELECTS_ALL_BELOW_RHO_WITH_STREAMING_OUTLIER"
    if (
        support["groups_with_verified_pair_selected_cost_below_rho"] == support["group_count"]
        and support["false_selected_pair_count"] == 0
    ):
        if support["groups_with_streaming_below_rho_verified_pair"] == support["group_count"]:
            return "P857_PUBLIC_SUPPORT_SELECTOR_MATCHES_P856_BELOW_RHO"
        return "P857_PUBLIC_SUPPORT_SELECTOR_SELECTS_ALL_BELOW_RHO_WITH_STREAMING_OUTLIER"
    if (
        tail["groups_with_verified_pair_selected_cost_below_rho"] == tail["group_count"]
        and tail["false_selected_pair_count"] == 0
    ):
        if tail["groups_with_streaming_below_rho_verified_pair"] == tail["group_count"]:
            return "P857_PUBLIC_EVENT_TAIL_SELECTOR_REPRODUCES_P856_BELOW_RHO"
        return "P857_PUBLIC_EVENT_TAIL_SELECTOR_SELECTS_ALL_BELOW_RHO_WITH_STREAMING_OUTLIER"
    if (
        support_terms["groups_with_streaming_below_rho_verified_pair"] == support_terms["group_count"]
        and support_terms["false_selected_pair_count"] == 0
    ):
        return "P857_PUBLIC_SUPPORT_TERMS_SELECTOR_MATCHES_P856_BELOW_RHO"
    if (
        support["groups_with_streaming_below_rho_verified_pair"] == support["group_count"]
        and support["false_selected_pair_count"] == 0
    ):
        return "P857_PUBLIC_SUPPORT_SELECTOR_MATCHES_P856_BELOW_RHO"
    if (
        tail["groups_with_streaming_below_rho_verified_pair"] == tail["group_count"]
        and tail["false_selected_pair_count"] == 0
    ):
        return "P857_PUBLIC_EVENT_TAIL_SELECTOR_REPRODUCES_P856_BELOW_RHO"
    if tail["groups_with_verified_pair"] == tail["group_count"]:
        return "P857_PUBLIC_EVENT_TAIL_SELECTOR_VERIFIES_WITH_ABOVE_RHO_OUTLIERS"
    if tail["groups_with_verified_pair"]:
        return "P857_PUBLIC_EVENT_TAIL_SELECTOR_PARTIAL_VERIFICATION"
    return "NEGATIVE_RESULT_P857_PUBLIC_EVENT_PAIR_SELECTOR_FAILS"


def summarize_all(policy_summaries: dict[str, dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "claim_status": determine_claim(policy_summaries, errors),
        "error_count": len(errors),
        "policy_count": len(policy_summaries),
        "same_tail_event": policy_summaries["same_tail_event"],
        "strongest_support_policy": max(
            (policy_summaries["same_support_event"], policy_summaries["same_support_terms_event"]),
            key=lambda item: (
                item["groups_with_streaming_below_rho_verified_pair"],
                -item["false_selected_pair_count"],
            ),
        ),
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
