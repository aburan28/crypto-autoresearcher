# Native worksheet execution: EXP-ECDLP-30277c

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Source experiment: EXP-ECDLP-3365b4. Explicit descriptive successor 3365b4, original c9 ambiguous contract still unchanged. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.

Hypothesis `H-ECDLP-3db46b`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-7727d1 | output_validated | 8.420076 | 7.625571 | 168984576 |
| RUN-ECDLP-2d3b31 | output_validated | 7.488339 | 6.61127 | 169029632 |

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
        "band_high": "697/500",
        "band_high_gap": "3/500",
        "band_low": "451/500",
        "band_low_gap": "1/500",
        "basin_sizes": [
          4,
          2
        ],
        "conventions": [
          {
            "convention": "min(D,tau)",
            "cycle_constant": "81/32",
            "cycle_cost": "9/2",
            "cycle_gap": "713/800",
            "cycle_truncated_sum": 18,
            "lambda_costs": [
              "5/2",
              "101/40",
              "11/4"
            ],
            "path_constant": "25/16",
            "path_cost": "5/2",
            "path_gap": "31/400",
            "path_truncated_sum": 15
          },
          {
            "convention": "min(D+1,tau)",
            "cycle_constant": "121/32",
            "cycle_cost": "11/2",
            "cycle_gap": "1713/800",
            "cycle_truncated_sum": 22,
            "lambda_costs": [
              "17/6",
              "1717/600",
              "187/60"
            ],
            "path_constant": "289/144",
            "path_cost": "17/6",
            "path_gap": "-1321/3600",
            "path_truncated_sum": 17
          }
        ],
        "cover_sizes": [
          4,
          5
        ],
        "cover_union": 6,
        "falsifier": "779/500",
        "intersection": 3,
        "one_minus_lower": "69281/109601",
        "one_minus_upper": "5611771/8877691",
        "path_cover_sets": [
          [
            0,
            1,
            2,
            3
          ],
          [
            1,
            2,
            3,
            4,
            5
          ]
        ],
        "rung_product": 1024,
        "series_partial": "109601/40320",
        "series_strict_bounds": [
          true,
          true
        ],
        "size_sum": 9,
        "spacing_ratio": "3/8",
        "twice_gap": "2/25",
        "uncovered": 2
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-7727d1"
  },
  {
    "metrics": {
      "implementations_agree": true,
      "measurement_valid": true,
      "observations": {
        "band_high": "697/500",
        "band_high_gap": "3/500",
        "band_low": "451/500",
        "band_low_gap": "1/500",
        "basin_sizes": [
          4,
          2
        ],
        "conventions": [
          {
            "convention": "min(D,tau)",
            "cycle_constant": "81/32",
            "cycle_cost": "9/2",
            "cycle_gap": "713/800",
            "cycle_truncated_sum": 18,
            "lambda_costs": [
              "5/2",
              "101/40",
              "11/4"
            ],
            "path_constant": "25/16",
            "path_cost": "5/2",
            "path_gap": "31/400",
            "path_truncated_sum": 15
          },
          {
            "convention": "min(D+1,tau)",
            "cycle_constant": "121/32",
            "cycle_cost": "11/2",
            "cycle_gap": "1713/800",
            "cycle_truncated_sum": 22,
            "lambda_costs": [
              "17/6",
              "1717/600",
              "187/60"
            ],
            "path_constant": "289/144",
            "path_cost": "17/6",
            "path_gap": "-1321/3600",
            "path_truncated_sum": 17
          }
        ],
        "cover_sizes": [
          4,
          5
        ],
        "cover_union": 6,
        "falsifier": "779/500",
        "intersection": 3,
        "one_minus_lower": "69281/109601",
        "one_minus_upper": "5611771/8877691",
        "path_cover_sets": [
          [
            0,
            1,
            2,
            3
          ],
          [
            1,
            2,
            3,
            4,
            5
          ]
        ],
        "rung_product": 1024,
        "series_partial": "109601/40320",
        "series_strict_bounds": [
          true,
          true
        ],
        "size_sum": 9,
        "spacing_ratio": "3/8",
        "twice_gap": "2/25",
        "uncovered": 2
      },
      "prediction_match": true
    },
    "run_id": "RUN-ECDLP-2d3b31"
  }
]
```

The single runtime prediction_match flag compares the original-compatible min(D,tau) arm and the other original predicates. The min(D+1,tau) arm is descriptive and has no separate runtime prediction flag. The original ambiguous c9 contract remains unchanged.

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-30277c/runs/RUN-ECDLP-7727d1`; archive `4b00d91dce8503706f69d1112b2fd53ff1e69305`.
- `experiments/EXP-ECDLP-30277c/runs/RUN-ECDLP-2d3b31`; archive `4b00d91dce8503706f69d1112b2fd53ff1e69305`.
