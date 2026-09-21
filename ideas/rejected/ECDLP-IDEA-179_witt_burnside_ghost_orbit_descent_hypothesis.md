# ECDLP-IDEA-179 — Witt-Burnside ghost-orbit descent

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `none`
- State: `rejected_scoped_unlabelled_regular_prime_cyclic_marks`
- Cohort: `20260718-c`
- Evidence scale: scoped prime-cyclic mark argument and primary literature only; no theorem receipt or experiment exists
- Contract posture: rejected scoped evidence; no contract or run is authorized
- Scale labels: any finite check would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; valid ghost coordinates, marks, or toy scalar recovery is not an ECDLP break.

## Falsifiable hypothesis

Each public elliptic endpoint determines a target-conditioned almost-finite cyclic action object. Dress-Siebeneicher ghost/mark coordinates followed by Möbius inversion recover scalar-orbit digits and exact signed factor-base source orbits, enabling complete relation collection and masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **endpoint-to-almost-finite-action encoding followed by ghost-mark inversion to exact source orbits**. It is not the Witt-Kummer symbol of IDEA-162 or the block-monoid transfer of IDEA-166. An explicit scalar-indexed orbit table, generator orientation directory, or solver substitution is a control.

Independent review confirms only the unlabelled regular-action scope. Richer
endpoint-conditioned action objects are not closed by the identical-mark argument, but
their endpoint construction and source inverse are precisely the missing new operations.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, cyclic action category, ghost map, masks, and verifier are frozen.
2. A target-conditioned almost-finite action object is built from endpoint coordinates without a scalar label.
3. Its marks distinguish every nonzero translation scalar and all exact source-orbit digits.
4. Möbius inversion returns all signed sources and multiplicities without materializing `N` states.
5. Object construction, ghost coordinates, inversion, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_conditioned_almost_finite_action | Witt_Burnside_ghost_marks | Mobius_orbit_inversion | exact_source_orbits | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the direct scalar-orientation label control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1411-SEGMENTED-DIRECTORY-NO-PROMOTION`, the complete orientation-directory boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1417-CRT-QUOTIENT-NO-PROMOTION`, the exact quotient-action no-promotion result.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the large known-scalar orbit no-compression result.
5. `inputs/ledger_inventory.json` — imported `P1479`, the public-feature scalar-orientation boundary.

## Closest primary literature

- Dress and Siebeneicher, [The Burnside ring of profinite groups and the Witt vector construction](https://doi.org/10.1016/0001-8708(88)90052-7), constructs the governing Burnside-Witt and ghost framework.
- Elliott, [Constructing Witt–Burnside rings](https://doi.org/10.1016/j.aim.2005.04.014), realizes these rings using almost-finite group sets with orbit-constant labels.

Neither checked primary source makes isomorphic regular prime-cyclic actions remember generator orientation or elliptic source ancestry; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the action category, endpoint encoding, ghost coordinates, inversion order, factor base, masks, and verifier.
2. Build the action object for each known `R_j=[r_j]P` without `r_j`, a source tuple, or an orbit directory.
3. Compute all charged marks and apply Möbius inversion to emit every signed factor-base source orbit.
4. Verify all tuples; preserve orbit isomorphisms, collisions, repeats, infinity, misses, labels, and output.
5. Collect rank `B`, solve factor-base logs, and independently verify every recovered log.
6. Apply the identical object construction and ghost inverse to fresh `Q+[t]P` masks.
7. Substitute verified logs, remove masks, retain every candidate, and verify `[x]P=Q`.
8. Charge object construction, marks, inversion, labels, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let action setup cost `N^a,N^a_m`, reciprocal relation and target densities be `N^delta,N^delta_t`, ghost inversion cost `N^q,N^q_m`, output and ambiguity be `N^o,N^u`, and factor-log algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These complete exponents charge every orbit representative, subgroup mark, coefficient, and emitted source.

## Likely fatal obstruction

For prime `N`, every nonzero translation action of `C_N` on itself is a regular `N`-cycle and all such actions are isomorphic. Their subgroup marks and hence Witt-Burnside ghost coordinates are identical, so they reveal orbit type but not the nonzero scalar. Distinguishing translations requires a chosen generator/orientation or `N` labeled states, relocating the DLP and source table.

## Proof track

An outside-scope successor must exhibit a scalar-blind nonisomorphic endpoint action family, prove injective sub-rho ghost inversion to all exact sources, and derive complete `lambda,mu<=0.45` descent.

## Disproof track

Classify prime-cyclic transitive actions, compute their identical marks, or show any separating refinement uses an orientation label, explicit `N`-state table, incomplete recall, or exponent at least `0.5`.

## Positive and negative controls

- Small nonisomorphic finite-group actions whose mark vectors do separate orbit types.
- Nonzero regular `C_N` translation actions under changed generator labels.
- Explicit scalar-oriented orbit tables and IDEA-162/166 controls.
- Exhaustive toy marks, rho, BSGS, known-log, and blind-target checks.

## Quantitative promotion and falsification gates

This version is rejected for prime-order translation actions. Reopening requires five scalar-distinct public endpoints with provably distinct scalar-blind marks, exact all-source inversion, no `N`-state advice, and formal `lambda,mu<=0.45`. Isomorphic mark vectors, one lost source, or either exponent at least `0.5` is falsifying.

## Artifact plan

- Prospective scoped mark argument: `ideas/artifacts/ECDLP-IDEA-179/prime_cyclic_mark_no_go.md`
- Prospective action specification: `ideas/artifacts/ECDLP-IDEA-179/action_object_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-179/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-179/cost_analysis.md`

All paths are prospective; no artifact, contract, or experiment was created.

## Interpretation boundary

This is scoped rejected evidence and novelty-unverified outside that scope. Finite calculations are toy and projections heuristic and model-bound. Ghost-map correctness or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-179/prime_cyclic_mark_no_go.md` classifying the nonzero translation actions and proving their ghost/mark vectors cannot encode scalar orientation without `N` states.
