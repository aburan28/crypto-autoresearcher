#set page(paper: "a4", margin: 1.7cm)
#set text(font: "Linux Libertine", size: 10pt, lang: "en")
#set heading(numbering: "1.")

= SSIQ supervisor infrastructure report

This is an observation-only report for `EXP-SSIQ-dcb6d6`. It records the
execution boundary reached by `RUN-SSIQ-9fe433`; it does not assign scientific
meaning to the failure and does not change the experiment or hypothesis state.

== Identity and provenance

- *Experiment:* `EXP-SSIQ-dcb6d6`
- *Hypothesis:* `H-SSIQ-4baf2b`
- *Goal:* `GOAL-SSIQ-001`
- *Task:* `TASK-20261011-25a161`
- *Trial:* `geometric-kernel-census`
- *Run:* `RUN-SSIQ-9fe433`
- *Plan:* `experiments/EXP-SSIQ-dcb6d6/trial-plan-d9e39a.json`
- *Plan SHA-256:* `408c5e1eab449f4aade52c4ca9210de7be4be60f431380fe5f63bcc4383fb8b7`
- *Approval:* `DEC-20261010-21d5d6`
- *Authority commit:* `40b3d9ff254d420a939b71e748122375aec8aeec`
- *Run-record commit:* `71e66b14a8`

The frozen plan binds `implementation/run.py` to SHA-256
`64ae4002ba5251ec98ee71e3b2a78f0b1916ef52662e518f38bc2a2be04b9290` and
`implementation/check.py` to SHA-256
`efb75b09b7916d12f421b7f486acd5401c4d7e4009234a49234875b475aa3923`.

== Recorded execution

The supervisor created its run envelope and then failed in the child-process
pre-execution hook. The receipt records:

#table(
  columns: (4.1cm, 10.0cm),
  inset: 5pt,
  table.header[*Item*][*Value*],
  [Status], [`infrastructure_error`],
  [Detail], [`Exception occurred in preexec_fn.`],
  [Start], [`2026-10-11T17:45:13.907789+00:00`],
  [Finish], [`2026-10-11T17:45:13.914642+00:00`],
  [Return code], [`null`],
  [Checker return code], [`null`],
  [Published by supervisor], [`false`],
  [Scientific producer output], [none],
  [Independent checker], [not started],
)

The recorded environment is macOS (`darwin`) with Python 3.13.1. The plan
requested a 4096 MiB per-trial memory limit and a 1800 second watchdog. The
failure occurred before Sage, the producer, or the checker ran; therefore no
kernel counts, closure rows, timings, or reading were produced.

== Artifact boundary

Present in the run directory are `command.txt`, `environment.json`,
`execution-receipt.json`, `launch.json`, `stdout.log`, `stderr.log`,
`check.stdout.log`, and `check.stderr.log`. The declared scientific artifacts
`manifest.yaml` and `raw-result.json` are absent, consistently with the
pre-execution failure. The empty logs are retained exactly.

#figure(
  image("graph.svg", width: 100%),
  caption: [Recorded execution path for `RUN-SSIQ-9fe433`; the run stopped at the platform pre-execution guard.],
)

The diagram is an execution-boundary record, not a quantitative result.

== Reproduction boundary

The consumed run ID is not retried. Any repair of the macOS supervisor/runtime
compatibility must be additive and use a new approved plan and a new run ID.
The Linux-container attempt made before this host receipt also did not reach
the producer because that image invocation lacked the required `git` command;
it is not combined with this run record.

#text(size: 8pt, fill: gray)[Run evidence: `experiments/EXP-SSIQ-dcb6d6/runs/RUN-SSIQ-9fe433/`.]

