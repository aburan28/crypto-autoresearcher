# TASK-20260803-007 — Fresh Red Team Review

Act only as the independent Red Team defined by `agents/red-team.md` and the
archived `TASK-20260803-007` handoff. Read the complete handoff and
`red_team_review_protocol.yaml`, then attack the immutable Git objects they
name. Do not trust working-tree substitutions and do not inspect the concurrent
Validator report.

Write exactly one artifact:
`coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-007/red_team_report.yaml`.
Record objections and controls only; do not repair, commit, merge, materialize
a repository candidate, run ECDLP work, or make a Coordinator decision. Use
`CLEAR`, `OBJECT`, or `INCOMPLETE` for `disposition` and `PASS` or `BLOCK` for
`r5_gate`. Keep candidate-tree and ECDLP conclusions outside the review scope.
