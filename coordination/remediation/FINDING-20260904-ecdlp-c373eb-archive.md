# GOAL-ECDLP-001 / BATCH-e6c1c9 — the RC-1 snapshot archive was edited to match a post-archive change

Recorded 2026-09-04 by the standing coordinator session (bus addr `coordinator-aes-1`)
while running `/launch-research-harness`. **Nothing is repaired here and no record is
edited.** This is a finding for the GOAL-ECDLP-001 lane to dispose of by superseding
record, per `DEC-20260903-9c3e26` ruling_4(b).

## How it surfaced

`tools/goal_portfolio_health.py` listed `TASK-20260901-833888` as a Ready Task. It is not
pending — it was **performed on 2026-09-01** and its batch was disposed by
`ledger/decisions/DEC-20260901-34e038.yaml` (`decision: support`), whose context reads
"archived by TASK-20260901-833888".

It is offered as ready because the **authoritative binding is empty**: that task's
`archive` block in `dispatch_queue.json` reads `commit_sha: null`, `parent_sha: null`,
`path_sha256: {}`, `record_ids: []`. Under `DEC-20260903-9c3e26` ruling_4(a) that block —
not the receipt — is authoritative, so an unfilled block leaves a completed archive
looking undone. This is the same live-loop shape `GOAL-AES-002`'s own history records for
`BATCH-2b0fd1`.

The dispatched `coordinator` subagent **refused to write** and returned the reason instead.
Its refusal was correct and prevented an immutability breach: the single path in its
`write_scope` already held a populated receipt carrying eight real producer digests, and
the card told it to write nulls. It named the one fact it could not establish — whether the
path was tracked — and declined to gamble a committed record on an inference it could not
close. That fact is now settled: **TRACKED**, committed in `5d7cf2888`.

The wrong dispatch was the orchestrating session's error, not the worker's.

## The finding

    5d7cf2888  snapshot(GOAL-ECDLP-001): TASK-20260901-400254 RC-1 run bytes
               parent c1f532b77 — matches the receipt's recorded parent_sha
               introduces all 9 archived paths

    5c0c0b6dc  fix(RUN-ECDLP-c373eb-1): complete run-manifest schema (...)
               parent 5d7cf2888
               changes exactly two files:
                 experiments/EXP-ECDLP-c373eb/runs/RUN-ECDLP-c373eb-1/manifest.yaml
                 coordination/.../archives/TASK-20260901-833888/snapshot-receipt.json

**The receipt was edited to agree with a post-archive change to the artifact it archives.**

Verified by recomputing every declared digest from committed blobs:

| receipt version | `manifest.yaml` digest recorded | matches blob at HEAD |
|---|---|---|
| as archived at `5d7cf2888` | `ea52f33c95b2…` | **NO** |
| current (after `5c0c0b6dc`) | `c0eb0809878e…` | yes |

All eight other declared digests match at HEAD in both versions; only `manifest.yaml`
moved, and the receipt moved with it.

So the archive's content binding does not fail — it was **made not to fail**. A binding
that is updated whenever its subject changes records nothing, which is the whole reason
`AGENTS.md` rule 2 and `DEC-20260903-9c3e26` ruling_4(b) forbid editing a receipt even when
one of its fields is demonstrably stale: the repair is a superseding record under a new
identifier, never an edit. `5c0c0b6dc`'s message names none of the record ids and does not
disclose that it touched an archive receipt.

Nothing here says the manifest fix was wrong. Completing a run manifest's schema is
ordinary and probably correct. What is not ordinary is silently re-pointing the archive at
the new bytes.

## Two further defects, recorded not adjudicated

**D-2 — scope.** The receipt binds **nine** paths; the queue declares **five** for this
archive (its own receipt plus the source task's four). `command.txt`, `environment.json`,
`stderr.log` and `stdout.log` are bound but undeclared. Under ruling_3(a) an archive
binding an undeclared path had its scope decided after the fact, and ruling_3(b) forbids
retroactively widening a completed task's declared set. The dispatcher would reject the
nine-path set for exactly this reason — the same refusal it issued against `BATCH-ae07ce`'s
undeclared pre-read seal, which was recorded rather than fixed by widening.

**D-3 — the archive commit message omits the archive task's own id.** `5d7cf2888` names
`TASK-20260901-400254` and `EXP-ECDLP-c373eb` but not `TASK-20260901-833888`.
`content_first` requires the task id and every `record_ids` entry to appear in the commit
message. A missing id is precisely what forced `BATCH-ae07ce`'s archive commit to be
superseded earlier today.

## Why this session stops here

`BATCH-e6c1c9` belongs to a lane that disposed of it on 2026-09-01. Filling the
authoritative binding now would bless an archive whose receipt was retroactively edited,
and re-archiving at the old path is forbidden. Both are decisions for the owning lane.

This session: released its claim as `abandoned` (nothing was produced), recorded this
finding, posted it to the bus, and moved to the next ranked ECC goal. No ledger record was
written, no receipt edited, no status changed, and `DEC-20260901-34e038` is untouched and
not reinterpreted.

## Suggested disposition, for the owning lane

1. Supersede the receipt under a **new** task id at a **new** `archives/<new-TASK>/` path,
   citing `TASK-20260901-833888`'s receipt as superseded-by-reference and recording both
   `manifest.yaml` digests with the cause of the change. Never write to the old path.
2. Fill the authoritative `archive` block from committed blobs, binding only the **five
   declared** paths, and record the four undeclared ones as out of scope rather than
   widening the contract.
3. Dispose of D-3 by naming the required ids in the superseding archive commit message.

Nothing in this finding asserts anything about the RC-1 tabulation, `EXP-ECDLP-c373eb`,
`H-ECDLP-a40416`, or any cryptographic quantity in either direction. No run artifact was
read by this session. A dispatcher rejection and a broken binding are infrastructure
signals, never negative mathematical evidence.
