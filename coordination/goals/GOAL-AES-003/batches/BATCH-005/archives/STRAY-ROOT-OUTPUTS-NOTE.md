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

A DOUBLED PATH.

**MY FIRST DIAGNOSIS OF THIS WAS WRONG, AND THE BUG RECURRED BECAUSE OF IT.** I
wrote that an `echo >> .gitignore` had run while the shell's working directory
was a task subdirectory, so a relative path was appended onto a prefix already
present. That story was plausible and false, and I did not test it.

THE ACTUAL CAUSE: my own repair script rewrote `.gitignore` with
`"\n".join(lines)`, which DROPS THE TRAILING NEWLINE. The next `>>` append then
concatenated its first line directly onto the file's last line. So the repair
that removed the doubled paths was itself what recreated the condition for the
next one — and an hour later a second doubled path appeared by exactly the same
route, on a rule that then silently matched nothing.

Fixed properly: every rewrite now ends with `.rstrip("\n") + "\n"`, and the
result is checked with `git check-ignore -v` AND by asserting the file ends in a
newline.

The lesson is not about newlines. It is that I diagnosed a silent failure from a
plausible story instead of from the file, which is the same act as the six
recorded claims about the corpus that turned out to be wrong -- and here it cost
a recurrence, because a wrong diagnosis leaves the real cause in place.

This is the same class as the regex that corrupted a checkpoint field
(CORR-20260803-f459b3) and the inlined commit message that substituted itself
(BATCH-006 snapshot): **a write whose result was never read back**. A `.gitignore`
line that matches nothing fails silently and looks identical to one that works.

Repaired by truncating every doubled path to its last `coordination/goals/`
occurrence, and verified with `git check-ignore -v` rather than by assuming.
