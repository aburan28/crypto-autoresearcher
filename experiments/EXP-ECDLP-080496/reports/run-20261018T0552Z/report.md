# Native worksheet execution: EXP-ECDLP-080496

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-09812e`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-9f8c2f | output_validated | 2.2783150850009406 | 0.894817 | 54951936 |
| RUN-ECDLP-e6d65d | output_validated | 2.450528593999479 | 0.959099 | 55083008 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "chart_candidates_tested": 9507,
      "chart_size_before_normalize": 117,
      "fixed_points_of_sigma": 0,
      "identity_fixed_points": 117,
      "identity_fixes_all": true,
      "implementations_agree": null,
      "point_count": 117,
      "prediction_comparison": {
        "fixed_points": true,
        "point_count": true,
        "sigma_O": true,
        "sigma_cube_is_id": true,
        "sigma_preserves_all": true
      },
      "previous": null,
      "sigma_O": [
        1,
        0,
        96
      ],
      "sigma_cube_is_id": true,
      "sigma_preserves_all": true,
      "state": "awaiting_separate_route_b",
      "tail_point_on_curve": false,
      "tail_point_tested": true
    },
    "run_id": "RUN-ECDLP-9f8c2f"
  },
  {
    "metrics": {
      "chart_candidates_tested": 9507,
      "chart_size_before_normalize": 117,
      "fixed_points_of_sigma": 0,
      "identity_fixed_points": 117,
      "identity_fixes_all": true,
      "implementations_agree": true,
      "point_count": 117,
      "prediction_comparison": {
        "fixed_points": true,
        "point_count": true,
        "sigma_O": true,
        "sigma_cube_is_id": true,
        "sigma_preserves_all": true
      },
      "previous": {
        "native_receipt_sha256": "111e218815075e3fa553983da85086dcc5e410152b610dae372d81782551e115",
        "raw_sha256": "b1540731f580e8e34970633c2e443e55ff7e2c8755f25ec34b30a72c6a20c49b",
        "run_id": "RUN-ECDLP-9f8c2f",
        "trial_id": "route-a"
      },
      "sigma_O": [
        1,
        0,
        96
      ],
      "sigma_cube_is_id": true,
      "sigma_preserves_all": true,
      "state": "two_separate_route_runs_compared",
      "tail_point_on_curve": false,
      "tail_point_tested": true
    },
    "run_id": "RUN-ECDLP-e6d65d"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-080496/runs/RUN-ECDLP-9f8c2f`; archive `47ad70ed9828de87424d1be3eab2087a1fc7d3df`.
- `experiments/EXP-ECDLP-080496/runs/RUN-ECDLP-e6d65d`; archive `47ad70ed9828de87424d1be3eab2087a1fc7d3df`.
