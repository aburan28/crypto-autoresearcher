# Native execution report: EXP-ECDLP-ee406e

Descriptive operational observations only; no scientific verdict or attack claim.

Run `RUN-ECDLP-4110e6`; hypothesis `H-ECDLP-af796a`; goal `GOAL-ECDLP-001`. Immutable records: `experiments/EXP-ECDLP-ee406e/runs/RUN-ECDLP-4110e6`. Raw publication commit `8e3856c252124c942662d01b2fee41434b171bdb`.

Requested 1 trial; driver and original checker each exited 0. Native output_validated 1, failed 0, timed out 0. Native elapsed 2.976810 seconds is derived as finished_at minus started_at. Manifest adapter wall seconds=0.3197879360013758; child CPU seconds=0.09001399999999998; maximum per-child RSS bytes=16384000; dirty state=True. Detailed CPU model was not recorded. The 256 MiB limit is a ceiling. The adapter wall interval and child resource boundaries are stated exactly in report-data.json; native elapsed includes the separate supervisor checker.

The unchanged legacy driver and its original checker ran in isolated scratch; all three fresh legacy output byte strings were retained exactly. A fresh source-bound envelope carries the new outer EXP/RUN identity. The supervisor checker replayed the original checker against copies of the preserved bytes. Native output_validated describes metadata/control acceptance, without a scientific verdict. Earlier original invalid_output slots remain unchanged.

Execution commit `08ae94ace6e0792b86029a5443d00c10df871503`. Platform and Python are retained in [report-data.json](report-data.json). Exact [commands](command.json), source and specification hashes, raw parameters, local timing fields and controls are retained without changes. Seed: deterministic fixture, no recorded random draw.

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
  "random_seconds": 7.098000060068443e-05,
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
  "structured_seconds": 0.0007434029994328739,
  "structured_solution_count": 1,
  "t0": 0,
  "target": [
    2,
    3
  ],
  "variable_count": 2
}
```

One deterministic toy fixture was reproduced, with no uncertainty interval or sampled inference. The raw result still carries its original EXP identity; the old manifest retains the original RUN identity in legacy-manifest.yaml. Fresh timing observations are never compared for byte equality to a separate old run. Raw timings use the original driver's local boundaries and are not end-to-end performance comparisons. No scientific certificate, security-bit estimate, asymptotic claim or deployed-curve conclusion follows. A later approved successor would have its own identity and observations.

Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment's frozen specification. No scientific graph content changes follow from a metadata reproduction. The pipeline diagram shows the execution and acceptance point because there is one fixture and no pair of comparable performance arms.

[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: the run's execution-receipt.json, launch.json, environment.json, manifest.yaml, legacy-manifest.yaml, legacy-execution.json, raw-result.json and original RESULTS.md.
