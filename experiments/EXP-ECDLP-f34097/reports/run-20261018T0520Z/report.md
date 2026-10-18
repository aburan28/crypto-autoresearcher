# Native execution report: EXP-ECDLP-f34097

Descriptive operational observations only; no scientific verdict or attack claim.

Run `RUN-ECDLP-62ec3d`; hypothesis `H-ECDLP-af796a`; goal `GOAL-ECDLP-001`. Immutable records: `experiments/EXP-ECDLP-f34097/runs/RUN-ECDLP-62ec3d`. Raw publication commit `abe8d1d21d27eb1083ff9bc4647c19912c607f24`.

Requested 1 trial; driver and original checker each exited 0. Native output_validated 0, invalid_output 1, timed out 0. Native elapsed 0.115407 seconds is derived as finished_at minus started_at. CPU seconds, peak RSS, dirty state, detailed CPU model and a canonical certificate were not recorded. The 256 MiB limit is a ceiling, not measured memory use.

The missing canonical fields are code, environment, inputs, timing and result; the exact native reason is retained in report-data.json. The original checker accepted the emitted worksheet shape, then the supervisor rejected the manifest envelope. The run remains immutable and cannot be rerun in this slot. This process outcome is not a mathematical refutation.

Execution commit `fc3365ccc7715963e041cd4c83fef948e131f2b3`. Platform and Python are retained in [report-data.json](report-data.json). Exact [commands](command.json), source and specification hashes, raw parameters, local timing fields and controls are retained without changes. Seed: deterministic fixture, no recorded random draw.

Recorded worksheet fields, unchanged:

```json
{
  "claim_boundary": "observation of one toy cell; not a section-cost exponent and not a statement about any deployed curve",
  "degree_bound": 1,
  "experiment_id": "EXP-ECDLP-f34097",
  "generator": [
    2,
    3
  ],
  "hypothesis_id": "H-ECDLP-af796a",
  "identity_at_planted": true,
  "oracle_multiplier": 1,
  "oracle_recovered": true,
  "p": 31,
  "planted_on_curve": true,
  "planted_section": [
    2,
    0,
    3,
    0
  ],
  "random_contains_planted": true,
  "random_seconds": 6.899399886606261e-05,
  "random_solution_count": 1,
  "schema": "crypto.autoresearch.exp-ecdlp-f34097.stage0.v1",
  "solutions": [
    [
      4,
      5
    ]
  ],
  "solutions_truncated": [
    [
      0,
      0
    ]
  ],
  "stage": 0,
  "structured_contains_planted": true,
  "structured_seconds": 0.0003756339992833091,
  "structured_solution_count": 1,
  "t0": 0,
  "target": [
    2,
    3
  ],
  "variable_count": 2
}
```

One deterministic toy fixture was measured, with no uncertainty interval or sampled inference. Raw timings use the original driver's local boundaries and are not end-to-end performance comparisons. No scientific certificate, security-bit estimate, asymptotic claim or deployed-curve conclusion follows. A later approved successor would have its own identity and observations.

Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment's frozen specification. No scientific graph content changes follow from a legacy manifest rejection. The pipeline diagram shows the execution and stopping point because there is one fixture and no pair of comparable performance arms.

[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: the run's execution-receipt.json, launch.json, environment.json, manifest.yaml, raw-result.json and original RESULTS.md.
