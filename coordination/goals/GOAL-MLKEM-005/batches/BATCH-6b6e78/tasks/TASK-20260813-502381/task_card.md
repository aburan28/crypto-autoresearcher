# TASK-20260813-502381 — SNAPSHOT ARCHIVE that NOTARIZES PREREG-2 (runs alone)

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-25cb95
    review_required false
    archive         snapshot, sources TASK-20260813-25cb95
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## Why it runs alone, and before everything

So that `A-1`, its five falsifiers and the four-way termination clause are
**provably prior** to every number this batch produces — by the git record, in
both directions, checkable by a session that trusts nobody here. The
split-producer notarization pattern has worked five times and has been verified
in both directions by independent sessions each time.

## Declared path set — EXACTLY THREE

    archives/TASK-20260813-502381/snapshot-receipt.json
    tasks/TASK-20260813-25cb95/prereg.md
    tasks/TASK-20260813-25cb95/prereg_sha256.txt

The commit changes **exactly** those three and **nothing else**. 0 extra,
0 missing. Compare the change set against the declared set explicitly and record
both counts in the receipt. `dispatch_queue.json` and the seven `task_card.md`
files belong to the **opening** commit and must already be committed or must be
left unstaged.

## CHECK THIS BEFORE YOU DO ANYTHING ELSE

**Is `prereg.md` already in the history at this task's parent?** It exists in the
working tree from batch open, so the opening commit had to leave it **unstaged**.
If it is already committed, the notarization property is destroyed before the
batch began, **this task must not proceed as specified**, and the defect is
reported to the Coordinator rather than papered over. Verify it; do not assume it.

Then: **zero producer artifacts** exist anywhere under
`tasks/TASK-20260813-2ce014` at this commit. Verify that too.

## The receipt pattern is MANDATORY

The receipt body carries `commit_sha: null` and rides **inside** its own commit.
The real sha and parent go into the queue's `archive` block **afterwards**, with
`path_sha256` for all three paths read **from the commit**. Inverting this cost
`BATCH-9e3584` two archives.

## prereg_sha256.txt is YOURS (declared gap G-2)

Compute it. Record the command used in the receipt. **Do not transcribe a hash
from anywhere else and never invent one.**

## Before and after

Fetch `origin/main` and **MERGE** it (never rebase); record the base commit and
the merge outcome in the receipt and in the commit message as
`Base checked: origin/main <sha>`. **RUN THE POST-COMMIT VERIFIER BEFORE THE
PUSH, NOT AFTER** — this goal's most repeated recorded lesson, paid for four
times. Then push and open or refresh the PR naming `BATCH-6b6e78` and `PREREG-2`.

**NO MEASURING TASK MAY BE DISPATCHED UNTIL THIS COMMIT EXISTS AND THE VERIFIER
HAS ACCEPTED IT.** Do not edit `prereg.md`: it is frozen. Stage paths explicitly;
never `git add -A`. `knowledge/INDEX.md` is not written, regenerated or staged.
