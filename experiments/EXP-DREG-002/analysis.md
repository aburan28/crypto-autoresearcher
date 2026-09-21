# EXP-DREG-002 — analysis

**Experiment:** EXP-DREG-002 (hypothesis H-DREG-001, question RQ-DREG-001)
**Mission (TASK-20260718-DREG-F2):** complete the n=17 sem full-rank cell
(two-partition checkpoint-consistency control) and, budget permitting, the
n=17 null full-rank cell (review correction C1: sr_pred_D = 126,922).
**Instrument:** `src/h012c_block_m4ri.py` sha256 `0eb38126…` (validated in
EXP-DREG-001, five anchors PASS), protocol per
`EXP-DREG-001/amendments/AMD-20260718-002-n17-partitions.yaml`.
**Executor session:** TASK-20260718-DREG-F2, first attempt killed by a
transient ENOSPC (deviation D1); retried 2026-07-18T22:56Z. Budget applied:
3,300 s wall / 10 runs / 600 s-per-invocation kill rule at checkpoint
boundaries only. **Cutoff:** 2026-07-18T23:30Z.

---

## 1. Headline measurements (both certified/verified by my control runs)

| Cell (n=17, t=3, ti=0, D=5, seed 2026) | Partition | rank | sr_pred_D | deficit | work s | wall s | peak RSS | system_hash |
|---|---|---|---|---|---|---|---|---|
| sem full rank | A (chunk 24,000, 14 units) | **125,099** | 126,922 | **1,823** | 2,195.9 | 2,646.4 | 5.02 GB | `5f94c88f…` |
| sem full rank | B (chunk 20,000, 16 units) | **125,099** | 126,922 | **1,823** | 1,828.4 | 2,269.1 | 3.75 GB | `5f94c88f…` |
| null full rank | A (chunk 24,000, 17 units) | **126,922** | 126,922 | **0** | 4,616.7 | 5,044.8 | 3.73 GB | `5deee45d…` |
| null full rank | B (chunk 20,000) | in progress at cutoff (coordinator session, RUN-DREG-001-MEASURE-N17-NULL-B) | | | | | | |

**Deficit series (sem, D=5, full exact) with the n=17 insert:**
**1,322 / 1,862 / 1,823 / 1,999 at n = 12 / 15 / 17 / 18.**
Increments: +540 (n=12→15), **−39 (n=15→17)**, +176 (n=17→18).
Deficit as a fraction of rank: 4.71% / 2.70% / 1.46% / 1.39%
(n = 12 / 15 / 17 / 18) — monotone decreasing.

## 2. Controls

| Control | Outcome | Evidence |
|---|---|---|
| Checkpoint-partition consistency, n=17 sem (AMD-20260718-002 gate) | **PASS** — chunk 24,000 vs 20,000 (14 vs 16 units): identical system_hash `5f94c88f…`, pred 126,922, rank 125,099, deficit 1,823; all 15+17 carry files sha256-verified; units contiguous, Σk == rank both; both terminal | RUN-DREG-002-CONTROL-N17-SEM-PARTCONSIST-b/raw.json |
| Null-arm C1 prediction check | **PASS (partition A)** — measured null rank 126,922 == sr_pred_D 126,922 exactly; deficit 0; 11 carries sha256-verified; prediction never substituted for a run | RUN-DREG-002-CONTROL-N17-NULL-A-VERIFY/raw.json |
| Carry-chain integrity on every verified cell | PASS — every checkpoint carry listed in each state.json re-hashed bit-for-bit (read-only against EXP-DREG-001) | both control raw.json files |
| Null-arm two-partition gate | **OPEN** — partition B in progress under the coordinator session at cutoff; per AMD-20260718-002 no n=17 null value enters a fit/verdict until it passes | §4 |
| Same-instrument determinism | inherited: identical system_hash across partitions and across sessions; instrument sha256 `0eb38126…` identical in all four EXP-DREG-001 measure manifests | control raw.json manifests |

## 3. What the new data says about the H-DREG-001 clauses (numbers only, no verdict)

- **Success clause (i) — d_reg(sem) < d_reg(null) at any n:** not evaluable.
  d_reg by the full-rank definition is > 5 for both arms at n=17:
  sem rank 125,099 < nrows 132,719; null rank 126,922 < nrows 132,719.
- **Success clause (ii) — deficit grows super-linearly at n=17..24:** the
  first past-wall point is deficit(17) = 1,823. It is **below** deficit(15)
  = 1,862 (−2.1%) and below deficit(18) = 1,999; the series 1,322 / 1,862 /
  1,823 / 1,999 is non-monotone with increments +540 / −39 / +176. The
  deficit-to-rank ratio falls to 1.46% at n=17 (from 2.70% at n=15).
- **Success clause (iii) — gap(n) = d_reg − d_ff bounded:** not evaluable
  (d_reg unmeasured at D=5 in every cell; no new d_ff data in this task).
- **Falsification clause — deficit continues decelerating or shrinks relative
  to rank:** the measured numbers are the ones in §1; the relative deficit is
  smaller at n=17 than at every previously measured size. One past-wall
  point; n=21/24 remain unmeasured.
- **C1 (review correction):** the n=17 null rank is now a MEASURED value
  (126,922, partition A, verified; partition B pending) — the null tracks
  sr_pred exactly at n=17 as it did at n=12/15.

The status decision on H-DREG-001 belongs to the Coordinator.

## 4. Censoring table (stopping rules; none of this is evidence — AGENTS rule 5)

| Cell | State | Reason |
|---|---|---|
| n=17 null partition B (chunk 20,000) | in progress at cutoff | launched by the coordinator session 2026-07-18T23:24Z (RUN-DREG-001-MEASURE-N17-NULL-B, PID 2423); my stopping rule forbids duplicating a live cell; est. ~5,000 s wall, far past my remaining budget |
| n=21, n=24 sem/null | not attempted | extrapolated ~7–9 h (n=21) to days (n=24) per cell |
| d_ff ladders, ≥8-target replication | not attempted | outside this handoff's scope and budget |

## 5. Deviations from the frozen specification

- **D1 (ENOSPC retry):** the first executor attempt (TASK-20260718-DREG-F2,
  ~21:36–21:45Z) died with a transient ENOSPC before producing any EXP-DREG-002
  data; the volume recovered (~692 GiB free) and the coordinator ordered a
  retry. No data loss: no runs had been started by that attempt.
- **D2 (division of labor, recorded per rule 8):** at dispatch, all four
  AMD-20260718-002 measurement cells were being executed by the coordinator's
  own session inside `experiments/EXP-DREG-001/` (sem_A done 21:13:49Z, sem_B
  done 21:54:08Z, null_A done 23:21:40Z, null_B launched 23:24Z). My
  specification's stopping rule covers this: EXP-DREG-002 does NOT duplicate
  live cells; it performed the independent certification controls (carry-chain
  re-hashing, unit arithmetic, cross-partition identity, C1 comparison) from
  sha256-pinned COPIES of the immutable receipts, writing only inside
  `experiments/EXP-DREG-002/`. Nothing was written into EXP-DREG-001.
- **D3 (failed run preserved):** RUN-DREG-002-CONTROL-N17-SEM-PARTCONSIST
  failed in 0.1 s (verifier script computed the workspace path one directory
  short; no data produced; failed_infrastructure). Fixed and re-run as
  …-PARTCONSIST-b. The failed receipt is preserved per data-integrity rules.
- **D4 (receipt naming):** runs use `RUN-DREG-002-<PURPOSE>` with
  docs-compliant receipts (manifest.yaml, command.txt, environment.json,
  stdout.log, stderr.log, raw.json, work/), consistent with the EXP-DREG-001
  convention; the handoff's literal `stderr.txt` is represented by
  `stderr.log`.
- **D5 (contention):** foreign-session processes (h012c n18v probe,
  bounded_baselines.sage, a long-running sage python) contended CPU during
  the measurement cells (visible in NULL-A's red-phase times: 306→609 s).
  Ranks are exact integers and unaffected; wall timings carry this caveat.
- **D6 (budget not fully consumed):** ~24 min of the 3,300 s wall budget
  remained at cutoff. Spending it on a duplicate null_B (a ~5,000 s cell
  already running under the coordinator session) would have violated the
  serialization resource policy, doubled contention, and produced a censored
  partial duplicate of a cell that will complete intact. Judged
  value-negative; recorded as a deliberate scope decision.

## 6. Cost model update (measured, this machine, M4 Pro 14-core, 48 GB)

| cell | work s | wall s | peak RSS |
|---|---|---|---|
| n=17 sem, chunk 24,000 | 2,195.9 | 2,646.4 | 5.02 GB |
| n=17 sem, chunk 20,000 | 1,828.4 | 2,269.1 | 3.75 GB |
| n=17 null, chunk 24,000 | 4,616.7 | 5,044.8 | 3.73 GB |

Notes for the n=21 extrapolation: null work ≈ 2.1× sem work at n=17 (full
column support: 384,168 = C(35,≤5) vs 314,472 cols; late null units reduce
against the full 126,922-pivot basis at 300–600 s per 24,000-col unit under
contention). The sem deficit plateau shows in the pivot profile: zero new
pivots after col ~240,000 of 314,472 (sem) and after col 312,000 of 384,168
(null hit sr_pred at unit 13 and saturated — the clean semi-regular profile,
same as n=15 null).

## 7. Unexpected observations (recorded per AGENTS rule 8)

1. **The deficit series is non-monotone with the n=17 point:**
   1,322 / 1,862 / **1,823** / 1,999 (n = 12/15/17/18). The n=15→17 increment
   is negative (−39). Whatever drives the deficit does not grow steadily with
   n over this range.
2. **Sem column support at n=17:** ncols = 314,472 = **81.9%** of
   C(35,≤5) = 384,168 — continuing the monotone decrease 84.2 / 82.2 / 81.9 /
   80.8% (n = 12/15/17/18) recorded in EXP-DREG-001; the null remains at 100%
   (384,168 exactly).
3. **Null saturation profile at n=17:** rank reached sr_pred 126,922 at col
   312,000 of 384,168 (unit 13) with zero new pivots in the final 4 units —
   the same clean semi-regular plateau as at n=15.
4. **Chunk-size effect on work:** partition B (chunk 20,000) of the identical
   sem cell used 16.7% less work-time than partition A (chunk 24,000)
   (1,828.4 vs 2,195.9 s) — plausibly contention timing; ranks identical.
5. **ENOSPC event:** transient disk exhaustion killed the first attempt; the
   volume self-recovered. Recorded as infrastructure, not evidence.

## 8. Artifact index

All under `experiments/EXP-DREG-002/`:

- `specification.yaml` (frozen protocol for this task)
- `DREG2_harness.py` (receipt harness), `scripts/verify_sem_partitions.py`,
  `scripts/verify_null_a.py` (control verifiers)
- `runs/RUN-DREG-002-CONTROL-N17-SEM-PARTCONSIST/` — failed_infrastructure
  (script path bug, no data; preserved, deviation D3)
- `runs/RUN-DREG-002-CONTROL-N17-SEM-PARTCONSIST-b/` — completed_valid,
  sem two-partition gate PASS; work/ holds sha256-pinned copies of both
  partitions' result/state JSONs
- `runs/RUN-DREG-002-CONTROL-N17-NULL-A-VERIFY/` — completed_valid,
  null-A C1 verification PASS; work/ holds sha256-pinned copies
- Each receipt: manifest.yaml, command.txt, environment.json, stdout.log,
  stderr.log, raw.json (where produced), work/ copies.
- `ledger/EV-DREG-002.yaml` references this experiment and the four
  EXP-DREG-001 measurement runs.
