# BATCH-20b43f — RC-45 successor admission audit

## Objective

Resolve whether the declared successor to BATCH-046 can execute the frozen
RC-45 package without silently changing its contract or reusing the voided
MOV/direct-solve and empty-ledger controls.

## Bound input

- `GOAL-ECDLP-001`, `RQ-ECDLP-002`, `H-IT-001`, and `EXP-IT-001`.
- `PA-IT-001-v3-rc45-repair-5.yaml` is immutable. Its only frozen Executor
  commands are the `smoke` and `measure` strings.
- BATCH-046 is scoped inconclusive in `EV-IT-008` /
  `DEC-20260803-004`. Validator findings BF-1 through BF-3 and red-team
  objections RT-046-B1 through RT-046-B3 void the transfer interpretation.

## Admission question

The previous decision directs a successor Executor batch under RC-45 to
exercise `CTRL-ANOMALOUS-TRACE1`, a non-empty
`CTRL-NULL-IT-PLANT` edge ledger, and a live null-packaging gate. The frozen
RC-45 text simultaneously limits execution to the existing exact commands and
forbids changing the amendment. This batch does **not** assume that a code
repair can be made under those conditions.

An independent Validator and Red Team must determine whether the currently
frozen implementation and commands can meet all three controls as written.
They must distinguish:

1. an admissible exact-command execution;
2. a repair that requires a new, reviewed protocol amendment; and
3. an infrastructure or provenance issue, which is not mathematical evidence.

## Claim boundary

No ECDLP solve, relation, transfer win, HEUR-ISO-1 result, asymptotic claim,
or hypothesis transition is in scope. The maximum possible result is an
admission determination for a later toy-tier executor run. Pollard rho remains
the relevant generic baseline, and a control-only result carries no
time/memory/data advantage.

## Next checkpoint

The Coordinator will archive the two independent reports with
`EV-IT-6143cd` and `DEC-20260804-d8f8f5`. If either report finds the frozen
package cannot exercise all controls, the sole successor is a newly frozen and
independently reviewed amendment; no executor run is authorized by this
opening.
