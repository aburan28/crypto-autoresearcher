# ECDLP-IDEA-306 — Demazure nil-Hecke source divided difference

## Status and claim labels

- Class: `algebraic_combinatorial_representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_divided_differences_annihilate_symmetric_source_data`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct divided-difference identity, nonzero class, valid relation, or toy factor lift is not an ECDLP break.

## Falsifiable hypothesis

The symmetric summation-polynomial fiber can be lifted to a compact type-A nil-Hecke module in which Demazure divided-difference operators recover an ordered exact factor tuple from endpoint data, enabling reusable relation generation and blind masked-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the symmetric endpoint fiber to a nil-Hecke module and apply the divided differences `partial_i(f)=(f-s_i f)/(x_i-x_{i+1})` to peel an ordered source word whose coordinates invert to exact signed factor points**. This is more specific than generic coefficient extraction: the proposed primitive uses the nil-Hecke action and its Schubert-word basis as a source router. But the endpoint polynomial and factor-product data are permutation-invariant, so every simple divided difference annihilates them. A nonzero word must begin with an order-breaking, source-labelled lift, which restores the missing provenance rather than deriving it. The proposal therefore merges with IDEAs 092, 152, 177, 187, and 188.

## Assumptions

1. A compact, target-uniform nil-Hecke module is constructible from the curve, factor-base predicate, and endpoint equations without enumerating or labelling source tuples.
2. Polynomial divided differences remain defined and point-separating across collisions, repeated factors, signs, and all nonreduced strata.
3. One public operator word has a canonical biconditional inverse from its surviving class to every exact signed factor point.
4. Module construction, symmetrization, operator words, all outputs, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`symmetric_summation_fiber | nil_Hecke_module_lift | Demazure_divided_difference_word | ordered_exact_factor_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-P1418-EXACT-PROJECTIVE-DIFFERENTIAL-CONTROL`, the exact permutation-closed projective differential compiler control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the known-difference representation that does not compress source recovery.
3. `inputs/ledger_inventory.json` — imported `ECFG-P1421-EXACT-TRANSPOSED-MATRIX-CONTROL`, the exact factor-polynomial matrix and pair-state control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank and no-low-block-rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1449`, the open joint EC-sum/source-ancestry feature and ancestry-permutation obstruction.

## Closest primary literature

- Demazure, [Desingularisation des varietes de Schubert generalisees](https://doi.org/10.24033/asens.1261), constructs the Schubert-resolution setting from which Demazure operators arise; it does not invert a symmetric finite-field endpoint fiber to labelled source points.
- Kostant and Kumar, [The nil Hecke ring and cohomology of G/P for a Kac-Moody group G](https://doi.org/10.1073/pnas.83.6.1543), develops the nil-Hecke action and Schubert-basis structure for supplied Weyl data, not a source-free point decoder.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives symmetric endpoint equations but no nil-Hecke source inverse.

No checked source supplies the hypothesized order-free module lift, exact all-strata factor inverse, blind descent, or complete sub-rho cost path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, symmetric summation equations, nil-Hecke presentation, module lift, public operator word, masks, and independent verifier.
2. For random known-log endpoints, build the module element without enumerating, ordering, or otherwise labelling its hidden factor tuples.
3. Apply the frozen divided-difference word, lift every nonzero output to exact signed factor points, and independently verify the endpoint relation.
4. Collect independent verified rows, solve the full factor-log system, and verify every recovered factor logarithm.
5. Apply the identical module construction and operator word to fresh masked targets `Q+[t]P` without target-trained words, selectors, or source advice.
6. Substitute factor logs, remove masks, retain every operator and sign ambiguity, and return all scalar candidates.
7. Accept only exact `[x]P=Q`, charging module state, word evaluation, exceptional strata, outputs, failures, rows, factor logs, descent, verification, time, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one module/divided-difference/inverse `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, target ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes module construction, every polynomial divided-difference operator, exact inverse, and independent verification; `o` includes every returned word and tuple. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Nil-Hecke divided differences measure failure of Weyl invariance: `partial_i(f)=0` whenever `f` is invariant under the adjacent transposition `s_i`. The summation polynomial and an unlabeled product over factor-base atoms are symmetric in source coordinates, so the proposed peeling word returns zero. Making it nonzero requires an ordered flag, nonsymmetric seed, primitive idempotent, or source-labelled monomial basis. That auxiliary object already contains the ancestry the operator was supposed to recover and has source- or tuple-sized construction/output in the generic case.

## Proof track

Construct a source-unlabelled compact module and prove that a public divided-difference word is nonzero, target-uniform, biconditional with exact signed factor tuples on every stratum, yields enough independent relations and reusable factor logs, supports blind descent, and satisfies `lambda,mu<=0.45`.

## Disproof track

Prove the relevant endpoint module lies in the symmetric invariants and is annihilated by every positive-length nil-Hecke word, or show that every nonzero point-separating lift requires ordered source incidence, primitive-idempotent decomposition, or state/output of exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied nonsymmetric Schubert polynomial with a labelled reduced word must reproduce its known divided-difference descendants and exact labels.
- Negative: a symmetrized version of the same polynomial must be annihilated and must not be reported as source recovery.
- Baselines: explicit tuple ordering, generic coefficient extraction, IDEAs 092/152/177/187/188, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an independent all-strata source biconditional, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if the symmetric input is annihilated, any nonzero lift needs source-labelled order or post-hoc operator choice, or charged state/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-306/nil_hecke_source_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-306/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-306/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-306/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of source extraction from symmetric endpoint data by nil-Hecke divided differences, not a universal impossibility theorem for Demazure operators or nonsymmetric encodings. A correct operator identity, nonzero labelled control, or valid relation does not provide exact source recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-306/nil_hecke_source_biconditional.md` proving either a source-free nonzero divided-difference inverse or the symmetric-annihilation/source-labelled-lift biconditional before any implementation.
