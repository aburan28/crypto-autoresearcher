# Loss record: BATCH-c45baf review artifacts destroyed before archiving

**Status: NOT EVIDENCE. NOT A REVIEW.** This is a Coordinator incident record. It
asserts nothing about the batch's science and may not be cited as validation of
anything.

Author: coordinator. Date: 2026-08-03. Batch: BATCH-c45baf.
Reviewed package: snapshot `555a5762`.

## What happened

The execution container was replaced mid-batch and the repository re-cloned at
`24e8e7f8` (BATCH-011 era). The local clone's reflog begins at that commit, so
this was a fresh clone, not a reset. All pushed work was intact on
`origin/claude/mlkem-batch009-validation-retry` at `7678f0b2` and was recovered
by fast-forward; the local branch was verified to be a strict ancestor of origin
first, so nothing unique was discarded.

## What survived

Everything committed:

- BATCH-d2a728, BATCH-f75059 and BATCH-c45baf producer packages
- every snapshot and ledger archive through `7678f0b2`, receipts bound and verified
- `EV-MLKEM-af61e7`, `EV-MLKEM-da9e3b`, `EV-MLKEM-50901f`, their decisions, the
  `GOAL-MLKEM-004` record, and `KN-TECH-14efa5`

The BATCH-c45baf producer package (`TASK-20260803-db170f`, seven artifacts)
survived **because it was committed in the snapshot archive before the reviews
were dispatched**. That ordering is the harness's own rule and it is the reason
this incident cost two reviews rather than the whole batch.

## What was lost, exactly

Working-tree files that were never committed:

| path | owner |
|---|---|
| `tasks/TASK-20260803-3fc363/report.yaml` | batch-3 validator |
| `tasks/TASK-20260803-3fc363/notes.md` | batch-3 validator |
| `tasks/TASK-20260803-d2e23e/report.yaml` | batch-3 red team |
| `tasks/TASK-20260803-d2e23e/notes.md` | batch-3 red team |
| `ledger/evidence/EV-MLKEM-b22280.yaml` | coordinator (unarchived draft) |
| `ledger/decisions/DEC-20260803-ee1cda.yaml` | coordinator (unarchived draft) |

`EV-MLKEM-b22280` and `DEC-20260803-ee1cda` were **never committed and are not
ledger records**. Those identifiers are hereby **retired unused**: they name no
archived record, they are cited by nothing, and they must not be reused. Any
future record covering BATCH-c45baf takes a freshly minted identifier.

## The two review tasks are `queued`, and that is correct

`TASK-20260803-3fc363` and `TASK-20260803-d2e23e` are still `queued` in the
committed dispatch queue, because a review's state advances to `completed` only
in the ledger archive, which never ran. The committed record therefore already
matches reality: these reviews have produced no archived artifact. They are
re-dispatched under their **existing identifiers**. No successors are minted and
no identifier drifts, because nothing was ever archived under them — this is
unlike the BATCH-009 and BATCH-011 session-limit failures, where the failed tasks
had produced `infra_failure_receipt.yaml` files that themselves needed archiving.

## Rule 5

This is an infrastructure failure. It is **not** negative evidence about the
batch, about the row-permutation separation, about the sieve, or about ML-KEM. A
container was replaced; that says nothing mathematical.

## Disclosed contamination risk — read this before weighing the re-run

Both reviews **ran to completion and returned findings** before the loss. The
Coordinator retains those findings in session context. They are **not recorded
here**, and they were **not forwarded** to the re-dispatched reviews, which
receive the original card text unchanged.

This is disclosed rather than hidden because it is a real weakening of
independence and the record should show it:

1. The Coordinator now knows what the first pass concluded, so Coordinator
   framing of any follow-up question is not naive. `DEC-20260803-85adf8`'s
   corrective rule applies with full force — any Coordinator reading that bears
   on a pending review is dispatched as an **interrogative in the card**, never
   as a note supplying both the answer and the verdict.
2. If the re-run reviews reach the same conclusions independently, that is
   genuine corroboration and is stronger than the lost single pass.
3. If they do not, the discrepancy is itself informative, and the Coordinator
   will raise the specific unaddressed question as a **disclosed** objection for
   a further review rather than substituting its own memory for a review.

What the Coordinator will not do is reconstruct the lost reports. They are two
independent agents' work products; authoring them and archiving them as those
agents' output would be fabrication under AGENTS.md rule 9, and remembering
their conclusions does not make the artifacts exist.

## Process change adopted

Reviews are archived when they return, not batched into the ledger commit at the
end. The ledger archive then references already-committed review artifacts
instead of holding them in the working tree across a dispatch window. The
producer package survived this incident precisely because it followed that
pattern; the reviews did not, and were lost.
