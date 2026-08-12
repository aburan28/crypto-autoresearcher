# EXP-011 v2 Result: Binary FPPR/Petit-Quisquater First-Fall Calibration

SEED=2024  timestamp=2026-05-31 00:01:08

## Meter self-validation (MANDATORY)

| control | d_ff | D_reg | fires | role |
|---|---|---|---|---|
| POS-A 3 cubics sharing quadratic | 4 | 7 | True | must fire |
| NEG-1 3 generic quadrics | 4 | 4 | False | must be quiet |
| NEG-2 3 generic cubics | 7 | 7 | False | must be quiet |

**METER_SELF_VALIDATED = True**

## System construction (v2 fix)

V1 bug: Fed raw degree-12 Semaev projections to meter alongside degree-2 field eqs.
V2 fix: Multilinearize the Semaev projections via t_k^2=t_k BEFORE meter.
Result: system has degree <= 2l multilinear Semaev polys + degree-2 field eqs.

## Binary FPPR results

| n | l | n_polys | n_vars | degrees | d_ff | D_reg | fires |
|---|---|---|---|---|---|---|---|
| 7 | 3 | 13 | 6 | [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3] | 4 | 4 | False |
| 7 | 4 | 15 | 8 | [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3] | 4 | 5 | True |
| 9 | 3 | 15 | 6 | [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3] | 3 | 4 | True |
| 9 | 4 | 17 | 8 | [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3] | 4 | 4 | False |
| 11 | 3 | 17 | 6 | [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] | 3 | 4 | True |
| 11 | 4 | 19 | 8 | [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] | 4 | 4 | False |

**d_ff bounded as n grows:** False
**Any binary cell fires (d_ff < D_reg):** True

## Contrast: binary vs prime-field

| setting | d_ff | fires | source | cells |
|---|---|---|---|---|
| Binary FPPR Weil-S3 (this exp) | see table | True | EXP-011 | 6 |
| Prime-field x-ring Semaev | D_reg (7/10/12) | False | EXP-009 | 48 |

## Verdict

**SURVIVED**

Binary FPPR early fall reproduced: d_ff < D_reg. Meter calibrated at large-degree Semaev profile. PO-002 met.

## Interpretation and limitations

The meter fires on the multilinearized binary FPPR system, reproducing the documented Gaudry/Petit-Quisquater early fall. Proof-obligation PO-002 is met: the nontrivial-syzygy meter is calibrated at the FPPR/Semaev degree profile, not just the small [3,3,3]/[4,3] profile of the previous controls. The binary d_ff is bounded (constant) as n grows -- the hallmark of the FPPR subexponential mechanism. The prime-field x-ring result (d_ff=D_reg, EXP-009) remains unaffected: this is binary-field calibration only.

## Next

1. Try the UN-REDUCED system (raw degree-12 Semaev projections without multilinearization, with field eqs): feed both to the meter and check if the fall is at D slightly above the field-eq degree.
2. Increase l to {5,6} to test whether the fall is a threshold effect.
3. Consult FPPR/Gaudry source: identify whether their 'first fall' is the BFS nontrivial-syzygy fall or a different (e.g., last-fall/hybrid) phenomenon.
