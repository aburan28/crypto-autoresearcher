# BATCH-960560 — Scope decision

## What this batch was asked to do

Design-gate (no code, no experiment execution) an Executor batch that carries
out `ledger/goals/GOAL-ECDLP-001/goal.yaml`'s currently-committed `next_action`
(sourced from `DEC-20260803-004`, checkpointed at `current_batch_id: BATCH-046`):
open a successor batch under frozen `PA-IT-001-v3-rc45-repair-5` that

1. exercises `CTRL-ANOMALOUS-TRACE1` at `bits=20` with a verified anomalous
   certificate and `C_special=ceil(8*log2(p))`,
2. persists a non-empty `CTRL_NULL_IT_PLANT` edge ledger and a live
   `CTRL-NULL-PACKAGING-GATE`,
3. emits `dominated_by` / `sota_delta` on run deliverables,
4. rebinds `execution_report`/manifest provenance,

then runs reserved measure if smoke controls pass, with independent
validate + red-team.

## What the design gate found

**This exact next_action was already executed**, in this same working tree,
before this design gate began — and its outcome was already superseded by two
further official Coordinator decisions. `ledger/goals/GOAL-ECDLP-001/goal.yaml`'s
`current_batch_id: BATCH-046` and `next_action` are **stale**.

Concretely, and in this exact repository:

- **BATCH-047** (`RUN-IT-001-rc47`, `EV-IT-aefd12`) already did (1)-(4)
  above: `CTRL-ANOMALOUS-TRACE1` closed at `bits=20` with a verified Smart
  anomalous certificate (ratio 0.202), a 48-row null-plant edge ledger, and a
  packaging gate that correctly rejects an uncertified synthetic result.
  Independent Validator `VAL-20260803-029` returned `COMPLETED_VALID_SCOPED`.
  Independent Red Team `RT-20260803-030` returned **FAIL** on three *new*
  formal-compliance defects unrelated to (1)-(4), and flagged a structural
  concern (O-6): trace of Frobenius is an isogeny-class invariant, so
  `rho_special=0` might not be a finite-scale artifact.
- **BATCH-048** (`TASK-20260804-002`, `EV-IT-511f3d`, `DEC-20260804-2fae6a`)
  resolved that concern: the **unconditional Tate isogeny theorem** proves
  ordinary `F_p`-isogenies preserve trace of Frobenius, so H-IT-001's three
  named special families (anomalous, MOV, Weil-descent) are isogeny-class
  invariants and **no finite ordinary isogeny path, at any scale, connects a
  generic curve to any of them**. `rho_special=0` is a mathematical
  certainty, not a measurement outcome. H-IT-001 transitioned
  `specified -> weakened` (ordinary-isogeny mechanism scope) on this
  decision.
- **BATCH-049 through BATCH-053** exhausted every proposed successor
  isogeny-based mechanism (class-group DLP reduction, Elkies ell-isogeny
  augmentation, ordinary isogeny MITM), converging on a named obstruction
  (`DEC-20260804-fec1e8`): the **scalar-domain mismatch** (ECDLP scalar has
  order `N~p`; every isogeny-related structure examined has order at most
  `h(D)~sqrt(p)`). **`SG-ECDLP-002` — the subgoal that owns H-IT-001 —
  transitioned `active -> paused`** with a named, explicit, still-unmet
  resume condition.
- **BATCH-060** and later (through checkpoint `BATCH-e0ccb2`, 2026-08-06)
  independently reconfirm both transitions and move the goal on to unrelated
  hypotheses (H-GGM-001, H-OIFP-097d1a, H-PSEUDO, Semaev BKK). None of them
  references H-IT-001, SG-ECDLP-002, or `PA-IT-001-v3-rc45-repair-5` again.

This is not a novel discovery. Two other coordinator sessions already found
and documented the same staleness without editing `goal.yaml` in place:
`ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-9c41dd.yaml` and
`ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-a83850.yaml` (the latter's
`goal_head_note` states verbatim that the head "is stale (current_batch_id
BATCH-046) relative to BATCH-121..124 merged from other sessions"). This
batch is a third, independent confirmation, specific to the exact thread the
stale `next_action` names.

## Scope decision

**No Executor task is dispatched under `PA-IT-001-v3-rc45-repair-5`.** Doing
so would duplicate already-completed, already-superseded work; would re-run a
measurement whose target quantity is now a proven mathematical certainty
rather than an open empirical question; and would silently violate the
still-standing pause condition on `SG-ECDLP-002` without meeting its named
resume condition. `H-IT-001` stays `weakened`; `SG-ECDLP-002` stays `paused`.
This batch authors no `coordinator_decision` and changes no status — the
finding is procedural (a stale goal-head pointer), not a new hypothesis
result.

## Recommendation

The orchestrating session should dispatch a **dedicated goal-head
reconciliation task** — reading every checkpoint under
`ledger/goals/GOAL-ECDLP-001/checkpoints/*.yaml` and every
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-*` directory newer than
`BATCH-046`, identifying the true latest checkpoint across all merged
sessions (currently `BATCH-e0ccb2` / `DEC-20260806-08b9ed`, 2026-08-06, unless
a later one exists that this design gate did not locate), and writing **one
new record** that supersedes the `BATCH-046` head explicitly — never editing
the `BATCH-046` note or `goal.yaml`'s current fields in place. Only after
that reconciliation should any new batch be opened against
`GOAL-ECDLP-001`'s "current" state, on the correct current thread (which, as
of the latest located checkpoint, is unrelated to H-IT-001 or
`PA-IT-001-v3-rc45-repair-5`).

See `batch.yaml` in this directory for the full evidence chain (record IDs
and artifact paths) and `dispatch_queue.json` for the task cards this batch
actually issues.
