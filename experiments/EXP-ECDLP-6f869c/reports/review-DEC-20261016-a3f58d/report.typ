#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.")

= Evidence review: EXP-ECDLP-6f869c (`DEC-20261016-a3f58d`)

*Decision:* `inconclusive`. *Evidence:* `EV-ECDLP-7c2e94`, direction neutral, strength inconclusive, claim tier toy, proof status derivation. *Run:* `RUN-ECDLP-3d61b8` (working tree, unpublished, manifest not schema-complete, no runner envelope; not cited as evidence). *Executor return:* `TASK-20261016-5e81c3`. *Hypothesis:* `H-ECDLP-b4ebad` (no status transition; stays `specified`). *Idea / question / goal:* `IDEA-20261006-6374b1`, `RQ-ECDLP-002`, `GOAL-ECDLP-001`. *Approval:* `DEC-20261012-4e00e6`. *Producer task:* `TASK-20261012-ec55fb`.

*Exact scoped claim.* In the additive group `Z/503Z` with generator 1, four planted targets, sixteen frozen seeds, sixteen jump branches and DP modulus 16, the frozen census is unscored on both labelings: 3 of 16 seeds finish on the identity labeling and 6 of 16 on the permuted labeling, against a preregistered minimum of 12. The drops are structural: the 2000-step cap exceeds the group order, so they are not timeouts. Re-executing the deterministic driver reproduces them. No `S/J` ratio is scored, so `H-ECDLP-b4ebad` is untested. Nothing here concerns an elliptic curve, a cryptographic group order or the generic exponent 1/2.

Earlier run reports: none exist. `experiments/EXP-ECDLP-6f869c/reports/run-*/` was absent at review time; it is owed by `TASK-20261016-5e81c3`.

= Observation

#figure(
  image("census.svg", width: 100%),
  caption: [Finished seeds per labeling (count of 16; exact, deterministic driver, no spread) against the preregistered minimum of 12 (dashed), with the per-seed finished map. n = 16 seeds per labeling. Values copied from `RUN-ECDLP-3d61b8` raw-result.json (working tree, unpublished). Data: `census-data.json`.],
)

#table(
  columns: 4,
  [labeling], [finished], [finished seeds], [medians],
  [identity], [3 / 16], [3, 11, 13], [null (unscored)],
  [permuted], [6 / 16], [0, 3, 11, 13, 14, 15], [null (unscored)],
)

Recorded step counts for the finished seeds (steps, in finished-seed order). Identity: joint `[49, 73, 114]`, separate `[61, 155, 206]`. Permuted: joint `[76, 120, 127, 168, 106, 56]`, separate `[193, 183, 199, 292, 160, 93]`. No ratio or median is computed from them: the contract forbids it. Flags: `scored = false`, `planted_ok = false`, `matrix_holds = false`, `beyond_matrix = false`, `implementations_agree = scanner_ok = true`. The diagnostic `h1` is false on both labelings; it is not preregistered and is not interpreted.

Validity: run count 1 of 1; seeds 0..15 with the frozen SHA-256 label; raw and manifest agree; frozen inputs match. Defects: V-1 manifest lacks `run.id/status/code/environment/inputs/timing/result`; V-2 no launch record, execution receipt, command, environment or logs; V-3 uncommitted; V-4 source-hash binding not re-checked; V-5 stray `__pycache__`; V-6 no per-seed record for dropped seeds; V-7 the planted check and the implementation-agreement control cannot fail, and the checker imports the driver it checks; V-8 the separate arm is accounting from one shared walk.

= Comparison

- Preregistered reading: neither positive nor negative is reachable. `decision_impact.on_unscored` applies: record the shortfall (identity short by 9, permuted short by 6) and compute no ratio. Neither the 12-seed rule nor the 7/5 threshold is changed.
- Permuted-labeling control: not exercised, because neither labeling is scored.
- Index-calculus baseline and matched rho: not applicable. No ECDLP cost is measured, and no improvement over the index-calculus baseline is claimed. The distance remaining to the matched rho is not measured by this experiment.

= Inference

From derivations D1-D5 (`EV-ECDLP-7c2e94`, `derivation_note`):

- D1: with generator 1, recovery is the identity, so the planted-residue check cannot fail.
- D2: the step map is a deterministic self-map of a 503-element set and the cap is 2000, so every point a walk can ever reach is examined. Drops are cap-independent.
- D3: a target finishes only if it shares the generator's component of the functional graph and a stored DP lies on the shared part of the path.
- D4: the driver is deterministic, so a re-run reproduces the census.
- D5: `S - J = sum(g_i) - max(g_i) >= 0` holds identically, so the ratio is an accounting quantity.

The contract as frozen cannot score the hypothesis, and replicating it adds provenance only. The 10 seeds dropped under both labelings are consistent with component separation, which does not depend on the labeling. This reading is not measured.

= Limitation

Toy tier: one group, sixteen seeds. D1-D5 have not been independently re-derived. The run record is unpublished and schema-incomplete. The reviewing subagent had no shell: the ids were not run through `allocate_id.py --check`, `validate_ledger.py` was not run, the source hashes were not re-checked, and this PDF must be rendered and inspected by the session. If no renderer can be installed, the Typst source and SVG are the archived form and the blocker is stated in the session summary.

= Next actions

+ Session: `allocate_id.py --check` on `EV-ECDLP-7c2e94`, `DEC-20261016-a3f58d`, `TASK-20261016-5e81c3`; run `validate_ledger.py`; write `analysis.md` from `EV-ECDLP-7c2e94`; render and inspect this PDF.
+ Executor: `TASK-20261016-5e81c3` publishes `RUN-ECDLP-3d61b8` or names its provenance gaps. No new trial.
+ Coordinator ledger archive (run alone), then push and open or refresh a PR naming `EV-ECDLP-7c2e94`, `DEC-20261016-a3f58d`, `TASK-20261016-5e81c3`.
+ Goal next action: rerank `GOAL-ECDLP-001`. This idea is a constant-factor accounting measurement and ranks below exponent-targeting work. If it is retained, design a v2 contract under a new EXP id with:
  - a walk-restart rule;
  - an executed separate arm;
  - per-seed records with drop reasons;
  - a schema-complete manifest;
  - a planted check that can fail;
  - a checker independent of `run.py`;
  - the 12-seed rule and 7/5 threshold re-preregistered, disclosing that the design follows the v1 census.

Canonical graphs checked and left unchanged: there is no graph source (svg, dot, typ or mmd) at the top level of `knowledge/frontiers/ecdlp/`. The one frontier row this idea cites, `KR-RHO-46c2c6` (DP reuse across targets), is a text row and is unchanged. An inconclusive decision changes no supported content.
