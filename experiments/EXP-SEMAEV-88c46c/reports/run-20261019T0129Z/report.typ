#set page(paper: "a4", margin: (x: 17mm, y: 15mm))
#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9.5pt)
#set par(justify: true)
= EXP-SEMAEV-88c46c run report

*Observation-only run record.* Successor contract for the mtic-010b cell of EXP-SEMAEV-93d5cc (H-SEMAEV-94dab2, GOAL-ECDLP-001). One trial: `RUN-SEMAEV-980e8c`, started 2026-10-19T01:30:34.382405+00:00, status: interrupted (container restart at about 01:45 UTC, about 16 min in; no receipt, no aggregation). No verdict; the evidence review decides.

The run was lost to a container restart and is preserved as an interrupted, non-evidence attempt; amendment `AMD-EXP-SEMAEV-88c46c-20261019-successor` moves the unchanged cell to EXP-SEMAEV-6e9dcf (RUN-SEMAEV-0e5876). Too few comparable values for a graph in this experiment alone, so a diagram of what ran is given; the cell's values are graphed and tabulated with the other six cells in the parent report `experiments/EXP-SEMAEV-93d5cc/reports/run-20261018T2156Z/report.pdf`.

#figure(image("diagram.svg", width: 100%), caption: [What ran in EXP-SEMAEV-88c46c (RUN-SEMAEV-980e8c).])

Sources: `experiments/EXP-SEMAEV-88c46c/runs/RUN-SEMAEV-980e8c/` (launch.json, command.txt, environment.json, arm logs).
