# Pre-run theory review v1

## Handoff: coordinate translator correctness and launch gates

### Claim or task

Formalize the finite-orbit Semaev translator, identify sign and identity
exceptions, and decide whether the initial draft was ready for development
execution.

### Status

`RESTRICTED THEOREM` for finite-orbit correctness; `REVISE` and theory
`NO-GO` for the reviewed draft.

### Assumptions

- Nonsingular short-Weierstrass curve over an odd prime field.
- Odd prime-order subgroup, sign-complete factor base, and repeated leaves.
- `D2=F+F` includes identity and is sign complete.
- `M2` is the split squarefree polynomial of nonidentity D2 x-orbits.
- Target is affine; identity target has a separate branch.
- Every accepted source root is covered and no accepted denominator vanishes.

### Evidence so far

- The S4 roots of the proposed gcd are exactly the finite D2 x-orbits `x(A)`
  for which `Q-A` lies in exact `D3=F+D2`, provided source and D2 products are
  implemented exactly and signs are recovered from sign-complete sets.
- An identity-side S4 witness can be rerouted to finite halves for first-witness
  semantics, but a complete candidate API still needs an identity sentinel.
- The draft S3 control was wrong at the identity boundary. The finite product
  omitted `Q=A+O`; the corrected affine polynomial is
  `(V-x(Q))*product_w f3(V,w,x(Q)) mod M2`.
- A concrete `F={+/-G}, Q=2G` fixture makes the uncorrected S3 control miss the
  only finite orbit.
- The full-D3 advice comparison stored both affine orientations independently.
  A fair comparator stores one x-orbit key and one orientation-bound witness,
  deriving the negative witness by toggling adjacent sign-pair indices.
- In the explicit classical product model, the leading root-product work is
  approximately `B*n^2` with `n about B^2`, hence `B^5`; this diagnoses the
  current representation but is not a lower bound on implicit or fast
  resultant circuits.

### Failure modes

- Unsigned interpretation without sign closure.
- Identity omission while claiming exact candidate-set equality.
- First-witness behavior reported as complete orbit enumeration.
- Dense target templates hidden as code rather than advice/workspace.
- x-orbit candidate advice compared with duplicated affine baseline keys.
- Polynomial roots reported without charged signed five-leaf recovery.
- Correctness promoted without relation quality, rank, linear algebra, or
  descent.

### Next concrete action

Add the identity-edge S3 counterexample, implement the corrected S3 factor and
symmetry-compressed D3 comparator, then request a second theory review before
any evidence run.

### Artifact paths

- `contract.md`
- `theory.md`
- `src/polynomial_engine.py`
- `src/exact_floor.py`
- `src/outer_translator.py`
- `tests/test_outer_translator_polynomial.py`
- `tests/test_outer_translator.py`

## Coordinator response

The required repairs were implemented before launch. The corrected identity
fixture, symmetry codec, exact negative-witness recovery, and reduced full-stack
smoke now pass. This v1 review remains immutable; readiness is decided only by a
separate v2 review.
