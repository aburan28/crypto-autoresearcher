"""EXP-ECDLP-e36df2 v2 (PA-ECDLP-e36df2-v1-to-v2 / TASK-20260921-9b17e4):
select exactly ONE new, non-engineered curve via the identical seeded search
procedure already frozen for this experiment, under a NEW seed (20260921),
and find its 4 reduction primes by the same criteria used throughout this
experiment family.

This is a NEW script (not a modification of any existing driver file). It
reuses, read-only:
  - `_candidate_curves` from experiments/EXP-ECDLP-a26bde/driver/curves.py
    (imported via frozen_ref, which already puts that module on sys.path
    as `a26bde_curves`), for the ordinary (non-engineered) curve search.
  - `find_primes_for_curve` (== a26bde `_find_primes_for_curve`) from
    frozen_ref, exactly as driver/positive_control.py used it for the
    engineered positive-control curve.

Avoid-set: the (A,B,x0,y0) keys of all 6 existing curves used anywhere in
this experiment (the 5 original global curves from
EXP-ECDLP-a26bde/frozen_curves_and_primes.json, idx 0..4, plus the engineered
positive-control curve idx 5 from frozen_positive_control_curve.json), so the
new candidate cannot coincide with any already-used curve even by chance.
The a26bde anomalous-pair curve (A=9,B=-397,x0=7,y0=3) is not one of the six
required avoid-set entries per the handoff's literal wording, but is checked
against too, defensively, and recorded separately below.
"""
from __future__ import annotations

import json
import os

from frozen_ref import a26bde_curves, find_primes_for_curve

SEED = 20260921
CURVE_IDX = 6

# The 5 original global curves (EXP-ECDLP-a26bde/frozen_curves_and_primes.json).
EXISTING_5 = [
    (3, -315, 7, 7),
    (9, -801, 9, 3),
    (9, 26, 1, 6),
    (2, -54, 5, 9),
    (9, -134, 5, 6),
]
# The engineered positive-control curve (frozen_positive_control_curve.json).
POSITIVE_CONTROL = (5, 10, 1, 4)
# Defensive extra (not one of the required "six"): a26bde's anomalous pair.
ANOMALOUS_EXTRA = (9, -397, 7, 3)

AVOID_SIX = set(EXISTING_5) | {POSITIVE_CONTROL}
AVOID_WITH_ANOMALOUS = AVOID_SIX | {ANOMALOUS_EXTRA}


def select_and_freeze() -> dict:
    avoid = set(AVOID_WITH_ANOMALOUS)  # defensive superset actually passed to the search
    candidates = list(a26bde_curves._candidate_curves(SEED, 1, avoid=avoid))
    assert len(candidates) == 1, (
        f"expected exactly 1 new candidate curve, got {len(candidates)}")
    A, B, x0, y0 = candidates[0]
    key = (A, B, x0, y0)
    assert key not in AVOID_SIX, "new candidate collided with an existing curve"
    assert key not in AVOID_WITH_ANOMALOUS, (
        "new candidate collided with the anomalous-pair curve")

    primes = find_primes_for_curve(A, B, x0, y0, SEED, CURVE_IDX, count=4)

    return {
        "idx": CURVE_IDX,
        "A": A, "B": B, "x0": x0, "y0": y0,
        "seed": SEED,
        "primes": primes,
        "engineered": False,
        "avoid_set_required_six": sorted(AVOID_SIX),
        "avoid_set_actually_used_defensive": sorted(AVOID_WITH_ANOMALOUS),
        "note": (
            "Non-engineered curve selected by the same seeded search "
            "(_candidate_curves / _find_primes_for_curve, "
            "EXP-ECDLP-a26bde/driver/curves.py) used for the original five "
            "curves, under a new seed (20260921) distinct from 20260905 and "
            "20260911, per PA-ECDLP-e36df2-v1-to-v2. curve_idx=6 (one past "
            "the existing six curves: idx 0..4 original + idx 5 engineered "
            "positive control). Not a repeat of the positive-control "
            "pattern; no coincidence (rational-2-torsion-like slope, small "
            "point order, etc.) was sought or checked for."),
    }


if __name__ == "__main__":
    result = select_and_freeze()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "frozen_new_curve_c6_seed20260921.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
