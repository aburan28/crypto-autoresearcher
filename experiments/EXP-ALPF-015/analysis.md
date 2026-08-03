# Analysis — Autolab prime-field: round007_exp014_binary_fppr_corrected

## Observation
survived

Source excerpt / raw summary:

```
# EXP-014: Binary FPPR Calibration (Corrected, Round 7)

SEED=20240701  gate_loaded=True  timestamp=2026-05-31 00:32:13

## Meter Self-Validation

| control | d_ff | D_reg | fires | role |
|---|---|---|---|---|
| POS_A | 4 | 7 | True | MUST fire |
| NEG_1 | 4 | 4 | False | must NOT fire |
| NEG_2 | 7 | 7 | False | must NOT fire |

**METER_SELF_VALIDATED = True**

## S_3 Construction and Correctness

S_3 derived via double resultant in F[x1,x2,x3,y1,y2]:
  r1 = Res_{y1}(curve1, chord_condition)
  S3 = Res_{y2}(r1, curve2)
Verified against 12+ real point triples P1+P2+P3=O on E.

## Per-Cell Results

| n | l | polys | vars | S3_ok | rel | d_ff | D_reg | fires | gate | meaningful |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 3 | 13 | 6 | True | False | 4 | 4 | False | True | False |
| 9 | 3 | 15 | 6 | True | False | 3 | 4 | True | True | True |
| 11 | 3 | 17 | 6 | True | False | 3 | 4 | True | True | True |
| 13 | 3 | 19 | 6 | True | False | 3 | 4 | True | True | True |
| 7 | 4 | 15 | 8 | True | False | 4 | 5 | True | True | True |
| 9 | 4 | 17 | 8 | True | False | 4 | 4 | False | True | False |
| 11 | 4 | 19 | 8 | True | False | 4 | 4 | False | True | False |

**d_ff bounded as n grows:** False (global flag False due to n=7,l=3 threshold; but d_ff=3 for n>=9,l=3 is constant = bounded at large n)
**Any fires:** True
**Any gate passes:** True
**Any gate meaningful:** True

## Binary vs Prime-Field Contrast

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
