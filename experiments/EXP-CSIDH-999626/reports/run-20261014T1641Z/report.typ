#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-CSIDH-999626 run report]
  \
  #text(size: 10pt)[RUN-CSIDH-8701fb · RUN-CSIDH-2ea205 · 2026-10-14]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority; those belong to the evidence review.

== Identity
- Goal: `GOAL-CSIDH-001` · Hypothesis: `H-CSIDH-73e6ab` · Task: `TASK-20261006-5a2994` (claim epoch 1, owner `executor-run-jz8jdd`)
- Approval recorded in the plan: `DEC-20261006-3cccf4` · Source idea: `IDEA-20261005-1896e8`
- Plan: `experiments/EXP-CSIDH-999626/trial-plan-v1.json` (SHA-256 `1ca1a1c3…6decb`)
- Run directories: `experiments/EXP-CSIDH-999626/runs/RUN-CSIDH-8701fb/` (stage 0), `.../runs/RUN-CSIDH-2ea205/` (stage 1)
- Code commit at launch: `00aa7abe12a58f3d17495756658b461dbb398374`; launch admission requires committed, hash-matching inputs.

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-CSIDH-999626/trial-plan-v1.json --owner executor-run-jz8jdd --epoch 1
```
Worker commands: `run.py --stage 0|1 --trial-plan … --run-dir {run_dir}`; check: `check.py {run_dir}`. Host: Linux cloud container, CPython 3.13.16, 4 vCPU. Declared memory ceiling 512 MiB per trial. Deterministic; no seed.

== Trials
#table(columns: 6,
  [Trial], [Run], [Status], [rc / check rc], [Started (UTC)], [Wall (s, derived)],
  [stage0-memcap-freeze], [RUN-CSIDH-8701fb], [output_validated], [0 / 0], [16:41:57.736], [0.22],
  [stage1-memcap-census], [RUN-CSIDH-2ea205], [output_validated], [0 / 0], [16:41:58.840], [0.32],
)
Requested 2, completed 2, failed 0, timed out 0. Wall time is derived as finished_at − started_at from `execution-receipt.json`.

== Recorded values (measured, stage 1)
Discriminant −419 (p = 419, n = 4); N = 9 by both route A and route B; M_free = 4; `reconstruction_ok: true`; outcome label recorded by the runner: `O-SEPARATES`; recorded `ratio_G1 = 2.0`, `blind_ratio_G1 = 1.0`.

#figure(image("counts.svg", width: 100%),
  caption: [Recorded integer counts per arm for RUN-CSIDH-2ea205 (census G1/G2) and its n = 1 control (N1 control G1/G2). Exact counts, one value each, no spread. Data: `data.json`, drawn by `plot.py`.])

Controls recorded: N1 control ratios 1.0 for G1 and G2 (M_free = 2); wrong-discriminant control disc −1676 count 36, `used_as_N: false`; `g_scale_ok: true`; `twin_ok: true`.

== Notes
The runner also wrote `experiments/EXP-CSIDH-999626/stage0/`, `stage1/` and `RESULTS.md` outside the run directories; they are not committed by this session (the run skill commits run directories only). `data.json` copies the values plotted here from `stage1/census.json` and `stage1/control-table.json`.
