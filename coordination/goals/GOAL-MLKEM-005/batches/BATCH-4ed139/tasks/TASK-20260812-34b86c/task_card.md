# TASK-20260812-34b86c — author PREREG-1, the frozen pre-registration

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           coordinator
    policy         coordinator-orchestration-code      effort high
    state          completed (executed 2026-08-12, NO SHELL)
    depends_on     (none — this is the batch's first task)
    archived_by    TASK-20260812-1ed548
    budget         5400 s wall clock, 2 GB, 1 run
    claim tier     TOY

## Objective

Write and freeze PREREG-1: the G-VAR2 criterion per AM-16 (a)(b)(c) with the
AM-17(c) fibre clause and the AM-17(d) family declaration; both fixtures'
declared target behaviour; the V_evade prediction and its falsifier; and the
**three-way termination clause** with what each branch licenses and forbids —
all before any measurement exists.

## Why this task exists and is archived alone

If the termination clause is written after the numbers, the batch can only
assert an outcome it chose after seeing them, and six consecutive instrument
batches would be followed by a seventh chosen the same way. The ordering is the
substance.

## Artifacts

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-34b86c/prereg.md

`prereg_sha256.txt` is **not** this task's artifact: the executing session held
no shell and could not compute a hash, and inventing one would be a fabrication
under AGENTS.md rule 9. It is owned by TASK-20260812-1ed548 (queue gap G-4).

## What this task actually found

Two things neither review wave and neither prior amendment contains, both found
by writing the specification rather than by measuring:

1. **AM-16(a)'s scaled criterion is undefined for any beta-free candidate.**
   Its scale is the candidate's own between-cell range at fixed (d,k), taken
   over the beta grid; a beta-free candidate has range exactly 0. `rdet` is
   beta-free **by definition**, so the naive reading `s/0 = +inf → ADMIT` would
   make fixture F1 fail for an arithmetic reason rather than a lattice one.
   PREREG-1 3.2 freezes a `scale_degenerate` rule with **both readings named**
   and requires the naive verdict reported beside the frozen one at every such
   cell.
2. **The fibre clause moves the undeclared free parameter rather than removing
   it** — from FAMILY to DECLARED ARGUMENT SET. PREREG-1 3.5 says so before the
   run and names it as the place to attack; TASK-20260812-696cd4's primary
   target is exactly there.

## Completion gate

See `dispatch_queue.json`, this task's `handoff.completion_gate` (ten items).

## Binding carries

PREREG-1 sections 11 and 11.1 in full. CLAIM TIER STAYS TOY.
`knowledge/INDEX.md` is not written, regenerated or staged.
