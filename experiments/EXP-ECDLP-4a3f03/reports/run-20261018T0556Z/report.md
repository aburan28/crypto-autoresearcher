# Native worksheet execution: EXP-ECDLP-4a3f03

Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.

Hypothesis `H-ECDLP-91699d`; goal `GOAL-ECDLP-001`. Requested 2 trials; native statuses and resources follow.

| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |
| --- | --- | ---: | ---: | ---: |
| RUN-ECDLP-030f1f | output_validated | 3.636633431999144 | 1.443031 | 55087104 |
| RUN-ECDLP-4b5355 | output_validated | 3.125591876998442 | 1.232926 | 55087104 |

All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest's explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.

Complete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.

Recorded metric fields (complete, unchanged):

```json
[
  {
    "metrics": {
      "beta_factor": 3,
      "depth_product": 1024,
      "embed_degree13": 2,
      "factor_product": 6,
      "field13": {
        "B": 6,
        "beta_factor": 3,
        "beta_orbits": 2,
        "difference": 4,
        "embedding_degree": 2,
        "embedding_reason": "least_positive_exponent_verified",
        "embedding_residues": [
          6,
          1
        ],
        "gcd_order_pm1": 1,
        "nonidentity_points": 6,
        "order": 7,
        "p": 13,
        "p_power_minus_one_residue_if_noncoprime": null,
        "sign_factor": 2,
        "sign_pairs": 3,
        "trace": 7
      },
      "field7": {
        "B": 5,
        "beta_factor": 3,
        "beta_orbits": 2,
        "difference": 4,
        "embedding_degree": null,
        "embedding_reason": "noncoprime_base_and_order_no_positive_embedding_degree",
        "embedding_residues": [
          0
        ],
        "gcd_order_pm1": 1,
        "nonidentity_points": 6,
        "order": 7,
        "p": 7,
        "p_power_minus_one_residue_if_noncoprime": 6,
        "sign_factor": 2,
        "sign_pairs": 3,
        "trace": 1
      },
      "grid_cells": 25,
      "implementations_agree": null,
      "prediction_comparison": {
        "beta_factor": true,
        "depth_product": true,
        "embed_degree13": true,
        "factor_product": true,
        "field13_beta_factor": true,
        "field13_sign_factor": true,
        "grid_cells": true,
        "sign_factor": true,
        "third_gap": true,
        "trace7": true
      },
      "previous": null,
      "sign_factor": 2,
      "state": "awaiting_separate_route_b",
      "third_gap": "1/300",
      "trace7": 1
    },
    "run_id": "RUN-ECDLP-030f1f"
  },
  {
    "metrics": {
      "beta_factor": 3,
      "depth_product": 1024,
      "embed_degree13": 2,
      "factor_product": 6,
      "field13": {
        "B": 6,
        "beta_factor": 3,
        "beta_orbits": 2,
        "difference": 4,
        "embedding_degree": 2,
        "embedding_reason": "least_positive_exponent_verified",
        "embedding_residues": [
          6,
          1
        ],
        "gcd_order_pm1": 1,
        "nonidentity_points": 6,
        "order": 7,
        "p": 13,
        "p_power_minus_one_residue_if_noncoprime": null,
        "sign_factor": 2,
        "sign_pairs": 3,
        "trace": 7
      },
      "field7": {
        "B": 5,
        "beta_factor": 3,
        "beta_orbits": 2,
        "difference": 4,
        "embedding_degree": null,
        "embedding_reason": "noncoprime_base_and_order_no_positive_embedding_degree",
        "embedding_residues": [
          0
        ],
        "gcd_order_pm1": 1,
        "nonidentity_points": 6,
        "order": 7,
        "p": 7,
        "p_power_minus_one_residue_if_noncoprime": 6,
        "sign_factor": 2,
        "sign_pairs": 3,
        "trace": 1
      },
      "grid_cells": 25,
      "implementations_agree": true,
      "prediction_comparison": {
        "beta_factor": true,
        "depth_product": true,
        "embed_degree13": true,
        "factor_product": true,
        "field13_beta_factor": true,
        "field13_sign_factor": true,
        "grid_cells": true,
        "sign_factor": true,
        "third_gap": true,
        "trace7": true
      },
      "previous": {
        "native_receipt_sha256": "ac05cd4da725cbb210a75e057dcfa7f8780c3ae4d3df2d53c2525104d8d1c8e2",
        "raw_sha256": "6df561b46e8a264e9ce16675894d739c8245a8e6270da370fdfc790b83344a37",
        "run_id": "RUN-ECDLP-030f1f",
        "trial_id": "route-a"
      },
      "sign_factor": 2,
      "state": "two_separate_route_runs_compared",
      "third_gap": "1/300",
      "trace7": 1
    },
    "run_id": "RUN-ECDLP-4b5355"
  }
]
```

Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.

[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:

- `experiments/EXP-ECDLP-4a3f03/runs/RUN-ECDLP-030f1f`; archive `e798e465f333eb45ec0904acb9a13d2dfafe39a4`.
- `experiments/EXP-ECDLP-4a3f03/runs/RUN-ECDLP-4b5355`; archive `e798e465f333eb45ec0904acb9a13d2dfafe39a4`.
