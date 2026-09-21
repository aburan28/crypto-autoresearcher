# ECDLP-IDEA-391 — Mackey double-coset source decomposition

## Status and claim labels

- Class: `representation-theoretic`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_useful_double_cosets_require_hidden_scalar_labels_and_representation_components_lack_factor_provenance`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run theorem-preflight only; `review_required`, unapproved, and never dispatchable
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Mackey decomposition or character identity is not an ECDLP break.

## Falsifiable hypothesis

Signed factor-deck membership admits a nonhomomorphic public correspondence with subgroups `H,K` whose induced representation decomposes by a small Mackey double-coset set, and the components can be queried and recombined to recover exact factor occurrences for relations and blind targets below the campaign gates.

## Mechanism-new operation

The screened operation is **induce a source representation from one deck subgroup, restrict it along a second public correspondence, decompose the restriction over `K\G/H` by Mackey's formula, solve component-local endpoint constraints, and lift a compatible component tuple to signed factor occurrences**. It is distinct only if the correspondence is nonhomomorphic and source-faithful; an isogeny, character basis, or ordinary subgroup relabelling is a control.

## Assumptions

1. Public endpoint data define groups/subgroups and a nonhomomorphic correspondence whose double cosets align with factor-deck source fibers without using scalar labels.
2. The number and representation dimensions of relevant double-coset components fit target-independent setup/state `B^(9/4+o(1))`.
3. Component restriction/intertwining is exact, covers every signed Semaev stratum, and admits a canonical occurrence-labelled inverse.
4. The same frozen component system gives full-rank relations and scalar-blind target descent with complete query work `B^(5/4+o(1))`.
5. Group/correspondence construction, induction/restriction, intertwiners, component ambiguity, output, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`nonhomomorphic_deck_correspondence | induced_source_representation | Mackey_double_coset_restriction | component_endpoint_matching | occurrence_source_lift`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H008`; auxiliary Prym/elliptic blocks motivate decomposition but do not supply a native source inverse.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-030`; exact cover components act scalarly or trivially on the visible elliptic factor.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`; an extra elliptic factor still lacks a useful native-prime off-deck correspondence.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact component/value matrices retain full source rank.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; full character/phase information does not construct exact source provenance.

## Closest primary literature

- Mackey, [Induced representations of locally compact groups I](https://doi.org/10.2307/1969423), develops induction/restriction structure underlying the double-coset decomposition.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives exact elliptic endpoint relations without an induced-representation source dictionary.

No checked primary source constructs the proposed nonhomomorphic double-coset correspondence or a canonical factor-occurrence lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, `B=N^(1/5)` signed factor decks, groups `G,H,K`, correspondence, representation conventions, double-coset representatives, restrictions, masks, and verifier.
2. Build target-independent induced/restricted representation state, double-coset decomposition, and intertwiners within `B^(9/4+o(1))`, without scalar labels or one basis vector per source tuple.
3. For known-log targets, project the endpoint constraint into components, solve compatible local constraints, recombine them, lift one result to five occurrence-labelled factors, and verify the signed group sum.
4. Collect at least `B` independent verified rows, charging empty/spurious components, multiplicities, ambiguity, duplicate/dependent rows, and output; solve factor logs and verify them.
5. Apply the unchanged correspondence, components, and lift to fresh scalar-blind `Q+[t]P`, with restrictions frozen prospectively and all target-specific rebuilding charged.
6. Recover factor occurrences, substitute verified factor logs, remove `t`, retain component ambiguity, and verify `[x]P=Q`.
7. Charge correspondence construction, induction/restriction, double-coset enumeration, intertwiners, component solves, source lift, output, rank, logs, descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

For a prime-order elliptic group, useful proper subgroup structure is absent; any fine double-coset partition of factor points is likely defined by the scalar labels being sought. Homomorphic/isogeny correspondences preserve the known same-field transfer obstruction, while a genuinely nonhomomorphic correspondence has no representation law guaranteeing that component solutions preserve elliptic addition. Mackey decomposition reorganizes a supplied representation but does not invert its basis vectors to factor occurrences. This merges with IDEAs 010, 043, 099, 127, and 261 unless a public nonhomomorphic source correspondence is constructed.

## Proof track

Construct the nonhomomorphic correspondence, prove a double-coset/source biconditional and canonical inverse on every stratum, bound all component dimensions, and derive complete exponents at most `0.45`.

## Disproof track

Show the double-coset labels reveal or require discrete logs, the correspondence is homomorphic/scalar/trivial, two source tuples share every component transcript, or component construction exceeds the state/query gates.

## Positive and negative controls

- Positive: supplied finite-group induction examples with known `H,K` double cosets and labelled basis vectors must decompose, recombine, and source-lift exactly.
- Negative: cyclic prime-order groups, scalar-labelled cosets, homomorphic/isogeny correspondences, shuffled basis labels, equal-character/different-source instances, arbitrary restrictions, all signed strata, and blind targets.
- Baselines: IDEAs 010/043/099/127/261, character transforms, same-field isogenies, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a public nonhomomorphic correspondence, exact source lift, no hidden scalar labels, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one scalar-defined coset, homomorphic/scalar action, component/source collision, missing signed stratum, source-sized basis/intertwiner construction, or either exponent at least `0.50`.
- A correct Mackey identity, character match, or toy representation decomposition is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-391/double_coset_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-391/scalar_label_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-391/component_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-391/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic source decomposition, not Mackey theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a representation identity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-391/double_coset_source_obligations.md` and identify whether each proposed double-coset label is computable without a factor discrete logarithm.
