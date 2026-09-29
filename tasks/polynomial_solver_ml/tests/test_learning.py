import json

import numpy as np
import pytest

from polynomial_ml import learning


def _positive_fixture():
    sign = np.tile(np.array([-1.0, 1.0]), 24)
    features = np.column_stack((sign, np.ones_like(sign)))
    costs = np.column_stack((np.where(sign > 0.0, 1.0, 9.0),
                             np.where(sign > 0.0, 9.0, 1.0)))
    return features, costs, (sign < 0.0).astype(int)


def test_positive_control_learns_sign_dependent_action():
    features, costs, expected = _positive_fixture()
    checkpoint = learning.train(features, costs, seed=19)
    selections = learning.select(checkpoint, features)
    assert np.array_equal(selections["ridge"], expected)
    assert np.array_equal(selections["bandit"], expected)
    report = learning.controls(seed=19)
    assert report["positive_passed"] is True
    assert report["positive"]["ridge_accuracy"] == 1.0
    assert report["positive"]["bandit_accuracy"] == 1.0


def test_constant_cost_null_has_no_artificial_improvement():
    features = np.column_stack((np.arange(24, dtype=float), np.ones(24)))
    costs = np.full((24, 3), 2.0)
    checkpoint = learning.train(features, costs, seed=4)
    assert np.asarray(checkpoint["bandit"]["weights"]).max() == 0.0
    assert np.asarray(checkpoint["bandit"]["weights"]).min() == 0.0
    report = learning.controls(seed=4)
    assert report["constant_passed"] is True
    assert report["constant"]["improvement_over_fixed"] == 0.0


def test_unpenalized_ridge_bias_fits_constant_action_log_costs_at_any_row_count():
    expected_intercept = np.log(np.array([2.0, 5.0, 11.0]))
    for row_count in (3, 19):
        features = np.linspace(-3.0, 4.0, row_count)[:, None]
        costs = np.tile(np.exp(expected_intercept), (row_count, 1))
        checkpoint = learning.train(features, costs, seed=11)
        weights = np.asarray(checkpoint["ridge"]["weights"])
        np.testing.assert_allclose(weights[0], expected_intercept, rtol=0.0, atol=1e-12)
        np.testing.assert_allclose(weights[1], 0.0, rtol=0.0, atol=1e-12)


def test_json_replay_and_train_only_normalization():
    features, costs, _ = _positive_fixture()
    training_rows = np.arange(0, len(features), 2)
    checkpoint = learning.train(features[training_rows], costs[training_rows], seed=7)
    replay = json.loads(json.dumps(checkpoint, allow_nan=False))
    expected_mean = features[training_rows].mean(axis=0)
    expected_std = features[training_rows].std(axis=0)
    expected_std[expected_std == 0.0] = 1.0
    assert checkpoint["normalization"]["mean"] == expected_mean.tolist()
    assert checkpoint["normalization"]["std"] == expected_std.tolist()
    first = learning.select(checkpoint, features)
    second = learning.select(replay, features)
    assert np.array_equal(first["ridge"], second["ridge"])
    assert np.array_equal(first["bandit"], second["bandit"])


@pytest.mark.parametrize(
    "features,costs",
    [
        ([[1.0]], np.ones((1, 1))),
        (np.ones((1, 1)), [[1.0]]),
        (np.ones((2, 1)), np.ones((1, 1))),
        (np.ones((1, 1)), np.array([[0.0]])),
        (np.array([[np.nan]]), np.ones((1, 1))),
    ],
)
def test_train_rejects_invalid_inputs(features, costs):
    with pytest.raises(ValueError):
        learning.train(features, costs)


def test_select_rejects_invalid_checkpoint_and_features():
    features, costs, _ = _positive_fixture()
    checkpoint = learning.train(features, costs, seed=2)
    with pytest.raises(ValueError):
        learning.select(checkpoint, [[1.0, 1.0]])
    with pytest.raises(ValueError):
        learning.select(checkpoint, np.ones((1, 3)))
    checkpoint["normalization"]["std"][0] = 0.0
    with pytest.raises(ValueError):
        learning.select(checkpoint, np.ones((1, 2)))
    checkpoint = learning.train(features, costs, seed=2)
    checkpoint["bandit"]["learning_rate"] = 1.0
    with pytest.raises(ValueError):
        learning.select(checkpoint, np.ones((1, 2)))
