# Candidate review v3: exact zero-locator frontier

## Handoff: ranking after the coordinate-moment barrier

### Claim or task

Choose the next paper mechanism after explicit bounded separation, linear
moments, and trace-resolvent recurrence reached their scoped boundaries.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`, paper-only. No implementation or execution is
authorized.

### Assumptions

- Ordinary generated prime-field curves and fully charged fixed preprocessing.
- `B approximately n_group^(1/5)`, D2 degree `Theta(B^2)`, and three source
  modes of size `Theta(B)`.
- Target work, traffic, and peak state are strict `o(B^2)`; fixed advice and
  preprocessing workspace are strict `o(B^3)`.
- Exact output is five signed public identifiers, not only a scalar predicate.

### Evidence so far

The bounded-separation cycle produced four scoped boundaries:

- the actual translated coordinate has `n+1` independent linear moment
  directions in the complete split algebra;
- explicit canonical CP/Horner streams reach `Omega(n)` under their stated
  active-count conditions;
- a rank-one symbolic EC coordinate is excluded by nonvertical addition-fiber
  divisors, though finite quotient collapse remains open;
- the explicit reduced trace recurrence recreates a degree-Theta(B3)
  translated-support polynomial.

The cycle also corrected descent: one child evaluation is sufficient at a
known-zero parent. More importantly, current literature supplies an exact TT
normal form over arbitrary fields with zero-tensor testing and leading-index
recovery.

For a finite-branch tensor `G_Q`, the componentwise field indicator

```text
Z_Q=1-G_Q^(|K|-1)
```

is one exactly where `G_Q` is zero. An exact leading nonzero TT index would
therefore locate the registered three-source tuple directly. A D2 witness
lookup supplies the remaining two leaves, so subset descent is unnecessary on
this route. This is a repository synthesis, not a published EC algorithm.

### Ranked successors

1. **Exact TT zero locator with a compiled `G_Q`.** Build `G_Q` without a B2
   coefficient/term stream, apply the Fermat indicator through exact Hadamard
   products and arbitrary-field TT normalization, then recover a leading
   source index. Required thresholds for uniform rank `r` are at least
   `O(B*r^2)=o(B^2)` state and `O(B*r^3)=o(B^2)` work per normalization before
   circuit length and logarithms. Fatal obstruction: no compact `G_Q` builder
   or EC rank bound is known.
2. **Composition-tower fiber compiler.** Choose or derive node polynomials whose
   fixed evaluation circuit has sublinear depth/size and stays low-rank after
   every quotient reduction. Feed its output to the exact TT locator. Fatal
   obstruction: ordinary D2 root polynomials may be indecomposable or the TT
   ranks may saturate.
3. **Batched target translation update.** Maintain normalized TT or scalar
   locator state across a preregistered target progression. Fatal obstruction:
   target translation may require rebuilding `G_Q`, and fixed-polynomial
   evaluation data structures do not remove the B3 product-algebra query size.

### Go/no-go boundary

A TT successor may continue only after a paper ledger gives:

- an exact complete branch or selector construction;
- a division-free `G_Q` circuit with every fixed and target-dependent gate;
- exact TT ranks and core sizes after every multiplication, addition,
  reduction, and normalization;
- total indicator-chain work and traffic, including `O(log |K|)` Hadamard
  operations;
- a proof that leading TT index maps to three signed source identifiers;
- the root-only D2 identity route and exact D2 pair-witness lookup;
- positive and negative certificates under independent replay.

Stop before source code if any target path reaches `Omega(B^2)` work or traffic,
peak state reaches `Omega(B^2)`, advice/workspace reaches `Omega(B^3)`, or the
`G_Q` construction remains an oracle.

### Failure modes

- Treating exact TT normalization as a theorem that EC ranks are small.
- Computing the indicator while omitting the cost of `G_Q`.
- Using approximate SVD rounding for a zero predicate.
- Confusing zero-tensor detection with zero-entry location without the Fermat
  indicator.
- Hiding a full tensor, pair polynomial, target table, or coefficient stream in
  preprocessing.
- Returning a tensor index without registered source IDs and a D2 pair witness.

### Next concrete action

Write the zero-run exact-TT-indicator preflight with a complete `G_Q` circuit
and rank recurrence; stop on paper if construction length or normalized ranks
cannot satisfy the strict gates.

### Artifact paths

- `bounded-separation-preflight-v3.md`
- `bounded-separation-literature-review-v1.md`
- `decision-v3.json`
- `object-dimension-ledger.md`
