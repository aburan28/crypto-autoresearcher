"""Small, deterministic learners for the bounded solver-selection benchmark.

The checkpoint format deliberately contains only JSON scalars, lists, and
objects.  It is an interchange format, not a serialized Python object.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


_SCHEMA_VERSION = 1
_RIDGE_LAMBDA = 1.0
_BANDIT_LEARNING_RATE = 0.05
_MAX_STEPS = 5000
_SEED_LIMIT = 2**32


def _is_int(value: Any) -> bool:
    return type(value) is int


def _finite_number(value: Any, name: str) -> float:
    if type(value) not in (int, float) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _finite_array(value: Any, name: str, *, ndim: int | None = None) -> np.ndarray:
    """Convert a numeric value to a finite float array without accepting objects."""
    if isinstance(value, np.ndarray) and value.dtype.kind not in "iuf":
        raise ValueError(f"{name} must have a numeric dtype")
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a rectangular numeric array") from error
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"{name} must be {ndim}-dimensional")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain only finite values")
    return array


def _training_inputs(features: np.ndarray, costs: np.ndarray, seed: int, steps: int) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(features, np.ndarray) or not isinstance(costs, np.ndarray):
        raise ValueError("features and costs must be numpy arrays")
    x = _finite_array(features, "features", ndim=2)
    c = _finite_array(costs, "costs", ndim=2)
    if x.shape[0] < 1 or x.shape[1] < 1:
        raise ValueError("features must have at least one row and one column")
    if c.shape[0] != x.shape[0] or c.shape[1] < 1:
        raise ValueError("costs must have matching rows and at least one action")
    if (c <= 0).any():
        raise ValueError("costs must be strictly positive")
    if not _is_int(seed) or not 0 <= seed < _SEED_LIMIT:
        raise ValueError("seed must be an unsigned 32-bit integer")
    if not _is_int(steps) or not 1 <= steps <= _MAX_STEPS:
        raise ValueError(f"steps must be an integer from 1 to {_MAX_STEPS}")
    return x, c


def _scale_training_features(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    # A constant feature has no training variation.  Giving it scale one keeps
    # the representation finite and prevents test rows from influencing scale.
    std = np.where(std == 0.0, 1.0, std)
    scaled = (x - mean) / std
    return scaled, mean, std


def _augment(x: np.ndarray) -> np.ndarray:
    return np.column_stack((np.ones(x.shape[0]), x))


def _softmax(logits: np.ndarray) -> np.ndarray:
    bounded = np.clip(logits, -40.0, 40.0)
    shifted = bounded - bounded.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def train(features: np.ndarray, costs: np.ndarray, *, seed: int = 0, steps: int = 1200) -> dict[str, Any]:
    """Fit ridge log-cost predictions and a one-step offline bandit policy.

    Normalization is fitted solely from ``features`` passed here.  The bandit
    observes the complete measured table, but each update samples one action
    per row and uses its row-centred, row-normalized log-cost reward.
    """
    x, c = _training_inputs(features, costs, seed, steps)
    scaled, mean, std = _scale_training_features(x)
    design = _augment(scaled)
    log_costs = np.log(c)
    action_count = c.shape[1]

    regularization = _RIDGE_LAMBDA * np.eye(design.shape[1])
    regularization[0, 0] = 0.0  # The augmented bias is deliberately unpenalized.
    gram = design.T @ design + regularization
    ridge_weights = np.linalg.solve(gram, design.T @ log_costs)

    # A zero reward for constant rows is intentional: it makes the null
    # control detect accidental policy movement or reward-sign mistakes.
    row_mean = log_costs.mean(axis=1, keepdims=True)
    row_std = log_costs.std(axis=1, keepdims=True)
    constant_rows = np.ptp(log_costs, axis=1, keepdims=True) == 0.0
    rewards = np.divide(row_mean - log_costs, row_std,
                        out=np.zeros_like(log_costs), where=(~constant_rows) & (row_std > 0.0))
    rng = np.random.default_rng(seed)
    bandit_weights = np.zeros((design.shape[1], action_count), dtype=float)
    row_indexes = np.arange(design.shape[0])
    for _ in range(steps):
        probabilities = _softmax(design @ bandit_weights)
        sampled = (rng.random(design.shape[0])[:, None] > np.cumsum(probabilities, axis=1)).sum(axis=1)
        sampled = np.minimum(sampled, action_count - 1)
        advantage = rewards[row_indexes, sampled]
        one_hot = np.zeros_like(probabilities)
        one_hot[row_indexes, sampled] = 1.0
        gradient = design.T @ ((one_hot - probabilities) * advantage[:, None]) / design.shape[0]
        bandit_weights += _BANDIT_LEARNING_RATE * gradient
        # This is a numerical guard, not a tuned regularizer.
        np.clip(bandit_weights, -100.0, 100.0, out=bandit_weights)

    return {
        "schema_version": _SCHEMA_VERSION,
        "kind": "polynomial_solver_ml_checkpoint",
        "feature_count": int(x.shape[1]),
        "action_count": int(action_count),
        "normalization": {"mean": mean.tolist(), "std": std.tolist()},
        "ridge": {"lambda": _RIDGE_LAMBDA, "weights": ridge_weights.tolist()},
        "bandit": {"learning_rate": _BANDIT_LEARNING_RATE, "steps": steps,
                   "weights": bandit_weights.tolist()},
    }


def _checkpoint_arrays(checkpoint: Any) -> tuple[int, int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not isinstance(checkpoint, dict):
        raise ValueError("checkpoint must be a JSON object")
    if (not _is_int(checkpoint.get("schema_version")) or checkpoint.get("schema_version") != _SCHEMA_VERSION
            or checkpoint.get("kind") != "polynomial_solver_ml_checkpoint"):
        raise ValueError("unsupported checkpoint schema")
    dimensions = (checkpoint.get("feature_count"), checkpoint.get("action_count"))
    if not all(_is_int(value) and value >= 1 for value in dimensions):
        raise ValueError("checkpoint dimensions must be positive integers")
    feature_count, action_count = dimensions
    normalization, ridge, bandit = checkpoint.get("normalization"), checkpoint.get("ridge"), checkpoint.get("bandit")
    if not all(isinstance(value, dict) for value in (normalization, ridge, bandit)):
        raise ValueError("checkpoint model sections must be objects")
    if _finite_number(ridge.get("lambda"), "checkpoint ridge lambda") != _RIDGE_LAMBDA:
        raise ValueError("checkpoint ridge lambda is unsupported")
    if _finite_number(bandit.get("learning_rate"), "checkpoint bandit learning rate") != _BANDIT_LEARNING_RATE:
        raise ValueError("checkpoint bandit learning rate is unsupported")
    if not _is_int(bandit.get("steps")) or not 1 <= bandit["steps"] <= _MAX_STEPS:
        raise ValueError("checkpoint bandit steps are invalid")
    mean = _finite_array(normalization.get("mean"), "checkpoint normalization mean", ndim=1)
    std = _finite_array(normalization.get("std"), "checkpoint normalization std", ndim=1)
    ridge_weights = _finite_array(ridge.get("weights"), "checkpoint ridge weights", ndim=2)
    bandit_weights = _finite_array(bandit.get("weights"), "checkpoint bandit weights", ndim=2)
    if mean.shape != (feature_count,) or std.shape != (feature_count,) or (std <= 0).any():
        raise ValueError("checkpoint normalization dimensions or scales are invalid")
    expected_weights = (feature_count + 1, action_count)
    if ridge_weights.shape != expected_weights or bandit_weights.shape != expected_weights:
        raise ValueError("checkpoint weight dimensions are invalid")
    return feature_count, action_count, mean, std, ridge_weights, bandit_weights


def select(checkpoint: dict[str, Any], features: np.ndarray) -> dict[str, np.ndarray]:
    """Return deployable greedy action IDs from a plain-JSON checkpoint."""
    feature_count, action_count, mean, std, ridge_weights, bandit_weights = _checkpoint_arrays(checkpoint)
    if not isinstance(features, np.ndarray):
        raise ValueError("features must be a numpy array")
    x = _finite_array(features, "features", ndim=2)
    if x.shape[0] < 1 or x.shape[1] != feature_count:
        raise ValueError("features do not match checkpoint dimensions")
    design = _augment((x - mean) / std)
    ridge_actions = np.argmin(design @ ridge_weights, axis=1).astype(int)
    bandit_actions = np.argmax(design @ bandit_weights, axis=1).astype(int)
    if (ridge_actions >= action_count).any() or (bandit_actions >= action_count).any():
        raise ValueError("checkpoint produced an invalid action")
    return {"ridge": ridge_actions, "bandit": bandit_actions}


def controls(*, seed: int = 0) -> dict[str, Any]:
    """Run deterministic positive and constant-reward learner controls."""
    if not _is_int(seed) or not 0 <= seed < _SEED_LIMIT:
        raise ValueError("seed must be an unsigned 32-bit integer")
    signs = np.tile(np.array([-1.0, 1.0]), 32)
    positive_features = np.column_stack((signs, np.ones_like(signs)))
    positive_costs = np.column_stack((np.where(signs > 0.0, 1.0, 8.0),
                                      np.where(signs > 0.0, 8.0, 1.0)))
    positive_model = train(positive_features, positive_costs, seed=seed, steps=1200)
    positive_choices = select(positive_model, positive_features)
    expected = (signs < 0.0).astype(int)
    ridge_accuracy = float(np.mean(positive_choices["ridge"] == expected))
    bandit_accuracy = float(np.mean(positive_choices["bandit"] == expected))

    constant_features = np.column_stack((np.linspace(-2.0, 2.0, 32), np.ones(32)))
    constant_costs = np.full((32, 3), 3.5)
    constant_model = train(constant_features, constant_costs, seed=seed, steps=1200)
    constant_choices = select(constant_model, constant_features)
    constant_selected_cost = float(constant_costs[np.arange(32), constant_choices["bandit"]].mean())
    constant_improvement = float(3.5 - constant_selected_cost)
    constant_weights_max_abs = float(np.abs(np.asarray(constant_model["bandit"]["weights"])).max())
    return {
        "positive_passed": ridge_accuracy == 1.0 and bandit_accuracy == 1.0,
        "constant_passed": constant_improvement == 0.0 and constant_weights_max_abs == 0.0,
        "positive": {"ridge_accuracy": ridge_accuracy, "bandit_accuracy": bandit_accuracy,
                     "rows": int(len(signs))},
        "constant": {"selected_mean_cost": constant_selected_cost,
                     "improvement_over_fixed": constant_improvement,
                     "bandit_weights_max_abs": constant_weights_max_abs,
                     "rows": 32},
    }
