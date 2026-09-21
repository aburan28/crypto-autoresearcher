#!/usr/bin/env python3
"""P1050 nonlinear two-feature transform audit after P1049."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1045_p231_yresidue_representation_change_rank_scout as p1045
import low_term_total2_p1047_p231_fresh_row_representation_validation as p1047
import low_term_total2_p1048_p231_coefficient_transform_representation_audit as p1048
import low_term_total2_p1049_p231_constant_free_random_feature_null_audit as p1049


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1050_p231_nonlinear_two_feature_transform_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit_probe.json"
DEFAULT_P1049_INPUT = STATE_DIR / "low_term_total2_p1049_p231_constant_free_random_feature_null_audit_probe.json"
DEFAULT_INPUTS = p1045.DEFAULT_INPUTS
SCHEMA = "ecdlp.low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit.v1"
ORDER = p1045.ORDER
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 64
DEFAULT_TRIALS = 64

PairFn = Callable[[dict[str, Any]], tuple[int, int]]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def serializable_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def pair_specs() -> list[dict[str, Any]]:
    return [
        {"name": "x_y", "fn": lambda form: (p1048.feature_x(form), p1048.feature_y(form))},
        {"name": "x_y_over_x", "fn": lambda form: (p1048.feature_x(form), p1048.feature_y_over_x(form))},
        {"name": "x_y_over_x_plus_1", "fn": lambda form: (p1048.feature_x(form), p1048.feature_y_over_x_plus_1(form))},
        {"name": "x_kummer", "fn": lambda form: (p1048.feature_x(form), p1048.feature_kummer_x_plus_inv(form))},
        {"name": "y_kummer", "fn": lambda form: (p1048.feature_y(form), p1048.feature_kummer_x_plus_inv(form))},
        {"name": "trace_norm", "fn": lambda form: (p1048.feature_trace_sum(form), p1048.feature_norm_product(form))},
        {"name": "disc_kummer", "fn": lambda form: (p1048.feature_discriminant(form), p1048.feature_kummer_x_plus_inv(form))},
        {"name": "rational_disc", "fn": lambda form: (p1048.feature_y_over_x_plus_1(form), p1048.feature_discriminant(form))},
        {"name": "xmod11_ymod5", "fn": lambda form: (p1048.feature_x_mod_11(form), p1048.feature_y_mod_5(form))},
    ]


def channel_values(mode: str, a: int, b: int) -> list[tuple[int, str, int]]:
    a %= ORDER
    b %= ORDER
    ab = (a * b) % ORDER
    if mode == "direct_pair":
        return [(8, "a", a), (11, "b", b)]
    if mode == "cross_pair":
        return [(8, "a", a), (8, "ab", ab), (11, "b", b), (11, "ab", ab)]
    if mode == "quadratic_pair":
        return [(8, "a", a), (8, "a2", a * a % ORDER), (11, "b", b), (11, "b2", b * b % ORDER)]
    if mode == "full_pair":
        return [(8, "a", a), (8, "b", b), (8, "ab", ab), (11, "a", a), (11, "b", b), (11, "ab", ab)]
    if mode == "antisym_pair":
        return [(8, "a_plus_b", (a + b) % ORDER), (11, "a_minus_b", (a - b) % ORDER)]
    raise ValueError(f"unknown channel mode: {mode}")


def transform_specs() -> list[dict[str, Any]]:
    modes = [
        "direct_pair",
        "cross_pair",
        "quadratic_pair",
        "full_pair",
        "antisym_pair",
    ]
    specs = []
    for pair in pair_specs():
        for mode in modes:
            specs.append(
                {
                    "description": f"{pair['name']} two-feature channel mode {mode}.",
                    "mode": mode,
                    "name": f"{pair['name']}__{mode}",
                    "pair_fn": pair["fn"],
                    "pair_name": pair["name"],
                }
            )
    return specs


def labels_for_spec(spec: dict[str, Any]) -> list[tuple[int, str]]:
    return sorted({(factor, channel) for factor, channel, _value in channel_values(spec["mode"], 2, 3)})


def pair_histogram(spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    pair_fn: PairFn = spec["pair_fn"]
    return serializable_counter(Counter(pair_fn(row["form"]) for row in rows))


def matrix_for_rows(
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    label_index: dict[tuple[int, str], int],
) -> list[list[int]]:
    pair_fn: PairFn = spec["pair_fn"]
    vectors = []
    for row in rows:
        a, b = pair_fn(row["form"])
        channel_map = {(factor, channel): value for factor, channel, value in channel_values(spec["mode"], a, b)}
        vector = [0] * len(label_index)
        for factor, coeff in p1045.form_signature(row["form"], 0):
            for (channel_factor, channel), value in channel_map.items():
                if channel_factor != factor:
                    continue
                vector[label_index[(channel_factor, channel)]] = (
                    vector[label_index[(channel_factor, channel)]] + (coeff % ORDER) * (value % ORDER)
                ) % ORDER
        vectors.append(vector)
    return vectors


def rank(vectors: list[list[int]]) -> int:
    return p1045.p1043.mod_rank(vectors, ORDER)


def nonzero_count(vectors: list[list[int]]) -> int:
    return sum(1 for vector in vectors if any(value % ORDER for value in vector))


def summarize_model(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    compressed_false_count: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    label_index = {label: offset for offset, label in enumerate(labels_for_spec(spec))}
    train_vectors = matrix_for_rows(spec, train_rows, label_index)
    validation_vectors = matrix_for_rows(spec, validation_rows, label_index)
    combined_vectors = train_vectors + validation_vectors
    train_rank = rank(train_vectors)
    validation_rank = rank(validation_vectors)
    combined_rank = rank(combined_vectors)
    train_nonzero = nonzero_count(train_vectors)
    validation_nonzero = nonzero_count(validation_vectors)
    validation_in_train_span = bool(validation_rows and combined_rank == train_rank)
    candidate = bool(
        train_rank > 0
        and validation_nonzero > 0
        and validation_in_train_span
        and compressed_false_count == 0
    )
    return {
        "candidate_success_predicate": candidate,
        "channel_count": len(label_index),
        "combined_rank": combined_rank,
        "description": spec["description"],
        "labels": [list(label) for label in sorted(label_index)],
        "mode": spec["mode"],
        "name": spec["name"],
        "pair_histogram": pair_histogram(spec, all_rows),
        "pair_name": spec["pair_name"],
        "train_nonzero_row_count": train_nonzero,
        "train_rank": train_rank,
        "train_rows": len(train_rows),
        "validation_in_train_span": validation_in_train_span,
        "validation_nonzero_row_count": validation_nonzero,
        "validation_rank": validation_rank,
        "validation_rows": len(validation_rows),
    }


def public_pair_map(spec: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[list[str], list[tuple[int, int]]]:
    publics = sorted({p1045.public_key_value(row["form"]) for row in rows})
    pair_fn: PairFn = spec["pair_fn"]
    pairs = []
    for public in publics:
        form = next(row["form"] for row in rows if p1045.public_key_value(row["form"]) == public)
        a, b = pair_fn(form)
        pairs.append((a % ORDER, b % ORDER))
    return publics, pairs


def mapped_spec(spec: dict[str, Any], mapping: dict[str, tuple[int, int]], source: str, index: int) -> dict[str, Any]:
    def pair_fn(form: dict[str, Any]) -> tuple[int, int]:
        return mapping.get(p1045.public_key_value(form), (0, 0))

    return {
        "description": f"{source} two-feature control {index} for {spec['name']}.",
        "mode": spec["mode"],
        "name": f"{spec['name']}__{source}_{index:03d}",
        "pair_fn": pair_fn,
        "pair_name": f"{spec['pair_name']}_{source}",
    }


def matched_random_pairs(name: str, index: int, observed_pairs: list[tuple[int, int]], count: int) -> list[tuple[int, int]]:
    rng = random.Random(stable_seed(f"{SCHEMA}:{name}:matched:{index}"))
    first_values = [item[0] for item in observed_pairs]
    second_values = [item[1] for item in observed_pairs]
    return [(rng.choice(first_values), rng.choice(second_values)) for _ in range(count)]


def full_random_pairs(name: str, index: int, count: int) -> list[tuple[int, int]]:
    rng = random.Random(stable_seed(f"{SCHEMA}:{name}:full:{index}"))
    return [(rng.randrange(1, ORDER), rng.randrange(1, ORDER)) for _ in range(count)]


def control_analysis(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    compressed_false_count: int,
    observed: dict[str, Any],
    trials: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    publics, observed_pairs = public_pair_map(spec, all_rows)
    control_sets: dict[str, list[dict[str, Any]]] = {
        "shuffled_pair": [],
        "matched_random_pair": [],
        "full_random_pair": [],
    }
    for index in range(trials):
        shuffled = list(observed_pairs)
        random.Random(stable_seed(f"{SCHEMA}:{spec['name']}:shuffle:{index}")).shuffle(shuffled)
        control_sets["shuffled_pair"].append(
            summarize_model(
                mapped_spec(spec, dict(zip(publics, shuffled)), "shuffle", index),
                train_rows,
                validation_rows,
                compressed_false_count,
            )
        )
        matched = matched_random_pairs(spec["name"], index, observed_pairs, len(publics))
        control_sets["matched_random_pair"].append(
            summarize_model(
                mapped_spec(spec, dict(zip(publics, matched)), "matched_random", index),
                train_rows,
                validation_rows,
                compressed_false_count,
            )
        )
        full = full_random_pairs(spec["name"], index, len(publics))
        control_sets["full_random_pair"].append(
            summarize_model(
                mapped_spec(spec, dict(zip(publics, full)), "full_random", index),
                train_rows,
                validation_rows,
                compressed_false_count,
            )
        )

    observed_rank = int(observed["combined_rank"])

    def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
        rank_ge = [
            result
            for result in results
            if result["candidate_success_predicate"] and int(result["combined_rank"]) >= observed_rank
        ]
        profile_equal = [
            result
            for result in results
            if result["candidate_success_predicate"]
            and (
                result["train_rank"],
                result["validation_rank"],
                result["combined_rank"],
            )
            == (
                observed["train_rank"],
                observed["validation_rank"],
                observed["combined_rank"],
            )
        ]
        candidate_like = [result for result in results if result["candidate_success_predicate"]]
        return {
            "candidate_like_count": len(candidate_like),
            "profile_equal_count": len(profile_equal),
            "rank_ge_observed_count": len(rank_ge),
            "rank_histogram": serializable_counter(Counter(result["combined_rank"] for result in results)),
            "trial_count": trials,
        }

    return {name: summarize(results) for name, results in control_sets.items()}


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    strict_records, strict_form_rows, strict_meta = p1045.load_artifact_records(input_paths)
    broad_records, broad_meta = p1047.rematerialize_broad_pairs(args)
    factor_count = max(p1045.int_value(strict_meta["factor_count"]), p1045.int_value(broad_meta["factor_count"]))
    train_rows = p1047.rows_from_form_items(strict_form_rows, factor_count, "p1045_strict_train")
    train_ids = {row["identity"] for row in train_rows}
    broad_rows_all = p1047.rows_from_prediction_pairs(broad_records, factor_count, "p1050_broad_validation")
    validation_rows = [row for row in broad_rows_all if row["identity"] not in train_ids]
    p1047.assign_ordinals(train_rows + validation_rows)

    compressed_false_count = sum(1 for record in broad_records if not record["toy_secret_verified"])
    compressed_true_count = sum(1 for record in broad_records if record["toy_secret_verified"])
    compressed_prediction_count = len(broad_records)

    model_results = []
    for spec in transform_specs():
        observed = summarize_model(spec, train_rows, validation_rows, compressed_false_count)
        controls = control_analysis(spec, train_rows, validation_rows, compressed_false_count, observed, args.trials)
        strict_pass = bool(
            observed["candidate_success_predicate"]
            and controls["shuffled_pair"]["rank_ge_observed_count"] == 0
            and controls["matched_random_pair"]["rank_ge_observed_count"] == 0
            and controls["full_random_pair"]["rank_ge_observed_count"] == 0
        )
        model_results.append(
            {
                "control_analysis": controls,
                "model": observed,
                "strict_validation_pass": strict_pass,
            }
        )
    model_results.sort(
        key=lambda item: (
            not item["strict_validation_pass"],
            not item["model"]["candidate_success_predicate"],
            item["control_analysis"]["matched_random_pair"]["rank_ge_observed_count"],
            item["control_analysis"]["full_random_pair"]["rank_ge_observed_count"],
            item["control_analysis"]["shuffled_pair"]["rank_ge_observed_count"],
            -item["model"]["combined_rank"],
            item["model"]["name"],
        )
    )

    strict_passes = [item for item in model_results if item["strict_validation_pass"]]
    public_candidates = [item for item in model_results if item["model"]["candidate_success_predicate"]]
    matched_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["matched_random_pair"]["rank_ge_observed_count"] > 0
    ]
    full_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["full_random_pair"]["rank_ge_observed_count"] > 0
    ]
    shuffled_reproduced = [
        item
        for item in public_candidates
        if item["control_analysis"]["shuffled_pair"]["rank_ge_observed_count"] > 0
    ]
    if strict_passes:
        claim = "P1050_NONLINEAR_TWO_FEATURE_PUBLIC_SIGNAL"
        taxonomy = "OBSERVATION"
    elif public_candidates and len(matched_reproduced) == len(public_candidates):
        claim = "NEGATIVE_RESULT_P1050_TWO_FEATURES_MATCH_MATCHED_RANDOM_NULL"
        taxonomy = "NEGATIVE RESULT"
    elif public_candidates and len(full_reproduced) == len(public_candidates):
        claim = "NEGATIVE_RESULT_P1050_TWO_FEATURES_MATCH_FULL_RANDOM_NULL"
        taxonomy = "NEGATIVE RESULT"
    elif public_candidates and len(shuffled_reproduced) == len(public_candidates):
        claim = "NEGATIVE_RESULT_P1050_TWO_FEATURES_MATCH_SHUFFLE_NULL"
        taxonomy = "NEGATIVE RESULT"
    elif public_candidates:
        claim = "NEGATIVE_RESULT_P1050_TWO_FEATURES_NOT_STRICTLY_VALIDATED"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1050_NO_TWO_FEATURE_HELDOUT_CANDIDATES"
        taxonomy = "NEGATIVE RESULT"

    p1049_payload = json.loads(Path(args.p1049_input).read_text(encoding="utf-8")) if Path(args.p1049_input).exists() else {}
    windows = broad_meta["windows"]
    source_hashes = {
        window: p1005.sha256_file(p1047.p1044.p1007.expanded_source_path(window))
        for window in windows
        if p1047.p1044.p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1049_input": str(args.p1049_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1049_input_sha256": p1005.sha256_file(Path(args.p1049_input)) if Path(args.p1049_input).exists() else None,
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "TWO-FEATURE-CHANNELS: global channel labels are used; there are no public-specific factor labels.",
            "NULL-CONTROLS: shuffled observed pairs, matched random pairs, and full-field random pairs are all promotion blockers.",
            "REPRESENTATION-CATALOG: this tests finite nonlinear channel families only, not all possible coordinate representations.",
            "INDEX-CALCULUS PRECURSOR: a pass would still require relation collection, sparse linear algebra, and target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "model_results": model_results,
        "parameters": {
            "base_residual": p1045.BASE_RESIDUAL,
            "base_signature": [list(item) for item in p1045.BASE_SIGNATURE],
            "factor_count": factor_count,
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "modulus": ORDER,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "trials": args.trials,
            "windows": windows,
        },
        "p1049_claim_status": p1049_payload.get("claim_status"),
        "rematerialized_broad_summary": {
            "all_base_rows": len(broad_rows_all),
            "broad_only_validation_rows": len(validation_rows),
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "forward_exists_count": sum(1 for value in broad_meta["forward_exists"].values() if value),
            "pool_summaries": broad_meta["pool_summaries"],
            "unique_broad_public_count": len({p1045.public_key_value(row["form"]) for row in broad_rows_all}),
            "unique_validation_public_count": len({p1045.public_key_value(row["form"]) for row in validation_rows}),
        },
        "schema": SCHEMA,
        "strict_train_summary": {
            "input_paths": [str(path) for path in input_paths],
            "strict_pair_count": len(strict_records),
            "train_rows": len(train_rows),
            "unique_train_public_count": len({p1045.public_key_value(row["form"]) for row in train_rows}),
        },
        "summary": {
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "full_random_reproduced_candidate_count": len(full_reproduced),
            "matched_random_reproduced_candidate_count": len(matched_reproduced),
            "public_candidate_count": len(public_candidates),
            "shuffled_reproduced_candidate_count": len(shuffled_reproduced),
            "strict_validation_pass_count": len(strict_passes),
            "strict_validation_pass_models": [item["model"]["name"] for item in strict_passes],
            "tested_model_count": len(model_results),
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated persisted strict witness probe paths for train rows",
    )
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Rematerialization window count")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1049-input", default=str(DEFAULT_P1049_INPUT), help="P1049 constant-free probe path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to rematerialize")
    parser.add_argument("--targets", default=p1047.p1044.p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Controls per model")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} train_rows={train} validation_rows={validation} compressed_pred={pred} compressed_false={false} candidates={candidates} matched_random={matched} full_random={full} shuffled={shuffled} strict_pass={passes} out={out}".format(
            claim=payload["claim_status"],
            train=summary["train_rows"],
            validation=summary["validation_rows"],
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            candidates=summary["public_candidate_count"],
            matched=summary["matched_random_reproduced_candidate_count"],
            full=summary["full_random_reproduced_candidate_count"],
            shuffled=summary["shuffled_reproduced_candidate_count"],
            passes=summary["strict_validation_pass_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
