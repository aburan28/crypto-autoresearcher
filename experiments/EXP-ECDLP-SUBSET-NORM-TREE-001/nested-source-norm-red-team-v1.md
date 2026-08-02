# Nested source-norm red-team v1

## Handoff: dense and black-box interface audit

### Claim or task

Audit the scoped negatives and determine whether scalar-only transposed norm
evaluation remains open.

### Status

`REVISE`, not `INVALID`. The explicit-interface negatives survive; six scope and
identity repairs were required and have been applied to the primary preflight.

### Assumptions

- `d_i=Theta(B)` and `n_I=Theta(B^2)` only in the balanced collision-light
  specialization.
- Dense counts are allocated power-basis or Sylvester slots, not guaranteed
  nonzero support.
- Scalar-only means no materialized `A_12`, `A_123`, component mask, or
  equivalent target vector.

### Evidence so far

- Materialized `G_(I,Q)` allocates `Theta(B^3)` source-tensor coordinates.
- A sequential dense resultant that emits its penultimate quotient result
  allocates `Theta(B^2)` `A_12` slots.
- Direct ordered-triple evaluation touches `Theta(B^3)` tuples.
- Standard determinant/Krylov vectors over `A_123`, or length-`Theta(B)` vectors
  over `A_12`, expose `Theta(B^3)` scalar coordinates.
- Determinant-defined resultants remain exact over the product rings;
  division-based accelerations owe global unit proofs.

### Required revisions applied

- The D2-identity sentinel is now root-only; finite children use `R_I(Q)=0`.
- Dense and Sylvester counts are labeled allocated/worst-case interface counts.
- The two-source penultimate module is claimed only for sequential elimination
  that explicitly emits it.
- Compact selectors and complete projective formulas remain open; branch-local
  denominators require a charged global unit or fraction-free execution.
- A scalar parent circuit may expose both child scalars internally, so child
  recomputation is not claimed universally.
- Ambient tensor dimension is not treated as a lower bound: a separable tensor
  is an explicit counterexample to such wording.

### Failure modes

Do not promote the result into a lower bound on simultaneous or reordered
elimination, scalar transposition, structured tensor contraction, compact branch
selection, or parent circuits retaining child scalars.

### Next concrete action

Independently re-read the repaired primary note, then define every vector space
and oracle boundary of a scalar-only transposed norm candidate.

### Artifact paths

- `nested-source-norm-preflight-v1.md`
- `candidate-review-v1.md`
