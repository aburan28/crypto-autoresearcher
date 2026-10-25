# Native worksheet execution: EXP-ECDLP-524b38

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Source experiment: EXP-ECDLP-efafc0. Original approved frozen finite worksheet. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.

Hypothesis `H-ECDLP-db6960`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-762d8c | output_validated | 7.658767 | 6.777645000000001 | 169000960 |
| RUN-ECDLP-b80f30 | output_validated | 6.952908 | 6.252601999999999 | 169000960 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate. The authorized outer supervisor environment sets GIT_CONFIG_COUNT=1, GIT_CONFIG_KEY_0=core.preloadIndex and GIT_CONFIG_VALUE_0=false under DEC-20261018-1a5209; exact direct child argv and resource limits are unchanged. The exact outer command style is retained in report-data.json.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "chord_collinear": false,
        "control_collinear": false,
        "points_on_curve": [
          true,
          true,
          true
        ],
        "slope": 0,
        "sum_of_first_two": [
          13,
          16
        ],
        "third_intersection": [
          13,
          1
        ]
      },
      "prediction_match": false
    },
    "run_id": "RUN-ECDLP-762d8c"
  },
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "chord_collinear": false,
        "control_collinear": false,
        "points_on_curve": [
          true,
          true,
          true
        ],
        "slope": 0,
        "sum_of_first_two": [
          13,
          16
        ],
        "third_intersection": [
          13,
          1
        ]
      },
      "prediction_match": false
    },
    "run_id": "RUN-ECDLP-b80f30"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-524b38/runs/RUN-ECDLP-762d8c`; archive `7fdfc7dbbb7a7ded6e504a38095a41c203a94e1b`.
- `experiments/EXP-ECDLP-524b38/runs/RUN-ECDLP-b80f30`; archive `7fdfc7dbbb7a7ded6e504a38095a41c203a94e1b`.
