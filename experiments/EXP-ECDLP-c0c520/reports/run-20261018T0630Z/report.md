# Native worksheet execution: EXP-ECDLP-c0c520

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Source experiment: EXP-ECDLP-95f69f. Original approved frozen finite worksheet. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.

Hypothesis `H-ECDLP-7bd5f5`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-36eff6 | output_validated | 8.015864 | 6.923945 | 169021440 |
| RUN-ECDLP-f5bde2 | output_validated | 6.801209 | 6.210864000000001 | 168996864 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "mod17_image_sizes": [
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2
        ],
        "mod17_images": [
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ]
        ],
        "mod17_mismatches": 136,
        "mod17_pairs": 289,
        "mod4_image_sizes": [
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1
        ],
        "mod4_images": [
          [
            0
          ],
          [
            1
          ],
          [
            2
          ],
          [
            3
          ],
          [
            1
          ],
          [
            2
          ],
          [
            3
          ],
          [
            0
          ],
          [
            2
          ],
          [
            3
          ],
          [
            0
          ],
          [
            1
          ],
          [
            3
          ],
          [
            0
          ],
          [
            1
          ],
          [
            2
          ]
        ],
        "mod4_mismatches": 0,
        "mod4_pairs": 16,
        "residue_pairs": 16
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-36eff6"
  },
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "mod17_image_sizes": [
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2
        ],
        "mod17_images": [
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            1,
            2
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            2,
            3
          ],
          [
            0,
            3
          ],
          [
            0,
            1
          ],
          [
            1,
            2
          ]
        ],
        "mod17_mismatches": 136,
        "mod17_pairs": 289,
        "mod4_image_sizes": [
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1,
          1
        ],
        "mod4_images": [
          [
            0
          ],
          [
            1
          ],
          [
            2
          ],
          [
            3
          ],
          [
            1
          ],
          [
            2
          ],
          [
            3
          ],
          [
            0
          ],
          [
            2
          ],
          [
            3
          ],
          [
            0
          ],
          [
            1
          ],
          [
            3
          ],
          [
            0
          ],
          [
            1
          ],
          [
            2
          ]
        ],
        "mod4_mismatches": 0,
        "mod4_pairs": 16,
        "residue_pairs": 16
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-f5bde2"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-c0c520/runs/RUN-ECDLP-36eff6`; archive `a8bd3f444c96ca0dc7f3bec846c6b2bdc443b3be`.
- `experiments/EXP-ECDLP-c0c520/runs/RUN-ECDLP-f5bde2`; archive `a8bd3f444c96ca0dc7f3bec846c6b2bdc443b3be`.
