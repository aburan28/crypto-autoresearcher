# BATCH-004 rank 3 was resumed AFTER its snapshot, and its bound artifacts now diverge

## What happened

The BATCH-004 producer snapshot (TASK-20260803-9b1482) bound 101 paths by
sha256, including
`tasks/TASK-20260803-367b1b/{RESULTS.json,PREREGISTRATION.md,budget_stamps.jsonl}`.

The independent red team then found that the rank-3 S-box arm **has no decay
control** — the producer's own `checks_that_did_not_run` records the r=6
random-S-box arms as unrun for budget — and named that as structurally the same
defect the BATCH-003 red team found for zero-entry matrices, reproduced inside
the batch convened to repair it. Cost to fix: about 310 s.

I resumed the producer to run it. It is now appending continuation stamps, so
`budget_stamps.jsonl` has already diverged from its archived digest
(`ceaff346…` archived, `9aece197…` in the worktree).

## The archive is NOT broken, and here is why

`research_dispatch.py` verifies an archive against **its commit**, not the
working tree, and it still accepts TASK-20260803-9b1482. This was established
earlier in this campaign when seven BATCH-002 paths diverged and the snapshot
continued to verify — and it is also the point on which I once wrote a FALSE
justification into CORR-20260802-a7146b and had to correct it. The archived
package is exactly what the reviewers read; nothing about it changed.

## What this means for the record, and it is the BATCH-002 rule applied again

**THE r=6 DECAY ARMS ARE SEGMENT-2 AND ARE UNREVIEWED.** The validator and the
red team both read the segment-1 package bound at the snapshot. Whatever the
resumed arms measure:

- carries NO weight in this batch's evidence record;
- supports NO observation in it;
- and is named as measured-but-not-reviewed, exactly as BATCH-002's segment 3
  was, so that a reader can see which conclusions rest on reviewed measurement
  and which do not.

If the r=6 arms KILL the S-BOX-INDEPENDENT conclusion — the red team's
"finding that would hurt most", since a live r=6 would mean the signal is not
round-limited and therefore not a yoyo — then the honest handling is NOT to
quietly fold that into this batch. It is to record the segment-1 conclusion at
the strength its own reviewers gave it, record the segment-2 measurement beside
it as unreviewed, and make the review of segment 2 the next batch's rank 1. A
conclusion overturned by an unreviewed arm is not thereby corrected; it is
thereby QUESTIONED, and the question goes to reviewers.

## Why the arm was run anyway rather than deferred whole

Because it is 310 s and it is the cheapest available falsifier of this batch's
headline. Leaving a published conclusion standing while its falsifier sat unrun
and affordable is the failure this campaign has already recorded against itself
twice — once as the zero-entry decay control that went unfilled for three
batches, and once as the mod-8 null control. Running it and scoping it honestly
is strictly better than not running it.
