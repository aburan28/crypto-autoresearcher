# BATCH-a39862 merge-certificate verifier disposition

The verifier snapshot is durable and useful, but it is not approved.

Snapshot `cc290b7e93d01c053af6b72d1106db04e7260539` preserves the
read-only pre/post verifier, 15 focused tests, and the Executor report. The
focused suite passes 15/15, existing merge-hygiene tests pass 9/9, and the real
frozen input passes with five first-parent commits, fifteen exact allowed paths,
and exactly six add/add plus one content conflict.

Fresh independent Validator `TASK-20260814-0d61a6` and Red Team
`TASK-20260814-b44436`, both at `review-breakthrough`/`max`, return `REVISE`.
Both reproduce a complete post-mode `PASS` from caller-authored JSON that merely
claims the validator command, exit code zero, and zero new violations even when
the validator does not exist and never ran. The Validator also demonstrates a
first-parent file `shape` versus second-parent `shape/leaf.txt`: Git reports an
eighth directory/file conflict, while the flattened structural detector reports
only seven and returns `PASS`.

These are certificate-integrity failures, not mathematical or scientific
results. Coordinator `TASK-20260814-9bc151` records `REVISE`; the merge, live
goal, and `BATCH-0bfcc8` remain blocked. Snapshot custody and the specific
passing tests remain valid, but they do not overcome reproduced false accepts.

The next bounded action is one additive zero-run Executor repair: remove
unauthenticated caller-supplied ledger success, execute and bind the validator
inside the exact clean inspected checkout, use or conservatively cover actual
Git conflict semantics including directory/file conflicts, sanitize inherited
Git object/index/worktree/alternate/replacement state, and add the exact
reproductions as regression tests. The repair requires a new snapshot and fresh
independent max-effort Validator and Red Team PASS verdicts.

No merge, live-goal edit, queue activation, experiment, ECDLP result, speedup,
security claim, scientific transition, closure, or breakthrough occurred.
