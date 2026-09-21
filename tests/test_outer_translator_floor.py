from __future__ import annotations

import importlib.util
import inspect
import itertools
import sys
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FLOOR_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-OUTER-TRANSLATOR-001"
    / "src"
    / "exact_floor.py"
)
COMPRESSED_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-COMPRESSED-JOIN-001"
    / "src"
    / "compressed_join.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FLOOR = load_module("test_outer_translator_exact_floor", FLOOR_PATH)
HARNESS = load_module("test_outer_translator_compressed_harness", COMPRESSED_PATH)
BASE = HARNESS.BASE


@lru_cache(maxsize=None)
def clean_fixture(seed: int) -> SimpleNamespace:
    """Build a real repository D2 on a seeded generated clean toy curve."""

    curve_record = BASE.generate_clean_curve(8, seed)
    curve = BASE.Curve(
        curve_record["p"],
        curve_record["a"],
        curve_record["b"],
    )
    q = curve_record["q"]
    generator = tuple(curve_record["generator"])
    factor_record = BASE.make_factor_base(
        "random_x",
        curve,
        q,
        generator,
        8,
        seed ^ 0xA5A5_5A5A,
    )
    factors = [tuple(point) for point in factor_record["points"]]
    d2 = HARNESS.build_d2(curve, factors)
    d3 = FLOOR.build_d3(curve, factors, d2, BASE.Ops)
    d5 = FLOOR.build_d5_audit_support(curve, factors, d2, d3, BASE.Ops)
    return SimpleNamespace(
        record=curve_record,
        curve=curve,
        q=q,
        generator=generator,
        factors=factors,
        d2=d2,
        d3=d3,
        d5=d5,
    )


def add_leaves(curve: Any, factors: list[Any], witness: tuple[int, ...]) -> Any:
    total = None
    for index in witness:
        total = curve.add(total, factors[index])
    return total


def enumerate_group(curve: Any, q: int, generator: Any) -> list[Any]:
    points = []
    current = None
    for _ in range(q):
        points.append(current)
        current = curve.add(current, generator)
    assert current is None
    assert len(set(points)) == q
    return points


def test_public_integration_names_and_signatures_are_concise() -> None:
    expected = {
        "build_d3": ["curve", "factor_points", "d2", "ops_factory"],
        "build_d5_audit_support": [
            "curve",
            "factor_points",
            "d2",
            "d3",
            "ops_factory",
        ],
        "make_target_schedule": ["kind", "count", "seed"],
        "query_d2_d3": [
            "curve",
            "target",
            "factor_points",
            "d2",
            "d3",
            "ops_factory",
        ],
        "build_partial_d3": ["d3", "numerator", "denominator", "seed"],
        "query_partial_d3": [
            "curve",
            "target",
            "factor_points",
            "d2",
            "cache",
            "fallback",
            "ops_factory",
        ],
        "run_target_major_batch": [
            "curve",
            "targets",
            "factor_points",
            "d2",
            "d3",
            "ops_factory",
        ],
        "run_d2_major_batch": [
            "curve",
            "targets",
            "factor_points",
            "d2",
            "d3",
            "ops_factory",
        ],
    }
    for name, prefix in expected.items():
        assert name in FLOOR.__all__
        assert list(inspect.signature(getattr(FLOOR, name)).parameters)[: len(prefix)] == prefix


@pytest.mark.parametrize("seed", [3317584535, 967613517])
def test_exact_d3_matches_bruteforce_and_is_order_independent(seed: int) -> None:
    fixture = clean_fixture(seed)
    multiplicities: dict[Any, int] = {}
    witnesses: dict[Any, tuple[int, int, int]] = {}
    for d2_index, partial in enumerate(fixture.d2.points):
        for factor_index, factor in enumerate(fixture.factors):
            point = fixture.curve.add(partial, factor)
            candidate = tuple(
                sorted(fixture.d2.witnesses[d2_index] + (factor_index,))
            )
            multiplicities[point] = multiplicities.get(point, 0) + 1
            witnesses[point] = min(witnesses.get(point, candidate), candidate)

    assert fixture.d3.points == sorted(witnesses, key=FLOOR.point_sort_key)
    assert fixture.d3.point_to_witness == witnesses
    assert fixture.d3.multiplicities == [
        multiplicities[point] for point in fixture.d3.points
    ]
    assert fixture.d3.attempts == len(fixture.d2.points) * len(fixture.factors)
    assert fixture.d3.record["build_ops"]["group_operations"] == fixture.d3.attempts
    assert fixture.d3.record["collisions"] == fixture.d3.attempts - len(witnesses)
    assert fixture.d3.record["logical_advice_bytes"] == len(fixture.d3.points) * (
        FLOOR.logical_point_bytes(fixture.curve.p)
        + 3 * FLOOR.logical_factor_index_bytes(len(fixture.factors))
    )
    for point, witness in fixture.d3.point_to_witness.items():
        assert add_leaves(fixture.curve, fixture.factors, witness) == point

    reversed_d2 = SimpleNamespace(
        points=list(reversed(fixture.d2.points)),
        witnesses=list(reversed(fixture.d2.witnesses)),
        build_ops=BASE.Ops(),
    )
    replay = FLOOR.build_d3(
        fixture.curve,
        fixture.factors,
        reversed_d2,
        BASE.Ops,
    )
    assert replay.point_to_witness == fixture.d3.point_to_witness
    assert replay.multiplicities == fixture.d3.multiplicities
    assert replay.record["advice_digest"] == fixture.d3.record["advice_digest"]


@pytest.mark.parametrize("seed", [3317584535, 967613517])
def test_d5_audit_support_equals_independent_five_multiset_support(seed: int) -> None:
    fixture = clean_fixture(seed)
    brute_support = {
        add_leaves(fixture.curve, fixture.factors, witness)
        for witness in itertools.combinations_with_replacement(
            range(len(fixture.factors)),
            5,
        )
    }
    assert set(fixture.d5.points) == brute_support
    assert fixture.d5.attempts == len(fixture.d2.points) * len(fixture.d3.points)
    assert fixture.d5.record["build_ops"]["group_operations"] == fixture.d5.attempts
    assert fixture.d5.record["eligible_query_advice"] is False
    assert fixture.d5.record["support_digest"] == FLOOR.stable_digest(
        [FLOOR.point_json(point) for point in fixture.d5.points]
    )
    for point, witness in fixture.d5.point_to_witness.items():
        assert tuple(sorted(witness)) == witness
        assert add_leaves(fixture.curve, fixture.factors, witness) == point


def test_supported_and_uniform_schedules_are_replayable_point_only_records() -> None:
    fixture = clean_fixture(3317584535)
    supported = FLOOR.make_target_schedule(
        "supported",
        8,
        0x5151,
        d5_support=fixture.d5,
    )
    supported_replay = FLOOR.make_target_schedule(
        "supported",
        8,
        0x5151,
        d5_support=fixture.d5,
    )
    assert supported.points == supported_replay.points
    assert supported.record == supported_replay.record
    assert len(set(supported.points)) == 8
    assert all(point is not None and point in fixture.d5 for point in supported)
    assert supported.record["target_scalars_emitted"] is False
    assert supported.record["construction_witnesses_emitted"] is False

    uniform = FLOOR.make_target_schedule(
        "uniform",
        12,
        0x7171,
        curve=fixture.curve,
        q=fixture.q,
        generator=fixture.generator,
        ops_factory=BASE.Ops,
    )
    uniform_replay = FLOOR.make_target_schedule(
        "uniform",
        12,
        0x7171,
        curve=fixture.curve,
        q=fixture.q,
        generator=fixture.generator,
        ops_factory=BASE.Ops,
    )
    assert uniform.points == uniform_replay.points
    assert uniform.record == uniform_replay.record
    assert len(set(uniform.points)) == 12
    assert all(point is not None and fixture.curve.on_curve(point) for point in uniform)
    assert uniform.record["target_scalars_emitted"] is False
    assert uniform.record["target_scalar_hashes_emitted"] is False
    assert "scalars" not in uniform.record


def test_scalar_query_is_complete_for_every_group_point_and_segregates_audit() -> None:
    fixture = clean_fixture(3317584535)
    point_bytes = FLOOR.logical_point_bytes(fixture.curve.p)
    index_bytes = FLOOR.logical_factor_index_bytes(len(fixture.factors))
    for target in enumerate_group(fixture.curve, fixture.q, fixture.generator):
        result = FLOOR.query_d2_d3(
            fixture.curve,
            target,
            fixture.factors,
            fixture.d2,
            fixture.d3,
            BASE.Ops,
        )
        assert result["success"] == (target in fixture.d5)
        counters = result["counters"]
        assert counters["group_operations"] == counters["complement_tests"]
        assert counters["dictionary_probes"] == counters["complement_tests"]
        assert counters["d2_point_reads"] == counters["complement_tests"]
        assert counters["target_point_reads"] == counters["complement_tests"]
        assert counters["d3_key_reads"] == counters["complement_tests"]
        assert counters["point_reads"] == 3 * counters["complement_tests"]
        assert counters["logical_d2_point_bytes_read"] == (
            counters["d2_point_reads"] * point_bytes
        )
        assert counters["logical_target_point_bytes_read"] == (
            counters["target_point_reads"] * point_bytes
        )
        if result["success"]:
            assert len(result["witness"]) == 5
            assert add_leaves(
                fixture.curve,
                fixture.factors,
                tuple(result["witness"]),
            ) == target
            assert counters["d2_witness_reads"] == 1
            assert counters["d3_witness_reads"] == 1
            assert counters["logical_witness_bytes_read"] == 5 * index_bytes
            audit = result["witness_verification_audit"]
            assert audit["verified"] is True
            assert audit["counters"]["group_operations"] == 5
            assert counters["group_operations"] == result["operation_record"][
                "group_operations"
            ]
        else:
            assert counters["witness_reads"] == 0


def test_montgomery_batch_inverse_is_exact_and_rejects_zero() -> None:
    values = [2, 3, 5, 7, 11]
    result = FLOOR.montgomery_batch_inverse(values, 101)
    assert [value * inverse % 101 for value, inverse in zip(values, result["inverses"])] == [
        1
    ] * len(values)
    assert result["field_inversions"] == 1
    assert result["prefix_multiplications"] == len(values) - 1
    assert result["backward_multiplications"] == 2 * (len(values) - 1)
    assert result["field_multiplications"] == 3 * (len(values) - 1)
    assert FLOOR.montgomery_batch_inverse([], 101)["field_inversions"] == 0
    with pytest.raises(ZeroDivisionError):
        FLOOR.montgomery_batch_inverse([1, 0, 2], 101)


def test_batch_affine_subtraction_handles_identity_inverse_doubling_and_ordinary() -> None:
    fixture = clean_fixture(3317584535)
    group = enumerate_group(fixture.curve, fixture.q, fixture.generator)
    subtrahend = next(point for point in group if point is not None)
    ordinary = next(
        point
        for point in group
        if point is not None
        and point not in (subtrahend, fixture.curve.neg(subtrahend))
        and point[0] != subtrahend[0]
    )
    targets = [
        None,
        subtrahend,
        fixture.curve.neg(subtrahend),
        ordinary,
    ]
    result = FLOOR.batch_affine_subtract(
        fixture.curve,
        targets,
        subtrahend,
        BASE.Ops,
        verify_scalar=True,
    )
    assert result["points"] == [
        fixture.curve.add(target, fixture.curve.neg(subtrahend))
        for target in targets
    ]
    counters = result["counters"]
    assert counters["group_operations"] == len(targets)
    assert counters["identity_routes"] == 1
    assert counters["inverse_routes"] == 1
    assert counters["doubling_routes"] == 1
    assert counters["ordinary_routes"] == 1
    assert counters["batch_denominators"] == 2
    assert counters["field_inversions"] == 1
    assert counters["prefix_multiplications"] == 1
    assert counters["backward_multiplications"] == 2
    assert counters["peak_batch_pending_entries"] == 2
    assert counters["peak_batch_workspace_logical_bytes"] > 0
    assert result["scalar_equality_audit"]["exact"] is True

    identity_row = FLOOR.batch_affine_subtract(
        fixture.curve,
        targets,
        None,
        BASE.Ops,
        verify_scalar=True,
    )
    assert identity_row["points"] == targets
    assert identity_row["counters"]["identity_routes"] == len(targets)
    assert identity_row["counters"]["field_inversions"] == 0

    order_two_curve = BASE.Curve(17, 0, 16)
    order_two = (1, 0)
    assert order_two_curve.on_curve(order_two)
    order_two_result = FLOOR.batch_affine_subtract(
        order_two_curve,
        [order_two, None],
        order_two,
        BASE.Ops,
        verify_scalar=True,
    )
    assert order_two_result["points"] == [None, order_two]
    assert order_two_result["counters"]["inverse_routes"] == 1
    assert order_two_result["counters"]["field_inversions"] == 0


@pytest.mark.parametrize("seed", [3317584535, 967613517])
def test_d2_major_and_target_major_have_identical_solved_sets_and_exact_counts(
    seed: int,
) -> None:
    fixture = clean_fixture(seed)
    supported = FLOOR.make_target_schedule(
        "supported",
        10,
        seed ^ 0x1010,
        d5_support=fixture.d5,
    )
    uniform = FLOOR.make_target_schedule(
        "uniform",
        10,
        seed ^ 0x2020,
        curve=fixture.curve,
        q=fixture.q,
        generator=fixture.generator,
        ops_factory=BASE.Ops,
    )
    targets = list(supported) + list(uniform) + [None]
    target_major = FLOOR.run_target_major_batch(
        fixture.curve,
        targets,
        fixture.factors,
        fixture.d2,
        fixture.d3,
        BASE.Ops,
    )
    d2_major = FLOOR.run_d2_major_batch(
        fixture.curve,
        targets,
        fixture.factors,
        fixture.d2,
        fixture.d3,
        BASE.Ops,
        verify_affine=True,
    )
    assert d2_major["solved_indices"] == target_major["solved_indices"]
    assert [row["success"] for row in d2_major["per_target"]] == [
        row["success"] for row in target_major["per_target"]
    ]
    assert [row["witness"] for row in d2_major["per_target"]] == [
        row["witness"] for row in target_major["per_target"]
    ]
    assert d2_major["counters"]["dictionary_probes"] == target_major["counters"][
        "dictionary_probes"
    ]
    assert d2_major["counters"]["group_operations"] == d2_major["counters"][
        "dictionary_probes"
    ]
    assert d2_major["counters"]["d2_point_reads"] <= len(fixture.d2.points)
    assert d2_major["counters"]["d2_point_reads"] < target_major["counters"][
        "d2_point_reads"
    ]
    assert d2_major["counters"]["field_inversions"] <= target_major["counters"][
        "field_inversions"
    ]
    assert d2_major["counters"]["backward_multiplications"] == 2 * d2_major[
        "counters"
    ]["prefix_multiplications"]
    assert 0 < d2_major["counters"]["peak_batch_pending_entries"] <= len(targets)
    assert d2_major["counters"]["peak_batch_workspace_logical_bytes"] > 0
    assert d2_major["affine_equality_audit"]["exact"] is True
    assert d2_major["witness_verification_audit"]["verified"] is True
    for summary in (target_major, d2_major):
        multiplications = summary["counters"]["field_multiplications"]
        inversions = summary["counters"]["field_inversions"]
        assert summary["weighted_field_work"] == {
            "10": multiplications + 10 * inversions,
            "50": multiplications + 50 * inversions,
            "100": multiplications + 100 * inversions,
        }


def test_partial_d3_is_sha_ranked_and_miss_charges_cache_plus_complete_fallback() -> None:
    fixture = clean_fixture(3317584535)
    quarter = FLOOR.build_partial_d3(fixture.d3, 1, 4, 0xD3D3)
    quarter_replay = FLOOR.build_partial_d3(fixture.d3, 1, 4, 0xD3D3)
    assert quarter.points == quarter_replay.points
    assert quarter.witnesses == quarter_replay.witnesses
    assert quarter.record == quarter_replay.record
    assert len(quarter.points) == len(fixture.d3.points) // 4
    assert quarter.record["target_independent"] is True

    target = next(point for point in fixture.d5.points if point is not None)
    full_cache = FLOOR.build_partial_d3(fixture.d3, 1, 1, 0xD3D3)
    unexpected_fallback_calls = 0

    def unexpected_fallback(_: Any) -> dict[str, Any]:
        nonlocal unexpected_fallback_calls
        unexpected_fallback_calls += 1
        raise AssertionError("full D3 cache must not fall back for a supported target")

    cache_hit = FLOOR.query_partial_d3(
        fixture.curve,
        target,
        fixture.factors,
        fixture.d2,
        full_cache,
        unexpected_fallback,
        BASE.Ops,
    )
    assert cache_hit["success"] is True
    assert cache_hit["cache_hit"] is True
    assert cache_hit["fallback_used"] is False
    assert unexpected_fallback_calls == 0

    empty_cache = FLOOR.build_partial_d3(
        fixture.d3,
        1,
        len(fixture.d3.points) + 1,
        0xD3D3,
    )
    assert empty_cache.points == []
    fallback_calls = 0

    def complete_fallback(fallback_target: Any) -> dict[str, Any]:
        nonlocal fallback_calls
        fallback_calls += 1
        return FLOOR.query_d2_d3(
            fixture.curve,
            fallback_target,
            fixture.factors,
            fixture.d2,
            fixture.d3,
            BASE.Ops,
        )

    fallback_result = FLOOR.query_partial_d3(
        fixture.curve,
        target,
        fixture.factors,
        fixture.d2,
        empty_cache,
        complete_fallback,
        BASE.Ops,
    )
    assert fallback_calls == 1
    assert fallback_result["success"] is True
    assert fallback_result["cache_hit"] is False
    assert fallback_result["fallback_used"] is True
    assert fallback_result["source"] == "complete_fallback"
    for field in (
        "group_operations",
        "field_multiplications",
        "field_inversions",
        "dictionary_probes",
        "d2_point_reads",
        "target_point_reads",
        "logical_bytes_read",
    ):
        assert fallback_result["counters"][field] == (
            fallback_result["cache_stage"]["counters"][field]
            + fallback_result["fallback_stage"]["counters"][field]
        )
    assert fallback_result["cache_stage"]["counters"]["dictionary_probes"] == len(
        fixture.d2.points
    )
    assert fallback_result["witness_verification_audit"]["verified"] is True


def test_invalid_fallback_accounting_and_mutated_witnesses_are_rejected() -> None:
    fixture = clean_fixture(3317584535)
    target = next(point for point in fixture.d5.points if point is not None)
    empty_cache = FLOOR.build_partial_d3(
        fixture.d3,
        1,
        len(fixture.d3.points) + 1,
        9,
    )
    with pytest.raises(ValueError, match="success and counters"):
        FLOOR.query_partial_d3(
            fixture.curve,
            target,
            fixture.factors,
            fixture.d2,
            empty_cache,
            lambda _: {"success": False},
            BASE.Ops,
        )

    valid = FLOOR.query_d2_d3(
        fixture.curve,
        target,
        fixture.factors,
        fixture.d2,
        fixture.d3,
        BASE.Ops,
    )
    assert valid["success"]
    with pytest.raises(ValueError, match="out of factor-base range"):
        FLOOR.verify_five_leaf_witness(
            fixture.curve,
            fixture.factors,
            list(valid["witness"][:-1]) + [len(fixture.factors)],
            target,
            BASE.Ops,
        )


def test_weighted_work_validates_weights_and_uses_only_m_plus_w_i() -> None:
    operations = {
        "field_multiplications": 123,
        "field_inversions": 7,
        "field_additions": 9999,
    }
    assert FLOOR.weighted_field_work(operations) == {
        "10": 193,
        "50": 473,
        "100": 823,
    }
    with pytest.raises(ValueError, match="distinct"):
        FLOOR.weighted_field_work(operations, [10, 10])
