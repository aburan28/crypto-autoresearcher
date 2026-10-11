#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Libertinus Serif", size: 10pt)
#set par(leading: 0.65em)

= Run report: geometric kernel census

This is an observation report for `EXP-SSIQ-dcb6d6`, not an evidence review. It records the one successor execution attempt and its operational stopping point. It does not interpret the mathematical hypothesis or treat the infrastructure failure as a numerical observation.

== Identity and binding

- Experiment: `EXP-SSIQ-dcb6d6`
- Hypothesis: `H-SSIQ-4baf2b`
- Goal: `GOAL-SSIQ-001`
- Trial: `geometric-kernel-census`
- Run: `RUN-SSIQ-e489dd`
- Successor plan: `experiments/EXP-SSIQ-dcb6d6/trial-plan-v2.json`
- Plan SHA-256: `3ea77789652c16e62fc780f0523be088cc6554547a5e89a2969623c5338ecea3`
- Run-record commit: `d4393aa8ea`
- Host/runtime: macOS worktree; supervisor invoked with elevated filesystem access for the shared execution lock
- Dirty state at launch: pre-existing untracked session receipts were present; the run directory itself was created by this attempt

== Exact command and requested scope

The supervisor command was:

#raw("python3 tools/experiment_execution.py run --plan experiments/EXP-SSIQ-dcb6d6/trial-plan-v2.json --owner executor-ssiq-successor --epoch 1", block: true)

The frozen successor trial requested Sage execution of both target and null geometric kernel censuses at characteristic 53 for prime degrees 3, 5, and 7. The plan has no random seed. The declared memory guard was 4096 MB and the watchdog was 1800 seconds. The run was admitted with the published executor claim at epoch 1.

== Recorded execution path

#image("pipeline.svg", width: 100%)

The supervisor wrote `launch.json`, `command.txt`, `environment.json`, the four stdout/stderr log files, and `execution-receipt.json`. The receipt records `status: infrastructure_error`, a null process return code, and `detail: Exception occurred in preexec_fn`. The Sage process therefore did not begin, and the checker was not reached. The raw result, manifest, target counts, null counts, per-degree counts, threshold comparisons, control outcomes, wall time, CPU time, and peak memory are missing from this attempt.

The diagram is derived directly from `pipeline-data.json`, `launch.json`, and `execution-receipt.json`; it contains no inferred measurement.

== Artifact index

- Run directory: `experiments/EXP-SSIQ-dcb6d6/runs/RUN-SSIQ-e489dd/`
- Execution receipt: `execution-receipt.json`
- Launch provenance: `launch.json`
- Command: `command.txt`
- Environment/source binding: `environment.json`
- Process logs: `stdout.log`, `stderr.log`
- Checker logs: `check.stdout.log`, `check.stderr.log`
- Graph source/data: `pipeline.svg`, `pipeline-data.json`

The run directory and this report describe an infrastructure event only. No scientific value was produced by this attempt, and no hypothesis or experiment status was changed.
