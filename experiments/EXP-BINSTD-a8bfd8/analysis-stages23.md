# Analysis — EXP-BINSTD-a8bfd8 Stages 2–3

Hypothesis: `H-BINSTD-85e778` · Experiment: `EXP-BINSTD-a8bfd8` ·
Approval: `DEC-20261002-b1f692` · Expand: `DEC-20261003-d323c0` ·
Producer: `TASK-20261003-dbe1ab` · Snapshot: `TASK-20261003-a57d15` ·
Review plan: `REVIEW-BINSTD-a8bfd8-STAGES23-20261003` ·
Prior Stages 0–1: `EV-BINSTD-a894c0` / `DEC-20261003-d323c0`

## Observation

- `RUN-BINSTD-352dc7` (Stage 2): `status=completed_valid`,
  `outcome=O-STAGES-2-CONTROLS-OK`, `execution-receipt.status=output_validated`,
  `check_returncode=0`. Artifact: `stage2/controls.json`.
  Amazon Bedrock: NOT_USED. Certificate: none.
- `RUN-BINSTD-939c8c` (Stage 3): `status=completed_valid`,
  `outcome=O-IMPEDIMENT`, `output_validated`, `check_returncode=0`.
  Artifact: `stage3/impediment.json`. Probe:
  `python_solver_importable=false`; vendored C at
  `inputs/TRIMOSKA-WDSAT-2024` present but not built/provisioned.
  `asserts_nothing_about`: E1/E2, (A)/(B), Stage-2 outcomes.
  Amazon Bedrock: NOT_USED. Certificate: none.
- Stage-2 controls at `m=15`, `l=6`, `t=2` (from controls.json):
  - same_weight: `isolates_w=true`; within support Δ≤2 < cross gap 12;
    within XOR Δ≈0.133 < cross gap ≈0.800.
  - fixed_V: `ok=true` (`degree_lt_6_polynomial_window`, 12 core vars).
  - 9d12bd: `claim_9d12bd_ok=true`; 16/16 leaf ratios = 1.0 in band
    [0.95,1.05]; support gap persists 14/16 seeds.
  - 99294c: `claim_99294c_ok=true`; 8/8 trials
    `agree_shape_indicators=true` (nonzero_equation_count=13,
    leaf_proxy_vars=12).
- `RESULTS.md` names exactly one outcome: **O-IMPEDIMENT** (Stage 3).
  Protocol success criterion admits this label.
- Blind re-derivation (plan): same_weight isolation inequalities and
  9d12bd leaf_ratios all 1.0 — PASS against controls.json alone.
- Run count: 2 Stages 2–3 runs (+ 2 prior Stages 0–1); within
  `maximum_runs` budgets of the respective trial plans. No re-run of
  Stages 0–1.

## Comparison

- Stage-2 control directions match the frozen HOLD-I Stage-2 arms:
  same-weight isolates `w`; N_leaf discriminator holds under
  matched-width relabel; fully-determined shape indicators invariant
  under basis change; fixed-V held.
- Stage-3 E1/E2 conflict-count classification has **no observation** —
  O-IMPEDIMENT under SR-5. Missing solver is **not** compared to E1
  and is not a negative mathematical result (rule 3 / invalidation
  rules).
- Stages 0–1 (A)/(B) from `EV-BINSTD-a894c0` remain intact and were
  not re-measured.
- Proves-too-much: no E1 confirmation and no security/exponent claim
  in RESULTS.md or run manifests.

## Inference

Stages 2–3 package is **valid**. Stage 2 **supports** the scoped
control claims (same-weight / 9d12bd / 99294c / fixed-V) at toy
`(m=15,l=6,t=2)`, strength **preliminary**, continuing Stages 0–1
support for (A)/(B). Stage 3 O-IMPEDIMENT is infrastructure under
SR-5 — **not** weakens / reject_scoped / E1 falsification. Official
decision: **expand** — re-admit Stage-3 only when a Python-importable
WDSat/ANF clears the impediment; do **not** re-run Stages 0–2; do
**not** support full `H-BINSTD-85e778` (E1 untested). No break /
exponent / attack. Knowledge promotion not warranted.

## Limitation

- Toy cell `m=15,l=6` for Stage-2 controls only; no NIST/ANSI solve.
- Stage-3 E1/E2 unmeasured (no importable Python WDSat/ANF).
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Single implementation; Stage-2 controls use seeded trials but not
  an independent reimplementation.
- Manifests schema-completed additively (`manifest_v2`); originals
  remain flat (immutable).
- No Magma/Sage/AUXIN/Bedrock path used or required.
