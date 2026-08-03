# What the BATCH-002 ledger archive does and does not cover

Written by the Coordinator before the ledger archive runs, because resuming a
producer after its reviewers had been dispatched has a consequence that must
not be silently absorbed.

## The situation

The snapshot archive TASK-20260802-f92a96 bound the producer package at commit
c1ff4665, 134 paths by sha256. Both reviewers reviewed THAT package. Their
verdicts are statements about c1ff4665 and nothing else.

I then resumed TASK-20260802-142a4b a third time to run M1_r5_j0 -- the arm
BOTH reviewers named as decisive for the wording of the D-DERIV-1 correction.
That was the right call on the merits: the alternative was to write a
correction into the ledger while the single measurement that settles its scope
sat unrun and affordable.

The consequence is that seven archived paths now differ in the working tree
from their archived digests. THE ARCHIVE ITSELF IS UNAFFECTED: the dispatcher
verifies an archive against its COMMIT, not against the worktree, and
research_dispatch.py still accepts TASK-20260802-f92a96. Git holds the reviewed
bytes permanently at c1ff4665.

## The rule this forces, and it is not negotiable

SEGMENT 3 IS UNREVIEWED PRODUCER OUTPUT. No reviewer has seen M1_r5_j0. Putting
its result into EV-AES-d33b1c would promote a producer's own unreviewed
measurement into an evidence record, which is exactly what the snapshot →
independent review → ledger sequence exists to prevent, and exactly the kind of
shortcut this campaign has already had to correct itself for twice.

Therefore:

1. EV-AES-d33b1c records ONLY what the reviewers reviewed: segments 1 and 2,
   as bound at c1ff4665.
2. The M1 result is NAMED in DEC-20260802-b226fb as MEASURED BUT NOT REVIEWED,
   with its value stated and its status stated beside it, and it carries NO
   evidence strength and supports NO claim in the evidence record.
3. The round-split D-DERIV-1 correction is written from the REVIEWERS' analysis
   -- the validator's independent verification that fact 2's k=1 class
   contributes a multiple of 2^24, and the red team's constraint-counting
   argument about M0 -- both of which are reviewed material. It is NOT written
   from the M1 measurement, whichever way that measurement came out.
4. Segment 3 carries into BATCH-003 as its opening input, requiring its own
   snapshot archive and its own independent review before any record relies on
   it.

## Why this is recorded rather than just done

A reader comparing the working tree to the snapshot receipt will find seven
mismatches and is entitled to know whether that is drift, tampering, or a
deliberate act. It is deliberate, it is dated after the reviews, and the
reviewed bytes remain addressable at c1ff4665. The alternative -- not resuming
the producer -- would have left the decisive arm unrun to keep a hash table
tidy.
