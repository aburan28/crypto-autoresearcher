# ECDLP-IDEA-184 — Munn inverse-semigroup source idempotents

## Status and claim labels

- Class: `representation`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_source_domain_dictionary_scoped_negative`
- Cohort: `20260718-d`
- Evidence scale: primary-literature and semantic preflight only; no experiment ran
- Contract posture: no contract warranted after the source-domain reduction
- Scale labels: every prospective finite check is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct inverse-semigroup representation, idempotent, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Partial elliptic-addition maps restricted to factor-base-compatible domains generate a finite inverse semigroup whose idempotent semilattice records admissible source domains. The Munn representation or its idempotent spectrum then separates and reconstructs every exact factor-base source of a public endpoint without source enumeration, supporting rank-complete relations and blind masked descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **partial-addition inverse-semigroup generation followed by Munn idempotent-domain source separation**. It is mechanism-new only if public endpoint partial maps determine compact idempotents whose domains identify all exact signed sources without storing those domains point by point. Building the inverse semigroup from supplied source maps, changing its representation algorithm, or listing all factor-base domains is a control.

Semantic review found that the Munn representation faithfully acts on principal ideals of the idempotent semilattice, but the separating idempotents are precisely domain predicates for the partial source maps. Encoding them finely enough to distinguish same-endpoint source tuples is a source-domain dictionary; coarser endpoint idempotents merge provenance. The version is merged/rejected at this representation boundary while leaving inverse-semigroup theory intact.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, signed-source arity, partial-map convention, masks, and verifier are frozen.
2. A scalar-blind finite inverse semigroup is constructed from public elliptic endpoints without enumerating factor-base tuples.
3. Its idempotent semilattice handles signs, repetition, infinity, exceptional domains, and multiplicities exactly.
4. Munn action or spectrum returns all exact source points for each endpoint with no source-indexed advice.
5. Domain construction, semigroup closure, idempotents, representation, output, failed trials, rank, descent, verification, time, and memory are charged.

## Semantic fingerprint

`partial_elliptic_addition_inverse_semigroup | Munn_idempotent_semilattice | exact_source_domain_separation | no_source_dictionary | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the direct source-label control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1411-SEGMENTED-DIRECTORY-NO-PROMOTION`, the segmented source-directory boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, where differential state retains charged provenance.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the nearest compact state/source-identification boundary.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.

## Closest primary literature

- Munn, [Matrix Representations of Inverse Semigroups](https://doi.org/10.1112/plms/s3-14.1.165), develops representations controlled by the idempotent structure of inverse semigroups.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides public elliptic endpoint relations but not a compact source-domain semilattice.

Neither checked primary source supplies the proposed endpoint-to-idempotent compiler, exact source extraction, or complete sub-rho descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta`, partial elliptic-addition generators, domain and idempotent encodings, signs, arity, masks, and an independent verifier.
2. Construct from each known-log endpoint `R_j=[r_j]P` the same scalar-blind inverse-semigroup element without using `r_j` or its source tuple.
3. Compute the Munn action or idempotent spectrum and emit every exact signed factor-base source domain and tuple for that endpoint.
4. Verify membership and elliptic sum; preserve equal partial maps, domain collisions, repeats, infinity, multiplicities, misses, and false tuples.
5. Collect at least `B+sigma` independently verified rows of rank `B`, solve factor-base logarithms, and verify every log by scalar multiplication.
6. Apply the identical semigroup construction and representation to fresh masked targets `Q+[t]P`.
7. Substitute verified factor logs, remove masks, retain all ambiguity candidates, and accept only `x` satisfying `[x]P=Q`.
8. Charge generator and closure setup, all domain bits and idempotents, Munn maps, failed queries, source output, rank, linear algebra, descent, verification, time, and peak bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let semigroup, closure, and idempotent setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one Munn/source query cost `N^q,N^q_m`; source output and target ambiguity be `N^o,N^u`; and factor-log linear algebra cost `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every semigroup element, domain bit, idempotent, principal ideal, collision branch, output tuple, and failed endpoint is charged; representation faithfulness is not free source recovery.

## Likely fatal obstruction

Munn faithfulness distinguishes inverse-semigroup elements by how they transport idempotents, but exact elliptic sources are not determined by the endpoint partial map. To separate two same-endpoint tuples, the idempotent semilattice must contain different predicates for their source domains. Materializing those predicates is a source-domain dictionary, with up to `B^m` distinct domains at arity `m`; compressing them by endpoint merges the provenance required for factor-base rows.

## Proof track

Define a target-uniform finite inverse semigroup from endpoint data, prove its compact idempotent spectrum is source-biconditional on all strata without a source dictionary, and establish complete rank and blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Find two distinct exact sources inducing the same endpoint semigroup element and idempotent action, prove any separating semilattice needs source-indexed domains of size `B^m`, find one lost multiplicity, or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Positive: finite inverse semigroups with explicitly supplied partial maps and independently known idempotent domains.
- Positive: exhaustive toy elliptic partial maps built from a deliberately enumerated source fiber.
- Negative: the group completion, whose trivialized idempotents preserve endpoint composition but erase source domains.
- Negative: explicit segmented domain directories, hash-colliding compressed domains, solver substitutions, rho, BSGS, known-log leakage, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected at compact idempotent separation. A successor under a new ID requires 100% source/multiplicity recall, zero false tuples, no source-indexed domain directory, exact handling of every exceptional partial domain, verified rank `B`, successful blind masked descent, and formal `lambda,mu<=0.45`. Values in `(0.45,0.50)` are inconclusive; one indistinguishable source pair, hidden domain deck, or either exponent at least `0.50` falsifies the scoped successor. Semigroup correctness alone cannot promote it.

## Artifact plan

- Partial-addition semigroup specification: `ideas/artifacts/ECDLP-IDEA-184/partial_addition_semigroup_spec.md`
- Idempotent separation lower-bound audit: `ideas/artifacts/ECDLP-IDEA-184/idempotent_domain_audit.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-184/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-184/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-184/cost_analysis.md`

All paths are prospective. No artifact directory, contract, or run exists.

## Interpretation boundary

This is a novelty-unverified representation-changing scoped negative: exact separating idempotents merge with an existing source-directory obstruction. Any finite evidence would be toy, and all cost projections remain heuristic and model-bound. No inverse-semigroup identity or relation constitutes a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-184/idempotent_domain_audit.md` proving or refuting that a bounded public idempotent semilattice can separate all same-endpoint factor-base source domains without storing a source-indexed dictionary.
