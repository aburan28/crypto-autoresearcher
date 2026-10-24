# Native worksheet execution: EXP-ECDLP-911c16

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-208a11`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-5febcb | output_validated | 1.233303891000105 | 1.2267179999999998 | 55115776 |
| RUN-ECDLP-cfbd49 | output_validated | 1.0059735690010712 | 1.006148 | 55115776 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "bad_label": "does_not_suffice",
      "bad_ratio": "1/2",
      "bad_remaining": "0/1",
      "good_ratio": "1/8",
      "good_remaining": "3/4",
      "implementations_agree": null,
      "numeric_bad_off": "1/1",
      "numeric_good_off": "1/4",
      "numeric_lower": "2/1",
      "numeric_matches_symbolic": true,
      "prediction_comparison": {
        "bad_label": true,
        "bad_ratio": true,
        "bad_remaining": true,
        "good_ratio": true,
        "good_remaining": true,
        "numeric_matches_symbolic": true
      },
      "previous": null,
      "state": "awaiting_separate_route_b"
    },
    "run_id": "RUN-ECDLP-5febcb"
  },
  {
    "metrics": {
      "bad_label": "does_not_suffice",
      "bad_ratio": "1/2",
      "bad_remaining": "0/1",
      "good_ratio": "1/8",
      "good_remaining": "3/4",
      "implementations_agree": true,
      "numeric_bad_off": "1/1",
      "numeric_good_off": "1/4",
      "numeric_lower": "2/1",
      "numeric_matches_symbolic": true,
      "prediction_comparison": {
        "bad_label": true,
        "bad_ratio": true,
        "bad_remaining": true,
        "good_ratio": true,
        "good_remaining": true,
        "numeric_matches_symbolic": true
      },
      "previous": {
        "native_receipt_sha256": "2207e94e461220b00dad07555e6e63da5ebcd5ff1a561ec2b1ce7a84d3ea9a0f",
        "raw_sha256": "e05d43b9b64ef5736013231bf15b6fa06a96fe9dbc4304e48ebc60d322701ed4",
        "run_id": "RUN-ECDLP-5febcb",
        "trial_id": "route-a"
      },
      "state": "two_separate_route_runs_compared"
    },
    "run_id": "RUN-ECDLP-cfbd49"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-911c16/runs/RUN-ECDLP-5febcb`; archive `22be797d6bb21659979666341b4c57bcee033eaa`.
- `experiments/EXP-ECDLP-911c16/runs/RUN-ECDLP-cfbd49`; archive `22be797d6bb21659979666341b4c57bcee033eaa`.
