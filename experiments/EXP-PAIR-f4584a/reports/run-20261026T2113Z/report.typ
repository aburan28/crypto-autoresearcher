#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-PAIR-f4584a

This report records one executed polynomial trial. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-PAIR-0ac6e0; goal GOAL-PAIR-001; task TASK-20261012-739d5b. The frozen plan requested one `cubic-slot-count` trial, with named points (1,4) and (2,8), a smoothness bound of 7, and a declared control point (4,4). The output is `experiments/EXP-PAIR-f4584a/runs/RUN-PAIR-e887a4/`.

*Execution.* One requested, one completed and output validated; zero failed or timed out. The runner command was `python3 experiments/EXP-PAIR-f4584a/implementation/run.py --trial-plan experiments/EXP-PAIR-f4584a/trial-plan.json --run-dir <run directory>`; the checker was `implementation/check.py <run directory>`. Exact argv is in `command.txt` and `manifest.yaml`. No seed is declared. Driver and checker returned 0. Recorded supervisor wall time was 0.139506 seconds, from 2026-10-26 21:13:01.359911 UTC to 21:13:01.499417 UTC. CPU time and host name were not recorded. Platform: Linux, Python 3.11.17. Launch authority commit `5e4b73d75a680087395df61972a8808bfeaea6a5`. The supervisor required committed source inputs; full-tree dirty state was not measured.

*Recorded observations.* At (1,4), the two agreeing evaluators each recorded f=81, g=69, (x+1)^3=125, and x^3+2=129. At (2,8), they each recorded f=648, g=552, (x+1)^3=1000, and x^3+2=1032. For both named points, the raw booleans are `duplicate_accepts=true`, `nearby_accepts=true`, `pair_accepts=false`, and `treatment_accepts=false`. The raw result also records `gap_holds=true`, `planted_ok=true`, `zero_is_not_smooth=true`, and `beyond_pattern=false`. The control point coordinates are recorded; no separate numeric control-point evaluation appears in `raw-result.json`.

#figure(image("graph.svg", width: 100%), caption: [Recorded f and g values at the two named points in RUN-PAIR-e887a4 (n=2 points, polynomial values). The raw result records two agreeing evaluations per value and no uncertainty interval. data.json copies the plotted values from raw-result.json.])

*Certificate and limits.* The manifest records certificate kind `none`; no discrete-log or decomposition claim was made. The run covers the frozen two-point matrix only. Raw values, checker logs, environment, and receipt remain in the run directory.
