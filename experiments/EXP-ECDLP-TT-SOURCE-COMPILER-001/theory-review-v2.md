# Theory review v2

## Handoff: source-TT compiler v2 theory re-review

### Claim or task

Determine whether v2 repairs the coefficient formula, exact normalizer,
scalar/zero semantics, schedule counts, controls, and finite-instance claim.

### Status

`GO` for the mathematical and protocol-consistency layer. This does not
authorize implementation or execution; accounting, red-team, execution-matrix,
clean-commit, and hash-freeze gates remain pending.

### Assumptions

- Arithmetic and rank decisions are exact over `F_p`.
- The inherited manifest, circuit, order, and tree remain unchanged.
- Verifier enumeration remains isolated from producer preprocessing.

### Evidence so far

- `c3=X_Q^2+nY_Q^2` is correct, gives `h_O=nZ2`, and has a dedicated mutation.
- Left-to-right prefix compression followed by right-to-left suffix
  compression supports the exact unfolding-rank claim.
- Nonzero scalar rank preservation and tagged-zero semantics are consistent.
- One RCB call has 12 Hadamards, five curve-scalar gates, 17 additions, and six
  subtractions; `b3` formation is separately charged.
- The census is consistent: six source cells, nine emitted tensors per cell,
  five retained tensors, 18 trace-zero target TTs, six general-trace controls,
  24 total target TTs, and 13 mutations.
- The direct-sum, zero, identity, planted, asymmetric, and nonzero-trace
  controls cover the repaired theorem boundaries.
- Passing remains a finite-instance constructive result only; resource refusal
  narrows only the literal streamed gate schedule.

### Failure modes

- Incorrect reshape order, factor absorption, transfer propagation, or zero
  handling can still break an implementation.
- Final ranks cannot excuse omitted raw, prefix, or two-sweep costs.
- Toy completion cannot be widened to the Fermat locator or an ECDLP result.

### Next concrete action

Derive and review the execution matrix with per-gate operation, traffic,
allocation, and stopping ceilings before producer implementation.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/theory-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/specification.json`
