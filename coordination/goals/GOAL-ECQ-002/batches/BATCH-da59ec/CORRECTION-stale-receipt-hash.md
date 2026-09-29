# CORRECTION: I committed a receipt carrying a STALE hash

Fault: THE ORCHESTRATING SESSION'S. Caught by the archiving role, not by me.
Severity: a content mismatch, which CLAUDE.md makes FATAL to an archive.
Status: repaired before the next commit; the bad state existed at exactly one commit, 27fdafbcc.

## What happened

The sequence was:

  1. I hashed all 12 declared paths and verified them: 0 problems.
  2. I sent DEC-20260823-839fc6 back to its author to repair three rule-9 citations.
  3. The author repaired it — correctly, and without relabelling any source.
  4. I committed the receipt at 27fdafbcc WITHOUT RE-VERIFYING.

Step 4 is the error. The decision's digest in that receipt was computed at step 1 and the file
changed at step 3, so the committed receipt declared

    ledger/decisions/DEC-20260823-839fc6.yaml: 921a1cea58f3...

while the tree held `38c8464409e6...`. Every other declared path was untouched and still matched.

## Why this is serious even though nothing false was published

CLAUDE.md is explicit: "Archive receipts bind to CONTENT first... A content mismatch is still
fatal." The whole point of the hash set is that it is checkable by someone who trusts nobody. A
receipt whose declared digest disagrees with the tree fails that check, and it fails it in the most
dangerous way — it looks verified. A verifier reading 27fdafbcc would have been entitled to
conclude the decision had been swapped after archiving.

Nothing false was actually published: the content that landed is the repaired decision, which
validates clean, and the repair is fully documented. The defect was in the BINDING, not the record.

## Root cause, and the rule that follows

I verified, then did a round trip to another agent, then committed on the strength of a
verification that predated the round trip. Hashes are a snapshot of a moment; any agent turn
between verification and commit invalidates them.

RULE: RE-VERIFY THE FULL HASH SET IMMEDIATELY BEFORE `git commit`, in the same command, with no
agent turn in between. Not before dispatching, not before a message, not "a moment ago".

That is now what happened: the re-verification above ran in the same invocation as the re-hash,
and reports 12 paths / 0 mismatches with `validate_ledger` clean at 7023 records.

## Credit where it is due

The archiving role told me its edit had invalidated my digest, unprompted, in the same message that
delivered the repair. It also corrected its own receipt's `path_count` from 13 to 12 — the 13th was
the receipt itself, which cannot appear in its own mapping — and recorded that correction rather
than silently fixing it, on the grounds that a declared count disagreeing with its own mapping is
something a verifier is entitled to read as a scope discrepancy. Both are exactly right.

It also declined to mark `O-PROOF-ARTIFACT-ORDERING` discharged on its own authority, attributing
the ancestry check to me because it has no shell and did not run it. That attribution is correct
and I accept it: I ran `git merge-base --is-ancestor` for both review commits and both returned
ancestor-of-HEAD.
