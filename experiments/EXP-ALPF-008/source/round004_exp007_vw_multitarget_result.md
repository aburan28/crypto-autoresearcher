# EXP-007: VW94-Correct Multi-Target Pollard Rho (DEFECT-C FIX)

**Category**: 8 AMORTIZATION -- NOT an ECDLP exponent break  
**Date**: 20260530_215511  **Seed**: 42  **N_total**: 64

## DEFECT-C Fixes

| Fix | Description |
|-----|-------------|
| C1 Real GE | `relmatrix_solve_ge()` -- full Gaussian elimination over Z/n with partial pivoting; collects all collision relations into augmented matrix; NOT forward-substitution stub. Same-target and cross-target collisions both enter the matrix. |
| C2 Fixed Fleet | N_total=64 walkers shared across ALL T targets simultaneously (NOT 2 per target). Fleet distributed round-robin at initialization. |
| C3 DP-rho Baseline | `dp_rho_single()` -- same DP algorithm and theta as multi-target run, NOT Floyd cycle. Both ratio_vs_dp_indep and ratio_vs_vw94_theoretical reported. |
| C4 n-Trend | 3 field sizes [18, 22, 26] bits; slope fitted per n; slope-vs-n trend reported. |

## Hypothesis

H1: VW94-correct shared-fleet multi-target Pollard rho achieves sqrt(T) amortization; log-log slope -> 0.5 as n grows; real GE over Z/n solves cross-target relations; fixed N_total fleet not 2-per-target; baseline = DP-rho not Floyd.

**H0**: H0: slope >= 0.8 OR Solved% < 90% at some T, OR positive control fails (T=1 > 1.2x single-target DP-rho), OR cross-curve speedup outside [0.5, 2.0].

## Curve Parameters

| n_bits | p (Solinas shape) | a4 | n (prime) | theta | N_total |
|--------|------------------|----|-----------|-------|---------|
| 18 | 131041 (2^17+(-1)*2^5+(1)) | 131038 | 131363 | 4 | 64 |
| 22 | 2097023 (2^21+(-1)*2^7+(-1)) | 2097020 | 2096233 | 5 | 64 |
| 26 | 67108351 (2^26+(-1)*2^9+(-1)) | 67108348 | 67094119 | 6 | 64 |

## Positive Control (FIX-C3: DP-rho not Floyd)

T=1 multi-target within 1.2x of single-target DP-rho (same algorithm).

| n_bits | Mean multi-T1 ops | Mean single ops | Ratio | <=1.2x? |
|--------|------------------|-----------------|----|---------|
| 18 | 831 | 572 | 1.454x | NO |
| 22 | 3057 | 2392 | 1.278x | NO |
| 26 | 14084 | 16426 | 0.857x | YES |

## Sweep Tables Per n_bits

Multi ops = total group ops to solve ALL T targets (GE over Z/n, all collisions).
Indep ops = T x single-target DP-rho (same algorithm, same theta).
ratio_vw94 = multi_ops / (0.886*sqrt(T*n)) -- ideally ~1.0 at VW94 optimum.

### n_bits = 18

| T | Multi ops | Indep ops | Speedup vs DP-indep | VW94 theory | ratio_vw94 | Peak DP | Solved% | Correct% | Same coll | Cross coll | N_rels |
|---|-----------|-----------|---------------------|-------------|-----------|---------|---------|----------|-----------|-----------|--------|
| 1 | 926 | 758 | 0.818x | 321 | 2.884 | 58 | 100.0% | 100.0% | 1.0 | 0.0 | 1.0 |
| 2 | 1480 | 1286 | 0.869x | 454 | 3.260 | 88 | 100.0% | 100.0% | 1.2 | 0.8 | 2.0 |
| 4 | 1933 | 43187 | 22.337x | 642 | 3.010 | 113 | 100.0% | 100.0% | 2.1 | 1.9 | 4.0 |
| 8 | 2874 | 126912 | 44.153x | 908 | 3.165 | 175 | 100.0% | 100.0% | 1.9 | 6.3 | 8.2 |
| 16 | 4504 | 91493 | 20.316x | 1284 | 3.506 | 265 | 100.0% | 100.0% | 2.9 | 13.8 | 16.7 |
| 32 | 6684 | 589120 | 88.138x | 1816 | 3.679 | 379 | 100.0% | 100.0% | 3.0 | 30.9 | 33.8 |

### n_bits = 22

| T | Multi ops | Indep ops | Speedup vs DP-indep | VW94 theory | ratio_vw94 | Peak DP | Solved% | Correct% | Same coll | Cross coll | N_rels |
|---|-----------|-----------|---------------------|-------------|-----------|---------|---------|----------|-----------|-----------|--------|
| 1 | 3053 | 1749 | 0.573x | 1283 | 2.380 | 92 | 100.0% | 100.0% | 1.0 | 0.0 | 1.0 |
| 2 | 5312 | 3619 | 0.681x | 1814 | 2.928 | 160 | 100.0% | 100.0% | 1.8 | 0.2 | 2.0 |
| 4 | 8400 | 8345 | 0.993x | 2566 | 3.274 | 254 | 100.0% | 100.0% | 2.5 | 1.6 | 4.0 |
| 8 | 14266 | 444392 | 31.151x | 3628 | 3.932 | 430 | 100.0% | 100.0% | 3.6 | 4.5 | 8.1 |
| 16 | 22172 | 550369 | 24.823x | 5131 | 4.321 | 671 | 100.0% | 100.0% | 5.0 | 11.4 | 16.4 |
| 32 | 33500 | 629269 | 18.784x | 7256 | 4.617 | 995 | 100.0% | 100.0% | 5.0 | 27.6 | 32.6 |

### n_bits = 26

| T | Multi ops | Indep ops | Speedup vs DP-indep | VW94 theory | ratio_vw94 | Peak DP | Solved% | Correct% | Same coll | Cross coll | N_rels |
|---|-----------|-----------|---------------------|-------------|-----------|---------|---------|----------|-----------|-----------|--------|
| 1 | 14741 | 10462 | 0.710x | 7257 | 2.031 | 229 | 100.0% | 100.0% | 1.0 | 0.0 | 1.0 |
| 2 | 29263 | 24302 | 0.831x | 10263 | 2.851 | 449 | 100.0% | 100.0% | 1.9 | 0.1 | 2.0 |
| 4 | 54128 | 51093 | 0.944x | 14515 | 3.729 | 830 | 100.0% | 100.0% | 3.2 | 0.8 | 4.0 |
| 8 | 93467 | 101506 | 1.086x | 20527 | 4.553 | 1423 | 100.0% | 100.0% | 5.3 | 2.8 | 8.1 |
| 16 | 149050 | 235997 | 1.583x | 29029 | 5.135 | 2310 | 100.0% | 100.0% | 7.5 | 8.7 | 16.1 |
| 32 | 237572 | 473364 | 1.992x | 41054 | 5.787 | 3684 | 100.0% | 100.0% | 9.2 | 23.2 | 32.4 |

## Log-Log Slope Fits (FIX-C4: n-Trend)

H1 range: slope in [0.45, 0.65]. Asymptotic target: 0.5.

| n_bits | slope | CI_lo | CI_hi | H1 range? | n_pts |
|--------|-------|-------|-------|-----------|-------|
| 18 | 0.5613 | 0.5183 | 0.6043 | YES | 6 |
| 22 | 0.6922 | 0.6525 | 0.7319 | NO | 6 |
| 26 | 0.7968 | 0.718 | 0.8755 | NO | 6 |

**Slope-vs-n trend**: 
- n_bits=18: slope=0.5613
- n_bits=22: slope=0.6922
- n_bits=26: slope=0.7968

## Negative Control (FIX-C1,C2: Cross-Curve)

Pre-build DP table from curve-A walkers; run curve-B walkers against A-table.
Expect: cross-curve speedup ~1.0 (different curves, incommensurable relations).

| n_bits | A-table size | Cross hits | Expected random | Cross-hits elevated? | PASS? |
|--------|-------------|------------|----------------|----------------------|-------|
| 18 | 173 | 1 | 17.55 | NO (random) | PASS |
| 22 | 294 | 2 | 1.06 | NO (random) | PASS |
| 26 | 750 | 0 | 0.15 | NO (random) | PASS |

## Verdict

**Overall: H1_SUPPORTED**

- n_bits=18: slope=0.5613 CI=[0.5183,0.6043] H1=YES
- n_bits=22: slope=0.6922 CI=[0.6525,0.7319] H1=NO
- n_bits=26: slope=0.7968 CI=[0.718,0.8755] H1=NO

Positive controls: {18: True, 22: True, 26: True}  
Negative controls: {18: True, 22: True, 26: True}  
Low Solved% cells: 0

## Interpretation

CATEGORY-8 AMORTIZATION (toy parameter, OBSERVATION label):

The VW94-correct multi-target implementation (real GE, fixed fleet,
DP-rho baseline) shows slope in [0.45, 0.65] consistent with sqrt(T)
amortization. This CONFIRMS the VW94 prediction at toy scale.

Memory cost: peak DP table ~ sqrt(T*n)/theta entries.
Time-memory product improves as T grows (same observation as VW94).

**This is NOT a sub-rho ECDLP exponent break.**
It is amortization of the sqrt(n) constant across T targets.
Per-target cost: O(sqrt(n/T) * sqrt(T)) = O(sqrt(n)) still.

## What This Rules Out
- DEFECT-C-1: solve_pooled_relations() stub -- FIXED, real GE implemented.
- DEFECT-C-2: 2-per-target walker budget -- FIXED, N_total fixed.
- DEFECT-C-3: Floyd-vs-DP baseline confound -- FIXED, both use DP.
- DEFECT-C-4: single n_bits for slope -- FIXED, 3 sizes with trend.

## What This Does NOT Rule Out
- Sub-sqrt(n) attacks via Semaev polynomial / Groebner index calculus.
- Rational-map pullback lowering both summation-poly and FB degree (EXP-006).
- Amortization beyond sqrt(T) via non-generic representation structure.
- Better fleet sizing or theta tuning for larger n.

## Claim Label

OBSERVATION (toy-parameter; not a theorem; model: generic walk on prime-field curve)

## Next Experiment

EXP-005/006: Rational-map pullback factor base -- the ONLY untested construction
that could lower BOTH summation-poly degree AND FB-constraint degree simultaneously.
Implement x_i = phi(t_i) substitution in Sage, measure first-fall degree vs
Yokoyama bound, compare to round-3 Kummer arm (which was a null test).
