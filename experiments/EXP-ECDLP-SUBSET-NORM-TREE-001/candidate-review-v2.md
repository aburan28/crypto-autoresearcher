# Candidate review v2: scalar contraction frontier

## Handoff: ranking after the source-norm preflight

### Claim or task

Update the successor ranking after the exact nested source norm and its explicit
interfaces were independently reviewed.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`, paper-only. No implementation or execution is
authorized.

### Assumptions

- Ordinary generated prime-field curves and fully charged fixed preprocessing.
- `B approximately n^(1/5)` with strict `o(B^2)` target work and state for the
  compressed root operator.
- Five signed public identifiers and exact child predicates are mandatory.

### Evidence so far

The source-level norm gives an exact scalar root predicate and exact finite-child
factorization. It closes three more implementation families without closing the
mathematical frontier:

- dense sequential resultants expose a B2 target output;
- direct source triples process B3 tuples;
- standard product-basis determinant/Krylov routes carry B3 vector coordinates.

The scalar-only route remains open because ambient tensor dimension is not a
circuit lower bound. The literature supplies no matching algorithm, but points
to one concrete structural condition: bounded tensor separation or an equally
compact recurrence for the complete EC membership element.

### Ranked successors

1. **Bounded-separation scalar contraction.** Derive a complete-projective form
   `G=sum_(ell<=r) a_ell(T1)b_ell(T2)c_ell(T3)` and a BFSS-style norm contraction.
   The required rank, moments, selectors, child substitutions, and target work
   must all be `o(B^2)`. Likely failure: evaluating degree-N2 node membership
   makes separation rank grow to N2 or worse.
2. **Composition-tower fiber norm.** Replace degree-B source polynomials by
   constant-degree composition towers and norm layer by layer. Likely failure:
   no arbitrary-prime `x_interval` tower is known, or active width reaches D2.
3. **Batched target-translation recurrence.** Update scalar child norms across a
   preregistered target progression. Likely failure: recurrence state is an N2
   remainder or loses witness descent.

### Go/no-go boundary

No current family passes the zero-run gate. A new paper interface may continue
only if it lists every internal vector space and target boundary, provides an
exact compact selector or complete addition formulation, exposes both child
values or updates, and has a plausible strict sub-B2 work path.

### Failure modes

- Treating scalar output, low displacement rank, visual sparsity, or complete
  addition formulas as a complexity result.
- Suppressing `soft-O(B^2)` logarithms and calling the result subquadratic.
- Omitting selector, moment, child, certificate, or witness state.
- Moving B3 tables into fixed preprocessing without charging advice.

### Next concrete action

Derive or refute the bounded-separation normal form for complete-projective
`G_(I,Q)` at the root, including the node polynomial `M_I`; stop if rank,
moments, selector state, or contraction work reaches `Omega(B^2)`.

### Artifact paths

- `candidate-review-v1.md`
- `nested-source-norm-preflight-v1.md`
- `nested-source-norm-literature-review-v1.md`
- `decision-v2.json`
