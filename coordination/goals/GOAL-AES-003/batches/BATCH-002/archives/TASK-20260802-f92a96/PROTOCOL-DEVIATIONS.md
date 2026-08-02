# BATCH-002 protocol deviations, recorded before the snapshot archive

Written by the Coordinator while preparing TASK-20260802-f92a96. These are
recorded because a deviation nobody wrote down is indistinguishable from one
that did not happen.

## D-1. Coordinator over-subscribed the machine, and it cost rank 1 its trials

Three producers were dispatched concurrently onto a 4-core machine. Load
average reached 12. TASK-20260802-9dcca8's r=6 runs took 253-282 s against
BATCH-001's 69 s for the same work, and five of eight wrong-hint trials
(`WRONG6-03..07`) died on their 1150 s timeout after structure 0 of 2.

`GOAL-AES-003.yaml` states that `max_concurrent: 3` is a cap ACROSS all three
active AES campaigns, not three each, and that if honouring it would require
running degraded, the batch WAITS. That instruction was not honoured. This is a
Coordinator scheduling defect, not a producer defect.

The timeouts are recorded as RESOURCE EXHAUSTION and are excluded from every
distribution. Under AGENTS.md they are never negative mathematical evidence,
and the producer excluded them correctly.

REPAIR: rank 1 was resumed on an idle machine to run the partial-hint arm and
further all-wrong trials sequentially at full thread count. The repair restores
declared scope; it adds none.

## D-2. Wall times taken under contention are not cost measurements

The producer stated this itself and it is endorsed here. No timing measured
during the contended window is offered as a cost. The r=6 dominated finding
(69.39 s against ~25 s exhaustive search over the same hinted residual,
`sota_delta` negative) is carried forward as a BATCH-001 measurement and was NOT
re-measured in this batch.

## D-3. HEAD moved under the producers mid-run

The Coordinator merged origin/main and then untracked the in-flight producer
tree while all three producers were running, so HEAD moved from 41414e80 to
982a2b96 mid-session. TASK-20260802-9dcca8 recorded both SHAs in RESULTS.json,
which is the correct handling. The queue was also re-keyed mid-run when a fourth
ID collision forced DEC-20260802-007 to be reissued as DEC-20260802-9bda5c; that
producer cites both identifiers.

## D-4. A stray file was written outside every declared write scope

`p2.log` appeared in the repository ROOT: 68 bytes reading
`nohup: failed to run command './pair.sh': No such file or directory`. It
carries no research content and was removed rather than archived. It indicates a
producer launched a command from the repository root instead of its own task
directory. No declared artifact is affected, and no other out-of-scope write was
found.

## D-5. WRONG7-01 was killed by the executor's own re-planning

The producer reported killing its driver's `timeout` wrapper during re-planning,
which forwarded SIGTERM to the child and produced 0 bytes. It recorded this as an
executor protocol deviation and relaunched as WRONG7-02, which completed. Recorded
here because the producer disclosed it rather than dropping the run silently.

## D-6. The over-subscription destroyed rank 2+4 entirely. Full cost, stated.

D-1 understated the damage. TASK-20260802-142a4b produced **ZERO measured
numbers**. Every arm it started -- both RANK 4 zero-entry arms and two attempts
at a RANK 2 arm -- was killed at its timeout with no output, while `sq_null`
(rank 1) and `probe` (rank 3) held ~2.7 of 4 cores and load average sat near 13.
Its full-coset passes ran 4-10x slower than BATCH-001's equivalents: BATCH-001's
r=5 arm took 25.66 s; its arms were still running at 725 s CPU when the binding
stop fired.

This is `resource_exhaustion` and it is NOT mathematical evidence in either
direction. Nothing is asserted about the zero-entry mixing layer, and nothing
new is asserted about the null residue distribution. The producer reported this
correctly and did not manufacture a number to fill the gap.

WHAT SURVIVED THE LOSS, and it is not nothing:
  - `cnt.c`, a counting engine with a CONFIGURABLE GF(2^8) mixing matrix. No
    BATCH-001 instrument has this: `count5.c` is AES-NI only and physically
    cannot vary the mixing layer. Pinned bit-exactly against an independent
    Python reference whose S-box is DERIVED from the GF inverse plus the affine
    map rather than copied, on 8 keys at r=4,5,10 for three matrices.
  - `matrices.json`: M0 (one zero entry, det 0x1d, rank 4) and M1 (four zeros,
    det 0x14, rank 4), each with an explicit inverse and M.M^-1 = I verified.
    Both are MDS-SUBSTITUTES, correctly labelled -- a true MDS matrix cannot
    have a zero entry.
  - An ANALYTIC finding, labelled analysis and frozen in the preregistration
    before measuring: working the derivation's algebra with a general
    non-singular M, the no-zero-entry hypothesis appears DISPENSABLE for the
    mod-8 conclusion, and for r=4 only 4 of 16 entries are critical, with which
    4 depending on j0.

THE PRODUCER WAS RIGHT NOT TO CALL THAT A DEFECT IN THE DERIVATION. The card's
trigger was "if the property SURVIVES the zero entry" -- survival was not
observed because nothing was observed. An analytic argument that the hypothesis
is dispensable is a reason to RUN the arm, not a substitute for running it.
Promoting it now would be exactly the fabrication these rules exist to prevent.

REPAIR: rank 2+4 is to be resumed ALONE, after rank 1's resumed segment
finishes, with the frozen parameters in its `params.json` and the successor
order it specified -- M0_r5_j0, then M0_r4_j0_CRIT (exact prediction
547608330240, max occupancy exactly 256, which doubles as the large-non-zero
instrument control BATCH-001 never had), then M0_r4_j1_NONCRIT. Not concurrently
with anything.
