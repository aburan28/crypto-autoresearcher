# ECDLP-IDEA-284 — Cassels–Tate torsor-orientation decoder

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_pairing_orients_classes_not_source_representatives`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid torsor, Cassels–Tate pairing value, relation, recovered label, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform global lift of each finite-field source fiber to torsor classes in a polarized abelian variety admits a canonical Cassels–Tate orientation whose pairing vector distinguishes one exact factor tuple.  Computing that orientation would decode relations and fresh-target decompositions with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the finite-field source fiber to global torsor classes, evaluate Cassels–Tate pairings against a compact public test basis, and use the resulting orientation to select an exact source representative**.  This is an arithmetic-transfer operation rather than a solver substitution.  Poonen–Stoll's pairing is defined on Shafarevich–Tate classes modulo the maximal divisible subgroup and can detect a polarization-associated class, but it does not canonically name a cocycle representative or finite-field factor tuple.  A lift that assigns distinct classes or pairing vectors to every tuple constructs a source-indexed deck; a compact lift identifies representatives.  The proposal therefore merges with missing-section and full-rank-transform negatives once global lifting, local conditions, test classes, output, and descent are charged.

## Assumptions

1. Public curve data, source equations, and endpoint canonically produce a global field, polarized abelian variety, and torsor lift without knowing a source tuple.
2. Source tuples map injectively to computable nondisible torsor classes, rather than to representatives of the same class.
3. A compact target-independent test basis gives a pairing orientation that returns an exact signed factor tuple on every relevant stratum.
4. Global models, local-solubility tests, cocycles, pairing evaluation, ambiguity, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | global_torsor_source_lift | cassels_tate_pairing_orientation | source_representative_decode | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the arithmetic-transfer exact-return boundary.
3. `inputs/ledger_inventory.json` — imported `P1478`, the auxiliary-object construction-cost boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the compact invariant versus source-preimage boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the endpoint-selected representative boundary.

## Closest primary literature

- Poonen and Stoll, [The Cassels-Tate pairing on polarized abelian varieties](https://arxiv.org/abs/math/9911267), gives equivalent definitions of the pairing and criteria involving the polarization-associated class; it does not provide an inverse from a pairing value to a torsor representative.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations and bounded-solution problem whose exact tuple the transfer would have to return.

No checked primary source constructs a target-uniform global torsor lift whose Cassels–Tate orientation selects an ECDLP factor tuple; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, summation-polynomial source equations, global-lift compiler, polarization, local conditions, pairing convention, masks, and verifier.
2. For random known-log endpoints, construct the global torsor instance and its public compact pairing test basis without enumerating source tuples.
3. Evaluate the orientation, decode every accepted class to exact signed factor points, and verify each resulting relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen lift and pairing basis to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode all surviving torsor orientations to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging global lifting, local tests, pairing evaluation, class ambiguity, source output, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one global-lift/pairing/decode attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned torsor/source output be `N^o`, unresolved class-to-representative ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every global coefficient, completion, local condition, cocycle, torsor class, test class, pairing value, failed lift, representative branch, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

The Cassels–Tate pairing is an invariant of global torsor classes, not a section choosing representatives inside a finite-field source fiber.  Distinct factor tuples can induce the same class and hence identical pairing vectors.  Forcing injectivity requires a separate class or test coordinate for the source alphabet, while constructing a global lift from a selected tuple already imports the missing witness.  The pairing can orient or constrain supplied classes but cannot manufacture the endpoint-to-tuple section.

## Proof track

Construct the lift independently of witnesses, prove injectivity from every exact source tuple to a compact pairing vector, prove a canonical inverse returning signed factors on all strata, and certify complete `lambda,mu<=0.45`.

## Disproof track

Exhibit two source tuples with the same torsor class or pairing vector, prove that an injective test basis or global-lift description has exponent at least `0.50`, show that local-solubility/cocycle construction imports the witness, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy global torsor family with explicit cocycles, a known nondegenerate pairing table, and labelled representatives.
- Negative controls: coboundary-changed representatives of one class, locally soluble torsors with identical public pairing rows, permuted source labels, explicit tuple-indexed test classes, materialized source tables, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires witness-free lift construction, injective compact orientation, exact all-strata factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  A class collision, representative dependence, source-indexed input, pairing/output/lift exponent at least `0.50`, missing factor return, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-284/cassels_tate_orientation_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-284/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-284/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-284/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative arithmetic-transfer proposal.  Every finite pairing check would be toy and projections heuristic and model-bound.  A correct lift, pairing value, orientation, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-284/cassels_tate_orientation_theorem.md` proving compact injective representative selection or the class-collision/source-indexing obstruction.
