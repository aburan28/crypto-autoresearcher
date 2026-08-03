# Analysis — Autolab prime-field: round008_exp015_m4_semaev_gated

## Observation
failed

Source excerpt / raw summary:

```
# EXP-015 Result: m=4 Semaev S5 in prime-field x-ring under the gated meter

Round 008. Seed 42. Timestamp 2026-05-31 00:54:53.

## Meter self-validation (mandatory)
- POS-A fires d_ff=4<7: **True**
- NEG-1 & NEG-2 quiet: **True**
- e-ring m=3 base-fires but NOT gate_meaningful (artifact): **True**
- POS-C Weil S_3 gate_meaningful (gate PASSES): **True**
- overall meter_self_validated: **True**

| control | d_ff | D_reg | fires | gate_passes | gate_meaningful | lf_degs |
|---|---|---|---|---|---|---|
| POS-A | 4 | None | False | False | False | [3, 3, 3] |
| NEG-1 | None | None | False | False | False | [2, 2, 2] |
| NEG-2 | None | None | False | False | False | [3, 3, 3] |
| e-ring m3 | 3 | 7 | True | False | False | [2, 2, 2, 4] |
| POS-C WeilS3 | 4 | 9 | True | True | True | [3, 3, 3, 3] |

## S5 correctness verification
- S5 total degree: 32 ; degree-per-variable: [8, 8, 8, 8, 8] ; #monomials: 54757
- S4 total degree: 12
- vanishes on REAL 5-tuples (P1+..+P5=O): 6/6 passed
- NEGATIVE control (random x-tuples, should be nonzero): 6/6 nonzero
- S5 verification ok: **True**

## Per-cell meter table (m=4 decomposition system [s5R, F(x1..x4)], sumpoly_indices=[0])

| bits | family | fbsize | s5R tdeg | s5R deg/var | lf_degs | d_ff | D_reg | fires | gate_passes | gate_meaningful | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | random_primeorder | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 13 | random_primeorder | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 13 | random_primeorder | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 13 | solinas_a-3 | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 13 | solinas_a-3 | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 13 | solinas_a-3 | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 15 | random_primeorder | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 15 | random_primeorder | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 15 | random_primeorder | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 15 | solinas_a-3 | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
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
