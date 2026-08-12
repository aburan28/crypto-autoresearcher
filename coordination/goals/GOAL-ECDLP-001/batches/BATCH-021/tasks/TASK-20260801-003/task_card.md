# TASK-20260801-003 — Ledger archive: EV-DS-648 and DEC-20260801-629 for the RUN-DS-001-ctrl-unplanted control

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/dispatch_queue.json`. Where this mirror and the queue disagree, **the queue
governs and the disagreement is a defect to report**, not to resolve by preference.

- **Role:** coordinator
- **Depends on:** TASK-20260801-001, TASK-20260801-002
- **Archived by:** n/a (this IS the archive)
- **Inference policy:** `coordinator-orchestration-code`, fallback_allowed=True, independent_session_required=False

## Objective

Write EV-DS-648 and DEC-20260801-629 from the two independent reviews, update the GOAL-ECDLP-001 checkpoint and next action, and commit all six declared paths IN ONE COMMIT.

## Write scope

- `ledger/evidence/EV-DS-648.yaml`
- `ledger/decisions/DEC-20260801-629.yaml`
- `ledger/goals/GOAL-ECDLP-001.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/archives/TASK-20260801-003`

## Deliverables

- `ledger/evidence/EV-DS-648.yaml`
- `ledger/decisions/DEC-20260801-629.yaml`
- `ledger/goals/GOAL-ECDLP-001.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/archives/TASK-20260801-003/ledger_commit_receipt.json`

## Constraints

1. COMMIT ALL SIX DECLARED PATHS IN ONE COMMIT, RECEIPT INCLUDED, WITH THE RECEIPT'S OWN commit_sha FIELD SET TO null. This is BATCH-020's TASK-20260731-041 convention and it is LOAD-BEARING: CORR-20260731-010 proves that splitting the receipt into a following commit makes the archive PERMANENTLY UNBINDABLE. Do not repeat that error.
2. Check for a stale .git/index.lock before staging and report what you found; never delete one silently.
3. Stage EXACTLY the six declared paths. No extras, no deletions.
4. EV-DS-648 must not assert above its claim tier: toy, one cell, bits=20, unplanted targets, producer-authored instrument.
5. If either review returns INADMISSIBLE or a blocking objection, the decision is inconclusive or revise - NOT support.
6. H-DS-001 may move only if the archived evidence moves it and DEC-20260801-629 says why. H-IC-001 and H-STR-002 stay untouched.
7. Do not claim a closure quorum; none is available and none is needed here.

## Completion gate

- Six declared paths committed in one commit; receipt records commit_sha null, parent_sha, every path sha256 from git object content, and a PASS/FAIL per check; EV/DEC scoped to claim tier toy.
