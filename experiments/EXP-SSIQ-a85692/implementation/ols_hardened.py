#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v5 (BATCH-008) -- PART A: GD-11's fix.

Implements experiments/EXP-SSIQ-a85692/specification_v5.yaml
inputs.gd11_fix_v5 EXACTLY as frozen.

GD-11 (RT-BATCH-007.md Front 4 / OBJ-2): descent_hitting_time.ols_loglog_fit's
degeneracy guard is `if sxx == 0.0: raise ValueError(...)`, where sxx is
computed by summing n copies of a floating-point log(N) value and dividing by
n. IEEE-754 summation-then-division does not always round-trip back to the
exact input value, so for specific (N, repeat-count) pairs `sxx` is a tiny
nonzero float even though every x is mathematically identical -- the guard
silently fails to fire, and a spurious (sometimes materially wrong, nonzero)
`gamma` can enter the caller's results. Independently reproduced at
N=324/repeat=3 and N=611/repeat=6 (this campaign's own real prime N values
for 3889 and 7333) by RT-BATCH-007.md.

descent_hitting_time.py is EXP-SSIQ-58b642's own frozen artifact and stays
byte-for-byte UNTOUCHED (per AGENTS.md immutability and this amendment's own
amendment_scope). This module supersedes by ADDITION, never by in-place edit:

  1. ols_loglog_fit_v2 -- BYTE-IDENTICAL to dht.ols_loglog_fit except the
     degeneracy guard changes from the exact-float check `sxx == 0.0` to
     `max(xs) == min(xs)` -- checking the INPUT log-values directly for
     exact equality, independent of any summation/division rounding.

  2. bootstrap_gap_ci_v2 -- PF-1 FIX APPLIED (round-1 pre-freeze review,
     specification_v5.yaml amendment_scope): a GENUINELY NEW function, NOT
     an alias to dht.bootstrap_gap_ci. dht.bootstrap_gap_ci calls
     ols_loglog_fit by its bare module-global name inside its resampling
     loop, with no parameter to inject an alternate fit function -- so a
     plain alias binding here would have made ols_loglog_fit_v2's hardening
     unreachable from any actual bootstrap resample, exactly the call path
     where GD-11's confirmed spurious-gamma failure occurs. This function
     ports dht.bootstrap_gap_ci's resampling loop structure verbatim (same
     PRIMES-as-resampling-unit design, same n_boot default, same
     percentile-based CI extraction) but calls ols_loglog_fit_v2 (defined in
     THIS module, not the original) for BOTH per-resample fits (fg, fr).

This amendment does NOT retroactively re-run or re-derive any prior batch's
already-archived gamma/CI values (EV-SSIQ-87d21a O-4); it reads no prior
run's raw-result.json at all.
"""

import math

__all__ = ["ols_loglog_fit_v2", "bootstrap_gap_ci_v2"]


def ols_loglog_fit_v2(N_list, y_list):
    """OLS of log(y) on log(N): log(y) = log_c + gamma * log(N).
    Pure Python, deterministic (no floating-point library beyond math.log/
    exp/sqrt), so re-running gives bit-identical output (C-REPRO).

    BYTE-IDENTICAL to descent_hitting_time.ols_loglog_fit EXCEPT the
    degeneracy guard: `if sxx == 0.0: raise ValueError(...)` is replaced by
    `if max(xs) == min(xs): raise ValueError(...)` -- GD-11's fix
    (inputs.gd11_fix_v5)."""
    n = len(N_list)
    if n != len(y_list):
        raise ValueError("N_list and y_list length mismatch")
    if n < 3:
        raise ValueError("too few points for a 2-parameter OLS fit: %d" % n)
    xs = [math.log(N) for N in N_list]
    ys = [math.log(y) for y in y_list]
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    sxx = sum((x - xbar) ** 2 for x in xs)
    sxy = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    if max(xs) == min(xs):
        raise ValueError("degenerate design: all N equal")
    gamma = sxy / sxx
    log_c = ybar - gamma * xbar
    resid = [y - (log_c + gamma * x) for x, y in zip(xs, ys)]
    rss = sum(r * r for r in resid)
    tss = sum((y - ybar) ** 2 for y in ys)
    dof = n - 2
    sigma2 = (rss / dof) if dof > 0 else float("nan")
    se_gamma = math.sqrt(sigma2 / sxx) if dof > 0 else float("nan")
    r2 = (1.0 - rss / tss) if tss > 0 else float("nan")
    return {
        "gamma": gamma, "se_gamma": se_gamma, "log_c": log_c,
        "c": math.exp(log_c), "n": n, "r_squared": r2, "rss": rss,
        "dof": dof, "N_list": list(N_list), "y_list": list(y_list),
    }


def bootstrap_gap_ci_v2(N_list, median_greedy_list, median_random_list, rng,
                         n_boot=2000):
    """Bootstrap CI for M-GAP = gamma_random - gamma_greedy by resampling
    PRIMES (the unit of the OLS fit) with replacement.

    PF-1 FIX APPLIED: a GENUINELY NEW function with its own resampling loop
    (necessarily duplicating dht.bootstrap_gap_ci's loop structure, since
    descent_hitting_time.py cannot be edited), calling ols_loglog_fit_v2 (
    this module's hardened fit) for BOTH per-resample fits (fg, fr), and
    catching the SAME ValueError the hardened guard now raises more
    reliably, discarding that resample exactly as the original does for a
    caught ValueError."""
    n = len(N_list)
    gaps = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        Nb = [N_list[i] for i in idx]
        gb = [median_greedy_list[i] for i in idx]
        rb = [median_random_list[i] for i in idx]
        try:
            fg = ols_loglog_fit_v2(Nb, gb)
            fr = ols_loglog_fit_v2(Nb, rb)
        except ValueError:
            continue
        gaps.append(fr["gamma"] - fg["gamma"])
    gaps.sort()
    if not gaps:
        return None, None, []
    lo = gaps[int(0.025 * len(gaps))]
    hi = gaps[min(len(gaps) - 1, int(0.975 * len(gaps)))]
    return lo, hi, gaps
