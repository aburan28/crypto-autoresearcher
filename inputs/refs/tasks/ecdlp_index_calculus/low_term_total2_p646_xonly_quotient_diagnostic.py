#!/usr/bin/env python3
"""P646 sign-insensitive proxy diagnostic for P642 positives."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p643_phase0_salt203_burst_scout as p643


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p646_xonly_quotient_diagnostic_probe.json"

DATASETS = [
    {
        "role": "positive",
        "name": "p642_positive",
        "path": STATE_DIR
        / "low_term_total2_fixed_leaf_shared_product_gate_p642_order9887_right206_anchor3_salt204_salt206_22120_22132_density_gate_probe.json",
    },
    {
        "role": "quiet_control",
        "name": "p643_adjacent_quiet",
        "path": STATE_DIR
        / "low_term_total2_fixed_leaf_shared_product_gate_p643_order9887_phase0_salt203_burst_22133_22145_density_gate_probe.json",
    },
    {
        "role": "quiet_control",
        "name": "p644_exact_quiet",
        "path": STATE_DIR
        / "low_term_total2_fixed_leaf_shared_product_gate_p644_order9887_exact_crt_repeat_22209_22212_density_gate_probe.json",
    },
    {
        "role": "quiet_control",
        "name": "p645_fresh_quiet",
        "path": STATE_DIR
        / "low_term_total2_fixed_leaf_shared_product_gate_p645_order9887_source_policy_reset_22213_22225_density_gate_probe.json",
    },
]

SALT_RE = re.compile(r":salt(?P<salt>\d+)$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def row_key_salts(case: dict[str, Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_key in case.get("row_keys") or []:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group("salt")))
    return tuple(sorted(salts))


def salt_span(salts: tuple[int, ...]) -> int:
    if len(salts) < 2:
        return 0
    return max(salts) - min(salts)


def mirror_anchor(anchor: int) -> int:
    return min(anchor, 16 - anchor)


def anchor_parity(anchor: int) -> str:
    return "odd" if anchor % 2 else "even"


def row_salt_multiset(f: dict[str, Any]) -> str:
    salts = row_key_salts(f["_case"])
    return "row_salts:" + ",".join(str(item) for item in salts)


def unordered_selector_salts(f: dict[str, Any]) -> str:
    salts = sorted([int_value(f.get("salt_left")), int_value(f.get("salt_right"))])
    return f"selector_salts:{salts[0]},{salts[1]}"


def selector_salt_span(f: dict[str, Any]) -> str:
    salts = sorted([int_value(f.get("salt_left")), int_value(f.get("salt_right"))])
    return f"salt_span:{salts[1] - salts[0]}"


def right_salt(f: dict[str, Any]) -> str:
    return f"right_salt:{f.get('salt_right')}"


def anchor_mirror(f: dict[str, Any]) -> str:
    return f"anchor_mirror:{mirror_anchor(int_value(f.get('right_anchor')))}"


def anchor_mirror_parity(f: dict[str, Any]) -> str:
    anchor = int_value(f.get("right_anchor"))
    return f"anchor_mirror:{mirror_anchor(anchor)}:parity:{anchor_parity(anchor)}"


def anchor_mod4(f: dict[str, Any]) -> str:
    return f"anchor_mod4:{int_value(f.get('right_anchor')) % 4}"


def leaf_mirror(f: dict[str, Any]) -> str:
    anchor = int_value(f.get("right_anchor"))
    return f"L{int_value(f.get('left_leaf')):02d}_Rmirror{mirror_anchor(anchor):02d}-{int_value(f.get('top_k'))}"


def row_salts_anchor_mirror(f: dict[str, Any]) -> str:
    return f"{row_salt_multiset(f)}|{anchor_mirror(f)}"


def selector_salts_anchor_mirror(f: dict[str, Any]) -> str:
    return f"{unordered_selector_salts(f)}|{anchor_mirror(f)}"


def right_salt_anchor_mirror(f: dict[str, Any]) -> str:
    return f"{right_salt(f)}|{anchor_mirror(f)}"


def salt_span_anchor_mirror(f: dict[str, Any]) -> str:
    return f"{selector_salt_span(f)}|{anchor_mirror(f)}"


def quotient_leaf_salt_span(f: dict[str, Any]) -> str:
    return f"{leaf_mirror(f)}|{selector_salt_span(f)}"


def phase_quotient_selector(f: dict[str, Any]) -> str:
    return (
        f"phase{f.get('transfer_mod12')}_mod7{f.get('transfer_mod7')}"
        f"|{unordered_selector_salts(f)}|{anchor_mirror(f)}"
    )


BUCKET_FAMILIES: list[tuple[str, str, bool, Callable[[dict[str, Any]], str]]] = [
    ("row_salt_multiset", "Unordered salts extracted from public row keys", True, row_salt_multiset),
    ("selector_salt_multiset", "Unordered selector salt pair", True, unordered_selector_salts),
    ("selector_salt_span", "Salt-pair span only", True, selector_salt_span),
    ("right_salt", "Right salt only", True, right_salt),
    ("anchor_mirror", "Right anchor mirrored under a 16-leaf quotient", True, anchor_mirror),
    ("anchor_mirror_parity", "Anchor mirror plus parity", True, anchor_mirror_parity),
    ("anchor_mod4", "Right anchor modulo 4", True, anchor_mod4),
    ("leaf_mirror", "Leaf signature with mirrored right anchor", True, leaf_mirror),
    ("row_salts_anchor_mirror", "Row salt multiset plus anchor mirror", True, row_salts_anchor_mirror),
    ("selector_salts_anchor_mirror", "Selector salt multiset plus anchor mirror", True, selector_salts_anchor_mirror),
    ("right_salt_anchor_mirror", "Right salt plus anchor mirror", True, right_salt_anchor_mirror),
    ("salt_span_anchor_mirror", "Salt span plus anchor mirror", True, salt_span_anchor_mirror),
    ("quotient_leaf_salt_span", "Mirrored leaf signature plus salt span", True, quotient_leaf_salt_span),
    ("phase_quotient_selector", "Phase/mod7 plus quotient proxy selector", False, phase_quotient_selector),
]


def feature_from_case(case: dict[str, Any], dataset: str, role: str) -> dict[str, Any]:
    feature = p643.feature(case)
    feature["_case"] = case
    feature["dataset"] = dataset
    feature["dataset_role"] = role
    feature["row_key_salts"] = list(row_key_salts(case))
    return feature


def load_dataset(item: dict[str, Any]) -> list[dict[str, Any]]:
    payload = json.loads(Path(item["path"]).read_text())
    return [
        feature_from_case(case, item["name"], item["role"])
        for case in payload.get("cases", [])
    ]


def summarize_dataset(features: list[dict[str, Any]]) -> dict[str, Any]:
    raw = p643.summarize_cases(features)
    raw["dataset_count"] = len({str(f.get("dataset")) for f in features})
    raw["datasets"] = sorted({str(f.get("dataset")) for f in features})
    return raw


def bucket_metrics(
    family: str,
    description: str,
    transfer_independent: bool,
    bucket_key: str,
    selected: list[dict[str, Any]],
) -> dict[str, Any]:
    p642 = [f for f in selected if f.get("dataset") == "p642_positive"]
    controls = [f for f in selected if f.get("dataset_role") == "quiet_control"]
    p642_verified = [f for f in p642 if f.get("direct_verified")]
    p642_below = [f for f in p642 if f.get("direct_below_rho_verified")]
    p642_rank3 = [f for f in p642_verified if int_value(f.get("rank")) >= 3]
    control_verified = [f for f in controls if f.get("direct_verified")]
    p642_count = len(p642)
    control_count = len(controls)
    below_count = len(p642_below)
    rank3_count = len(p642_rank3)
    precision = below_count / p642_count if p642_count else 0.0
    contamination_ratio = control_count / max(1, p642_count)
    # Penalize buckets that only look good by being transfer-specific.
    transfer_penalty = 1.0 if transfer_independent else 0.25
    separation_score = round(
        transfer_penalty
        * (below_count + 0.5 * rank3_count)
        * (precision + 0.01)
        / (1 + contamination_ratio),
        8,
    )
    return {
        "bucket_family": family,
        "bucket_key": bucket_key,
        "description": description,
        "transfer_independent": transfer_independent,
        "p642_selected_count": p642_count,
        "p642_direct_verified_count": len(p642_verified),
        "p642_direct_below_rho_verified_count": below_count,
        "p642_rank3_direct_verified_count": rank3_count,
        "p642_below_rho_precision": precision,
        "quiet_control_selected_count": control_count,
        "quiet_control_direct_verified_count": len(control_verified),
        "quiet_control_dataset_counts": dict(Counter(str(f.get("dataset")) for f in controls)),
        "quiet_control_load_over_p642": contamination_ratio,
        "separation_score": separation_score,
        "p642_positive_feature_counts": dict(Counter(p643.feature_id(f) for f in p642_below)),
        "p642_rank3_feature_counts": dict(Counter(p643.feature_id(f) for f in p642_rank3)),
        "p642_direct_below_rho_case_entries": [p643.case_entry(f) for f in p642_below],
        "p642_rank3_case_entries": [p643.case_entry(f) for f in p642_rank3],
        "examples": selected[:12],
    }


def family_report(
    family: str,
    description: str,
    transfer_independent: bool,
    key_fn: Callable[[dict[str, Any]], str],
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        if feature.get("parse_ok"):
            buckets[key_fn(feature)].append(feature)
    entries = [
        bucket_metrics(family, description, transfer_independent, key, selected)
        for key, selected in sorted(buckets.items())
    ]
    entries.sort(
        key=lambda item: (
            -float(item["separation_score"]),
            -int(item["p642_direct_below_rho_verified_count"]),
            -int(item["p642_rank3_direct_verified_count"]),
            int(item["quiet_control_selected_count"]),
            str(item["bucket_key"]),
        )
    )
    return {
        "bucket_family": family,
        "description": description,
        "nonempty_bucket_count": len(entries),
        "top_buckets": entries[:20],
        "top_transfer_independent_buckets": [
            item for item in entries if item.get("transfer_independent")
        ][:20],
    }


def best_buckets(reports: list[dict[str, Any]], transfer_independent_only: bool) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for report in reports:
        for item in report.get("top_buckets") or []:
            if transfer_independent_only and not item.get("transfer_independent"):
                continue
            entries.append(item)
    entries.sort(
        key=lambda item: (
            -float(item["separation_score"]),
            -int(item["p642_direct_below_rho_verified_count"]),
            -int(item["p642_rank3_direct_verified_count"]),
            int(item["quiet_control_selected_count"]),
            str(item["bucket_family"]),
            str(item["bucket_key"]),
        )
    )
    return entries[:30]


def literal_baseline(features: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        if not feature.get("parse_ok"):
            continue
        key = (
            f"phase{feature.get('transfer_mod12')}_mod7{feature.get('transfer_mod7')}"
            f"|{feature.get('row_pair')}|anchor{feature.get('right_anchor')}"
        )
        buckets[key].append(feature)
    entries = [
        bucket_metrics(
            "literal_phase_row_anchor",
            "Literal phase/mod7 plus row-pair and anchor baseline",
            False,
            key,
            selected,
        )
        for key, selected in buckets.items()
    ]
    entries.sort(
        key=lambda item: (
            -int(item["p642_direct_below_rho_verified_count"]),
            -float(item["p642_below_rho_precision"]),
            int(item["quiet_control_selected_count"]),
            str(item["bucket_key"]),
        )
    )
    return {"top_literal_buckets": entries[:20]}


def determine_claim(best_independent: list[dict[str, Any]], literal: dict[str, Any]) -> str:
    best = best_independent[0] if best_independent else None
    best_literal = (literal.get("top_literal_buckets") or [None])[0]
    if not best or int_value(best.get("p642_direct_below_rho_verified_count")) == 0:
        return "NEGATIVE_RESULT_P646_NO_PROXY_POSITIVE_CONCENTRATION"
    if (
        int_value(best.get("p642_direct_below_rho_verified_count")) >= 8
        and float(best.get("quiet_control_load_over_p642") or 0.0) <= 3.0
        and float(best.get("separation_score") or 0.0)
        >= 0.5 * float((best_literal or {}).get("separation_score") or 0.0)
    ):
        return "P646_TRANSFER_INDEPENDENT_PROXY_BUCKET_SIGNAL"
    return "P646_WEAK_PROXY_CONCENTRATION_OBSERVATION"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    features: list[dict[str, Any]] = []
    dataset_summaries: dict[str, Any] = {}
    for item in DATASETS:
        dataset_features = load_dataset(item)
        features.extend(dataset_features)
        dataset_summaries[item["name"]] = summarize_dataset(dataset_features)

    reports = [
        family_report(family, desc, independent, key_fn, features)
        for family, desc, independent, key_fn in BUCKET_FAMILIES
    ]
    literal = literal_baseline(features)
    best_independent = best_buckets(reports, transfer_independent_only=True)
    best_any = best_buckets(reports, transfer_independent_only=False)
    claim_status = determine_claim(best_independent, literal)

    payload = {
        "schema": "ecdlp.low_term_total2_p646_xonly_quotient_diagnostic.v1",
        "created_at": utc_now(),
        "method": "p646_xonly_quotient_diagnostic",
        "claim_status": claim_status,
        "artifacts": {
            "datasets": [
                {"name": item["name"], "role": item["role"], "path": str(item["path"])}
                for item in DATASETS
            ]
        },
        "summary": {
            "claim_status": claim_status,
            "dataset_summaries": dataset_summaries,
            "best_transfer_independent_proxy_buckets": best_independent[:12],
            "best_any_proxy_buckets": best_any[:12],
            "literal_baseline": literal,
        },
        "bucket_family_reports": reports,
        "honesty_boundary": [
            "Existing artifacts do not expose true elliptic-curve x-coordinates.",
            "P646 uses sign-insensitive public proxy buckets over row keys, salts, anchors, and leaf signatures.",
            "A proxy bucket is a representation-change hypothesis, not a quotient-aware relation generator.",
            "P642 positives are compared against P643/P644/P645 quiet selected-load controls.",
            "No faster-than-rho ECDLP claim follows without source-generation cost, sparse linear algebra, and target descent accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "best_transfer_independent_proxy": best_independent[0] if best_independent else None,
                "p642_direct_below_rho": dataset_summaries["p642_positive"]["direct_below_rho_verified_count"],
                "quiet_direct_verified_total": sum(
                    dataset_summaries[name]["direct_verified_count"]
                    for name in dataset_summaries
                    if name != "p642_positive"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
