#set page(
  paper: "a4",
  margin: (x: 1.6cm, y: 1.4cm),
  numbering: "1",
)
#set text(font: "DejaVu Sans", size: 9pt, lang: "en")
#set par(leading: 0.62em)

#let label(text) = text(fill: rgb("304a70"), weight: "bold")

= EXP-AUXIN-fef6ac run report

*Observation record only.* This report describes one attempted Stage 0 launch. It does not evaluate the hypothesis, assign evidence strength, or change any research status. The supervisor stopped in macOS `preexec_fn` before the scientific child process began.

== Identity and execution

#table(
  columns: (2.8cm, 1fr, 2.8cm, 1fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("c7d0df"),
  fill: (x, y) => if y == 0 { rgb("eef2f8") } else { white },
  [*Experiment*], [EXP-AUXIN-fef6ac], [*Hypothesis*], [H-AUXIN-9d9ee0],
  [*Goal*], [GOAL-AUXIN-a93442], [*Task*], [TASK-20261004-f88f65],
  [*Run*], [RUN-AUXIN-69eec8], [*Approval*], [DEC-20261004-927012],
  [*Plan SHA-256*], [4e0a325e…fdace1f2c6724834], [*Platform*], [darwin],
  [*Python*], [3.13.1], [*Status*], [infrastructure_error],
)

The first trial started at `2026-10-11T19:48:35.407017Z` and the receipt finished at `2026-10-11T19:48:35.437853Z`. The runner recorded source commit `74de5c3280d161fba4073c68c4f671415966f25a`. The run-record commit is `d8d90a393e`.

== Requested pipeline

The frozen plan requested Stage 0 `RUN-AUXIN-69eec8`, followed by dependent Stage 1 `RUN-AUXIN-aa27b4`. The exact supervisor command was:

#raw(
  "/usr/local/bin/python3 tools/experiment_execution.py run --plan experiments/EXP-AUXIN-fef6ac/trial-plan-v1.json --owner executor-auxin-fef6ac --epoch 1",
  block: true,
  lang: "text",
)

#image("graph.svg", width: 17.8cm)

#align(center)[
  *Figure 1.* Execution diagram for `RUN-AUXIN-69eec8`; the failure occurred before the scientific child process.
]

== Recorded result and missing data

#table(
  columns: (5.2cm, 4.8cm, 1fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("c7d0df"),
  [*Field*], [*Recorded value*], [*Source*],
  [Supervisor status], [infrastructure_error], [execution-receipt.json],
  [Failure detail], [Exception occurred in preexec_fn.], [execution-receipt.json],
  [Child return code], [null], [execution-receipt.json],
  [Checker return code], [null], [execution-receipt.json],
  [Scientific program started], [false], [empty child logs and missing raw result],
  [Trials requested], [2], [trial-plan-v1.json],
  [Run directories materialized], [1], [execution-receipt.json],
  [Output validated], [0], [supervisor summary],
)

The runner produced launch, receipt, command, environment, stdout, stderr, and checker-log files for Stage 0. It did not produce `manifest.yaml`, `raw-result.json`, Stage 0 freeze files, Stage 1 census files, or `RESULTS.md`. No scientific metric, control outcome, uncertainty, certificate, wall-time value, or CPU-time value was recorded.

The report's graph source/data are `graph.svg` and `graph-data.json`. The corresponding machine-readable receipt is `../../runs/RUN-AUXIN-69eec8/execution-receipt.json`.

== Runtime note

The frozen plan was not edited and no replacement run ID was minted. A Linux recovery was attempted through the pinned local container path, but the Docker API did not answer and no configured RunPod executor or remote connector was available in this session. That attempt produced no additional run directory. This report records the host-side infrastructure outcome only.
