# ECDLP-IDEA-224 — Wavelet-scattering source inverse

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_invariant_scattering_loses_phase_and_requires_relation_signal`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; stable scattering coefficients, phase recovery, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-defined relation indicator on a public group or graph has a multiscale wavelet-scattering transform whose bounded paths preserve exact signed source identities while quotienting irrelevant translations. A canonical scattering inverse would yield relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **nonlinear modulus-wavelet propagation followed by exact source-phase inversion**. It merges/rejects in the admitted bounded invariant/averaged model because modulus and averaging identify phase/translation orbits. This is not a universal noninjectivity claim for every scattering transform. Constructing the input relation signal already enumerates source events; retaining enough paths and phases for exact inversion in this model restores the full coefficient/source payload.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, domain, wavelets, paths, and masks are frozen.
2. The endpoint signal is computable without materializing relation rows or a scalar orbit table.
3. Bounded scattering coefficients invert exactly to every signed point, sign, repeat, and multiplicity.
4. Signal construction, convolutions, paths, phases, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_relation_signal | multiscale_group_wavelets | modulus_scattering_paths | exact_phase_and_source_inverse | factor_logs | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full value-matrix rank boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the phase-rank and nonlinear-gap control.
3. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate compression gap.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1407-NO-PROMOTION`, the predicate-compression negative.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing relation signal/source generator.

## Closest primary literature

- Mallat, [Group invariant scattering](https://arxiv.org/abs/1101.2286), constructs stable invariant coefficients through wavelet modulus and averaging.
- Bruna and Mallat, [Invariant scattering convolution networks](https://arxiv.org/abs/1203.1513), develops the finite scattering cascade and its retained information.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies elliptic endpoint relations but not a sparse source signal or phase inverse.

No checked source proves source-complete scattering for an implicit elliptic relation signal. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the signal domain, wavelets, paths, averaging, phase inverse, masks, and verifier.
2. Build the endpoint signal without enumerating source tuples; compute all charged scattering coefficients.
3. Invert accepted coefficients to every exact signed factor point and independently verify each relation.
4. Collect full rank, solve and verify factor-base logarithms.
5. Repeat unchanged for fresh `Q+[t]P`, invert target coefficients, substitute logs, and subtract `t`.
6. Preserve phase/translation ambiguity and accept only `[x]P=Q`, charging signal, paths, output, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, scattering plus exact inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every signal entry, wavelet path, phase tag, and recovered source is charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

For the admitted bounded invariant/averaged transform, modulus and averaging identify phase/translation orbits, while exact elliptic ancestry is carried by those discarded coordinates. Its coefficients cannot create a sparse relation signal that was not already computed. A source-complete inverse in this model needs all phases or an injective path family whose size tracks the original signal/source deck; transforms outside this frozen model are not covered by the rejection.

## Proof track

Prove endpoint-only signal construction and injective bounded-path scattering with an exact all-source inverse and `lambda,mu<=0.45`.

## Disproof track

Exhibit distinct source signals with identical admitted coefficients, prove phase/path count reaches source size, or show signal construction enumerates the relation fiber.

## Positive and negative controls

- Positive control: planted sparse signals with supplied phases and independently invertible wavelet frames.
- Negative controls: phase scrambling, translation pairs, coefficient averaging, IDEA-048/110/124/155, explicit relation tensors, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires 100% source recall and zero false sources under the frozen invariant/averaged path set, no materialized relation signal, path/phase state exponent at most `0.45`, and complete `lambda,mu<=0.45`. One collision under that admitted transform or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-224/scattering_source_inverse_theorem.md`
- Prospective collisions: `ideas/artifacts/ECDLP-IDEA-224/scattering_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-224/independent_scattering_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-224/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. Scattering stability, phase recovery on a planted signal, relation validity, or a toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-224/scattering_source_inverse_theorem.md` proving injectivity on endpoint-derived relation signals or preserving a same-coefficient/different-source collision with all phase paths charged.
