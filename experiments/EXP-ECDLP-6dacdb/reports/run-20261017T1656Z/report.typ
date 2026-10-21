#set page(paper: "a4", margin: 1.8cm)
#set text(size: 10pt)
#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-ECDLP-6dacdb run report]
  \
  #text(size: 10pt)[RUN-ECDLP-c770f6 · RUN-ECDLP-393d10 · 2026-10-17]
]

This report records what ran and what the runner recorded. It states no verdict, support, weakening, significance or priority; those belong to the evidence review. A failed process is an operational fact, not a mathematical refutation.

== Identity
- Goal: `GOAL-ECDLP-001` · Hypothesis: `H-ECDLP-bd1572` · Task: `TASK-20261010-ab5786` (claim epoch 1, owner `executor-ecdlp-h3-2y4itb`)
- Approval recorded in the plan: `DEC-20261010-81ff18`
- Plan: `experiments/EXP-ECDLP-6dacdb/trial-plan.json`, trials `part-a-embedding-degree-census` and `part-b-deployed-k-and-threshold`
- Run directories: `experiments/EXP-ECDLP-6dacdb/runs/RUN-ECDLP-c770f6/` (part A), `.../runs/RUN-ECDLP-393d10/` (part B)
- Code commit at launch: `c31fa9fa67cac786445d3f146bf3ed789d34049b`; sources verified by the supervisor against the plan's `source_sha256`.

== Command and host
```text
python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-6dacdb/trial-plan.json --owner executor-ecdlp-h3-2y4itb --epoch 1
→ python3 experiments/EXP-ECDLP-6dacdb/implementation/run.py --part A --seeds 1 2 3 --curves 64 --out <run_dir>
→ python3 experiments/EXP-ECDLP-6dacdb/implementation/run.py --part B --out <run_dir>
```
Host: Linux cloud container (4 cores, 15 GiB), CPython 3.13.16. Declared memory ceiling 512 MiB per trial; watchdogs 3600 s (A) and 1800 s (B). Part A seeds 1, 2, 3; part B deterministic.

== Trials
#table(columns: 5,
  [Trial], [Run], [Supervisor status], [rc / check rc], [Wall (s, recorded)],
  [part-a-embedding-degree-census], [RUN-ECDLP-c770f6], [invalid_output], [0 / 0], [62.3],
  [part-b-deployed-k-and-threshold], [RUN-ECDLP-393d10], [invalid_output], [0 / 0], [2.9],
)
Requested 2, processes completed 2, failed 0, timed out 0. Both drivers exited 0; the independent checker exited 0 on both ("parts A, 12 curve row(s) recounted independently, 0 error(s)"; "parts B, 0 curve row(s) recounted independently, 0 error(s)" — part B's check re-verifies [l]G = O and the Hasse bounds rather than recounting curves). The supervisor recorded `invalid_output` for both with "manifest.yaml fails the run schema (tools/validate_ledger.py): expected top-level key 'run'": the driver writes a flat manifest, not the nested `run:` record the ledger schema requires; coverage reads `needs_reconciliation` (exit 3). This is a record-format defect of the frozen implementation, not a property of the measured data.

== Part A, recorded values (RUN-ECDLP-c770f6)
72 cells: d ∈ {2, 3, 4, 5}, two arms (special 16-bit p = m#super[d] − c; seed-matched random 16-bit prime), 3 primes per d per arm, 3 seeds; 64 random curves per cell with the largest prime factor l of the point count and the embedding degree k = ord#sub[l] (p) computed exactly; anomalous curves (point count equal to p) excluded and counted (4 cells record `anomalous: 1`); a per-cell `ctrl_count` row records a Hasse check and `point_killed: true`.
- Curves: special 2300, random 2304 (recorded `n_curves`).
- `mean_log2_t` with t = (p − 1)/k: special 1.2487, random 1.2667, difference −0.0181, permutation p-value 0.684.
- `small_k_fraction`: special 0.1591, random 0.1328, difference 0.0263, recorded standard error 0.0104.
- t histogram, bins [1], [2], [3–4], [5–16], [≥17]: special (851, 725, 288, 309, 127), random (862, 679, 304, 330, 129); chi-square 2.71, permutation p-value 0.612.
- `smallest_k`: both arms record k = 1 at l ∈ {5, 7} and at l = 11 (random) or l = 29 (special).
- Supersingular controls: 43 rows, every one records k = 2 (l from 19 to 15671).

== Part B, recorded values (RUN-ECDLP-393d10)
Six public parameter sets; prime checks on p and l, Hasse check, an order check [l]G = O where a base point was available, an exact embedding-degree lower bound by direct exponentiation to 10#super[6], the rho cost log#sub[2] of the square root of πl/2 and k\* under three recalled L(1/3, c) constants with the o(1) dropped (c = 1.923 GNFS, 1.747 exTNFS, 1.526 SNFS/STNFS).
#table(columns: 9,
  [curve], [special], [l bits], [k measured], [rho log2], [k\* GNFS], [k\* exTNFS], [k\* SNFS], [[l]G = O],
  [Curve25519], [yes], [253], [> 10#super[6]], [125.8], [9], [11], [16], [true (ladder)],
  [P-256], [yes], [256], [> 10#super[6]], [127.8], [9], [12], [17], [true],
  [secp256k1], [yes], [256], [> 10#super[6]], [127.8], [9], [12], [17], [true],
  [P-521], [yes], [521], [> 10#super[6]], [260.3], [27], [34], [48], [true],
  [Ed448], [yes], [446], [> 10#super[6]], [222.8], [21], [27], [37], [not run (no base point recorded)],
  [brainpoolP256r1], [no], [256], [> 10#super[6]], [127.5], [9], [12], [17], [true],
)
Embedding-degree searches took 0.28–0.44 s per curve (recorded). The runner's own note: constants are recalled and the o(1) is dropped, so k\* is optimistic for the attacker; k measured is an exact lower bound.

#figure(image("census.svg", width: 100%),
  caption: [Left: recorded part A t histogram per arm (RUN-ECDLP-c770f6, 2300 special and 2304 random curves). Middle: log#sub[2] (k/l) per recorded curve row, derived as the quotient of the recorded k and l. Right: recorded part B k\* per curve and constant (RUN-ECDLP-393d10). Data: `data.json`, drawn by `plot.py`.])

== Missing data
Ed448 has no recorded base point, so its order check is `null`. No per-curve CPU time was recorded.

== Notes
Both run directories hold the supervisor's ten artifacts plus, for part B, `deployed-table.md`. `data.json` copies the recorded test block, the supersingular controls, the per-cell (k, l, t) rows and the whole part B block from the two `raw-result.json` files.
