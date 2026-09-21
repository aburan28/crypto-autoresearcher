# Theory Review V2

## Handoff: V2 implementation-readiness review

### Status

`HYPOTHESIS`: `REVISE`. Execution remains zero-run and unauthorized.

### Evidence so far

V2 materially closed the v1 blockers. The EC formulas, canonical encodings,
common/compiler-specific universes, exact optimizer objective, fresh state,
finite rank, chart replication, joint mechanism gate, controls, and separated
accounting are coherent.

### Exact blockers

1. Conflict density `2E/(V*(V-1))` was undefined for `V<2`.
2. Overlapping outcome predicates had no exact precedence.

### Next concrete action

Add an eligible-vertex nonvacuity gate and one ordered, mutually exclusive
decision tree before repeating review.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/contract.md`
- `experiments/EXP-SGCP-SECANT-REP-001/specification.json`
