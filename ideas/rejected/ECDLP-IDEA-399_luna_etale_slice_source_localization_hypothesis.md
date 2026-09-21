# ECDLP-IDEA-399 — Luna étale-slice source localization

## Status and claim labels

- Class: `etale_slice_quotient_localization`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_slice_requires_supplied_action_and_local_quotient_lift_does_not_return_factor_occurrences`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid étale slice or quotient chart is not an ECDLP break.

## Falsifiable hypothesis

The permutation quotient of signed relation tuples admits an endpoint-constructible Luna étale slice near each target orbit, and its transverse coordinates plus stabilizer data give an exact restriction-stable lift to occurrence-labelled factor points below rho and BSGS.

## Mechanism-new operation

The screened operation is **replace a reductive action near a closed orbit by an associated bundle `G x^H S`, pass through the étale quotient `S//H`, and invert the slice coordinates to one labelled source tuple**. The proposed gain is local quotient localization rather than a new invariant list or dense elimination backend.

## Assumptions

1. A public reductive action models every source permutation, sign, and exceptional stratum.
2. Closed-orbit representatives, stabilizers, and transverse slices are endpoint-constructible and target-uniform.
3. Slice quotient points lift canonically to exact factor occurrences under arbitrary deck restrictions.
4. The finite atlas and transition data fit the setup/query caps without listing orbit points or roots.
5. Action construction, slice equations, transitions, inverse lift, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`symmetric_relation_quotient | Luna_etale_slice_localization | stabilizer_transverse_coordinates | quotient_point_to_occurrence_source_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact endpoint membership still needs a source-return interface.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; a representation must be constructed without source-indexed advice.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; full-rank transforms do not yield compression.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; quotient phase and orientation remain charged.
5. `inputs/ledger_inventory.json` — imported `P1479`; every restriction and source occurrence must survive the representation change.

## Closest primary literature

- Luna, [Slices étales](https://doi.org/10.24033/msmf.110), proves the local slice theorem for supplied reductive actions near closed orbits.
- Alper, Hall, and Rydh, [A Luna étale slice theorem for algebraic stacks](https://doi.org/10.4007/annals.2020.191.3.4), extends the local quotient framework under stated hypotheses, without a canonical point section.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives symmetric relation equations but no slice-to-factor inverse.

No checked source constructs the proposed endpoint-only action, finite slice atlas, and labelled inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, action, orbit convention, slice atlas, stabilizers, transitions, restrictions, and verifier.
2. Build the target-independent quotient and slice atlas within `B^(9/4+o(1))`, without orbit/source enumeration.
3. For known-log targets, decide exact restricted existence in a slice, lift through `S//H`, undo stabilizer ambiguity to one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging empty charts, overlaps, ambiguity, output, and dependent rows; solve and verify factor logs.
5. Reuse the unchanged atlas for fresh scalar-blind `Q+[t]P` targets and all restrictions.
6. Substitute factor logs, remove `t`, retain all slice and stabilizer branches, and verify `[x]P=Q`.
7. Charge action/atlas construction, quotient queries, transitions, lift, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Luna's theorem starts from a supplied action and is local around a chosen closed orbit. The slice and stabilizer are noncanonical up to equivariant choices, while passing to the quotient deliberately forgets which roots and occurrences formed the tuple. Refinement sufficient for exact arbitrary-restriction lifting reconstructs the orbit/root deck. This meets IDEAs 075, 094, 246, 261, and 334 at the invariant-quotient section boundary.

## Proof track

Construct a uniform public action and complete finite slice atlas, prove exact source-biconditional lifting across overlaps and restrictions, and certify `lambda,mu<=0.45`.

## Disproof track

Exhibit two occurrence-labelled tuples with the same slice quotient, show one required orbit/slice choice is source-bearing, or prove atlas/transition/lift growth above the caps.

## Positive and negative controls

- Positive: supplied reductive actions with labelled closed orbits and explicit slices must replay quotient and lift maps.
- Negative: equal quotient points with permuted roots, nonclosed orbits, stabilizer ambiguity, chart overlaps, all signed strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 075/094/246/261/334, explicit orbit tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only action and atlas, exact occurrence lift, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one supplied orbit/slice datum, quotient collision, missing chart or stratum, cap violation, or either exponent at least `0.50`.
- A correct toy slice computation is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-399/luna_slice_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-399/quotient_lift_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-399/slice_transition_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-399/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic slice-localization route, not Luna's theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; quotient correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-399/luna_slice_source_obligations.md` and classify the action, orbit, stabilizer, slice, transitions, and lift by endpoint versus source dependence.
