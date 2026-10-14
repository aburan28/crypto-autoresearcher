#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-BINSTD-a33de2 run report]
  \
  #text(size: 10pt)[RUN-BINSTD-113958 · 2026-10-14]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority. The stage-0 process exited 0, but the plan's output check failed, so the supervisor marked the trial `invalid_output` and did not launch stage 1. That is an operational fact, not a mathematical result.

== Identity
- Goal: `GOAL-ECDLP2M-001` · Hypothesis: `H-BINSTD-ce918e` · Task: `TASK-20261003-81a0eb` (claim epoch 1, owner `executor-run-jz8jdd`)
- Approval recorded in the plan: `DEC-20261003-a57c49`
- Plan: `experiments/EXP-BINSTD-a33de2/trial-plan-v1.json` (SHA-256 `daf55ac1…ffa51`)
- Run directory: `experiments/EXP-BINSTD-a33de2/runs/RUN-BINSTD-113958/` (stage 0). Stage 1 (`RUN-BINSTD-250727`) was not created.
- Code commit at launch: `00aa7abe12a58f3d17495756658b461dbb398374`.

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-BINSTD-a33de2/trial-plan-v1.json --owner executor-run-jz8jdd --epoch 1
```
Host: Linux cloud container, CPython 3.13.16. Declared memory 2048 MiB (stage 0), 4096 MiB (stage 1). Catalog seed recorded: 2026100388923.

== Trials
#table(columns: 5,
  [Trial], [Run], [Status], [rc / check rc], [Wall (s)],
  [stage0-shared-baseline-package-floor-freeze], [RUN-BINSTD-113958], [invalid_output (needs_reconciliation)], [0 / 1], [5.02 derived; 4.51 recorded by runner],
  [stage1r-shared-baseline-delta-rss], [—], [not launched (waiting_on_dependencies)], [—], [—],
)
Requested 2, completed 0 validated, failed 1 (output check), not launched 1, timed out 0.

Recorded check failure (`check.stdout.log`):
```text
FAIL:
  evidence_cited must include EV-BINSTD-602614 and EV-BINSTD-cd47a8
  Stage-0 freeze must cite EV-BINSTD-602614 and EV-BINSTD-cd47a8
```
The recorded `evidence_cited` is `[EV-BINSTD-c45564, EV-BINSTD-602614]`.

== Recorded values (measured, stage 0)
Shared-baseline RSS 31137792 B; OS RSS floor 31137792 B; M0 = 16777216 B; α = 1.0; rss_mode `process_isolated_delta_shared_baseline`; allocator_ok, rss_probe_ok, twin_ok, floor_clear_calibration_ok all true; runner outcome label `O-STAGE0-OK`.

#figure(image("allocator-probe.svg", width: 90%),
  caption: [Recorded stage-0 allocator probe from RUN-BINSTD-113958: delta RSS at 2, 8 and 16 MiB allocations (one sample per size, no spread recorded). Dotted line is the allocation size for reference. Data: `data.json`, drawn by `plot.py`.])

== Notes
The runner also wrote `experiments/EXP-BINSTD-a33de2/stage0/` outside the run directory; this session does not commit it. Getting stage 1 to run needs a change to the implementation or contract so stage 0 cites the evidence the check requires. That change is reported separately, not made here.
