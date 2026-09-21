#!/usr/bin/env python3
"""P748 setup-amortization and modular matrix bridge for P747 policy.

This probe freezes the P747 public-selected policy (fb48, width2, hash6),
scans a larger challenge batch, exports verifier-backed modular relation forms,
and measures whether the online relation signal becomes a reusable
index-calculus component under honest batch accounting.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import time
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p748_setup_amortization_matrix_bridge.md"
DEFAULT_P747_SUMMARY = STATE_DIR / "low_term_total2_p747_scheduled_walk_public_selector_summary.json"
SCHEMA = "ecdlp.low_term_total2_p748_setup_amortization_matrix_bridge.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_p746_module() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p746_incremental_walk", P746_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P746 helper from {P746_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_csv_strings(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


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


def rank_mod(matrix: list[list[int]], modulus: int) -> int:
    rows = [[value % modulus for value in row] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return 0
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % modulus, -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = rows[row][col] % modulus
            if factor:
                rows[row] = [
                    (rows[row][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def rref_augmented(rows: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int], bool]:
    if not rows:
        return [], [], True
    reduced = [[value % modulus for value in row] for row in rows]
    nvars = len(reduced[0]) - 1
    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(nvars):
        pivot = None
        for row in range(pivot_row, len(reduced)):
            if reduced[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        inv = pow(reduced[pivot_row][col] % modulus, -1, modulus)
        reduced[pivot_row] = [(value * inv) % modulus for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row == pivot_row:
                continue
            factor = reduced[row][col] % modulus
            if factor:
                reduced[row] = [
                    (reduced[row][idx] - factor * reduced[pivot_row][idx]) % modulus
                    for idx in range(nvars + 1)
                ]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    consistent = True
    for row in reduced:
        if all(row[col] % modulus == 0 for col in range(nvars)) and row[-1] % modulus:
            consistent = False
            break
    return reduced, pivot_cols, consistent


def solved_variables(reduced: list[list[int]], pivot_cols: list[int], nvars: int, modulus: int) -> dict[int, int]:
    free_cols = set(range(nvars)) - set(pivot_cols)
    solved: dict[int, int] = {}
    for row_index, col in enumerate(pivot_cols):
        if all(reduced[row_index][free_col] % modulus == 0 for free_col in free_cols):
            solved[col] = reduced[row_index][-1] % modulus
    return solved


def public_rank_probe(relprobe: Any, verifier: Any, forms: list[tuple[Any, int, list[int]]], order: int) -> dict[str, Any]:
    if not forms:
        return {"mixed_wide_relation_rank": 0, "mixed_wide_relations_derive_secret": False, "derived_secret": None}
    return relprobe.linear_rank_probe(verifier, forms, order)


def group_cost(bit_length: int, delta_setup: int, trials: int) -> int:
    return (2 * bit_length) + 1 + delta_setup + max(0, trials - 1)


def seed_labels(count: int) -> list[str]:
    return [f"t{index:02d}" for index in range(count)]


def scan_export_walk(
    p746: Any,
    relprobe: Any,
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    target: str,
    factor_base_size: int,
    width: int,
    mode: str,
    seed_label: str,
    full_seed: str,
    trials: int,
    early_budget: int,
    max_relations: int,
    max_subsets: int,
) -> dict[str, Any]:
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, factor_base_size)
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
    walk = p746.walk_schedule(verifier, mode, base, public, ainvs, p)
    initial_a, initial_b = p746.deterministic_start(order, full_seed, mode)
    a, b = initial_a, initial_b
    lhs = verifier.add_points(
        verifier.mul_point(a, base, ainvs, p),
        verifier.mul_point(b, public, ainvs, p),
        ainvs,
        p,
    )

    forms: list[tuple[Any, int, list[int]]] = []
    exported_forms: list[dict[str, Any]] = []
    seen_forms: set[tuple[Any, int]] = set()
    hits = 0
    zero_b_hits = 0
    zero_b_skips = 0
    derived_at = None
    derived = {"mixed_wide_relations_derive_secret": False, "mixed_wide_relation_rank": 0, "derived_secret": None}
    early_snapshot: dict[str, Any] | None = None
    attempted_trials = 0
    started = time.monotonic()

    for trial in range(1, trials + 1):
        attempted_trials = trial
        indices = subset_table.get(lhs)
        if indices is not None:
            hits += 1
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
                        forms.append((coeffs, rhs, terms))
                        exported_forms.append(
                            {
                                "a": int(a),
                                "b": int(b),
                                "coeffs": [int(value) for value in coeffs],
                                "form_index": len(exported_forms),
                                "rhs": int(rhs),
                                "terms": [int(term) for term in terms],
                                "trial": trial,
                            }
                        )
                        if len(forms) >= 8:
                            current = relprobe.linear_rank_probe(verifier, forms, order)
                            if current["mixed_wide_relations_derive_secret"] and derived_at is None:
                                derived = current
                                derived_at = trial
                        if len(forms) >= max_relations:
                            break

        if trial == early_budget:
            early_rank = public_rank_probe(relprobe, verifier, forms, order)
            early_snapshot = {
                "accepted_mixed_relations": len(forms),
                "decomposition_hits": hits,
                "mixed_wide_relation_rank": int(early_rank["mixed_wide_relation_rank"]),
                "observed_decomposition_rate": round(hits / trial, 6),
                "scanned_trials": trial,
                "zero_b_skips": zero_b_skips,
            }

        if trial == trials or len(forms) >= max_relations:
            break
        delta = p746.select_delta(walk, full_seed, trial, a, b)
        a = (a + int(delta["da"])) % order
        b = (b + int(delta["db"])) % order
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    if early_snapshot is None:
        early_rank = public_rank_probe(relprobe, verifier, forms, order)
        divisor = max(1, attempted_trials)
        early_snapshot = {
            "accepted_mixed_relations": len(forms),
            "decomposition_hits": hits,
            "mixed_wide_relation_rank": int(early_rank["mixed_wide_relation_rank"]),
            "observed_decomposition_rate": round(hits / divisor, 6),
            "scanned_trials": attempted_trials,
            "zero_b_skips": zero_b_skips,
        }

    final_derived = public_rank_probe(relprobe, verifier, forms, order)
    if final_derived["mixed_wide_relations_derive_secret"] and derived_at is None:
        derived = final_derived
        derived_at = attempted_trials
    elif final_derived["mixed_wide_relations_derive_secret"]:
        derived = final_derived

    elapsed = round(time.monotonic() - started, 6)
    rho = int(challenge["generic_rho_steps"])
    bit_length = max(1, order.bit_length())
    delta_setup_group_additions = int(walk["delta_setup_group_additions"])
    collection_online_group_additions = group_cost(bit_length, delta_setup_group_additions, attempted_trials)
    solve_trials = int(derived_at) if derived_at is not None else attempted_trials
    solve_attempt_online_group_additions = group_cost(bit_length, delta_setup_group_additions, solve_trials)
    first_derive_online_group_additions = solve_attempt_online_group_additions if derived_at is not None else None
    subset_group_additions = subset_count * max(0, width - 1)
    derived_ok = bool(final_derived["mixed_wide_relations_derive_secret"] and final_derived["derived_secret"] == secret)

    return {
        "_expected_secret": int(secret),
        "accepted_mixed_relations": len(forms),
        "actual_subset_coverage": round(len(subset_table) / max(1, order), 6),
        "configured_trials": trials,
        "cost_model": {
            "collection_online_group_additions": collection_online_group_additions,
            "collection_one_shot_group_additions": subset_group_additions + collection_online_group_additions,
            "delta_setup_group_additions": delta_setup_group_additions,
            "first_derive_online_group_additions": first_derive_online_group_additions,
            "first_derive_online_group_additions_beats_rho": (
                first_derive_online_group_additions is not None and first_derive_online_group_additions < rho
            ),
            "initial_mixed_group_additions": (2 * bit_length) + 1,
            "solve_attempt_online_group_additions": solve_attempt_online_group_additions,
            "solve_attempt_one_shot_group_additions": subset_group_additions + solve_attempt_online_group_additions,
            "subset_group_additions": subset_group_additions,
        },
        "decomposition_hits": hits,
        "derived": derived_ok,
        "elapsed_seconds": elapsed,
        "early_public": early_snapshot,
        "factor_base_size": len(factor_base),
        "forms": exported_forms,
        "generic_rho_steps": rho,
        "improvement_ratios": {
            "collection_online_group_additions_over_rho": ratio(collection_online_group_additions, rho),
            "collection_one_shot_group_additions_over_rho": ratio(subset_group_additions + collection_online_group_additions, rho),
            "first_derive_online_group_additions_over_rho": ratio(first_derive_online_group_additions, rho),
            "solve_attempt_online_group_additions_over_rho": ratio(solve_attempt_online_group_additions, rho),
            "solve_attempt_one_shot_group_additions_over_rho": ratio(
                subset_group_additions + solve_attempt_online_group_additions,
                rho,
            ),
            "subset_additions_over_rho": ratio(subset_group_additions, rho),
        },
        "matrix_challenge_id": f"{target}:{seed_label}",
        "mixed_wide_relation_rank": int(final_derived["mixed_wide_relation_rank"]),
        "observed_decomposition_rate": round(hits / max(1, attempted_trials), 6),
        "policy_key": {
            "factor_base_size": len(factor_base),
            "subset_width": width,
            "walk_mode": mode,
        },
        "relation_trials": solve_trials,
        "scanned_trials": attempted_trials,
        "seed": full_seed,
        "seed_label": seed_label,
        "subset_count": subset_count,
        "subset_sum_collisions": subset_collisions,
        "subset_unique_sums": len(subset_table),
        "subset_width": width,
        "target": target,
        "trials_to_derive_secret": derived_at,
        "walk": {
            "delta_option_count": len(walk["delta_options"]),
            "initial_a": int(initial_a),
            "initial_b": int(initial_b),
            "mode": mode,
            "scheduled": bool(walk["scheduled"]),
        },
        "zero_b_hits": zero_b_hits,
        "zero_b_skips": zero_b_skips,
    }


def form_rows_by_challenge(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        challenge_id = row["matrix_challenge_id"]
        for form in row.get("forms") or []:
            grouped[challenge_id].append(form)
    return grouped


def factor_eliminated_relations(rows: list[dict[str, Any]], order: int, factor_count: int) -> list[dict[str, Any]]:
    relations: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for challenge_id, forms in form_rows_by_challenge(rows).items():
        for form in forms:
            coeffs = [int(value) % order for value in form["coeffs"]]
            if coeffs[0] % order == 0:
                factor_coeffs = tuple(coeffs[1 : 1 + factor_count])
                rhs = int(form["rhs"]) % order
                if any(factor_coeffs):
                    relations.setdefault(
                        (factor_coeffs, rhs),
                        {"challenge_id": challenge_id, "coeffs": list(factor_coeffs), "rhs": rhs, "source": "zero_secret_coeff"},
                    )
        for left, right in combinations(forms, 2):
            left_coeffs = [int(value) % order for value in left["coeffs"]]
            right_coeffs = [int(value) % order for value in right["coeffs"]]
            left_b = left_coeffs[0]
            right_b = right_coeffs[0]
            factor_coeffs = tuple(
                (right_b * left_coeffs[1 + index] - left_b * right_coeffs[1 + index]) % order
                for index in range(factor_count)
            )
            rhs = (right_b * int(left["rhs"]) - left_b * int(right["rhs"])) % order
            if any(factor_coeffs):
                relations.setdefault(
                    (factor_coeffs, rhs),
                    {
                        "challenge_id": challenge_id,
                        "coeffs": list(factor_coeffs),
                        "rhs": rhs,
                        "source": "pairwise_secret_elimination",
                    },
                )
    return list(relations.values())


def matrix_summary(rows: list[dict[str, Any]], order: int) -> dict[str, Any]:
    challenge_ids = sorted({row["matrix_challenge_id"] for row in rows})
    challenge_index = {challenge_id: index for index, challenge_id in enumerate(challenge_ids)}
    expected = {row["matrix_challenge_id"]: int(row["_expected_secret"]) for row in rows}
    factor_count = max((len(form["coeffs"]) - 1 for row in rows for form in row.get("forms") or []), default=0)
    nvars = len(challenge_ids) + factor_count
    augmented_rows: list[list[int]] = []
    form_count = 0
    for row in rows:
        challenge_col = challenge_index[row["matrix_challenge_id"]]
        for form in row.get("forms") or []:
            coeffs = [int(value) % order for value in form["coeffs"]]
            matrix_row = [0] * nvars
            matrix_row[challenge_col] = coeffs[0]
            for factor_index in range(factor_count):
                matrix_row[len(challenge_ids) + factor_index] = coeffs[1 + factor_index]
            augmented_rows.append(matrix_row + [int(form["rhs"]) % order])
            form_count += 1

    reduced, pivots, consistent = rref_augmented(augmented_rows, order)
    solved = solved_variables(reduced, pivots, nvars, order) if consistent else {}
    solved_secret_reports = []
    for challenge_id, col in challenge_index.items():
        if col in solved:
            solved_secret_reports.append(
                {
                    "challenge_id": challenge_id,
                    "matches_expected": solved[col] == expected[challenge_id],
                    "seed_label": challenge_id.rsplit(":", 1)[-1],
                    "target": challenge_id.rsplit(":", 1)[0],
                }
            )

    factor_relations = factor_eliminated_relations(rows, order, factor_count)
    factor_matrix = [relation["coeffs"] for relation in factor_relations]
    factor_augmented = [relation["coeffs"] + [relation["rhs"]] for relation in factor_relations]
    factor_rank = rank_mod(factor_matrix, order)
    factor_augmented_rank = rank_mod(factor_augmented, order)
    raw_coefficient_rank = rank_mod([row[:-1] for row in augmented_rows], order)
    raw_augmented_rank = rank_mod(augmented_rows, order)
    dense_proxy = nvars**3 if nvars else 0
    sparse_proxy = form_count * raw_coefficient_rank
    return {
        "challenge_count": len(challenge_ids),
        "consistent": consistent,
        "factor_augmented_rank": factor_augmented_rank,
        "factor_count": factor_count,
        "factor_relation_count": len(factor_relations),
        "factor_relation_rank": factor_rank,
        "factor_relation_sample": factor_relations[:12],
        "factor_relations_consistent": factor_augmented_rank == factor_rank,
        "form_count": form_count,
        "linear_algebra_proxy": {
            "boundary": "FIELD-OP PROXY ONLY: not charged as group additions against rho in P748 cost ratios.",
            "dense_nvars_cubed": dense_proxy,
            "sparse_forms_times_rank": sparse_proxy,
        },
        "raw_augmented_rank": raw_augmented_rank,
        "raw_coefficient_rank": raw_coefficient_rank,
        "secret_match_count": sum(1 for report in solved_secret_reports if report["matches_expected"]),
        "secret_solved_count": len(solved_secret_reports),
        "secret_solved_sample": solved_secret_reports[:12],
        "variable_count": nvars,
    }


def cost_summary(rows: list[dict[str, Any]], matrix: dict[str, Any], order: int) -> dict[str, Any]:
    if not rows:
        return {}
    rho = int(rows[0]["generic_rho_steps"])
    setup = int(rows[0]["cost_model"]["subset_group_additions"])
    attempted = len(rows)
    derived_rows = [row for row in rows if row.get("derived")]
    online_wins = [
        row for row in derived_rows if row["cost_model"]["first_derive_online_group_additions_beats_rho"]
    ]
    collection_online_total = sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    solve_attempt_online_total = sum(int(row["cost_model"]["solve_attempt_online_group_additions"]) for row in rows)
    success_only_online_total = sum(
        int(row["cost_model"]["first_derive_online_group_additions"])
        for row in derived_rows
        if row["cost_model"]["first_derive_online_group_additions"] is not None
    )
    honest_batch_solve_total = setup + solve_attempt_online_total
    honest_batch_collection_total = setup + collection_online_total
    success_only_lower_bound_total = setup + success_only_online_total
    individual_baseline = len(derived_rows) * rho
    matrix_baseline = int(matrix.get("secret_match_count") or 0) * rho
    return {
        "attempted_challenges": attempted,
        "break_even_solved_secret_count_honest_solve_attempt": math.ceil(honest_batch_solve_total / rho),
        "collection_online_total": collection_online_total,
        "derived_challenges": len(derived_rows),
        "honest_batch_collection_total": honest_batch_collection_total,
        "honest_batch_collection_total_over_individual_derived_rho": ratio(honest_batch_collection_total, individual_baseline),
        "honest_batch_solve_attempt_total": honest_batch_solve_total,
        "honest_batch_solve_attempt_total_over_individual_derived_rho": ratio(honest_batch_solve_total, individual_baseline),
        "honest_batch_solve_attempt_total_over_matrix_solved_rho": ratio(honest_batch_solve_total, matrix_baseline),
        "individual_derived_rho_baseline": individual_baseline,
        "matrix_solved_rho_baseline": matrix_baseline,
        "online_below_rho_individual_count": len(online_wins),
        "rho": rho,
        "setup_group_additions": setup,
        "solve_attempt_online_total": solve_attempt_online_total,
        "success_only_lower_bound_total": success_only_lower_bound_total,
        "success_only_lower_bound_total_over_individual_derived_rho": ratio(
            success_only_lower_bound_total,
            individual_baseline,
        ),
        "linear_algebra_cost_charged": False,
        "success_rate": round(len(derived_rows) / attempted, 8) if attempted else None,
    }


def summarize_target(target: str, rows: list[dict[str, Any]], order: int) -> dict[str, Any]:
    matrix = matrix_summary(rows, order)
    costs = cost_summary(rows, matrix, order)
    derived_rows = [row for row in rows if row.get("derived")]
    derived_rows.sort(
        key=lambda row: (
            row["improvement_ratios"]["first_derive_online_group_additions_over_rho"]
            if row["improvement_ratios"]["first_derive_online_group_additions_over_rho"] is not None
            else 10**18,
            row["seed_label"],
        )
    )
    return {
        "best_individual_derived": strip_private(derived_rows[0]) if derived_rows else None,
        "cost_summary": costs,
        "matrix_summary": matrix,
        "relation_stats": {
            "accepted_forms": sum(len(row.get("forms") or []) for row in rows),
            "accepted_forms_per_challenge": stat([len(row.get("forms") or []) for row in rows]),
            "decomposition_hits_per_challenge": stat([int(row.get("decomposition_hits") or 0) for row in rows]),
            "individual_rank_per_challenge": stat([int(row.get("mixed_wide_relation_rank") or 0) for row in rows]),
        },
        "target": target,
        "top_individual_derived": [strip_private(row) for row in derived_rows[:8]],
    }


def strip_private(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_private(inner) for key, inner in value.items() if not str(key).startswith("_")}
    if isinstance(value, list):
        return [strip_private(item) for item in value]
    return value


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    any_honest = any(
        (summary["cost_summary"].get("honest_batch_solve_attempt_total_over_individual_derived_rho") or 10**18) < 1.0
        for summary in target_summaries
    )
    if any_honest:
        return "P748_HONEST_BATCH_BELOW_RHO_SIGNAL"
    any_rank = any(int(summary["matrix_summary"].get("factor_relation_rank") or 0) > 0 for summary in target_summaries)
    any_online = any(int(summary["cost_summary"].get("online_below_rho_individual_count") or 0) > 0 for summary in target_summaries)
    any_matrix_extra = any(
        int(summary["matrix_summary"].get("secret_match_count") or 0) > int(summary["cost_summary"].get("derived_challenges") or 0)
        for summary in target_summaries
    )
    if any_rank and any_matrix_extra:
        return "P748_MATRIX_RANK_SOLVES_EXTRA_SECRETS_BATCH_COST_NEGATIVE"
    if any_rank and any_online:
        return "P748_FACTOR_RANK_POSITIVE_BATCH_COST_NEGATIVE"
    if any_online:
        return "P748_INDIVIDUAL_ONLINE_SIGNAL_BATCH_MATRIX_NEGATIVE"
    return "NEGATIVE_RESULT_P748_SELECTED_POLICY_BATCH_NO_USEFUL_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p747_summary = load_json(args.p747_summary)
    selected = ((p747_summary.get("summary") or {}).get("selected_policy") or {})
    factor_base_size = int(selected.get("factor_base_size") or args.factor_base_size)
    width = int(selected.get("subset_width") or args.width)
    mode = str(selected.get("walk_mode") or args.walk_mode)
    targets = parse_csv_strings(args.targets)
    labels = seed_labels(args.seed_count)
    p746 = load_p746_module()
    relprobe = p746.load_relation_probe_module()

    target_rows: dict[str, list[dict[str, Any]]] = {}
    target_summaries: list[dict[str, Any]] = []
    for target in targets:
        verifier, record, inv = p746.load_target(relprobe, target)
        rows: list[dict[str, Any]] = []
        for seed_label in labels:
            full_seed = f"{args.seed_prefix}:{seed_label}:fb{factor_base_size}:w{width}:{mode}"
            rows.append(
                scan_export_walk(
                    p746,
                    relprobe,
                    verifier,
                    record,
                    inv,
                    target,
                    factor_base_size,
                    width,
                    mode,
                    seed_label,
                    full_seed,
                    args.trials,
                    args.early_budget,
                    args.max_relations,
                    args.max_subsets,
                )
            )
        target_rows[target] = rows
        target_summaries.append(summarize_target(target, rows, int(inv["base_order"])))

    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p747_summary": str(args.p747_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: P747 selected scheduled-walk subset relation model.",
            "BATCH-COST DISCIPLINE: honest cost includes failed selected-policy attempts.",
            "SUCCESS-ONLY LOWER BOUND: success-only curves are diagnostic and cannot be promoted as speedups.",
            "TARGET_DESCENT_OPEN: factor rank is an index-calculus component signal, not a complete target-descent algorithm.",
        ],
        "method": "p748_setup_amortization_matrix_bridge",
        "parameters": {
            "early_budget": args.early_budget,
            "factor_base_size": factor_base_size,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "seed_count": args.seed_count,
            "seed_labels": labels,
            "seed_prefix": args.seed_prefix,
            "selected_policy_source": str(args.p747_summary),
            "targets": targets,
            "trials": args.trials,
            "walk_mode": mode,
            "width": width,
        },
        "results": {target: [strip_private(row) for row in rows] for target, rows in target_rows.items()},
        "schema": SCHEMA,
        "summary": {
            "selected_policy": {"factor_base_size": factor_base_size, "subset_width": width, "walk_mode": mode},
            "target_summaries": target_summaries,
        },
    }
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", default="67.a1@11789,22050.cf1@11731")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--seed-count", type=int, default=256)
    parser.add_argument("--seed-prefix", default="ecdlp-p746-scheduled-seed-extension-v1")
    parser.add_argument("--trials", type=int, default=128)
    parser.add_argument("--early-budget", type=int, default=24)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--p747-summary", type=Path, default=DEFAULT_P747_SUMMARY)
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
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "selected_policy": summary["summary"]["selected_policy"],
                "targets": [
                    {
                        "target": item["target"],
                        "cost": item["cost_summary"],
                        "matrix": {
                            key: item["matrix_summary"].get(key)
                            for key in [
                                "form_count",
                                "factor_relation_count",
                                "factor_relation_rank",
                                "secret_match_count",
                                "secret_solved_count",
                            ]
                        },
                    }
                    for item in summary["summary"]["target_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
