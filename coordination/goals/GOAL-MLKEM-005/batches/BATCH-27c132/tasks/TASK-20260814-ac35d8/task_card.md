# TASK-20260814-ac35d8 — PROPOSE IDEAS on RQ-MLKEM-001 for GOAL-MLKEM-005's own C1-C3

    goal / batch    GOAL-MLKEM-005 / BATCH-27c132
    role            idea-generator
    policy          research-deep                      effort high
    state           queued
    depends_on      (none)
    review_required false
    archived_by     (not yet minted -- see dispatch_queue.json pending_tasks_awaiting_ids)
    budget          7200 s, 2 GB, 1 run
    claim tier      N/A (ideation; no measurement, no claim)

## What this task is for

Discharges `DEC-20260814-b0a095`'s single `next_action` via option (ii) of the
three it licensed but did not commission: redirect `RQ-MLKEM-001` capacity
toward `GOAL-MLKEM-005`'s own still-untouched primary completion criteria,
rather than (i) a further reformulated-M2/instrument-extension follow-up on
the now-`analyzed` `H-MLKEM-11aabf`, or (iii) advancing `H-MLKEM-232843` or
`H-MLKEM-34e22e`. The full reasoning, including two corrections to this
session's own opening brief (`EXP-MLKEM-bfdb63` targets a different goal
entirely; the nearest existing ledger object to C1-C3, `H-MLKEM-dc51f5`,
measures a different mechanism), is recorded in
`PORTFOLIO-RULING-20260814.md` in this same batch directory.

Because no hypothesis currently in the ledger targets `GOAL-MLKEM-005`'s own
tracked object (a shared BKZ-beta-reduced basis; the per-target ratio
`R = ||pi_{d-beta}(e)||^2 / ||e||^2` of a CBD error vector under best-of-M
ciphertext selection) directly, this batch opens with `/propose-ideas`
(`docs/task-lifecycle.md` step 2), not `/design-experiment`: there is nothing
mature enough to freeze into a protocol yet.

## What it asks for

3-5 structured, falsifiable proposals on `RQ-MLKEM-001`, each targeting at
least one of `GOAL-MLKEM-005.completion_criteria` C1 (a numeric best-of-M
`dbeta` bound under a named cost model), C2 (a census of M across
standardised/deployed ML-KEM specifications -- the cheapest of the three, a
literature/citation task with no lattice compute required), or C3 (the
projected-error left-tail measurement on real BKZ-reduced bases with real CBD
errors, adjudicated against the Beta tail law). At least one proposal must
address C2 directly; at least one must address C1 and/or C3.

The handoff directs the idea-generator to check novelty against
`H-MLKEM-dc51f5` (key-side multi-target selection by secret norm -- adjacent,
not identical) and `H-MLKEM-11aabf` (same pinned `tools/sage_free_estimator`
instrument, different object -- ciphertext-side noise-model readout, not
best-of-M selection) before assigning any `novelty_status` stronger than
`unverified`, and to state explicitly, per idea, that
`GOAL-MLKEM-005.ceiling_known_in_advance` already proves no lane of this goal
can move an exponent, so every `target_complexity` field is bounded by that
proven constant rather than silently omitted.

## What it does not do

Creates no hypothesis. Changes no hypothesis status. Does not close, pause,
or complete `GOAL-MLKEM-005`. Does not authorize, freeze, or repair
`EXP-MLKEM-bfdb63` or `EXP-MLKEM-6715e6`. Does not reopen or re-score the
`hkz`/HKZ-independence lineage or `H-MLKEM-11aabf`'s own findings. Mints no
identifier by invention -- any `IDEA-*` filed from this task's output is
minted via `tools/allocate_id.py --next idea --check` by whichever session
holds a shell when the output is ready to file (declared gap `G-1`,
`dispatch_queue.json`).

## Next steps after this task completes

1. The returned idea(s) are verified against the schema
   (`.claude/skills/propose-ideas/SKILL.md` step 4); incomplete ideas go back,
   not repaired by the Coordinator.
2. `IDEA-YYYYMMDD-<tok>` identifier(s) are minted (one per complete idea),
   two-scope `--check`'ed, and each idea is saved under `ledger/proposals/`.
3. A Coordinator-only snapshot archive task (new `TASK-*` id, minted then)
   commits exactly the new `ledger/proposals/IDEA-*.yaml` path(s), any
   `knowledge/literature/` notes the novelty check produced, and its own
   receipt -- run alone, per this goal's established snapshot-before-review
   discipline, before any idea is treated as filed.
4. Only then does a separate Coordinator act select among the filed ideas (or
   rule none is decision-ready) and, if warranted, convert one to a frozen
   `H-MLKEM-*` hypothesis via `/design-experiment` in a subsequent batch.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-27c132/tasks/TASK-20260814-ac35d8/task_card.md
