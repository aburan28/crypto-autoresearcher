# Native worksheet execution: EXP-ECDLP-5a293e

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-78a3d1`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-113f49 | output_validated | 1.4692843020002329 | 0.5924619999999999 | 55091200 |
| RUN-ECDLP-8c3ce8 | output_validated | 2.0442457720000675 | 0.8090309999999998 | 55091200 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "affine_point_count": 17,
      "all_y_zero_points_included": true,
      "implementations_agree": null,
      "points_with_y_zero": 1,
      "prediction_comparison": {
        "affine_point_count": true,
        "x_mismatches": true,
        "x_plus_1_mismatches": true,
        "y_mismatches": true
      },
      "previous": null,
      "state": "awaiting_separate_route_b",
      "x_mismatches": 0,
      "x_plus_1_mismatches": 0,
      "y_mismatches": 16
    },
    "run_id": "RUN-ECDLP-113f49"
  },
  {
    "metrics": {
      "affine_point_count": 17,
      "all_y_zero_points_included": true,
      "implementations_agree": true,
      "points_with_y_zero": 1,
      "prediction_comparison": {
        "affine_point_count": true,
        "x_mismatches": true,
        "x_plus_1_mismatches": true,
        "y_mismatches": true
      },
      "previous": {
        "native_receipt_sha256": "b98e3a7b4c90a5528f417ee75fb90d467f1e230497c5696f34c2fa38412e8c21",
        "raw_sha256": "db221eaf324ab9e427cead0e3252ed219d2aab61327669ada0f9830f4d89e1a7",
        "run_id": "RUN-ECDLP-113f49",
        "trial_id": "route-a"
      },
      "state": "two_separate_route_runs_compared",
      "x_mismatches": 0,
      "x_plus_1_mismatches": 0,
      "y_mismatches": 16
    },
    "run_id": "RUN-ECDLP-8c3ce8"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-5a293e/runs/RUN-ECDLP-113f49`; archive `1bfc925fe0bfa1610e687bea2d2b1f40077b45dc`.
- `experiments/EXP-ECDLP-5a293e/runs/RUN-ECDLP-8c3ce8`; archive `1bfc925fe0bfa1610e687bea2d2b1f40077b45dc`.
