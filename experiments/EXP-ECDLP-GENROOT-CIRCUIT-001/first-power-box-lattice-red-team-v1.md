# Independent audit: first-power box lattice v1

## Handoff: explicit lattice negative

### Claim or task

Independently recompute the dimensions, determinant, modular norm screen, and
scope of `first-power-box-lattice-negative-v1.md`.

### Status

`NEGATIVE RESULT`, `MODEL-BOUND`, `GO` after revision.

The explicit-size negative is valid. The determinant argument is a heuristic
screen and must not be stated as a theorem excluding useful short vectors.

### Assumptions

- `d_i,X_i=Theta(B)`, `p=Theta(B^5)`, and all five-dimensional first-power box
  shifts are instantiated.
- Non-source variables have unrestricted `Theta(p)` bounds.
- The `Theta(B^6)` nonzero count assumes expanded coefficient-dense membership
  polynomials.

### Evidence so far

- `A_0=product_i d_i=Theta(B^5)`; a constant union of translated supports has
  `C=Theta(B^5)` columns and `Theta(B^5)` raw generators.
- With dense expanded membership equations, `Theta(B^5)` shifted rows each have
  `Theta(B)` coefficients, giving `Theta(B^6)` nonzeros. Sparse or implicit
  storage changes this count but defines a different representation.
- If shifted equation rows have rank `r` modulo `p`, the unscaled lattice index
  is `p^(C-r)`. Exact column scaling multiplies the determinant by the product
  of the column weights.
- The all-shifts box has average source degree `Theta(B)`.
- For an `s`-term returned polynomial, scaled norm below `p/sqrt(s)` is a
  sufficient modular-to-integer vanishing criterion. Using `p/sqrt(C)` is a
  conservative sufficient screen, not a necessary condition.
- The determinant geometric mean lies far above that sufficient screen even at
  `r=C` and with no surviving full-field degree. This supplies no positive
  recovery prediction but does not lower-bound the shortest vector.
- Materializing `Theta(B^5)` columns or generators already violates the required
  `o(B^2.5)` preprocessing path independently of the recovery heuristic.

### Failure modes

- Exceptional sparse vectors, syzygies, or combinations eliminating every
  full-field variable may evade the determinant-volume prediction.
- Higher powers, reduced shift subsets, support-adapted columns, implicit lattice
  operations, or elimination-first solvers are outside this negative.
- Sparse/product-circuit storage invalidates the dense nonzero count, though not
  the explicit all-shifts column count.

### Next concrete action

Do not implement this shift family. Derive a genuinely different implicit or
composition-tower operator and give it a fresh object-dimension ledger.

### Artifact paths

- `first-power-box-lattice-negative-v1.md`
- `object-dimension-ledger.md`
- `decision.json`
