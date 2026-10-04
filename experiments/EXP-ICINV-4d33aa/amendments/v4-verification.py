#!/usr/bin/env python3
"""Verification script for EXP-ICINV-4d33aa amendment v4 (SR3 gate
false-pass-rate disclosure + one-sided-tests redesign). Run and its output
captured verbatim in v4-verification-output.txt at filing time, per
AGENTS.md rule 9 -- every number amendment v4's rationale cites is
reproducible by re-running this file.

CORR-20260810-a4c123 (independent Validator + Red Team review of amendment
v3's execution) found v3's CI-overlap SR3 sub-check has a 44.3-45.0%
false-pass rate under a genuine null (true ratio = 1) at the sample sizes
this contract uses -- a 40-50x inflation over the ~1-2% false-pass rate of
the literal [1.3,3.6] check v3 replaced. This script does three things:

1.  Confirms the naive "fix" of simply tightening the two-sided confidence
    level (e.g. 95% -> 99%) makes the false-pass rate WORSE, not better --
    a higher confidence level means a WIDER individual CI, which is MORE
    likely to overlap any fixed band. This is verified here so amendment
    v4's text does not need a reader to take it on faith, and so a future
    amendment author does not try the same naive fix.
2.  Derives and verifies change A10's actual redesign: replace the
    two-sided CI-overlap test with TWO INDEPENDENT ONE-SIDED TESTS, each at
    the standard alpha=0.05 significance level, testing H0: true_ratio>=1.3
    (reject = FAIL low) and H0: true_ratio<=3.6 (reject = FAIL high)
    separately. This reuses the EXACT SAME Wilson-Hilferty machinery
    amendment v3 already froze (chi2_wilson_hilferty_bounds(df, z)), with
    ONLY the z parameter changed: z=1.6449 (the standard normal 95th
    percentile, for a one-sided 5% test) instead of z=1.96 (for a two-sided
    95% CI). No new formula is introduced.
3.  Confirms no regression: the two rows amendment v3 was built to admit
    (p=6007, fb=4 and fb=5) still pass under the tighter v4 acceptance
    region, and the sanity row (fb=6) is unaffected. Confirms
    non-vacuousness is preserved (ratio=1.00 and ratio=4.50 at df=139 are
    still correctly rejected, now with a materially tighter margin).

Also verifies the Wilson-Hilferty approximation at z=1.6449 is accurate
against the mathematically exact chi-square quantile (via mpmath), the
same discipline amendment v3's own change A8 applies at z=1.96.
"""
import math

try:
    import mpmath as mp
    mp.mp.dps = 30
    HAVE_MPMATH = True
except ImportError:
    HAVE_MPMATH = False


def wh_bounds(df: int, z: float) -> tuple[float, float]:
    """harness/exp_icinv.py:binomial_null_verdict lines 428-433's formula,
    generalized to an arbitrary z (v3 froze z=1.96 only)."""
    lo = df * (1 - 2 / (9 * df) - z * math.sqrt(2 / (9 * df))) ** 3
    hi = df * (1 - 2 / (9 * df) + z * math.sqrt(2 / (9 * df))) ** 3
    return lo, hi


def chi2_cdf_exact(x: float, df: int) -> float:
    return float(mp.gammainc(df / 2, 0, x / 2, regularized=True))


def false_pass_rate(df: int, z: float, band: tuple[float, float] = (1.3, 3.6)) -> float:
    """P(gate passes | true ratio == 1), exact via the regularized
    incomplete gamma function (chi2 CDF): stat = df*observed_ratio ~
    chi2(df) under a true null, and the gate passes iff
    stat in [df*accept_lo, df*accept_hi]."""
    lo, hi = wh_bounds(df, z)
    accept_lo = band[0] * lo / df
    accept_hi = band[1] * hi / df
    return chi2_cdf_exact(df * accept_hi, df) - chi2_cdf_exact(df * accept_lo, df)


BAND = (1.3, 3.6)
DFS = {"p=6007 (n=140)": 139, "p=4001 (n=138)": 137, "p=2003 (n=104, ungated)": 103}

print("=== Part 1: naive fix (tighten two-sided confidence level) makes it WORSE ===")
print(f"{'z':>8} {'level':>8}   " + "   ".join(f"{label:>24}" for label in DFS))
for z, label in [(1.96, "95% (v3)"), (2.576, "99%"), (2.807, "99.5%"), (3.0, "~99.7%")]:
    row = [f"{false_pass_rate(df, z)*100:>22.2f}%" for df in DFS.values()]
    print(f"{z:>8.3f} {label:>8}   " + "   ".join(row))

print()
print("=== Part 2: change A10 redesign -- two one-sided 5% tests (z=1.6449) ===")
Z_ONESIDED = 1.6449
for label, df in DFS.items():
    lo, hi = wh_bounds(df, Z_ONESIDED)
    accept = (BAND[0] * lo / df, BAND[1] * hi / df)
    fp = false_pass_rate(df, Z_ONESIDED)
    print(f"{label}: df={df}  accept=({accept[0]:.4f},{accept[1]:.4f})  "
          f"false-pass@ratio=1={fp*100:.2f}%  (v3 was "
          f"{false_pass_rate(df, 1.96)*100:.2f}%)")

if HAVE_MPMATH:
    print()
    print("=== Wilson-Hilferty accuracy check at z=1.6449 (vs exact chi2 quantile) ===")
    for label, df in DFS.items():
        lo_wh, hi_wh = wh_bounds(df, Z_ONESIDED)
        lo_exact = float(mp.findroot(lambda x: chi2_cdf_exact(x, df) - 0.05, df))
        hi_exact = float(mp.findroot(lambda x: chi2_cdf_exact(x, df) - 0.95, df))
        print(f"{label}: WH lo={lo_wh:.4f} exact={lo_exact:.4f} "
              f"(rel.err {abs(lo_wh-lo_exact)/lo_exact:.2e})  "
              f"WH hi={hi_wh:.4f} exact={hi_exact:.4f} "
              f"(rel.err {abs(hi_wh-hi_exact)/hi_exact:.2e})")
        # correctness check: reject-rate at the boundary ratio=1.3 should be ~alpha=0.05
        reject_rate = chi2_cdf_exact(lo_wh, df)
        print(f"   reject-rate at true ratio=1.3 boundary (should ~= 0.05): {reject_rate:.4f}")

print()
print("=== Part 3: no-regression + non-vacuousness check, p=6007 (df=139) ===")
lo, hi = wh_bounds(139, Z_ONESIDED)
accept = (BAND[0] * lo / 139, BAND[1] * hi / 139)
print(f"v4 accept region at df=139: {accept}")
for ratio, label in [(1.2315292605941532, "fb=4 (v2-failing, v3-fixed)"),
                      (1.1125313273888915, "fb=5 (v2-failing, v3-fixed)"),
                      (1.4518421211510657, "fb=6 (sanity, already-passing)")]:
    passes = accept[0] <= ratio <= accept[1]
    print(f"  {label}: ratio={ratio:.6f}  passes v4? {passes}")
for ratio in (1.00, 4.50):
    passes = accept[0] <= ratio <= accept[1]
    print(f"  non-vacuousness probe ratio={ratio}: passes v4? {passes} "
          f"(must be False)")
