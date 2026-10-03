# EXP-SEMBIN-509d41 RESULTS (Stages 0–1)

Recorded at: 2026-10-03T00:49:07Z  
Task: `TASK-20261003-af0d91` · Archive owner: `TASK-20261003-caff4e`  
Approved by: `DEC-20261002-15b02c` · Plan: `trial-plan-v1.json`

## Outcomes

| Run | Stage | Outcome | Status |
|---|---|---|---|
| `RUN-SEMBIN-9000a8` | 0 | `S0-FREEZE-OK` | `output_validated` |
| `RUN-SEMBIN-bd538f` | 1 | `S1-INVARIANTS-OK` | `output_validated` |

Stage-1 combinatorial label for this admission: **`S1-INVARIANTS-OK`**.

## Stage 0

Frozen before any Stage-1 metric was read as evidence:

- `stage0/preregistered-predictions.json`
- `stage0/worksheet-note.md`

## Stage 1 (observations only)

- Tree census `t=3..8` matches `(2t-3)!!` (3, 15, 105, 945, 10395, 135135); invariant hold rate 1.0 at every `t`.
- Design-figure `sigma_top` cells at Semaev `(n,t,k)` rows all within stated tolerance (`design_figure_ok: true`).
- DAG known-false control written (`stage1/dag-known-false.md`).
- Wall clock ≈ 1.92 s. Stage 2 **not** admitted by `trial-plan-v1`; no full `O-*` HEUR-TOP headline under this card.

Artifacts: `stage1/tree-census.json`, `stage1/sigma-top-tables.json`, `stage1/dag-known-false.md`.

## Scope / non-claims

No Magma/Sage/AUXIN. Amazon Bedrock: **NOT SELECTED**.  
No exponent move, IC-vs-rho, FIPS verdict, or deployed-curve ECDLP claim.  
Observations only — no hypothesis status change in this packet.
