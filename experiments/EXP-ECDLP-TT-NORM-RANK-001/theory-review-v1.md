# Theory review of v1

## Handoff: mathematical audit

### Claim or task

Audit the Frobenius repair, multidegrees, Hilbert caps, source coefficients,
projective scaling, and power-frontier statements in the exact v1 bundle.

### Status

`REVISE` with one wording blocker. The first-norm theorem passed.

### Assumptions

- The review covers the frozen left-associated RCB circuit and registered
  `F_p` points only.
- Rank statements are upper bounds, not attained ranks.

### Evidence so far

- The degree-preserving conjugate, multidegrees `(16,16,8,4,2)` and
  `(32,32,16,8,4)`, Hilbert caps `(96,9216,288,12)`, six source coefficients,
  identity-target formula, trace-zero bases, and projective scaling passed.
- The bound `(192,36864,1152,24)` for `h^2` passed.
- The v1 `j_star` formula is valid only for pure squaring states. A mixed
  addition-chain accumulator with exponent `e_s` must instead use
  `rho2<=min(B^2,9216*e_s^2)` and loses a strict sub-`B` certificate when
  `e_s>=ceil(sqrt(B/9216))`.
- A `j_star-1,j_star` bracket is defined only when `j_star>0`.

### Failure modes

- Calling a pure-squaring diagnostic chain-wide.
- Ignoring a mixed accumulator that crosses the Hilbert threshold earlier.

### Next concrete action

Repair the terminology in `theory-v2.md`, `contract-v2.md`, and
`specification-v2.json`, preserving v1.

### Artifact paths

- `theory-v1.md`
- `theory-v2.md`
- `contract-v2.md`

