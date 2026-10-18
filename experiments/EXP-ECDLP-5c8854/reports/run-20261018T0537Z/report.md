# Native execution report: EXP-ECDLP-5c8854

Descriptive operational observations only; no scientific verdict or attack claim.

Run `RUN-ECDLP-67ed93`; hypothesis `H-ECDLP-753879`; goal `GOAL-ECDLP-001`. Immutable records: `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93`. Raw publication commit `0279e73f3ce3d0fb61738473ddd8ca30abdafa32`.

Requested 1 trial; driver and original checker each exited 0. Native output_validated 1, failed 0, timed out 0. Native elapsed 1.067623 seconds is derived as finished_at minus started_at. Manifest adapter wall seconds=0.09296327300035045; child CPU seconds=0.060922; maximum per-child RSS bytes=16252928; dirty state=True. Detailed CPU model was not recorded. The 256 MiB limit is a ceiling. The adapter wall interval and child resource boundaries are stated exactly in report-data.json; native elapsed includes the separate supervisor checker.

The unchanged legacy driver and its original checker ran in isolated scratch; all three fresh legacy output byte strings were retained exactly. A fresh source-bound envelope carries the new outer EXP/RUN identity. The supervisor checker replayed the original checker against copies of the preserved bytes. Native output_validated describes metadata/control acceptance, without a scientific verdict. Earlier original invalid_output slots remain unchanged.

Execution commit `0424d057b9af606bb7d1d0dcb9aa2daa1d1643b4`. Platform and Python are retained in [report-data.json](report-data.json). Exact [commands](command.json), source and specification hashes, raw parameters, local timing fields and controls are retained without changes. Seed: deterministic fixture, no recorded random draw.

Recorded worksheet fields, unchanged:

```json
{
  "a": 0,
  "b": 2,
  "claim_boundary": "observation of one rank-1 toy cell; not a mutual-information estimate and not a statement about any deployed curve",
  "elapsed_seconds": 3.403400114621036e-05,
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

One deterministic toy fixture was reproduced, with no uncertainty interval or sampled inference. The raw result still carries its original EXP identity; the old manifest retains the original RUN identity in legacy-manifest.yaml. Fresh timing observations are never compared for byte equality to a separate old run. Raw timings use the original driver's local boundaries and are not end-to-end performance comparisons. No scientific certificate, security-bit estimate, asymptotic claim or deployed-curve conclusion follows. A later approved successor would have its own identity and observations.

Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment's frozen specification. No scientific graph content changes follow from a metadata reproduction. The pipeline diagram shows the execution and acceptance point because there is one fixture and no pair of comparable performance arms.

[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: the run's execution-receipt.json, launch.json, environment.json, manifest.yaml, legacy-manifest.yaml, legacy-execution.json, raw-result.json and original RESULTS.md.
