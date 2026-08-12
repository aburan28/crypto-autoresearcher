# Analysis — Autolab prime-field: round006_exp011_binary_fppr

## Observation
survived

Source excerpt / raw summary:

```
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
