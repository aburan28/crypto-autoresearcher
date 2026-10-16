#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.")

= Evidence review: EXP-SEMBIN-22a1a2 (`DEC-20261016-8d3f61`)

*Decision:* `inconclusive`. *Evidence:* `EV-SEMBIN-5e2b97`, direction neutral, strength inconclusive, claim tier toy, proof status derivation. *Run:* `RUN-SEMBIN-a818df` (working tree, unpublished, manifest not schema-complete; not cited as evidence). *Executor return:* `TASK-20261016-b7c94e`. *Hypothesis:* `H-SEMBIN-ce9e29` (no status transition). *Idea / question / goal:* `IDEA-20261006-8f4f02`, `RQ-SEMBIN-9e8f82`, `GOAL-SEMBIN-fcb7a2`. *Approval:* `DEC-20261012-67e44f`.

*Exact scoped claim.* For the single polynomial `S_3 = (x1x2+x1x3+x2x3)^2 + x1x2x3 + 1` over `F_2[z]/(z^3+z+1)` (9 bit variables, degree cap 4), the frozen driver's three labels are determined by the three generators alone and are invariant under `x1 -> x1+1`. The experiment therefore cannot discriminate whether the coset shift separates the Boolean label from the unreduced or Macaulay label. No statement about n = 24, EQS4 batches, odd characteristic or any deployed curve.

Earlier run reports: none exist (`experiments/EXP-SEMBIN-22a1a2/reports/run-*/` absent at review time; owed by `TASK-20261016-b7c94e`).

= Observation

#figure(
  image("labels.svg", width: 100%),
  caption: [Labelled first-fall degrees (dimensionless; 5 = no fall by cap 4; Macaulay absent plotted at 5 with open markers). n = 1 deterministic pass per side, no spread. Values from `RUN-SEMBIN-a818df` raw-result.json (working tree, unpublished). Dashed line: preregistered bound 4. Data: `labels-data.json`.],
)

#table(
  columns: 5,
  [side], [`def5_true`], [`def6_fake`], [Macaulay degree], [Macaulay present],
  [unshifted], [5], [4], [null], [false],
  [shifted], [5], [4], [null], [false],
)

`planted_ok = true`, `matrix_holds = true`, `beyond_matrix = false`.

Validity: run count 1 of 1; no seeds (deterministic); raw and manifest agree; frozen inputs match. Defects: V-1 manifest lacks `run.id/status/code/environment/inputs/timing/result`; V-2 no command, environment, logs or execution receipt; V-3 uncommitted; V-4 source hash binding not re-checked; V-5 stray `__pycache__`; V-6 null control cannot fail; V-7 checker imports the driver it checks.

= Comparison

- Preregistered prediction (shifted `def6_fake <= 4` and shifted `def5_true > 4`): literally met.
- Matched unshifted control: identical on every label; shifted minus unshifted = 0 on all three.
- Null control: uninformative (tautological).
- Index-calculus baseline and matched rho: not applicable. No ECDLP cost is measured; no improvement over the IC baseline is claimed; the distance remaining to the matched rho is unmeasured by this experiment.

= Inference

Derivation D1-D6 (`EV-SEMBIN-5e2b97`, `derivation_note`): the driver admits a multiplier only if its degree plus the *unreduced* generator degree (4) is at most d, with d at most 4, so only the three generators ever enter. Their degree-4 parts are an invertible image of the squares of the independent coordinates of `Q`, so no combination falls (`def5_true = 5`) and they are independent (Macaulay absent). Boolean reduction drops each generator to degree at most 3 with constant term 1, so `def6_fake = 4`. The shift adds only terms of degree at most 2. Hence `matrix_holds == planted_ok` on both sides, fixed before execution. The two explanations (shift separates labels vs construction artifact) predict the same data: inconclusive.

= Limitation

Toy tier; one polynomial; characteristic 2. The derivation is unreviewed by an independent agent. The run record is unpublished and schema-incomplete. No shell was available to the reviewing subagent: ids were not run through `allocate_id.py --check`, `validate_ledger.py` was not run, and this PDF was rendered (if at all) by the session.

= Next actions

+ Session: `allocate_id.py --check` on the three new ids; `validate_ledger.py`; write `analysis.md` from `EV-SEMBIN-5e2b97`; render and inspect this PDF.
+ Executor: `TASK-20261016-b7c94e`, publish `RUN-SEMBIN-a818df` or name its provenance gaps; no new trial.
+ Coordinator ledger archive (alone), then push and PR naming `EV-SEMBIN-5e2b97`, `DEC-20261016-8d3f61`, `TASK-20261016-b7c94e`.
+ Goal next action: design a v2 stage-0 contract (cap at least 6, reduced-degree multiplier admission or field equations, contrast-form prediction, a null that can fail, proves-too-much object, checker independent of `run.py`, reproduction gate).

Canonical graphs checked and left unchanged: no graph source (svg, dot, typ, mmd) exists at the top level of `knowledge/frontiers/ecdlp/`. The rows that mention first fall (`KR-IC-889857`, `KR-IC-f5c584`) are text rows and are unchanged. An inconclusive decision changes no supported content.
