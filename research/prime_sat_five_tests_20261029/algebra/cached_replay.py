#!/usr/bin/env python3
"""Additive replay wrapper: cache monomial comparisons, preserve the experiment.

The frozen producer/checker files are never modified. In a fresh process this
wrapper replaces only their order-key callbacks with precomputed integer ranks.
Every pair in the configured finite universe is checked before fixture work.
The row choices, field operations, certificates, counters and fixtures remain
those of the original implementation. This is not a timing comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def _corrected_source_rank(matrix, p):
    """Independent streamed echelon rank; read the current reduced row.

    The immutable check.py used enumerate(row) while rebinding row. Its
    iterator therefore retained stale coefficients after a pivot subtraction.
    This additive checker indexes the current row at every column instead.
    """
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged source matrix")
    pivots = {}
    for source in matrix:
        row = [int(value) % p for value in source]
        for column in range(width):
            value = row[column]
            if value == 0:
                continue
            if column in pivots:
                base = pivots[column]
                row = [(a - value * b) % p for a, b in zip(row, base)]
            else:
                inverse = pow(value, -1, p)
                pivots[column] = [a * inverse % p for a in row]
                break
    return len(pivots)


def _rank_integrity_regressions():
    cases = [
        ("empty", [], 5, 0),
        ("zero", [[0, 0], [0, 0]], 5, 0),
        ("identity", [[1, 0], [0, 1]], 5, 2),
        ("dependent", [[1, 1], [2, 2]], 5, 1),
        ("stale_iterator_counterexample", [[1, 1], [1, 0]], 5, 2),
        ("three_pivots", [[1, 1, 0], [1, 0, 1], [0, 1, 1]], 5, 3),
    ]
    for name, matrix, p, expected in cases:
        assert _corrected_source_rank(matrix, p) == expected, name
    return {
        "passed": True,
        "cases": [name for name, *_ in cases],
        "correction": "index the current reduced row instead of a stale enumerate iterator",
        "immutable_original_checker_preserved": True,
    }


def _load_original(filename, name):
    # A separately loaded module prevents accidental interference with a
    # caller's original module instance. Its on-disk source is untouched.
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _certified_order_cache(original_order, n):
    if not isinstance(n, int) or not 0 <= n <= 8:
        raise ValueError("This corrective replay admits only the frozen n<=8 universe")
    universe = range(1 << n)
    keys = [original_order(mask) for mask in universe]
    assert len(set(keys)) == len(keys), "original monomial order has ties"
    ordered = sorted(universe, key=keys.__getitem__)
    ranks = {mask: rank for rank, mask in enumerate(ordered)}
    pairs = 0
    for left in universe:
        for right in universe:
            old_comparison = (keys[left] > keys[right]) - (keys[left] < keys[right])
            new_comparison = (ranks[left] > ranks[right]) - (ranks[left] < ranks[right])
            assert old_comparison == new_comparison, "monomial order changed"
            pairs += 1
    digest = hashlib.sha256(json.dumps([ranks[i] for i in universe], separators=(",", ":")).encode()).hexdigest()
    return ranks.__getitem__, {
        "maximum_variables": n,
        "universe_size": 1 << n,
        "exhaustively_checked_ordered_pairs": pairs,
        "rank_table_sha256": digest,
        "comparison_equivalence_verified_before_fixture_work": True,
    }


def run(config, checkpoint_dir=None):
    if checkpoint_dir is None:
        raise ValueError("corrective replay requires a durable per-cell checkpoint_dir")
    # Needed only for the original producer's direct-script import fallback.
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    producer = _load_original("run.py", "_prime_sat_algebra_frozen_producer")
    cached_order, cache_record = _certified_order_cache(producer.mask_order, config["max_variables"])
    rank_regressions = _rank_integrity_regressions()
    producer.mask_order = cached_order
    result = producer.run(config, checkpoint_dir=checkpoint_dir)
    result["cached_replay"] = {
        "order_cache": cache_record,
        "source_rank_checker_correction": rank_regressions,
        "frozen_producer_sha256": hashlib.sha256((HERE / "run.py").read_bytes()).hexdigest(),
        "frozen_checker_sha256": hashlib.sha256((HERE / "check.py").read_bytes()).hexdigest(),
        "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "mutation_scope": "new-process producer.mask_order callback only",
        "changed_fixtures": False,
        "changed_counted_arithmetic": False,
        "timing_improvement_claim": False,
    }
    return result


def _verify_inventory_and_controls(data):
    cfg = data["config"]
    expected = {}
    for p, s, target, population in itertools.product(
            cfg["primes"], cfg["digits"], cfg["targets"], cfg["populations"]):
        expected[f"{population}-p{p}-s{s}-r{target}"] = (population, p, 2 * s)
    for p in cfg["primes"]:
        expected[f"affine-unsat-p{p}"] = ("affine_unsat", p, 4)
        expected[f"gate-backdoor-p{p}"] = ("planted_gate_backdoor", p, 7)
    cells = data["cells"]
    actual = [cell["id"] for cell in cells]
    assert len(actual) == len(set(actual)), "duplicate fixture IDs"
    assert set(actual) == set(expected), "missing or unplanned fixtures"
    lead3_count = lead4_count = branch_count = 0
    for cell in cells:
        assert (cell["population"], cell["p"], cell["n"]) == expected[cell["id"]]
        for key, declared in (("lead3", cfg["lead3_arms"]), ("lead4", cfg["lead4_arms"])):
            arms = [arm["arm"] for arm in cell[key]]
            assert len(arms) == len(set(arms)) == len(declared), "duplicate or missing arm"
            assert set(arms) == set(declared), "unplanned arm"
        lead3_count += len(cell["lead3"])
        lead4_count += len(cell["lead4"])
        for arm in cell["lead4"]:
            expected_branches = 1 << min(cfg["backdoor_bits"], cell["n"])
            assert len(arm["branches"]) == expected_branches
            branch_count += len(arm["branches"])
        if cell["population"] == "affine_unsat":
            assert cell["oracle_models"] == []
            assert all(arm["status"] == "UNSAT" and arm["models"] == [] for arm in cell["lead3"])
            assert all(arm["strong_backdoor"] and arm["models"] == [] for arm in cell["lead4"])
        elif cell["population"] == "planted_gate_backdoor":
            assert cell["oracle_models"], "positive control has no models"
            assert all(arm["status"] == "SAT_COMPLETE" for arm in cell["lead3"])
            candidate = next(arm for arm in cell["lead4"] if arm["arm"] == "degree_drop")
            assert candidate["strong_backdoor"], "known-backdoor positive control failed"
            assert 6 in candidate["cut"], "syntax policy missed the planted gate variable"
    source_cfg = cfg["source_calibration"]
    assert data["source_calibration"]["input"] == source_cfg, "source calibration input changed"
    n = len(source_cfg["variables"])
    expected_source_keys = [
        (degree, prefix)
        for degree in range(2, source_cfg["max_degree"] + 1)
        for prefix in range(1, len(list(itertools.combinations_with_replacement(range(n), degree - 2))) + 1)]
    actual_source_keys = [(matrix["degree"], matrix["prefix_multipliers"])
                          for matrix in data["source_calibration"]["matrices"]]
    assert actual_source_keys == expected_source_keys, "source prefix matrix coverage changed"
    expected_source_matrices = len(expected_source_keys)
    assert len(data["source_calibration"]["matrices"]) == expected_source_matrices
    return {
        "expected_cells": len(expected),
        "expected_lead3_arms": lead3_count,
        "expected_lead4_arms": lead4_count,
        "expected_branch_assignments": branch_count,
        "expected_source_matrices": expected_source_matrices,
        "planned_inventory_verified": True,
        "positive_controls_verified": True,
    }


def verify(data):
    # The checker retains its own polynomial operations and independent
    # exhaustive semantics. Its order cache is certified from its own callback,
    # not from the producer's precomputed table.
    checker = _load_original("check.py", "_prime_sat_algebra_frozen_checker")
    cached_order, cache_record = _certified_order_cache(checker.order, data["config"]["max_variables"])
    rank_regressions = _rank_integrity_regressions()
    checker.order = cached_order
    checker.source_rank = _corrected_source_rank
    inventory = _verify_inventory_and_controls(data)
    checked = checker.verify(data)
    assert checked["cells"] == inventory["expected_cells"]
    assert checked["lead3_arms"] == inventory["expected_lead3_arms"]
    assert checked["lead4_arms"] == inventory["expected_lead4_arms"]
    assert checked["branch_assignments"] == inventory["expected_branch_assignments"]
    assert checked["source_matrices"] == inventory["expected_source_matrices"]
    return {**checked, **inventory, "independent_checker_order_cache": cache_record,
            "source_rank_checker_correction": rank_regressions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--checkpoint-dir")
    parser.add_argument("--output", required=True)
    parser.add_argument("--verify", metavar="RESULT_JSON")
    args = parser.parse_args()
    if args.verify:
        result = verify(json.loads(Path(args.verify).read_text()))
    else:
        if args.config is None or args.checkpoint_dir is None:
            parser.error("run mode requires --config and --checkpoint-dir")
        result = run(json.loads(Path(args.config).read_text()), args.checkpoint_dir)
    Path(args.output).write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"output": args.output, "mode": "verify" if args.verify else "run"}))


if __name__ == "__main__":
    main()
