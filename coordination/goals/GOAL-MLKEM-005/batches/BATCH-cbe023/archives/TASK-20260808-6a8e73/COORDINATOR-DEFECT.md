# Coordinator defect: the ledger archive commit message omits two record ids

Recorded 2026-08-08 by the harness-driving session, immediately on detection.

## What is wrong

`tools/research_dispatch.py` refuses the BATCH-cbe023 plan:

```
dispatch error: archive task TASK-20260808-6a8e73 commit message is missing IDs
['EV-MLKEM-9b8f7f', 'DEC-20260808-05b684']
```

The archive declares four `record_ids`. The commit message for `b33158fc8`
names `KN-FIND-f38a89` and `GOAL-MLKEM-005` in prose, but never writes
`EV-MLKEM-9b8f7f` or `DEC-20260808-05b684` literally. The rule is mechanical:
every declared record id must appear verbatim in the archive commit's message.

## Why it was not fixed

**The commit is pushed.** `ea4bd9185` carries it to `origin`. Amending it would
rewrite history over a commit containing run records and ledger records, which
AGENTS.md and CLAUDE.md forbid. The identical defect occurred on
`GOAL-MLKEM-005 BATCH-a44d08` earlier in this same session and *was* repaired by
amendment — because it was caught **before** the push. That is the whole
difference between the two cases.

Two alternative repairs were considered and rejected:

- **Reduce the declared `record_ids` to the two that appear.** This would
  misreport the archive: the evidence and decision records are genuinely part of
  it, and both are in the commit.
- **A follow-up commit naming the ids.** The check reads the archive commit's own
  message, so a later commit does not satisfy it and would only add noise.

## What is not compromised

- All 14 files are committed and the receipt binds every one by sha256.
- `check_merge_hygiene.py` passes.
- `validate_ledger.py` introduces **zero** new errors from this batch's records;
  the 6 that differ from `main` are pre-existing on this branch.
- The evidence, decision, finding and goal records are intact, parse, and are
  reachable. Nothing about the research content is affected.

What fails is a check on how the commit **message** was written.

## The actual lesson, stated so it is usable

**Run the dispatcher's post-commit verification BEFORE `git push`, not after.**

Three archive defects occurred in this session and all three are the same shape —
a rule that is checkable mechanically, checked too late:

| batch | defect | caught | outcome |
| --- | --- | --- | --- |
| BATCH-a44d08 | commit message missing `GOAL-MLKEM-005` | before push | amended, clean |
| BATCH-a68f79 (MCE) | artifacts committed one commit early | after push | unrepairable, recorded |
| BATCH-cbe023 | commit message missing two record ids | after push | unrepairable, recorded |

The verification step is cheap and takes seconds. The cost of running it late is
an archive that can never be made to verify, because the only repair is a
history rewrite that is itself prohibited.

This is also, precisely, why `GOAL-ECDLP-001` has two dead queues: not because
anything is corrupt, but because a mechanical check was satisfied too late to
matter and the repair window had closed.

## Status of the batch

BATCH-cbe023's nine tasks are all terminal and its research content is complete
and archived. The plan will not render for the archive task, so any successor
batch must be opened directly rather than through this batch's plan. The
decision `DEC-20260808-05b684` and its single `next_action` stand and are
unaffected.
