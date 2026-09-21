# Red-Team Review: Source Pair-Sum Orbit-Multiplicity Selector

## Handoff: Orbit-multiplicity replication

### Claim or task
Test whether source pair-sum negation-orbit multiplicity predicts typed
five-term relation support on two fresh ordinary curves.

### Status
NEGATIVE RESULT

### Assumptions
- Only public source pair sums are used to rank suffix columns.
- The strict gate requires exact projected support, exact held-out coverage,
  valid witnesses, and full quotient rank at a strict sub-full budget.
- Full replay and rho are correctness controls, not a cryptographic attack.
- Two curves falsify this fixed selector, not all compositional source
  operators.

### Evidence so far
- No accepted strict sub-full budget on either fresh curve.
- Full replay, witnesses, independent selector regeneration, and rho
  certificates pass.
- Partial support and held-out signals occur in rank-deficient rows, preserving
  the need for the quotient-rank gate.
- Pair-sum construction costs are explicitly recorded.

### Failure modes
- The invariant compresses source-state multiplicity but does not encode the
  target-compatible recursive transition needed for rank preservation.
- The experiment remains toy-scale and uses the existing row-space locator.
- Sparse linear algebra, individual descent, and asymptotic scaling are not
  improved by this selector.

### Next concrete action
Stop scalar suffix re-ranking and implement a source-derived recursive-state
operator or circuit-contracted row-space basis, with exact witness lift and the
same fresh two-curve held-out/rank/rho gates.

### Artifact paths
- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001/contract.md`
- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001/runs/RUN-TT-SOURCE-ORBIT-001/`
- `experiments/EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001/runs/RUN-TT-SOURCE-ORBIT-002/`

