# Direct five-source TT theory review v2

## Handoff: frozen preflight v2 theory audit

### Claim or task

Audit `preflight-v2.md` at SHA256
`b90c09448b740d198b52afbf9743735e0fca12dc51a0011352610fb2fdf49ce1`
and `object-dimension-ledger-v2.md` at SHA256
`92435885c64f912627e7a212712561f907aa84485c0f326d818e245d4b9fe9fa`.

### Status

`GO`, for the paper theory and accounting-consistency layer.

The candidate correctly remains `HYPOTHESIS`, `NOVELTY-UNVERIFIED`, and
`REVIEW_REQUIRED`; this review does not authorize implementation.

### Assumptions

- RCB Algorithm 1 is used exactly in homogeneous projective coordinates with
  `b3=3*b`.
- Every source point and intermediate sum remains in the registered odd-order
  subgroup.
- Dense-core claims apply only to standard dense TT cores.
- Vilmart's normalization bounds are route-specific upper bounds.

### Evidence so far

- Actual per-stage Hadamard bonds, conditional raw allocation, sufficient
  normalizer gates, all five final storage terms, canonical-byte accounting,
  logarithmic-chain costs, Frobenius/final-subtraction traffic, preprocessing
  tiers, support/yield disclosure, and exact `N2,N3` comparator are present.
- The RCB formula's exceptional pairs differ by nontrivial 2-torsion. Closure
  of the odd-order subgroup therefore validates every left-associated call,
  including identities, inverses, doubling, and repetitions.
- Projective equality for `Q=O` is exact: `g_O=-omega*Z`, while `Z=0` on the
  registered cubic forces the unique point `(0:1:0)`.
- Distinct partial sums create disjoint row and column blocks, proving
  `rho_k(Zcal_Q)=m_(k,Q)` over every field.
- `rho_2<=B*rho_1` implies `B*rho_1*rho_2>=rho_2^2`; the symmetric cut-three
  statement is valid. An `Omega(B)` central rank therefore fails the standard
  dense-core gate without becoming a universal circuit lower bound.
- Vilmart supports the stated `O(r*s)` exact reduction and post-sweep leading-
  index bound. The sixth-root rank condition is correctly route-specific.

### Failure modes

- The GO is lost if the curve coordinates or RCB formula change.
- Dense-core theorems cannot reject a separately specified structured or sparse
  representation.
- Vilmart's upper bound cannot be promoted to a lower bound.
- Low final rank cannot be treated as a construction algorithm.
- Intermediate ranks, transcripts, and negative-certificate costs remain open.

### Next concrete action

Retain the implementation prohibition until the complete independent review
bundle approves one exact successor version.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v2.md`
