# Repair note — TASK-111 task_report race at 07232da8

The committed `task_report.md` blob under TASK-20260731-111 in snapshot
`07232da8` incorrectly contains BATCH-026 **IT-amend** prose from a concurrent
author session race. Official BATCH-026 open under DEC-20260731-030 is
**CTRL-RT025-CI-IDENTITY** (see QUEUE-AMEND-015, SCOPE-DECISION, DEC-030).

This note does not rewrite the immutable commit. CI review binds to
`experiments/EXP-DS-001/amendments/v2_ctrl_ci_identity.yaml` and
`experiments/EXP-DS-001/controls/CTRL-RT025-CI-IDENTITY.yaml` at `07232da8`,
not to the raced task_report prose.
