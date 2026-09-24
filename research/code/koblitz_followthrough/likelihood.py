"""Calibration/accounting utilities for decomposition-likelihood experiments.

Predictions may rank solver attempts.  They must not be used as a hard rejection
filter unless the experiment's frozen validation gate permits it.
"""
from __future__ import annotations
import math
from typing import Iterable, Sequence


def brier_score(y: Sequence[int], p: Sequence[float]) -> float:
    _check(y, p)
    return sum((float(a) - b) ** 2 for a, b in zip(y, p)) / len(y)


def log_loss(y: Sequence[int], p: Sequence[float], eps: float = 1e-12) -> float:
    _check(y, p)
    total = 0.0
    for a, b in zip(y, p):
        q = min(1.0 - eps, max(eps, b))
        total -= a * math.log(q) + (1 - a) * math.log(1 - q)
    return total / len(y)


def calibration_error(y: Sequence[int], p: Sequence[float], bins: int = 10) -> float:
    _check(y, p)
    if bins <= 0:
        raise ValueError("bins must be positive")
    groups = [[] for _ in range(bins)]
    for a, q in zip(y, p):
        idx = min(bins - 1, int(q * bins))
        groups[idx].append((a, q))
    n = len(y)
    return sum(
        len(g) / n * abs(sum(a for a, _ in g) / len(g) - sum(q for _, q in g) / len(g))
        for g in groups if g
    )


def threshold_accounting(y: Sequence[int], p: Sequence[float], threshold: float) -> dict:
    """Report the safety-critical cost of rejecting candidates below threshold."""
    _check(y, p)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [0,1]")
    rejected = [i for i, q in enumerate(p) if q < threshold]
    false_negatives = sum(1 for i in rejected if y[i] == 1)
    return {
        "threshold": threshold,
        "rejected": len(rejected),
        "solver_calls_avoided": len(rejected),
        "false_negatives": false_negatives,
        "hard_rejection_gate_passed": false_negatives == 0,
    }


def _check(y: Sequence[int], p: Sequence[float]) -> None:
    if not y or len(y) != len(p):
        raise ValueError("nonempty y and p must have equal length")
    if any(a not in (0, 1) for a in y):
        raise ValueError("labels must be 0/1")
    if any((q < 0.0 or q > 1.0 or not math.isfinite(q)) for q in p):
        raise ValueError("probabilities must be finite and in [0,1]")
