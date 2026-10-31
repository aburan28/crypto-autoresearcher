#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-CSIDH-72413d

This report records one executed toy-curve trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-CSIDH-695382; goal GOAL-CSIDH-001; task TASK-20261012-6757e8. The frozen plan requested one `kronecker-edge` trial at p=47, comparing declared Kronecker splitting degrees with rational kernel edge degrees for the stated toy parameters. The output is `experiments/EXP-CSIDH-72413d/runs/RUN-CSIDH-92d9d9/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner was `python3 experiments/EXP-CSIDH-72413d/implementation/run.py --trial-plan experiments/EXP-CSIDH-72413d/trial-plan.json --run-dir <run directory>`; the checker was `implementation/check.py <run directory>`. Exact expanded argv is in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 8.861923 seconds, from 2026-10-26 21:19:29.974354 UTC to 21:19:38.836277 UTC. CPU time and host name were not recorded. Platform: Linux, Python 3.11.17. Launch authority commit `d66335a2b7c2d61e495e7a06d0f7e6c1fd0b96a7`. The supervisor required committed source inputs; full-tree dirty state was not measured.

*Recorded observations.* The raw result records splitting degrees [3,7] and edge degrees [3,7], with symmetric difference 0. It records `curve_A=1`, `ordinary_A=3`, `matrix_holds=true`, `planted_ok=true`, and `beyond_matrix=false`. No numeric uncertainty interval was recorded.

#figure(image("graph.svg", width: 100%), caption: [Recorded degree sets for RUN-CSIDH-92d9d9 (n=2 degrees in each set). Values and symmetric difference are copied into data.json from raw-result.json; no uncertainty interval was recorded.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. This is the frozen p=47 instance only. Raw values, checker logs, environment, and receipt remain in the run directory.
