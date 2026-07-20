# ECDLP-IDEA-071 — Elliptic Cauchy-displacement reporter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_merged`
- Evidence scale: `toy` determinant identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with ideas `013/041/055`
- Breakthrough claim: **none**; a fast determinant or incidence report is not an ECDLP break.

## Falsifiable hypothesis

The Frobenius–Stickelberger addition determinant for factor-base points can be organized
as a Cauchy-like operator of constant displacement rank. Its generators support
output-sensitive target incidence reporting and recursively conditioned minors that
recover every source tuple, collect full-rank factor-base relations, and complete masked
target descent below rho and BSGS in time and memory.

## Mechanism-new operation

The proposed operation was a **constant-displacement elliptic addition operator with
conditioned source unranking**. Literature supplies determinant identities; it does not
show constant displacement rank for the restricted factor-base incidence matrix or avoid
source output. Semantic review found the same locator/reporter operation in rejected
ideas `013`, `041`, and `055`. A faster determinant evaluator changes the query backend,
not relation density or descent.

## Assumptions

1. `E/F_p` has a prime-order subgroup `<P>` of order `N` and a target-independent factor base of size `B`.
2. A complete finite-field Frobenius–Stickelberger identity covers all addition charts and multiplicities.
3. Restricted incidence matrices have bounded displacement rank under a public ordering.
4. Conditioned minors recover source atoms without scanning all rows or pairs.
5. Setup, output, relation density, rank, calibration, target descent, verification, and memory are charged.
6. No explicit pair table, target-selected ordering, or post-hoc reporter is permitted.
7. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`Frobenius_Stickelberger_addition_determinant | Cauchy_displacement_generators | output_sensitive_incidence | conditioned_minor_source_unranking | relation_and_target_descent`

Collision fingerprint: `elliptic_Cauchy_chord_locator | secant_syzygy_flattening | incidence_reporter | unchanged_density_output`. It is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H669`, the balanced product/subresultant reporting lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H670`, the exact root-row hyperplane reporter.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H671`, the affine root-pencil/secant source-recovery lane.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact Cauchy/secant identity control.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P041`, the prior reporter/ordering control with unchanged relation density.

## Closest primary literature

- Frobenius and Stickelberger, [Zur Theorie der elliptischen Functionen](https://doi.org/10.1515/crll.1877.83.175), supplies the classical elliptic determinant identity.
- Onishi, [Determinant expressions for hyperelliptic functions](https://doi.org/10.1017/S0013091503000695), gives higher-genus determinant analogues, not source-reporting complexity.
- Okada, [An elliptic generalization of Schur's Pfaffian identity](https://doi.org/10.1016/j.aim.2005.05.022), supplies nearby elliptic determinant/Pfaffian structure.

No source proves the required restricted displacement rank or below-rho source unranking.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, complete determinant charts, factor base, and public ordering.
2. Build displacement generators and reproduce every determinant zero against exhaustive additions.
3. Report all target incidences and recursively condition generators to source leaves.
4. Verify every source tuple and retain all duplicates/misses.
5. Collect full-rank relations and solve verified factor-base logs.
6. Apply the identical reporter to randomized `Q+[t]P`.
7. Complete source-labelled target descent and substitute factor logs.
8. Remove `t` and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, setup exponent `a`, per-query reporter
exponent `kappa`, relation and target reciprocal densities `N^delta,N^delta_t`, source
output exponent `omega`, sparse linear algebra `2beta`, and memory `mu`. Then
`lambda=max(a,beta+delta+kappa,beta+delta+omega,2beta,delta_t+kappa,delta_t+omega,mu)`.
The `beta` terms charge the `N^beta` accepted rows required for calibration. For pair
support of probability `Theta(B^2/N)`, collecting `B` rows already costs `N/B`; when
`beta<1/4` is required by linear algebra, this is worse than rho before reporting.
Constant displacement rank receives no credit if query count or source output restores
the `1/2` exponent.

## Likely fatal obstruction

The determinant compresses evaluation of a relation condition but not the number of
targets or source incidences. Restricting to a generic factor base can destroy displacement
rank; recursively conditioned minors can visit `Theta(B^2)` leaves. Even a perfect reporter
leaves random relation density, factor-base rank, and individual descent unchanged.

## Proof track

Prove complete bounded displacement rank, output-sensitive source unranking, and all-stage
relation/descent exponents below rho.

## Disproof track

Show restricted displacement rank grows with `B`, source conditioning has quadratic
output, or full `lambda>=1/2`; semantic identity with `041/055` already rejects this version.

## Positive and negative controls

- Positive identity control: exhaustive Frobenius–Stickelberger determinant checks.
- Positive source control: planted Cauchy matrices with known low displacement and leaf labels.
- Negative structure control: matched random factor bases/orderings.
- Mechanism control: exhaustive secant reporter and the idea `041` locator.
- Leakage control: no target-specific ordering or discarded incidences.

## Quantitative promotion and falsification gates

No active promotion gate exists. A successor must first prove a new elliptic identity not
present in `013/041/055`, then achieve zero source errors, 1,000 relations, 100 blind
descents, and upper 95% `lambda,mu<=0.45`. Rank growth, quadratic source output, or lower
95% `lambda>=0.50` falsifies it.

## Artifact plan

- Collision report: `ideas/artifacts/ECDLP-IDEA-071/ledger_collision.md`
- Determinant derivation: `ideas/artifacts/ECDLP-IDEA-071/displacement_identity.md`
- Verifier: `ideas/artifacts/ECDLP-IDEA-071/verify_sources.sage`
- Retain matrices, generators, minors, incidences, sources, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. A fast exact
reporter or valid relation is not a breakthrough.

## Exactly one next executable action

1. If reopened, first write `ideas/artifacts/ECDLP-IDEA-071/ledger_collision.md` proving a source-recovery operation absent from ideas `013/041/055`; otherwise execute nothing.
