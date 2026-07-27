# EXP-SIG-007 analysis — n=21 residual_5 attempt (staged, checkpointed)

Thread: **SIG asymptotics (2026-07-24)**, handoff TASK-20260724-SIGN21.
Numbers-only observation; status decisions belong to the Coordinator.
Evidence record: `ledger/EV-SIG-007.yaml`.

## Headline

The mission's two decisive quantities — **D5 deficit at n=21** and
**residual_5 at n=21** — are **NOT measured**. rank(M5) at n=21 is a
hours-scale computation (measured rate this task: 333 s work for the first
6.17% of columns; honest extrapolation ~3–5 h per seed; DREG model
2.5–3.2×10⁴ s), unfinishable inside the 3,300 s / 12-invocation budget.
Per AGENTS rule 5 this is **infrastructure censoring, not evidence** in
either direction about the n=18 drop (1158 → 974).

What IS delivered: a memory-safe staged instrument that (i) passes all
controls, (ii) completes every cheap exact stage at n=21 on **two standard
seeds with zero variance**, producing new structural numbers (rankK5,
A3_5, A4_5, D5 support size), and (iii) leaves a sha256-verified,
resume-ready checkpoint for the rank stage at 48,000/778,394 columns.

## Controls — all PASS

| control | outcome | run |
|---|---|---|
| C1 null residual 0, both reductions, n=9/12 | PASS | RUN-a |
| C2 injected 3-generator syzygy detected | PASS | RUN-a |
| C3 T2 anchor n=15 s1 (D3 def 1, D4 def 40, residual 10/11) | PASS | RUN-a |
| C4a in-run determinism (n=15 s3 ×2) | identical | RUN-a |
| C9a staged-path anchors | n=12 s2: rankK5 **2093**, A3_5 **242**, A4_5 **444**; n=15 s1: **3944/392/705**; n=18 s1: **6650/578/1026** → residual_5 **974** implied — all EXACT | RUN-b, RUN-c |
| C9b staircase engine validation | rank **28,097** at n=12 s2 under chunk 4,000 (with mid-run resume) AND chunk 12,000 | RUN-b |
| C5 null arm n=21 D3/D4 | extra=0, rank==sr_pred on both seeds | RUN-d/e (S0) |
| C4b determinism n=21 s1 S0–S2 | identical modulo timing; S1 pickles byte-identical | RUN-d vs RUN-f |

The staged union-rank method (reduction-free `rank(K5 ∪ F) − rank(K5)` on
dense m4ri) reproduces the canonical full_reduce anchors **bit-exactly** at
three sizes — it is validated as a primary method, not just a cross-check.

## n=21 cells (sem, standard both seeds, zero seed variance)

| quantity | seed 1 | seed 2 | law/anchor check |
|---|---|---|---|
| filter standard | true | true | C8 |
| D3 deficit / extra | 1 / 1 | 1 / 1 | count-1 law ✓ |
| D4 deficit / extra | 56 / 56 | 56 / 56 | 8n/3 = 56 ✓ |
| residual_4 canonical / pinned | 15 / 14 | 15 / 14 | 2n/3+1 = 15 ✓ (EV-SIG-004) |
| B3 / B4 | 1 / 56 | 1 / 56 | == extras ✓ |
| D5 nrows | 279,048 | 279,048 | formula 21·C(42,≤3)+21·C(42,≤2) ✓ |
| D5 ncols (support) | **778,394** | **778,394** | new |
| sr_pred(D5) | 268,674 | 268,674 | computed, anchors cross-checked |
| rankK5 | **10,373** | **10,373** | new (family 10,374 → near-saturated) |
| A3_5 | **800** | **800** | new |
| A4_5 | **1,407** | **1,407** | new |
| rank(M5), deficit_5, extra_5, residual_5 | **unmeasured (censored)** | **unmeasured (censored)** | S3 pending |

**Preliminary flag:** the n=21 null arm was measured only through D4 (clean);
the null D5 control (extra=0, rank==sr_pred) needs the same hours-scale rank
and is **censored by cost** (AGENTS rule 5). All n=21 D5-stage sem numbers
above are therefore **PRELIMINARY** (no null D5 validation), per the
handoff's own fallback.

## New series points (preliminary at n=21)

- A3_5 (D3-syzygy closure rank at D5): 242 / 392 / 578 / **800** at
  n=12/15/18/21 — increments +150/+186/+222.
- A4_5 (D3+D4 closure rank at D5): 444 / 705 / 1,026 / **1,407** —
  increments +261/+321/+381. Both closure components keep growing at n=21.
- rankK5: 2,093 / 3,944 / 6,650 / **10,373** (n=12 s2 / 15 s1 / 18 s1 / 21).
- D5 support coverage: 84.2% / 82.2% / 80.8% / **79.84%** (778,394 of
  C(42,≤5) = 974,982) — the sem support keeps thinning (rule-8 structural
  series from EV-DREG-001 §3 extended one point).

## S3 (rank M5) checkpoint state + resume

**Update, turn 3 (resume t–y):** seed 1 advanced 128,000 → **159,000 /
778,394 columns (20.43%)**, rank_acc = 157,726, cumulative work 1,790 s
(+500 s this turn), 38 units, peak RSS ≤ 7.98 GB. Turn-3 runs: t (harness
kill after 1 checkpointed unit, 128–132k preserved; failed_infrastructure,
rule 5), u (132–138k), v (138–144k), w (144–149k), x (149–154k), y
(154–159k). Per-chunk k full (6,000/5,000) except a 4,868 dip on y —
rank/cols = 99.2% at 20%.

**Resume-overhead finding (recorded, drives the plan):** the per-invocation
resume cost is dominated by sage's m4ri pickle format (PNG-encoded GF(2)
matrices): measured adjacency unpickle 0.2 s, carrier sha256 8.3 s, carrier
unpickle **141.6 s at 33 blocks and growing ~4.3 s/block**. At ~250–280 s
load the harness cap would strangle the resume (projected near rank
~230–250k). Mitigation adopted this turn: `max-units 1` with chunk
5,000–6,000 (one full chunk per invocation, no mid-unit kills). Wall
efficiency is now ~32% work/wall; at ~500–600 s work per turn the tail is
**~23–27 turns**. A one-time carrier-codec engineering turn (raw-bit
store + fast reconstruction, or fewer/larger checkpoints) could lift this
to ~70–80% (~7 turns) — flagged to the Coordinator as an option; not
undertaken mid-measurement to preserve instrument stability.

- State: `experiments/EXP-SIG-007/work/n21_s1/rank5/` (state.json + 32
  carries, all sha256-verified). Resume (repeatable, ~4-min invocations):

  ```
  sage experiments/EXP-SIG-007/SIG7_run.sage --mode rank5 --n 21 --seed 1 \
       --work experiments/EXP-SIG-007/work/n21_s1 --budget 250 \
       --max-units 1 --chunk-force 5000 --out <RUN>/raw.json
  ```

  (Cadence since turn 3: `max-units 1` + chunk 5,000–6,000 — one full
  chunk per invocation; resume load is ~140–180 s and grows with rank.)

- Seed 2: rank not started; S1 adjacency checkpointed
  (`work/n21_s2/s1_adjacency.pkl`), resume-ready with the same command on
  `--work .../n21_s2`.
- Measured cost model (this instrument, this machine): 1,790 s work for
  159,000 cols; marginal ~17 s/1,000 cols growing ~linearly with rank.
  Extrapolated full-cell work ≈ 1.4–1.6×10⁴ s (~4.3 h) per seed; at
  ~500–600 s work per task turn (load-bound), **~23–27 more turns** to
  completion of seed 1 (~7 turns if the carrier-codec optimization is
  approved and lands).
- Once rank completes per seed: `extra_5 = (279,048 − rank) − 10,373`;
  `residual_5 = extra_5 − 1,407`; `deficit_5 = 268,674 − rank`.
- Two-partition control (different chunk size) is REQUIRED before any rank
  claim (spec C9b-style; budgeted for the completing turn).

## Deviations

- **D1 (driver debug, 2 extra invocations):** RUN-b took 3 attempts — the
  sage preparser coerced `random.Random(1)` → `Random(Integer)` and
  `Integer`/`RealNumber` literals broke `json.dump` (same bug class as
  EXP-DREG-001 D6). Both crashes are failed_infrastructure with no data;
  fixed (`int()`, an `fsafe` sanitizer) before any measurement.
- **D2 (RUN-g killed):** the h012c adaptive chunk formula clamps to
  24,000 columns when rank_acc = 0; one such chunk at n=21 (~290 s) exceeds
  the 300 s harness cap. Killed mid-first-chunk; the orphan carrier (no
  state.json) was discarded and rank5 restarted with `--chunk-force 4000`.
  AGENTS rule 5 — not evidence.
- **D3 (tighter cap):** per-invocation work capped ~170–235 s by the
  ~280 s harness cap (stricter than the mission's 600 s); checkpoint
  cadence increased accordingly.
- **D4 (null D5 censored):** a priori by cost; sem D5-stage quantities
  preliminary.

## Unexpected observations (rule 8)

1. The D5 sem support coverage at n=21 is **79.84%** — the thinning trend
   (84.2/82.2/80.8) continues; the support itself is identical in size
   across the two seeds (778,394 both).
2. rankK5 at n=21 is 10,373 of a 10,374-member family — near-saturated,
   matching the pattern at smaller sizes (2,093/2,094 at n=12).
3. No saturation shoulder through 16% of columns (rank_acc/cols = 99.1%;
   the n=12 sem cell saturated only in its final chunks; the n=15 null
   plateaued at sr_pred by 57% of columns).
4. Both closure components A3_5 and A4_5 keep growing at n=21 with
   *increasing* increments (+150/+186/+222 and +261/+321/+381) — whatever
   residual_5 turns out to be, the lower-degree closure does not shrink at
   n=21.

## What this establishes (numbers only)

The n=21 cell is staged, controlled, and 6.17% into its rank computation
with a verified resume path. The residual_5/deficit_5 question (decline
onset vs lattice fluctuation; deceleration vs re-acceleration) is
**untouched by this experiment's data** — both possible completions remain
open. The cheap-stage series (A3_5, A4_5, rankK5, support) extend cleanly
to n=21 with zero seed variance.
