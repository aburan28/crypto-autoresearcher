# Patch instruction for `ledger/goals/GOAL-ECQ-002/goal.yaml` — BATCH-8b08ef

**Authored by:** coordinator, at the opening of BATCH-8b08ef, the fourth and last batch under the
declared campaign budget.
**Applied by:** the orchestrating session, which runs the parse guard and makes the commit. The
Coordinator that wrote this file has no shell and did not edit `goal.yaml`.
**Why a patch file and not an edit:** three consecutive batches left `goal.yaml` out of a declared
artifact set and could not stage it (`DEC-20260823-ee9162` limitations, `BATCH-541940` checkpoint
`goal_record_flag_discrepancy`). This file is the exact replacement text, and it is itself declared
in `TASK-20260823-3eedf3`'s `artifact_paths` so that it is content-bound by this batch's ledger
archive.

**Goal status stays `active`.** Nothing here closes, pauses or retires the goal. The pre-declared
transition to `closed_at_budget` (unless `C1'` is met) belongs to `TASK-20260823-3eedf3` at the
close of this batch and to no record before it — `DEC-20260823-ee9162` N2.

---

## 1. Fields to replace, exactly

Replace the four fields below. Indentation is two spaces, i.e. they are direct children of
`research_goal:`. Nothing else in the file is touched by this patch.

### 1a. `current_batch_id` (currently `BATCH-da59ec`, two batches stale)

```yaml
  current_batch_id: BATCH-8b08ef
```

### 1b. `dispatch_queue_path` (currently points at `BATCH-da59ec`)

```yaml
  dispatch_queue_path: coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/dispatch_queue.json
```

### 1c. `next_action` — exactly one, replacing the two-batch-stale "Run BATCH-da59ec…"

```yaml
  next_action: >-
    RUN BATCH-8b08ef, THE FOURTH AND LAST BATCH UNDER THE DECLARED CAMPAIGN BUDGET. One job: test
    the tuple lever where it has never been tested, which is HIGH CEILING AT LOW CONTENT, and finish
    the truncated negative in the same run. Enumerate admissible canonical 6-tuples with the free
    squarefree-discriminant pre-filter applied FIRST, over a spread box large enough to yield a few
    hundred families of Shioda-Tate ceiling >= 13 at log P2 below 6; then rank-search all of them
    plus the 2114 unsearched fibres of BATCH-541940's 46 load-bearing families, across the full
    declared T-box with no height cap and no family cap; and report the coverage fraction actually
    reached, as numerator over denominator, with the certified-rank-versus-height curve and the
    random-curve null beside it. The binding text is the red team's next_concrete_action and
    resource_reading in
    coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/TASK-20260823-33a825/objections.yaml,
    which bind in preference to any paraphrase including this one. Both branches are pre-declared in
    H-ECQ-0ed5c8: full coverage returning no certified rank->=12 fibre below 79.32867457792244
    CLOSES the lever with a measured obstruction and is a complete result; one such fibre means
    BATCH-541940's central interpretive move was wrong. Coverage below 1.00 fires neither branch and
    the coverage fraction is then the result. NO CELL HAS BEEN TAKEN IN THREE BATCHES ON ANY METRIC.
    NO EXTENSION PAST THIS BATCH IS GRANTED OR IMPLIED. Queue
    coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/dispatch_queue.json, hypothesis
    H-ECQ-0ed5c8, review plan
    coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/review_plan.yaml. DISPATCH PRECONDITION: an
    EXP-ECQ-* contract must be minted, frozen and committed before TASK-20260823-827765 starts --
    fourth consecutive batch owing it, and DEC-20260823-ee9162 N1(h) makes a fifth instance a
    dispatch blocker rather than a recorded item.
```

### 1d. `latest_verified_commit` and its note

`latest_verified_commit` currently reads `ab0aa5404319796966241478dc44e25592139b44`, from
`BATCH-f2341e`. **The note must be replaced in the same patch**: it currently asserts that the
dispatcher's completed-archive check cannot pass under this session's durability-commit pattern,
which is WRONG and was superseded by `DEC-20260823-ee9162` R9(e) — `binding_mode: content_first` is
the supported path, and `BATCH-541940`'s snapshot archive passed under it with 100 of 100 declared
digests verified. Leaving the old note beside a new sha would make the record self-contradictory
and would republish a superseded claim.

```yaml
  latest_verified_commit: bc8d2e470
  latest_verified_commit_note: >-
    The latest commit of this campaign whose research content has been independently verified,
    supplied by the orchestrating session at the opening of BATCH-8b08ef. Recorded here, as always,
    with the standing caveat that A RECORD CANNOT CARRY THE SHA OF THE COMMIT THAT INTRODUCES IT, so
    the commit that applies this patch is necessarily not the one named. VERIFICATION MODE:
    binding_mode content_first, which is the SUPPORTED path rather than a workaround -- CLAUDE.md
    binds archive receipts to CONTENT first and treats commit reachability as advisory, and this
    campaign's archives have passed under it (BATCH-541940 snapshot, 100 of 100 declared digests
    verified against the tree by the validator's own recomputation). THE PRIOR NOTE AT THIS FIELD,
    asserting that the dispatcher's completed-archive commit-scope check CANNOT pass under this
    session's durability-commit pattern, IS WRONG AND IS SUPERSEDED BY DEC-20260823-ee9162 R9(e); it
    is replaced here rather than carried, and CORRECTION-archive-completed-verification.md is
    superseded by reference and must not be repeated. This field is re-set by BATCH-8b08ef's ledger
    archive TASK-20260823-3eedf3, which declares this path in its artifact_paths.
```

---

## 2. Deferred deliberately — do NOT apply now

Recorded so they are not lost and not smuggled in. Each belongs to `TASK-20260823-3eedf3`, whose
`artifact_paths` name `ledger/goals/GOAL-ECQ-002/goal.yaml` for the first time in this campaign.

- **`active_hypothesis_ids`** still reads `[H-ECQ-a609f8]`, which was `rejected_scoped` by
  `DEC-20260823-839fc6` and has been superseded twice (`H-ECQ-8b600d`, now `H-ECQ-0ed5c8`).
  Correcting it is a hypothesis-state change and belongs in the ledger archive alongside the
  batch's decision, not in a pre-dispatch patch.
- **`superseded_hypothesis_ids`** does not yet list `H-ECQ-8b600d`.
- **`status`**, **`checkpoints`**, **`decision_ids`**, **`evidence_ids`**: the transition to
  `closed_at_budget` (unless `C1'` is met), the `BATCH-541940` and `BATCH-8b08ef` checkpoint shard
  paths, `DEC-20260823-ee9162` / `DEC-20260823-722a46`, and `EV-ECQ-8ee697` / `EV-ECQ-5c2c0a` are
  all the ledger archive's to write. Note that `checkpoints` currently lists only `BATCH-f2341e`
  although `BATCH-da59ec` and `BATCH-541940` shards exist and are committed.
- **`objective`** states the elliptic-K3 ceiling as 18 over C and 17 over Q. For *this*
  construction the measured cap is 15 — every admissible family carries a multiplicative fibre at
  `T = infinity` of type `I_4` (13352 of 13391) or `I_6` (39). The objective is not wrong about the
  generic K3; it is silent about the construction. Superseding it is a research statement and
  belongs with the batch's evidence record.
- **`C1.met` / `C1prime.met` / `C2.met` flags** are correct as they stand (`C1` superseded, `C1'`
  not met, `C2` met with four qualifications) and must not be touched by this patch.

---

## 3. Parse guard

After applying, re-parse `ledger/goals/GOAL-ECQ-002/goal.yaml` and run
`python3 tools/validate_ledger.py` before committing. Two specific failure modes have cost this
program repair rounds and both are possible in this patch: opening a node with a scalar key and
continuing it as a sequence, and a `#` inside a flow mapping. Every replacement above is a plain
key with a folded block scalar (`>-`) or a plain scalar, at two-space indentation, and contains
neither.
