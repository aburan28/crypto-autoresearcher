#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[CSIDH successor execution report]
  \
  #text(size: 10pt)[EXP-CSIDH-7886f6 · RUN-CSIDH-db3ad8 · 2026-10-11]
]

This report records observations from the supervised execution attempt only. It adds no verdict, evidence interpretation, hypothesis transition, support, weakening, or priority decision. The worker failed before the scientific driver began, so no scientific measurement was recorded.

== Identity and scope

- Goal: `GOAL-CSIDH-001`
- Hypothesis: `H-CSIDH-10eb0a`
- Successor task: `TASK-20261011-66ee62`
- Original failed admission: `TASK-20261009-9ec9ef`, epoch 3
- Successor snapshot task: `TASK-20261011-01e73f`
- Plan: `experiments/EXP-CSIDH-7886f6/trial-plan-v2.json`
- Plan SHA-256: `537495a6a43d325ffdadadc9e161f6b5cd38a7b50ea543205a801e0782b7d0f5`
- Trial requested: one deterministic `class-number-truncation-83` trial
- Run directory: `experiments/EXP-CSIDH-7886f6/runs/RUN-CSIDH-db3ad8/`

The successor plan retained the original scientific trial contract and run identifier because the earlier admission had created no run directory. This attempt did create the run directory and therefore consumed that run identity as an infrastructure-failure record.

== Exact command and host

The supervisor command was:

```text
python3 tools/experiment_execution.py run --plan experiments/EXP-CSIDH-7886f6/trial-plan-v2.json --owner executor-codex-successor-20261011 --epoch 1
```

The launch record bound the worker command to `python3 experiments/EXP-CSIDH-7886f6/implementation/driver.py --out {run_dir} --run-id RUN-CSIDH-db3ad8`. The recorded host platform was Darwin with CPython 3.12.8. The launch authority commit recorded in the run directory was `09f1b08c1fd7be026c5354a63eca6483fe851f5a`; the successor package was published from commit `3c93c59670ddb3d2c02996e6f0d4bd9e7182d1b8` before the claim.

The trial declared a 512 MiB per-process address-space ceiling and a 600 second machine watchdog. No seed was used by the deterministic driver contract.

== Recorded execution facts

The supervisor completed admission and wrote `launch.json`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `check.stdout.log`, `check.stderr.log`, and `execution-receipt.json`. The two stdout logs and two stderr logs are empty. The receipt records `status: infrastructure_error`, `returncode: null`, `check_returncode: null`, and `detail: Exception occurred in preexec_fn.`

The driver did not start. The five driver artifacts—`manifest.yaml`, `raw-result.json`, `forms-83.json`, `forms-84.json`, and `reading.yaml`—are absent. No measured value, control outcome, certificate, sample, timing, or uncertainty was produced. The claim was released as failed with no scientific observation.

As a host-level diagnostic, the same address-space operation used by the supervisor (`setrlimit(RLIMIT_AS, 512 MiB, 512 MiB)`) raised `ValueError: current limit exceeds maximum limit` in a minimal child process on this Darwin host. This diagnostic is operational context for the recorded pre-exec failure; it is not a result of the CSIDH experiment.

== Diagram

#figure(
  image("pipeline.svg", width: 100%),
  caption: [Execution stages and stopping point for `RUN-CSIDH-db3ad8`; no scientific values were available.]
)

== Artifact and custody notes

The generated supervisor artifacts remain under the run directory and are preserved for the successor snapshot/archive workflow. The claim and release records are immutable. The original queue, original handoff, original plan, and original protocol decision were not edited. The successor run identity must not be reused.

The report source and diagram are derived communication artifacts. They do not alter the run receipt or imply a mathematical conclusion.
