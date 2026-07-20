# EXP-SIG-004 — Analysis: residual series re-anchor with canonical reduction

Experiment: EXP-SIG-004 (hypothesis H-SIG-001, question RQ-SIG-001)
Dispatched by: DEC-20260718-019 (next_actions); handoff TASK-20260718-SIG-F4.
Runs: RUN-EXP-SIG-004-a (gate, PASS), -b (n=9), -c (n=12), -d (n=15),
-e (n=18), -f (n=21), -g (C4b determinism repeat), -h (C4b compare
receipt); RUN-EXP-SIG-004-c0-superseded (**invalid** — driver
control-aggregation bug, receipt preserved, cell payloads bit-identical to
RUN-c modulo timing).
Instrument: bit-identical copy of the EXP-SIG-001/002/003 instrument
(`src/h013_f5_signatures.sage`, sha256
`1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087`,
re-verified at every run start); new driver `SIG4_run.sage` with
`full_reduce` copied verbatim from `experiments/EXP-SIG-003/SIG3_run.sage`.
Git: commit `1b6373f86252d72f6f162b5b13c3426ba5f6baca` at manifest time
(HEAD moved from `df595e8…` during execution — concurrent-session activity;
all measurement used the sha256-pinned src copies, hashes recorded in every
raw.json), dirty tree.
Budget: 9 invocations of 10 maximum (one deliberately unspent); ≈ 130 s
compute wall of 3,300 s; peak RSS 0.90 GB of 24 GB (RUN-f). No censoring,
no timeouts; the 600 s kill rule never engaged (longest invocation
77.0 s real, RUN-f).

## 0. What was measured (fixed before execution — specification.yaml)

On the SAME boolean chained Semaev m=3 systems as EXP-SIG-002 (same sizes,
same seed sets, same input-side filter), per (n, seed, arm) cell:

- D3/D4 classification with kernel bases; the verbatim EXP-SIG-002
  v3_mults family (monomial multiples {x_j·ker_3} embedded at D4).
- `residual_pinned` = extra_4 − rank mod K4 by the instrument's early-break
  `reduce_against` (verbatim pinned semantics — continuity anchor).
- `residual_canonical` = extra_4 − rank mod K4 by `full_reduce` (clears
  every pivot-lead bit; linear; rank-exact — the corrected measure).
- C8: `rank(v3_mults ∪ K4) − rank(K4)` (reduction-free union echelon) must
  equal the canonical rank on every cell.
- D3 non-Koszul count = D3 extra (reduce-free; mission item 4).
- Null arm: same computation on the support-matched null, including the
  null's OWN D3-kernel multiples (EXP-SIG-002 inferred null residual 0 from
  extra = 0; here it is measured explicitly).

## 1. Side-by-side table: old (pinned) vs corrected (canonical), per size and seed

Standard instances (sem arm). All numbers exact integers; "old" = EXP-SIG-002
anchored value, reproduced in-run by the pinned reduction on every cell.

| n | seed | D4 def | D4 extra | v3 imgs | rank_old | rank_new | union chk | **old residual** | **corrected residual** | Δ |
|---|------|--------|----------|---------|----------|----------|-----------|------------------|------------------------|---|
| 9  | 1 | 41 | 41 | 18 | 18 | 17 | 17 | 23 | **24** | +1 |
| 9  | 2 | 41 | 41 | 18 | 18 | 17 | 17 | 23 | **24** | +1 |
| 9  | 3 | 41 | 41 | 18 | 18 | 17 | 17 | 23 | **24** | +1 |
| 12 | 2 | 32 | 32 | 24 | 23 | 23 | 23 | 9  | **9**  | 0 |
| 12 | 4 | 32 | 32 | 24 | 23 | 23 | 23 | 9  | **9**  | 0 |
| 12 | 5 | 32 | 32 | 24 | 23 | 23 | 23 | 9  | **9**  | 0 |
| 12 | 6 | 32 | 32 | 24 | 23 | 23 | 23 | 9  | **9**  | 0 |
| 12 | 7 | 32 | 32 | 24 | 23 | 23 | 23 | 9  | **9**  | 0 |
| 15 | 1 | 40 | 40 | 30 | 30 | 29 | 29 | 10 | **11** | +1 |
| 15 | 3 | 40 | 40 | 30 | 30 | 29 | 29 | 10 | **11** | +1 |
| 15 | 4 | 40 | 40 | 30 | 30 | 29 | 29 | 10 | **11** | +1 |
| 15 | 5 | 40 | 40 | 30 | 30 | 29 | 29 | 10 | **11** | +1 |
| 15 | 6 | 40 | 40 | 30 | 30 | 29 | 29 | 10 | **11** | +1 |
| 18 | 1 | 48 | 48 | 35 | 35 | 35 | 35 | 13 | **13** | 0 |
| 18 | 2 | 48 | 48 | 35 | 35 | 35 | 35 | 13 | **13** | 0 |
| 18 | 3 | 48 | 48 | 35 | 35 | 35 | 35 | 13 | **13** | 0 |
| 21 | 1 | 56 | 56 | 42 | 42 | 41 | 41 | 14 | **15** | +1 |
| 21 | 2 | 56 | 56 | 42 | 42 | 41 | 41 | 14 | **15** | +1 |
| 21 | 3 | 56 | 56 | 42 | 42 | 41 | 41 | 14 | **15** | +1 |

Filtered instances (recorded observations, excluded from the series;
re-measured with both reductions):

| n | seed | type | old residual | corrected residual | Δ |
|---|------|------|--------------|--------------------|---|
| 12 | 1 | degenerate R_x = 0 | 82 | 82 | 0 |
| 12 | 3 | linear-equation | 0 | 0 | 0 |
| 15 | 2 | linear-equation | 0 | 0 | 0 |

Null arm: residual_pinned = residual_canonical = 0, extra = 0,
rank = sr_pred at D3/D4 on all 22 null cells (19 standard-matched + 3
filtered-matched).

## 2. The corrected series and its statements (numbers only)

- Corrected series (standard instances, zero within-size variance on
  3–5 seeds per size): **24 (n=9), 9 (n=12), 11 (n=15), 13 (n=18),
  15 (n=21)**.
- Old series (reproduced verbatim in-run): 23, 9, 10, 13, 14.
- Per-size correction Δ = corrected − old: **+1 (n=9), 0 (n=12), +1 (n=15),
  0 (n=18), +1 (n=21)**.
- **Monotonicity over n = 12..21: the corrected series IS still monotone
  increasing: 9 → 11 → 13 → 15**, increments **+2, +2, +2** (old
  increments were +1, +3, +1).
- **The n=9 exception persists**: corrected residual 24 > 9 = the n=12
  value (series with n=9 included is non-monotone: 24 → 9 → 11 → 13 → 15),
  and the n=9 D4 deficit 41 ≠ 8n/3 = 24 replicates on all 3 seeds.
- Continuity direction (mission rule): corrected ≥ old on every one of the
  19 standard sem cells (and on all 41 measurement cells); no halt
  triggered. The EV-SIG-003 caveat direction is confirmed.
- **Does the EV-SIG-002 series stand?** (numbers, no verdict): at n=12 and
  n=18 the old counts stand as-is (9, 13). At n=9, 15, 21 the old counts
  are strict lower bounds; the corrected counts are **24, 11, 15**. The
  old series as a whole is a lower bound on the corrected series, strict
  at three of five sizes.
- **D3 non-Koszul count (mission item 4)**: = 1 on every standard cell at
  every size n = 9..21 (19/19; reduce-free quantity, unchanged as
  expected — confirmed). Filtered instances: 0.

## 3. Controls (all passed)

| Control | Outcome | Evidence |
|---|---|---|
| C1 null residual gate (n=9,12) | PASS: extra=0, rank==sr_pred, residual 0 under BOTH reductions (explicitly computed from the null's own D3 kernel) | RUN-a raw.json |
| C2 injected-syzygy detection | PASS: 3-generator constant-multiplier rep detected | RUN-a raw.json |
| C3 T2 anchor continuity (n=15 s1) | PASS: D3 def 1, D4 def 40, pinned residual == 10 verbatim; canonical 11 ≥ 10 | RUN-a raw.json |
| C4a in-run determinism (n=15 s3 sem, twice) | PASS: identical modulo timing | RUN-a raw.json |
| C4b cross-invocation determinism (18:1:sem, RUN-e vs RUN-g) | PASS: identical=True (formal receipt RUN-h) | RUN-h raw.json |
| C5 null on every measurement cell | PASS on all 22 null cells: extras 0, rank==sr_pred D3/D4, residual 0 both reductions | RUN-b..f raw.json |
| C6 T2 anchors | PASS: D4 deficit == 8n/3 on all 16 standard cells at n≥12 (32/40/48/56); D3 deficit == extra == 1 on all 19 standard cells; n=9 deficit 41 recorded (3 seeds) | RUN-b..f raw.json |
| C7 continuity (corrected ≥ old) | PASS on all 41 measurement cells (Δ ≥ 0 everywhere; min 0, max +1); stop rule never engaged | summary.json |
| C8 union cross-check | PASS on all 41 measurement cells: canonical rank == rank(v3∪K4) − rankK4 exactly | summary.json |
| C9 instance filter | PASS: filter applied input-side; 3 filtered instances re-recorded (n=12 s1 R_x=0 residual 82/82; n=12 s3 linear 0/0; n=15 s2 linear 0/0) | RUN-c/d raw.json filter blocks |
| Pinned-semantics continuity with EXP-SIG-002 | PASS: residual_pinned reproduces the EXP-SIG-002 per-cell anchor on all 19 standard cells | summary.json |
| Kill rule / budget | never engaged; longest invocation 77.0 s < 600 s | manifests |

## 4. Scope executed vs approved spec

All handoff items executed: five sizes × EXP-SIG-002's seed sets (19
standard instances) with both reductions; side-by-side per-seed table (§1);
monotonicity and n=9 statements (§2); all controls (§3); the D3 non-Koszul
count re-confirmed at n=9..21 (mission item 4 — unchanged 1, reduce-free,
no extra runs needed); no scope reduction (n=21 and n=18 both reached).

## 5. Unexpected observations (AGENTS rule 8)

1. **The corrected increments are exactly even.** Over n=12..21 the
   corrected series 9, 11, 13, 15 is arithmetic with common difference +2,
   i.e. corrected residual == 2n/3 + 1 == (D4 deficit)/4 + 1 at every
   measured size in the anchored range (old series increments were +1, +3,
   +1). Four points; no law fit attempted; recorded.
2. **The early-break rank overestimate is exactly 1 wherever it occurs.**
   rank_old − rank_new ∈ {0, 1} on every cell: 1 at n=9, 15, 21 and 0 at
   n=12, 18 (also 0 on all filtered and null cells). The defect correlates
   with the parity of n/3 (odd at n=9,15,21; even at n=12,18) on these
   five sizes; mechanism unexplained; recorded.
3. **n=9 corrected residual == 8n/3.** The corrected n=9 residual is 24,
   numerically equal to the 8n/3 value that the (violated at n=9) T2 law
   would give for the D4 deficit — while the actual n=9 D4 deficit stays
   41. Pure numerical coincidence as far as the data shows; recorded.
4. **HEAD moved during execution.** The git HEAD changed from df595e8 to
   1b6373f between the gate run and manifest generation (concurrent
   session activity). No EXP-SIG-004 file was affected; all measurement
   ran against the sha256-pinned src copies (hashes verified at every run
   start and recorded in every raw.json); manifests record the commit at
   receipt time.
5. **The degenerate R_x=0 instance's residual (82) is NOT underestimated.**
   On n=12 seed 1, residual 82 under both reductions (Δ=0): the pinned
   instrument's defect is specific to the standard instances' v3-multiples
   family at the noted sizes, not a uniform downward bias.

## 6. Deviations

- **D1 (superseded receipt, preserved):** the first RUN-c launch used the
  pre-fix driver whose run-level control aggregation applied the C6
  T2-anchor control to FILTERED (recorded-observation) cells, producing
  spurious `control_failures` entries. Cell payloads are verified
  bit-identical to the re-run RUN-c modulo timing fields (measurement data
  unaffected; the bug was in run-level aggregation only). Receipt moved to
  `RUN-EXP-SIG-004-c0-superseded`, validity_status invalid; re-run as
  RUN-c after the fix. Analogue of EXP-SIG-003 deviation D1.
- **D2 (run budget not fully consumed):** 9 invocations of 10 used (8
  valid runs + the superseded one). The 10th was unnecessary: the D3
  non-Koszul confirmation (mission item 4) is reduce-free and comes from
  the same D3 classifications, and no censoring occurred. Recorded as a
  deliberate scope decision (precedent: EXP-SIG-003 D2).

## 7. Censoring table (AGENTS rule 5 — none of this is evidence)

| Cell | State | Reason |
|---|---|---|
| n=21 arm | completed | longest invocation 77.0 s, far under the 600 s kill rule |
| any size reduction | not needed | no soft-cap engagement |

## 8. Artifacts

- `specification.yaml`, `implementation.md`, `analysis.md` (this file)
- `SIG4_run.sage` (driver), `make_manifests.py`, `summarize.py`,
  `compare_determinism.py`
- `src/{h013_f5_signatures.sage, semaev_tree.py, ic_first_fall_fast.py,
  macaulay_export.py}` — bit-identical instrument copies (sha256 in every
  manifest and raw.json)
- `runs/RUN-EXP-SIG-004-{a..h}/{manifest.yaml, command.txt,
  environment.json, stdout.txt, stderr.txt, raw.json}` (RUN-h:
  determinism-compare receipt; RUN-EXP-SIG-004-c0-superseded preserved)
- `summary.json` (machine-readable old-vs-corrected table + aggregate checks)
- `ledger/EV-SIG-004.yaml`

Environment: SageMath 10.9, Python 3.14.3, macOS-15.6 arm64 (M4 Pro).
All raw.json files carry: exact CLI args, environment, UTC timestamps,
instrument sha256 set + pinned-match flag, per-D ranks/predictions/kernel
data, instance-filter fields, both-reduction v3-multiples ranks, union
cross-check, per-cell and run-level control outcomes. Manifests carry peak
RSS, CPU seconds (from `/usr/bin/time -l`), git commit/dirty state.
