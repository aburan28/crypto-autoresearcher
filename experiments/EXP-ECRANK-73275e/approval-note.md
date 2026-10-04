# Approval authorship note -- TASK-20260907-467315 (BATCH-a2bf8b)

Authored inline by the Coordinator session (native Cursor cloud-agent
binding; resolved model cursor-grok-4.6; model_verified false) under
AGENTS.md standing user authorization of 2026-09-06 ('all is approved.
ideas/experiments should be always approved'), recorded in
DEC-20260907-12086e.

Diff scope of this task (and ONLY this scope):

1. `experiments/EXP-ECRANK-73275e/specification.yaml` -- three designated
   gate fields:
   - `status: review_required` -> `status: approved`
   - `approved_by: null` -> `approved_by: coordinator`
   - `approval_note` -> approval record citing DEC-20260907-12086e and
     the standing authorization; the pre-approval note preserved
     verbatim inside the new note.
   Version stays 1. Every protocol field untouched.
2. `ledger/handoffs/TASK-20260907-2a3331.yaml` -- the executor handoff
   carrying the contract budget envelope (maximum_runs 8; per-run wall
   7200 s; worst-case 57600 s; memory 8 GB; counted-ops cap 1.0e8 exact)
   and the completion gate from DEC-20260907-12086e.
3. This note.

No protocol field was edited. No identifier was minted beyond those
allocated for this batch. Zero experiment compute in this authorship
task. H-ECRANK-36d8d7 stays specified. C1 stays OPEN and UNPROMOTED.
IMP-2 is untouched.
