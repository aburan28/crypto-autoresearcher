# ECDLP-IDEA-199 — Ranked subset-convolution source unranking

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_subset_dp_requires_endpoint_coefficient_deck`
- Cohort: `20260718-d`
- Evidence scale: literature and input-size audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective tests are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a fast transform or detected coefficient is not an ECDLP break.

## Falsifiable hypothesis

A ranked subset-convolution/zeta-transform representation of factor-base atoms can propagate elliptic partial sums while retaining source rank, and an endpoint coefficient can be self-reduced to an exact signed five-source tuple with setup and query below rho/BSGS.

## Mechanism-new operation

The operation is **ranked Möbius/zeta convolution with exact endpoint-conditioned source unranking**. Fast subset convolution changes an explicit subset-DP backend; the proposed ECDLP gain requires a compact endpoint coefficient oracle. With `B` atom labels, the transform domain has `2^B` states, while restricting to five-subsets still exposes `Theta(B^5)` coefficients or the existing transition/source deck. Thus this version merges into coefficient-oracle and provenance controls.

## Assumptions

1. Public curve, prime order `N`, `B=N^beta` factor points, and target are fixed.
2. Partial-sum values are represented without a table over group endpoints or scalar indices.
3. The transform retains signs, repeated atoms, infinity, and exact labelled ancestry.
4. Endpoint self-reduction uses target-independent queries and emits every exact source.
5. Transform construction, coefficients, failed endpoints, output, rank, descent, and memory are charged.

## Semantic fingerprint

`ranked_subset_lattice | fast_zeta_Mobius_convolution | elliptic_partial_sum_payload | endpoint_coefficient_self_reduction | exact_source_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the explicit serial-state boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge floor.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge charge.
5. `inputs/ledger_inventory.json` — imported `P1480`, a solver/backend control on the same relation.

## Closest primary literature

- Björklund, Husfeldt, Kaski, and Koivisto, [Fourier meets Möbius: fast subset convolution](https://doi.org/10.1145/1250790.1250801), accelerates transforms on an explicit subset lattice.
- Alon, Yuster, and Zwick, [Color-coding](https://doi.org/10.1145/210332.210337), isolates supplied combinatorial structures but does not construct an elliptic source grammar.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint relations without a subset coefficient oracle.

No checked source supplies the compact source-unranking operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the ranked transform, partial-sum encoding, signs, masks, and verifier.
2. Build the transform without enumerating endpoint/source coefficients.
3. Query known-log endpoints, self-reduce nonzero coefficients to exact sources, and verify them.
4. Preserve transform collisions, repeats, infinity, multiplicity, failed targets, and output lists.
5. Collect independent rows, solve and verify factor logs.
6. Query fresh masks `Q+[r]P` using the same transform.
7. Substitute logs, subtract masks, and verify the scalar.
8. Charge construction, transforms, queries, output, rank, descent, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup be `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query/self-reduction `N^q,N^q_m`, ranked rows/query `N^r`, output/ambiguity `o,u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; fast transform time on an explicit exponential domain is not promotable.

## Likely fatal obstruction

The subset transform indexes supplied atom subsets, not elliptic endpoints. Attaching exact group sums yields one state per retained subset/partial source; endpoint coefficient access therefore materializes `B^5=N` leaves or at least the `B^3` meet state. Möbius inversion preserves aggregate coefficients but supplies no new source-generating operation.

## Proof track

Construct a quotient of the ranked transform with at most `B^2.25` states that is biconditional for exact endpoints and retains leaf ancestry, then prove `lambda,mu<=0.45` through blind descent.

## Disproof track

Prove distinct source subsets require distinct transform states, reduce coefficient queries to explicit source edges, exhibit endpoint collisions after quotienting, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: subset convolution on supplied small labelled families with known endpoint payloads.
- Negative control: explicit `2^B` transforms, five-subset tables, scalar-index payloads, and post-hoc coefficient selectors.
- Negative control: rho, BSGS, known-log endpoints, and blind masks.

## Quantitative promotion and falsification gates

This version is merged/rejected. A successor needs at most `B^2.25` target-independent transform state, exact all-source unranking, zero false tuples, no scalar labels, and `lambda,mu<=0.45`. Explicit `B^3` or `B^5` state, one merged source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective state theorem: `ideas/artifacts/ECDLP-IDEA-199/ranked_transform_state_theorem.md`
- Prospective unranking specification: `ideas/artifacts/ECDLP-IDEA-199/endpoint_unranking_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-199/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified algorithm analysis. Tests would be toy and projections heuristic and model-bound. A transform, coefficient, source tuple, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-199/ranked_transform_state_theorem.md` proving a source-biconditional quotient with at most `B^2.25` state or proving that exact endpoint/source separation forces `Omega(B^3)` retained states.

