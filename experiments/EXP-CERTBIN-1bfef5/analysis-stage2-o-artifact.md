# Analysis: EXP-CERTBIN-1bfef5 Stage 2 (H-CERTBIN-4d3853) — O-ARTIFACT

Review plan: `experiments/EXP-CERTBIN-1bfef5/review/review-plan-stage2-o-artifact.yaml`
(`REVIEW-CERTBIN-1bfef5-STAGE2-O-ARTIFACT-20261003`), written before this
analysis. Producer: TASK-20261003-656718. Snapshot: TASK-20261003-9fd48e @
`0aa04d6b6f` (package tip `21e90f7659`). Stage-2 admit: DEC-20261003-a6c85a /
AMD-20261003-9e0869. Stage-1 precondition: EV-CERTBIN-f218ae /
DEC-20261003-b8f938 O-ARM-A-PASS 288/288. Decision target: **refine**
(O-ARTIFACT — S62 control void; instrument unread; not negative evidence
against Propositions B/F or H1 rate claims). Prefer refine (localize
oracle-A / W_4 / S62 control under non-polynomial V) over inventing
weaken / reject_scoped. No break; no exponent; no ECC2K-130; no
Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** One new Stage-2 run directory:
`RUN-CERTBIN-9dcb6d`. Has `manifest.yaml`, additive `manifest_v2.yaml`,
`raw-result.json`, `environment.json`, `command.txt`,
`execution-receipt.json`, `check.stdout.log` = `PASS`, `stage2-result.json`,
`per-set-summary.json`, `per-set-rows.json`, `RESULTS.md`. Receipt status
`output_validated`; producer status `completed_valid`; outcome
`O-ARTIFACT`. Within `maximum_runs: 4`. Required Stage-2 artifacts under
`stage2/` present and mirrored in the run directory. Amazon Bedrock not
used. `certificate.kind: engine_eval_orbit` (Prop F orbit via
`closure.eval_cert`; stock e94b27 `verify_cert.py` not the success path).
Producer claims: `break: false`, `exponent_move: false`. Stage-1
precondition cited: O-ARM-A-PASS 288/288 / EV-CERTBIN-f218ae /
DEC-20261003-b8f938.

**O-ARTIFACT trigger (J2) — blind row re-derivation.**

| quantity | source | blind check | producer |
| --- | --- | --- | --- |
| First trigger | `per-set-rows.json` V_R | key `S62:F-S3:101`; x_R=31046; M_4.one=false; W_4.one=true; oracle_A_sat=false; oracle_A_n_roots=0 | reason: S62 refuted under V_R … (M_4=False, W_4=True) |
| S62_refuted_count | recount W_4.one on set=S62 rows | V_N 24; V_R 25; V_S_octic1 22; V_S_octic2 28 | matches `per-set-summary.json` |
| Seed / cell | stage2-result | seed=2026092691; n_targets=144; curve_B=126251; normal_alpha=3 | agrees |

Blind re-derivation agrees with producer fields. Note: under V_R the
trigger row is oracle-A **unsat** while archive-labeled S62; under
V_S_octic1 the same key is oracle_A_sat=true and W_4 not refuted. The
contract still voids on any S62-control refutation / sat-refute path
(AMD C-2/C-4; invalidation_rules; H falsification_conditions).

**Rates present but unread (J3).** Recorded U62 W_4 point rates:
V_N≈0.452, V_R≈0.339, V_S_octic1≈0.274, V_S_octic2≈0.565; all U62 M_4
rates 0/62. Under O-ARTIFACT these are **not** admissible for
O-E-SET / O-E-POLY / O-MIXED (H distinguishable_outcomes O-ARTIFACT:
"Nothing else read"). Stage-1 arm-(a) 288/288 remains the prior identity
gate (EV-CERTBIN-f218ae) and is not re-litigated here.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break, no
exponent move, no Bedrock. Toy RC-1 cell only.

## Comparison

Against H-CERTBIN-4d3853 distinguishable outcomes and Stage-2 AMD:

- Stage-1 precondition O-ARM-A-PASS 288/288: **holds** (prior EV; not reopened).
- S62 satisfiable control on every V-set: **fails** — S62_refuted_count ∈
  {22,24,25,28} > 0 on all four sets; first producer trigger under V_R
  at S62:F-S3:101 (W_4=true, M_4=false).
- O-ARTIFACT: **met** by contract (instrument void).
- O-E-SET / O-E-POLY / O-MIXED: **not evaluable** (voided instrument).
- Proposition B falsified: **not claimed** (no new arm-(a) disagreement).
- Proposition F falsified: **not claimed** (O-ARTIFACT stop is S62 void,
  not a failed 17/17 orbit with verifying source as the headline).
- O-IMPEDIMENT: **not met** (completed_valid scientific stop, not infra).

## Inference

The Stage-2 package is **valid**. The honest official label is
**O-ARTIFACT**: S62 controls void the instrument under arms (b)–(d), so
structured W_4/M_4 rates must not be read as E-SET/E-POLY/MIXED.
Official reading: instrument void with measured quantity
(S62_refuted_count and first-trigger row), **not** a mathematical
falsifier of Propositions B/F or of H1 saturation predictions.
Decision: **refine**. Hypothesis and experiment `approved → analyzed`.
Do **not** support. Do **not** weaken or reject_scoped H's exact
propositions or empirical rate claims from this voided package
(unreplicated empirical-only adverse call on math forbidden; contract
names S62 refutation as instrument void). No break; no exponent; no
ECC2K-130. Successor (not this tick): localize whether oracle-A over
non-polynomial V incorrectly flips archive-S62 sat, vs W_4 false
refutation of sat targets, vs labeling mismatch; then additive AMD +
Stage-2 re-admit under standing authorization.

## Limitation

- Toy RC-1 cell only (n=17, m=2, l=9); no transfer to n≥131 / ECC2K-130.
- First unreplicated Stage-2 observation; single seed; no independent
  validator/red-team (review-plan PD-1).
- O-ARTIFACT voids rate reading — recorded W_4 rates are not E-POLY.
- oracle_A_sat=false on the V_R trigger row is a localization clue, not
  a completed diagnosis.
- Prop F orbit path is observational under `engine_eval_orbit`; not the
  headline of this stop.
- Strength preliminary for the O-ARTIFACT observation — insufficient for
  support, reject_scoped, or KN-FIND promotion.
- Prior Stage 0-1 RUNs/EVs immutable and not rewritten.
