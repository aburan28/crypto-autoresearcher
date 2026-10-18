# Native worksheet execution: EXP-ECDLP-417a94

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Source experiment: EXP-ECDLP-f7310e. Original approved frozen finite worksheet. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.

Hypothesis `H-ECDLP-cf422c`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-40d618 | output_validated | 7.062644 | 6.299678000000001 | 169021440 |
| RUN-ECDLP-e3586e | output_validated | 7.408159 | 6.655797 | 169000960 |

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
        "rows": [
          {
            "defect": 10,
            "defect_remainder": 0,
            "gap": 30,
            "lambda": 2,
            "lhs": -4,
            "ref_cross": 26,
            "ref_remainder": 1,
            "rhs": 26,
            "three_times_defect": 30,
            "x": 2,
            "x_cross": 8,
            "y": 1,
            "y_gap": 60
          },
          {
            "defect": 65,
            "defect_remainder": 0,
            "gap": 195,
            "lambda": 1,
            "lhs": 1,
            "ref_cross": 36,
            "ref_remainder": 1,
            "rhs": 196,
            "three_times_defect": 195,
            "x": 4,
            "x_cross": 16,
            "y": 2,
            "y_gap": 195
          }
        ]
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-40d618"
  },
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "rows": [
          {
            "defect": 10,
            "defect_remainder": 0,
            "gap": 30,
            "lambda": 2,
            "lhs": -4,
            "ref_cross": 26,
            "ref_remainder": 1,
            "rhs": 26,
            "three_times_defect": 30,
            "x": 2,
            "x_cross": 8,
            "y": 1,
            "y_gap": 60
          },
          {
            "defect": 65,
            "defect_remainder": 0,
            "gap": 195,
            "lambda": 1,
            "lhs": 1,
            "ref_cross": 36,
            "ref_remainder": 1,
            "rhs": 196,
            "three_times_defect": 195,
            "x": 4,
            "x_cross": 16,
            "y": 2,
            "y_gap": 195
          }
        ]
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-e3586e"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-417a94/runs/RUN-ECDLP-40d618`; archive `65db23d06d9bce972f89c112c00a3b9d79fc5a48`.
- `experiments/EXP-ECDLP-417a94/runs/RUN-ECDLP-e3586e`; archive `65db23d06d9bce972f89c112c00a3b9d79fc5a48`.
