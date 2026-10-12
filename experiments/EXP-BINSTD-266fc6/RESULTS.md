# RESULTS — EXP-BINSTD-266fc6 (Stages 0–1)

| Field | Value |
|---|---|
| Experiment | `EXP-BINSTD-266fc6` |
| Hypothesis | `H-BINSTD-953387` |
| Idea | `IDEA-20261001-2b71e5` |
| Decision | `DEC-20261003-63fca9` |
| Task | `TASK-20261003-6cb2e7` |
| Trial plan | `experiments/EXP-BINSTD-266fc6/trial-plan-v1.json` |
| Fixture | `stub_synthetic` (n=17, 50 relations, seed 2026100326715) |
| Amazon Bedrock | NOT USED |
| AUXIN / Magma / Sage | NOT USED |

## Stage 0 — `RUN-BINSTD-6dd261`

- Status: `output_validated` / `completed_valid`
- Outcome: **S0-FREEZE-OK**
- Artifacts: `stage0/planted-fault-api.json`, `stage0/preregistered-predictions.json`
- Scientific rates: none (freeze only)

## Stage 1 — `RUN-BINSTD-ad40d3`

- Status: `output_validated` / `completed_valid`
- Outcome: **E-INDEPENDENT**
- Reading: `single_axis_plants_separate`
- Controls: `control_ok=true` (no-fault / triple-fault / null-off-cert)
- On-axis reject / off-axis accept thresholds: both met at ≥0.99
- Artifact: `stage1/matrix-n17.json`

## Claims

- Instrument observation only at toy/stub scale.
- No O-SUPPORT / break / exponent / n≥131 transfer claim.
- Live Part-2 replacement of stubs requires a later amendment.

## next_action

`/review-evidence EXP-BINSTD-266fc6` (compose EV + DEC from Stage 0–1 receipts; Stage 2 remains out of scope until a later decision).
