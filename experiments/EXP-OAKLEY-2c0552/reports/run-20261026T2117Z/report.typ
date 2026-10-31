#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-OAKLEY-2c0552

This report records one executed toy-curve identity trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-OAKLEY-2fae30; goal GOAL-ECDLP2M-001; task TASK-20261012-4cebfe. The frozen plan requested one `chain-s3-identity` trial on `y^2 = x^3 + x + 1` over F_17, comparing chained S3 with four-point sums on the declared ordered quadruples. The output is `experiments/EXP-OAKLEY-2c0552/runs/RUN-OAKLEY-a451a8/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner was `python3 experiments/EXP-OAKLEY-2c0552/implementation/run.py --trial-plan experiments/EXP-OAKLEY-2c0552/trial-plan.json --run-dir <run directory>`; the checker was `implementation/check.py <run directory>`. Exact expanded argv is in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 0.389447 seconds, from 2026-10-26 21:17:29.752320 UTC to 21:17:30.141767 UTC. CPU time and host name were not recorded. Platform: Linux, Python 3.11.17. Launch authority commit `ebcf5f569f8b9ff3f891362f71df5f87dc0f2931`. The supervisor required committed source inputs; full-tree dirty state was not measured.

*Recorded observations.* The raw result records 9 points on the curve, 83,521 ordered quadruples, and 0 disagreements. It records `planted_ok=true` and a planted tuple with `x1=0`, `x2=4`, `x_sum=13`, and `s3=0`. No numeric uncertainty interval was recorded.

#figure(image("graph.svg", width: 100%), caption: [Execution diagram for RUN-OAKLEY-a451a8, copying the one disagreement count and two population sizes from data.json. A diagram is used because there is one disagreement count, without a comparable series or numeric uncertainty interval.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. This is the frozen F_17 instance only. Raw values, checker logs, environment, and receipt remain in the run directory.
