#!/usr/bin/env python3
"""
TASK-20260805-258754 (BATCH-013, GOAL-AES-003), RC-C.

Recompute OBS-B8-7's S-box-specificity percentile using all FIVE available
AES r=5 data points at probe geometry amask=1, smask=1, instead of the two
BATCH-008 originally used.

Source data (verified directly against each source file; see RESULTS.json
for exact field quotes):
  - Y-AES-main : W_ge1_nontrivial = 27 at trials = 2^31 (BATCH-004)
                 -> scaled to a 2^30-equivalent RATE: 27 / 2 = 13.5
                    (a rate, NOT an independently observed integer count)
  - D-AES-K1   : MEASURED_W_ge1 = 14 at trials = 2^30 (BATCH-005)
  - D-AES-K2   : MEASURED_W_ge1 = 14 at trials = 2^30 (BATCH-005)
  - D-AES-K3   : MEASURED_W_ge1 = 8  at trials = 2^30 (BATCH-005)
  - B0-AES-REF : W_ge1_nontrivial = 12 at trials = 2^30 (BATCH-006)

Random-S-box reference distribution (from OBS-B8-7, EV-AES-8b8dcf):
  27 arms, r=5, 2^30 trials each, mean 15.48, range 6-25.
  We use the Poisson(15.48) model exactly as OBS-B8-7 did, so this
  recomputation is comparable to the original two-point computation.

This script computes, independently, per-arm right-tail Poisson
probabilities P(X >= k | Poisson(15.48)) for each of the four raw-count
AES arms (14, 14, 8, 12), and separately reports where the derived rate
13.5 falls relative to the same distribution via CDF interpolation
(flagged explicitly as a rate, not a count -- no Poisson percentile
lookup is performed treating 13.5 as an observed integer draw).
"""
import math


def poisson_pmf(k, lam):
    # Stable for the modest lambda (~15.48) and k ranges used in this
    # script: compute in log-space via lgamma to avoid factorial overflow
    # for the (unused-in-practice) large upper truncation bound.
    return math.exp(k * math.log(lam) - lam - math.lgamma(k + 1))


def poisson_sf_ge(k, lam, upper=200):
    """P(X >= k | Poisson(lam)), summed directly (toy-scale lambda, exact
    to double precision -- terms beyond upper=200 are < 1e-100 for
    lambda=15.48 and are negligible)."""
    return sum(poisson_pmf(i, lam) for i in range(k, upper))


def poisson_cdf_le(k, lam, upper=200):
    """P(X <= k | Poisson(lam))."""
    return sum(poisson_pmf(i, lam) for i in range(0, k + 1))


def main():
    lam = 15.48

    # ---- Four raw-count AES arms, computed INDIVIDUALLY (not averaged) ----
    raw_arms = {
        "D-AES-K1": 14,
        "D-AES-K2": 14,
        "D-AES-K3": 8,
        "B0-AES-REF": 12,
    }

    print(f"Poisson(lambda={lam}) reference model, from EV-AES-8b8dcf OBS-B8-7's")
    print("27-arm random-S-box distribution (mean 15.48, range 6-25).")
    print()
    print("Per-arm right-tail probabilities P(X >= k | Poisson(15.48)):")
    per_arm_results = {}
    for arm, k in raw_arms.items():
        p_ge = poisson_sf_ge(k, lam)
        # percentile position (fraction of the distribution mass <= k-1,
        # i.e. where this arm sits from below)
        p_le_below = poisson_cdf_le(k - 1, lam) if k > 0 else 0.0
        per_arm_results[arm] = {
            "measured_W_ge1": k,
            "P_X_ge_k": p_ge,
            "P_X_le_k_minus_1": p_le_below,
            "approx_percentile_from_below": p_le_below * 100.0,
        }
        print(
            f"  {arm:12s} k={k:2d}  P(X>=k)={p_ge:.6f}  "
            f"P(X<={k-1})={p_le_below:.6f}  "
            f"(~{p_le_below*100:.1f}th percentile from below)"
        )

    mean_raw = sum(raw_arms.values()) / len(raw_arms)
    print()
    print(f"Unweighted mean of the four raw counts (14,14,8,12) = {mean_raw}")
    print("(reported for description ONLY -- per-item C4 forbids averaging")
    print("first and computing one percentile on the mean; each arm above")
    print("was computed independently before this mean was taken.)")

    # ---- Y-AES-main: scaled RATE, not a count ----
    print()
    print("Y-AES-main: 27 hits at 2^31 trials -> rate-scaled to a 2^30-equivalent")
    print("RATE of 27/2 = 13.5. This is NOT an independently observed integer")
    print("count and is NOT run through a Poisson P(X>=k) lookup as if it were")
    print("a draw. Instead its position is described via CDF interpolation")
    print("between the two neighboring integers, and via the nearest-integer")
    print("bound P(X>=14) is quoted only as a bracketing reference.")

    rate = 13.5
    p_ge_13 = poisson_sf_ge(13, lam)
    p_ge_14 = poisson_sf_ge(14, lam)
    # Linear interpolation of the survival function between k=13 and k=14
    # purely as a descriptive device for where 13.5 sits; not a probability
    # statement about an observed count.
    interp_sf_13_5 = p_ge_13 + (p_ge_14 - p_ge_13) * (13.5 - 13)
    p_le_12 = poisson_cdf_le(12, lam)
    p_le_13 = poisson_cdf_le(13, lam)
    interp_cdf_13_5_from_below = p_le_12 + (p_le_13 - p_le_12) * (13.5 - 12)

    print(f"  P(X>=13 | Poisson(15.48)) = {p_ge_13:.6f}")
    print(f"  P(X>=14 | Poisson(15.48)) = {p_ge_14:.6f}   (nearest-integer bound)")
    print(f"  Linear-interpolated 'survival at 13.5' (descriptive only) = {interp_sf_13_5:.6f}")
    print(f"  Linear-interpolated 'position from below at 13.5' (descriptive only) = {interp_cdf_13_5_from_below*100:.1f}%")

    print()
    print("Combined descriptive picture (five points, computed per-arm, never pooled")
    print("into a single test statistic here):")
    for arm, k in raw_arms.items():
        r = per_arm_results[arm]
        print(f"  {arm:12s} = {k:5.1f}  ~{r['approx_percentile_from_below']:.1f}th pct (raw count)")
    print(f"  {'Y-AES-main':12s} = {rate:5.1f}  ~{interp_cdf_13_5_from_below*100:.1f}th pct (RATE, interpolated, not a count)")


if __name__ == "__main__":
    main()
