#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-SCURVE-7003fe

This report records outputs from one executed toy-curve trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-SCURVE-01f984; goal GOAL-SCURVE-873d08; task TASK-20261012-a25520. The frozen plan requested one trial, `transfer-trigger-matrix`, with three nonsingular short-Weierstrass curves and one destroyed-trace null. Embedding-degree search was bounded at 12.

*Run record.* `experiments/EXP-SCURVE-7003fe/runs/RUN-SCURVE-acab50/`. The runner command was `python3 experiments/EXP-SCURVE-7003fe/implementation/run.py --trial-plan experiments/EXP-SCURVE-7003fe/trial-plan.json --run-dir <run directory>`; the checker used `implementation/check.py <run directory>`. Exact expanded argv is retained in `command.txt` and `manifest.yaml`. No random seed is declared in this plan.

*Execution.* One requested, one completed and output validated; zero failed or timed out. Driver and checker exit codes were both 0. Recorded supervisor wall time was 0.192027 seconds, from 2026-10-26 21:08:43.044015 UTC to 21:08:43.236042 UTC. CPU time and host name were not recorded. Platform was Linux with Python 3.11.17. Launch authority commit `fbfff85d5adcf3156923742a2a5aa0f8241aeed4`; source hashes and environment are in `environment.json`. The supervisor required committed source inputs. A complete working-tree dirty-state measurement was not recorded.

*Recorded observations.* For `(p,A,B)=(5,3,2)`, point count was 5, trace 1, and the predicate triggered. For `(5,0,1)`, point count was 6, trace 0, and the predicate triggered. For `(17,3,5)`, point count was 23, trace -5, and the predicate did not trigger. Both point-count methods agreed in each row; the nonsingularity and Hasse checks were true. The synthetic null `(p,order,trace)=(5,5,0)` did not trigger. The raw result recorded `planted_ok=true`, `matrix_holds=true`, and `beyond_matrix=false`; these are program outputs, not an evidence verdict.

#figure(image("graph.svg", width: 100%), caption: [Point counts recorded for the three curves in RUN-SCURVE-acab50 (n=3, points). The synthetic null is excluded because it is a supplied tuple, not a counted curve. No uncertainty interval was recorded.])

*Certificate and limits.* `manifest.yaml` records certificate kind `none`, with no discrete-log or decomposition claim. The run covers only the three declared curves and one null tuple. Raw observations, checks, commands, and receipt are preserved in the run directory. The graph is generated from `data.json` by `graph.py`; its values are copied from `raw-result.json` without further calculation.
