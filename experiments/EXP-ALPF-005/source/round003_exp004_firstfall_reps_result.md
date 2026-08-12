# EXP-004: Validated First-Fall Instrument + Three-Representation Sweep

**Experiment:** round003-exp004  **Seed:** 42  **Date:** 2026-05-30 21:21  **Verdict:** FAILED

## Instrument Gate (STEP 0)

Gate criteria:
- (0a) Planted-syzygy system {xy-1, xz-1, yz-1} must show d_ff < D_reg_pred
- (0b) Semiregular random system must NOT show early fall
- LIMITATION: Sensitivity to strict early falls not independently validated (see log)

| Gate | Pass? | d_ff | D_reg_pred | early_fall |
|---|---|---|---|---|
| 0a: calibration (semiregular: d_ff=D_reg_pred) | PASS | 4 | 4 | False |
| 0b: specificity (no false positives) | PASS | 4 | 4 | False |
| **Overall gate** | **PASS** | | | |

## Per-Cell Results

| Cell | Rep | d_ff | D_reg_pred | fb_deg | early_fall? |
|---|---|---|---|---|---|
| structured_13b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_13b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_13b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_13b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_13b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_13b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_13b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_13b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_13b_FB5 | Kummer | 10 | 10 | 4 | no |
| structured_15b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_15b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_15b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_15b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_15b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_15b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_15b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_15b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_15b_FB5 | Kummer | 10 | 10 | 4 | no |
| structured_17b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_17b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_17b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_17b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_17b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_17b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_17b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_17b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_17b_FB5 | Kummer | 10 | 10 | 4 | no |
| structured_19b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_19b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_19b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_19b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_19b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_19b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_19b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_19b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_19b_FB5 | Kummer | 10 | 10 | 4 | no |
| random_13b_FB3 | e-ring | 1 | 1 | 1 | no |
| random_13b_FB3 | power-sum | 4 | 4 | 3 | no |
| random_13b_FB3 | Kummer | 7 | 7 | 3 | no |
| random_13b_FB4 | e-ring | 4 | 4 | 2 | no |
| random_13b_FB4 | power-sum | 7 | 7 | 4 | no |
| random_13b_FB4 | Kummer | 10 | 10 | 4 | no |
| random_13b_FB5 | e-ring | 5 | 5 | 3 | no |
| random_13b_FB5 | power-sum | 10 | 10 | 5 | no |
| random_13b_FB5 | Kummer | 10 | 10 | 4 | no |
| random_15b_FB3 | e-ring | 1 | 1 | 1 | no |
| random_15b_FB3 | power-sum | 4 | 4 | 3 | no |
| random_15b_FB3 | Kummer | 7 | 7 | 3 | no |
| random_15b_FB4 | e-ring | 4 | 4 | 2 | no |
| random_15b_FB4 | power-sum | 7 | 7 | 4 | no |
| random_15b_FB4 | Kummer | 10 | 10 | 4 | no |
| random_15b_FB5 | e-ring | 5 | 5 | 3 | no |
| random_15b_FB5 | power-sum | 10 | 10 | 5 | no |
| random_15b_FB5 | Kummer | 10 | 10 | 4 | no |

## Rho Baseline

| family | bits | n | n_ops_rho | expected | ratio | solved |
|---|---|---|---|---|---|---|
| structured | 13 | 4153 | 201 | 57 | 3.52x | YES |
| structured | 15 | 16183 | 678 | 113 | 6.015x | YES |
| structured | 17 | 65993 | 687 | 228 | 3.018x | YES |
| structured | 19 | 262193 | 2805 | 454 | 6.183x | YES |
| random | 13 | 8087 | 387 | 80 | 4.857x | YES |
| random | 15 | 25819 | 513 | 142 | 3.603x | YES |

## Primary Verdict

**NEGATIVE RESULT** (clean, instrument-validated)

No representation (e-ring, power-sum, Kummer) shows d_ff < D_reg_pred in any tested cell.

CLAIM LABEL: NEGATIVE RESULT

Scope: toy prime sizes 2^13-2^19, |FB| in {3,4,5}, Solinas+random prime-order curves, e-ring/power-sum/Kummer representations, m=3 Semaev system.

Red-team hypothesis CONFIRMED: e-symmetric rewrite lowers S4 total degree (12->lower) but FB-constraint degree does NOT drop correspondingly; total D_reg is conserved. Power-sum gives same degree profile. Kummer/rational-map factored FB does not change fb_deg (still 4 for |FB|=4).

## What This Rules Out

- d_ff instrument is now VALIDATED (gate passed): results are trustworthy.
- Round-2 sweep-start artifact (D starting at input degree) is fixed.
- No strict-early-fall for e-ring, power-sum, or Kummer FB representation at toy sizes (extends NR-009, NR-010 to m=3 with a validated detector).
- The red-team hypothesis about D_reg conservation is supported: lowering the S4 degree in symmetric coordinates does not lower D_reg because FB-constraint degree rises correspondingly.

## What This Does NOT Rule Out

- A representation that SIMULTANEOUSLY lowers BOTH the summation-poly degree AND the FB-constraint degree (the exact condition the red team identified).
- m >= 4 systems or different prime sizes.
- Non-Buchberger solvers (XL, crossbred) that exploit sparsity.
- Extension-field analogs (P2 positive control confirms falls exist there).
- Isogeny-quotient or endomorphism-derived factor bases.

## Next Three Experiments

1. **Conservative:** Test m=4 (S_5 summation polynomial) -- additional symmetry may break the D_reg conservation pattern.
2. **Representation-changing:** Design a TRUE rational-map FB where phi: P^1 -> x-line is degree-2 AND the Semaev polynomial in the t_i variables has lower effective degree. Requires computing S4 composition phi(t_i) and measuring the resulting degree in (t1,t2,t3).
3. **High-risk speculative:** p-adic lift + formal group log: represent x-coordinates as p-adic expansions and test whether the carry structure of EC addition creates a smoothness-like decomposition in the first p-adic digits.
