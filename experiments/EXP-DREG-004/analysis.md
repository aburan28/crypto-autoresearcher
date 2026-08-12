# EXP-DREG-004 — analysis

**Experiment:** EXP-DREG-004 (hypothesis H-DREG-001; decisive past-wall point n=21, D=5)
**Instrument:** `src/h012c_block_m4ri.py` (checkpointable block-m4ri exact full-column
rank over GF(2), block-staircase carriers, sha256 `0eb38126…` — identical to the
EXP-DREG-001/002 validated instrument, verified by hash at receipt time)
**Executor sessions:** TASK-20260724-DREGN21 turn 1 (2026-07-24T19:43:41Z–20:38Z,
9 invocations), turn 2 (2026-07-24T20:38:51Z–21:33Z, 8 invocations), turn 3
(2026-07-24T21:33:53Z–22:25Z, 7 invocations), turn 4 (2026-07-24T22:34:43Z–23:30Z,
8 invocations). Per-turn budget 3,300 s wall / 12 runs; execution-surface foreground
cap 300 s per invocation.
**Cutoff:** 2026-07-24T23:15:42Z (last launch). Runs used: 9/12 + 8/12 + 7/12 + 8/12.

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
| columns processed | **192,000 / 778,394 (24.67 %)** |
| rank_acc (partial) | 186,574 (NOT a cell result — monotone nondecreasing lower bound only; 69.4 % of sr_pred) |
| instrument work | 2,498.4 s (`secs_total`, phase-sum; t1: 778.8, t2: +791.1, t3: +501.0, t4: +427.5) |
| observed wall | ≈ 1,560 (t1) + ≈ 2,235 (t2) + ≈ 2,030 (t3) + ≈ 2,135 s (t4, 8 invocations) |
| peak RSS | 12.0 GB (invocation 1, adjacency build); steady-state 5.5 → 9.4 GB, growing with rank |
| checkpoint state | `runs/RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_measure_n21_sem_a_sem_n21_t0/` |
| final state.json sha256 | `8617ff259819802c127ed2f93b42c7bf484e79208a6c75050db7ba99db5570c3` (t1: `c0f0fe42…fa2f`, t2: `79db92a9…fe291`, t3: `f41b32d5…8538f5`) |
| carries | 44 files, 1,377,166,667 bytes, **all sha256 re-verified post-run (turn 4)** |
| done flag | false |

**Exact resume command** (from repo root `/Volumes/Volume/crypto-autoresearcher`; each
invocation resumes from the shared checkpoint; partition A so far = 8,000-cols unit 1,
then 10,000 (units 2–9), 8,000 (10–12), 6,000 (13–17), 5,000 (18), 4,000 (19–24),
3,000 (25–29), 2,000 (30–32) — keep chunk ≤ 2,000–3,000 under a 300 s invocation cap):

```
/usr/bin/time -l env DOT_SAGE=/Volumes/Volume/crypto-autoresearcher/experiments/EXP-DREG-004/runtime/sage \
  /usr/local/bin/sage -python src/h012c_block_m4ri.py --n-list 21 --t 3 --targets 1 \
  --d 5 --seed 2026 --tag measure_n21_sem_a --budget 230 --max-units 1 \
  --chunk-force 2000 --which sem \
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
| 18 | …-CONT-17 | 142,000–147,000 | 5,000 | 145,858 | 8.53 GB |
| 19 | …-CONT-18 | 147,000–151,000 | 4,000 | 149,858 | 9.39 GB |
| 20 | …-CONT-19 | 151,000–155,000 | 4,000 | 153,858 | 8.82 GB |
| 21 | …-CONT-20 | 155,000–159,000 | 3,868 | 157,726 | 8.97 GB |
| 22 | …-CONT-21 | 159,000–163,000 | 3,898 | 161,624 | 8.91 GB |
| 23 | …-CONT-22 | 163,000–167,000 | 4,000 | 165,624 | 8.69 GB |
| 24 | …-CONT-23 | 167,000–171,000 | 3,805 | 169,429 | 8.75 GB |
| 25 | …-CONT-24 | 171,000–174,000 | 2,981 | 172,410 | 7.61 GB |
| 26 | …-CONT-25 | 174,000–177,000 | 2,455 | 174,865 | 9.59 GB |
| 27 | …-CONT-26 | 177,000–180,000 | 3,000 | 177,865 | 9.63 GB |
| 28 | …-CONT-27 | 180,000–183,000 | 2,195 | 180,060 | 8.23 GB |
| 29 | …-CONT-28 | 183,000–186,000 | 2,503 | 182,563 | 8.15 GB |
| 30 | …-CONT-29 | 186,000–188,000 | 1,554 | 184,117 | 7.82 GB |
| 31 | …-CONT-30 | 188,000–190,000 | 1,567 | 185,684 | 7.92 GB |
| 32 | …-CONT-31 | 190,000–192,000 | 890 | 186,574 | 7.75 GB |

Turn-4 pre-launch lineage: CONT-24's prelaunch state sha256
(`f41b32d5…8538f5`) was verified against turn 3's recorded final hash before any launch.
Turn-3 pre-launch lineage: CONT-17's prelaunch state sha256
(`79db92a9…fe291`) was verified against turn 2's recorded final hash before any launch.
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
  units 13–19 (cols 112k–159k) returned to exactly full-pivot; from col 159k the
  dependent density rises steadily: k/c per chunk 95–97.5 % (159k–171k) → 73–82 %
  (171k–190k) → **44.5 %** (unit 31, cols 190k–192k, k = 890/2,000) — the steepest
  dependent region so far. The n=18 late-column deficit zone (k/c → 0.001) is still
  ahead; rank_acc is 69.4 % of sr_pred at 24.67 % of columns.
- **nrows 279,048 > sr_pred 268,674:** even a semi-regular outcome would not be full
  row-rank; d_reg(sem) > 5 at n=21 regardless of the deficit outcome (same shape as
  n=18: 152,532 > 145,881).
- **Measured matmul rate 2.37e12** bit-ops/s (instrument `rate_mat`) vs 1.21e12 in the
  n=18 anchor — less foreign-session contention. Timings remain contention-caveated;
  ranks are exact integers.

## 5. Cost model update (measured, both sessions)

Per-unit phases at chunk c and rank r: reduce ≈ r × c × 8.24e-8 s (rate 2.37e12),
ech 0.5–16 s, post 3–51 s, fill/tr1 < 1 s. **Fixed per-invocation overhead dominates
and grows with the carry set: ≈ 170–190 s (t2) → ≈ 200–230 s (t3) → ≈ 215–225 s
(t4)** (sage start, adjacency load, carry load+sha256-verify, save_carry+hash-back,
gc/exit). The 300 s cap forced chunks 10k → 8k → 6k → 5k → 4k → 3k → 2k; turn-4
process walls 261–280 s. Remaining: 586,394 cols ≈ ~290 two-k invocations ≈ ~21 h
wall under this capped pattern (**≈ 35–45 further turns** at ~8 chunks/turn). The
single long session (≥ 3,600 s-per-invocation, chunk 24,000, ≈ 3.5–4.5 h) is **not
available on this surface** (turn-4 handoff) — the chunked pattern is the only route.
Timings contention-caveated.

## 6. Censoring table (stopping rules; none of this is evidence — AGENTS rule 5)

| Cell | State | Reason |
|---|---|---|
| sem n=21 D5 rank, columns 192,000–778,394 | censored at checkpoint | per-turn wall budgets (4 × 3,300 s) + 300 s invocation cap consumed; 24.67 % processed |
| two-partition consistency control (partition B) | not exercisable | requires a completed partition A first; mandatory before any rank claim |
| n=21 null arm | not attempted | explicitly out of scope |
| turn-1 10–12, turn-2 9–12, turn-3 8–12, turn-4 9–12 (of 12 per turn) | not launched | minute-~45 stop rule + 300 s wall margin exhausted |

No invocation was killed, OOM-censored, or hash-failed across all four sessions:
32/32 exit 0, all resume checks passed, zero failed_infrastructure records.

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
- **D7 (turn-3 chunk reductions, recorded pre-launch in CONT-17/CONT-18
  prelaunch.json):** 6,000 → 5,000 (unit 18) → 4,000 (unit 19); fixed overhead
  reached 200–230 s/invocation, leaving < 10 s of wall margin at turn end.
  Pure infrastructure pacing.
- **D8 (turn-4 chunk reductions, recorded pre-launch in CONT-24/CONT-29
  prelaunch.json):** 4,000 → 3,000 (unit 25) → 2,000 (unit 30); overhead growth
  kept consuming the margin (~296 s call at unit 28). Pure infrastructure pacing.

## 8. What this cell will decide once completed

Deficit(n=21) = 268,674 − rank_full against the series 1,322 / 1,862 / 1,823 / 1,999
at n = 12 / 15 / 17 / 18. Any value > 1,999 resumes growth (increments +540/−39/+176/?);
a value in [1,823, 1,999] extends the stall; a value < 1,823 is the first decline.
Nothing in the partial telemetry above prejudges the outcome — the deficit forms in the
late column region (n=18 pattern), which this checkpoint has not reached (the partial
rank_acc 186,574 is 69.4 % of sr_pred at 24.67 % of columns).

## 9. Artifact index

- `specification.yaml` (frozen parameters incl. sr_pred = 268,674), `sr_pred_n21.py`,
  `sr_pred_n21.json`, `sr_pred_n21.stderr`
- `checkpoint-summary.json` (final state sha256, carry verification, unit trajectory)
- `make_manifests.py` (receipt generator; re-runnable, covers all 32 runs)
- `runs/RUN-DREG-004-MEASURE-N21-SEM-A/` — invocation 1 + shared checkpoint
  `work/h012c_measure_n21_sem_a_sem_n21_t0/` (state.json + 29 carries + adjacency cache
  `h012c_adj_sem_n21_t3_i0_D5_s2026_0da7ff6aa40007e8.pkl`)
- `runs/RUN-DREG-004-MEASURE-N21-SEM-A-CONT-{1..31}/` — invocations 2–32
- Each run dir: `command.txt`, `stdout.log`, `stderr.log`, `environment.json`,
  `manifest.yaml`, `prelaunch.json` (CONT runs)

---

## 10. Restart lineage (2026-07-25 rebuild turn)

After INC-20260724-EXFAT-01 destroyed the carry payloads at 194,000 / 778,394
columns (24.93 %), the cell was **rebuilt from column 0** in a new run series
`RUN-DREG-004-REBUILD-A` (tag `rebuild_a`, fresh results dir; the ghost state
dir of the destroyed series was not resumed). Pre-incident lineage is preserved
in `STATE-RESCUE.json` (state.json sha256
`436b7121ae2c0403236fe7694090c178c444621b5e03dadaf5e72ade3a1f497f`, internally
consistent: sum(npiv) == rank_acc == 188,122).

**Identity gate PASS** on the fresh init: ncols = 778,394, nrows = 279,048,
sr_pred = 268,674, system_hash prefix `0da7ff6aa40007e8` — the frozen cell is
bit-identical to the destroyed one, so the rebuild measures the same
mathematical object.

Rebuild progress at end of turn: **52,000 / 778,394 columns (6.68 %)**, rank_acc
= 52,000 (full-rank plateau region, as expected this early), 7 units, 8 carry
files (2 pickle + 6 RAWCARR1), all sha256-verified, secs_total = 227.0
(instrument phase-seconds). No rank claim: cell incomplete.

## 11. Codec gate (verdict: PASS) and the RAWCARR1 store

The handoff gated the raw-bit carrier store on (a) bit-exactness vs pickle
carries and (b) load wall < pickle at 40+ blocks, with instant reversion to
pickle on failure. Gate script `codec_gate3.py`, data `codec_gate3.json`,
codec `rawcarrier.pyx` → `rawcarrier_ext.so` (per-row memcpy against the m4ri
`mzd_t` via `_entries`).

Measured on this cell's real data and a worst-case synthetic (279,048 x 6,808):

| payload              | pickle load | raw load | pickle dump | raw dump | bit-exact |
|----------------------|------------:|---------:|------------:|---------:|:---------:|
| real carry k=2,000   | 2.02 s      | 0.006 s  | 1.70 s      | 0.014 s  | yes |
| synthetic k=6,808    | 7.76 s      | 0.027 s  | 16.64 s     | 0.038 s  | yes |

Projected over the destroyed 45-file npiv distribution: raw load total
**0.7 s** vs measured pickle load **198.6 s** (44 blocks, 4.51 s/block, turn-5
probe) — margin 197.9 s per invocation. Gate (a) and (b) both PASS.

Integration: `src/h012c_block_m4ri_rawbit.py` (sha256 in checkpoint-summary;
derived from the hash-pinned `src/h012c_block_m4ri.py` 0eb38126…, which is
untouched). Only `save_carry` / `load_carries` changed: RAWCARR1 files (8-byte
magic, LE header length, JSON header {nr, k, P}, packed row-major bitmap),
sha256-per-file verification kept, pickle read fallback for the two pre-gate
carries; all mathematics identical. In-situ self-check passed: resume loaded
pickle carries and wrote RAWCARR1 (CONT-1), next resume loaded RAWCARR1 and
continued with nominal rank progression (CONT-2).

Effect on pacing: per-invocation wall is now compute-bound (adjacency ~42 s +
phases), so chunk 8,000 with 2 units/invocation fits the 300 s cap
(CONT-4: 237 s, RSS 4.7 GB). Unit cost at rank r ~ 46 s + ~0.65 s/1,000 rank
(reduce-dominated); ETA to full cell ~ 9–11 further turns at this cadence
(~93 invocations), vs ~35–45 turns had the gate failed.

Infra note: one invocation (CONT-3) was killed by the 295 s tool timeout after
completing and checkpointing 2 of 3 units — infrastructure event only (AGENTS
rule 5); state on disk was consistent at the last save boundary and the next
invocation resumed cleanly.

---

## 12. INC-20260725-EXFAT-02 and second rebuild (2026-07-25 turn 3)

Second payload destruction (see `INCIDENT-20260725-EXFAT-02.md`): after a
machine reboot (~01:38Z), the worktree was swept at ~04:20Z — all RAWCARR1
carries and state.json of the 124,000-col checkpoint deleted; the 2 legacy
pickle carries, the adjacency cache, and `.git` survived (same signature as
INC-01). Recovery: state reconstructed from the committed 52,000-col snapshot
truncated to the 2 sha256-verified survivors; resume identity checks passed.
**Countermeasure in force:** every invocation now mirrors new carry payloads
into the git object store (`mirror-log.json`), which survived both incidents.

Rebuild-2 progress at end of turn 3: **72,000 / 778,394 columns (9.25 %)**,
rank_acc = 71,993, 18 carries (2 pickle + 16 RAWCARR1) all sha256-verified and
git-mirrored. No rank claim: cell incomplete.

Dependent-density telemetry (watch item): first sub-full pivot unit of this
rebuild at cols 64,000–72,000 with k/c = 99.91 % (k = 7,993) — onset of the
dependent region, consistent with the pre-incident lineage (first dip 98.6 %
at cols 78,000–88,000; block boundaries differ, trend matches). All units
before it were full-pivot, matching the plateau expectation.

Pacing deviations (infrastructure only): D7 — first recovery invocation used
chunk 12,000 (single unit under budget 130); D8 — max-units reduced 2 → 1 from
col 48,000 as 2-unit walls hit 277.6 s of the 280 s tool cap under EXP-SIG-007
contention (real/user ratio up to 1.7, RSS to 6.4 GB).

## 13. Turn 4 (2026-07-25, 05:43-06:28Z): 116,000 / 778,394 (14.90 %)

+44,000 columns this turn (72,000 -> 116,000), rank_acc 114,858, 28 carries
(2 pickle + 26 RAWCARR1), all sha256-verified and git-blob mirrored per
invocation. Two 280 s tool-timeout kills at rank ~103k under residual load
(8k-chunk walls exceeded the cap); state consistent at both kills (AGENTS
rule 5). D9: chunk reduced 8,000 -> 6,000 for wall margin.

**Rank cross-validation:** rank_acc matches the pre-incident lineage EXACTLY
at cols 88,000 / 96,000 / 104,000 / 116,000 (87,615 / 95,299 / 103,068 /
114,858) — the rebuilt staircase is pointwise identical to the destroyed one
wherever the column grid aligns. Dependent density oscillating 96.0-99.5 %
through this region (pre-incident: 96.1-100 %), still far above the n=18
late-column deficit zone (~0.1 %). No rank claim: cell incomplete.

## 14. Turn 5 (2026-07-26, 02:03-02:48Z): 178,000 / 778,394 (22.87 %)

+62,000 columns (116,000 -> 178,000), rank_acc 175,865; 39 carries
(2 pickle + 37 RAWCARR1), all sha256-verified and git-blob mirrored. D10: a
2,000-col alignment unit (116k-118k) locked the chunk grid onto the
pre-incident lineage grid, enabling exact cross-checks at every subsequent
unit: rank_acc matches the rescued lineage EXACTLY at 118k / 124k / 130k /
136k / 142k (116,858 / 122,858 / 128,858 / 134,858 / 140,858). Combined with
turn 4 (88k / 96k / 104k), every aligned point of the rebuilt staircase is
bit-identical to the destroyed run. Dependent density: full-pivot through
148k, then 96.9 / 99.2 / 96.4 / 90.9 % (154k-178k) — the collapse region
opening on schedule vs lineage (73-82 % at 174k-183k, 44.5 % at 190k-192k).
Next aligned checks: 190k -> 186,574 and 194k -> 188,122 (rescued frontier).
Infra: /tmp mirror-log wiped mid-turn (second /tmp loss); blobs were safe in
.git and the log was rebuilt deterministically (hash-object without -w). No
rank claim: cell incomplete.

## 15. Turn 6 (2026-07-26, 07:28-08:13Z): 230,000 / 778,394 (29.55 %) — rescued frontier re-derived, virgin territory entered

+52,000 columns (178,000 -> 230,000), rank_acc 214,527; 48 carries (2 pickle +
46 RAWCARR1), all sha256-verified and git-blob mirrored.

**Frontier cross-check PASSED.** 190k -> 185,684 and 194k -> 188,122, both
bit-exact vs the STATE-RESCUE lineage; the 4k frontier unit's k = 2,438 equals
890 + 1,548 (the lineage's two sub-units) exactly. The rebuilt cell has now
re-derived the ENTIRE pre-incident lineage: every aligned rank point from
88,000 through the 194,000-col rescued frontier is identical. (Correction, new
record per rule 4: turn-5's summary wrote the expectation "190k -> 186,574";
186,574 is the lineage's 192k value. The true 190k value 185,684 is what the
rebuild produced — the measurement was right, the expectation string was
wrong.)

**Virgin territory onset (past 194k):** dependent density k/c = 57.9 / 75.4 /
94.8 / 66.1 / 69.9 % at 194k-230k — deep non-monotone oscillation, not a
monotone collapse. rank_acc 214,527 = 79.8 % of sr_pred (268,674) at 29.55 %
of columns. The deficit question remains open; the n=18 late-column deficit
zone (k/c ~ 0.1 %) has not appeared. RSS peaked 11.3 GB at 8k chunk; backed
to 6k (walls 214-219 s). No rank claim: cell incomplete.

## 16. Turn 7 (2026-07-26, 16:17-17:02Z): 266,000 / 778,394 (34.17 %)

+36,000 columns (230,000 -> 266,000), rank_acc 235,394 = 87.61 % of sr_pred
(268,674); 55 carries (2 pickle + 53 RAWCARR1), all sha256-verified and
git-blob mirrored. One 280 s timeout kill on the opening 8k attempt (C-reverse
contention; state consistent, rule 5); D11: chunk 6,000 -> 5,000 after a
278.6 s wall (1.4 s from cap). Walls then eased 259 -> 191 s as the control
fire wound down.

Dependent-density telemetry (virgin territory): k/c = 63.6 / 56.3 / 70.1 /
74.9 / 67.2 / **42.0 / 30.4** % (230k-266k). The oscillation persists, but
the last two units are the deepest dips measured anywhere in this cell (prior
minimum: 44.5 % at 190k-192k in the lineage). Direction is toward the n=18
deficit zone, but at ~30 % density it remains ~300x above that zone's ~0.1 %.
rank/cols: 235,394 at 266,000 cols — the deficit (if any) must form in the
remaining 512,394 columns. No rank claim: cell incomplete.

## 17. Turn 8 (2026-07-26, 18:59-19:44Z): 316,000 / 778,394 (40.60 %)

+50,000 columns (266,000 -> 316,000), rank_acc 255,033 = 94.92 % of sr_pred;
65 carries (2 pickle + 63 RAWCARR1), all sha256-verified and git-blob
mirrored. Ten clean invocations at chunk 5,000 (walls 188-222 s), zero kills.

Dependent-density telemetry: k/c = 30.8 / 43.0 / 49.4 / **21.4 (new cell
minimum)** / 25.5 / 25.5 / 40.9 / **86.1 (bounce)** / 43.6 / 26.6 %
(266k-316k). The 30-42 % dips of turn 7 did NOT monotonically deepen into the
deficit zone: the band oscillates with widening amplitude (this turn alone
spans 21.4-86.1 %). The n=18 late-column zone (~0.1 %) is still ~200x below
anything observed. Interpretation guard: with rank already 94.92 % of sr_pred
at 40.60 % of columns, the remaining ~24,000 pivots to sr_pred can form over
~462,000 columns at the observed mean density; a deficit (rank < sr_pred) of
any size remains fully consistent with the telemetry, and so does exact
semiregularity. No rank claim: cell incomplete.
