#set page(paper: "a4", margin: (x: 17mm, y: 15mm))
#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9.5pt)
#set par(justify: true)
= EXP-SEMAEV-6e9dcf run report

*Observation-only run record.* Successor contract for the mtic-010b cell of EXP-SEMAEV-93d5cc (H-SEMAEV-94dab2, GOAL-ECDLP-001). One trial: `RUN-SEMAEV-0e5876`, started 2026-10-19T01:57:06.965854+00:00, status: output_validated; CTRL-LEGACY-REPRO passed; check.py exit 0. No verdict; the evidence review decides.

Recorded: in both arms every ablation solve was capped (B = 52: 13 of 13; B = 115: 12 of 12) and regime (i) with K\* infinite held under every accounting at 16, 20 and 24 bits, equal to the archived RUN-MTIC-010b; CTRL-LEGACY-REPRO, CTRL-ARM-FINGERPRINT and CTRL-REEXTRACT passed. Too few comparable values for a graph in this experiment alone, so a diagram of what ran is given; the cell's values are graphed and tabulated with the other six cells in the parent report `experiments/EXP-SEMAEV-93d5cc/reports/run-20261018T2156Z/report.pdf`.

#figure(image("diagram.svg", width: 100%), caption: [What ran in EXP-SEMAEV-6e9dcf (RUN-SEMAEV-0e5876).])

Sources: `experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/` (launch.json, command.txt, environment.json, arm logs, manifest.yaml, raw-result.json, arms.tar.gz, execution-receipt.json, check.stdout.log).
