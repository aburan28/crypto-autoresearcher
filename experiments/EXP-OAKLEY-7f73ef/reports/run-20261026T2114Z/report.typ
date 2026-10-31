#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-OAKLEY-7f73ef

This report records one executed factor-base trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-OAKLEY-020f90; goal GOAL-ECDLP2M-001; task TASK-20261012-e42be3. The frozen plan requested one `subfield-hit-count` trial on `y^2 + x*y = x^3 + z` over the declared p=5 construction with modulus `z^25 + z^3 + 1`. The output is `experiments/EXP-OAKLEY-7f73ef/runs/RUN-OAKLEY-326307/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner was `python3 experiments/EXP-OAKLEY-7f73ef/implementation/run.py --trial-plan experiments/EXP-OAKLEY-7f73ef/trial-plan.json --run-dir <run directory>`; the checker was `implementation/check.py <run directory>`. Exact expanded argv is in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 4.851819 seconds, from 2026-10-26 21:14:17.873903 UTC to 21:14:22.725722 UTC. CPU time and host name were not recorded. Platform: Linux, Python 3.11.17. Launch authority commit `2cafe57c7b72e84a28576fb18e043694e0443c65`. The supervisor required committed source inputs; full-tree dirty state was not measured.

*Recorded observations.* The raw result records factor-base size 23, subfield population 32, and hit count 0. It records predicted probability `1/120`, `within_three_sd=true`, and `beyond_three_sd=false`, without a numeric uncertainty interval. The planted checks record `addition_identities=true`, `b_outside_subfield=true`, `subfield_closed=true`, and `planted_ok=true`. The raw planted point coordinates and doubled coordinates remain in `raw-result.json`.

#figure(image("graph.svg", width: 100%), caption: [Execution diagram for RUN-OAKLEY-326307, copying the one hit count and two declared population sizes from data.json. A diagram is used because the run recorded one hit count and no comparable series or numeric uncertainty interval.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. This is the frozen p=5 instance only. Raw values, checker logs, environment, and receipt remain in the run directory.
