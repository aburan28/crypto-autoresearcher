"""Stage 1: freeze the engineered positive-control curve and its 4
reduction primes, per specification.yaml Stage 1 / required_artifacts
frozen_positive_control_curve.json.

A=5, B=10, (x0,y0)=(1,4): 4^2=16=1+5+10 (on-curve by construction),
doubling slope lambda=(3*1+5)/(2*4)=1 exactly, giving 2S^=(-1,-2) exactly
over Q (verified directly against frozen_ref.exactcurve, not merely
asserted).

The 4 primes are found via frozen_ref.find_primes_for_curve, i.e.
EXP-ECDLP-a26bde/driver/curves.py's OWN `_find_primes_for_curve`, imported
read-only and applied unmodified to these fixed parameters -- "the identical
seeded search procedure/criteria as driver/curves.py's
_find_primes_for_curve" required by the handoff constraints.
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction

from frozen_ref import exactcurve, find_primes_for_curve

A, B, X0, Y0 = 5, 10, 1, 4
SEED = 20260905  # same seed as the original five curves (curves.py default)
CURVE_IDX = 5    # one past the five original curves (idx 0..4)


def build_and_freeze() -> dict:
    P = (Fraction(X0), Fraction(Y0))
    assert exactcurve.is_on_curve(A, B, P), "engineered curve point off-curve"
    two_S = exactcurve.add(A, B, P, P)
    assert two_S == (Fraction(-1), Fraction(-2)), (
        f"2S^ mismatch: expected (-1,-2), got {two_S}")
    lam = Fraction(3 * X0 * X0 + A, 2 * Y0)
    assert lam == 1, f"doubling slope mismatch: expected 1, got {lam}"

    primes = find_primes_for_curve(A, B, X0, Y0, SEED, CURVE_IDX, count=4)

    return {
        "idx": CURVE_IDX,
        "A": A, "B": B, "x0": X0, "y0": Y0,
        "doubling_slope_lambda": str(lam),
        "two_S_hat_exact": [str(two_S[0]), str(two_S[1])],
        "seed": SEED,
        "primes": primes,
        "engineered": True,
        "note": (
            "Engineered positive control per specification.yaml Stage 1: "
            "on-curve by construction (4^2=16=1+5+10), doubling slope "
            "lambda=1 exactly, giving 2S^=(-1,-2) exactly over Q -- the "
            "known m=2 coincidence the cross-prime x-screen must flag on "
            "4/4 of the primes below."),
    }


if __name__ == "__main__":
    result = build_and_freeze()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "frozen_positive_control_curve.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
