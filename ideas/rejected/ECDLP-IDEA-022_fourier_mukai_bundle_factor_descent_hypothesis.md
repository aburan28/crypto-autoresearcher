# ECDLP-IDEA-022 — Fourier–Mukai bundle-factor descent

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct derived transform or bundle isomorphism is not a break.

## Falsifiable hypothesis

After a frozen Fourier–Mukai transform from `E` to its dual, target divisor incidence can
be represented as tensor/convolution of a small dictionary of factor-base bundle atoms and
factored with witness recovery in sublinear work in `B=N^beta`. Complete relation
collection, base-log linear algebra, and unchanged individual descent then have exponent
below `1/2`.

## Mechanism-new operation

Transform point/divisor objects to sheaves on the dual elliptic curve so addition becomes
tensor/convolution, then perform **sparse bundle-atom factorization with inverse-transform
witness recovery**. This is not an equation/solver change or idea 012's aggregate support
intersection. If the transform only relabels the same degree-`B` support problem, the
proposal is a categorical duplicate and fails.

## Assumptions

1. The Fourier–Mukai kernel, normalizations, and inverse transform are explicit over the charged field.
2. Factor-base atoms and their bundle images are target-independent.
3. A factorization returns actual curve points after inverse transform, not only a K-theory class.
4. Isomorphism testing, extension groups, ranks, failures, and multiplicities are charged.
5. Relation and target densities are measured independently.
6. Every scaling statement is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`point_sheaf_Fourier_Mukai_transform | addition_to_tensor_convolution | factor_base_bundle_atom_dictionary | sparse_factorization_with_inverse_witness`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the quotient cost the bundle factorization must remove.
2. `ledger/H-REP-001.yaml` — prevents a representation equivalence alone from counting.
3. `ledger/H-FB-001.yaml` — atom selection is not the new operation.
4. `ledger/EV-FB-001.yaml` — supplies the matched density control.
5. `ledger/SYNTHESIS-20260716.md` — requires complete descent and memory accounting.

## Closest primary literature

- Mukai, [Duality between `D(X)` and `D(X-hat)` with its application to Picard sheaves](https://doi.org/10.1017/S002776300001922X), establishes Fourier–Mukai duality for abelian varieties.
- Burban and Kreußler, [Derived categories of irreducible projective curves of arithmetic genus one](https://arxiv.org/abs/math/0503499), supplies explicit genus-one derived-category structure.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), is the point-decomposition baseline.

No source supplies the claimed sparse bundle-factor witness algorithm; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the transform kernel, inverse, factor base `F`, and a canonical bundle-atom representation.
2. Transform every atom and build the target-independent dictionary with exact storage accounting.
3. For `R=[a]P+[b]Q`, transform the target object and recover every sparse atom factorization.
4. Invert each candidate, verify all points lie in `F` and sum to `R`, and retain failures/ambiguities.
5. Collect independent rows and solve factor-base logarithms.
6. Factor the unchanged transformed object for `Q+[t]P`, substitute base logs, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Let transform/dictionary construction cost `N^a`, per-query bundle factorization `N^q`,
reciprocal relation/target densities `N^delta,N^delta_t`, sparse-LA exponent
`omega_s*beta`, inverse verification `N^v`, and storage `N^s`. Rho is `N^1/2` time;
BSGS is `N^1/2` time/memory. The proposal has
`lambda=max(a,beta+delta+q,omega_s*beta,delta_t+q,beta+v)` and
`mu=max(s,beta)`. Dense extension-algebra or isomorphism costs replace optimistic terms
when applicable.

## Likely fatal obstruction

Fourier–Mukai is an equivalence and should preserve the information-theoretic hardness of
Picard support. Sparse factorization can require the same membership quotient, and a
K-theory-class decomposition need not recover points. Bundle ranks/extension spaces can
grow as `Omega(B)`.

## Proof track

Give an explicit transform-level factorization theorem with unique recoverable atoms and
prove build, density, query, inverse, and LA bounds giving `lambda,mu<1/2`.

## Disproof track

Show equivalence to the occupied aggregate/quotient matrix, produce class-level collisions
without point witnesses, or prove factorization/extension dimension is `B^(1-o(1))`.

## Positive and negative controls

- Positive control: planted direct sums/tensor products of known line-bundle atoms.
- Positive instrumentation control: exhaustive transform/inverse checks on tiny curves.
- Negative control: random same-rank bundles with matched Chern data.
- Duplicate control: compare matrices and operation counts with ideas 012 and 013.
- Leakage control: blind atom labels and reject target-trained dictionaries.

## Quantitative promotion and falsification gates

Use 11–24-bit subgroups, 30 curves per size, `beta in {0.15,0.18,0.20}`, and exhaustive
truth through 16 bits. Promotion requires zero false inverse witnesses, 99.9% transform
agreement, 1,000 relations and 100 descents at the largest two sizes, and upper 95%
`q+delta<=0.20`, `q+delta_t<=0.45`, `lambda<=0.45`, `mu<=0.45`.
Falsify if only K-theory classes are recoverable, any accepted point support is wrong,
the implementation is matrix-equivalent to an occupied mechanism without a cost
separation, or every full-cost lower bound reaches `0.50`. Library failures are infrastructure evidence.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-022/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-022/fourier_mukai_factor.sage`
- `ideas/artifacts/ECDLP-IDEA-022/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-022/runs/<run_id>/bundles.jsonl`
- `ideas/artifacts/ECDLP-IDEA-022/runs/<run_id>/supports.jsonl`
- `ideas/artifacts/ECDLP-IDEA-022/analysis.md`

## Interpretation boundary

All claims are toy, heuristic, model-bound, and novelty-unverified. Transform correctness,
a bundle identity, or a relation certificate is not a speedup.

## Exactly one next executable action

1. Implement the exhaustive transform-factor-inverse loop for planted and random supports on 11–16-bit curves and compare its matrices to ideas 012 and 013.
