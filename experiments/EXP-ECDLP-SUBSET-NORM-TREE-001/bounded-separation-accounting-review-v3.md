# Bounded-separation accounting review v3

## Handoff: final root-path accounting

### Claim or task

Audit explicit term events, one-child first-witness descent, cumulative path
cost, identity scans, and terminal witness recovery.

### Status

`GO`, accounting layer only. The candidate remains `REVISE`,
`REVIEW_REQUIRED`.

### Assumptions

- Parent and child norms lie in the field `K` and satisfy `R_I=R_L*R_R`.
- Formal and active term counts are distinct.
- No termwise linear consumer is assumed to compute the nonlinear norm.

### Evidence so far

- Streaming can reduce live state but not an `Omega(L_active)` term stream.
- A balanced chosen child retains the `Omega(n)` formal endpoint count when one
  base rank is at least two; quotient work inherits it only after nonvanishing
  is proved.
- First-witness descent charges one child decision per known-zero parent.
- Work and traffic are summed over the whole path, and `S_peak` includes
  retained ancestor and certificate state.
- The root-only `o_2` scan and the `Theta(B)` terminal signed-witness scan are
  charged separately and fit below the B2 boundary.

### Failure modes

Compact selectors, exact nonlinear contraction, quotient-level active ranks,
and decision certificates remain uninstantiated. A small logical output or
small streaming state is not a complexity result.

### Next concrete action

Apply the same ledger to the exact TT zero-locator candidate, including every
normalization, Hadamard rank, and source-index recovery step.

### Artifact paths

- `bounded-separation-preflight-v3.md`
- `object-dimension-ledger.md`

