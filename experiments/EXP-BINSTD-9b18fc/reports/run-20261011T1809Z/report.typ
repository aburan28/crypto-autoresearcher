#set page(paper: "a4", margin: 1.6cm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: none)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-BINSTD-9b18fc — run observation report]\
  #text(size: 9pt, fill: rgb("555555"))[Stage 0 RUN-BINSTD-54a677 · 2026-10-11 18:09 UTC]
]
#block(fill: rgb("eef4fb"), inset: 9pt, radius: 4pt)[*Observations only.* Stage 0 stopped in the supervisor pre-execution hook. Stage 1 remained dependency-gated; no catalog, panel, or scientific result was produced.]
= Bound execution
#table(columns: (32%, 68%), inset: 5pt, [*Field*], [*Recorded value*], [Goal], [`GOAL-ECDLP2M-001`], [Experiment], [`EXP-BINSTD-9b18fc`], [Plan], [`trial-plan-v2.json`, SHA-256 `b6f5786e…`], [Correction], [`CORR-20261011-dace28`], [Task / epoch], [`TASK-20261011-903edd` / `1`], [Stage 0 run], [`RUN-BINSTD-54a677`], [Stage 1 run], [`RUN-BINSTD-6e9fde` — waiting], [Host], [Darwin; Python 3.12.8])
= Stage boundary
The Stage 0 producer was `python3 experiments/EXP-BINSTD-9b18fc/implementation/run.py --stage 0 --trial-plan experiments/EXP-BINSTD-9b18fc/trial-plan-v1.json --run-dir experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-54a677`. The sealed receipt records `status = infrastructure_error`, `detail = Exception occurred in preexec_fn.`, and null producer/checker return codes. All logs are empty and the run manifest/raw result are absent.

Stage 1 was not attempted because its frozen dependency was not validated. The Stage 0 catalog, twin probe, admission floors, Stage 1 panels, and `RESULTS.md` were not reached.
= Visual record
There were zero comparable measurements, so the visual is a stage-boundary diagram rather than a numerical graph.
#figure(image("graph.svg", width: 100%), caption: [Stage boundary for `EXP-BINSTD-9b18fc`; source data: `graph-data.json` and sealed supervisor artifacts. Recorded comparable values: 0.])
= Limitations
This report records an operational stop only. It makes no mathematical inference and does not change any research state. The original plan and legacy design queue were not edited.
