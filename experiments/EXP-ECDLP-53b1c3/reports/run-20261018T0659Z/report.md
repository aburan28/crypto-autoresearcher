# Native worksheet execution: EXP-ECDLP-53b1c3

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Source experiment: EXP-ECDLP-615fcf. Original approved frozen finite worksheet. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.

Hypothesis `H-ECDLP-242aa4`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-ef9a36 | output_validated | 8.272994 | 7.123952999999998 | 168988672 |
| RUN-ECDLP-449da5 | output_validated | 7.148197 | 6.372923 | 169000960 |

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
        "bound": 96,
        "commuting_counts": [
          4,
          4,
          4
        ],
        "commuting_points": [
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ],
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ],
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ]
        ],
        "curve_model": "y^2=x^3+8*x^2+2*x over F11",
        "double_T": [
          5,
          7
        ],
        "gap": 288,
        "nearby_bound": 384,
        "point_count": 12,
        "points": [
          null,
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            5,
            4
          ],
          [
            5,
            7
          ],
          [
            7,
            1
          ],
          [
            7,
            10
          ],
          [
            9,
            3
          ],
          [
            9,
            8
          ],
          [
            10,
            4
          ],
          [
            10,
            7
          ]
        ],
        "witness_left": [
          7,
          1
        ],
        "witness_right": [
          7,
          10
        ]
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-ef9a36"
  },
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "bound": 96,
        "commuting_counts": [
          4,
          4,
          4
        ],
        "commuting_points": [
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ],
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ],
          [
            null,
            [
              0,
              0
            ],
            [
              1,
              0
            ],
            [
              2,
              0
            ]
          ]
        ],
        "curve_model": "y^2=x^3+8*x^2+2*x over F11",
        "double_T": [
          5,
          7
        ],
        "gap": 288,
        "nearby_bound": 384,
        "point_count": 12,
        "points": [
          null,
          [
            0,
            0
          ],
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            5,
            4
          ],
          [
            5,
            7
          ],
          [
            7,
            1
          ],
          [
            7,
            10
          ],
          [
            9,
            3
          ],
          [
            9,
            8
          ],
          [
            10,
            4
          ],
          [
            10,
            7
          ]
        ],
        "witness_left": [
          7,
          1
        ],
        "witness_right": [
          7,
          10
        ]
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-449da5"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-53b1c3/runs/RUN-ECDLP-ef9a36`; archive `02ae61792b58ae70bec1e4657dbb1bf71fdb4e31`.
- `experiments/EXP-ECDLP-53b1c3/runs/RUN-ECDLP-449da5`; archive `02ae61792b58ae70bec1e4657dbb1bf71fdb4e31`.
