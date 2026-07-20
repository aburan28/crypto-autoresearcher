# ECDLP-IDEA-041 — Elliptic Cauchy chord locator

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct pair-sum identity, locator count, or toy relation is not a break.

## Falsifiable hypothesis

For a generic ordinary prime-field curve with a prime subgroup of order `N≈p`, there is
an exact elliptic Cauchy/Frobenius–Stickelberger product identity that compiles a frozen
factor base `F` of size `B=N^beta` into a target-independent chord locator of construction
and bit-memory exponent below `1/2`. A recursive factor splitter queries this locator at
`R`, returns actual atoms `A,B in F` with `A+B=R`, and supports enough known-scalar
relations plus a separate masked-target descent for total exponent below rho and BSGS.
The claim is `heuristic`, `model-bound`, `novelty-unverified`, and initially only `toy`.

## Mechanism-new operation

The proposed operation is an **exact elliptic product compression with recursive atom
recovery**: derive a succinct product/norm formula for the chord intersections of two
factor-base subsets, evaluate it on a target, and bisect the subsets until a verified
pair is exposed. This is not low spectral rank (`001`), an aggregate count (`012`), an
elliptic-code syndrome (`014`), a dense resultant, or a generic solver substitution.
It survives only if the elliptic identity avoids materializing `Theta(B^2)` pair sums and
the same recursive factors return both atom labels. Otherwise it merges with `001/012`.

## Assumptions

- `E(F_p)` contains a public prime subgroup `<P>` of order `N=p^(1+o(1))`, with `Q=[x]P`.
- `F` and every subset split are deterministic and independent of `Q`.
- All vertical lines, tangencies, repeated points, signs, poles, and points at infinity
  are represented and verified exactly.
- Locator construction, coefficients, product trees, misses, recursive splits, and
  emitted witnesses are charged in bit operations and bits of storage.
- No scalar-indexed pair table, known-log branch selector, or target-specific rebuild is used.
- Extrapolation from toy curves remains heuristic and model-bound.

## Semantic fingerprint

`elliptic_chord_Cauchy_product | succinct_pair_sum_locator | recursive_factor_split | explicit_two_atom_witness | target_independent_relation_and_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field relation and membership cost floor the locator must remove.
2. `ledger/H-FB-001.yaml` — changing the shape of the point set is not the proposed operation.
3. `ledger/EV-FB-001.yaml` — supplies the matched random-base yield and scaling control.
4. `ledger/H-REP-001.yaml` — prevents an equation rewrite at unchanged pair-search cost from counting as new.
5. `ledger/SYNTHESIS-20260716.md` — requires a complete relation, linear-algebra, descent, and rho comparison.

## Closest primary literature

- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), gives the underlying point-sum condition.
- Bostan, Morain, Salvy, and Schost, [Fast algorithms for computing isogenies between elliptic curves](https://doi.org/10.1090/S0025-5718-08-02066-8), develops nearby elliptic product and fast rational-function machinery but not this locator.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, [3SUM with preprocessing](https://arxiv.org/abs/1907.08355), is the generic preprocessing/query baseline.

None of these sources supplies a subquadratic exact chord-product representation with
recursive witness recovery. That proximity statement is not a novelty proof.

## Complete factor-base-to-target-descent path

- Freeze `F`, a balanced deterministic subset tree, and exact chord-line conventions.
- Build the proposed elliptic product object at every tree node without enumerating pair sums.
- For independent known scalars `r`, query `R=[r]P`; recursively split only certified
  nonempty product factors and output candidate pairs.
- Independently verify `A,B in F` and `A+B=R`; retain every miss, ambiguity, and false branch.
- Collect `B+margin` independent rows and solve for every factor-base logarithm.
- Query the identical frozen locator on `Q+[t]P`, recover a verified pair, substitute its
  solved logs, remove `t`, and verify `[x]P=Q` on the original curve.

## Full rho/BSGS cost model

Let `B=N^beta`; locator build cost `N^a`; one query and recursive witness recovery cost
`N^q`; reciprocal known-target and masked-target success probabilities `N^delta` and
`N^delta_t`; target query exponent `q_t`; and complete stored coefficients and tree state
`N^s` bits.

- Pollard rho: `N^(1/2+o(1))` group operations and `N^o(1)` memory.
- BSGS: `N^(1/2+o(1))` time and `N^(1/2+o(1))` stored points.
- Locator construction: `N^(a+o(1))`.
- Relation collection: `N^(beta+delta+q+o(1))`, including misses and recursive branches.
- Sparse linear algebra: `N^(2*beta+o(1))` time and `N^(beta+o(1))` memory; dense fallback is charged as `N^(3*beta+o(1))`.
- Individual descent: `N^(delta_t+q_t+o(1))`.

Thus the optimistic sparse time exponent is
`lambda=max(a,beta+delta+q,2*beta,delta_t+q_t)` and bit-memory exponent is
`mu=max(s,beta)`. Any `Theta(B^2)` locator has `a` or `s` at least `2*beta` and must be
charged as such; no amortization is used for the single-target claim.

## Likely fatal obstruction

The divisor of the exact pair-sum locator may contain `Theta(B^2)` independent zeros, so
information-theoretic output size or coefficient degree can force quadratic construction
or storage even when multipoint evaluation is fast. Recursive nonemptiness may also be
count-only, with atom recovery reconstructing the original support problem.

## Proof track

Prove the elliptic product identity, a subquadratic representation-size bound, and a
target-uniform recursive splitter that emits all pair labels with charged complexity.
Combine its density with relation rank, sparse solve, and masked target descent to exhibit
parameters with `lambda,mu<1/2`.

## Disproof track

Prove a `B^(2-o(1))` degree/size lower bound, show recursive splitting needs ordinary
pair enumeration, find count/witness separation, or establish that every admissible
parameter choice has a lower confidence bound `lambda>=1/2`.

## Positive and negative controls

- Positive control: a scalar-labeled cyclic group with an FFT pair-sum locator and exact witnesses.
- Instrumentation control: exhaustive pair sums must match every locator query through the truth boundary.
- Negative control: random point sets with matched size and pair-sum density.
- Mechanism ablation: ordinary product-tree evaluation without the elliptic compression identity.
- Leakage control: audit and reject scalar-indexed caches, known-log branches, and target-dependent rebuilds.

## Quantitative promotion and falsification gates

Use ordinary curves at 10–19 bits, at least 30 curves per size, `B` from 32 through 512,
and exhaustive pair truth throughout. Promotion requires zero false accepted pairs,
exact count agreement, upper 95% bounds `a<=0.40`, `q<=0.20`, `s<=0.40`, and at least one
preregistered `beta<=0.22` arm with `lambda<=0.45` and `mu<=0.45`. Falsify the scoped
claim if representation size is `Omega(B^2)`, any nonempty recursive branch cannot emit
atoms without enumeration, or every full-cost fit has lower 95% `lambda>=0.50`.

## Artifact plan

- Specification: `ideas/artifacts/ECDLP-IDEA-041/preflight_spec.yaml`
- Identities: `ideas/artifacts/ECDLP-IDEA-041/chord_product_identity.md`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-041/chord_locator.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-041/runs/<run-id>/`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-041/analysis.md`

## Interpretation boundary

This is a toy, heuristic, model-bound, novelty-unverified hypothesis. A correct identity,
fast evaluation, count, or valid relation is not a breakthrough. Only complete verified
atom recovery and target descent below both rho and BSGS can justify escalation.

## Exactly one next executable action

1. On every preregistered ordinary prime-order curve with `p<2^19`, construct bases through `B=512`, compare candidate elliptic product identities with exhaustive pair sums, and record exact representation size and recursive witness operations.
