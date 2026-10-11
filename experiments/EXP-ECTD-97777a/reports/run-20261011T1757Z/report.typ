#set page(paper: "a4", margin: 1.6cm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: none)

#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-ECTD-97777a — run observation report]\
  #text(size: 9pt, fill: rgb("555555"))[RUN-ECTD-63f478 · 2026-10-11 17:57 UTC]
]

#block(fill: rgb("eef4fb"), inset: 9pt, radius: 4pt)[
  *Observations only.* The supervisor created the run envelope and stopped in the child-process pre-execution hook. The producer and checker did not execute, so no census values or scientific controls were measured.
]

= Bound execution

#table(
  columns: (28%, 72%),
  inset: 5pt,
  align: (left, left),
  [*Field*], [*Recorded value*],
  [Goal], [`GOAL-ECTD-001`],
  [Experiment], [`EXP-ECTD-97777a`],
  [Plan], [`trial-plan-v2.json`, SHA-256 `02fa1006…`],
  [Correction], [`CORR-20261011-f18bdf`],
  [Task / epoch], [`TASK-20261011-4b3aad` / `1`],
  [Run], [`RUN-ECTD-63f478`],
  [Host], [Darwin; Python 3.12.8],
  [Elapsed wall time], [0.014 seconds (derived from recorded start and finish timestamps)],
)

= Exact execution boundary

The producer command was `python3 experiments/EXP-ECTD-97777a/implementation/run.py --run-dir experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478`. The planned checker was `python3 experiments/EXP-ECTD-97777a/implementation/check.py experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478`.

The sealed receipt records `status = infrastructure_error`, `detail = Exception occurred in preexec_fn.`, and null producer and checker return codes. Standard output, standard error, and both checker logs are empty. `manifest.yaml` and `raw-result.json` were not created.

The frozen protocol parameters were not reached: the fixed ordinary field is `F_89`, with `a=b=1`, the declared unordered-pair eligibility/order, and the separate permutation-label null. No controls were measured.

= Visual record

There were fewer than two comparable recorded values, so the accompanying visual is an execution-boundary diagram rather than a numerical graph. It shows the frozen plan, supervisor envelope, pre-execution stop, and absent producer/checker outputs.

#figure(
  image("graph.svg", width: 100%),
  caption: [Execution boundary for `RUN-ECTD-63f478`; source data: `graph-data.json` and sealed run artifacts. Recorded comparable values: 0.]
)

= Limitations and artifacts

This report records an operational stop only. It makes no mathematical inference and does not change any research state. The source Markdown report and all sealed run receipts remain beside this PDF. The predecessor frozen plan and pointer queue were not edited.

#table(
  columns: (35%, 65%),
  inset: 4pt,
  [*Artifact*], [*Path*],
  [Execution receipt], [`experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478/execution-receipt.json`],
  [Launch envelope], [`experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478/launch.json`],
  [Environment], [`experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478/environment.json`],
  [Correction], [`ledger/corrections/CORR-20261011-f18bdf.yaml`],
)
