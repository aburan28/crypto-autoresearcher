# Pre-implementation theory review v2

## Handoff: repaired generalized-root correctness

### Claim or task

Re-review the exact five-leaf circuit after v1 repairs.

### Status

`RESTRICTED THEOREM`: `GO` for the correctness layer only.

Operator and solver feasibility remains `REVIEW_REQUIRED`. No implementation or
execution is authorized.

### Assumptions

- `p>3`, the short-Weierstrass curve is nonsingular, and registered points lie
  in the stated odd-prime-order group.
- `Reg` and each squarefree `M_b` exactly represent accepted non-pole sources,
  orientations, and identifiers.
- Branch enumeration is frozen and source lifts are unique.

### Evidence so far

- The five typed addition cases exactly cover the group law; odd order excludes
  the finite `y=0` overlap.
- Four gates compute the exact ordered five-point sum, including repetition and
  identity intermediates.
- Equality of public-id projections is exact and does not assert a false
  coordinate-solution bijection.
- Registry rejection, duplicates, aliases, candidate completeness, and attempt
  accounting are explicit.

### Failure modes

No mathematical defect remains in the correctness layer. The theorem does not
provide a bounded-root inequality, completion bound, or favorable complexity.

### Next concrete action

Independently audit the frozen first-power lattice negative and derive a
mathematically distinct root operator. Do not implement.

### Artifact paths

- `theory.md`
- `contract.md`
- `first-power-box-lattice-negative-v1.md`
