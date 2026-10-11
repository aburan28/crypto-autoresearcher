#set page(paper: "a4", margin: 1.6cm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: none)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-ECTD-07b200 — run observation report]\
  #text(size: 9pt, fill: rgb("555555"))[RUN-ECTD-e5714e · 2026-10-11 18:00 UTC]
]
#block(fill: rgb("eef4fb"), inset: 9pt, radius: 4pt)[*Observations only.* The supervisor created the run envelope and stopped in the child-process pre-execution hook. The producer and checker did not execute, so no scan values or scientific controls were measured.]
= Bound execution
#table(columns: (30%, 70%), inset: 5pt, [*Field*], [*Recorded value*], [Goal], [`GOAL-ECTD-001`], [Experiment], [`EXP-ECTD-07b200`], [Plan], [`trial-plan-v2.json`, SHA-256 `203be1db…`], [Correction], [`CORR-20261011-9bb7aa`], [Task / epoch], [`TASK-20261011-358a81` / `1`], [Run], [`RUN-ECTD-e5714e`], [Host], [Darwin; Python 3.12.8], [Elapsed wall time], [0.018 seconds from recorded timestamps])
= Exact execution boundary
The producer command was `python3 experiments/EXP-ECTD-07b200/implementation/run.py --run-dir experiments/EXP-ECTD-07b200/runs/RUN-ECTD-e5714e`. The planned checker was `python3 experiments/EXP-ECTD-07b200/implementation/check.py experiments/EXP-ECTD-07b200/runs/RUN-ECTD-e5714e`.

The sealed receipt records `status = infrastructure_error`, `detail = Exception occurred in preexec_fn.`, and null producer and checker return codes. All four logs are empty. `manifest.yaml` and `raw-result.json` were not created. The finite prime limit, coefficient ranges, all-root selection, p=3 handling, and first-edge controls were not reached.
= Visual record
There were zero comparable recorded values, so the visual is an execution-boundary diagram rather than a numerical graph.
#figure(image("graph.svg", width: 100%), caption: [Execution boundary for `RUN-ECTD-e5714e`; source data: `graph-data.json` and sealed run artifacts. Recorded comparable values: 0.])
= Limitations
This report records an operational stop only. It makes no mathematical inference and does not change any research state. The predecessor plan and pointer queue were not edited.
