# ECDLP-IDEA-173 — Gain-graph switching-potential descent

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `high_risk`
- Top lane: `none`
- State: `deferred_needs_public_balanced_gain_and_source_inverse_theorem`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: every future finite check is `toy`; all projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a balanced gain graph, switching potential, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Partial elliptic-sum transitions lift target-uniformly to a compact public gain graph over a nonabelian or group-valued label system. Switching to a balanced canonical representative yields vertex potentials that invert biconditionally to exact signed factor-base points, providing complete relations and masked target descent below rho and BSGS without discrete logs or an explicit edge deck.

## Mechanism-new operation

The operation is **public gain lifting of partial-sum transitions followed by balanced switching-potential source inversion**. Removal requires explicit coordinate-to-gain and potential-to-source maps, cycle balance, canonical switching, and compact evaluation without logs or source edges. Gains in `Z/NZ` computed by DLP, supplied potentials, explicit `B^2/B^3` transition decks, or post-hoc switching are controls.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, transition schema, gain group, switching convention, masks, and verifier are frozen.
2. Edge gains are computed from public coordinates without scalar labels, source tuples, or materialized pair/triple decks.
3. Relevant cycles are balanced and admit a canonical target-uniform switching potential on every declared stratum.
4. Potentials invert exactly to all signed factor points and compose to complete source tuples with sub-rho ambiguity.
5. Gain construction, switching, output, rank, logs, descent, verification, and peak bit memory are charged.

## Semantic fingerprint

`partial_elliptic_sum_transitions | public_group_valued_gain_lift | balanced_cycle_switching | canonical_vertex_potentials | exact_factor_source_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, where direct labels do not promote.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1411-SEGMENTED-DIRECTORY-NO-PROMOTION`, the segmented source-directory boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, where differential transition state remains insufficient.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the closest held-out transition/source representation boundary.

## Closest primary literature

- Zaslavsky, [Biased graphs. I. Bias, balance, and gains](https://doi.org/10.1016/0095-8956(89)90063-4), gives gain labels, balance, and switching structure but no elliptic source inverse.
- Zaslavsky, [Biased graphs IV: Geometrical realizations](https://doi.org/10.1016/S0095-8956(03)00035-2), gives canonical gain-graph representations, not target-local factor-point potentials.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives nearby partial-sum relation equations but no balanced gain lift.

No checked primary source supplies the proposed public gain and source-return pipeline; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the partial-sum graph, gain group, coordinate gain formula, cycle orientation, switching normalization, masks, and verifier.
2. Prove compact endpoint-only gain evaluation, cycle balance, and canonical switching without scalar labels or source edges.
3. For known `R_j=[r_j]P`, compute reachable switched potentials and invert each to exact signed factor points.
4. Compose point labels into complete tuples; preserve unbalanced cycles, gauge ambiguity, collisions, misses, and output.
5. Verify sums, collect `B+sigma` independent relation rows of rank `B`, solve factor logs, and verify every log.
6. Apply the identical gain construction and switching to fresh `Q+[t]P` masks.
7. Substitute factor logs, remove masks, retain every gauge/source candidate, and accept only `x` with `[x]P=Q`.
8. Charge graph construction, gains, cycle tests, switching, source inversion, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let gain/graph setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one switching plus source inversion query cost `N^q,N^q_m`; output and gauge/target ambiguity exponents be `o,u`; and factor-log algebra cost `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every edge generated, gain word, cycle check, gauge representative, source label, and failed endpoint is included.

## Likely fatal obstruction

Useful additive gains in `Z/NZ` are scalar differences, so deriving them from elliptic coordinates is DLP. Gains computed directly from coordinates generally lack the path-product law and balanced cycles needed for switching potentials. Restoring balance by listing pair or triple transitions materializes the forbidden `B^2/B^3` source graph.

## Proof track

Specify a nonlogarithmic compact gain group and coordinate formula; prove balance, canonical switching, all-strata potential/source inversion, and complete blind descent with `lambda,mu<=0.45`.

## Disproof track

Reduce gains or switching to DLP, exhibit an unbalanced coordinate cycle, find source-distinct vertices with equal potentials, expose explicit `B^2/B^3` edges, or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Published balanced gain graphs with independently known switching functions.
- Synthetic elliptic transition graphs supplied with scalar-difference gains.
- Coordinate-only labels tested for cycle imbalance and gauge collisions.
- Explicit pair/triple decks, direct logarithmic potentials, rho, BSGS, known-log, and blind-target controls.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires explicit public gain, balance, switching, exact source-inverse, and formal `lambda,mu<=0.45` theorems before any run. A later approved toy preflight needs 100% source recall, zero false potentials, zero unexplained unbalanced cycles, no scalar advice, and complete ambiguity charging. One DLP-valued gain, lost source, explicit deck, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Prospective gain and balance theorem: `ideas/artifacts/ECDLP-IDEA-173/gain_balance_theorem.md`
- Prospective switching/source specification: `ideas/artifacts/ECDLP-IDEA-173/switching_source_inverse_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-173/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-173/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-173/cost_analysis.md`

All paths are prospective; no artifact, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is deferred, high-risk, novelty-unverified representation research. Finite checks would be toy and every complexity projection is heuristic and model-bound. Balance or relation correctness is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-173/gain_balance_theorem.md` specifying one coordinate-derived gain law and either proving cycle balance plus nonlogarithmic source return or recording the first typed obstruction; do not build an edge deck.
