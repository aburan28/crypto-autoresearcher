# TASK-20260729-014 — Freeze the EXP-YIELD-002 repaired-null contract

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs and the
disagreement is a defect to be reported**, not resolved by preference.

| | |
|---|---|
| **Role** | coordinator |
| **Depends on** | nothing |
| **Archived by** | TASK-20260729-015 |
| **Budget** | 3600 s, 2 GB, `maximum_runs: 1` (schema rejects 0; the semantically correct value is ZERO — this card executes nothing) |
| **Inference** | requested policy `coordinator-orchestration-code`; record the resolved model and `fallback_used` honestly |

## Objective

Convert **RC-A** into one frozen experiment contract `EXP-YIELD-002` at status
`review_required`, carrying the pre-registered prediction verbatim, both
denominator readings, the de-duplicated declared cell set, the explicit
identity-bin treatment and `confirmatory_status: exploratory_only` — and write
the criterion feasibility table that evaluates every threshold and invalidation
rule with shown arithmetic at the exact cells that will run.

## Exclusive write scope

- `experiments/EXP-YIELD-002/specification.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014`

## Artifact paths (exact)

1. `experiments/EXP-YIELD-002/specification.yaml`
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md`

## What RC-A is, in the governing record's own terms

At the four `INV-4`-failing cells of BATCH-011 — `(k=18, β=0.200, m=3, B=16,
C_red=688)`, `(k=16, β=0.225, m=3, B=16, C_red=688)`, `(k=18, β=0.225, m=3,
B=24, C_red=2312)`, `(k=18, β=0.250, m=3, B=28, C_red=3668)` — and at a declared
sample of passing cells, run the antipodal occupancy null **with the
pre-marking**: mark `|S_{m−2}|` bins chosen uniformly at random, then throw
`C_red/2` antipodal pairs, then count distinct occupancy. Compare against the
**unchanged** `P_pred` under **both** denominator readings.

Governing record: `ledger/decisions/DEC-20260729-001.yaml`, next action `NA-1`.
Its text is not weakened, paraphrased or narrowed.

## Binding freeze constraints (each from a named objection)

- **RC-E** — primary criterion under the standard-error-of-the-mean reading,
  secondary under the single-replicate sd, **both** reported, **both** required
  to pass. Replicate schedule fixed to the amended `C-14` (100 / 30 / 10 by
  `C_red`) with the reason stated: raising it tightens SEM by ~`sqrt(count)` and
  could fire the criterion on a known second-order term rather than a
  measurement fault. A high-precision diagnostic block is required and must be
  labelled as feeding **no** criterion.
- **RC-C** — declared cell set is the 49 criterion-evaluable BATCH-011 cells
  **de-duplicated on measured `B` within each `(k, m)` column**, merging
  `(k=12, β=0.325)` and `(k=12, β=0.350)` (identical `B = 22`, `C_red = 1782`)
  into one tuple, yielding 48 distinct tuples. Name the merged cells.
- **RC-G** — `confirmatory_status: exploratory_only`, with its basis stated, and
  pre-registration **order** distinguished from confirmatory **standing**.
- **RC-D** — no unquantified comparative word in any criterion.
- **OB-10** — identity bin handled **explicitly**: `(N−1)/2` antipodal-pair bins
  plus the identity bin, whether it may be pre-marked, whether it may be hit,
  the odd-`C_red` rule, the effect-size arithmetic, and any difference from the
  BATCH-011 process declared **before data**.
- **DEFER-BATCH009-003** — criterion feasibility table mandatory, including the
  counterfactual in which the diagnostic is wrong and the repaired null still
  falls short by the full `|S_{m−2}| e^{−λ}` term.
- **RC-8** — DETERMINED or SAMPLED per quantity, per cell.
- **RC-7** — declared **inapplicable**, with the reason. Nothing here solves an
  instance, so there is no matched rho/BSGS baseline. Do not fabricate one and
  do not silently omit the requirement.

## Prohibitions

Create no hypothesis and change none (`hypothesis_id: null`, with a note that
this experiment tests no hypothesis). Specify **zero curve arithmetic**. Compute
no efficiency `E` and no yield ratio. Do not un-fire or re-dispose `INV-4`.
Declare `INV-5` neither way. Touch no cost model — even a fully repaired null
yields no cost-model consequence (`O-6`, not `O-4`). Edit nothing under
`experiments/EXP-YIELD-001`. **Make no commit.**

## Completion gate

`F1`–`F10` as listed in the queue entry. `F7` (the feasibility table, including
the counterfactual firability check) is the point of the card.
