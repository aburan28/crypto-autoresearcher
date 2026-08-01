# ECDLP-IDEA-259 — Kruskal moment-tensor source atomization

## Status and claim labels

- Class: `moment_tensor_decomposition`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_kruskal_requires_hidden_moment_tensor`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; uniqueness of a supplied tensor decomposition, relation validity, an atom list, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Three fixed public feature maps turn one endpoint's unknown five signed factor points into a compact rank-five third-order moment tensor.  Kruskal-identifiable CP decomposition would then recover the five atoms up to harmless permutation and scaling, enabling complete relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **form `T_R=sum_{i=1}^5 a(D_i) tensor b(D_i) tensor c(D_i)` and apply Kruskal-identifiable CP decomposition to recover the five source atoms**.  Tensor atomization conditional on `T_R` is the only operation receiving credit.  It merges with IDEA-191 because moment/cumulant inversion also assumes source-sensitive moments, and with IDEA-253 because canonical tensor recovery begins after a source-faithful tensor is supplied; IDEA-035, IDEA-124, live `P1536`, and live `P1539` are representation, aggregate-moment, derivative-localization, and endpoint-fiber controls.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Fixed target-independent feature maps `a,b,c` are computable for factor-base points and give Kruskal ranks sufficient for uniqueness over the working finite field.
2. A compact endpoint-only procedure constructs the rank-five tensor `T_R` without already knowing one source tuple or summing the full relation fiber.
3. CP factors lift biconditionally through scaling, permutation, signs, multiplicities, and exceptional strata to exact factor-base points.
4. Feature construction, moment formation, decomposition, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`compact_endpoint_moment_tensor | Kruskal_identifiable_CP_decomposition | rank_one_source_atoms | exact_signed_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/tensor preprocessing barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the proposed exact source-resolving recursive-feature representation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full-rank nonlinear feature-to-source boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact aggregate transition primitive whose composition becomes dense.

## Closest primary literature

- Kruskal, Three-way arrays: rank and uniqueness of trilinear decompositions, [https://doi.org/10.1016/0024-3795(77)90069-6](https://doi.org/10.1016/0024-3795(77)90069-6), proves sufficient uniqueness conditions for a supplied three-way tensor decomposition.
- Allman, Matias, and Rhodes, Identifiability of parameters in latent structure models with many observed variables, [https://doi.org/10.1214/09-AOS689](https://doi.org/10.1214/09-AOS689), applies Kruskal-type identifiability to supplied joint distributions rather than constructing hidden elliptic source moments.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but no rank-five mixed-moment oracle.

These primary records were checked for the named identifiable tensor operation.  None supplies endpoint-to-moment construction, exact point-source calibration, factor-log completion, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity five, feature maps `a,b,c`, tensor field, Kruskal-rank gate, normalization, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the claimed rank-five `T_R` from compact endpoint and factor-base data without knowing a source tuple, enumerating the `B^5` fiber, or storing a `Theta(B)` full-factor-base moment tensor.
3. Decompose `T_R`, normalize scaling and permutation, lift all rank-one factors to exact signed factor points, verify sums, and preserve every nonunique decomposition, rank failure, repeated atom, multiplicity, false source, ambiguity branch, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen moment constructor and atomizer to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected features, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by tensor ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one tensor construction plus exact CP source inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every feature value, tensor entry, tensor rank, decomposition branch, normalization, preprocessing query, failed target, source atom, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; CP uniqueness or relation validity alone has no performance meaning.

## Likely fatal obstruction

Kruskal uniqueness begins after the tensor is supplied.  The desired rank-five tensor is itself a sum over the five unknown sources, while the endpoint group sum supplies none of its mixed moments.  Summing features over the public factor base produces rank `Theta(B)` aggregate data unrelated to the selected tuple; building the desired rank-five tensor requires knowing the answer.  A source-faithful tensor over all endpoint-compatible tuples restores the relation deck, so Kruskal identifiability is not a tensor-construction or hidden-source oracle.

## Proof track

Construct `T_R` from the endpoint alone, prove the Kruskal conditions and a scaling/permutation-safe exact point inverse on every stratum, and derive complete exponents at most 0.45.

## Disproof track

Exhibit two endpoint-compatible source orbits inducing indistinguishable permitted moments, reduce `T_R` construction to knowledge of a source tuple or the full relation tensor, or prove tensor rank, output, or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied rank-five tensors with planted factors satisfying preregistered Kruskal-rank conditions and independent atom verification.
- Negative controls: source permutations and scalings, deficient Kruskal ranks, moment-matched distinct source multisets, full-factor-base moments, IDEA-124, IDEA-191, IDEA-253, live `P1536`, live `P1539`, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-only tensor construction and decomposition of exponent at most 0.45, exact all-source and multiplicity recall with zero false sources, no planted or source-indexed moment input, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  Supplied rank-five moments, a rank-`Theta(B)` aggregate tensor, one nonunique source lift, source-deck construction, or either exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-259/kruskal_moment_source_no_go.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-259/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-259/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-259/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A unique CP decomposition, correct tensor identity, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-259/kruskal_moment_source_no_go.md` proving either an endpoint-only rank-five moment compiler with exact atom lift or that moment construction already requires the hidden source tuple/relation deck.
