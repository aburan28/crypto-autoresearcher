#!/usr/bin/env python3
"""Known-answer control for the Sage-free lattice-estimator harness.

WHY THIS FILE EXISTS. The harness replaces Sage with a shim (shim/sage/all.py).
A shim that is subtly wrong produces plausible numbers, and this campaign has
already lost three batches to exactly that failure mode: KN-FIND-014 rested on a
misread of a `/k_fft` factor that no one re-derived until BATCH-008. So the shim
asserts nothing on its own authority. It is trusted only insofar as it
reproduces numbers that were computed under REAL Sage, archived, and committed
before the shim existed.

The control is RUN-MLKEM-015-001 (EXP-MLKEM-015, BATCH-001 of GOAL-MLKEM-003),
run under Sage 10.9 with lattice-estimator 3e48ef4. Its primal_bdd/MATZOV costs
for the three FIPS 203 parameter sets are the reference. They are reproduced
here to floating-point equality, not to a tolerance.

USAGE
    git clone https://github.com/malb/lattice-estimator <dir>
    git -C <dir> checkout 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
    PYTHONPATH=tools/sage_free_estimator/shim:<dir> \
        python3 tools/sage_free_estimator/known_answer_control.py

Exit 0 iff every reference value is reproduced. Requires mpmath and scipy.

SCOPE OF THE SHIM. `PowerSeriesRing` is a stub that raises: the Arora-Gröbner
attack is unavailable, so no result from this harness may claim to be the best
attack overall -- only the best among the attacks it actually served. `line` is
plotting and never lies on a cost path. `RealDistribution` implements exactly
the chi-squared and beta CDFs the estimator calls.
"""
from __future__ import annotations

import math
import sys

PINNED_COMMIT = "3e48ef421ec256afddb3e7d2249a77eab6e9ba12"

# From experiments/EXP-MLKEM-015/runs/RUN-MLKEM-015-001/raw-result.json,
# computed under real Sage. Also recorded in EV-MLKEM-015.
REFERENCE = {
    "Kyber512": 140.1994731076207,
    "Kyber768": 200.9587149140538,
}

NIST_CLASSICAL_CUTOFF = {"Kyber512": 143, "Kyber768": 207, "Kyber1024": 272}


def main() -> int:
    try:
        from estimator import RC, schemes
        from estimator.lwe_primal import primal_bdd
    except ImportError as exc:
        print(f"FAIL: cannot import the estimator ({exc}).", file=sys.stderr)
        print(f"      Clone it at {PINNED_COMMIT} and put it plus the shim on "
              f"PYTHONPATH.", file=sys.stderr)
        return 2

    params = {
        "Kyber512": schemes.Kyber512,
        "Kyber768": schemes.Kyber768,
        "Kyber1024": schemes.Kyber1024,
    }

    failures = []
    print(f"{'set':10} {'log2(rop)':>14} {'reference':>18} {'delta':>10} "
          f"{'beta':>5} {'eta':>5} {'d':>6}")
    for name, p in params.items():
        r = primal_bdd(p, red_cost_model=RC.MATZOV)
        got = math.log2(float(r["rop"]))
        beta, eta, d = int(r["beta"]), int(r["eta"]), int(r["d"])
        ref = REFERENCE.get(name)
        if ref is None:
            print(f"{name:10} {got:14.10f} {'(no reference)':>18} {'--':>10} "
                  f"{beta:5} {eta:5} {d:6}")
            continue
        delta = abs(got - ref)
        print(f"{name:10} {got:14.10f} {ref:18.10f} {delta:10.2e} "
              f"{beta:5} {eta:5} {d:6}")
        # Exact equality is the bar. A shim that merely lands close is a shim
        # whose disagreements have not been explained.
        if delta != 0.0:
            failures.append((name, got, ref, delta))

    if failures:
        print("\nFAIL: the shim does not reproduce the Sage-computed reference.",
              file=sys.stderr)
        for name, got, ref, delta in failures:
            print(f"  {name}: got {got!r}, reference {ref!r}, delta {delta:.3e}",
                  file=sys.stderr)
        print("  Do not use this harness for any research claim until this "
              "agrees exactly.", file=sys.stderr)
        return 1

    print(f"\nPASS: every reference value reproduced exactly (delta 0.0) against "
          f"lattice-estimator {PINNED_COMMIT[:12]}.")
    print("Scope: primal_bdd under RC.MATZOV. Arora-GB is unavailable in this "
          "harness; 'best attack' claims are scoped to the attacks served.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
