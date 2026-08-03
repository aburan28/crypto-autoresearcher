# Analysis — Autolab prime-field: round011_exp022_solvegate_ic_vs_rho

## Observation
**Date:** 2026-05-31  **Seed base:** 20260531  **m:** 3

Source excerpt / raw summary:

```
# EXP-022 SOLVE-GATE: IC vs Rho End-to-End Cost

**Date:** 2026-05-31  **Seed base:** 20260531  **m:** 3

## Per-cell results

| bits | p | n_bits | |FB| | #rel | P_rel | ops/attempt | IC_coll | IC_la | IC_desc | IC_total | rho | IC/rho | k_verified | extrap |
|------|---|--------|-----|------|-------|-------------|---------|-------|---------|----------|-----|--------|------------|--------|
| 12 | 2971 | 12 | 14 | 19 | 1.28e-01 | 1842.7 | 2.75e+05 | 2.85e+02 | 0.00e+00 | 2.75e+05 | 5.74e+02 | 478.63 | YES | measured |
| 14 | 12577 | 14 | 23 | 28 | 1.81e-01 | 4058.2 | 6.29e+05 | 6.72e+02 | 0.00e+00 | 6.30e+05 | 1.19e+03 | 531.07 | YES | measured |
| 16 | 57829 | 16 | 39 | 44 | 1.47e-01 | 10361.0 | 3.10e+06 | 1.76e+03 | 0.00e+00 | 3.10e+06 | 2.56e+03 | 1211.60 | YES | measured |
| 18 | 204667 | 18 | 59 | 64 | 1.42e-01 | 22522.7 | 1.01e+07 | 3.84e+03 | 0.00e+00 | 1.01e+07 | 4.81e+03 | 2109.18 | YES | measured |

## Scaling fit

```
log2(IC/rho) ~ 0.368 * log2(n) + 4.42  (slope>0 means ratio grows)
```

## Interpretation

- Full end-to-end IC solve (k*P==Q verified): **4 / 4 cells**

- IC/rho ratio GROWS with bits (slope > 0): NEGATIVE RESULT confirmed — IC is more expensive than rho and diverges.


## Claim

NEGATIVE RESULT (scoped): For m=3 Semaev IC on toy prime-field curves at bits in {12,14,16,18}, the total measured field-ops exceed Pollard rho by ratio 478.6--2109.2 and the ratio grows with bit-size. This quantifies the EXP-022 capstone.


## Limitations

- Toy scale only (12--18 bits); no deployment relevance.

- m=3 MITM decomposition is a LOWER BOUND on Semaev cost (optimal MITM, no summation-poly solve).

- Extrapolated cells use empirical P_rel; actual cost may vary.

- EXP-009 p-flat artifact NOT present here: factor base grows with p, P_rel is p-dependent.
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
