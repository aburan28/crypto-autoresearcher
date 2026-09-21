#!/usr/bin/env python3
"""P745 low-cost prospective calibration grid for 67.a1@11789.

This grid reuses relation_probe.py's verifier-backed scalar-free relation
generator and searches for lower-cost calibration configurations. A row is a
candidate improvement only if it derives the target secret; cheap non-derived
rows are kept as negative controls.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
RELATION_PROBE = TASK_DIR / "relation_probe.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TARGET = "67.a1@11789"
DEFAULT_P744 = STATE_DIR / "low_term_total2_p744_calibration_cost_prospective_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p745_low_cost_calibration_grid_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p745_low_cost_calibration_grid.md"
SCHEMA = "ecdlp.low_term_total2_p745_low_cost_calibration_grid.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_relation_probe_module() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_relation_probe", RELATION_PROBE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import relation_probe from {RELATION_PROBE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def parse_csv_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def parse_csv_strings(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_target(raw: str) -> tuple[str, int]:
    label, sep, prime = raw.partition("@")
    if not sep or not label:
        raise argparse.ArgumentTypeError(f"target must be label@prime: {raw!r}")
    return label, int(prime)


def load_target(relprobe: Any, target: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    verifier = relprobe.load_verifier_module()
    records = verifier.load_records()
    label, p = parse_target(target)
    by_label = {record["label"]: record for record in records}
    record = by_label.get(label)
    if record is None:
        raise ValueError(f"unknown target label {label!r}")
    inv = verifier.reduction_invariants(record, p)
    return verifier, record, inv


def run_config(
    relprobe: Any,
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    target: str,
    width: int,
    factor_base_size: int,
    seed: str,
    trials: int,
    max_relations: int,
    max_subsets: int,
) -> dict[str, Any]:
    args = argparse.Namespace(
        factor_base_size=factor_base_size,
        max_relations=max_relations,
        max_subsets=max_subsets,
        seed=seed,
        stop_on_derive=True,
        trials=trials,
        width=width,
    )
    started = time.monotonic()
    row = relprobe.probe_target(verifier, record, inv, args)
    elapsed = round(time.monotonic() - started, 6)
    rho = int_value(row.get("generic_rho_steps"))
    cost = row.get("cost_model") if isinstance(row.get("cost_model"), dict) else {}
    single = int_value(cost.get("single_challenge_group_additions"))
    online = int_value(cost.get("estimated_online_group_additions"))
    scalar_mults = int_value(cost.get("online_scalar_mults"))
    relation_trials = int_value(row.get("relation_trials"))
    subset_additions = int_value(cost.get("one_time_subset_group_additions"))
    return {
        "accepted_mixed_relations": int_value(row.get("accepted_mixed_relations")),
        "actual_subset_coverage": row.get("actual_subset_coverage"),
        "configured_trials": trials,
        "cost_model": cost,
        "decomposition_hits": int_value(row.get("decomposition_hits")),
        "derived": bool(row.get("mixed_wide_relations_derive_secret")),
        "elapsed_seconds": elapsed,
        "factor_base_size": factor_base_size,
        "generic_rho_steps": rho,
        "improvement_ratios": {
            "online_group_additions_over_rho": ratio(online, rho),
            "online_scalar_mults_over_rho": ratio(scalar_mults, rho),
            "one_shot_group_additions_over_rho": ratio(single, rho),
            "relation_trials_over_rho": ratio(relation_trials, rho),
            "subset_additions_over_rho": ratio(subset_additions, rho),
        },
        "max_relations": max_relations,
        "max_subsets": max_subsets,
        "mixed_wide_relation_rank": int_value(row.get("mixed_wide_relation_rank")),
        "observed_decomposition_rate": row.get("observed_decomposition_rate"),
        "relation_trials": relation_trials,
        "seed": seed,
        "subset_count": int_value(row.get("subset_count")),
        "subset_sum_collisions": int_value(row.get("subset_sum_collisions")),
        "subset_unique_sums": int_value(row.get("subset_unique_sums")),
        "subset_width": width,
        "target": target,
        "trials_to_derive_secret": row.get("trials_to_derive_secret"),
    }


def p744_baseline(path: Path) -> dict[str, Any]:
    summary = load_json(path)
    best = summary.get("prospective_best_probe") if isinstance(summary.get("prospective_best_probe"), dict) else {}
    return {
        "accepted_mixed_relations": best.get("accepted_mixed_relations"),
        "derived": best.get("derived"),
        "online_group_additions_over_rho": (best.get("amortization") or {}).get("online_group_additions_over_rho"),
        "one_shot_group_additions_over_rho": best.get("one_shot_group_additions_over_rho"),
        "relation_trials": best.get("relation_trials"),
        "relation_trials_over_rho": (best.get("amortization") or {}).get("relation_trials_over_rho"),
        "scalar_mults_over_rho": (best.get("amortization") or {}).get("online_scalar_mults_over_rho"),
        "subset_count": best.get("subset_count"),
    }


def derived_sort_key(row: dict[str, Any]) -> tuple[float, float, int, int, str]:
    ratios = row.get("improvement_ratios") or {}
    one_shot = ratios.get("one_shot_group_additions_over_rho")
    online = ratios.get("online_group_additions_over_rho")
    return (
        float(one_shot) if one_shot is not None else 10**18,
        float(online) if online is not None else 10**18,
        int_value(row.get("relation_trials"), 10**9),
        int_value(row.get("factor_base_size"), 10**9),
        str(row.get("seed")),
    )


def determine_claim(best: dict[str, Any] | None, baseline: dict[str, Any]) -> str:
    if not best:
        return "NEGATIVE_RESULT_P745_NO_DERIVED_LOW_COST_CONFIGURATION"
    one_shot = (best.get("improvement_ratios") or {}).get("one_shot_group_additions_over_rho")
    online = (best.get("improvement_ratios") or {}).get("online_group_additions_over_rho")
    base_one = baseline.get("one_shot_group_additions_over_rho")
    if one_shot is not None and one_shot < 1.0:
        return "P745_LOW_COST_CALIBRATION_ONE_SHOT_BELOW_RHO_SIGNAL"
    if online is not None and online < 1.0:
        return "P745_LOW_COST_CALIBRATION_ONLINE_BELOW_RHO_SIGNAL"
    if one_shot is not None and base_one is not None and one_shot < float(base_one):
        return "P745_CALIBRATION_COST_REDUCTION_SIGNAL_GROUP_ABOVE_RHO"
    return "NEGATIVE_RESULT_P745_NO_GROUP_COST_REDUCTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    relprobe = load_relation_probe_module()
    verifier, record, inv = load_target(relprobe, args.target)
    baseline = p744_baseline(args.p744_summary)
    factor_base_sizes = parse_csv_ints(args.factor_base_sizes)
    widths = parse_csv_ints(args.widths)
    seeds = parse_csv_strings(args.seeds)
    rows: list[dict[str, Any]] = []
    for width in widths:
        for factor_base_size in factor_base_sizes:
            if factor_base_size < width:
                continue
            for seed in seeds:
                rows.append(
                    run_config(
                        relprobe,
                        verifier,
                        record,
                        inv,
                        args.target,
                        width,
                        factor_base_size,
                        f"{args.seed_prefix}:{seed}:fb{factor_base_size}:w{width}",
                        args.trials,
                        args.max_relations,
                        args.max_subsets,
                    )
                )
    derived_rows = [row for row in rows if row.get("derived")]
    derived_rows.sort(key=derived_sort_key)
    best = derived_rows[0] if derived_rows else None
    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p744_summary": str(args.p744_summary),
            "script": str(Path(__file__)),
        },
        "baseline": {
            "p744_best": baseline,
            "pollard_rho_baseline_steps": math.ceil(math.sqrt(math.pi * int_value(inv.get("base_order")) / 2.0)),
        },
        "claim_status": "",
        "created_at": now_iso(),
        "grid_parameters": {
            "factor_base_sizes": factor_base_sizes,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "seed_prefix": args.seed_prefix,
            "seeds": seeds,
            "target": args.target,
            "trials": args.trials,
            "widths": widths,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: grid uses the existing relation_probe scalar-free subset relation model.",
            "PRIMARY COST MODEL: group additions including subset precomputation remain the speedup gate.",
            "NEGATIVE CONTROL: non-derived low-cost rows are not counted as improvements.",
            "NO DEPLOYED-CURVE CLAIM: no sparse-linear-algebra or large-prime scaling result is implied.",
        ],
        "method": "p745_low_cost_prospective_calibration_grid",
        "results": rows,
        "schema": SCHEMA,
        "summary": {
            "best_derived": best,
            "configuration_count": len(rows),
            "derived_count": len(derived_rows),
            "derived_one_shot_ratio_stats": stat(
                [
                    row["improvement_ratios"]["one_shot_group_additions_over_rho"]
                    for row in derived_rows
                    if row["improvement_ratios"]["one_shot_group_additions_over_rho"] is not None
                ]
            ),
            "derived_online_ratio_stats": stat(
                [
                    row["improvement_ratios"]["online_group_additions_over_rho"]
                    for row in derived_rows
                    if row["improvement_ratios"]["online_group_additions_over_rho"] is not None
                ]
            ),
            "nonderived_count": len(rows) - len(derived_rows),
            "top_derived": derived_rows[:10],
        },
    }
    payload["claim_status"] = determine_claim(best, baseline)
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "baseline": payload["baseline"],
        "grid_parameters": payload["grid_parameters"],
        "honesty_boundary": payload["honesty_boundary"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--factor-base-sizes", default="12,16,20,24,28,32,36,40,44,48")
    parser.add_argument("--widths", default="2,3")
    parser.add_argument("--seeds", default="p745-a,p745-b,p745-c")
    parser.add_argument("--seed-prefix", default="ecdlp-p745-grid-v1")
    parser.add_argument("--trials", type=int, default=1024)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--p744-summary", type=Path, default=DEFAULT_P744)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    best = summary["summary"]["best_derived"] or {}
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_derived": {
                    key: best.get(key)
                    for key in [
                        "target",
                        "factor_base_size",
                        "subset_width",
                        "seed",
                        "relation_trials",
                        "accepted_mixed_relations",
                        "mixed_wide_relation_rank",
                        "improvement_ratios",
                    ]
                }
                if best
                else None,
                "claim_status": summary["claim_status"],
                "configuration_count": summary["summary"]["configuration_count"],
                "derived_count": summary["summary"]["derived_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
