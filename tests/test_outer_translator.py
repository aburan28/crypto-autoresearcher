from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-OUTER-TRANSLATOR-001"
    / "src"
    / "outer_translator.py"
)
VERIFIER_PATH = MODULE_PATH.with_name("verify_outer_translator.py")
RUN_WRAPPER_PATH = MODULE_PATH.with_name("run_development.py")


def load_module():
    name = "test_outer_translator_module"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OT = load_module()


def load_verifier():
    name = "test_outer_translator_verifier_module"
    spec = importlib.util.spec_from_file_location(name, VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VERIFY = load_verifier()


def load_run_wrapper():
    name = "test_outer_translator_run_wrapper_module"
    spec = importlib.util.spec_from_file_location(name, RUN_WRAPPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUN_WRAPPER = load_run_wrapper()


def test_development_wrapper_is_source_bound_and_cannot_authorize_canonical(
    tmp_path: Path,
) -> None:
    raw_result = tmp_path / "raw-result.json"
    command = RUN_WRAPPER.generator_command(raw_result)
    assert "--allow-development" in command
    assert "--authorize-canonical" not in command
    bit_sizes = command[command.index("--bit-sizes") + 1 : command.index("--seeds")]
    seeds = command[
        command.index("--seeds") + 1 : command.index("--floor-families")
    ]
    assert bit_sizes == ["8", "10", "12"]
    assert seeds == ["3317584535", "2246822507"]
    assert OT.bound_source_hashes()["run_wrapper_sha256"] == OT.sha256_file(
        RUN_WRAPPER_PATH
    )
    with pytest.raises(FileExistsError):
        RUN_WRAPPER.run_development(tmp_path)


def toy_family(family: str, seed: int = 901):
    curve_record = OT.BASE.generate_clean_curve(8, seed)
    curve = OT.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = OT.BASE.point_from_json(curve_record["generator"])
    size = OT.BASE.choose_factor_base_size(curve_record["q"], 0.5)
    factor_base = OT.BASE.make_factor_base(
        family,
        curve,
        curve_record["q"],
        generator,
        size,
        seed ^ 0xA5A5,
    )
    points = [OT.BASE.point_from_json(value) for value in factor_base["points"]]
    d2 = OT.SOURCE.build_source_d2(curve, points, "symmetry_lex", 0)
    return curve_record, curve, factor_base, points, d2


def test_target_cardinality_record_fails_closed_when_support_is_short() -> None:
    exact = OT.target_cardinality_record(7, 9)
    assert exact == {
        "requested_count": 7,
        "available_count": 9,
        "realized_count": 7,
        "count_was_clamped": False,
        "cardinality_status": "EXACT",
        "cardinality_gate": True,
    }
    short = OT.target_cardinality_record(7, 3)
    assert short["realized_count"] == 3
    assert short["count_was_clamped"] is True
    assert short["cardinality_status"] == "INSUFFICIENT_SUPPORT"
    assert short["cardinality_gate"] is False


@pytest.mark.parametrize(
    "family", ["x_interval", "square_map", "rational_union", "random_x"]
)
def test_source_branches_reproduce_every_factor_x(family: str) -> None:
    _, curve, factor_base, _, _ = toy_family(family)
    branches = OT.extract_source_branches(factor_base, curve)
    emitted = []
    for branch in branches:
        for root, expected in zip(branch["source_roots"], branch["x_values"]):
            actual = OT.map_source_value(
                branch["map_kind"], root, branch["params"], curve.p
            )
            assert actual == expected
            emitted.append(expected)
    expected_x = {
        OT.BASE.point_from_json(fiber["points"][0])[0]
        for fiber in factor_base["fibers"]
    }
    assert set(emitted) == expected_x
    assert len(emitted) == len(set(emitted))


def test_brute_s4_roots_recover_exact_five_leaf_witnesses() -> None:
    _, curve, _, points, d2 = toy_family("square_map", seed=977)
    target = None
    for point in points[:5]:
        target = curve.add(target, point)
    brute = OT.brute_s4_compatibility(curve, target, points, d2)
    assert brute["roots"] or brute["identity_route"] is not None
    recovered = OT.recover_s4_roots(
        curve,
        target,
        points,
        d2,
        brute["roots"],
        stop_after_first=False,
    )
    assert recovered["success"]
    assert recovered["all_requested_roots_recovered"]
    for row in recovered["recovered_roots"]:
        assert row["witness"] is not None
        verified, _ = OT.verify_factor_witness(
            curve, points, row["witness"], target
        )
        assert verified


def test_all_root_recovery_preserves_coexisting_identity_route() -> None:
    curve_record, curve, _, points, d2 = toy_family("x_interval", seed=983)
    generator = OT.BASE.point_from_json(curve_record["generator"])
    target = None
    brute = None
    for scalar in range(1, curve_record["q"]):
        candidate = curve.mul(scalar, generator)
        candidate_brute = OT.brute_s4_compatibility(curve, candidate, points, d2)
        if candidate_brute["roots"] and candidate_brute["identity_route"] is not None:
            target = candidate
            brute = candidate_brute
            break
    assert target is not None and brute is not None
    recovered = OT.recover_s4_roots(
        curve,
        target,
        points,
        d2,
        brute["roots"],
        stop_after_first=False,
    )
    assert recovered["all_requested_roots_recovered"]
    assert recovered["identity"] is not None
    verified, _ = OT.verify_factor_witness(
        curve, points, recovered["identity"]["witness"], target
    )
    assert verified


def test_s3_brute_roots_match_exact_complement_routes() -> None:
    _, curve, _, _, d2 = toy_family("x_interval", seed=991)
    nonidentity = [point for point in d2.points if point is not None]
    target = curve.add(nonidentity[0], nonidentity[1])
    result = OT.brute_s3_compatibility(curve, target, d2)
    assert result["roots"] or result["identity_pair"] is not None
    for pair in result["root_pairs"].values():
        left, right = pair
        recovered = curve.add(d2.points[left], d2.points[right])
        assert recovered == target


def test_authorization_separates_development_and_frozen_configs() -> None:
    development = dict(OT.FROZEN_CONFIG)
    development["bit_sizes"] = [8, 10, 12]
    assert OT.enforce_authorization(development, True, False) is False
    with pytest.raises(ValueError):
        OT.enforce_authorization(development, False, False)
    with pytest.raises(ValueError):
        OT.enforce_authorization(development, False, True)
    assert OT.enforce_authorization(OT.FROZEN_CONFIG, False, True) is True
    with pytest.raises(ValueError):
        OT.enforce_authorization(OT.FROZEN_CONFIG, True, False)


def test_curve_schedule_preflight_is_unique_and_rejects_collisions() -> None:
    config = {
        "bit_sizes": [8, 10, 12],
        "seeds": [3317584535, 2246822507],
    }
    scheduled = OT.preflight_curve_schedule(config)
    assert [row["curve"]["p"] for row in scheduled] == [
        251,
        239,
        991,
        983,
        4079,
        3931,
    ]
    assert len({row["curve"]["p"] for row in scheduled}) == len(scheduled)
    assert all(
        row["curve"]["embedding_degree"]
        > OT.MOV_EMBEDDING_DEGREE_THRESHOLD
        for row in scheduled
    )
    with pytest.raises(AssertionError, match="repeated field modulus"):
        OT.preflight_curve_schedule(
            {"bit_sizes": [8], "seeds": [3317584535, 967613517]}
        )


def test_partial_fraction_parser_reduces_and_rejects_duplicates() -> None:
    assert OT.parse_fraction_pairs([1, 2], [8, 4]) == [[1, 8], [1, 2]]
    with pytest.raises(ValueError):
        OT.parse_fraction_pairs([1, 2], [2, 4])
    with pytest.raises(ValueError):
        OT.parse_fraction_pairs([1], [1])


def test_s3_control_includes_the_d2_identity_edge() -> None:
    curve_record = OT.BASE.generate_clean_curve(8, 3317584535 + 8 * 1009)
    assert curve_record["p"] == 251 and curve_record["q"] == 227
    curve = OT.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = OT.BASE.point_from_json(curve_record["generator"])
    factor_points = [generator, curve.neg(generator)]
    d2 = OT.SOURCE.build_source_d2(
        curve, factor_points, "symmetry_lex", 0
    )
    target = curve.add(generator, generator)
    assert target is not None
    roots = list(OT.d2_x_orbits(d2))
    assert roots == [target[0]]
    polynomial = OT.load_polynomial_engine()
    relation = polynomial.build_f3_fixed_x(
        curve.p, curve.a, curve.b, target[0]
    )
    m2 = polynomial.build_m2(roots, curve.p)
    finite = polynomial.s3_root_product_mod_m2(
        relation, roots, m2=m2
    )
    _, finite_roots = polynomial.gcd_roots_against_m2(
        finite, m2, roots, curve.p
    )
    corrected = polynomial.s3_identity_corrected_root_product_mod_m2(
        relation, target[0], roots, m2=m2
    )
    _, corrected_roots = polynomial.gcd_roots_against_m2(
        corrected, m2, roots, curve.p
    )
    brute = OT.brute_s3_compatibility(curve, target, d2)
    assert finite_roots == ()
    assert list(corrected_roots) == brute["roots"] == roots


def test_s3_identity_target_control_covers_every_orbit_and_sentinel() -> None:
    _, curve, _, points, d2 = toy_family("x_interval", seed=997)
    control = OT.s3_identity_target_control(curve, points, d2)
    expected_roots = sorted(OT.d2_x_orbits(d2))
    assert control["functional_gate"]
    assert control["polynomial_input_defined"] is False
    assert control["polynomial_roots_by_identity_branch"] == expected_roots
    assert control["identity_sentinel"] is not None
    for row in control["recovered_finite_roots"]:
        assert OT.verify_factor_witness(curve, points, row["witness"], None)[0]
    assert OT.verify_factor_witness(
        curve,
        points,
        control["identity_sentinel"]["witness"],
        None,
    )[0]


def test_direct_scalar_resultant_matches_symbolic_f4_on_identical_tuples() -> None:
    _, curve, _, points, d2 = toy_family("x_interval", seed=1001)
    polynomial = OT.load_polynomial_engine()
    target = curve.add(points[0], points[2])
    assert target is not None
    f4 = polynomial.build_f4_fixed_x(
        curve.p,
        curve.a,
        curve.b,
        target[0],
    )
    factor_roots = sorted({point[0] for point in points})[:2]
    d2_roots = list(OT.d2_x_orbits(d2))[:3]
    for factor_x in factor_roots:
        for left_x in d2_roots:
            for right_x in d2_roots:
                counter = polynomial.OperationCounter()
                left = OT.scalar_f3_coefficients_in_z(
                    polynomial,
                    curve.p,
                    curve.a,
                    curve.b,
                    factor_x,
                    left_x,
                    counter,
                )
                right = OT.scalar_f3_coefficients_in_z(
                    polynomial,
                    curve.p,
                    curve.a,
                    curve.b,
                    right_x,
                    target[0],
                    counter,
                )
                direct = OT.scalar_quadratic_resultant(
                    polynomial,
                    curve.p,
                    left,
                    right,
                    counter,
                )
                symbolic = (
                    f4.evaluate_one_variable(0, factor_x)
                    .evaluate_one_variable(0, left_x)
                    .evaluate_one_variable(0, right_x)
                    .coefficient(())
                )
                assert direct == symbolic
                assert counter.coefficient_multiplications > 0
    direct_roots = OT.direct_scalar_f4_tuple_roots(
        polynomial,
        curve.p,
        curve.a,
        curve.b,
        target[0],
        factor_roots,
        d2_roots,
        False,
    )
    symbolic_roots = OT.direct_f4_tuple_roots(
        polynomial,
        f4,
        factor_roots,
        d2_roots,
        False,
    )
    assert direct_roots["roots"] == symbolic_roots["roots"]
    assert direct_roots["tuple_tests"] == symbolic_roots["tuple_tests"]
    assert direct_roots["left_cache_entries"] == len(factor_roots) * len(d2_roots)
    assert direct_roots["right_cache_entries"] == len(d2_roots)
    assert (
        direct_roots["operations"]["coefficient_multiplications"]
        < 24 * direct_roots["tuple_tests"]
    )


def test_symmetry_compressed_d3_matches_full_point_queries() -> None:
    curve_record, curve, _, points, d2 = toy_family("x_interval", seed=1009)
    floor = OT.load_exact_floor()
    d3 = floor.build_d3(curve, points, d2, OT.Ops)
    codec = OT.build_symmetry_d3_codec(curve, points, d3)
    generator = OT.BASE.point_from_json(curve_record["generator"])
    for scalar in range(1, min(curve_record["q"], 32)):
        target = curve.mul(scalar, generator)
        full = floor.query_d2_d3(
            curve, target, points, d2, d3, OT.Ops
        )
        compressed = OT.query_symmetry_d3(
            curve, target, points, d2, codec
        )
        assert compressed["success"] == full["success"]
        if compressed["success"]:
            verified, _ = OT.verify_factor_witness(
                curve, points, compressed["witness"], target
            )
            assert verified
    full_record = OT.serialize_d3(d3, curve, len(points))
    assert codec.record["logical_advice_bits"] < full_record["logical_advice_bits"]


def test_reduced_integration_run_is_functional_and_nonpromoting() -> None:
    config = {
        "bit_sizes": [8],
        "seeds": [3317584535],
        "floor_families": ["x_interval", "random_x"],
        "translator_families": ["x_interval", "random_x"],
        "partial_d3_fractions": [[1, 2]],
        "batch_multipliers": [1, 256],
        "batch_replicates": 1,
        "coordinate_targets": 1,
        "occupancy_lambda": 0.5,
        "rho_trials": 1,
    }
    result = OT.run_experiment(config, False, bind_sources=False)
    assert result["development_only"] is True
    assert result["source_hashes"] == {}
    assert result["promotion_rows"] == []
    assert result["aggregate"]["translator_row_count"] == 2
    assert result["aggregate"]["verified_functional_translator_rows"] == 2
    matched_target_sets = []
    clamped_batches = []
    for row in result["instances"][0]["rows"]:
        assert row["translator"]["functional_gate"] is True
        matched_target_sets.append(
            [
                target["target"]
                for target in row["translator"]["matched_uniform_targets"]
            ]
        )
        assert {
            batch["target_count"]
            for batch in row["translator"]["amortized_projection"]["rows"]
        } == {1, result["instances"][0]["factor_base_size"], 16 * result["instances"][0]["factor_base_size"]}
        for target in row["translator"]["targets"]:
            gates = target["gates"]
            for weight in ("10", "50", "100"):
                assert gates["crossover_preprocessing_differential"][weight] == max(
                    0,
                    gates["translator_preprocessing_weighted_work"][weight]
                    - gates["comparator_d3_preprocessing_weighted_work"][weight],
                )
        for batch in row["floor"]["batches"]:
            comparison = batch["comparison"]
            if batch["count_was_clamped"]:
                clamped_batches.append(batch)
                assert comparison["cardinality_status"] == "INSUFFICIENT_SUPPORT"
                assert comparison["cardinality_gate"] is False
                assert comparison["practical_signal_gate"] is False
            assert comparison["multiplication_within_disclosed_tradeoff"]
            assert comparison["workspace_within_disclosed_tradeoff"]
            assert (
                comparison["peak_batch_workspace_logical_bytes"]
                <= comparison["batch_workspace_logical_upper_bound_bytes"]
            )
    assert matched_target_sets[0] == matched_target_sets[1]
    assert clamped_batches


def test_replay_comparison_strips_only_validated_wall_clock_fields() -> None:
    left = {
        "generated_at_utc": "2026-07-17T00:00:00+00:00",
        "payload": [{"wall_seconds": 0.1, "stable": 7}],
        "candidate_wall_seconds": 0.2,
    }
    right = {
        "generated_at_utc": "2026-07-17T00:00:01+00:00",
        "payload": [{"wall_seconds": 9.5, "stable": 7}],
        "candidate_wall_seconds": 4.0,
    }
    VERIFY.validate_replay_volatiles(left)
    VERIFY.validate_replay_volatiles(right)
    VERIFY.compare_exact(
        VERIFY.strip_replay_volatiles(left),
        VERIFY.strip_replay_volatiles(right),
    )
    with pytest.raises(AssertionError):
        VERIFY.validate_replay_volatiles({"wall_time_seconds": -1.0})
    with pytest.raises(AssertionError):
        VERIFY.compare_exact(
            VERIFY.strip_replay_volatiles(left),
            VERIFY.strip_replay_volatiles({**right, "payload": [{"stable": 8}]}),
        )


def test_independent_verifier_replays_floor_only_rows_and_rejects_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = {
        "bit_sizes": [8],
        "seeds": [3317584535],
        "floor_families": ["x_interval", "random_x"],
        "translator_families": ["random_x"],
        "partial_d3_fractions": [[1, 2]],
        "batch_multipliers": [1],
        "batch_replicates": 1,
        "coordinate_targets": 1,
        "occupancy_lambda": 0.5,
        "rho_trials": 1,
    }
    document = VERIFY.GENERATOR.run_experiment(config, False, bind_sources=False)
    monkeypatch.setattr(VERIFY.GENERATOR, "bound_source_hashes", lambda: {})
    counts = VERIFY.verify_artifact(document, allow_development=True)
    assert counts["instances"] == 1
    assert counts["families"] == 2
    assert document["instances"][0]["rows"][0]["translator"] is None

    mutations = []

    factor_mutation = copy.deepcopy(document)
    factor_mutation["instances"][0]["rows"][0]["factor_base"]["points"][0][0] ^= 1
    mutations.append(factor_mutation)

    source_mutation = copy.deepcopy(document)
    source_mutation["instances"][0]["rows"][1]["translator"]["preprocessing"][
        "branches"
    ][0]["source_roots"][0] ^= 1
    mutations.append(source_mutation)

    target_mutation = copy.deepcopy(document)
    target_mutation["instances"][0]["rows"][1]["translator"][
        "matched_uniform_targets"
    ][0]["target"][0] ^= 1
    mutations.append(target_mutation)

    root_mutation = copy.deepcopy(document)
    root_mutation["instances"][0]["rows"][1]["translator"]["targets"][0][
        "polynomial_s4_roots"
    ].append(0)
    mutations.append(root_mutation)

    operation_mutation = copy.deepcopy(document)
    operation_mutation["instances"][0]["rows"][1]["translator"]["targets"][0][
        "candidate_total_field_vector"
    ]["field_multiplications"] += 1
    mutations.append(operation_mutation)

    direct_comparator_mutation = copy.deepcopy(document)
    direct_comparator_mutation["instances"][0]["rows"][1]["translator"][
        "targets"
    ][0]["direct_scalar_f4_full_root_set"]["tuple_tests"] += 1
    mutations.append(direct_comparator_mutation)

    cardinality_mutation = copy.deepcopy(document)
    cardinality_mutation["instances"][0]["rows"][1]["translator"][
        "coordinate_target_cardinality"
    ]["cardinality_gate"] = False
    mutations.append(cardinality_mutation)

    functional_conjunction_mutation = copy.deepcopy(document)
    functional_conjunction_mutation["instances"][0]["rows"][1]["translator"][
        "functional_gate"
    ] = False
    mutations.append(functional_conjunction_mutation)

    trend_mutation = copy.deepcopy(document)
    trend_mutation["aggregate"]["trend_gates"][0]["trend_gate"] = True
    mutations.append(trend_mutation)

    advice_mutation = copy.deepcopy(document)
    advice_mutation["instances"][0]["rows"][1]["translator"]["preprocessing"][
        "incremental_logical_bits"
    ] += 1
    mutations.append(advice_mutation)

    witness_mutation = copy.deepcopy(document)
    witness = witness_mutation["instances"][0]["rows"][1]["translator"][
        "targets"
    ][0]["exact_d2_d3_query"]["witness"]
    witness[0] ^= 1
    mutations.append(witness_mutation)

    for mutated in mutations:
        with pytest.raises(AssertionError):
            VERIFY.verify_artifact(mutated, allow_development=True)
