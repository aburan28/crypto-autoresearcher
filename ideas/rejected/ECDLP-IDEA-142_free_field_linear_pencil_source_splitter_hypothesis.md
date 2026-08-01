# ECDLP-IDEA-142 — Free-field linear-pencil source splitter

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_free_field_linearization_backend`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: all prospective measurements are `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a minimal pencil, correct quasideterminant, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The compact serial elliptic-addition circuit admits a target-specialized noncommutative rational realization of sub-rho dimension whose pencil singularities have source-labelled residues biconditional with all accepted five-factor tuples. Minimal realization and quasideterminant evaluation can be performed without materializing the commutative `B^2/B^3` state sets, and residue vectors invert exactly to factor-base indices for relation collection and blind descent.

## Mechanism-new operation

The proposed operation is **free-field linearization followed by source-resolving noncommutative residues**. Treat the ordered source transitions as noncommuting letters, synthesize a minimal linear pencil for the rational serial-addition expression, specialize public factor membership and target data, and extract singular residue modules as exact source words.

Independent semantic review merges/rejects this specification. Free-field realizations compress evaluation or identity representations; they do not construct the missing commutative relation fiber. After specialization, aggregate residues repeat IDEA-089's supplied-algebra residue split, while source-labelled residues require the specialized kernels/source states already bounded by IDEA-115 and P1477/P1478. A commutative resultant pencil, block-Krylov on a supplied quotient, dense companion realization, or eigenvectors labelled after source enumeration is likewise a solver/backend control.

## Assumptions

1. `E/F_p`, prime-order `<P>` of size `N`, target `Q`, and signed factor base `F` of size `B=N^beta` are public.
2. Complete projective addition, signs, repetitions, infinity, and denominators have one uniform rational expression.
3. A canonical noncommutative lift is independent of the hidden scalar and does not introduce false words when evaluated in the commutative finite field.
4. Minimal pencil synthesis is direct from the compact circuit and has dimension/time/memory below rho; it is not built from the relation algebra or source list.
5. Every accepted singular residue decodes biconditionally to exact ordered factor points with multiplicity.
6. Synthesis, coefficient size, specialization, residues, output, rank, factor logs, blind descent, verification, and peak memory are charged.

## Semantic fingerprint

`serial_elliptic_rational_circuit | canonical_free_field_lift | minimal_noncommutative_linear_pencil | singular_source_residue_module | exact_word_to_factor_inverse | blind_descent`

The source-residue biconditional and sub-rho direct realization are load-bearing. Linearization alone is a solver/backend substitution.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H680`, which requires a recursive source-resolving circuit rather than bounded predicates or a backend swap.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, whose explicit forward/backward serial-`S3` state polynomials densify and fail the complete query gate.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-035`, where reusable factor-only pencil indexes make first-shift target descent no better than rho once the actual query/index cost is charged.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where a compact transition norm becomes a dense quadratic commutative composition; noncommutative ancestry must remove, not rename, that stage.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, the failed solver-substitution control for the same serial relation.

## Closest primary literature

- Volčič, [Matrix coefficient realization theory of noncommutative rational functions](https://doi.org/10.1016/j.jalgebra.2017.12.009), develops minimal linear realizations and obstruction modules, not root/source extraction for elliptic relations.
- Porat and Vinnikov, [Realizations of non-commutative rational functions around a matrix centre](https://doi.org/10.1112/jlms.12459), prove existence and uniqueness results for minimal realizations but no sub-rho source-residue theorem.
- Gelfand, Gelfand, Retakh, and Wilson, [Quasideterminants](https://arxiv.org/abs/math/0208146), develop noncommutative determinant calculus; it does not make commutative solution fibers source sparse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), is the neighboring relation framework.

No checked source provides the required canonical lift, source residues, or complete ECDLP cost path. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, ordered source alphabet, complete rational addition, free-field lift, realization normalization, and independent source verifier.
2. Synthesize the target-independent minimal pencil directly from the compact circuit and record dimension, coefficients, bit costs, and proof of semantic equivalence.
3. Specialize known-log targets and factor membership; compute all singular residue modules, decode complete source words, and verify direct elliptic addition.
4. Collect `B+sigma` verified rank-`B` rows, solve factor logs, and verify every point logarithm.
5. Specialize fresh masked targets `Q+[t]P`, decode every residue/source word, substitute logs, enumerate ambiguity, and accept only `[x]P=Q`.
6. Charge synthesis, specialization, residue computation/output, rank, linear algebra, descent, verification, and memory against rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let realization synthesis and memory be `N^a,N^a_m`; pencil dimension/serialization `N^c`; target specialization/residue time and working memory be `N^q,N^q_m`; inverse row/target densities `N^delta,N^delta_t`; source output `o`; ambiguity `u`; and factor-log linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
All linearization blocks, coefficient bits, minimality tests, nullspaces, residues, and output are charged. A compact formal expression with a large pencil or dense specialization fails. Finite toy slopes remain model-bound.

## Likely fatal obstruction

Free-field realizations linearize evaluation and identity, not commutative root finding. Noncommutative letters can retain word order only before specialization; mapping them back to commuting field coordinates can merge many source words. Making residues source-faithful may require a separate letter/state for every partial tuple, restoring P1477/P1478 dimensions. Minimal realization size can measure expression complexity while the zero set and source output remain large.

## Proof track

Define the canonical lift and prove evaluation equivalence, no spurious words, a joint singular-residue/source biconditional, and direct construction bounds giving `lambda,mu<=0.45`. Prove that commutative specialization does not collapse required ancestry.

## Disproof track

Show that residues depend only on the aggregate commutative value, that a source-faithful realization requires `Omega(B^(5/2))` dimension/work, or that synthesis reduces to an occupied quotient/resultant/Krylov solver. Any missed source, spurious word, or `lambda>=1/2` or `mu>=1/2` disproves the stated mechanism.

## Positive and negative controls

- **Positive control:** small noncommutative rational expressions with independently known minimal realizations and labelled poles/residues.
- **Positive control:** exhaustive tiny elliptic relation fibers with ordered source words, repeated points, signs, and infinity.
- **Negative control:** commuting specialization pairs with identical aggregate rational values but different source words.
- **Negative control:** P1477 states, P1478 resultants, ordinary companion pencils, block-Krylov, and generic SAT/SMT.
- **End-to-end control:** matched rho/BSGS plus known-log and blind targets with independent scalar verification.

## Quantitative promotion and falsification gates

The present lane is rejected as a representation/backend merge. A successor can receive a fresh ID only after proving a direct circuit-to-source operation not reducible to IDEA-089/115 or P1477/P1478, with complete `lambda,mu<=0.45` and no stage of dimension or traffic `N^(1/2)`. Falsify the original claim on one collapsed source pair, source-labelled input state, dense quotient/resultant, post-hoc label, or complete exponent at least `0.5`.

## Artifact plan

- Zero-run merge/no-go note: `ideas/artifacts/ECDLP-IDEA-142/free_field_linearization_merge.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-142/fixtures.json`
- Prospective realization code: `ideas/artifacts/ECDLP-IDEA-142/linear_pencil.py`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-142/verify_sources.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-142/cost_analysis.md`

These are prospective only; no artifact, contract, or experiment exists.

## Interpretation boundary

This is rejected, high-risk, novelty-unverified representation evidence. Every future finite result is toy and every exponent fit is heuristic and model-bound. A small realization, correct quasideterminant, or valid relation is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-142/free_field_linearization_merge.md` proving that commuting specialization either collapses word ancestry or restores the full source-state/pencil dimension, without running a solver.
