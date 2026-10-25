# Native worksheet execution: EXP-ECDLP-6491b4

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-4cf0ce`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-e63c06 | output_validated | 1.3060361050011124 | 1.30053 | 55099392 |
| RUN-ECDLP-46551e | output_validated | 0.568064407001657 | 0.567974 | 55099392 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "bound_by_cell": [
        "1/101",
        "1/1",
        "16/101"
      ],
      "implementations_agree": null,
      "leak_label": "above_floor",
      "numerator_by_cell": [
        1,
        101,
        16
      ],
      "prediction_comparison": {
        "bounds": true
      },
      "previous": null,
      "state": "awaiting_separate_route_b"
    },
    "run_id": "RUN-ECDLP-e63c06"
  },
  {
    "metrics": {
      "bound_by_cell": [
        "1/101",
        "1/1",
        "16/101"
      ],
      "implementations_agree": true,
      "leak_label": "above_floor",
      "numerator_by_cell": [
        1,
        101,
        16
      ],
      "prediction_comparison": {
        "bounds": true
      },
      "previous": {
        "native_receipt_sha256": "3b0940584a277504bb6e1f931caffa42adf1519f7d21603d53dcffbddabec629",
        "raw_sha256": "034efa274d7cb861e1d098c309fde64a2b66abe73905686b4a81ca63c73de002",
        "run_id": "RUN-ECDLP-e63c06",
        "trial_id": "route-a"
      },
      "state": "two_separate_route_runs_compared"
    },
    "run_id": "RUN-ECDLP-46551e"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-6491b4/runs/RUN-ECDLP-e63c06`; archive `19a39d881d633215c8fc994f7d353cf81937c7b0`.
- `experiments/EXP-ECDLP-6491b4/runs/RUN-ECDLP-46551e`; archive `19a39d881d633215c8fc994f7d353cf81937c7b0`.
