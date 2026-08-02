# Analysis — Autolab prime-field: round003_exp003b_multitarget

## Observation
INCONCLUSIVE

Source excerpt / raw summary:

```
# EXP-003b (FIXED): Multi-target Pollard Rho Amortization

**Category**: 8 AMORTIZATION — NOT an ECDLP exponent break
**Date**: 20260530_205919  **Seed**: 42

## Fixes Applied Over round002-EXP-003

- FIX-1: cross-target collision solving enabled via pooled constraint propagation
- FIX-2: actual independent-rho baseline measured at every T (not theoretical)
- FIX-3: no max_ops cap; n~2^20..2^22 so rho finishes at all T
- FIX-4: real cross-curve negative control (pre-build A-table, run B-walkers)
- FIX-5: positive control T=1 within 1.5x (target 1.2x)
- FIX-6: unified group-op counting; init ops excluded from solve cost

## Hypothesis
H1: shared-DP multi-target rho achieves sqrt(T) amortization; log-log slope in [0.45,0.65] with Solved%>=80% at all T

**H0**: H0: slope>=0.8 OR Solved%<80% at some T

## Curves

- **solinas**: p=2097023, n=2094787, a4=2097020, a6=1074645
- **random**: p=758971, n=760169, a4=713640, a6=608277
- **negctrl**: p=1914001, n=1915477, a4=1466211, a6=395545

## Positive Control (FIX-5)

T=1 multi-target must reproduce single-target rho within 1.2x (target) / 1.5x (pass).

| Curve | Med multi-T1 ops | Med single ops | Expected | Ratio m/s | <=1.2x? | <=1.5x? |
|-------|-----------------|----------------|----------|-----------|---------|---------|
| solinas | 2027 | 6045 | 1282 | 0.335x | YES | YES |
| random | 1411 | 3480 | 772 | 0.406x | YES | YES |

Positive control PASS: **True**

## Sweep Table (FIX-1,2,3)

Multi ops = total to solve ALL T targets (cross-target solving enabled).
Indep ops = actual measured independent single-target rho * T.
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
