#!/usr/bin/env python3
"""Scalar-free relation-harvesting probes for the ECDLP research task.

This is a host-side measurement helper, not a solver shortcut. It tests the
Grobner-free/Semaev direction as a combinatorial relation search: build a
low-weight subset table over the verifier factor base, sample mixed rows
``a*P + b*Q``, and record how often those rows decompose without using the
challenge scalar or factor-base discrete logs.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
from itertools import combinations
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
ENV_MAIN = TASK_DIR / "environment" / "main.py"
DEFAULT_TARGETS = (
    "22050.cf1@5641",
    "23232.cr1@9643",
    "21175.bc1@8089",
    "67.a1@11923",
    "114224.v1@9341",
)


def load_verifier_module():
    spec = importlib.util.spec_from_file_location("ecdlp_verifier_main", ENV_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import verifier helpers from {ENV_MAIN}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_target(raw: str) -> tuple[str, int]:
    label, sep, prime = raw.partition("@")
    if not sep or not label:
        raise argparse.ArgumentTypeError(f"target must be label@prime: {raw!r}")
    return label, int(prime)


def deterministic_secret(label: str, p: int, order: int, seed: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}:{p}:{order}".encode()).digest()
    return 1 + (int.from_bytes(digest, "big") % (order - 1))


def make_challenge(
    verifier: Any,
    inv: dict[str, Any],
    ainvs: list[int],
    seed: str,
    factor_base_limit: int | None = None,
) -> tuple[dict[str, Any], int]:
    order = int(inv["base_order"])
    secret = deterministic_secret(inv["label"], int(inv["p"]), order, seed)
    public = verifier.mul_point(secret, inv["base"], ainvs, int(inv["p"]))
    factor_seed = f"{inv['label']}:{inv['p']}:{order}"
    factor_limit = int(factor_base_limit) if factor_base_limit is not None else 48
    if factor_limit <= 0:
        raise ValueError(f"factor_base_limit must be positive, got {factor_limit}")
    factor_base = verifier.build_factor_base(ainvs, int(inv["p"]), order, limit=factor_limit, seed=factor_seed)
    challenge = {
        "label": inv["label"],
        "isogeny_class": inv["isogeny_class"],
        "p": int(inv["p"]),
        "ainvs": ainvs,
        "group_order": int(inv["order"]),
        "base": verifier.point_to_json(inv["base"]),
        "base_order": order,
        "public": verifier.point_to_json(public),
        "factor_base": [verifier.point_to_json(point) for point in factor_base],
        "generic_rho_steps": math.ceil(math.sqrt(math.pi * order / 2.0)),
        "precomputed_target": bool(inv.get("precomputed_target")),
        "research_targets": [
            "ecdlp",
            "semaev_summation_polynomials",
            "grobner_free_relation_harvesting",
            "first_fall_degree_probe",
            "finite_field_embedding_probe",
        ],
    }
    return challenge, secret


def subset_sum(point_indices: tuple[int, ...], points: list[Any], verifier: Any, ainvs: list[int], p: int) -> Any:
    acc = verifier.POINT_AT_INFINITY
    for index in point_indices:
        acc = verifier.add_points(acc, points[index], ainvs, p)
    return acc


def build_subset_table(
    verifier: Any,
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    width: int,
    max_subsets: int,
) -> tuple[dict[Any, tuple[int, ...]], int, int]:
    table: dict[Any, tuple[int, ...]] = {}
    collisions = 0
    total = 0
    for combo in combinations(range(len(factor_base)), width):
        if total >= max_subsets:
            break
        point = subset_sum(combo, factor_base, verifier, ainvs, p)
        if point in table:
            collisions += 1
        else:
            table[point] = combo
        total += 1
    return table, total, collisions


def linear_rank_probe(verifier: Any, forms: list[tuple[Any, int, list[int]]], order: int) -> dict[str, Any]:
    secret, proves, rank = verifier.derive_secret_from_relations(forms, order)
    return {
        "mixed_wide_relation_rank": rank,
        "derived_secret": None if secret is None else int(secret),
        "mixed_wide_relations_derive_secret": bool(proves),
    }


def probe_target(
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    challenge, secret = make_challenge(verifier, inv, ainvs, args.seed, args.factor_base_size)
    base = verifier.point_from_json(challenge["base"])
    public = verifier.point_from_json(challenge["public"])
    full_factor_base = [verifier.point_from_json(point) for point in challenge["factor_base"]]
    factor_base = full_factor_base[: max(1, min(args.factor_base_size, len(full_factor_base)))]

    subset_table, subset_count, subset_collisions = build_subset_table(
        verifier,
        factor_base,
        ainvs,
        p,
        args.width,
        args.max_subsets,
    )

    rng = random.Random(f"{args.seed}:{inv['label']}:{p}:{args.width}")
    relations: list[dict[str, Any]] = []
    forms: list[tuple[Any, int, list[int]]] = []
    seen_forms: set[tuple[Any, int]] = set()
    hits = 0
    attempted_trials = 0
    first_hit_at = None
    derived_at = None
    derived = {"mixed_wide_relations_derive_secret": False, "mixed_wide_relation_rank": 0, "derived_secret": None}

    for trial in range(1, args.trials + 1):
        attempted_trials = trial
        a = rng.randrange(order)
        b = 1 + rng.randrange(order - 1)
        lhs = verifier.add_points(
            verifier.mul_point(a, base, ainvs, p),
            verifier.mul_point(b, public, ainvs, p),
            ainvs,
            p,
        )
        indices = subset_table.get(lhs)
        if indices is None:
            continue

        hits += 1
        first_hit_at = first_hit_at or trial
        relation = {"a": int(a), "b": int(b), "indices": [int(index) for index in indices]}
        terms = verifier.relation_terms(relation, challenge, ainvs, p)
        if terms is None or not verifier.verify_relation(relation, challenge, ainvs, p, base, public):
            continue
        coeffs, rhs = verifier.relation_linear_form(relation, terms, challenge, order)
        key = (coeffs, rhs)
        if key in seen_forms:
            continue
        seen_forms.add(key)
        relations.append(relation)
        forms.append((coeffs, rhs, terms))
        if len(relations) >= args.max_relations:
            derived = linear_rank_probe(verifier, forms, order)
            if derived["mixed_wide_relations_derive_secret"]:
                derived_at = trial
            break
        if len(relations) >= 8:
            current = linear_rank_probe(verifier, forms, order)
            if current["mixed_wide_relations_derive_secret"]:
                derived = current
                derived_at = trial
                if args.stop_on_derive:
                    break

    if not derived["mixed_wide_relations_derive_secret"]:
        derived = linear_rank_probe(verifier, forms, order)

    rho_steps = int(challenge["generic_rho_steps"])
    online_scalar_mults = 2 * attempted_trials
    estimated_online_group_additions = online_scalar_mults * max(1, order.bit_length())
    subset_group_additions = subset_count * max(0, args.width - 1)
    single_challenge_group_additions = estimated_online_group_additions + subset_group_additions
    observed_rate = hits / attempted_trials if attempted_trials else 0.0
    expected_coverage = 1.0 - math.exp(-subset_count / max(1, order))

    return {
        "target": f"{inv['label']}@{p}",
        "order": order,
        "order_bit_length": order.bit_length(),
        "generic_rho_steps": rho_steps,
        "embedding_degree": inv.get("embedding_degree"),
        "factor_base_size": len(factor_base),
        "full_factor_base_size": len(full_factor_base),
        "subset_width": args.width,
        "subset_count": subset_count,
        "subset_unique_sums": len(subset_table),
        "subset_sum_collisions": subset_collisions,
        "expected_random_coverage": round(expected_coverage, 6),
        "actual_subset_coverage": round(len(subset_table) / max(1, order), 6),
        "configured_relation_trials": args.trials,
        "relation_trials": attempted_trials,
        "decomposition_hits": hits,
        "observed_decomposition_rate": round(observed_rate, 6),
        "first_hit_at_trial": first_hit_at,
        "accepted_mixed_relations": len(relations),
        "trials_to_derive_secret": derived_at,
        "mixed_wide_relation_rank": derived["mixed_wide_relation_rank"],
        "mixed_wide_relations_derive_secret": bool(
            derived["mixed_wide_relations_derive_secret"]
            and derived["derived_secret"] == secret
        ),
        "cost_model": {
            "one_time_subset_group_additions": subset_group_additions,
            "online_scalar_mults": online_scalar_mults,
            "estimated_online_group_additions": estimated_online_group_additions,
            "single_challenge_group_additions": single_challenge_group_additions,
            "online_trials_beats_rho": attempted_trials < rho_steps,
            "single_challenge_beats_rho": single_challenge_group_additions < rho_steps,
            "cost_caveat": (
                "The subset table is independent of Q and can be amortized across challenges, "
                "but it must be counted for a one-shot ECDLP claim."
            ),
        },
        "ffe_first_fall_proxy": {
            "field": f"GF({p})",
            "extension_degree": 1,
            "semaev_arity": args.width + 1,
            "first_fall_degree_hypothesis": (
                "Record relation-rate and rank behavior before assuming a low first fall degree "
                "or finite-field embedding advantage."
            ),
        },
        "relations_sample": relations[: min(5, len(relations))],
    }


def load_target_invariants(verifier: Any, records: list[dict[str, Any]], targets: list[tuple[str, int]]):
    by_label = {record["label"]: record for record in records}
    for label, p in targets:
        record = by_label.get(label)
        if record is None:
            continue
        try:
            inv = verifier.reduction_invariants(record, p)
        except Exception as exc:  # noqa: BLE001 - report target-level failures.
            yield {
                "target": f"{label}@{p}",
                "error": f"{type(exc).__name__}: {exc}",
            }
            continue
        yield record, inv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="append", type=parse_target, help="target as label@prime")
    parser.add_argument("--width", type=int, default=3, help="factor-base subset width")
    parser.add_argument("--factor-base-size", type=int, default=48, help="prefix of verifier factor base to use")
    parser.add_argument("--trials", type=int, default=192, help="mixed aP+bQ samples per target")
    parser.add_argument("--max-relations", type=int, default=96, help="accepted relations to keep")
    parser.add_argument("--max-subsets", type=int, default=25000, help="cap subset precomputation")
    parser.add_argument("--seed", default="ecdlp-relation-probe-v1")
    parser.add_argument("--stop-on-derive", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("ecdlp_index_calculus_state/manual_relation_scan.json"))
    args = parser.parse_args()

    if args.width < 2:
        parser.error("--width must be at least 2")

    verifier = load_verifier_module()
    records = verifier.load_records()
    targets = args.target or [parse_target(raw) for raw in DEFAULT_TARGETS]

    results: list[dict[str, Any]] = []
    for item in load_target_invariants(verifier, records, targets):
        if isinstance(item, dict):
            results.append(item)
            continue
        record, inv = item
        results.append(probe_target(verifier, record, inv, args))

    output = {
        "schema": "ecdlp_relation_harvesting_probe_v1",
        "method": "scalar_free_low_weight_subset_sum_relation_harvesting",
        "summary": {
            "targets": len(results),
            "derived_targets": sum(1 for row in results if row.get("mixed_wide_relations_derive_secret")),
            "honest_single_challenge_wins": sum(
                1 for row in results if row.get("cost_model", {}).get("single_challenge_beats_rho")
            ),
            "interpretation": (
                "A derived scalar-free relation system is verifier-relevant. It is not a rho-beating "
                "ECDLP claim unless the one-shot cost model also beats generic_rho_steps."
            ),
        },
        "parameters": {
            "targets": [f"{label}@{p}" for label, p in targets],
            "width": args.width,
            "factor_base_size": args.factor_base_size,
            "trials": args.trials,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "seed": args.seed,
        },
        "results": results,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print(json.dumps(output["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
