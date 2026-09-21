# Final audit: first-power box lattice v2

## Handoff: revised explicit lattice negative

### Claim or task

Verify the repaired split between the explicit-size negative and the
determinant-volume heuristic.

### Status

`GO`, `NEGATIVE RESULT`, `MODEL-BOUND`.

### Assumptions

- Every first-power box shift is explicitly materialized.
- `d_i,X_i=Theta(B)` and `p=Theta(B^5)`.
- `Theta(B^6)` nonzeros applies only to expanded coefficient-dense membership
  polynomials.

### Evidence so far

- `Theta(B^5)` columns and raw generators unconditionally violate the
  `o(B^2.5)` preprocessing gate.
- Dense nonzeros are correctly conditional.
- The determinant/index formula and average source degree `Theta(B)` are intact.
- `p/sqrt(s)` is labeled sufficient, and `p/sqrt(C)` only a conservative screen.
- Determinant volume is explicitly a heuristic prediction, not a shortest-vector
  lower bound.
- Exceptional sparse vectors, syzygies, elimination, implicit representations,
  reduced shifts, and higher powers are consistently outside the negative.

### Failure modes

No remaining scope or logic defect was found. The result rejects only the
explicitly materialized all-shifts family.

### Next concrete action

Preserve this family as `REJECTED_SCOPED`; do not implement or retune it.

### Artifact paths

- `first-power-box-lattice-negative-v1.md`
- `first-power-box-lattice-red-team-v1.md`
- `theory.md`
- `object-dimension-ledger.md`
- `decision.json`
