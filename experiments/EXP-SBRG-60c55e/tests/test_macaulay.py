from pathlib import Path
import importlib.util
import random
import sys

MODULE_PATH = Path(__file__).parents[1] / "driver" / "macaulay.py"
spec = importlib.util.spec_from_file_location("macaulay", MODULE_PATH)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
assert spec.loader is not None
spec.loader.exec_module(m)


def P(*masks):
    return frozenset(masks)


def test_boolean_multiplication_collapses_and_cancels():
    # (x0 + x0*x1) * x1 = x0*x1 + x0*x1 = 0 in the Boolean quotient.
    poly = P(0b001, 0b011)
    assert m.multiply_by_monomial(poly, 0b010) == frozenset()


def test_evaluate():
    poly = P(0, 0b001, 0b110)  # 1 + x0 + x1*x2
    assert m.evaluate(poly, 0b000) == 1
    assert m.evaluate(poly, 0b001) == 0
    assert m.evaluate(poly, 0b111) == 1


def test_gf2_rank():
    rows = [0b1000, 0b0100, 0b0010, 0b1000 ^ 0b0100]
    stats = m.gf2_rank(rows)
    assert stats.rank == 3
    assert stats.zero_rows == 1


def test_layer_detects_single_row_degree_fall_from_boolean_reduction():
    # f = x0*x1 + x0. At D=3, multiplier x0 makes the degree-3 projection vanish.
    f = P(0b011, 0b001)
    layer = m.analyze_layer([f], nvars=3, degree=3)
    assert layer.fall_dim >= 1
    assert layer.full_rank >= layer.top_rank


def test_exact_syzygy_is_counted():
    # Duplicate generators create one exact row dependency at their own degree.
    f = P(0b011, 0b001)
    layer = m.analyze_layer([f, f], nvars=2, degree=2)
    assert layer.syzygy_dim >= 1


def test_random_matched_system_preserves_histograms_and_plants_root():
    templates = [
        P(0, 0b001, 0b010, 0b101),
        P(0b011, 0b100, 0b111),
    ]
    planted = 0b101
    controls, meta = m.random_matched_system(
        templates, nvars=3, seed=1234, planted_assignment=planted
    )
    assert len(controls) == len(templates)
    assert all(m.evaluate(p, planted) == 0 for p in controls)
    if meta["degree_histogram_exact"]:
        for template, control in zip(templates, controls):
            assert m.degree_histogram(template) == m.degree_histogram(control)


def test_batch_reuse_matches_total_rank():
    fixed = [P(0b001, 0b010), P(0b100, 0)]
    targets = [
        [P(0b011, 0b101)],
        [P(0b110, 0b001)],
        [P(0b111, 0b010)],
    ]
    stats = m.analyze_batch_reuse(fixed, targets, nvars=3, degree=2)
    assert len(stats.targets) == 3
    for target, target_stats in zip(targets, stats.targets):
        cols = m.ColumnSpace.build(3, 2)
        all_rows = [cols.encode(p) for p in m.layer_rows(fixed + target, 3, 2)]
        expected = m.gf2_rank(all_rows).rank
        assert target_stats.total_rank == expected
        assert target_stats.rowspace_intersection_dim >= 0


def test_first_nonzero_fall():
    f = P(0b011, 0b001)
    layers = m.analyze_degrees([f], nvars=3, min_degree=2, max_degree=3)
    assert m.first_nonzero_fall(layers) == 3


def test_random_controls_are_deterministic_for_seed():
    templates = [P(0, 1, 2, 3), P(4, 5, 6)]
    a, ma = m.random_matched_system(templates, 3, seed=99, planted_assignment=0b101)
    b, mb = m.random_matched_system(templates, 3, seed=99, planted_assignment=0b101)
    assert a == b
    assert ma == mb
