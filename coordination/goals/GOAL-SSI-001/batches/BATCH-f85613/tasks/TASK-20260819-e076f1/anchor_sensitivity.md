# Anchor sensitivity — TASK-20260819-e076f1 (BATCH-f85613, GOAL-SSI-001)

Two anchors, both under the **corrected** charging law
(`log2T(w) = log2Tfull + 0.5*max(0, log2M-log2w) + overhead_bits`):

- **`fitted_opt`** — `RUN-WESOVOW-001/raw-result.json`'s own `per_field.*.optimal.{log2T,log2M}`
  (the B-grid-optimized, Dickman-fitted values).
- **`paper_pairs`** — `cost_model.py`'s own `PAPER_PAIRS` literal (the paper's raw
  Section 4.1 pairs, text-parsed from the source, never imported).

All numbers below are read from `recomputed_table.json` (produced by this
task's own `corrected_charging.py`), `c = 0.0` (zero hidden overhead) unless
stated otherwise.

## STANDING PROHIBITION, RESTATED VERBATIM AND NOT LIFTED

Per `batch.yaml`'s `standing_prohibition_carried_unchanged`: **"the crossover
values and never-beats-DG verdicts at P=384, P=576 and P=768 are
citation-eligible; the P=512 crossover value and its w=2^80 sign are NOT
citation-eligible pending resolution of the anchor ambiguity."** This task
does not lift that prohibition. Only a committed Coordinator decision on
independently reviewed evidence may ever lift it. The finding immediately
below is exactly why the prohibition exists, computed independently here for
the first time under both anchors together in one pass, and it does not
constitute the resolution the prohibition is waiting on.

## P=512 is the one field size whose sign flips between anchors, exactly at the tested boundary

At `w = 2^80`, `c = 0`:

| anchor | log2T(w) | log2speedup vs DG | beats Delfs-Galbraith? |
|---|---|---|---|
| `fitted_opt` | 256.98 | **−0.82** | **NO** |
| `paper_pairs` | 254.85 | **+1.15** | **YES** |

(`corr_wstar` — the corrected crossover memory — is `81.64` entries under
`fitted_opt` and `77.70` entries under `paper_pairs`; `w=2^80` straddles both,
landing 1.6-bit inside the "loses" side under one anchor and 2.3-bit inside
the "wins" side under the other.) **This is the sole cell, across the entire
5-field x 6-budget x 4-overhead grid, where the two anchors disagree on the
sign of `beats_baseline`.** It is exactly the P=512, w=2^80 sign the standing
prohibition names, confirmed here from a from-scratch recomputation rather
than assumed from the prohibition's own text.

## Every other field size: no sign flip anywhere in the tested grid

For P=384, P=576 and P=768, the `beats_baseline` flag at every one of the 24
tested (memory-budget, overhead) cells agrees between the two anchors — same
verdict, different magnitude only:

| log2p | w | c | fitted_opt beats? | paper_pairs beats? | agree? |
|---|---|---|---|---|---|
| 384 | 2^80 | 0.0 | True (+5.38) | True (+5.20) | yes |
| 384 | 2^30 | 0.0 | False (−19.62) | False (−19.80) | yes |
| 576 | 2^80 | 0.0 | False (−3.63) | False (−5.90) | yes |
| 576 | 2^30 | 0.0 | False (−28.63) | False (−30.90) | yes |
| 768 | 2^80 | 0.0 | False (−11.28) | False (−14.50) | yes |
| 768 | 2^30 | 0.0 | False (−36.28) | False (−39.50) | yes |

P=256's crossover magnitude differs by ~5 bits between anchors (`w* = 54.74`
fitted vs `49.50` paper-pairs, matching `CORR-20260808-c792f8`'s cited value
exactly), and its tested-grid sign pattern (loses at w<=2^50, wins at
w>=2^60 fitted; loses at w<=2^40, wins at w>=2^50 paper-pairs) shifts which
discrete tested budget is first to cross, but **no single tested `(w,c)` cell
for P=256 flips sign between anchors** the way the single P=512, w=2^80, c=0
cell does — P=256's crossover falls strictly inside a gap between two tested
grid points under both anchors (between 2^50 and 2^60 fitted; between 2^40
and 2^50 paper-pairs), so no tested cell is on the disagreeing side of both.

## Full corrected crossover (log2 w*, entries), both anchors, c=0

| log2p | fitted_opt anchor | paper_pairs anchor | delta (bits) | citation-eligible? |
|---|---|---|---|---|
| 256 | 54.74 | 49.50 | 5.24 | yes (not the boundary named by the prohibition) |
| 384 | 69.24 | 69.60 | 0.36 | **yes**, per standing prohibition |
| 512 | 81.64 | 77.70 | 3.94 | **NO — standing prohibition** |
| 576 | 87.27 | 91.80 | 4.53 | **yes**, per standing prohibition |
| 768 | 102.56 | 109.00 | 6.44 | **yes**, per standing prohibition |

The `paper_pairs`-anchor crossover values reproduce
`CORR-20260808-c792f8`'s independently-verified five-size table
(49.5/69.6/77.7/91.8/109.0) to the stated precision, an exact cross-check of
this task's independent recomputation against that correction's own
independent recomputation, both starting from the same `PAPER_PAIRS` literal
and the same corrected-law derivation, arrived at separately.

## Direction of the conclusions that DO NOT depend on the anchor choice

Regardless of anchor: under the corrected law and zero overhead, **the method
loses to Delfs-Galbraith at the low end of the tested memory-budget range
(`w=2^30`) at all five field sizes**, and the crossover memory needed to beat
Delfs-Galbraith **grows with field size** (roughly 50 to 110 bits of entries
across P=256..768, both anchors). At P=576 and P=768 the corrected crossover
(87-109 bits) sits at or above the largest tested budget (`w=2^80`), so the
method **never beats Delfs-Galbraith at any tested budget** for those two
sizes, under either anchor — this direction is anchor-invariant. Adding
overhead (`c>0`) only raises every crossover further (by `2c*sqrt(log2p)`
bits, same shift under both anchors and both laws), so it never restores a
"beats DG" verdict that was already false at `c=0`.

## What this does not establish

Per this batch's `claim_ceiling`: `certificate.kind` is `none` throughout.
Nothing here is an attack, a certificate, or a security statement about
SQIsign, CSIDH, or any standardized parameter set in either direction. This
does not resolve the P=512 anchor ambiguity (that requires a versioned
amendment and independent review, per `batch.yaml`'s `frozen_artifact_ruling`
and `relation_to_the_other_queued_items.item_3`) — it exhibits, quantitatively
and reproducibly, exactly the sign-flip the prohibition already anticipated,
using an independent from-scratch implementation rather than the prior
Validator's figures. No hypothesis status changes and no ledger record is
written by this task.
