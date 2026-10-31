# EXP-SEMBIN-24ec56 execution notes: lost attempt (2026-10-31)

Executor disclosure, no result. Facts only.

- Runbook session RBS-SEMBIN-24ec56 ran a fifth step attempt from 2026-10-23T21:07Z in a container
  that was later reclaimed. Its journal entries were never committed: the committed
  `journal.jsonl` ends at "attempt 4 started" (commit d00428a6c9).
- That attempt completed four trials whose run directories were committed with final receipts:
  rand-m3-n15 (RUN-SEMBIN-87be3b, output_validated), null-support-m3-n15 (RUN-SEMBIN-886cb7,
  invalid_output), null-dense-m3-n15 (RUN-SEMBIN-8ae959, invalid_output), poly-m3-n13
  (RUN-SEMBIN-8bd3c8, output_validated). Their digests are in their receipts, not in this
  session's journal.
- It then started rand-m3-n13 (RUN-SEMBIN-989e60) at about 2026-10-24T17:35Z. That run directory
  was never committed and was lost with the container. No output of it exists or was read.
- Claim epoch 1 of TASK-20261018-944ddb expired 2026-10-25T18:27Z.
- On 2026-10-31 the user asked to try again. The session is resumed from the committed journal,
  which will label the next step attempt "5"; it is the sixth attempt actually made, so the
  frozen five-interrupted-attempt protection is exceeded by one in fact. rand-m3-n13 has no run
  directory on disk, so the supervisor launches it under its frozen run id RUN-SEMBIN-989e60; the
  lost first launch of that id is recorded here and nowhere else.
