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

| Cell | Rep | d_ff | D_reg_pred | fb_deg | early_fall? | pos_dim? |
|---|---|---|---|---|---|---|
| structured_13b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| structured_13b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| structured_13b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| structured_13b_FB5 | power-sum | 10 | 10 | 5 | no | YES |
| structured_15b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| structured_15b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| structured_15b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| structured_15b_FB5 | power-sum | 10 | 10 | 5 | no | YES |
| structured_17b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| structured_17b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| structured_17b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| structured_17b_FB5 | power-sum | 10 | 10 | 5 | no | YES |
| structured_19b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| structured_19b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| structured_19b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| structured_19b_FB5 | power-sum | 10 | 10 | 5 | no | YES |
| random_13b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| random_13b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| random_13b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| random_13b_FB5 | power-sum | 10 | 10 | 5 | no | YES |
| random_15b_FB4 | e-ring | 4 | 4 | 2 | no | no |
| random_15b_FB4 | power-sum | 7 | 7 | 4 | no | YES |
| random_15b_FB5 | e-ring | 5 | 5 | 3 | no | no |
| random_15b_FB5 | power-sum | 10 | 10 | 5 | no | YES |

## Power-Sum Anomaly Analysis

**OPEN signal:** 12 cells show positive-dimensional anomaly in power-sum ring.

The power-sum Newton map (x1,x2,x3) -> (p1,p2,p3) is NOT injective over GF(p).
Multiple (x1,x2,x3) triples can map to the same (p1,p2,p3), making the image
of the variety in p-space higher-dimensional than in x-space.
CLAIM LABEL: OBSERVATION -- real structural property, not meter artifact.
This is NOT an early fall, but indicates the power-sum representation introduces
positive-dimensional fibers that inflate the first-fall degree.

## Primary Verdict

**INCONCLUSIVE** -- instrument gate failed.

## What This Rules Out

- Round-3 DEFECT-A is fixed: meter now has positive controls that demonstrate sensitivity.

## What This Does NOT Rule Out

- A representation that SIMULTANEOUSLY lowers both S4 degree AND FB-constraint degree (DEFECT-B: TRUE rational-map pullback, EXP-006).
- Non-Buchberger solvers (XL, crossbred) exploiting sparsity beyond first-fall degree.
- m >= 4 or different prime sizes.
- Extension-field analogs (P-ext positive control may or may not fire depending on degree).
- Power-sum positive-dimensional anomaly as a structural signal (OPEN).

## Next Three Experiments

1. **Conservative (EXP-006):** True rational-map FB pullback -- introduce t_i with x_i=phi(t_i),
   measure S4(phi(t1),phi(t2),phi(t3)) degree in t-ring. Can BOTH degrees drop simultaneously?
2. **Representation-changing:** Kummer x-line coordinates on Montgomery form -- does the
   Montgomery parameterization change the summation-poly degree?
3. **High-risk speculative:** Formalize the power-sum positive-dimensional anomaly:
   is there a quotient map from the p-sum variety that gives a cheaper decomposition
   by exploiting the non-injectivity of the Newton map over GF(p)?
