#!/usr/bin/env python3
"""P746 incremental-walk online-cost audit for 67.a1@11789.

P745 showed that relation generation can derive a calibration system, but its
online cost model paid two fresh scalar multiplications per trial. This probe
keeps the same verifier-backed subset relation model and tests public walks
where only the initial mixed point is scalar-multiplied; later trials advance by
one group addition. One-shot subset-table setup remains charged separately.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
RELATION_PROBE = TASK_DIR / "relation_probe.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TARGET = "67.a1@11789"
DEFAULT_P745 = STATE_DIR / "low_term_total2_p745_low_cost_calibration_grid_width2_seed_extension_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p746_incremental_walk_online_cost_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p746_incremental_walk_online_cost.md"
SCHEMA = "ecdlp.low_term_total2_p746_incremental_walk_online_cost.v1"


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


def deterministic_start(order: int, seed: str, mode: str) -> tuple[int, int]:
    digest = hashlib.sha256(f"{seed}:{mode}:walk-start".encode()).digest()
    rng = random.Random(int.from_bytes(digest, "big"))
    a = rng.randrange(order)
    b = 1 + rng.randrange(order - 1)
    return a, b


def walk_delta(verifier: Any, mode: str, base: Any, public: Any, ainvs: list[int], p: int) -> dict[str, Any]:
    neg_public = verifier.neg_point(public, ainvs, p)
    if mode == "inc_a":
        return {"da": 1, "db": 0, "delta": base, "delta_setup_group_additions": 0, "walk_update_group_additions": 1}
    if mode == "inc_b":
        return {"da": 0, "db": 1, "delta": public, "delta_setup_group_additions": 0, "walk_update_group_additions": 1}
    if mode == "inc_ab":
        return {
            "da": 1,
            "db": 1,
            "delta": verifier.add_points(base, public, ainvs, p),
            "delta_setup_group_additions": 1,
            "walk_update_group_additions": 1,
        }
    if mode == "inc_a_neg_b":
        return {
            "da": 1,
            "db": -1,
            "delta": verifier.add_points(base, neg_public, ainvs, p),
            "delta_setup_group_additions": 1,
            "walk_update_group_additions": 1,
        }
    if mode == "inc_2a_b":
        two_base = verifier.add_points(base, base, ainvs, p)
        return {
            "da": 2,
            "db": 1,
            "delta": verifier.add_points(two_base, public, ainvs, p),
            "delta_setup_group_additions": 2,
            "walk_update_group_additions": 1,
        }
    if mode == "inc_a_2b":
        two_public = verifier.add_points(public, public, ainvs, p)
        return {
            "da": 1,
            "db": 2,
            "delta": verifier.add_points(base, two_public, ainvs, p),
            "delta_setup_group_additions": 2,
            "walk_update_group_additions": 1,
        }
    raise ValueError(f"unknown walk mode {mode!r}")


def walk_schedule(verifier: Any, mode: str, base: Any, public: Any, ainvs: list[int], p: int) -> dict[str, Any]:
    base_modes = ("inc_a", "inc_b", "inc_ab", "inc_a_neg_b", "inc_2a_b", "inc_a_2b")
    if mode in base_modes:
        delta = walk_delta(verifier, mode, base, public, ainvs, p)
        return {
            "delta_options": [delta],
            "delta_setup_group_additions": int(delta["delta_setup_group_additions"]),
            "mode": mode,
            "scheduled": False,
            "walk_update_group_additions": 1,
        }
    if mode in {"cycle6", "hash6"}:
        options = [walk_delta(verifier, option_mode, base, public, ainvs, p) for option_mode in base_modes]
        return {
            "delta_options": options,
            "delta_setup_group_additions": sum(int(option["delta_setup_group_additions"]) for option in options),
            "mode": mode,
            "scheduled": True,
            "walk_update_group_additions": 1,
        }
    raise ValueError(f"unknown walk mode {mode!r}")


def select_delta(walk: dict[str, Any], seed: str, trial: int, a: int, b: int) -> dict[str, Any]:
    options = walk["delta_options"]
    if len(options) == 1 or walk["mode"] == "cycle6":
        return options[(trial - 1) % len(options)]
    if walk["mode"] == "hash6":
        digest = hashlib.sha256(f"{seed}:{trial}:{a}:{b}".encode()).digest()
        return options[int.from_bytes(digest[:8], "big") % len(options)]
    raise ValueError(f"unknown walk schedule {walk['mode']!r}")


def p745_baseline(path: Path) -> dict[str, Any]:
    summary = load_json(path)
    best = (summary.get("summary") or {}).get("best_derived") if isinstance(summary.get("summary"), dict) else {}
    ratios = best.get("improvement_ratios") if isinstance(best, dict) else {}
    return {
        "accepted_mixed_relations": best.get("accepted_mixed_relations") if isinstance(best, dict) else None,
        "derived": best.get("derived") if isinstance(best, dict) else None,
        "factor_base_size": best.get("factor_base_size") if isinstance(best, dict) else None,
        "online_group_additions_over_rho": ratios.get("online_group_additions_over_rho") if isinstance(ratios, dict) else None,
        "one_shot_group_additions_over_rho": ratios.get("one_shot_group_additions_over_rho") if isinstance(ratios, dict) else None,
        "relation_trials": best.get("relation_trials") if isinstance(best, dict) else None,
        "relation_trials_over_rho": ratios.get("relation_trials_over_rho") if isinstance(ratios, dict) else None,
        "seed": best.get("seed") if isinstance(best, dict) else None,
        "subset_count": best.get("subset_count") if isinstance(best, dict) else None,
        "subset_width": best.get("subset_width") if isinstance(best, dict) else None,
    }


def scan_walk(
    relprobe: Any,
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    target: str,
    factor_base_size: int,
    width: int,
    mode: str,
    seed: str,
    trials: int,
    max_relations: int,
    max_subsets: int,
) -> dict[str, Any]:
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, seed, factor_base_size)
    base = verifier.point_from_json(challenge["base"])
    public = verifier.point_from_json(challenge["public"])
    full_factor_base = [verifier.point_from_json(point) for point in challenge["factor_base"]]
    factor_base = full_factor_base[: max(1, min(factor_base_size, len(full_factor_base)))]
    subset_table, subset_count, subset_collisions = relprobe.build_subset_table(
        verifier,
        factor_base,
        ainvs,
        p,
        width,
        max_subsets,
    )
    walk = walk_schedule(verifier, mode, base, public, ainvs, p)
    a, b = deterministic_start(order, seed, mode)
    lhs = verifier.add_points(
        verifier.mul_point(a, base, ainvs, p),
        verifier.mul_point(b, public, ainvs, p),
        ainvs,
        p,
    )

    forms: list[tuple[Any, int, list[int]]] = []
    seen_forms: set[tuple[Any, int]] = set()
    relations: list[dict[str, Any]] = []
    hits = 0
    first_hit_at = None
    derived_at = None
    zero_b_hits = 0
    zero_b_skips = 0
    derived = {"mixed_wide_relations_derive_secret": False, "mixed_wide_relation_rank": 0, "derived_secret": None}
    attempted_trials = 0
    started = time.monotonic()

    for trial in range(1, trials + 1):
        attempted_trials = trial
        indices = subset_table.get(lhs)
        if indices is not None:
            hits += 1
            first_hit_at = first_hit_at or trial
            if b % order == 0:
                zero_b_hits += 1
                zero_b_skips += 1
            else:
                relation = {"a": int(a), "b": int(b), "indices": [int(index) for index in indices]}
                terms = verifier.relation_terms(relation, challenge, ainvs, p)
                if terms is not None and verifier.verify_relation(relation, challenge, ainvs, p, base, public):
                    coeffs, rhs = verifier.relation_linear_form(relation, terms, challenge, order)
                    key = (coeffs, rhs)
                    if key not in seen_forms:
                        seen_forms.add(key)
                        relations.append(relation)
                        forms.append((coeffs, rhs, terms))
                        if len(relations) >= max_relations:
                            derived = relprobe.linear_rank_probe(verifier, forms, order)
                            if derived["mixed_wide_relations_derive_secret"]:
                                derived_at = trial
                            break
                        if len(relations) >= 8:
                            current = relprobe.linear_rank_probe(verifier, forms, order)
                            if current["mixed_wide_relations_derive_secret"]:
                                derived = current
                                derived_at = trial
                                break

        if trial == trials:
            break
        delta = select_delta(walk, seed, trial, a, b)
        a = (a + int(delta["da"])) % order
        b = (b + int(delta["db"])) % order
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    if not derived["mixed_wide_relations_derive_secret"]:
        derived = relprobe.linear_rank_probe(verifier, forms, order)

    elapsed = round(time.monotonic() - started, 6)
    rho = int(challenge["generic_rho_steps"])
    bit_length = max(1, order.bit_length())
    initial_mixed_group_additions = (2 * bit_length) + 1
    delta_setup_group_additions = int(walk["delta_setup_group_additions"])
    updates = max(0, attempted_trials - 1)
    walk_update_group_additions = updates * int(walk["walk_update_group_additions"])
    online_group_additions = initial_mixed_group_additions + delta_setup_group_additions + walk_update_group_additions
    subset_group_additions = subset_count * max(0, width - 1)
    one_shot_group_additions = subset_group_additions + online_group_additions
    naive_independent_group_additions = attempted_trials * 2 * bit_length
    coverage = len(subset_table) / max(1, order)
    derived_ok = bool(derived["mixed_wide_relations_derive_secret"] and derived["derived_secret"] == secret)

    return {
        "accepted_mixed_relations": len(relations),
        "actual_subset_coverage": round(coverage, 6),
        "configured_trials": trials,
        "cost_model": {
            "cost_caveat": (
                "Online walk cost counts the initial mixed point, public walk-delta setup, and one "
                "group addition per subsequent trial. One-shot cost also counts subset precomputation."
            ),
            "delta_setup_group_additions": delta_setup_group_additions,
            "initial_mixed_group_additions": initial_mixed_group_additions,
            "naive_independent_group_additions": naive_independent_group_additions,
            "online_group_additions": online_group_additions,
            "online_group_additions_beats_rho": online_group_additions < rho,
            "one_shot_group_additions": one_shot_group_additions,
            "one_shot_group_additions_beats_rho": one_shot_group_additions < rho,
            "subset_group_additions": subset_group_additions,
            "walk_update_group_additions": walk_update_group_additions,
        },
        "decomposition_hits": hits,
        "derived": derived_ok,
        "elapsed_seconds": elapsed,
        "factor_base_size": len(factor_base),
        "generic_rho_steps": rho,
        "improvement_ratios": {
            "naive_independent_group_additions_over_rho": ratio(naive_independent_group_additions, rho),
            "online_group_additions_over_rho": ratio(online_group_additions, rho),
            "one_shot_group_additions_over_rho": ratio(one_shot_group_additions, rho),
            "relation_trials_over_rho": ratio(attempted_trials, rho),
            "subset_additions_over_rho": ratio(subset_group_additions, rho),
        },
        "max_relations": max_relations,
        "max_subsets": max_subsets,
        "mixed_wide_relation_rank": int_value(derived["mixed_wide_relation_rank"]),
        "observed_decomposition_rate": round(hits / attempted_trials, 6) if attempted_trials else 0.0,
        "relation_trials": attempted_trials,
        "seed": seed,
        "subset_count": subset_count,
        "subset_sum_collisions": subset_collisions,
        "subset_unique_sums": len(subset_table),
        "subset_width": width,
        "target": target,
        "trials_to_derive_secret": derived_at,
        "walk": {
            "delta_option_count": len(walk["delta_options"]),
            "initial_a": int(deterministic_start(order, seed, mode)[0]),
            "initial_b": int(deterministic_start(order, seed, mode)[1]),
            "mode": mode,
            "scheduled": bool(walk["scheduled"]),
            "step_a": None if walk["scheduled"] else int(walk["delta_options"][0]["da"]),
            "step_b": None if walk["scheduled"] else int(walk["delta_options"][0]["db"]),
        },
        "zero_b_hits": zero_b_hits,
        "zero_b_skips": zero_b_skips,
    }


def derived_sort_key(row: dict[str, Any]) -> tuple[float, float, int, int, str]:
    ratios = row.get("improvement_ratios") or {}
    online = ratios.get("online_group_additions_over_rho")
    one_shot = ratios.get("one_shot_group_additions_over_rho")
    return (
        float(online) if online is not None else 10**18,
        float(one_shot) if one_shot is not None else 10**18,
        int_value(row.get("relation_trials"), 10**9),
        int_value(row.get("factor_base_size"), 10**9),
        str(row.get("seed")),
    )


def determine_claim(best: dict[str, Any] | None) -> str:
    if not best:
        return "NEGATIVE_RESULT_P746_NO_DERIVED_INCREMENTAL_WALK"
    ratios = best.get("improvement_ratios") or {}
    online = ratios.get("online_group_additions_over_rho")
    one_shot = ratios.get("one_shot_group_additions_over_rho")
    if one_shot is not None and one_shot < 1.0:
        return "P746_INCREMENTAL_WALK_ONE_SHOT_BELOW_RHO_SIGNAL"
    if online is not None and online < 1.0:
        return "P746_INCREMENTAL_WALK_ONLINE_BELOW_RHO_SIGNAL_ONE_SHOT_ABOVE_RHO"
    return "P746_INCREMENTAL_WALK_DERIVES_GROUP_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    relprobe = load_relation_probe_module()
    verifier, record, inv = load_target(relprobe, args.target)
    baseline = p745_baseline(args.p745_summary)
    factor_base_sizes = parse_csv_ints(args.factor_base_sizes)
    widths = parse_csv_ints(args.widths)
    modes = parse_csv_strings(args.walk_modes)
    seeds = parse_csv_strings(args.seeds)
    rows: list[dict[str, Any]] = []
    for width in widths:
        for factor_base_size in factor_base_sizes:
            if factor_base_size < width:
                continue
            for mode in modes:
                for seed in seeds:
                    full_seed = f"{args.seed_prefix}:{seed}:fb{factor_base_size}:w{width}:{mode}"
                    rows.append(
                        scan_walk(
                            relprobe,
                            verifier,
                            record,
                            inv,
                            args.target,
                            factor_base_size,
                            width,
                            mode,
                            full_seed,
                            args.trials,
                            args.max_relations,
                            args.max_subsets,
                        )
                    )

    derived_rows = [row for row in rows if row.get("derived")]
    derived_rows.sort(key=derived_sort_key)
    best = derived_rows[0] if derived_rows else None
    online_wins = [
        row for row in derived_rows if (row.get("improvement_ratios") or {}).get("online_group_additions_over_rho", 10**18) < 1.0
    ]
    one_shot_wins = [
        row for row in derived_rows if (row.get("improvement_ratios") or {}).get("one_shot_group_additions_over_rho", 10**18) < 1.0
    ]
    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p745_summary": str(args.p745_summary),
            "script": str(Path(__file__)),
        },
        "baseline": {
            "p745_best": baseline,
            "pollard_rho_baseline_steps": math.ceil(math.sqrt(math.pi * int_value(inv.get("base_order")) / 2.0)),
        },
        "claim_status": determine_claim(best),
        "created_at": now_iso(),
        "grid_parameters": {
            "factor_base_sizes": factor_base_sizes,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "seed_prefix": args.seed_prefix,
            "seeds": seeds,
            "target": args.target,
            "trials": args.trials,
            "walk_modes": modes,
            "widths": widths,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: uses the existing relation_probe subset relation model and deterministic public walks.",
            "AMORTIZED-ONLINE BOUNDARY: online wins exclude reusable subset-table setup and are not one-shot ECDLP breaks.",
            "PRIMARY ONE-SHOT GATE: subset precomputation plus online walk cost must beat rho before claiming single-target speedup.",
            "NO DEPLOYED-CURVE CLAIM: no sparse-linear-algebra, target-descent, or large-prime scaling result is implied.",
        ],
        "method": "p746_incremental_public_mixed_row_walk_online_cost",
        "results": rows,
        "schema": SCHEMA,
        "summary": {
            "best_derived_by_online_group_cost": best,
            "configuration_count": len(rows),
            "derived_count": len(derived_rows),
            "derived_online_ratio_stats": stat(
                [
                    row["improvement_ratios"]["online_group_additions_over_rho"]
                    for row in derived_rows
                    if row["improvement_ratios"]["online_group_additions_over_rho"] is not None
                ]
            ),
            "derived_one_shot_ratio_stats": stat(
                [
                    row["improvement_ratios"]["one_shot_group_additions_over_rho"]
                    for row in derived_rows
                    if row["improvement_ratios"]["one_shot_group_additions_over_rho"] is not None
                ]
            ),
            "nonderived_count": len(rows) - len(derived_rows),
            "online_below_rho_count": len(online_wins),
            "one_shot_below_rho_count": len(one_shot_wins),
            "top_derived_by_online_group_cost": derived_rows[:12],
        },
    }
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
    parser.add_argument("--factor-base-sizes", default="24,28,32,36,40")
    parser.add_argument("--widths", default="2")
    parser.add_argument("--walk-modes", default="inc_a,inc_b,inc_ab,inc_a_neg_b,inc_2a_b,inc_a_2b,cycle6,hash6")
    parser.add_argument("--seeds", default="s00,s01,s02,s03,s04,s05,s06,s07,s08,s09,s10,s11")
    parser.add_argument("--seed-prefix", default="ecdlp-p746-incremental-walk-v1")
    parser.add_argument("--trials", type=int, default=160)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--p745-summary", type=Path, default=DEFAULT_P745)
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
    best = summary["summary"]["best_derived_by_online_group_cost"] or {}
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_derived_by_online_group_cost": {
                    key: best.get(key)
                    for key in [
                        "target",
                        "factor_base_size",
                        "subset_width",
                        "seed",
                        "walk",
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
                "online_below_rho_count": summary["summary"]["online_below_rho_count"],
                "one_shot_below_rho_count": summary["summary"]["one_shot_below_rho_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
