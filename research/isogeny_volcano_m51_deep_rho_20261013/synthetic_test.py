#!/usr/bin/env python3
"""Pre-outcome synthetic/adversarial tests for the deep-rho design and analysis."""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np

import analyze
from design import (
    ARMS,
    RNG_TEST_VECTORS,
    build_plan,
    build_setup_robustness_plan,
    conjugate,
    expected_scalar,
    expected_walk_stream,
    frobenius_offset,
    generate_schedule,
    load_json,
    read_f271_orbits,
    read_schedule,
    sha256_file,
)
from run_benchmark import (
    CHILD_ENV,
    RunError,
    fixture_pairs,
    make_units,
    recover_sealed_setup_robustness_summary,
    run_subprocess,
    seal_tree,
)


HERE = Path(__file__).resolve().parent


def add_outcomes(plan: list[dict[str, object]], *, constant_main: bool = False) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    bases = {"C": 1 << 10, "A": 1 << 11, "P": 1 << 12, "B": 1 << 13}
    for source in plan:
        row = dict(source)
        arm = str(row["arm"])
        pair = int(row["pair_id"])
        block = int(row["block_id"])
        if row["subset"] == "inference":
            if constant_main:
                walk_ops = bases[arm]
            else:
                arm_index = ARMS.index(arm)
                base = {"C": 10000, "A": 10350, "P": 10800, "B": 11150}[arm]
                pair_term = (pair - 15) * (arm_index + 1) * 3
                jitter = ((block * (17 + arm_index * 6) + arm_index * 13) % 97) - 48
                walk_ops = base + pair_term + jitter
        else:
            arm_index = ARMS.index(arm)
            base = 10000 + 300 * arm_index
            jitter = ((block * (19 + arm_index * 4) + arm_index * 11) % 83) - 41
            if row["replicate"] == "aa-A":
                walk_ops = base + jitter
            else:
                epsilon = ((pair + 2 * arm_index) % 7 - 3) * 0.0015
                other_jitter = ((block * (23 + arm_index * 2) + 31) % 83) - 41
                walk_ops = int(round((base + other_jitter) * (2.0**epsilon)))
        walk_ops = int(walk_ops)
        row.update(
            {
                "walk_ops": walk_ops,
                "walk_adds": walk_ops,
                "walk_doubles": 0,
                "setup_ops": 162,
                "setup_adds": 128,
                "setup_doubles": 34,
                "ops": walk_ops + 162,
                "adds": walk_ops + 128,
                "doubles": 34,
                "canon_calls": walk_ops // 2 + 1,
                "canon_x_squares": 0,
                "canon_y_squares": 0,
                "canon_sign_tests": walk_ops // 2 + 1,
                "canon_negations": walk_ops // 4,
                "walks": 2,
                "cycles": 0,
                "abandoned": 0,
                "useless": 0,
                "sec": walk_ops / 1e7,
            }
        )
        rows.append(row)
    return rows


def assert_close(actual: float, expected: float, tolerance: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"{actual} != {expected}")


def null_coverage_regression(
    matrix: np.ndarray, *, confidence: float, seed: int
) -> tuple[float, float, float]:
    """Independent fixed-seed Gaussian null check of family coverage."""
    outer = 500
    draws = 2048
    clusters = 32
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.asarray([-1.0, 1.0]), size=(draws, clusters))
    order = math.ceil((draws + 1) * confidence) - 1
    fixed_hits = 0
    restudentized_hits = 0
    restudentized_criticals: list[float] = []
    for _ in range(outer):
        arms = rng.normal(size=(clusters, 4))
        estimates = matrix @ np.mean(arms, axis=0)
        cluster_values = arms @ matrix.T
        influence = cluster_values - np.mean(cluster_values, axis=0)
        sum_squares = np.sum(influence * influence, axis=0)
        standard_error = np.sqrt(sum_squares / (clusters * (clusters - 1)))
        numerator = signs @ influence
        fixed_scores = numerator / np.sqrt(sum_squares)
        fixed_critical = float(
            np.partition(np.max(np.abs(fixed_scores), axis=1), order)[order]
        )
        restudentized_scores = analyze.restudentized_multiplier_scores(
            influence, signs
        )
        restudentized_critical = float(
            np.partition(
                np.max(np.abs(restudentized_scores), axis=1), order
            )[order]
        )
        fixed_hits += int(
            np.all(np.abs(estimates) <= fixed_critical * standard_error)
        )
        restudentized_hits += int(
            np.all(
                np.abs(estimates)
                <= restudentized_critical * standard_error
            )
        )
        restudentized_criticals.append(restudentized_critical)
    return (
        fixed_hits / outer,
        restudentized_hits / outer,
        float(np.mean(restudentized_criticals)),
    )


def skewed_cluster_mean_coverage_regression(seed: int) -> tuple[float, float]:
    """Positive gamma cluster means exercise the nonlinear log-mean estimator."""
    outer = 500
    draws = 2048
    clusters = 32
    confidence = 0.95
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.asarray([-1.0, 1.0]), size=(draws, clusters))
    order = math.ceil((draws + 1) * confidence) - 1
    fixed_hits = 0
    restudentized_hits = 0
    for _ in range(outer):
        arms = rng.gamma(shape=32.0, scale=1.0 / 32.0, size=(clusters, 4))
        full = analyze.CONTRAST_MATRIX @ np.log2(np.mean(arms, axis=0))
        leave = np.asarray(
            [
                analyze.CONTRAST_MATRIX
                @ np.log2(np.mean(np.delete(arms, omitted, axis=0), axis=0))
                for omitted in range(clusters)
            ]
        )
        pseudo = clusters * full - (clusters - 1) * leave
        influence = pseudo - np.mean(pseudo, axis=0)
        sum_squares = np.sum(influence * influence, axis=0)
        standard_error = np.sqrt(sum_squares / (clusters * (clusters - 1)))
        numerator = signs @ influence
        fixed_scores = numerator / np.sqrt(sum_squares)
        fixed_critical = float(
            np.partition(np.max(np.abs(fixed_scores), axis=1), order)[order]
        )
        restudentized_scores = analyze.restudentized_multiplier_scores(
            influence, signs
        )
        restudentized_critical = float(
            np.partition(
                np.max(np.abs(restudentized_scores), axis=1), order
            )[order]
        )
        fixed_hits += int(
            np.all(np.abs(full) <= fixed_critical * standard_error)
        )
        restudentized_hits += int(
            np.all(np.abs(full) <= restudentized_critical * standard_error)
        )
    return fixed_hits / outer, restudentized_hits / outer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip CPU-heavy coverage regression and reduce synthetic multiplier draws",
    )
    args = parser.parse_args()
    analyze.bind_design(HERE / "design.py", sha256_file(HERE / "design.py"))
    spec = load_json(HERE / "spec.json")
    schedule = read_schedule(HERE / "schedule.csv")
    assert schedule == generate_schedule(spec["seeds"]["schedule_root"])
    f271 = read_f271_orbits(HERE / "floor271_orbits.csv")
    pairs = fixture_pairs()
    assert all(pair.bottom_b != pair.bottom_orbit_rep for pair in pairs)
    assert [frobenius_offset(pair.bottom_orbit_rep, pair.bottom_b) for pair in pairs] == [
        1 + pair_id % 50 for pair_id in range(32)
    ]
    plan = build_plan(schedule, pairs, f271, spec["seeds"])
    for pair in pairs:
        for exponent in range(51):
            p = next(
                row
                for row in plan
                if row["replicate"] == "inference"
                and row["arm"] == "P"
                and row["pair_id"] == pair.pair_id
                and row["conjugate"] == exponent
            )
            b = next(
                row
                for row in plan
                if row["replicate"] == "inference"
                and row["arm"] == "B"
                and row["pair_id"] == pair.pair_id
                and row["conjugate"] == exponent
            )
            assert p["b"] == conjugate(pair.parent_b, exponent)
            assert b["b"] == conjugate(pair.bottom_b, exponent)
    units = make_units(plan, spec["seeds"]["schedule_root"], 4, [0, 1, 2, 3])
    assert len(plan) == 20480
    assert sum(len(worker.units) for worker in units) == 3556
    robustness_plan = build_setup_robustness_plan(
        pairs, f271, spec["setup_robustness"]
    )
    robustness_units = make_units(
        robustness_plan,
        spec["setup_robustness"]["panel_seed"],
        4,
        [0, 1, 2, 3],
        expected_models=97,
        expected_units=1649,
        expected_records=2176,
    )
    assert len(robustness_plan) == 2176
    assert sum(len(worker.records) for worker in robustness_units) == 2176
    assert sum(len(worker.units) for worker in robustness_units) == 1649
    all_robustness_seeds = [
        *spec["setup_robustness"]["setup_seeds"],
        spec["setup_robustness"]["original_setup_seed"],
    ]
    for setup_seed in all_robustness_seeds:
        root_rows = [row for row in robustness_plan if row["setup_seed"] == setup_seed]
        assert len(root_rows) == 128
        assert {row["target_index"] for row in root_rows} == set(range(32))
    assert spec["setup_robustness"]["original_setup_seed"] == spec["seeds"]["setup_root"]
    assert {
        (row["orbit_id"], row["conjugate"])
        for row in robustness_plan
        if row["arm"] == "A" and row["setup_seed"] == spec["setup_robustness"]["setup_seeds"][0]
    } and all(
        sum(
            row["arm"] == "A"
            and row["orbit_id"] == orbit_id
            and row["setup_seed"] == spec["setup_robustness"]["setup_seeds"][0]
            for row in robustness_plan
        )
        == 2
        for orbit_id in range(1, 17)
    )

    # Literal vectors bind the Python validator to the unchanged C RNG core.
    for target_seed, walk_seed, target_index, scalar, stream in RNG_TEST_VECTORS:
        assert expected_scalar(target_seed, target_index) == scalar
        assert expected_walk_stream(walk_seed, target_index) == stream

    # The analyzer must refuse altered design bytes before importing them.
    with tempfile.TemporaryDirectory(prefix="m51-design-tamper-") as directory:
        copied = Path(directory) / "design.py"
        shutil.copyfile(HERE / "design.py", copied)
        expected_design_hash = sha256_file(copied)
        analyze.load_design_module(copied, expected_design_hash)
        with copied.open("a") as handle:
            handle.write("\n# synthetic tamper\n")
        try:
            analyze.load_design_module(copied, expected_design_hash)
        except analyze.AnalysisError:
            pass
        else:
            raise AssertionError("analyzer accepted altered design.py bytes")

    # A fully sealed conditional phase remains recoverable if an asynchronous
    # exception lands after its atomic MANIFEST write but before return to the
    # caller.  Recovery must come from verified bytes, never stale memory.
    with tempfile.TemporaryDirectory(prefix="m51-post-seal-") as directory:
        root = Path(directory)
        phase = root / "setup_robustness"
        build = root / "build"
        phase.mkdir()
        build.mkdir()
        binary = build / "rho-batch"
        binary.write_bytes(b"synthetic static binary fixture\n")
        for name, value in (
            ("record_plan.csv", "plan\n"),
            ("records.csv", "records\n"),
            ("native_setups.csv", "setups\n"),
        ):
            (phase / name).write_text(value)
        phase_analysis = {
            "schema": "m51-deep-rho-setup-robustness-analysis/v1",
            "status": "complete",
        }
        (phase / "analysis.json").write_text(
            json.dumps(phase_analysis, sort_keys=True) + "\n"
        )
        decision_hash = "1" * 64
        primary_records_hash = "2" * 64
        preflight_hash = "3" * 64
        phase_manifest = {
            "schema": "m51-deep-rho-setup-robustness-run/v1",
            "scientific": True,
            "trigger_decision_sha256": decision_hash,
            "primary_records_sha256": primary_records_hash,
            "preflight_plan_sha256": preflight_hash,
            "records": 2176,
            "fresh_inferential_setup_root_clusters": 16,
            "descriptive_original_root_bridges": 1,
            "total_setup_roots": 17,
            "blocks_per_setup_root": 32,
            "distinct_models": 97,
            "execution_units": 1649,
            "execution_status": "complete",
            "analysis_status": "complete",
            "record_plan_sha256": sha256_file(phase / "record_plan.csv"),
            "records_sha256": sha256_file(phase / "records.csv"),
            "native_setups_sha256": sha256_file(phase / "native_setups.csv"),
            "analysis_sha256": sha256_file(phase / "analysis.json"),
            "binary_sha256": sha256_file(binary),
        }
        (phase / "run_manifest.json").write_text(
            json.dumps(phase_manifest, sort_keys=True) + "\n"
        )
        sealed_path = seal_tree(phase)
        recovered = recover_sealed_setup_robustness_summary(
            phase=phase,
            binary=binary,
            trigger_decision_sha256=decision_hash,
            primary_records_sha256=primary_records_hash,
            preflight_plan_sha256=preflight_hash,
        )
        assert recovered["status"] == "complete"
        assert recovered["phase_manifest_sha256"] == sha256_file(sealed_path)
        with (phase / "records.csv").open("a") as handle:
            handle.write("tamper\n")
        try:
            recover_sealed_setup_robustness_summary(
                phase=phase,
                binary=binary,
                trigger_decision_sha256=decision_hash,
                primary_records_sha256=primary_records_hash,
                preflight_plan_sha256=preflight_hash,
            )
        except RunError:
            pass
        else:
            raise AssertionError("post-seal recovery accepted a tampered tree")

    # A leader that exits while a descendant holds its pipes must be bounded,
    # killed as a process group, and reaped by this runner.
    shell = shutil.which("sh", path=CHILD_ENV["PATH"])
    if shell is None:
        raise AssertionError("fixed child PATH lacks sh")
    started = time.monotonic()
    cleanup = run_subprocess(
        [shell, "-c", "sleep 30 &"], cwd=HERE, timeout=10
    )
    assert cleanup["exit_status"] == 0
    assert cleanup["residual_group_cleaned"] is True
    assert "residual process group terminated and reaped" in cleanup["stderr"]
    assert time.monotonic() - started < 8

    zero_cell_scores = analyze.restudentized_multiplier_scores(
        np.asarray([[1.0], [1.0], [-1.0], [-1.0]]),
        np.asarray([[1.0, 1.0, -1.0, -1.0], [1.0, -1.0, 1.0, -1.0]]),
    )
    assert math.isinf(float(zero_cell_scores[0, 0]))
    assert math.isfinite(float(zero_cell_scores[1, 0]))
    positive_near_zero_scores = analyze.restudentized_multiplier_scores(
        np.asarray([[1.0 + 5e-8], [1.0 - 5e-8], [-1.0], [-1.0]]),
        np.asarray([[1.0, 1.0, -1.0, -1.0]]),
    )
    assert math.isinf(float(positive_near_zero_scores[0, 0]))
    scale_influence = np.asarray(
        [[1.0, -2.0], [3.0, 1.0], [-2.0, 4.0], [-2.0, -3.0]]
    )
    scale_signs = np.asarray(
        [[1.0, -1.0, 1.0, -1.0], [-1.0, -1.0, 1.0, 1.0]]
    )
    scale_reference = analyze.restudentized_multiplier_scores(
        scale_influence, scale_signs
    )
    np.testing.assert_allclose(
        analyze.restudentized_multiplier_scores(
            scale_influence * 1e-12, scale_signs
        ),
        scale_reference,
        rtol=1e-12,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        analyze.restudentized_multiplier_scores(
            scale_influence * 1e12, scale_signs
        ),
        scale_reference,
        rtol=1e-12,
        atol=1e-12,
    )

    if not args.quick:
        fixed_95, restudentized_95, critical_95 = null_coverage_regression(
            analyze.CONTRAST_MATRIX, confidence=0.95, seed=202610136109
        )
        assert fixed_95 < 0.93
        assert 0.93 <= restudentized_95 <= 0.98
        assert restudentized_95 - fixed_95 >= 0.025
        assert 2.75 <= critical_95 <= 2.95
        fixed_99, restudentized_99, critical_99 = null_coverage_regression(
            np.eye(4), confidence=0.99, seed=202610136110
        )
        assert fixed_99 < 0.985
        assert 0.975 <= restudentized_99 <= 1.0
        assert restudentized_99 > fixed_99
        assert 2.9 <= critical_99 <= 3.5
        skewed_fixed, skewed_restudentized = skewed_cluster_mean_coverage_regression(
            202610136111
        )
        assert skewed_fixed < 0.93
        assert 0.93 <= skewed_restudentized <= 0.98
        assert skewed_restudentized - skewed_fixed >= 0.025

    # Exact arithmetic-mean contrasts and deliberate zero-SE refusal.
    constant = add_outcomes(plan, constant_main=True)
    theta, means, _ = analyze.endpoint_theta(constant, list(range(32)))
    np.testing.assert_allclose(means, [2**10, 2**11, 2**12, 2**13], rtol=0, atol=0)
    np.testing.assert_allclose(theta, [1, 2, 3, 1, 2, 1, 1, 2, 0], rtol=0, atol=1e-14)
    zero_jack = analyze.jackknife(lambda ids: analyze.endpoint_theta(constant, ids), list(range(32)))
    zero_family = analyze.multiplier_family(
        zero_jack,
        seed=spec["seeds"]["multiplier_root"],
        domain=0x4D41494E,
        draws=1000,
        confidence=0.95,
        ids=analyze.CONTRAST_IDS,
    )
    assert zero_family["status"] == "non_estimable_zero_or_nonfinite_jackknife_scale"

    # Contrast identities, common-scale invariance and rank-3 singular family.
    assert np.linalg.matrix_rank(analyze.CONTRAST_MATRIX) == 3
    np.testing.assert_allclose(analyze.CONTRAST_MATRIX.sum(axis=1), 0.0, atol=0, rtol=0)
    x = np.asarray([10.0, 11.0, 12.0, 14.0])
    values = analyze.CONTRAST_MATRIX @ x
    assert_close(values[6], 1.5)
    assert_close(values[7], 2.5)
    assert_close(values[8], 0.5)
    assert_close(2 * values[8], (x[3] - x[2]) - (x[1] - x[0]))
    np.testing.assert_allclose(analyze.CONTRAST_MATRIX @ (x + 7.25), values, atol=1e-14)

    varied = add_outcomes(plan)
    shuffled = list(varied)
    random.Random(spec["seeds"]["synthetic_test_root"]).shuffle(shuffled)
    theta_ordered = analyze.endpoint_theta(varied, list(range(32)))[0]
    theta_shuffled = analyze.endpoint_theta(shuffled, list(range(32)))[0]
    np.testing.assert_allclose(theta_ordered, theta_shuffled, rtol=0, atol=1e-14)

    # The calibrated P mean differs from a raw-row mean because 45 conjugates
    # are duplicated; this catches accidental raw-row rather than cell weighting.
    p_rows = [row for row in varied if row["subset"] == "inference" and row["arm"] == "P"]
    for row in p_rows:
        row["walk_ops"] += int(row["conjugate"]) * 100
    calibrated_p = analyze.endpoint_theta(varied, list(range(32)))[1][2]
    raw_p = float(np.mean([row["walk_ops"] for row in p_rows]))
    assert not math.isclose(calibrated_p, raw_p, rel_tol=0, abs_tol=1e-6)

    # Missing cells fail closed, including in delete-one-pair recalibration.
    missing = [
        row
        for row in varied
        if not (
            row["subset"] == "inference"
            and row["arm"] == "A"
            and row["orbit_id"] == 1
            and row["conjugate"] == 0
        )
    ]
    try:
        analyze.endpoint_theta(missing, list(range(32)))
    except analyze.AnalysisError:
        pass
    else:
        raise AssertionError("missing A model cell did not fail closed")

    # Golden multiplier stream and conservative (R+1) order statistic.
    signs, sign_hash = analyze.rademacher(123456789, 0x54455354, 8, 4)
    assert signs.tolist() == [
        [-1, -1, 1, 1],
        [-1, -1, 1, -1],
        [1, 1, -1, -1],
        [1, -1, -1, -1],
        [1, 1, 1, -1],
        [-1, 1, 1, 1],
        [-1, -1, -1, 1],
        [1, 1, 1, -1],
    ]
    assert sign_hash == "b66b2324a7c3e0388f6cb2e68aceca8e3fcd515038eae5025a82d433218676bc"

    # Full 100k-draw synthetic analysis: null-like A/A must pass.
    analysis_spec = copy.deepcopy(spec)
    if args.quick:
        analysis_spec["contrast_family"]["resamples"] = 2048
        analysis_spec["aa_gate"]["resamples"] = 2048
    result = analyze.analyze_records(analysis_spec, varied)
    assert result["aa_gate"]["pass"] is True
    assert result["modeled_population_inference"]["population"] == {
        "parent_orbits": 2369,
        "bottom_orbits": 644368,
        "pilot_parent_fibers_excluded": 1,
    }
    assert result["claim_boundary"]["complete_named_levels"] is False

    trigger_fixture = copy.deepcopy(result)
    trigger_fixture["status"] = "complete"
    trigger_fixture["aa_gate"]["pass"] = True
    trigger_fixture["modeled_population_inference"]["family"]["status"] = "estimable"
    for row in trigger_fixture["contrasts"]:
        row["bits"] = 0.49
        row["modeled_population_lower_bits"] = 0.01
        row["modeled_population_upper_bits"] = 0.10
    assert not analyze.setup_robustness_trigger(
        trigger_fixture, spec["setup_robustness"]
    )["triggered"]
    trigger_fixture["contrasts"][0].update(
        bits=0.5,
        modeled_population_lower_bits=0.01,
        modeled_population_upper_bits=0.20,
    )
    trigger = analyze.setup_robustness_trigger(
        trigger_fixture, spec["setup_robustness"]
    )
    assert trigger["triggered"] is True
    assert [row["id"] for row in trigger["qualifying_contrasts"]] == ["A-C"]
    persistence_rows = [
        {
            "id": contrast_id,
            "bits": 0.7,
            "work_ratio": 2.0**0.7,
            "simultaneous_lower_bits": 0.5,
            "simultaneous_upper_bits": 0.9,
        }
        for contrast_id in analyze.CONTRAST_IDS
    ]
    persistence = analyze._setup_persistence_assessment(
        spec["setup_robustness"],
        trigger,
        persistence_rows,
        family_estimable=True,
    )
    assert persistence["directional_global"] == "complete"
    assert persistence["practical_global"] == "complete"
    assert persistence["contrasts"][0]["practical_persists"] is True
    two_trigger = copy.deepcopy(trigger)
    two_trigger["qualifying_contrasts"].append(
        {
            "id": "P-C",
            "bits": -0.7,
            "simultaneous_lower_bits": -0.9,
            "simultaneous_upper_bits": -0.1,
        }
    )
    persistence_rows[1].update(
        bits=-0.3,
        work_ratio=2.0**-0.3,
        simultaneous_lower_bits=-0.4,
        simultaneous_upper_bits=-0.1,
    )
    partial = analyze._setup_persistence_assessment(
        spec["setup_robustness"],
        two_trigger,
        persistence_rows,
        family_estimable=True,
    )
    assert partial["directional_global"] == "complete"
    assert partial["practical_global"] == "partial"
    persistence_rows[0].update(
        bits=0.1,
        work_ratio=2.0**0.1,
        simultaneous_lower_bits=-0.1,
        simultaneous_upper_bits=0.3,
    )
    none = analyze._setup_persistence_assessment(
        spec["setup_robustness"],
        trigger,
        persistence_rows,
        family_estimable=True,
    )
    assert none["directional_global"] == "none"
    assert none["practical_global"] == "none"
    assert none["contrasts"][0]["fresh_root_point_same_direction"] is True
    trigger_fixture["contrasts"][0]["modeled_population_lower_bits"] = 0.0
    assert not analyze.setup_robustness_trigger(
        trigger_fixture, spec["setup_robustness"]
    )["triggered"]

    all_signs, all_signs_hash = analyze.all_rademacher_signs(16)
    assert all_signs.shape == (65536, 16)
    assert len({bytes(row) for row in all_signs}) == 65536
    assert all_signs_hash == spec["setup_robustness"]["sign_vectors_sha256"]
    robustness_outcomes = add_outcomes(robustness_plan)
    robustness_analysis = analyze.analyze_setup_robustness(
        spec["setup_robustness"], robustness_outcomes, trigger
    )
    assert robustness_analysis["family"]["draws"] == 65536
    assert robustness_analysis["family"]["critical_order_1_based"] == 62260
    assert robustness_analysis["counts"]["panel_slots_per_arm"] == 32
    assert robustness_analysis["counts"]["fresh_inferential_setup_root_clusters"] == 16
    assert robustness_analysis["counts"]["descriptive_original_root_bridges"] == 1
    assert robustness_analysis["counts"]["total_setup_roots"] == 17
    assert robustness_analysis["counts"]["distinct_models_by_arm"] == {
        "C": 1,
        "A": 32,
        "P": 32,
        "B": 32,
    }
    assert robustness_analysis["descriptive_original_root_bridge"]["setup_seed"] == spec["seeds"]["setup_root"]
    assert robustness_analysis["persistence_assessment"]["status"] in {
        "estimable",
        "non_estimable",
    }

    # A 0.20-bit held-out shift in one arm raises the gate and withholds labels.
    shifted = copy.deepcopy(varied)
    for row in shifted:
        if row["subset"] == "aa" and row["replicate"] == "aa-B" and row["arm"] == "B":
            row["walk_ops"] = int(round(row["walk_ops"] * (2.0**0.20)))
            row["walk_adds"] = row["walk_ops"]
            row["ops"] = row["walk_ops"] + row["setup_ops"]
            row["adds"] = row["walk_adds"] + row["setup_adds"]
    alert = analyze.analyze_records(analysis_spec, shifted)
    assert alert["aa_gate"]["pass"] is False
    assert all(row.get("decision_label") == "WITHHELD_AA_ALERT" for row in alert["contrasts"])

    # Arithmetic-mean ratio, never mean log ratios.
    numerator = np.asarray([1.0, 100.0])
    denominator = np.asarray([1.0, 1.0])
    wanted = math.log2(float(np.mean(numerator) / np.mean(denominator)))
    trap = float(np.mean(np.log2(numerator / denominator)))
    assert not math.isclose(wanted, trap)

    print("synthetic analysis ok: schedule, calibration, jackknife, max-T, and A/A alert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
