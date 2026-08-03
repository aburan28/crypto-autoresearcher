# Two stray root-level files, and a corrupted .gitignore line

## The strays

`val_r6_M0.json` (0 bytes) and `val_r6_M0.err` (65 bytes) sat at the repository
ROOT, outside any task's write scope. Their entire content is:

    nohup: failed to run command './scan': No such file or directory

A launch that never started. The JSON is empty because no run produced anything.
They were first reported by a BATCH-005 producer, which correctly noted they
predated its task and that it had not created them.

**Disposition: gitignored, not deleted.** They carry no measurement, so nothing
is lost either way, but deleting a file because it is inconvenient is a habit
this campaign should not acquire — and the one fact they do carry, that a
reviewer's launch failed before producing data, is preserved verbatim above.

## The corrupted .gitignore line

Line 143 read:

    coordination/goals/.../BATCH-006/tasks/TASK-20260803-b8e91c/coordination/goals/.../TASK-20260803-0764fc/yoyo_sbox_v2

A DOUBLED PATH. An `echo >> .gitignore` ran while the shell's working directory
was a task subdirectory, so the relative path was appended onto a prefix that
was already there. The rule therefore matched nothing, and the compiled binary it
was meant to exclude stayed untracked and kept appearing in `git status` — which
is how it was noticed.

This is the same class as the regex that corrupted a checkpoint field
(CORR-20260803-f459b3) and the inlined commit message that substituted itself
(BATCH-006 snapshot): **a write whose result was never read back**. A `.gitignore`
line that matches nothing fails silently and looks identical to one that works.

Repaired by truncating every doubled path to its last `coordination/goals/`
occurrence, and verified with `git check-ignore -v` rather than by assuming.
