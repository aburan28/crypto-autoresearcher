# ECDLP-IDEA-178 — Moufang-associator ancestry transgression

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `none`
- State: `rejected_scoped_one_generated_homomorphic_moufang_lift`
- Cohort: `20260718-c`
- Evidence scale: scoped structural argument and primary-literature audit only; no theorem receipt or experiment exists
- Contract posture: rejected scoped evidence; no contract or run is authorized
- Scale labels: any finite check would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero associator, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A public alternative/Moufang lift of elliptic addition has an endpoint-computable normalized associator whose value retains bracket and source ancestry. Inverting those associators returns every exact signed factor-base word for known and masked target endpoints in sub-rho time and memory.

## Mechanism-new operation

The operation is **Moufang associator transgression followed by exact ancestry inversion**. Unlike IDEA-167's quasigroup-isotope normal form, this requires a nonzero scalar-blind associator, not a rewritten endpoint normalizer. It qualifies only if public endpoints determine associator data without a source word and the inverse returns all exact bracketed sources.

Independent review narrows the negative scope to a one-generated homomorphic lift. A
general nonhomomorphic section can introduce independent fiber generators, so
diassociativity alone does not prove that every scalar-compatible lift is one-generated.
Such a section remains outside scope but must provide its public canonical choice and
exact source inverse rather than assuming them.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, a Moufang lift, normalization, masks, and verifier are frozen.
2. Projection from the lift to `<P>` respects elliptic addition on every declared chart.
3. Normalized associators are nonzero and distinguish bracket/source ancestry without scalar labels.
4. Associator inversion returns all signed sources, multiplicities, and exceptional strata without a source table.
5. Lift construction, branches, output, rank, factor logs, descent, verification, time, and memory are charged.

## Semantic fingerprint

`public_Moufang_lift | normalized_associator_transgression | bracket_source_ancestry | exact_word_inverse | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the exact ancestry edge barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the explicit orientation-label control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the known-difference state no-promotion result.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the materialized serial-state source boundary.

## Closest primary literature

- Kinyon, Kunen, and Phillips, [A Generalization of Moufang and Steiner Loops](https://arxiv.org/abs/math/0105015), proves the nearby diassociativity theorem for ARIF loops, including Moufang loops.
- Wells, [Moufang loops arising from Zorn vector matrix algebras](https://eudml.org/doc/37767), supplies explicit nonassociative Moufang constructions but no elliptic endpoint/source inverse.

The checked primary sources expose the cyclic two-generator obstruction and do not supply this descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the lift, projection, associator normalization, factor base, masks, branch order, and verifier.
2. Lift known-log endpoints `R_j=[r_j]P` without scalar labels or supplied decompositions.
3. Compute normalized associator transcripts and invert each transcript to every signed factor-base word.
4. Verify all words; preserve bracketings, collisions, repeats, infinity, misses, and complete output.
5. Collect rank `B`, solve factor-base logs, and independently verify every recovered log.
6. Apply the identical lift and inverse to fresh masked targets `Q+[t]P`.
7. Substitute verified logs, remove masks, retain every ambiguity candidate, and verify `[x]P=Q`.
8. Charge lift construction, transcripts, inversion branches, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let lift setup cost `N^a,N^a_m`, reciprocal relation and target densities be `N^delta,N^delta_t`, associator inversion cost `N^q,N^q_m`, output and target ambiguity be `N^o,N^u`, and factor-log algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents; every lift fiber, bracketing, and emitted word is charged.

## Likely fatal obstruction

Moufang loops are diassociative: any two generated elements lie in an associative subloop. In the scoped one-generated homomorphic lift of `<P>`, every relevant associator is therefore zero and records no ancestry. A general nonhomomorphic section may introduce independent fiber generators; it is not closed by this argument, but its public choice and orientation become new charged operations and may restore the missing source data.

## Proof track

An outside-scope successor must construct a scalar-blind noncyclic lift, prove nonzero endpoint-computable associators and a complete exact word inverse, and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Apply diassociativity to the lifted cyclic subgroup, prove all relevant associators vanish, or show that any nonzero refinement requires source labels, `N` states, incomplete recall, or an exponent at least `0.5`.

## Positive and negative controls

- Explicit Zorn-matrix Moufang loops with known nonzero three-generator associators.
- Cyclic subloops and two-generator words, where associators must vanish.
- IDEA-167 isotope normalization and direct ancestry-label controls.
- Exhaustive toy fibers, rho, BSGS, known-log, and blind-target checks.

## Quantitative promotion and falsification gates

This version is rejected in the scalar-compatible cyclic scope. Reopening requires a theorem giving 100% source and multiplicity recall, zero false words, no scalar-oriented advice, and formal `lambda,mu<=0.45`. Zero cyclic associators, one lost source, an `N`-state lift, or either exponent at least `0.5` is falsifying.

## Artifact plan

- Prospective scoped structural argument: `ideas/artifacts/ECDLP-IDEA-178/moufang_diassociativity_no_go.md`
- Prospective lift specification: `ideas/artifacts/ECDLP-IDEA-178/moufang_lift_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-178/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-178/cost_analysis.md`

All paths are prospective; no artifact, contract, or experiment was created.

## Interpretation boundary

This is a scoped structural negative, not an existing theorem receipt, and remains novelty-unverified outside the one-generated homomorphic scope. Finite checks are toy and projections heuristic and model-bound. Associator correctness or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-178/moufang_diassociativity_no_go.md` proving the cyclic two-generator associator vanishes and itemizing the source labels needed by any nonzero lift.
