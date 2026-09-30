#!/usr/bin/env python3
"""Verification script for EXP-ICINV-4d33aa amendment v3 (statistical-comparison
SR3 redesign, change A7). Run and its output captured verbatim in
v3-verification-output.txt at filing time, per AGENTS.md rule 9 (never
fabricate a statistic) -- every number A7's rationale and
`confirmed_effect_on_the_run_that_motivated_this_change` cite is reproducible
by re-running this file, not transcribed from an earlier, unlogged session.

This script does two things, neither of which is itself part of the frozen
protocol (that is change A7's formula, in prose, in v3.yaml -- this file only
checks the formula before it is relied on):

1.  Recomputes, from experiments/EXP-ICINV-55c2d8/runs/RUN-ICINV-f09176/
    raw-result.json "rows" (values copied below, read directly from that file,
    not from memory of any earlier computation), the 95% confidence interval
    for R_true at the two rows that failed the version-2 literal band check
    (fb=4, fb=5) plus one sanity row already inside the literal band (fb=6),
    using the Wilson-Hilferty approximation exactly as it appears at
    harness/exp_icinv.py:binomial_null_verdict lines 428-433.

2.  Probes a grid of hypothetical ratios at the same n_curves=140 to show the
    redesigned check is not vacuous: it still rejects a ratio at or near the
    null value of 1 (no over-dispersion) and a ratio well above the historical
    ceiling, so amendment v2's frozen band still does real work under the
    redesign, just not at the two rows sampling noise was always going to
    threaten at this class size (A5's floor-slack caution).

This module is a filing-time check, not a run artifact, and is not imported by
any run. Change A8 requires the SAME Wilson-Hilferty arithmetic to be
REIMPLEMENTED (independently of this file) inside
harness/exp_icinv_fullgroup.py with its own cross-check against the committed
exp_icinv.binomial_null_verdict; this script does not satisfy A8 and does not
try to.
"""
import math

# harness/exp_icinv.py:binomial_null_verdict lines 428-433, copied verbatim.
def chi2_bounds(df: int, z: float = 1.96) -> tuple[float, float]:
    lo = df * (1 - 2 / (9 * df) - z * math.sqrt(2 / (9 * df))) ** 3
    hi = df * (1 - 2 / (9 * df) + z * math.sqrt(2 / (9 * df))) ** 3
    return lo, hi


def r_true_ci(ratio: float, n_curves: int, z: float = 1.96) -> tuple[float, float]:
    df = n_curves - 1
    lo, hi = chi2_bounds(df, z)
    stat = df * ratio
    return stat / hi, stat / lo


BAND = (1.3, 3.6)
# fb_size: (variance_ratio, n_curves) -- read directly, by hand, from
# experiments/EXP-ICINV-55c2d8/runs/RUN-ICINV-f09176/raw-result.json "rows".
ROWS = {
    4: (1.2315292605941532, 140),   # FAILED literal check in RUN-ICINV-99f722
    5: (1.1125313273888915, 140),   # FAILED literal check in RUN-ICINV-99f722
    6: (1.4518421211510657, 140),   # sanity: already inside literal band
}

print("=== Part 1: the two rows that motivated A7, plus one sanity row ===")
print(f"{'fb':>3} {'ratio':>18} {'n':>5} {'df':>5}   "
      f"{'95% CI lo':>10} {'95% CI hi':>10}   overlaps[1.3,3.6]  literal_pass")
for fb, (ratio, n) in ROWS.items():
    lo95, hi95 = r_true_ci(ratio, n, 1.96)
    overlaps = (lo95 <= BAND[1]) and (hi95 >= BAND[0])
    literal = BAND[0] <= ratio <= BAND[1]
    print(f"{fb:>3} {ratio:>18.16f} {n:>5} {n-1:>5}   "
          f"{lo95:>10.6f} {hi95:>10.6f}   {str(overlaps):>17}  {literal}")

print()
print("=== Part 2: non-vacuousness probe at n_curves=140 (df=139) ===")
for ratio in [0.9, 1.0, 1.05, 1.10, 1.15, 1.20, 1.25, 3.6, 4.0, 4.5, 5.0]:
    lo, hi = r_true_ci(ratio, 140)
    overlaps = (lo <= BAND[1]) and (hi >= BAND[0])
    print(f"ratio={ratio:>5.2f}  CI=[{lo:8.4f},{hi:8.4f}]  overlaps_band={overlaps}")
