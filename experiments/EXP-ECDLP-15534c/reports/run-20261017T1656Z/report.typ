#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-ECDLP-15534c run report]
  \
  #text(size: 10pt)[RUN-ECDLP-b927d1 · 2026-10-17]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority; those belong to the evidence review. A failed process is an operational fact, not a mathematical refutation.

== Identity
- Goal: `GOAL-ECDLP-001` · Hypothesis: `H-ECDLP-bd1572` · Task: `TASK-20261010-249c4f` (claim epoch 1, owner `executor-ecdlp-h3-2y4itb`)
- Approval recorded in the plan: `DEC-20261010-81ff18`
- Plan: `experiments/EXP-ECDLP-15534c/trial-plan.json` (SHA-256 `9ced00c5…937d`), trial `defect-uniformity-three-rules`
- Run directory: `experiments/EXP-ECDLP-15534c/runs/RUN-ECDLP-b927d1/`
- Code commit at launch: `c31fa9fa67cac786445d3f146bf3ed789d34049b` (clean working tree for the hashed sources; the supervisor verified `run.py`, `check.py`, `primeset.py` against the plan's `source_sha256`).

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-15534c/trial-plan.json --owner executor-ecdlp-h3-2y4itb --epoch 1
→ python3 experiments/EXP-ECDLP-15534c/implementation/run.py --d 2 3 5 --curves 6 --draws 400 --seeds 1 2 3 --out <run_dir>
```
Host: Linux cloud container (4 cores, 15 GiB), CPython 3.13.16. Declared memory ceiling 512 MiB, watchdog 7200 s. Seeds 1, 2, 3. Runner wall clock 28.0 s (recorded `wall_clock_seconds`); supervisor start 16:56:14Z, finish 16:56:43Z.

== Trials
#table(columns: 5,
  [Trial], [Run], [Supervisor status], [rc / check rc], [Wall (s, recorded)],
  [defect-uniformity-three-rules], [RUN-ECDLP-b927d1], [invalid_output], [0 / 0], [28.0],
)
Requested 1, process completed 1, failed 0, timed out 0. The driver exited 0 and the independent checker (`check.py`, which replays the Hensel lifts with its own arithmetic) exited 0 with "432 uniformity test(s), 1440 draw(s) replayed independently, 0 error(s)". The supervisor nevertheless recorded `invalid_output` with the reason "manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'": the driver writes a flat manifest, not the nested `run:` record the ledger schema requires. The coverage view therefore reads `needs_reconciliation` (exit 3). This is a record-format defect of the frozen implementation, not a property of the measured data.

== What ran (recorded)
Cells: d ∈ {2, 3}, two arms (special p = m#super[d] − c with small c, and a seed-matched random 14-bit prime), 2 primes per d per arm, 3 seeds: 24 cells; 6 curves per cell with a point P of odd prime order l; 3 lift rules (L1 integer Hensel, L2 Teichmüller Hensel, L3 random Hensel) to precision p#super[6]; 400 draws per (curve, rule): 432 uniformity tests, 400 samples each. The requested d = 5 produced no cell: `primeset.special_primes(5, 14, 2)` is empty (no 14-bit prime of the form m#super[5] − c with the declared small c exists), and the driver recorded nothing for it. Recorded test statistic per (curve, rule): chi-square on 20 bins of the defect δ mod p with its p-value, Kolmogorov–Smirnov distance to uniform on Z/p with the recorded threshold 0.09745 at α = 0.001, `zero_count`, `higher_valuation_skipped`, `precision_mismatch`.

== Recorded values
- Summary (recorded by the runner): `tests` 432; `bonferroni_alpha` 2.3148e-6 (0.001/432); chi-square rejections below that level: 5 in total, by arm:rule — random:L1 1, random:L2 1, random:L3 0, special:L1 2, special:L2 1, special:L3 0. The five recorded rejections have chi-square p ∈ {1.4e-7, 3.3e-7, 2.6e-8, 1.1e-6, 1.2e-10} and KS distance ∈ {0.061, 0.054, 0.058, 0.068, 0.096}.
- KS: the largest recorded KS distance over all 432 tests is 0.1143 (special, d = 2, p = 8287, l = 4231, L2); 4 tests record a KS distance above the 0.09745 threshold (derived count from the recorded per-test values in `data.json`).
- `precision_mismatch` is 0 in every test; `higher_valuation_skipped` is 0 in 419 tests and 1–2 in 13 tests (derived count).
- Anomalous positive controls (recorded): random arm p = 1789, curve (a, b) = (1202, 549) found after 100 curves tried; special arm p = 1039, (249, 467) after 238 tried. For every rule, 50 of 50 draws recovered the discrete logarithm and `delta_zero` = 50 of 50; both controls record `pass: true`.

#figure(image("uniformity.svg", width: 100%),
  caption: [Recorded per-test chi-square p-values (left, log scale, dashed line at the recorded Bonferroni α) and KS distances (right, dashed line at the recorded α = 0.001 threshold) for RUN-ECDLP-b927d1, by lift rule and arm; 432 tests of n = 400 draws. Data: `data.json`, drawn by `plot.py`.])

== Missing data
No cell for d = 5 (empty special prime set at 14 bits; recorded as absent, not as a failure). No per-draw CPU time was recorded; only the runner's total wall clock.

== Notes
The run directory holds `launch.json`, `execution-receipt.json`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `check.stdout.log`, `check.stderr.log`, `manifest.yaml` (flat) and `raw-result.json`. `data.json` copies the 432 per-test statistics, the summary and the controls from `raw-result.json`; the derived counts above are counted from those copied values and labelled derived.
