# Analysis — Autolab prime-field: round005_exp009_crossbred

## Observation
POTENTIAL SURVIVOR -- crossbred field-op cost within 10x of rho on >=1 verified cell. FLAG: extrapolate size trend before any claim.

Source excerpt / raw summary:

```
# EXP-009 Result: crossbred / XL-with-cutoff for m=3 prime-field Semaev

SEED=42  timestamp=2026-05-30 23:13:13  sage=SageMath version 10.9, Release Date: 2026-05-04

## Meter re-validation (round-005 kernel/nontrivial-syzygy meter)

| control | d_ff | D_reg | early_fall | role |
|---|---|---|---|---|
| POS-A 3 cubics shared quadratic factor | 4 | 7 | True | must fire |
| NEG-1 3 generic quadrics (regular CI) | 4 | 4 | False | must be quiet |
| NEG-2 3 generic cubics (regular) | 7 | 7 | False | must be quiet |

**METER VALIDATED: True**

## Cost table: crossbred(best d_1) vs F4 vs rho (FIELD-OP-EQUIVALENT)

rho field ops use 8 field-mults/group-op (conversion most favorable to rho);
F4 ops = ncols(D_solve)^2.37 proxy. cb ops = Macaulay build + exact RREF + guess.

| curve | |FB| | tr | D_reg | d_ff | early | best d_1 | cb ops | n_ver(cb) | F4 ops | n_ver(F4) | rho ops(8M) | cb<F4? | cb/rho | appr rho? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| structured/13b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 323 | True | 8.02 | True |
| structured/13b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 323 | True | 8.02 | True |
| structured/13b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 323 | True | 16.8 | False |
| structured/13b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 323 | True | 16.8 | False |
| structured/13b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 323 | True | 30.3 | False |
| structured/13b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 323 | True | 30.3 | False |
| structured/15b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 638 | True | 4.06 | True |
| structured/15b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 638 | True | 4.06 | True |
| structured/15b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 638 | True | 8.52 | True |
| structured/15b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 638 | True | 8.52 | True |
| structured/15b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 638 | True | 15.4 | False |
| structured/15b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 638 | True | 15.4 | False |
| structured/17b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.29e+03 | True | 2.01 | True |
| structured/17b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.29e+03 | True | 2.01 | True |
| structured/17b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.29e+03 | True | 4.22 | True |
| structured/17b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.29e+03 | True | 4.22 | True |
| structured/17b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.29e+03 | True | 7.61 | True |
| structured/17b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.29e+03 | True | 7.61 | True |
| structured/19b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 2.57e+03 | True | 1.01 | True |
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
