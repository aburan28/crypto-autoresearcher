#!/usr/bin/env python3
"""Public feature-delta diagnostic for P577/P578 relation-supply rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_POSITIVE_SOURCE = STATE_DIR / "low_term_total2_order9887_p577_leaf16_motif_extension_source_20725_20736_probe.json"
DEFAULT_POSITIVE_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p577_order9887_motif_extension_20725_20736_density_gate_probe.json"
DEFAULT_QUIET_SOURCE = STATE_DIR / "low_term_total2_order9887_p578_leaf16_phase_aware_motif_source_20737_20748_probe.json"
DEFAULT_QUIET_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p578_order9887_phase_aware_motif_20737_20748_density_gate_probe.json"
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_order9887_p579_relation_supply_source_20749_20760_probe.json"
DEFAULT_VALIDATION_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p579_order9887_relation_supply_20749_20760_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p579_relation_supply_discriminant_20749_20760_probe.json"


Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def phase_salt_anchor(row: Feature, phase: int, salt_right: int, anchor: int) -> bool:
    return (
        int(row.get("transfer_mod12") or -1) == phase
        and row.get("salt_right") == salt_right
        and row.get("right_anchor") == anchor
    )


def phase_salt_anchor_mod7(row: Feature, phase: int, salt_right: int, anchor: int, mod7: int) -> bool:
    return phase_salt_anchor(row, phase, salt_right, anchor) and int(row.get("transfer_mod7") or -1) == mod7


def p577_phase_only(row: Feature) -> bool:
    return phase_salt_anchor(row, 2, 208, 11) or phase_salt_anchor(row, 11, 207, 9)


def p577_phase_mod7(row: Feature) -> bool:
    return phase_salt_anchor_mod7(row, 2, 208, 11, 6) or phase_salt_anchor_mod7(row, 11, 207, 9, 1)


def p577_phase2_right208_anchor11_mod7_6(row: Feature) -> bool:
    return phase_salt_anchor_mod7(row, 2, 208, 11, 6)


def p577_phase11_right207_anchor9_mod7_1(row: Feature) -> bool:
    return phase_salt_anchor_mod7(row, 11, 207, 9, 1)


def p578_quiet_phase_mod7(row: Feature) -> bool:
    return phase_salt_anchor_mod7(row, 2, 208, 11, 4) or phase_salt_anchor_mod7(row, 11, 207, 9, 6)


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p577_phase_mod7_relation_supply_union",
            "P577 phase/salt/anchor plus transfer_mod7: phase2/right208/anchor11/mod7=6 or phase11/right207/anchor9/mod7=1",
            p577_phase_mod7,
        ),
        (
            "p577_phase_only_control",
            "P577 phase/salt/anchor without mod7 discriminant",
            p577_phase_only,
        ),
        (
            "p577_phase2_right208_anchor11_mod7_6",
            "P577 phase-2/right208/anchor11/mod7=6 branch",
            p577_phase2_right208_anchor11_mod7_6,
        ),
        (
            "p577_phase11_right207_anchor9_mod7_1",
            "P577 phase-11/right207/anchor9/mod7=1 branch",
            p577_phase11_right207_anchor9_mod7_1,
        ),
        (
            "p578_quiet_phase_mod7_control",
            "P578 quiet transfer_mod7 controls: phase2/right208/anchor11/mod7=4 or phase11/right207/anchor9/mod7=6",
            p578_quiet_phase_mod7,
        ),
    ]


def feature_tokens(row: Feature) -> list[str]:
    return [
        f"base_selector={row.get('base_selector')}",
        f"leaf_signature={row.get('leaf_signature')}",
        f"phase={row.get('transfer_mod12')}",
        f"phase_mod7={row.get('transfer_mod12')}:{row.get('transfer_mod7')}",
        f"policy_role={row.get('policy_role')}",
        f"right={row.get('salt_right')}:{row.get('right_anchor')}",
        f"right_phase={row.get('transfer_mod12')}:{row.get('salt_right')}:{row.get('right_anchor')}",
        f"right_phase_mod7={row.get('transfer_mod12')}:{row.get('salt_right')}:{row.get('right_anchor')}:{row.get('transfer_mod7')}",
        f"row_pair={row.get('row_pair')}",
        f"row_pair_anchor={row.get('row_pair')}:{row.get('right_anchor')}",
        f"salt_pair={row.get('salt_left')}:{row.get('salt_right')}",
        f"transfer_mod7={row.get('transfer_mod7')}",
    ]


def compact_row(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "direct_verified": row["direct_verified"],
        "leaf_signature": row["leaf_signature"],
        "policy_role": row["policy_role"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "salt_left": row["salt_left"],
        "salt_right": row["salt_right"],
        "selector": row["selector"],
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
        "transfer_mod7": row["transfer_mod7"],
    }


def selected_quiet_rows(rows: list[Feature]) -> list[Feature]:
    return [row for row in rows if p577_phase_only(row)]


def training_delta(positive_rows: list[Feature], quiet_rows: list[Feature]) -> dict[str, Any]:
    positive_tokens = Counter(token for row in positive_rows for token in feature_tokens(row))
    quiet_tokens = Counter(token for row in quiet_rows for token in feature_tokens(row))
    union = set(positive_tokens) | set(quiet_tokens)
    ranked = []
    for token in sorted(union):
        pos = positive_tokens[token]
        quiet = quiet_tokens[token]
        ranked.append(
            {
                "quiet_count": quiet,
                "token": token,
                "positive_count": pos,
                "positive_minus_quiet": pos - quiet,
                "positive_precision": ratio(pos, pos + quiet),
            }
        )
    ranked.sort(key=lambda item: (item["positive_minus_quiet"], item["positive_count"]), reverse=True)
    return {
        "positive_count": len(positive_rows),
        "quiet_count": len(quiet_rows),
        "top_positive_tokens": ranked[:32],
        "top_quiet_tokens": sorted(
            ranked,
            key=lambda item: (item["quiet_count"] - item["positive_count"], item["quiet_count"]),
            reverse=True,
        )[:16],
    }


def report(rows: list[Feature], selected: list[Feature], name: str, description: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "raw_positive_count": len(positives),
        "raw_verified_count": len(verified),
        "right_anchor_counts": dict(Counter(str(row["right_anchor"]) for row in selected).most_common()),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
        "salt_right_counts": dict(Counter(str(row["salt_right"]) for row in selected).most_common()),
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_count": len(selected),
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in selected_positive],
        "selected_direct_verified_case_entries": [row["case_entry"] for row in selected_verified],
        "selected_fraction": ratio(len(selected), len(rows)),
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))
        ),
    }


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": len(verified),
        "positive_phase_salt_anchor_mod7_counts": dict(
            Counter(
                f"phase{row.get('transfer_mod12')}_right{row.get('salt_right')}_anchor{row.get('right_anchor')}_mod7{row.get('transfer_mod7')}"
                for row in positives
            ).most_common()
        ),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
        "verified_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in verified).items(), key=lambda item: int(item[0]))
        ),
    }


def load_rows(source: Path, gate: Path, prefix: str) -> list[Feature]:
    return p570.source_rows([source], p570.gate_labels([gate]), prefix)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive-source", type=Path, default=DEFAULT_POSITIVE_SOURCE)
    parser.add_argument("--positive-gate", type=Path, default=DEFAULT_POSITIVE_GATE)
    parser.add_argument("--quiet-source", type=Path, default=DEFAULT_QUIET_SOURCE)
    parser.add_argument("--quiet-gate", type=Path, default=DEFAULT_QUIET_GATE)
    parser.add_argument("--validation-source", type=Path, default=DEFAULT_VALIDATION_SOURCE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    positive_all = load_rows(args.positive_source, args.positive_gate, "p577_positive")
    quiet_all = load_rows(args.quiet_source, args.quiet_gate, "p578_quiet")
    validation = load_rows(args.validation_source, args.validation_gate, "validation")

    positive_rows = [row for row in positive_all if row["direct_below_rho_verified"]]
    quiet_rows = selected_quiet_rows(quiet_all)
    reports = [
        report(validation, [row for row in validation if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    payload = {
        "artifacts": {
            "positive_gate": str(args.positive_gate),
            "positive_source": str(args.positive_source),
            "quiet_gate": str(args.quiet_gate),
            "quiet_source": str(args.quiet_source),
            "validation_gate": str(args.validation_gate),
            "validation_source": str(args.validation_source),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: validation rules use public transfer residues, right salt, and right anchor only.",
            "LABEL BOUNDARY: P577 direct outcomes are used only to train this discriminant and validation labels are joined only for evaluation.",
            "HEURISTIC: transfer_mod7 is a relation-supply hypothesis, not an algebraic theorem.",
            "NO SPEEDUP CLAIM: public product-gate selection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p579_relation_supply_discriminant",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p579_relation_supply_discriminant.v1",
        "summary": {
            "claim_status": (
                "P579_RELATION_SUPPLY_DISCRIMINANT_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "P579_RELATION_SUPPLY_DISCRIMINANT_DIRECT_VERIFIED_DIAGNOSTIC"
                if main_report["direct_verified_count"]
                else "NEGATIVE_RESULT_P579_RELATION_SUPPLY_DISCRIMINANT_NO_VALIDATION_SIGNAL"
            ),
            "training_delta": training_delta(positive_rows, quiet_rows),
            "validation_dataset": dataset_summary(validation),
            "main_rule": main_report,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
