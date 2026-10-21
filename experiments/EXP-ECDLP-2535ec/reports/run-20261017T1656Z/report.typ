#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-ECDLP-2535ec run report]
  \
  #text(size: 10pt)[RUN-ECDLP-d214b6 · 2026-10-17]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority; those belong to the evidence review. A failed process is an operational fact, not a mathematical refutation.

== Identity
- Goal: `GOAL-ECDLP-001` · Hypothesis: `H-ECDLP-bd1572` · Task: `TASK-20261010-2659fd` (claim epoch 1, owner `executor-ecdlp-h3-2y4itb`)
- Approval recorded in the plan: `DEC-20261010-81ff18`
- Plan: `experiments/EXP-ECDLP-2535ec/trial-plan.json` (SHA-256 `e65f8798…a402`), trial `paired-prime-smoothness-grid`
- Run directory: `experiments/EXP-ECDLP-2535ec/runs/RUN-ECDLP-d214b6/`
- Code commit at launch: `c31fa9fa67cac786445d3f146bf3ed789d34049b`; sources verified by the supervisor against the plan's `source_sha256`.

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-2535ec/trial-plan.json --owner executor-ecdlp-h3-2y4itb --epoch 1
→ python3 experiments/EXP-ECDLP-2535ec/implementation/run.py --d 3 4 5 --bits 30 40 --A 150 300 --Bs 512 2048 --seeds 1 2 3 --out <run_dir>
```
Host: Linux cloud container (4 cores, 15 GiB), CPython 3.13.16. Declared memory ceiling 1024 MiB, watchdog 14400 s. Seeds 1, 2, 3. Runner wall clock 198.9 s (recorded); supervisor start 16:56:14Z, finish 16:59:34Z.

== Trials
#table(columns: 5,
  [Trial], [Run], [Supervisor status], [rc / check rc], [Wall (s, recorded)],
  [paired-prime-smoothness-grid], [RUN-ECDLP-d214b6], [invalid_output], [0 / 0], [198.9],
)
Requested 1, process completed 1, failed 0, timed out 0. The driver exited 0; the independent checker exited 0 ("18 cell(s), replayed box [d=5 bits=40 seed=3 A=150 B_s=512], 0 error(s)": it recounts one full box with its own sieve-free smoothness test). The supervisor recorded `invalid_output` with "manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'": the driver writes a flat manifest, not the nested `run:` record the ledger schema requires; coverage reads `needs_reconciliation` (exit 3). This is a record-format defect of the frozen implementation, not a property of the measured data.

== What ran (recorded)
18 cells: d ∈ {3, 4, 5} × bits ∈ {30, 40} × seeds 1–3, each with three NFS polynomial arms on a shared coprime (a, b) box: `special` (f = x#super[d] − c with the recorded small c, m = ⌈p#super[1/d]⌉ root), `null_same_prime` (a generic degree-d polynomial for the same special p from the base-m expansion of p at a different m, recorded t), and `null_random_prime` (a seed-matched random prime of the same bit length with its base-m polynomial). Within each cell four boxes (A, B#sub[s]) ∈ {150, 300} × {512, 2048}: 72 boxes, 27 431 to 109 591 coprime pairs each (recorded). Per box the runner records the counted doubly smooth pairs per arm, the special-over-null yield ratios with bootstrap 95% intervals, the mean and median log#sub[2] algebraic norm per arm, the mean log#sub[2] rational side, and three controls: `ctrl_same_box` (identical pair set), `ctrl_predicted_direction` (the measured log#sub[2] gap in mean algebraic norm has the sign the coefficient sizes predict), and `ctrl_null_null` (the two null arms agree: |Δ mean log#sub[2] norm| ≤ 2 and count ratio ≤ 2).

== Recorded values
Counted doubly smooth pairs for the special arm range from 147 to 7989 per box. Yield ratios (recorded `ratio`, with the recorded bootstrap 95% CI drawn in the figure); per (d, bits) group, 12 boxes each, min / median / max are derived from the recorded per-box ratios:
#table(columns: 5,
  [group], [special vs random prime], [special vs same prime], [CI lower bound > 1, vs random / vs same (of 12)], [`ctrl_null_null` pass],
  [d=3, 30 bits], [1.19 / 1.60 / 2.74], [1.63 / 2.42 / 3.89], [12 / 12], [4 of 12],
  [d=3, 40 bits], [2.93 / 3.57 / 5.67], [2.47 / 4.66 / 12.29], [12 / 12], [10 of 12],
  [d=4, 30 bits], [0.74 / 1.12 / 1.40], [1.13 / 1.41 / 1.94], [6 / 12], [12 of 12],
  [d=4, 40 bits], [1.32 / 3.00 / 3.39], [2.55 / 2.98 / 4.28], [12 / 12], [10 of 12],
  [d=5, 30 bits], [0.96 / 1.38 / 1.93], [1.06 / 1.11 / 1.40], [8 / 9], [12 of 12],
  [d=5, 40 bits], [1.62 / 2.52 / 3.77], [1.25 / 2.64 / 3.86], [12 / 12], [11 of 12],
)
Over all 72 boxes the recorded CI lower bound exceeds 1 in 62 boxes (vs random prime) and 69 boxes (vs same prime) (derived counts). `ctrl_same_box` is true and `ctrl_predicted_direction` passes for both nulls in every box. `ctrl_null_null` fails in 13 boxes, all with a recorded count ratio between the two null arms of 1.55 to 2.37 (the pass criterion is ≤ 2.0 on the count ratio and ≤ 2.0 on the log#sub[2] norm gap; the recorded yield factors range 1.01 to 2.37 overall). Recorded mean log#sub[2] algebraic norms in the first box (d = 3, 30 bits, seed 1, A = 150, B#sub[s] = 512): special 22.35, same-prime null 24.44, random-prime null 26.27. `zero_norm_count` is 0 for every arm in every box.

#figure(image("yield.svg", width: 100%),
  caption: [Recorded per-box yield ratios with recorded bootstrap 95% intervals, RUN-ECDLP-d214b6: special vs seed-matched random prime (left) and special vs generic polynomial for the same prime (right), 72 boxes grouped by (d, bits), log scale, dashed line at ratio 1. Data: `data.json`, drawn by `plot.py`.])

== Missing data
None of the declared cells is absent. Per-box wall clock is recorded (0.50–8.37 s); no CPU time beyond the runner total.

== Notes
`data.json` copies, per box, the counts, ratios, intervals, norms and control outcomes from `raw-result.json`; the group minima, medians, maxima and the CI and control tallies above are counted from those copied values and are labelled derived.
