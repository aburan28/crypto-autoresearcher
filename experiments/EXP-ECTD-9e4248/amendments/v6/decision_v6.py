"""Exact null-safe ECTD v6 KS wrapper and unchanged three data branches."""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Iterable, Sequence

KS_SCHEMA = "crypto.autoresearch.ectd_v6_exact_ks.v1"
DECISION_SCHEMA = "crypto.autoresearch.ectd_v6_decision.v1"


def _finite_exact(values: Iterable[int | Fraction | float]) -> list[Fraction]:
    out: list[Fraction] = []
    for value in values:
        if isinstance(value, bool):
            raise TypeError("boolean is not a sample")
        if isinstance(value, float):
            if not math.isfinite(value):
                continue
            out.append(Fraction.from_float(value))
        elif isinstance(value, (int, Fraction)):
            out.append(Fraction(value))
        else:
            raise TypeError("samples must be exact numbers or finite floats")
    return out


def exact_ks_from_samples(
    sample_x: Sequence[int | Fraction | float],
    sample_y: Sequence[int | Fraction | float],
) -> dict[str, Any]:
    """Return exact D=a/b and the frozen strict cross-multiplied decision.

    Nonfinite floats are censored and counted.  If either finite sample is
    empty, rejects is null.  Equality in the threshold comparison does not
    reject because the predicate is strictly greater than.
    """
    x = sorted(_finite_exact(sample_x))
    y = sorted(_finite_exact(sample_y))
    n, m = len(x), len(y)
    censored_x = len(sample_x) - n
    censored_y = len(sample_y) - m
    if n == 0 or m == 0:
        return {
            "D": None,
            "censored_x": censored_x,
            "censored_y": censored_y,
            "comparison_lhs": None,
            "comparison_rhs": None,
            "m": m,
            "n": n,
            "rejects": None,
            "schema": KS_SCHEMA,
        }
    support = sorted(set(x) | set(y))
    ix = iy = 0
    D = Fraction(0, 1)
    for value in support:
        while ix < n and x[ix] <= value:
            ix += 1
        while iy < m and y[iy] <= value:
            iy += 1
        gap = abs(Fraction(ix, n) - Fraction(iy, m))
        if gap > D:
            D = gap
    a, b = D.numerator, D.denominator
    lhs = 625 * a * a * n * m
    rhs = 1156 * b * b * (n + m)
    return {
        "D": {"denominator": str(b), "numerator": str(a)},
        "censored_x": censored_x,
        "censored_y": censored_y,
        "comparison_lhs": str(lhs),
        "comparison_rhs": str(rhs),
        "m": m,
        "n": n,
        "rejects": lhs > rhs,
        "schema": KS_SCHEMA,
    }


def decide(
    *,
    vertical_ratios: Sequence[int | Fraction | float],
    horizontal_ratios: Sequence[int | Fraction | float],
    all_edges_in_band: bool,
    any_edge_ge_100_or_delta2: bool,
    non_ks_instrument_valid: bool,
) -> dict[str, Any]:
    """One global preregistered KS decision with null outside data branches."""
    ks = exact_ks_from_samples(vertical_ratios, horizontal_ratios)
    if not non_ks_instrument_valid:
        return {
            "decision_branch": "instrument_void",
            "ks_result": ks,
            "reason": "non_KS_instrument_gate_failed",
            "schema": DECISION_SCHEMA,
        }
    if ks["rejects"] is None:
        return {
            "decision_branch": "instrument_void",
            "ks_result": ks,
            "reason": "empty_finite_sample_makes_global_KS_undefined",
            "schema": DECISION_SCHEMA,
        }
    rejects = ks["rejects"]
    if rejects and any_edge_ge_100_or_delta2:
        branch = "discontinuity_nominates_endpoint"
    elif all_edges_in_band and not rejects:
        branch = "continuity_scoped"
    else:
        branch = "moderate_effect_unresolved"
    return {
        "all_edges_in_band": all_edges_in_band,
        "any_edge_ge_100_or_delta2": any_edge_ge_100_or_delta2,
        "decision_branch": branch,
        "ks_result": ks,
        "schema": DECISION_SCHEMA,
    }


def threshold_from_D(*, a: int, b: int, n: int, m: int) -> bool | None:
    """Direct fixture helper implementing the exact frozen inequality."""
    if n == 0 or m == 0:
        return None
    if b <= 0 or a < 0 or a > b or n < 0 or m < 0:
        raise ValueError("invalid exact KS components")
    return 625 * a * a * n * m > 1156 * b * b * (n + m)


if __name__ == "__main__":
    raise SystemExit("static decision module; no experiment execution entry point")
