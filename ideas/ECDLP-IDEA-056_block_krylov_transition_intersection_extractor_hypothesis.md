# ECDLP-IDEA-056 — Block-Krylov transition-intersection extractor

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` exact-identity preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Krylov kernel, common root, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Let the ledger's accepted logarithmic one-transition subgroup-norm oracle act on a
factor-base deck of size `L=N^beta`. Two consecutive transitions admit a shared module
`A_L` of dimension `L^(1+o(1))` and implicit multiplication operators `M_1,M_2` such
that a stated common-state nullspace/minimal-polynomial identity holds **if and only if**
the two-transition relation has a source witness. A block-Krylov computation and exact
lift from the nullspace recover all source endpoints in `L^(alpha+o(1))` time with
`alpha<1.5`, emit `Theta(L)` auditable rows per successful batch, never materialize the
dense `L^2` resultant, and give full time and memory exponents below `1/2`.

## Mechanism-new operation

The new operation is the **shared-module transition-intersection identity with source
lift**. The two sparse one-transition norm recurrences are represented as implicit
multiplication operators on one quotient module; their common cyclic state is extracted,
and its nullspace/eigenvector data invert to the original transition endpoints. Block
Wiedemann is only the evaluator of that identity.

A generic Krylov solver, a different resultant engine, an explicit `L^2` pair matrix,
Berlekamp-Massey on materialized coefficients, solver substitution, parameter change,
post-hoc selector, or relation-only certificate does not satisfy the mechanism.

## Assumptions

1. `E(F_p)` contains a known prime-order subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. The subgroup-x deck/factor base has `L=N^beta` public, target-independent elements.
3. The exact one-transition norm recurrence and endpoint extractor are independently reproduced before composition.
4. `M_1` and `M_2` are available by logarithmic-cost matvec oracles without storing their dense matrices or resultant.
5. The common-state identity is biconditional and its lift returns every source endpoint, including multiplicities and exceptional charts.
6. Block size, iterations, extension fields, output, failed batches, rank, target descent, and memory are fully charged.
7. All extrapolations are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`accepted_sparse_transition_norm | shared_quotient_module | implicit_multiplication_operators | common_state_nullspace_iff | exact_endpoint_source_lift | no_dense_L2_object`

The fingerprint targets the explicit open branch after `P1478/ECFG-MX-1478`. It is
distinct only if the shared-module theorem and source lift are established; "use block
Krylov on the resultant" is a duplicate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — fixes the measured source-membership arithmetic baseline.
2. `ledger/H-REP-001.yaml` — blocks an implicit representation with unchanged total solve cost.
3. `ledger/EV-REP-002.yaml` — supplies exact scaling and representation controls.
4. `ledger/H-FB-001.yaml` — prevents deck/factor-base retuning from carrying the claim.
5. `ledger/SYNTHESIS-20260716.md` — requires source recovery, relation rank, descent, verification, and memory costs.

## Closest primary literature

- Wiedemann, [Solving sparse linear equations over finite fields](https://doi.org/10.1109/TIT.1986.1057137), supplies the black-box minimal-polynomial method.
- Coppersmith, [Solving homogeneous linear equations over GF(2) via block Wiedemann algorithm](https://research.ibm.com/publications/solving-homogeneous-linear-equations-over-gf2-via-block-wiedemann-algorithm), supplies the block generalization.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the nearby point-decomposition relation.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies the complete-chart requirement for source lifting.

The linear-algebra papers do not provide the elliptic shared-module biconditional or
source lift. The ledger supplies an accepted one-transition primitive, not this
composition theorem; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,beta,L`, the subgroup-x deck, exact transition charts, and the previously accepted one-transition recurrence.
2. Reproduce the one-transition norm and endpoint extractor against exhaustive truth.
3. Define `A_L,M_1,M_2` and machine-check the claimed common-state biconditional on every tiny two-transition instance before any scaling.
4. Run frozen block-Krylov projections using only implicit matvecs; recover the common minimal polynomial/nullspace and lift every state to source endpoints.
5. For known `R=[a]P` batches, independently verify each endpoint, complete relation, coefficient, and curve sum; retain all misses and multiplicities.
6. Collect `L+margin` independent small-base rows, measuring batch output and rank, then solve factor-base logarithms.
7. Apply the identical module and lift to randomized `Q+[t]P` batches until a verified target descent is recovered.
8. Substitute factor-base logs, remove `t`, recover `x`, and independently verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `L=N^beta`; shared-module build exponent be
`a` in `N`; one successful source-resolving batch cost `L^alpha` and emit
`Theta(L)` usable candidate rows; reciprocal successful-batch and target-batch
probabilities be `N^delta` and `N^delta_t`; sparse linear algebra cost
`N^(2beta+o(1))`; and full retained storage exponent be `s`.

Then `T_rel=N^(delta+beta*alpha+o(1))`,
`T_desc=N^(delta_t+beta*alpha+o(1))`,
`lambda=max(a,delta+beta*alpha,2beta,delta_t+beta*alpha)`, and
`mu=max(s,beta)`. If a batch emits only `L^theta` independent rows with `theta<1`,
add `beta*(1-theta)` to relation collection. If matvec setup, Krylov dimension,
iterations, source lift, or output reaches `Omega(L^2)`, set `alpha>=2`. The ledger's
`alpha<1.5` gate is necessary; the focal `beta=0.20,delta=0.20` arm requires the
stronger upper bound `alpha<=1.25` for `lambda<=0.45`.

## Likely fatal obstruction

The two transition algebras may not share a small faithful module: their intersection
can have minimal-polynomial degree `Theta(L^2)`, exactly the dense resultant degree.
Even with a short nullspace, lifting eigenvectors to source endpoints can enumerate
`L^2` pairs, or emitted rows can be too dependent to amortize the batch. Any such outcome
restores the recorded obstruction.

## Proof track

Specify `A_L,M_1,M_2`; prove module dimension and logarithmic matvec bounds; prove the
common-state nullspace/minimal-polynomial condition is necessary and sufficient; give a
complete endpoint/source lift; and bound block size, iterations, extension degree,
output independence, density, rank, descent, verification, and memory to obtain
`lambda,mu<1/2`.

## Disproof track

Produce a generic false positive/negative to the biconditional, prove module or
minimal-polynomial dimension `Omega(L^2)`, show source lift enumerates pairs, measure
sublinear independent output, or establish `lambda>=1/2` for every frozen complete-cost arm.

## Positive and negative controls

- Positive primitive control: reproduce the exact logarithmic one-transition norm and endpoint extractor.
- Positive linear-algebra control: a planted pair of implicit sparse operators with a known shared invariant module and source labels.
- Positive correctness control: exhaustive two-transition roots and sources on tiny curves.
- Negative algebra control: matched random sparse operators with no shared state.
- Mechanism control: the dense two-transition resultant and an explicit `L^2` pair matrix.
- Solver control: block Wiedemann applied only after materializing the resultant; it must receive no mechanism credit.
- Leakage control: forbid scalar coordinates, target-selected projections, post-hoc row filters, hidden pair tables, and discarded failed batches.

## Quantitative promotion and falsification gates

Phase 1 is mandatory: on all frozen tiny instances, machine-check the shared-module
biconditional, exact multiplicities, and endpoint/source lift with zero errors. No scaling
metric may be interpreted before Phase 1 passes independently.

Phase 2 uses at least 20 ordinary prime-field curves per size, `L in {16,32,...,4096}`
where feasible, three preregistered block sizes, and three seeds. Promotion requires
zero incorrect or missed exhaustive witnesses, at least 1,000 verified relations and 100
target descents at each of the two largest `N` sizes, at least `0.8L` independent emitted
rows per accepted batch, upper 95% `alpha<=1.25` in the focal arm,
`a<=0.45`, `lambda<=0.45`, and `mu<=0.45`, stable leave-largest-size-out fits, and
no dense `L^2` object in resource traces.

Falsify the scoped mechanism on any independently reproduced biconditional/source-lift
error, lower 95% module dimension/iteration/lift exponent `>=2` in `L`, fewer than
`0.5L` independent rows per batch at two largest sizes, or lower 95%
`lambda>=0.50` in every arm. A crash, unsupported dependency, or budget censoring is not
mathematical falsification.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-056_transition_intersection_preflight.yaml`
- Module derivation: `ideas/artifacts/ECDLP-IDEA-056/shared_module_identity.md`
- Implementation: `ideas/artifacts/ECDLP-IDEA-056/transition_intersection.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-056/verify_sources.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-056/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-056/analysis.md`
- Retain operators, projections, Krylov sequences, minimal polynomials, nullspaces,
  endpoints, row ranks, failures, operation counts, memory, seeds, commands, environment,
  commit, dirty-tree state, stdout, and stderr.

## Interpretation boundary

The hypothesis remains toy, heuristic, model-bound, and novelty-unverified. Reproducing
the one-transition oracle, finding a short Krylov recurrence, or emitting a valid
relation is not a breakthrough. Only exact source recovery and complete matched
rho/BSGS accounting can support escalation.

## Exactly one next executable action

1. After coordinator approval, execute Phase 1 of `ideas/contracts/ECDLP-EXP-CONTRACT-056_transition_intersection_preflight.yaml` and stop before scaling unless the shared-module biconditional and source lift pass independently.
