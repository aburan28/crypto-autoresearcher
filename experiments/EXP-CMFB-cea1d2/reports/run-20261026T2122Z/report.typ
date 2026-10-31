#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)

= Run report: EXP-CMFB-cea1d2

This report records a stopped execution attempt. It makes no verdict about the hypothesis; evidence review is separate.

*Identity and scope.* Hypothesis H-CMFB-9b2eed; task TASK-20261015-1c0251. The specification deliberately omits a goal ID. The frozen plan requested eight dependent toy-size trials for family-level coverage and scan efficiency. This session wrote one run directory: `experiments/EXP-CMFB-cea1d2/runs/RUN-CMFB-2373be/` for `t1-inventory`.

*Execution.* One trial started and failed with `infrastructure_error`; zero trials completed or output validated, and seven remained waiting on dependencies. The exact command was `python3 experiments/EXP-CMFB-cea1d2/implementation/driver.py --trial t1-inventory --run-dir <run directory>`; expanded argv is in `command.txt`. No seed is declared for this trial. Driver exit code was 1; no checker ran. The receipt recorded start 2026-10-26 21:22:16.535706 UTC and finish 21:22:16.700928 UTC. It did not record separate wall or CPU time or a host name. Platform and Python version are in `environment.json`; launch authority commit `a12f7d47cd91fdab370251d325b68e7f8bc4b952`.

*Failure record.* `stderr.log` contains `ModuleNotFoundError: No module named 'numpy'` while importing the frozen driver. No `raw-result.json` or `manifest.yaml` was produced. The supervisor marks `t1-inventory` as needing reconciliation; its seven dependents were not launched. There are no measurement values, controls, or certificate outcomes to report. No scientific conclusion follows from this process failure.

#figure(image("graph.svg", width: 100%), caption: [Recorded execution flow for the one started trial RUN-CMFB-2373be and its seven unstarted dependents. The diagram copies the supervisor counts in data.json; no comparable measurements were recorded.])

*Limits.* The eight-trial measurement is incomplete. The run directory preserves the launch, environment, stderr, checker placeholders, and execution receipt. It is not a completed measurement run.
