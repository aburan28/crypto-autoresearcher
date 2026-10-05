# Analysis — EXP-BINSTD-a8bfd8 Stages 2–3

Hypothesis: `H-BINSTD-85e778` · Experiment: `EXP-BINSTD-a8bfd8` ·
Approval: `DEC-20261002-b1f692` · Expand: `DEC-20261003-021bb4` /
`EV-BINSTD-71eabe` · Amendment:
`AMD-EXP-BINSTD-a8bfd8-20261003-stages23-4f26` · Producer:
`TASK-20261003-17c958` · Snapshot: `TASK-20261003-feec8f` · Package tip:
`35e2e094` · Review plan: `REVIEW-BINSTD-a8bfd8-STAGES23-4f26` ·
Stages 0–1 analysis (`analysis.md`) left untouched.

## Observation

- `RUN-BINSTD-b2d17e` (Stage 2): `status=completed_valid`,
  `outcome=O-STAGES-2-CONTROLS-OK`, `execution-receipt.status=output_validated`,
  `check_returncode=0`. Artifact: `stage2/controls.json`. Certificate kind
  none. Amazon Bedrock: NOT_USED.
- `RUN-BINSTD-441e0e` (Stage 3): `status=completed_valid`,
  `outcome=O-IMPEDIMENT`, `output_validated`, `check_returncode=0`.
  Artifacts: `stage3/impediment.json`, `RESULTS.md` (exactly one O-*
  label: **O-IMPEDIMENT**). Certificate kind none. Amazon Bedrock: NOT_USED.
- Stage-2 cell: `m=15`, `l=6`, `t=2`, `V=degree_lt_6_polynomial_window`.
  - `same_weight.isolates_w=true`: within-weight support Δ ≤ 2 <
    cross-weight gap 12; within-weight XOR Δ ≈ 0.133 < cross-weight
    ≈ 0.800. Weight-3 pair (`0x8003`,`0x8011`) exact support/XOR equal
    (89 / 5.933…); weight-5 pair (`0x8017`,`0x802d`) support 101 vs 99.
  - `fixed_V.ok=true`; `core_variable_count=12`.
  - `claim_9d12bd_ok=true`: 16/16 `leaf_ratio_pent_over_tri=1.0` inside
    frozen N_leaf band `[0.95,1.05]`; `support_gap_persists` 14/16
    (seeds `20261009` equal 219/219; `20261013` pent 247 < tri 253).
  - `claim_99294c_ok=true`: 8/8 `agree_shape_indicators`;
    `leaf_proxy_vars_appearing=12`; `nonzero_equation_count=13`.
    Support of transformed systems varies (451–499) as allowed.
- Stage-3 impediment: `python_solver_importable=false`;
  `importable_modules=[]`; vendored C present at
  `inputs/TRIMOSKA-WDSAT-2024/upstream/src/wdsat.c` (not built).
  `asserts_nothing_about` E1/E2, (A)/(B), and Stage-2 outcomes. Reason:
  no importable Python WDSat/ANF; Magma/Sage/AUXIN/Bedrock forbidden as
  success path.
- Blind re-derivation (plan): `2 < 12` and `≈0.133 < ≈0.800`; all 16
  leaf ratios exactly 1.0 — PASS against `controls.json` without reading
  `run.py`.
- Run count this package: 2 ≤ `maximum_runs=3`. Historical Stages 0–1
  runs (`RUN-BINSTD-ff05d8`, `RUN-BINSTD-5b7fa9`) not re-executed.
- `claims.break=false`, `exponent_move=false`, `attack=false` on both
  runs.

## Comparison

- Stage-2 predicates match the frozen contract (same-weight isolates
  `w`; fixed-V held; 9d12bd N_leaf axis-pure; 99294c shape-invariant).
  Two of sixteen relabel seeds lose the support gap; N_leaf stays 1.0,
  so this is not `O-9d12bd-FALSE` (discriminator is the leaf band).
- Stage-3 outcome is the protocol-legal SR-5 terminal: missing solver
  records `O-IMPEDIMENT` and does not classify E1/E2. No artifact
  asserts a conflict-count difference or equality.
- Stages 0–1 (A)/(B) at `m∈{7,11,15}` remain those of `EV-BINSTD-71eabe`;
  this package did not remasure them.
- Versus the earlier Stages 2–3 packet on
  `cursor/review-binstd-a8bfd8-stages23-eb4c` (`EV-BINSTD-7eacca`, runs
  `352dc7`/`939c8c`): same control predicates and the same SR-5
  impediment shape; this review cites the re-admit Stages 0–1 IDs
  (`EV-BINSTD-71eabe` / `DEC-20261003-021bb4`) rather than the lost
  `#1622` pair.
- Proves-too-much control: no security-difference, exponent, or E1
  confirmation appears in `RESULTS.md` or run manifests.

## Inference

Stages 2–3 package is **valid**. Stage 2 **supports** the scoped HOLD-I
control claims (same-weight / 9d12bd / 99294c / fixed-V) at toy
`m=15,l=6,t=2`, strength **preliminary**. Stage 3 `O-IMPEDIMENT` is
**infrastructure**, not falsification of E1 or of (A)/(B). Official
decision: **expand** — re-admit Stage-3 only when a Python-importable
WDSat/ANF clears the impediment; do not re-run Stages 0–2; do not
rewrite Stages 0–1 records. Do **not** support full `H-BINSTD-85e778`
(E1 untested). Do **not** `weaken` / `reject_scoped`. No break /
exponent / attack. Knowledge promotion not warranted at this strength
and open E1 arm.

## Limitation

- Toy Stage-2 cell `m=15,l=6` only; transfer of confound (D) to
  NIST/ANSI degrees remains untested / non-claim.
- Stage-3 E1/E2 not executed; `O-IMPEDIMENT` must not be cited as
  evidence against E1 (SR-5 / SR-6 / AGENTS.md rule 3).
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Single implementation; no independent reimplementation.
- Relabel support-gap fails on 2/16 seeds; N_leaf still holds.
- Manifests schema-completed additively (`manifest_v2`); producer flats
  remain immutable.
- No Magma/Sage/AUXIN/Bedrock path used or required.
