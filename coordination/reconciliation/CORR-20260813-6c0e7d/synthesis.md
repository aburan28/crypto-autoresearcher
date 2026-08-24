# CORR-20260813-6c0e7d exact premerge resolution

The missing pre-reviewed merge resolution now exists and passed both required
independent reviews. Snapshot `e5e5649da9a411d8f16c90ca9a384e56930931a2`
freezes exactly three producer artifacts plus its self-neutral receipt: a
seven-conflict resolution manifest, a byte-exact neutral GOAL-ECDLP-001 third
body, and the fail-closed zero-run BATCH-0bfcc8 queue.

Validator `TASK-20260813-bc0164` and Red Team `TASK-20260813-a7ddb8` ran in
distinct fresh `review-breakthrough` sessions at `max` effort. Both returned
`PASS` for the same snapshot, source parents, seven conflicts, six immutable
origin/main bodies, neutral candidate, preserved `BUDGET-AMEND-20260812-001`,
and projected ledger validity. Coordinator `TASK-20260813-1a431f` therefore
records `PASS` at this exact static boundary.

This is not an immediate or general merge authorization. The ledger archive
must first be committed, post-commit verified, and terminal-bound as a future
first parent `P`. Only then may a custom certificate admit a two-parent merge
whose ordered parents are exactly `[P,
f07b67416bf2b5fe5a21fd36b66784399e566e71]`, whose merge base is exactly
`b2db8874b4052e25d0bbf3d7969a5f049fe474ca`, and whose seven resolutions equal
the reviewed OIDs and candidate bytes.

The Red Team identified two important traps. First, flipping the postmerge root
task from `blocked` to `queued` is enough for the generic dispatcher to select
it, so a state mutation is not a merge certificate. Second, checking only the
seven final conflict OIDs misses unrelated first-parent drift. The custom
certificate must therefore inspect the complete first-parent range, enforce
the declared repair path set, prove the exact pre-resolution conflict set and
ordered parents, verify all seven final OIDs and candidate equality, and run
baseline-aware ledger validation.

The safe BATCH-080a9c intersection remains `REVISE`, no implementation or
execution authority, zero runs, and no scientific status change. BATCH-1800b3
code remains branch-qualified implementation-only custody; code presence is
not integrated authority. Its adoption or supersession remains a separate
zero-run postmerge adjudication.

No merge, live-goal edit, queue activation, implementation, experiment, run,
ECDLP result, speedup, security claim, closure, or breakthrough is recorded by
this archive.
