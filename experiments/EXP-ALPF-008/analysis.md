# Analysis — Autolab prime-field: round004_exp007_vw_multitarget

## Observation
**Category**: 8 AMORTIZATION -- NOT an ECDLP exponent break

Source excerpt / raw summary:

```
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

```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
