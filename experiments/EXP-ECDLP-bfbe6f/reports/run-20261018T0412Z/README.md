# EXP-ECDLP-bfbe6f: original native execution observation

Observations only. No scientific verdict, support/weaken decision or attack claim is made. The driver and checker completed; the native supervisor rejected the obsolete manifest.

- Hypothesis: H-ECDLP-cba67a; goal: GOAL-ECDLP-001.
- Run: [RUN-ECDLP-8f5190](../../runs/RUN-ECDLP-8f5190/execution-receipt.json); one requested deterministic trial, driver/checker exits 0, supervisor-valid 0, invalid-output 1, no recorded timeout.
- Code commit: `54e902764866793036285e3d4368e483db6bb4cc` from the supervisor environment, not from the incomplete original manifest. Dirty-tree status and CPU/GPU model were not recorded.
- Native status: `invalid_output`. Exact failure: manifest.yaml fails the run schema (tools/validate_ledger.py): bad run id None; run missing required field 'id'; run missing required field 'status'; run missing required field 'code'; run missing required field 'environment'; run missing required field 'inputs'; run missing required field 'timing'; run missing required field 'result'; run.code.commit missing (not reproducible); run.code.command missing (not reproducible); run.result.certificate.kind must be one of discrete_log|decomposition|none
- Declared memory: 256MiB (limit, not measured peak). CPU seconds and peak RSS are unrecorded.
- Derived supervisor interval: 0.112187seconds = 2026-10-18T04:12:41.867048+00:00 minus 2026-10-18T04:12:41.754861+00:00. One deterministic observation, no uncertainty interval or speed comparison.
- Recorded original metrics: `{"beyond_matrix": false, "matrix_holds": true, "planted_ok": true}`. These are retained observations, not admitted scientific evidence.
- Certificate: missing in the obsolete manifest; the raw worksheet claims no attack. No certificate or formal verification is inferred.

Exact original inputs:

```json
{
  "prime": 41,
  "curve": "y^2 = x^3 + x + 2",
  "points": [
    [
      0,
      17
    ],
    [
      1,
      2
    ],
    [
      3,
      14
    ],
    [
      5,
      3
    ]
  ],
  "pairs": [
    [
      0,
      1
    ],
    [
      0,
      3
    ],
    [
      0,
      5
    ],
    [
      1,
      3
    ],
    [
      1,
      5
    ],
    [
      3,
      5
    ]
  ],
  "third_coordinate": 7,
  "expected_at_seven": [
    13,
    33,
    35,
    11,
    28,
    38
  ],
  "named_future_run_slot": "RUN-ECDLP-8f5190"
}
```

Exact frozen command argv (working directory was repository root):

```json
[
  "python3",
  "experiments/EXP-ECDLP-bfbe6f/implementation/run.py",
  "--trial-plan",
  "experiments/EXP-ECDLP-bfbe6f/trial-plan.json",
  "--run-dir",
  "/workspace/crypto-autoresearcher/experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190"
]
```

The native checker ran the original frozen controls, with exit 0. Its original scope and all controls/seeds are retained in [facts.json](facts.json) and the unchanged [specification](../../specification.yaml). No new random draw or unregistered re-scoring occurred.

![What actually ran and where native validation stopped](diagram.svg)

The diagram is used because this run has one wall interval and no two comparable scientific measurements; exit codes describe process outcomes. Caption: RUN-ECDLP-8f5190, n=1 deterministic worksheet, no reported uncertainty. [Editable graph](diagram.dot), [PDF report](report.pdf). No canonical scientific graph changes: the only new observation is operational manifest rejection.

Fresh reproduction, if separately approved and natively admitted, uses EXP-ECDLP-3521b9 / RUN-ECDLP-03ccb4; it preserves the original raw reading as in-sample calibration. The original run remains immutable invalid_output and needs_reconciliation.
