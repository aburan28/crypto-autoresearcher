# Analysis — EXP-BINSTD-a8bfd8 Stages 0–1

Hypothesis: `H-BINSTD-85e778` · Experiment: `EXP-BINSTD-a8bfd8` ·
Approval: `DEC-20261002-b1f692` · Producer: `TASK-20261003-a5391d` ·
Snapshot: `TASK-20261003-437edd` · Package tip: `460add6f89` ·
Review plan: `REVIEW-BINSTD-a8bfd8-20261003-d393` ·
Re-admit note: supersedes-lost-completion (prior PR #1622
`EV-BINSTD-a894c0` / `DEC-20261003-d323c0` never on main)

## Observation

- `RUN-BINSTD-ff05d8` (Stage 0): `status=completed_valid`,
  `outcome=S0-FREEZE-OK`, `execution-receipt.status=output_validated`,
  `check_returncode=0`. Artifacts:
  `stage0/preregistered-predictions.json`, `stage0/tensor-census.json`,
  `stage0/derivations-note.md`. Amazon Bedrock: NOT_USED.
- `RUN-BINSTD-5b7fa9` (Stage 1): `status=completed_valid`,
  `outcome=O-STAGES-0-1-COMPLETE`, `output_validated`,
  `check_returncode=0`. Artifacts: `stage1/support-census.json`,
  `RESULTS.md`. Amazon Bedrock: NOT_USED.
- Stage 0 census (distinct quadratic monomials, pent/tri):
  - m=7: 67/40 = 1.675; `a_holds=true`
  - m=11: 167/97 ≈ 1.722; `a_holds=true`
  - m=15: 299/176 ≈ 1.699; `a_holds=true`
  - `claim_A_ok=true`. Mean per-output XOR length also larger for
    pentanomial at each m.
- Stage 1 support census: 9 comparisons enumerated; 2 skipped
  (`m=7,l∈{7,8}` because `l≥m`); **7** non-skipped cells all have
  `claim_B_support_holds` and `claim_B_xor_holds` with support ratios
  pent/tri in ≈1.13–1.43. `claim_B_ok=true`. Producer
  `n_comparisons=7` matches the non-skipped count.
- Pre-registered E1 c-band `[0.9,1.0]` and N_leaf band `[0.95,1.05]`
  frozen in Stage 0; **not measured** (Stages 2–3 absent from
  trial-plan-v1).
- Certificate: none (measurement/control instrument; no solve/relation
  claimed). Manifests use `manifest_v2.yaml` schema completion under
  snapshot TASK-20261003-437edd.
- Blind re-derivation (plan): m=7 ratio 67/40 = 1.675 matches
  `raw-result.json` `cells_summary` and census — PASS.
- Run count: 2 ≤ `maximum_runs=8`.
- `claims.break=false`, `exponent_move=false`, `attack=false` on both
  runs.

## Comparison

- Claim (A) pre-registered direction (`pent/tri > 1`, constant-factor
  in m) matches all three Stage-0 cells; ratios cluster near ≈1.7.
- Claim (B) pre-registered direction (pentanomial support and mean XOR
  length strictly larger at matched `(m,t=2,l)`) matches all executable
  Stage-1 cells; skipped cells are protocol-legal (`l≥m`).
- Same-weight / relabelling / basis-change controls (Stage 2) and
  WDSat/ANF E1-vs-E2 (Stage 3) have **no observations** in this package.
- Proves-too-much control: no security-difference or exponent claim
  appears in RESULTS.md or run manifests.
- Versus lost #1622 packet: same run IDs and tip lineage re-admitted;
  this analysis corrects the non-skipped Stage-1 cell count to 7
  (prior draft said 5). Scientific direction unchanged.

## Inference

Stages 0–1 package is **valid** and **supports** the scoped HOLD-I
claims (A) and (B) at toy `m∈{7,11,15}`, `t=2`, `l∈{6,7,8}` (where
`l<m`), strength **preliminary** (deterministic single-implementation
arithmetic; not multi-seed / independent-implementation replication).
Official decision: **expand** — proceed to Stages 2–3 under existing
authorization `DEC-20261002-b1f692` / design card
`TASK-20261002-c39f37`. Do **not** support full `H-BINSTD-85e778`
(E1/E2, 9d12bd N_leaf, 99294c invariance untested). Do **not**
`reject_scoped`. No break / exponent / attack. Knowledge promotion not
warranted at this strength and partial scope. New evidence/decision
IDs (`EV-BINSTD-71eabe` / `DEC-20261003-021bb4`) supersede the lost
#1622 records for official ledger state.

## Limitation

- Toy degrees only; transfer of the constant-factor confound (D) to
  NIST/ANSI degrees is labelled extrapolation and untested here.
- Stages 2–3 (controls + solver E1/E2) not executed; full success
  criterion of the frozen contract remains unmet.
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Single implementation; Stage 0–1 deterministic — no seed replication
  layer.
- Manifests were schema-completed additively (`manifest_v2`); originals
  remain flat (immutable).
- No Magma/Sage/AUXIN/Bedrock path used or required for Stages 0–1.
- Prior #1622 EV/DEC never merged; cite only the new IDs on main-bound
  archives.
