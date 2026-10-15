#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-AUXIN-fef6ac run report]
  \
  #text(size: 10pt)[RUN-AUXIN-69eec8 · RUN-AUXIN-aa27b4 · 2026-10-14]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority; those belong to the evidence review.

== Identity
- Goal: `GOAL-AUXIN-a93442` · Hypothesis: `H-AUXIN-9d9ee0` · Task: `TASK-20261004-f88f65` (claim epoch 1, owner `executor-run-jz8jdd`)
- Approval recorded in the plan: `DEC-20261004-927012` · Source idea: `IDEA-20261005-447d82`
- Plan: `experiments/EXP-AUXIN-fef6ac/trial-plan-v1.json` (SHA-256 `4e0a325e…24834`)
- Run directories: `experiments/EXP-AUXIN-fef6ac/runs/RUN-AUXIN-69eec8/` (stage 0), `.../runs/RUN-AUXIN-aa27b4/` (stage 1)
- Code commit at launch: `00aa7abe12a58f3d17495756658b461dbb398374`.

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-AUXIN-fef6ac/trial-plan-v1.json --owner executor-run-jz8jdd --epoch 1
```
Host: Linux cloud container, CPython 3.13.16. Declared memory ceiling 512 MiB per trial. Deterministic; no seed.

== Trials
#table(columns: 5,
  [Trial], [Run], [Status], [rc / check rc], [Wall (s, derived)],
  [stage0-cheon-freeze], [RUN-AUXIN-69eec8], [output_validated], [0 / 0], [0.17],
  [stage1-cheon-census], [RUN-AUXIN-aa27b4], [output_validated], [0 / 0], [0.28],
)
Requested 2, completed 2, failed 0, timed out 0. Wall time derived as finished_at − started_at from `execution-receipt.json`.

== Recorded values (measured, stage 1)
Curve y² = x³ + x + 1 over F#sub[10007]; N = 10065 = 3·5·11·61 (trial division and Pollard agree); r = 61, cofactor 165; r−1 = 2²·3·5, r+1 = 2·31; d#sub[−] = 6, d#sub[+] = 2; B#sub[−] = 5.638, B#sub[+] = 7.523, B#sub[ρ] = 7.810; pinned_ratio = 1.3343; d2_ratio = 1.0844; recorded threshold 1.25. Outcome label recorded by the runner: `O-NO-SPLIT`. The runner notes Cheon's algorithm was not executed.

#figure(image("census.svg", width: 100%),
  caption: [Recorded B values and ratios for RUN-AUXIN-aa27b4, one exact value each (no spread). Dashed line: the threshold recorded in the control table. Data: `data.json`, drawn by `plot.py`.])

Controls recorded: r_null status `IMPOSSIBLE_CONSECUTIVE` (the runner records that the null's search range is empty because (r−1)/2 and (r+1)/2 are consecutive integers); d = 2 null ratio 1.0844; wrong-integer control (d#sub[N−] = 74, d#sub[N+] = 14) `used_for_metric: false`; twin factor and point-count checks true.

== Notes
The runner also wrote `stage0/`, `stage1/` and `RESULTS.md` under `experiments/EXP-AUXIN-fef6ac/`, outside the run directories; these are not committed by this session. `data.json` copies the plotted values from `stage1/census.json` and `stage1/control-table.json`.
