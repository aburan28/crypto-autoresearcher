# ECDLP-IDEA-161 — Rigidified N-primary theta return

## Status and claim labels

- Class: `arithmetic-geometry`
- Risk band: `high-risk-theorem-gated`
- Top lane: `none`
- State: `deferred_needs_nonsplit_class_canonical_section_and_typed_return`
- Cohort: `20260718-b`
- Evidence scale: literature and semantic audit only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: any finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; theta coordinates, a central-extension class, a relation, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

An explicitly `N`-primary nonsplit theta/Heisenberg extension attached to the public elliptic subgroup admits a canonical scalar-blind section. Its commutator and rigidified return map convert endpoint data into exact signed factor-base atoms or typed scalar equations without a full `N`-torsion dictionary, enabling complete relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The operation is **canonical rigidification of an `N`-primary theta extension followed by a typed same-group return**. IDEA-145 closes coprime-center split or gauge-removable extensions; this candidate occupies only its explicit `N`-primary exception. A theta embedding without a canonical section, a pairing value requiring a second DLP, or a solver change is a control.

## Assumptions

1. Public `E/F_p,P,N,Q,F,B=N^beta` and a line bundle/theta group of `N`-primary type are frozen.
2. The central extension is genuinely nonsplit on the admitted subgroup and constructible without hidden scalar coordinates.
3. A canonical section is invariant under presentation choices and returns exact source atoms or a typed scalar equation.
4. The full torsion field, representation dimension, commutator output, ambiguity, and inversion remain sub-rho.
5. Setup, failed relations, rank, factor logs, masked descent, verification, and memory are charged.

## Semantic fingerprint

`N_primary_theta_extension | public_canonical_rigidification | nonsplit_commutator_signal | typed_source_or_scalar_return | complete_blind_descent`

The novelty gate is the canonical section plus typed return; `mu_N` data without inversion is relation-only evidence.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1474`, the CM-stable sparse-deck control.
2. `inputs/ledger_inventory.json` — imported `P1479`, where public features do not contain factor-log orientation.
3. `inputs/ledger_inventory.json` — imported `ECFG-H664`, the nearest character/orientation hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1425-BOUNDED-PHASE-LIFT-NO-PROMOTION`, where bounded phase lifts fail to encode membership.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-005`, a nearby transfer/typed-return obstruction.

## Closest primary literature

- Mumford, [On the equations defining abelian varieties I](https://doi.org/10.1007/BF01389737), supplies theta groups and addition structure, not the proposed canonical `N`-primary return.
- Boneh and Silverberg, [Applications of multilinear forms to cryptography](https://eprint.iacr.org/2002/080), gives the multilinear-map boundary rather than a self-returning ECDLP map.
- Cheon, [Security analysis of the strong Diffie-Hellman problem](https://doi.org/10.1007/s00145-009-9047-0), shows auxiliary-power tradeoffs but not a public theta source decoder.

No checked primary source supplies the complete operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the theta group, extension class, section normalization, factor base, masks, exceptional charts, and verifier.
2. Prove nonsplitting and canonical construction without enumerating `E[N]` or scalar labels.
3. For known `R_j=[r_j]P`, compute the rigidified invariant and invert every output to exact signed factor-base tuples.
4. Verify all tuples directly; retain section ambiguity, commutator collisions, multiplicity, infinity, and failures.
5. Collect rank `B`, solve and independently verify factor-base logarithms.
6. Apply the identical invariant to fresh `Q+[t]P` masks.
7. Substitute factor logs, remove `t`, keep all candidates, and verify `[x]P=Q`.
8. Charge torsion fields, theta dimensions, outputs, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let theta setup cost `N^a,N^a_m`, reciprocal relation/target densities `N^delta,N^delta_t`, invariant plus typed inversion `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Full torsion-field degree and theta representation size are included in `a,a_m`.

## Likely fatal obstruction

`N`-primary theta data naturally needs an `N`-dimensional Heisenberg representation or the full `N`-torsion field. Commutators land in `mu_N`, where extracting the exponent is another DLP, while any canonical section may split the class and erase the proposed signal.

## Proof track

Prove an explicit nonsplit class, canonical public section, typed atom/scalar return, bounded representation, and complete `lambda,mu<=0.45` descent.

## Disproof track

Show the class splits after rigidification, the return is only a `mu_N` DLP, the representation/torsion field has exponent at least `0.5`, or two source fibers share every invariant.

## Positive and negative controls

- Small theta groups with known sections and commutators.
- Coprime-center/gauge-removable IDEA-145 controls.
- Supplied `N`-torsion bases and scalar-labelled theta coordinates as forbidden-advice controls.
- Rho, BSGS, exhaustive toy fibers, and independent scalar verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires the nonsplit-class, canonical-section, typed-return, and cost theorems before code. A later approved toy preflight must recover every source with zero false outputs and formal `lambda,mu<=0.45`. Splitting, return-DLP relocation, hidden torsion advice, or either exponent at least `0.5` falsifies this version.

## Artifact plan

- Theta return theorem: `ideas/artifacts/ECDLP-IDEA-161/n_primary_theta_return_theorem.md`
- Extension/section specification: `ideas/artifacts/ECDLP-IDEA-161/theta_section_spec.md`
- Fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-161/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-161/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-161/cost_analysis.md`

All paths are prospective; no experiment is authorized.

## Interpretation boundary

This is a deferred, novelty-unverified theorem lane. Any eventual computation is toy and every projection heuristic and model-bound. A theta identity or valid relation is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-161/n_primary_theta_return_theorem.md` specifying the nonsplit class, canonical section, and typed return before constructing theta coordinates.
