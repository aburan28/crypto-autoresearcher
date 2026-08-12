# Analysis — Autolab prime-field: round009_exp018_vw_optimal_fleet

## Observation
**Category**: 8 AMORTIZATION (H11) + 9 CONSTANT-FACTOR (H09)  NOT an ECDLP exponent break

Source excerpt / raw summary:

```
# EXP-018: VW94-Optimal-Fleet Multi-Target Pollard Rho

**Category**: 8 AMORTIZATION (H11) + 9 CONSTANT-FACTOR (H09)  NOT an ECDLP exponent break
**Date**: 20260531_020556  **Seed**: 42  **c_fleet_primary**: 1.00000000000000

## EXP-007 Defect Fix

| Problem | Fix |
|---------|-----|
| EXP-007 N_total=64 (fixed, too small for n=22,26) | N_total = round(c*sqrt(T*n)/theta) per (T,n) |
| Slope rose 0.56->0.80 (fleet starved at large n) | c_fleet swept {0.5,1.0,2.0}; primary c=1.0 |
| ratio_vw94 was 2.0-5.8 (should be ~1.0) | Target ratio_vw94 ~ 1.0 at optimal fleet |

## Optimal Fleet Sizes (c=1.0 vs EXP-007)

| n_bits | T=1 | T=8 | T=32 | EXP-007 |
|--------|-----|-----|------|---------|
| 16 | 11 | 32 | 64 | 64 |
| 20 | 23 | 64 | 128 | 64 |
| 24 | 45 | 128 | 256 | 64 |

## Positive Control (T=1 multi vs single-target DP-rho, c=1.0)

| n_bits | Multi-T1 ops | Single ops | Ratio | <=1.5x? | N_opt_T1 |
|--------|-------------|-----------|-------|---------|---------|
| 16 | 409 | 3165 | 0.129x | YES | 11 |
| 20 | 1359 | 5115 | 0.266x | YES | 23 |
| 24 | 7615 | 4706 | 1.618x | NO | 45 |

## Sweep Tables (c_fleet=1.0)

ratio_vw94 = multi_ops / (0.886*sqrt(T*n))  TARGET: ~1.0 (EXP-007 was 2.0-5.8)

### n_bits=16

| T | N_opt | Multi ops | Indep ops | Speedup | VW94_th | ratio_vw94 | Solved% |
|---|-------|-----------|-----------|---------|---------|-----------|---------|
| 1 | 11 | 342 | 293 | 0.856x | 161 | 2.128 | 100.0% |
| 2 | 16 | 714 | 735 | 1.030x | 227 | 3.143 | 100.0% |
| 4 | 23 | 1138 | 1176 | 1.033x | 321 | 3.542 | 100.0% |
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
