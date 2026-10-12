# Analysis: EXP-CERTBIN-1bfef5 (H-CERTBIN-4d3853)

Review plan: `experiments/EXP-CERTBIN-1bfef5/review/review-plan.yaml`
(`REVIEW-CERTBIN-1bfef5-20261003`), written before this analysis.
Producer: TASK-20261003-cb60b7. Snapshot: TASK-20261003-510177 @
`62d229ed2c`. Admit: DEC-20261003-f1d0f6. Design approval:
DEC-20261002-711879. Decision target: **refine** (O-IMPEDIMENT —
IMP-ARM-A-BASIS-SWAP; instrument gates passed; not negative evidence).
Prefer refine (wire arm-(a) basis-swap) over inventing weaken /
reject_scoped. No break; no exponent; no ECC2K-130; no Bedrock/AUXIN.
No re-run this tick.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-CERTBIN-ae7b9c` (Stage 0) and `RUN-CERTBIN-d4f1ee` (Stage 1). Each
has `manifest.yaml`, additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `command.txt`, `execution-receipt.json`, and
`check.stdout.log` = `OK`. Stage-0 receipt status `output_validated`,
producer status `completed_valid`. Stage-1 receipt status
`output_validated`, producer outcome `O-IMPEDIMENT` / status
`impediment`. Within `maximum_runs: 4`. Required Stage-0 freeze
artifacts (`stage0/preregistered-predictions.json`,
`stage0/propositions-note.md`, `stage0/instrument-pins.json`,
`stage0/seed-stream.json`, `stage0/precommit-hashes.json`) and Stage-1
artifacts (`stage1/c-pin.json`, `stage1/c-self.json`,
`stage1/c-fix.json`, `stage1/archived-label-census.json`,
`stage1/arm-a-admission.json`, `RESULTS.md`) present. Amazon Bedrock
not used. `certificate.kind: none` on both runs (instrument /
observational package; no discrete_log / key_recovery). Producer
claims: `break: false`, `exponent_move: false`.

**Stage 0 (J2).** `RUN-CERTBIN-ae7b9c` reports `status: completed_valid`,
`worksheet_ok: true`, freeze digests bound for all five `stage0/*`
artifacts. Frozen seed `2026092691`; arm-(a) agreement required
`288/288`; E-SET/E-POLY thresholds `0.90` / `0.50` (CP95); Proposition
B/F note written as observational instrument note (not a machine-checked
proof artifact). Independent `check.py` OK.

**Stage 1 (J3) — blind gate re-derivation.**

| gate | source | blind check | producer |
| --- | --- | --- | --- |
| C_PIN | six `EXP-CERTBIN-e94b27/impl/*.py` | sha256 match expected digests for gf2n/curve/macaulay/closure/oracles_rc1/elim | `ok: true` |
| C_SELF | `stage1/c-self.json` | `mismatches: []` | `ok: true` |
| census | `archived-label-census.json` | counts==expected; `label_rows=288` (U62/S62/C20 × {M_4,W_4}) | `ok: true` |
| C_FIX | `c-fix.json` triples | three (nv,D,neq) triples `ok: true` | `ok: true` |
| arm-(a) | `arm-a-admission.json` | `arm_a_executed: false`; impediment `IMP-ARM-A-BASIS-SWAP` | O-IMPEDIMENT |

Blind re-hash of pinned instruments and census recount match producer
gate fields. Arm-(a) random-basis re-descent of 144 archived targets was
**not** executed; `clears_when` names a documented copy/wrapper of
EXP-CERTBIN-e94b27 descent+closure under a random polynomial-V basis
and normal field basis comparing labels to RUN-CERTBIN-c417e0.
`asserts_nothing_about: Proposition B / Proposition F / E-SET rates`.

**Scope / non-claims (J4).** RESULTS.md and raw-result claim no break,
no exponent move, no Bedrock, and Stage 2 not authorized under this
trial-plan card. Instrument-control / toy RC-1 cell only.

## Comparison

Against H-CERTBIN-4d3853 distinguishable outcomes and Stage-1 contract:

- Stage 0 freeze: **holds** → Stage 1 may be read.
- Instrument gates (C_PIN / C_SELF / census / C_FIX): **all pass** → not
  an instrument-void O-ARTIFACT from gate failure.
- Arm-(a) identity control (288/288 label agreement): **unexecuted**
  because basis-swap wrapper unwired → **O-IMPEDIMENT** by contract
  (`IMP-ARM-A-BASIS-SWAP`), never negative evidence against Propositions
  B/F or H1 (hypothesis falsification_conditions; AGENTS.md rule 3).
- O-E-SET / O-E-POLY / O-MIXED: **not evaluable** (arm-(a) blocking;
  Stage 2 not authorized).
- O-ARTIFACT: **not met** (no label disagreement; no S62 refutation;
  no transferred-certificate failure).
- O-IMPEDIMENT: **met** as declared infrastructure/tooling stop.

## Inference

The package is **valid**. Stage 0 freeze and Stage 1 instrument gates
stand. The decisive arm-(a) identity regression was not run because
`implementation/run.py` has not yet wired the random-basis / normal-field
descent wrapper — an infrastructure/tooling impediment, not a
mathematical falsifier. Official reading: **O-IMPEDIMENT** as
preregistered. Decision: **refine**. Hypothesis and experiment
`approved → analyzed`. Do **not** support (arm-(a) unmeasured; Stage 2
unopened). Do **not** weaken or reject_scoped (infrastructure ≠
falsifier; unreplicated empirical-only adverse call forbidden). No
break; no exponent; no ECC2K-130. Successor (not this tick): wire
IMP-ARM-A-BASIS-SWAP per `clears_when`, then re-admit Stage 1 under the
frozen trial plan (or an additive amendment if the surface must change).

## Limitation

- Toy RC-1 cell only (n=17, m=2, l=9); Stage 2 arms (b)–(d) and
  Proposition F transfer not authorized under this card.
- Arm-(a) 288/288 agreement unmeasured (`arm_a_executed: false`).
- Stage 0 Proposition B/F note is an observational freeze, not a
  machine-checked proof artifact.
- First unreplicated observation; no independent validator/red-team
  (review-plan PD-1).
- `certificate.kind=none` — instrument package, not a solve certificate.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
