# Root operator theory review v1

## Handoff: exact root-only verification

### Claim or task

Verify the oriented translation factors, exceptional branches, resultant/norm
identity, companion displacement, and scoped `N2` boundary claim.

### Status

`RESTRICTED THEOREM`: `GO`.

`NEGATIVE RESULT`, `MODEL-BOUND`: `GO` for the empty-generator companion-
displacement and direct explicit-approximant interfaces only. Broader implicit
norm routes remain `REVIEW_REQUIRED`.

### Assumptions

- `p>3`, the curve is nonsingular of odd prime order, and `N2>=1` for the
  companion statement.
- Conjugation fixes `Z` and acts coefficientwise.
- "N2 boundary data" refers to explicit reconstruction through the frozen
  commutator interface, not information entropy of the target family.

### Evidence so far

- Frobenius conjugation recovers `(x,y)` from `x+omega*y`, proving oriented
  injectivity.
- The ordinary `Q-S` numerator signs and denominator powers are exact.
- `S=Q` is omitted as identity, `S=-Q` is replaced by the `2Q` factor, `Q=O`
  conjugates `P_3`, and identity sentinels remain external.
- `c_Q` is monic with degree `N3-epsilon_+(Q)` and distinct finite roots.
- Multiplication by `r_Q=c_Q mod M` has determinant `Res(M,c_Q)` with the stated
  sign in the product-over-translated-roots formula.
- `T_Q=r_Q(J)` commutes with `J`. Since `J` is cyclic,
  `Cent(J)=K[J]` has dimension `N2`, and `T -> T*e_0` identifies its power-basis
  remainder coefficients.
- Squarefreeness supports the root semantics but is not needed for the
  centralizer lemma.

### Failure modes

Rank zero does not imply `N2` information entropy. Target-parametric matrices,
sparse circuits, nested resultants, nonlinear transposition, batching, and
source-recursive descriptions remain outside the negative.

### Next concrete action

Reject only the frozen explicit interfaces and formalize a fresh implicit scalar
norm or nested source-level resultant interface before any child construction.

### Artifact paths

- `root-operator-preflight-v1.md`
- `theory.md`
- `contract.md`
- `object-dimension-ledger.md`
