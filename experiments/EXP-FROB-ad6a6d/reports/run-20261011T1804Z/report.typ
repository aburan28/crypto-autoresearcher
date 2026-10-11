#set page(paper: "a4", margin: 1.6cm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: none)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-FROB-ad6a6d — run observation report]\
  #text(size: 9pt, fill: rgb("555555"))[RUN-FROB-026551 · 2026-10-11 18:04 UTC]
]
#block(fill: rgb("eef4fb"), inset: 9pt, radius: 4pt)[*Observations only.* The supervisor created the run envelope and stopped in the child-process pre-execution hook. The producer and checker did not execute, so no field or chord-image values were measured.]
= Bound execution
#table(columns: (30%, 70%), inset: 5pt, [*Field*], [*Recorded value*], [Goal], [`GOAL-FROB-6333a9`], [Experiment], [`EXP-FROB-ad6a6d`], [Plan], [`trial-plan-v2.json`, SHA-256 `05f75ed5…`], [Correction], [`CORR-20261011-954734`], [Task / epoch], [`TASK-20261011-afcf52` / `1`], [Run], [`RUN-FROB-026551`], [Host], [Darwin; Python 3.12.8], [Elapsed wall time], [0.012 seconds from recorded timestamps])
= Exact execution boundary
The producer command was `python3 experiments/EXP-FROB-ad6a6d/implementation/run.py --run-dir experiments/EXP-FROB-ad6a6d/runs/RUN-FROB-026551`. The planned checker was `python3 experiments/EXP-FROB-ad6a6d/implementation/check.py experiments/EXP-FROB-ad6a6d/runs/RUN-FROB-026551`.

The sealed receipt records `status = infrastructure_error`, `detail = Exception occurred in preexec_fn.`, and null producer and checker return codes. All four logs are empty. `manifest.yaml`, `raw-result.json`, and `reading.yaml` were not created. The F_7^3 construction and slope-image comparison were not reached.
= Visual record
There were zero comparable recorded values, so the visual is an execution-boundary diagram rather than a numerical graph.
#figure(image("graph.svg", width: 100%), caption: [Execution boundary for `RUN-FROB-026551`; source data: `graph-data.json` and sealed run artifacts. Recorded comparable values: 0.])
= Limitations
This report records an operational stop only. It makes no mathematical inference and does not change any research state. The predecessor plan and pointer queue were not edited.
