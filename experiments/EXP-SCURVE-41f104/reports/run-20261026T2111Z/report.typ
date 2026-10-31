#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-SCURVE-41f104

This report records one executed toy-curve trial. It states no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-SCURVE-a8507f; goal GOAL-SCURVE-873d08; task TASK-20261012-eb1dae. The frozen plan requested one trial, `automorphism-cost-ratio`, comparing the declared main Montgomery parameter A=117050 with a negative control A=0. Its output is in `experiments/EXP-SCURVE-41f104/runs/RUN-SCURVE-5bc4fd/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner command was `python3 experiments/EXP-SCURVE-41f104/implementation/run.py --trial-plan experiments/EXP-SCURVE-41f104/trial-plan.json --run-dir <run directory>` and the checker was `implementation/check.py <run directory>`; exact expanded argv is retained in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 0.140168 seconds, from 2026-10-26 21:11:48.329743 UTC to 21:11:48.469911 UTC. CPU time and host name were not recorded. The platform was Linux with Python 3.11.17. Launch authority commit `c4f07e8dd271698aa471b39118114a2d6ba8ba3d`; relevant source inputs were required to be committed, while full-tree dirty state was not measured.

*Recorded observations.* The main row has automorphism order 2, a defined j-invariant with numerator 20573988602152562580551901739784 and denominator 428146953, and `within_five_percent=true`. The negative control has automorphism order 4, a defined j-invariant represented by numerator -1728 and denominator -1, and `within_five_percent=false`. The raw result also records `toy_order=10007`, `planted_ok=true`, `matrix_holds=true`, `null_within_five_percent=true`, and `beyond_matrix=false`. These are recorded program outputs, with no additional arithmetic inferred here.

#figure(image("graph.svg", width: 100%), caption: [Automorphism orders recorded for the main and negative-control parameters in RUN-SCURVE-5bc4fd (n=2, automorphisms). No uncertainty interval was recorded. The plotted values are copied into data.json from raw-result.json.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. The run covers the frozen toy parameters only. Raw values, checker logs, environment, and receipt are retained in the run directory.
