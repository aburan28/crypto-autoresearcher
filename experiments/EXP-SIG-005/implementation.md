# EXP-SIG-005 implementation notes

## What this is

Cascade-law falsifiable checks for H-SIG-001, dispatched by DEC-20260718-020
(handoff TASK-20260718-SIGCHK). Two predictions:

- **P1** — the canonical D4 residual law `residual == 2n/3+1` (fit on
  n=12/15/18/21 = 9/11/13/15, EV-SIG-004) predicts **17 at n=24**; the T2 law
  predicts D4 deficit **8n/3 = 64** and D3 non-Koszul count **1**. Measured
  with the verbatim EXP-SIG-004 both-reduction construction (pinned
  early-break + canonical full_reduce + union cross-check) on >= 3 standard
  seeds, input-side filter per EXP-SIG-002.
- **P2** — the residual_D birth law predicts a D6-born non-rewritable
  component at n=12: `residual_6 = extra_6 - A5 > 0`, where A5 is the rank
  mod K6 of the multiplication closure of ALL lower-degree non-model
  syzygies (D3 extra x mults deg <= 3, D4 extras x <= 2, D5 extras x <= 1)
  — the exact analog of EXP-SIG-003's `residual_5 = extra_5 - A4` (878 at
  n=12 seed 2).

## Instrument

Bit-identical copies in `src/` (sha256 verified in-driver against the
pinned set on every run; gate refuses to proceed on mismatch).
`full_reduce` copied verbatim from EXP-SIG-003 `SIG3_run.sage`.

## Driver (SIG5_run.sage)

- `--mode gate`: C1 null residual 0 under both reductions (n=9,12), C2
  injected-syzygy detection, C3 T2 anchor n=15 s1 (D3 def 1, D4 def 40,
  pinned 10, canonical 11), C4a in-run determinism (n=15 s3 twice), plus a
  build-only n=24 filter probe (seeds 1..6: R_x, eq_degs_hist, standard
  flag, build seconds) used to pick the P1 seed set.
- `--mode p1 --cells n:seed:arm,...`: the EXP-SIG-004 measurement cell
  (used at n=24). Halts on union-cross-check mismatch (driver bug).
- `--mode p2 --n 12 --seed 2 --arm sem|null`: the D6 closure cascade.
  Sem arm: D3/D4/D5 with extract=True -> extra quotient bases B3/B4/B5
  (canonical full_reduce mod K_D + echelon; the model family's images lie
  in K6 by the Koszul/principal composition argument of EXP-SIG-003, so
  extra-basis images span the same closure); residual_4 canonical;
  D5-closure continuity A3_5/A4_5/residual_5 (C9 anchors 242/444/878 halt
  the run BEFORE the expensive stage on mismatch); D6 count-only
  classification; closure images F3/F4/F5 at D6; closure ranks TWO exact
  ways (incremental-merged pivots from kpiv6; independent
  full_reduce-mod-K6 family ranks) plus a reduction-free union-echelon
  cross-check (C6). Null arm: count-only D3..D6; closure empty iff all
  lower extras are 0; control requires extra_6 = 0 and rank == sr_pred.

## Checkpoint / kill rule (600 s per invocation)

Every stage boundary is a checkpoint: the soft cap (default 520 s) is
checked before starting each stage/cell, and the D6-classification and
closure-rank stages are wrapped in a driver-level SIGALRM timer. A firing
timer records `censored_timeout_<stage>` (infrastructure censoring, AGENTS
rule 5 — NOT evidence) and the run exits cleanly with everything completed
flushed to raw.json. The instrument is untouched by this (the timer lives
in the driver).

## Censoring plan (pre-registered)

1. P2 null D6 arm (censor first), 2. P2 determinism repeat, 3. P2 entirely
(deliver P1 only). P1 never goes below 3 standard seeds. n=15 at D6 is not
attempted: its matrix is ~547k rows x ~768k cols (nb=30), an order of
magnitude beyond the 600 s cap — recorded as a deliberate scope decision,
not a measurement.

## Size estimates (from EXP-SIG-003/004 receipts + semireg_rank_pred)

- n=24 D4: nb=48, nrows 29,424, pred(4) 29,124 -> expected rank 29,060
  (deficit 64). ~20-45 s/cell by extrapolation from n=21 (9-13 s).
- n=12 D6: nb=24, nrows 183,312, ncols 190,051, pred(6) 156,520. The D5
  cell took 5 s (sem) / 24 s (null); D6 is ~6x rows, ~3.4x columns,
  ~5x rank — feasibility inside 520 s uncertain, hence the timer.
