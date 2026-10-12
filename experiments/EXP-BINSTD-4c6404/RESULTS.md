# EXP-BINSTD-4c6404 TASK-20261003-b17785 observations

Exactly one experiment-level label: **O-IMPEDIMENT**.

This is not a mathematical refutation of HEUR-BINSTD-79a077-H1 / H-BINSTD-dcc004.

## Stages

| Stage | Plan id | Run id | Supervisor | Notes |
| --- | --- | --- | --- | --- |
| 0 | stage0-pin-tau-catalog-freeze | RUN-BINSTD-9daa20 | invalid_output / needs_reconciliation | Producer argv exit 0; producer label O-STAGE0-OK left unchanged in raw-result.json and manifest.producer-stub.yaml. Independent check.py exit 1: `r_n freeze mismatch` (JSON string keys vs int `R_N`). |
| 1 | stage1-n17-ic-races | RUN-BINSTD-42a607 | not launched | Waiting on Stage 0 `output_validated`. Existing run directories are never reused. |
| 2 | stage2-n23-n31-plus-null | RUN-BINSTD-f9399a | not launched | Waiting on Stage 1. |

## Frozen prediction

Not compared. No Stage-1 or Stage-2 timings exist.

## Scope

Toys n in {17,23,31} only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No exponent. No n>=131 transfer.
