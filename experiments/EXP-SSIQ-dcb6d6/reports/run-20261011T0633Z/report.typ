#set page(paper: "a4", margin: 1.7cm)
#set text(font: "Linux Libertine", size: 10pt, lang: "en")
#set heading(numbering: "1.")

= SSIQ Linux successor run report

This is an observation-only report for `EXP-SSIQ-dcb6d6`; it records the files and process events produced by `RUN-SSIQ-16ccff`. It does not review the hypothesis, assign scientific meaning to the failure, or change any research state. The process entered the Sage implementation and stopped during prime-degree isogeny enumeration before producing the experiment's raw result.

== Identity and provenance

- *Experiment:* `EXP-SSIQ-dcb6d6`
- *Hypothesis:* `H-SSIQ-4baf2b`
- *Goal:* `GOAL-SSIQ-001`
- *Run:* `RUN-SSIQ-16ccff`
- *Trial:* `geometric-kernel-census`
- *Run directory:* `experiments/EXP-SSIQ-dcb6d6/runs/RUN-SSIQ-16ccff/`
- *Plan:* `experiments/EXP-SSIQ-dcb6d6/trial-plan-v3.json`
- *Plan SHA-256:* `9767e56f2ac9873d516dffb27a19561ab2e3d788530e203b1766da883323536c`
- *Authority commit:* `953e85012b92f417458fcaba0d243b90fae77b53`
- *Run-record commit:* `e6b2fe5ff2`
- *Release commit:* `57dd954773`

The supervisor recorded a Linux platform, Python `3.12.3`, and the declared source hashes in `environment.json`. The Sage container was `sagemath/sagemath:10.10` on `linux/amd64`; the implementation's Sage version was not reached in a producer report because the producer failed before writing `manifest.yaml`.

== Command, parameters, and controls

The supervisor recorded this implementation command in `command.txt`:

```text
["sage", "-python", "experiments/EXP-SSIQ-dcb6d6/implementation/run.py", "--run-dir", "/Volumes/SSD990-2/.codex/worktrees/3ffc/crypto-autoresearcher/experiments/EXP-SSIQ-dcb6d6/runs/RUN-SSIQ-16ccff"]
```

The frozen plan declared characteristic `53`, prime degrees `3, 5, 7`, geometric closure enumeration, no random seeds, one trial, a 4096 MiB memory limit, and a 1800 second watchdog. The independent checker was declared but was not started because the producer process returned first.

== Run accounting

#table(
  columns: (2.2cm, 2cm, 8.2cm),
  inset: 5pt,
  align: (left, right, left),
  table.header[*Item*][*Recorded value*][*Basis and limitation*],
  [Trials requested], [1], [Frozen trial plan.],
  [Trials completed], [0], [No `raw-result.json` or `manifest.yaml` was written.],
  [Trials failed], [1], [Supervisor `execution-receipt.json`, return code `1`.],
  [Trials timed out], [0], [Recorded `status: infrastructure_error`, with no watchdog expiry.],
  [Measured values], [none], [The producer stopped before the first census quantity.],
  [Wall time], [11.740 s], [Derived from `started_at` and `finished_at` in the execution receipt; not a scientific timing measurement.],
)

The recorded failure was a `TypeError` from Sage's `isogenies_prime_degree` path while processing the first arm at degree `ell = 3`: `no canonical coercion from Rational Field to Finite Field of size 53`. The complete traceback is retained in `stderr.log`. `stdout.log`, both checker logs, and the receipt are also retained. CPU time, peak memory, seeds consumed, arm counts, kernel counts, and all SSIQ metrics are missing because the producer did not reach its report-writing stage.

== Execution path

#figure(
  image("pipeline.svg", width: 100%),
  caption: [Recorded execution path for `RUN-SSIQ-16ccff`. The diagram shows where the process stopped and which artifacts were or were not produced.]
)

The editable graph input is `pipeline-data.json`; the rendered vector graph is `pipeline.svg`. The figure has no quantitative series to plot: the run recorded zero comparable scientific values, so a pipeline diagram is used to show the stop point and artifact boundary.

== Artifact inventory

- Present: `command.txt`, `environment.json`, `execution-receipt.json`, `launch.json`, `stdout.log`, `stderr.log`, `check.stdout.log`, `check.stderr.log`.
- Missing: `manifest.yaml`, `raw-result.json`, and all producer-side census rows.
- The checker was not run; therefore no checker validity status or certificate exists for this run.

== Reproduction pointer

The exact supervisor command, container image, plan, source hashes, and authority are preserved by the run record and commits named above. This report does not modify the implementation or retry the consumed run ID. Any later repair must use a new additive plan and a new run directory.

#text(size: 8pt, fill: gray)[Source visual data: `pipeline-data.json`. Run evidence: `experiments/EXP-SSIQ-dcb6d6/runs/RUN-SSIQ-16ccff/`.]
