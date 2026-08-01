# Analysis — Autolab prime-field: round004_exp005_validated_firstfall

## Observation
inconclusive

Source excerpt / raw summary:

```
# EXP-005: Sensitivity-Validated First-Fall Meter

**Experiment:** round004-exp005  **Seed:** 42  **Date:** 2026-05-30 21:47  **Verdict:** INCONCLUSIVE

## GATE VERDICT (FIRST)

**Gate status: FAIL**

- Positive controls fired (d_ff < D_reg_pred): 0/3
- Positive controls with anomaly (pos_dim/late_fall): 0/3
- Negative controls passed (no false fire): 2/2

| Control | Type | Fired? | d_ff | D_reg_pred | pos_dim? | Notes |
|---|---|---|---|---|---|---|
| P-syz | positive | no fire | 4 | 4 | False | P-syz: {xy-1, xz-1, yz-1} -- non-regular, 2 solutions, syzyg |
| P-overdet | positive | no fire | 3 | 3 | False | P-overdet: {x^2-1,y^2-1,z^2-1,xy-1} -- 4 eqs overdetermined |
| P-ext | positive | no fire | 8 | 8 | False | P-ext: GF(49) Semaev m=2, degs=[4, 7, 7], D_reg_pred=8 |
| N-semi | negative | PASS | 4 | 4 | False | 3 random dense quadrics in GF(10007)[x,y,z] |
| N-sparse | negative | PASS | N/A | N/A | N/A | 6 sparsity-matched random 3-quadric systems (noise floor: <= |

**Gate interpretation:** Gate FAILED. Semaev results are INCONCLUSIVE.

## Positive Control Details

The meter detects d_ff < D_reg_pred (strict early fall) ONLY when the actual
Hilbert function drops below the positive-truncated semiregular series. This
requires SIGNIFICANT syzygies -- merely having syzygies is not sufficient if
they cancel in the Hilbert series (as happens for complete intersections).

**P-syz:** d_ff=4, D_reg_pred=4, early_fall=False, pos_dim=False

  Ideal dimension: 0, GB degrees: [1, 1, 2]

**P-overdet:** d_ff=3, D_reg_pred=3, early_fall=False, pos_dim=False

  Ideal dimension: 0, GB degrees: [1, 2, 2]

**P-ext:** d_ff=8, D_reg_pred=8, early_fall=False, pos_dim=False

## Per-Cell m=3 Semaev Results
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
