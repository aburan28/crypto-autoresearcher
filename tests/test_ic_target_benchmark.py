"""Synthetic estimator controls; these data are not research observations."""

import itertools
import json

import pytest

from tools.ic_target_benchmark import CONFIG, add, mul, summarize
from crypto_autoresearcher.index_calculus import Curve


def synthetic_rows(ratio):
    config = json.loads(CONFIG.read_text())
    rows = []
    grid = itertools.product(config["bits"], config["curve_seeds"], config["solver_seeds"],
                             range(config["repetitions"]), config["arms"])
    for bits, curve, seed, repetition, arm in grid:
        rows.append(dict(bits=bits, curve_seed=curve, pair=f"{bits}:{curve}:{seed}:{repetition}",
                         arm=arm, status="completed", result={"verified": True},
                         seconds_full_solve=1 / ratio if arm == "fixed_window" else 1))
    return dict(config=config, rows=rows)


@pytest.mark.parametrize("ratio,passes", [(2, True), (1, False), (0.5, False), (1.04, False)])
def test_frozen_estimator_and_known_false_controls(ratio, passes):
    summary = summarize(synthetic_rows(ratio))
    assert summary["matched_pairs"] == 54
    assert summary["geometric_mean_speedup"] == pytest.approx(ratio)
    assert summary["clustered_bootstrap_95_interval"] == pytest.approx([ratio, ratio])
    assert summary["aa_factor"] == 1
    assert summary["protocol_criterion_met"] is passes


def test_censoring_never_becomes_a_successful_only_summary():
    raw = synthetic_rows(2)
    raw["rows"][0]["status"] = "timed_out"
    with pytest.raises(ValueError, match="unqualified"):
        summarize(raw)


def test_independent_arithmetic_including_identity_and_two_torsion():
    E = Curve(97, 2, 3)
    points = [None] + [(x, y) for x in range(97) for y in range(97) if E.is_on_curve((x, y))]
    for P in points:
        for k in [0, 1, 2, 15, 96, 100]:
            assert mul(k, P, 97, 2) == E.mul(k, P)
        for Q in [None, P, E.neg(P), (3, 6)]:
            assert add(P, Q, 97, 2) == E.add(P, Q)
