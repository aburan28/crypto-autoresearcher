# Native execution report: EXP-ECDLP-903c48

Descriptive operational observations only; no scientific verdict or attack claim.

Run `RUN-ECDLP-4616a2`; hypothesis `H-ECDLP-753879`; goal `GOAL-ECDLP-001`. Immutable records: `experiments/EXP-ECDLP-903c48/runs/RUN-ECDLP-4616a2`. Raw publication commit `5014c19c4962b62490ecabf4afd8a9b9a7b15e83`.

Requested 1 trial; driver and original checker each exited 0. Native output_validated 0, invalid_output 1, timed out 0. Native elapsed 0.227553 seconds is derived as finished_at minus started_at. CPU seconds, peak RSS, dirty state, detailed CPU model and a canonical certificate were not recorded. The 256 MiB limit is a ceiling, not measured memory use.

The missing canonical fields are code, environment, inputs, timing and result; the exact native reason is retained in report-data.json. The original checker accepted the emitted worksheet shape, then the supervisor rejected the manifest envelope. The run remains immutable and cannot be rerun in this slot. This process outcome is not a mathematical refutation.

Execution commit `d80cc1ebea504c2c3d2a3352c0ec42ecfe0f872e`. Platform and Python are retained in [report-data.json](report-data.json). Exact [commands](command.json), source and specification hashes, raw parameters, local timing fields and controls are retained without changes. Seed: deterministic fixture, no recorded random draw.

Recorded worksheet fields, unchanged:

```json
{
  "a": 0,
  "b": 2,
  "claim_boundary": "observation of one rank-1 toy cell; not a mutual-information estimate and not a statement about any deployed curve",
  "elapsed_seconds": 3.3909000194398686e-05,
  "experiment_id": "EXP-ECDLP-903c48",
  "first_positive_zero": 12,
  "group_law_order": 12,
  "hypothesis_id": "H-ECDLP-753879",
  "on_curve": true,
  "p": 11,
  "point": [
    1,
    5
  ],
  "schema": "crypto.autoresearch.exp-ecdlp-903c48.stage0.v1",
  "stage": 0,
  "w1": 1,
  "w12": 0,
  "w2": 10,
  "w3": 5,
  "w4": 4,
  "w6": 10,
  "window_end": 24,
  "zeros": [
    12,
    24
  ],
  "zeros_match_order_multiples": true
}
```

One deterministic toy fixture was measured, with no uncertainty interval or sampled inference. Raw timings use the original driver's local boundaries and are not end-to-end performance comparisons. No scientific certificate, security-bit estimate, asymptotic claim or deployed-curve conclusion follows. A later approved successor would have its own identity and observations.

Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment's frozen specification. No scientific graph content changes follow from a legacy manifest rejection. The pipeline diagram shows the execution and stopping point because there is one fixture and no pair of comparable performance arms.

[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: the run's execution-receipt.json, launch.json, environment.json, manifest.yaml, raw-result.json and original RESULTS.md.
