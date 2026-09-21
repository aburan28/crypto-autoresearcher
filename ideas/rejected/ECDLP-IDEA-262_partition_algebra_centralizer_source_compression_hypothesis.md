# ECDLP-IDEA-262 — Partition-algebra centralizer source compression

## Status and claim labels

- Class: `representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_fixed_arity_centralizer_only_removes_permutation_constant`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a diagram identity, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For fixed relation arity five, the factor-source tensor admits an exact partition-algebra/centralizer representation whose diagram coordinates retain point identities while reducing construction, storage, and source inversion below the rho and BSGS exponents.  Primitive centralizer components would then decode the unordered five-source orbit from an endpoint without enumerating the source tensor.

## Mechanism-new operation

The screened operation is **project the ordered five-source relation tensor through the partition-algebra centralizer, then invert centralizer components to the exact unordered factor-point orbit**.  Partition diagrams organize equality patterns and the commuting action on a supplied tensor.  Quotienting the five tensor slots by `S_5` removes at most the fixed `5!` permutation factor: the point-faithful unordered basis still has `binom(B+4,5)=Theta(B^5)` states.  Passing instead to the stable `S_B` centralizer forgets the actual factor-point labels and keeps only equality patterns.  Thus the proposal merges with IDEA-035 tensor rank, IDEA-142 linear-pencil compression, IDEA-151 orbit-finite symmetry compression, and IDEA-253 MPS canonicalization when the source tensor and label lift are charged.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A target-uniform centralizer element is constructed from compact elliptic equations and an endpoint without expanding the `B^5` source tensor.
2. The quotient retains a biconditional dictionary from every surviving component to exact signed factor points, not merely multiplicity or equality patterns.
3. Centralizer projection, decomposition, source unranking, ambiguity output, rank completion, factor logs, masked descent, and verification are exact over the stated field.
4. Tensor input, diagram coefficients, module multiplicities, point-label dictionaries, all failed branches, output, time, and peak memory are charged.

## Semantic fingerprint

`five_source_relation_tensor | partition_algebra_centralizer | fixed_slot_symmetry_quotient | point_faithful_component_inverse | exact_unordered_source_orbit | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate and tensor-source barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the transposed tensor/full-rank negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear feature-rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact-transition and dense-composition control.

## Closest primary literature

- Halverson and Ram, Partition Algebras, [https://arxiv.org/abs/math/0401314](https://arxiv.org/abs/math/0401314), develops the diagram algebra and its Schur-Weyl centralizer action on a supplied tensor space.
- Bowman, Doty, and Martin, Integral Schur-Weyl duality for partition algebras, [https://arxiv.org/abs/1906.00457](https://arxiv.org/abs/1906.00457), proves an integral centralizer description but does not supply a point-faithful inverse from an elliptic endpoint.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but not a compressed exact source tensor.

These primary records were checked for the named supplied-input operation.  None gives an endpoint-only point-faithful centralizer compiler, exact source-orbit inverse, factor-log calibration, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity five, tensor-slot action, centralizer basis, colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct its relation tensor directly in partition-algebra/centralizer coordinates without enumerating ordered or unordered five-source tuples and without a source-labelled table.
3. Decompose the centralizer element, invert every accepted component to exact signed factor points, and verify the elliptic sum.  Preserve every failure, collision, repeated point, equality-pattern ambiguity, infinity chart, nonreduced component, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and source output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and component inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected representation, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by component ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every tensor coordinate, diagram coefficient, module multiplicity, point dictionary, preprocessing query, failed target, branch, source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness or relation validity alone has no performance meaning.

## Likely fatal obstruction

At fixed arity five, slot symmetrization changes `B^5` only by the constant `5!`.  A partition-algebra centralizer small enough to be independent of `B` records equality diagrams under global relabelling and therefore cannot name actual factor points.  Restoring point labels requires a source-faithful module or dictionary of `Theta(B^5)` states, so the centralizer begins after the missing source tensor exists or discards the provenance needed for descent.

## Proof track

Construct an endpoint-only centralizer element, prove that its sub-`N^0.45` representation remains injective on exact unordered point orbits, give a deterministic all-source inverse, and prove both complete exponents at most `0.45`.

## Disproof track

Prove that every point-faithful fixed-arity quotient has `Theta(B^5)` states, exhibit distinct source orbits with identical stable centralizer coordinates, or show construction, label lift, output, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied five-source tensor with known point labels, where partition-diagram projection and exact orbit recovery are checked.
- Negative controls: slot permutations of the same tuple, tuples with the same equality pattern but different points, the stable `S_B` centralizer, IDEA-035, IDEA-142, IDEA-151, IDEA-253, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only centralizer compiler and exact point-orbit inverse of exponent at most `0.45`, zero false sources, complete recall on all frozen strata, full factor-log rank, blind masked descent, and complete `lambda` and `mu` at most `0.45`.  A fixed `5!` saving, equality-pattern output, supplied source tensor/dictionary, `Theta(B^5)` point-faithful state, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-262/partition_centralizer_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-262/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-262/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-262/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct centralizer identity, exact projection, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-262/partition_centralizer_source_theorem.md` proving a sub-rho endpoint-to-point-faithful centralizer inverse or the fixed-arity `Theta(B^5)`/label-forgetting no-go.
