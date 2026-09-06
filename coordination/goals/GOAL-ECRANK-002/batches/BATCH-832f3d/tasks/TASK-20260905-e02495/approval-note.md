# Approval authorship note -- TASK-20260905-e02495 (BATCH-832f3d)

Authored inline by the Coordinator session (opencode coordinator binding
balance-dead; declared fallback; resolved model
fireworks-ai/accounts/fireworks/models/qwen3p8-max; model_verified false)
under the user confirmation recorded verbatim in DEC-20260905-2d466e.

Diff scope of this task (and ONLY this scope):

1. `experiments/EXP-ECRANK-76a70d/specification.yaml` -- three designated gate fields:
   - `status: review_required` -> `status: approved`
   - `approved_by: null` -> `approved_by: coordinator`
   - `approval_note` -> approval record citing DEC-20260905-2d466e, the user answer
     verbatim, the findings engagement (1/2/3/6), the version-1 sha256
     binding (bcff5ced...), and the amendment-only rule; the pre-approval
     null-by-design note preserved verbatim inside the new note.
   Version stays 1. Every protocol field untouched. The ledger task
   re-verifies this diff against the BATCH-ef0456 committed bytes before
   committing.
2. `ledger/handoffs/TASK-20260905-26364a.yaml` -- the executor handoff per design-experiment
   skill step 5, carrying the contract budget envelope (maximum_runs 8;
   per-run wall 7200 s; worst-case 57600 s; memory 8 GB) and the completion
   gate from DEC-20260905-2d466e. Dispatched only by the execution batch opened after the
   approval decision lands on main.
3. This note.

No other file written. No identifier minted beyond those allocated for
this batch. Zero compute spent.
