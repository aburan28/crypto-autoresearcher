# Native worksheet execution: EXP-ECDLP-65f903

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-5b76e2`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-782cda | output_validated | 0.5880089279999083 | 0.587571 | 55107584 |
| RUN-ECDLP-c7395e | output_validated | 0.9198532199989131 | 0.919858 | 55107584 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "cross_products": [
        [
          5,
          6
        ],
        [
          4,
          5
        ],
        [
          6,
          4
        ]
      ],
      "implementations_agree": null,
      "left_below_witness": true,
      "n_cubed": 262144,
      "n_squared": 4096,
      "prediction_comparison": {
        "n_cubed": true,
        "n_squared": true,
        "reversed_below": true,
        "witness_inside": true
      },
      "previous": null,
      "reversed_below": false,
      "state": "awaiting_separate_route_b",
      "tail_products": [
        30,
        30
      ],
      "witness_below_right": true
    },
    "run_id": "RUN-ECDLP-782cda"
  },
  {
    "metrics": {
      "cross_products": [
        [
          5,
          6
        ],
        [
          4,
          5
        ],
        [
          6,
          4
        ]
      ],
      "implementations_agree": true,
      "left_below_witness": true,
      "n_cubed": 262144,
      "n_squared": 4096,
      "prediction_comparison": {
        "n_cubed": true,
        "n_squared": true,
        "reversed_below": true,
        "witness_inside": true
      },
      "previous": {
        "native_receipt_sha256": "10f858309c33a86fb846d16451ed36f8531089de425464ed7618f30316189ecc",
        "raw_sha256": "548e7c2ca73caa5a735f771368b844339d41c8b071bf5f1b2278264d7232cdce",
        "run_id": "RUN-ECDLP-782cda",
        "trial_id": "route-a"
      },
      "reversed_below": false,
      "state": "two_separate_route_runs_compared",
      "tail_products": [
        30,
        30
      ],
      "witness_below_right": true
    },
    "run_id": "RUN-ECDLP-c7395e"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-65f903/runs/RUN-ECDLP-782cda`; archive `9951ca2a853b502b5bb9c6fde3224a7be1dda426`.
- `experiments/EXP-ECDLP-65f903/runs/RUN-ECDLP-c7395e`; archive `9951ca2a853b502b5bb9c6fde3224a7be1dda426`.
