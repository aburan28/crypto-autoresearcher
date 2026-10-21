#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= EXP-ICPERF-9cd390: build launch failed
This report describes execution outputs only. It makes no scientific verdict or claim.

*Run:* RUN-ICPERF-caa0c1. *Hypothesis:* H-ICPERF-b3d1a4.
*Goal:* GOAL-ICPERF-e6b6a4.
*Code:* `156f4b271a57d6dc05f901df95ac64dd97555290`.

== Recorded execution
One trial attempted; zero completed; one infrastructure failure; zero timeouts. Nine dependent trials were not launched. The two other selected experiments were not launched after publication was blocked.

The build driver resolved its sibling checkout to `/workspace/crypto`. That directory is absent, so the frozen `run_step.sh`, `sources.sha256`, and `PROTOCOL.md` were unavailable. The frozen sibling protocol commit is `286bc22cc7c4f93a354b667981bf786f2f9fa671`.

Measured child exit code: 2. Runner status: `infrastructure_error`. Checker: not run. No build, scientific measurements, control outcomes, or certificates were produced. This operational failure establishes no mathematical result.

#image("pipeline.svg", width: 100%)

== Command and environment
Supervisor: `PYTHONPATH=src:. python3 tools/experiment_execution.py run --plan experiments/EXP-ICPERF-9cd390/trial-plan.json --owner executor-codex-harness-20261017 --epoch 1`. Child: `python3 experiments/EXP-ICPERF-9cd390/implementation/run.py --step build --run-dir <run-directory>`.

Python 3.12.14 on Linux. The tracked working tree was clean at launch; no dirty-state field was emitted in `environment.json`. The build has no seed. Frozen limits: 14,336 MiB and 3,600 seconds. The container has a 4-core CPU quota and a 16 GiB memory limit. CPU timing and host identity were not recorded.

Measured start: `2026-10-17T15:26:31.293634+00:00`. Measured finish: `2026-10-17T15:26:31.353088+00:00`. Derived elapsed: 0.059454 seconds (finish minus start), including wrapper overhead; this is not a computation benchmark. No uncertainty was recorded.

== Artifacts and publication
Source data: `../../runs/RUN-ICPERF-caa0c1/raw-result.json` and `execution-receipt.json`. The run preserves the exact command, environment, launch record, logs, manifest and SHA-256 receipt. Logs are empty. Full details are in `report.md`. The diagram is used because there are no comparable measurements. No canonical scientific graph changed.

Automatic approval review blocked GitHub publication of the run records, report and ownership release. These remain local. The initial claim was already pushed to `run/harness-20261017-1527`; its local release records failure. No scientific status changed.
