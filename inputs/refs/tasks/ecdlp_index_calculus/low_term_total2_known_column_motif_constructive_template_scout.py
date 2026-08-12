#!/usr/bin/env python3
"""Scout coarse constructive templates for known-column motif generation.

The public metadata scorer improved ranking a little, but it mostly learned
salt/transfer residues.  This probe asks a narrower constructive question:
can coarse public source templates, such as selected-support signature, top-k,
known-column presence/missing pattern, or salt-gap bucket, force the desired
relation-support motifs often enough to close the motif-oracle gap?

The templates are selected on calibration windows and evaluated on later
windows with source rows charged.  The result is intentionally scoped: a
failure here rules out this coarse template family, not motif generation.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from low_term_total2_known_column_motif_oracle_gap_scout import (
    case_supports,
    evaluate_current_pressure,
    evaluate_motif_oracle,
    int_value,
    learned_motifs,
    parse_motifs,
    parse_paths,
    stat,
    window_from_path,
)


SALT_RE = re.compile(r"salt(\d+)")
Template = Callable[[dict[str, Any]], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def salts_from_rows(row_keys: list[Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return tuple(salts)


def gap_bucket(gap: int | None) -> str:
    if gap is None:
        return "none"
    if gap <= 2:
        return "01_02"
    if gap <= 5:
        return "03_05"
    if gap <= 8:
        return "06_08"
    return "09_plus"


def compact_case(case: dict[str, Any] | None) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_index": case.get("case_index"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "hit": case.get("hit"),
        "known_structural_motifs": [list(motif) for motif in case.get("known_structural_motifs") or []],
        "row_keys": case.get("row_keys"),
        "salt_gap": case.get("salt_gap"),
        "salt_gap_bucket": case.get("salt_gap_bucket"),
        "selected_support": list(case.get("selected_support") or []),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unknown_motifs": [list(motif) for motif in case.get("unknown_motifs") or []],
        "verified_motifs": [list(motif) for motif in case.get("verified_motifs") or []],
    }


def load_window(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    start, end = window_from_path(path)
    cases: list[dict[str, Any]] = []
    for index, case in enumerate(payload.get("case_results") or []):
        if not isinstance(case, dict):
            continue
        selected = case.get("selected") if isinstance(case.get("selected"), dict) else {}
        row_keys = [str(row) for row in selected.get("row_keys") or []]
        salts = salts_from_rows(row_keys)
        salt_gap = abs(salts[1] - salts[0]) if len(salts) >= 2 else None
        selected_support = tuple(int_value(value) for value in case.get("selected_term_support") or [])
        known_present = tuple(value for value in selected_support if 7 <= value <= 14)
        known_missing = tuple(value for value in range(7, 15) if value not in selected_support)
        cases.append(
            {
                "artifact": str(path),
                "case_index": index,
                "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                "hit": bool(case.get("public_known_factor_verified")),
                **case_supports(case),
                "known_missing": known_missing,
                "known_present": known_present,
                "row_keys": row_keys,
                "salt_gap": salt_gap,
                "salt_gap_bucket": gap_bucket(salt_gap),
                "selected_support": selected_support,
                "top_k": int_value(selected.get("top_k")),
                "transfer_index": int_value(selected.get("transfer_index")),
            }
        )
    return {
        "artifact": str(path),
        "end": end,
        "start": start,
        "summary": payload.get("summary") or {},
        "cases": cases,
    }


def target_label(case: dict[str, Any], target_motifs: set[tuple[int, ...]]) -> bool:
    return any(tuple(motif) in target_motifs for motif in case.get("known_structural_motifs") or []) or any(
        tuple(motif) in target_motifs for motif in case.get("verified_motifs") or []
    )


def template_specs(calibration: list[dict[str, Any]], target_motifs: set[tuple[int, ...]]) -> dict[str, Template]:
    all_cases = [case for window in calibration for case in window["cases"]]
    target_cases = [case for case in all_cases if target_label(case, target_motifs)]
    specs: dict[str, Template] = {
        "all_pressure_cases": lambda case: True,
    }
    for top_k in sorted({int_value(case.get("top_k")) for case in all_cases}):
        specs[f"topk={top_k}"] = lambda case, top_k=top_k: int_value(case.get("top_k")) == top_k
    for support in sorted({tuple(case.get("selected_support") or []) for case in target_cases}):
        specs[f"support={','.join(map(str, support))}"] = (
            lambda case, support=support: tuple(case.get("selected_support") or []) == support
        )
    for present in sorted({tuple(case.get("known_present") or []) for case in target_cases}):
        specs[f"known_present={','.join(map(str, present))}"] = (
            lambda case, present=present: tuple(case.get("known_present") or []) == present
        )
    for missing in sorted({tuple(case.get("known_missing") or []) for case in target_cases}):
        specs[f"known_missing={','.join(map(str, missing))}"] = (
            lambda case, missing=missing: tuple(case.get("known_missing") or []) == missing
        )
    for bucket in sorted({str(case.get("salt_gap_bucket")) for case in target_cases}):
        specs[f"salt_gap_bucket={bucket}"] = (
            lambda case, bucket=bucket: str(case.get("salt_gap_bucket")) == bucket
        )
    for top_k in sorted({int_value(case.get("top_k")) for case in target_cases}):
        for bucket in sorted({str(case.get("salt_gap_bucket")) for case in target_cases}):
            specs[f"topk={top_k}|salt_gap_bucket={bucket}"] = (
                lambda case, top_k=top_k, bucket=bucket: (
                    int_value(case.get("top_k")) == top_k
                    and str(case.get("salt_gap_bucket")) == bucket
                )
            )
    for support in sorted({tuple(case.get("selected_support") or []) for case in target_cases}):
        for top_k in sorted({int_value(case.get("top_k")) for case in target_cases}):
            specs[f"support={','.join(map(str, support))}|topk={top_k}"] = (
                lambda case, support=support, top_k=top_k: (
                    tuple(case.get("selected_support") or []) == support
                    and int_value(case.get("top_k")) == top_k
                )
            )
    return specs


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hits = [row for row in rows if row.get("hit")]
    structural = [row for row in rows if row.get("selected_structural") or row.get("hit")]
    costs = [float_value(row.get("cost_over_rho")) for row in rows]
    total = sum(costs)
    return {
        "cost_over_rho": stat(costs),
        "cost_per_hit_window_over_rho": round(total / len(hits), 8) if hits else None,
        "cost_per_structural_window_over_rho": round(total / len(structural), 8) if structural else None,
        "direct_scan_count": sum(int_value(row.get("direct_scan_count")) for row in rows),
        "hit_window_count": len(hits),
        "rows": rows,
        "selected_window_count": sum(1 for row in rows if int_value(row.get("direct_scan_count")) > 0),
        "source_row_count": sum(int_value(row.get("source_row_count")) for row in rows),
        "structural_window_count": len(structural),
        "window_count": len(rows),
    }


def evaluate_template(
    windows: list[dict[str, Any]],
    predicate: Template,
    source_row_cost_over_rho: float,
) -> dict[str, Any]:
    rows = []
    for window in windows:
        cost = 0.0
        source_rows = 0
        direct_scans = 0
        selected_structural = None
        hit_case = None
        for case in window["cases"]:
            source_rows += 1
            cost += source_row_cost_over_rho
            if not predicate(case):
                continue
            direct_scans += 1
            cost += float_value(case.get("direct_ops_over_rho"))
            if selected_structural is None and (case.get("known_structural_motifs") or case.get("verified_motifs")):
                selected_structural = case
            if case.get("hit"):
                hit_case = case
                break
        rows.append(
            {
                "cost_over_rho": round(cost, 8),
                "direct_scan_count": direct_scans,
                "hit": hit_case is not None,
                "hit_case": compact_case(hit_case),
                "selected_structural": selected_structural is not None,
                "source_row_count": source_rows,
                "structural_case": compact_case(selected_structural),
                "window": f"{window['start']}_{window['end']}",
            }
        )
    return summarize_rows(rows)


def choose_template(
    calibration: list[dict[str, Any]],
    specs: dict[str, Template],
    source_row_cost_over_rho: float,
    min_hit_windows: int,
) -> dict[str, Any]:
    rows = []
    for name, predicate in specs.items():
        result = evaluate_template(calibration, predicate, source_row_cost_over_rho)
        hit_windows = int_value(result.get("hit_window_count"))
        cost_per_hit = result.get("cost_per_hit_window_over_rho")
        rows.append(
            {
                "cost_per_hit_window_over_rho": cost_per_hit,
                "direct_scan_count": result.get("direct_scan_count"),
                "hit_window_count": hit_windows,
                "selected_window_count": result.get("selected_window_count"),
                "source_row_count": result.get("source_row_count"),
                "template": name,
            }
        )
    eligible = [
        row for row in rows
        if int_value(row.get("hit_window_count")) >= min_hit_windows
        and isinstance(row.get("cost_per_hit_window_over_rho"), (int, float))
    ]
    eligible.sort(
        key=lambda row: (
            float_value(row.get("cost_per_hit_window_over_rho"), 999.0),
            -int_value(row.get("hit_window_count")),
            int_value(row.get("direct_scan_count")),
            row.get("template"),
        )
    )
    rows.sort(
        key=lambda row: (
            float_value(row.get("cost_per_hit_window_over_rho"), 999.0),
            -int_value(row.get("hit_window_count")),
            row.get("template"),
        )
    )
    best = eligible[0] if eligible else rows[0]
    return {
        "best_template": best["template"],
        "eligible_template_count": len(eligible),
        "top_templates": rows[:16],
    }


def degeneracy_report(windows: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [case for window in windows for case in window["cases"]]
    supports = {tuple(case.get("selected_support") or []) for case in cases}
    known_present = {tuple(case.get("known_present") or []) for case in cases}
    no_structural_windows = []
    for window in windows:
        if not any(case.get("known_structural_motifs") or case.get("verified_motifs") for case in window["cases"]):
            no_structural_windows.append(f"{window['start']}_{window['end']}")
    return {
        "case_count": len(cases),
        "no_structural_window_count": len(no_structural_windows),
        "no_structural_windows": no_structural_windows,
        "unique_known_present_count": len(known_present),
        "unique_known_present": [list(row) for row in sorted(known_present)[:16]],
        "unique_selected_support_count": len(supports),
        "unique_selected_supports": [list(row) for row in sorted(supports)[:16]],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--calibration-end-max", type=int, default=3055)
    parser.add_argument("--min-calibration-hit-windows", type=int, default=15)
    parser.add_argument("--min-motif-count", type=int, default=2)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--seed-known-motifs",
        default="8:11,9:11,10:13,10:14,11:13",
        help="comma-separated motifs, each encoded with colon-separated columns",
    )
    parser.add_argument("--source-row-cost-over-rho", type=float, default=1.0 / 137.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.artifacts)
    windows = [load_window(path) for path in paths]
    calibration = [window for window in windows if int_value(window.get("end")) <= args.calibration_end_max]
    validation = [window for window in windows if int_value(window.get("end")) > args.calibration_end_max]
    oracle_windows = [
        {
            **window,
            "cases": [
                {key: value for key, value in case.items() if key not in {"selected_support", "known_present", "known_missing"}}
                for case in window["cases"]
            ],
        }
        for window in windows
    ]
    oracle_calibration = [window for window in oracle_windows if int_value(window.get("end")) <= args.calibration_end_max]
    oracle_validation = [window for window in oracle_windows if int_value(window.get("end")) > args.calibration_end_max]
    target_motifs, avoid_motifs = learned_motifs(
        oracle_calibration,
        args.min_motif_count,
        parse_motifs(args.seed_known_motifs),
    )
    specs = template_specs(calibration, target_motifs)
    choice = choose_template(
        calibration,
        specs,
        args.source_row_cost_over_rho,
        args.min_calibration_hit_windows,
    )
    best_name = str(choice["best_template"])
    best_predicate = specs[best_name]
    template_validation = evaluate_template(validation, best_predicate, args.source_row_cost_over_rho)
    current = evaluate_current_pressure(oracle_validation)
    oracle = evaluate_motif_oracle(oracle_validation, target_motifs, avoid_motifs)
    template_cost = template_validation.get("cost_per_hit_window_over_rho")
    if isinstance(template_cost, (int, float)) and template_cost < 1.0:
        claim_status = "CONSTRUCTIVE_TEMPLATE_BELOW_RHO_CANDIDATE"
    elif int_value(template_validation.get("hit_window_count")) > 0:
        claim_status = "CONSTRUCTIVE_TEMPLATE_RECOVERS_NEEDS_DENSITY_GAIN"
    else:
        claim_status = "CONSTRUCTIVE_TEMPLATE_NO_FORWARD_HIT"
    payload = {
        "artifacts": [str(path) for path in paths],
        "calibration_end_max": args.calibration_end_max,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "degeneracy": {
            "calibration": degeneracy_report(calibration),
            "validation": degeneracy_report(validation),
        },
        "honesty_boundary": {
            "assumptions": [
                "Templates use coarse public source features only: selected support, known-column pattern, top-k, and salt-gap bucket.",
                "Template selection uses motif labels on calibration windows only.",
                "Validation charges skipped source rows and direct scans, but still uses direct-source pressure artifacts.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST / COARSE-TEMPLATE-SCOUT",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "full source generator",
                "shared-product amortized collector",
            ],
        },
        "learned_motifs": {
            "avoid_motifs": [list(motif) for motif in sorted(avoid_motifs)],
            "min_motif_count": args.min_motif_count,
            "seed_known_motifs": [list(motif) for motif in sorted(parse_motifs(args.seed_known_motifs))],
            "target_motifs": [list(motif) for motif in sorted(target_motifs)],
        },
        "schema": "ecdlp.low_term_total2_known_column_motif_constructive_template_scout.v1",
        "selection_results": {
            "current_pressure_order": current,
            "motif_oracle": oracle,
            "template_filter": template_validation,
        },
        "source_row_cost_over_rho": round(args.source_row_cost_over_rho, 8),
        "summary": {
            "best_template": best_name,
            "current_cost_per_hit_window_over_rho": current.get("cost_per_hit_window_over_rho"),
            "motif_oracle_cost_per_hit_window_over_rho": oracle.get("cost_per_hit_window_over_rho"),
            "template_cost_per_hit_window_over_rho": template_validation.get("cost_per_hit_window_over_rho"),
            "template_hit_window_count": template_validation.get("hit_window_count"),
        },
        "template_selection": choice,
        "window_split": {
            "calibration": [f"{window['start']}_{window['end']}" for window in calibration],
            "validation": [f"{window['start']}_{window['end']}" for window in validation],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
