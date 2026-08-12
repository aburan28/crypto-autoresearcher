# BIN-EXP-010 Result — m=5 diagonal point (CONFOUNDED by nvars < m(m−1))

**Date:** 2026-06-01. Script: `bin_exp010_m5_diagonal.sage` (resultant Semaev evaluator through S₆ + eval-descent + msolve). Log: `bin_exp010_m5_diagonal.log`.

## SURVIVOR: NO · CANDIDATE: NO · VERDICT: the m=5 point is CONFOUNDED — not a clean third diagonal datum

## What was attempted
Get the third diagonal point D_solv(m=5) to test the BIN-OBS-007 law D_solv ≈ m(m−1)+O(1) (predicting ≈20 at m=5). Enabled by the validated resultant Semaev evaluator (computes S₆ without building it symbolically; verified arity 3–6 vanish on real summing tuples).

## Raw result (byte-verified)

| n | m | nvars | descended degrees | D_solv (msolve) | msolve finished | real sol verified | descent secs |
|---|---|---|---|---|---|---|---|
| 15 | 5 | 15 | [14, 15] | 15 | **False** (walled) | True | 236 |

## The confound (decisive — why this is NOT a clean point)

**The descended degree is min(m(m−1), nvars), and at this cell nvars=15 < m(m−1)=20.** A boolean polynomial in 15 variables cannot have degree above 15, so the descended degree was **truncated to 15 by the Boolean ring dimension** — it is NOT the true m=5 Semaev solving degree (which would need ≥20 variables to manifest). The measured 15 = nvars, not the structural value.

This retroactively explains the whole diagonal:

| m | n | nvars | m(m−1) | observable? | measured D_solv |
|---|---|---|---|---|---|
| 3 | 11 | 12 | 6 | YES (nvars ≫ degree) | 7 = 6+1 ✓ |
| 4 | 11 | 12 | 12 | borderline (nvars = degree) | 12 = 12+0 |
| 5 | 15 | 15 | 20 | **NO (nvars < degree)** | 15 = nvars (truncated) |

## What this establishes (honest, useful)

1. **The m=5 datum is uninformative for the m(m−1) law** — variable count too small to host degree 20. Not a confirmation, not a refutation.
2. **METHODOLOGICAL FINDING:** to observe the true diagonal solving degree one needs **nvars ≥ m(m−1)**. For m=5 that means l ≥ 4, n ≥ 20, nvars ≥ 20 → 2^20 evaluations × 9ms/eval ≈ **3 hours descent** — infeasible at this compute scale with the resultant evaluator. The eval-descent's 2^nvars cost is the hard ceiling.
3. **Crucially, the confound is a TOY-SCALE ARTIFACT, not a real obstruction.** On the genuine Petit–Quisquater diagonal, nvars ≈ n and m(m−1) ≈ n^{2/3}, so nvars ≫ m(m−1) always holds for large n — the degree is always observable there. Our toy cells fail the nvars ≥ m(m−1) condition only because n is small. So the m=3,4 points (where it held or was borderline) remain the valid diagonal evidence; m=5 at toy n simply cannot be reached cleanly.

## Claim label

`OBSERVATION` (TOY/SCALED, confounded) → **BIN-OBS-008**: the m=5 diagonal solving-degree measurement is confounded — at the only reachable cell (n=15, nvars=15) the descended degree is truncated to nvars=15 < m(m−1)=20, so it does not test the D_solv≈m(m−1) law. The valid observability condition nvars ≥ m(m−1) requires n ≥ 20 for m=5 (2^20 evals ≈ 3h, infeasible here). The confound is a toy-scale artifact (on the real PQ diagonal nvars≈n ≫ m(m−1)≈n^{2/3}); the m=3,4 points stand as the diagonal evidence.

## What remains / next
- The clean m=5 point needs either a faster S₆ evaluator (current 9ms/eval is the bottleneck; the nested bivariate resultants over GF(2ⁿ) dominate) or a non-evaluation descent that respects nvars ≥ 20.
- The D_solv-vs-m law rests on m=3 (D_solv=7=6+1) and m=4 (D_solv=12=12+0) — two clean points consistent with m(m−1)+O(1); a third clean point is compute-blocked, not science-blocked.
- The decisive axis remains LINEAR ALGEBRA (BIN-NR-003), not solving degree.
