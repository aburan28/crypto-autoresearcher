#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-OAKLEY-4276c4

This report records one executed factor-base trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-OAKLEY-d18d58; goal GOAL-ECDLP2M-001; task TASK-20261012-9e8997. The frozen plan requested one `vsub-four-sum` trial on `y^2 + x*y = x^3 + z` at p=5 with modulus `z^25 + z^3 + 1`. The output is `experiments/EXP-OAKLEY-4276c4/runs/RUN-OAKLEY-524738/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner was `python3 experiments/EXP-OAKLEY-4276c4/implementation/run.py --trial-plan experiments/EXP-OAKLEY-4276c4/trial-plan.json --run-dir <run directory>`; the checker was `implementation/check.py <run directory>`. Exact expanded argv is in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 5.124492 seconds, from 2026-10-26 21:16:02.478447 UTC to 21:16:07.602939 UTC. CPU time and host name were not recorded. Platform: Linux, Python 3.11.17. Launch authority commit `5bb4d8c6e7efda227866e27f1c93339943baa7cd`. The supervisor required committed source inputs; full-tree dirty state was not measured.

*Recorded observations.* The raw result records measured four-sum image count 11,968, predicted count 376,992, and denominator 33,554,432. It records `within_factor_2=false` and `beyond_factor_4=true`. The planted checks record factor-base size 23, subfield size 32, `addition_identities=true`, `b_outside_subfield=true`, `subfield_closed=true`, and `planted_ok=true`. Planted point coordinates remain in `raw-result.json`. No numeric uncertainty interval was recorded.

#figure(image("graph.svg", width: 100%), caption: [Measured and predicted image counts recorded for RUN-OAKLEY-524738 (one frozen instance, image elements). Both plotted values are copied into data.json from raw-result.json; no uncertainty interval was recorded.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. This is the frozen p=5 instance only. Raw values, checker logs, environment, and receipt remain in the run directory.
