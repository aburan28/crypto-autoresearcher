# EXP-DREG-004 — analysis

**Experiment:** EXP-DREG-004 (hypothesis H-DREG-001; decisive past-wall point n=21, D=5)
**Instrument:** `src/h012c_block_m4ri.py` (checkpointable block-m4ri exact full-column
rank over GF(2), block-staircase carriers, sha256 `0eb38126…` — identical to the
EXP-DREG-001/002 validated instrument, verified by hash at receipt time)
**Executor sessions:** TASK-20260724-DREGN21 turn 1 (2026-07-24T19:43:41Z–20:38Z,
9 invocations) and turn 2 (2026-07-24T20:38:51Z–21:33Z, 8 invocations). Per-turn
budget 3,300 s wall / 12 runs; execution-surface foreground cap 300 s per invocation.
**Cutoff:** 2026-07-24T21:18Z (last launch). Runs used: 9/12 (turn 1) + 8/12 (turn 2).

---

## 1. Cell status — IN PROGRESS, CHECKPOINTED (no rank claim)

| quantity | value |
|---|---|
| system | boolean chained Semaev m=3, sem arm, t=3, ti=0, seed 2026 |
| n | 21 (nb = 42; 42 equations: 21 cubic + 21 quadratic) |
| system_hash | `0da7ff6aa40007e8…` (full 64-hex in state.json) |
| nrows | 279,048 |
| ncols | 778,394 (= **79.83%** of boolean simplex C(42,≤5) = 974,982) |
| **sr_pred (D=5)** | **268,674** (HF = [1, 42, 840, 10577, 93198, 601650, 2870049]) |
| columns processed | **142,000 / 778,394 (18.24 %)** |
| rank_acc (partial) | 140,858 (NOT a cell result — monotone nondecreasing lower bound only) |
| instrument work | 1,569.9 s (`secs_total`, phase-sum; turn 1: 778.8, turn 2: +791.1) |
| observed wall | ≈ 1,560 s (turn 1, 9 invocations) + ≈ 2,235 s (turn 2, 8 invocations) |
| peak RSS | 12.0 GB (invocation 1, adjacency build); steady-state 5.5 → 9.4 GB, growing with rank |
| checkpoint state | `runs/RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_measure_n21_sem_a_sem_n21_t0/` |
| final state.json sha256 | `79db92a932bba04aea4eecfce392393cbf80497ef04966ffbdec4f6da16fe291` |
| carries | 29 files, 1,156,252,875 bytes, **all sha256 re-verified post-run** |
| done flag | false |

**Exact resume command** (from repo root `/Volumes/Volume/crypto-autoresearcher`; each
invocation resumes from the shared checkpoint; partition A so far = 8,000-cols unit 1,
then 10,000 (units 2–9), 8,000 (units 10–12), 6,000 (units 13–17) — keep chunk ≤ 6,000
under a 300 s invocation cap):

```
/usr/bin/time -l env DOT_SAGE=/Volumes/Volume/crypto-autoresearcher/experiments/EXP-DREG-004/runtime/sage \
  /usr/local/bin/sage -python src/h012c_block_m4ri.py --n-list 21 --t 3 --targets 1 \
  --d 5 --seed 2026 --tag measure_n21_sem_a --budget 230 --max-units 1 \
  --chunk-force 6000 --which sem \
  --results-dir experiments/EXP-DREG-004/runs/RUN-DREG-004-MEASURE-N21-SEM-A/work
```

For a session with a larger per-invocation cap C seconds: `--budget C-60 --max-units 0`
and a larger chunk may be restored (e.g. 24,000) — per-unit reduce grows ∝ rank and
reaches ≈ 220 s/10k-cols at the projected final rank ≈ 266k. The mandatory partition-B
consistency control must re-run the completed cell from scratch with a *different* chunk
(e.g. `--chunk-force 12000` or 24000) and require identical rank + system_hash.

## 2. sr_pred provenance (pre-computation control — PASS)

`sr_pred_n21.py` (independent of the instrument; output `sr_pred_n21.json`): nb = 42,
eq_degs = 21×3 + 21×2, HF and `sr_pred_D5 = 268,674`, build 0.45 s. The instrument's own
init recomputed `pred = 268674` — exact agreement. PASS.

## 3. Invocations (all exit 0; zero infrastructure failures)

| # | run | cols added | k_new | rank_acc after | peak RSS |
|---|---|---|---|---|---|
| 1 | RUN-DREG-004-MEASURE-N21-SEM-A | 0–8,000 (+adj build 39.6 s) | 8,000 | 8,000 | 12.0 GB |
| 2 | …-CONT-1 | 8,000–18,000 | 10,000 | 18,000 | 5.45 GB |
| 3 | …-CONT-2 | 18,000–28,000 | 10,000 | 28,000 | 5.63 GB |
| 4 | …-CONT-3 | 28,000–38,000 | 10,000 | 38,000 | 5.98 GB |
| 5 | …-CONT-4 | 38,000–48,000 | 10,000 | 48,000 | 6.50 GB |
| 6 | …-CONT-5 | 48,000–58,000 | 10,000 | 58,000 | 6.45 GB |
| 7 | …-CONT-6 | 58,000–68,000 | 10,000 | 68,000 | 5.61 GB |
| 8 | …-CONT-7 | 68,000–78,000 | 9,864 | 77,864 | 7.79 GB |
| 9 | …-CONT-8 | 78,000–88,000 | 9,751 | 87,615 | 8.10 GB |
| 10 | …-CONT-9 | 88,000–96,000 | 7,684 | 95,299 | 8.09 GB |
| 11 | …-CONT-10 | 96,000–104,000 | 7,769 | 103,068 | 8.44 GB |
| 12 | …-CONT-11 | 104,000–112,000 | 7,797 | 110,865 | 8.67 GB |
| 13 | …-CONT-12 | 112,000–118,000 | 5,993 | 116,858 | 8.97 GB |
| 14 | …-CONT-13 | 118,000–124,000 | 6,000 | 122,858 | 8.27 GB |
| 15 | …-CONT-14 | 124,000–130,000 | 6,000 | 128,858 | 8.99 GB |
| 16 | …-CONT-15 | 130,000–136,000 | 6,000 | 134,858 | 9.20 GB |
| 17 | …-CONT-16 | 136,000–142,000 | 6,000 | 140,858 | 9.40 GB |

Turn-2 pre-launch lineage: CONT-9's prelaunch state sha256
(`c0f0fe42…fa2f`) was verified against turn 1's recorded final hash before any launch;
every continuation then passed the instrument's native resume gates (run-identity check
on n,t,ti,D,seed,which + per-carry sha256 at load). Each CONT run dir pins its
pre-launch state.json sha256 in `prelaunch.json`.

## 4. Observations (partial-cell telemetry; NOT cell results)

- **Column support continues its decline (rule 8):** sem ncols / C(nb,≤5) =
  84.2 / 82.2 / 81.9 / 80.8 / **79.83 %** at n = 12 / 15 / 17 / 18 / 21 — the
  support-matched null covers 100% at every measured size.
- **Dependent-column profile is non-monotone along the column order (new, turn 2):**
  units 2–7 full-pivot (k = chunk); a dip at cols 68k–112k (k/c ≈ 95–97.5 %);
  units 13–17 (cols 112k–142k) returned to exactly full-pivot (k = 6,000 = chunk).
  The deficit-forming region seen at n=18 (late columns) has not yet been entered.
- **nrows 279,048 > sr_pred 268,674:** even a semi-regular outcome would not be full
  row-rank; d_reg(sem) > 5 at n=21 regardless of the deficit outcome (same shape as
  n=18: 152,532 > 145,881).
- **Measured matmul rate 2.37e12** bit-ops/s (instrument `rate_mat`) vs 1.21e12 in the
  n=18 anchor — less foreign-session contention. Timings remain contention-caveated;
  ranks are exact integers.

## 5. Cost model update (measured, both sessions)

Per-unit phases at chunk c and rank r: reduce ≈ r × c × 8.24e-8 s (rate 2.37e12),
ech 4–16 s, post 24–51 s, fill/tr1 < 1 s. **Fixed per-invocation overhead dominates the
300 s-capped pattern and grows with the carry set: ≈ 170–190 s by turn 2** (sage start
~10 s, adjacency load ~10 s, carry load+sha256-verify ~40–60 s, save_carry+hash-back
~40–60 s, gc/exit). Consequently the 300 s cap forces shrinking chunks (10k → 8k → 6k)
and ~55–65 % of each invocation is overhead. Remaining: 636,394 cols. Under this
300 s-capped pattern ≈ 8–9 h additional wall; under a ≥ 3,600 s-per-invocation session
with chunk 24,000 and `--max-units 0`, overhead amortizes to a few % and the measured
phases project ≈ **3.5–4.5 h additional wall** (previous model 7–9 h; rate measured
faster than the n=18 anchor). Timings contention-caveated.

## 6. Censoring table (stopping rules; none of this is evidence — AGENTS rule 5)

| Cell | State | Reason |
|---|---|---|
| sem n=21 D5 rank, columns 142,000–778,394 | censored at checkpoint | per-turn wall budgets (2 × 3,300 s) + 300 s invocation cap consumed; 18.24 % processed |
| two-partition consistency control (partition B) | not exercisable | requires a completed partition A first; mandatory before any rank claim |
| n=21 null arm | not attempted | explicitly out of scope |
| turn-1 runs 10–12, turn-2 runs 9–12 (of 12 per turn) | not launched | minute-~45 stop rule reserving receipt time |

No invocation was killed, OOM-censored, or hash-failed across both sessions: 17/17
exit 0, all resume checks passed, zero failed_infrastructure records.

## 7. Deviations from handoff / prior pattern

- **D1 (invocation size):** handoff specified ~2,700 s capped invocations; the execution
  surface caps foreground commands at 300 s, so invocations are 300 s-capped
  (`--budget 230 --max-units 1`). Same checkpoint lineage, finer grain; zero
  partial-unit losses (every invocation ends at a clean checkpoint boundary).
- **D2 (shared checkpoint dir):** continuations resume the *same* state dir rather than
  the N17-CONT-1 pattern of copying the parent checkpoint package per run dir.
  Rationale: disk-tight environment (carry set 1.16 GB and growing). Logical lineage is
  preserved via sha256-pinned prelaunch manifests + instrument-native carry verification;
  the turn-2 launch verified the recorded turn-1 final hash before resuming.
- **D3 (chunking):** partition A is unit 1 at 8,000 cols, then 10,000 (units 2–9),
  8,000 (units 10–12), 6,000 (units 13–17) — shrinking to keep wall < 300 s as the
  fixed overhead grows. All boundaries are recorded verbatim in state.json; partition
  independence is exactly what the pending two-partition control will re-test.
- **D4 (manifest format):** manifests are JSON-serialized YAML (valid YAML 1.2).
- **D5 (budget underuse):** 3 (turn 1) + 4 (turn 2) of the per-turn 12 allowed runs
  deliberately unused (stop-launch rule).
- **D6 (turn-2 chunk reduction, recorded pre-launch in CONT-12/prelaunch.json):**
  8,000 → 6,000 at unit 13; pure infrastructure pacing, no mathematical meaning.

## 8. What this cell will decide once completed

Deficit(n=21) = 268,674 − rank_full against the series 1,322 / 1,862 / 1,823 / 1,999
at n = 12 / 15 / 17 / 18. Any value > 1,999 resumes growth (increments +540/−39/+176/?);
a value in [1,823, 1,999] extends the stall; a value < 1,823 is the first decline.
Nothing in the partial telemetry above prejudges the outcome — the deficit forms in the
late column region (n=18 pattern), which this checkpoint has not reached (the partial
rank_acc 140,858 is 52.4 % of sr_pred at 18.24 % of columns, i.e. the full-pivot
plateau region).

## 9. Artifact index

- `specification.yaml` (frozen parameters incl. sr_pred = 268,674), `sr_pred_n21.py`,
  `sr_pred_n21.json`, `sr_pred_n21.stderr`
- `checkpoint-summary.json` (final state sha256, carry verification, unit trajectory)
- `make_manifests.py` (receipt generator; re-runnable, covers all 17 runs)
- `runs/RUN-DREG-004-MEASURE-N21-SEM-A/` — invocation 1 + shared checkpoint
  `work/h012c_measure_n21_sem_a_sem_n21_t0/` (state.json + 29 carries + adjacency cache
  `h012c_adj_sem_n21_t3_i0_D5_s2026_0da7ff6aa40007e8.pkl`)
- `runs/RUN-DREG-004-MEASURE-N21-SEM-A-CONT-{1..16}/` — invocations 2–17
- Each run dir: `command.txt`, `stdout.log`, `stderr.log`, `environment.json`,
  `manifest.yaml`, `prelaunch.json` (CONT runs)
