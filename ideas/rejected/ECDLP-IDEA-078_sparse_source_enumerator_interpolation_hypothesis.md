# ECDLP-IDEA-078 — Sparse source-enumerator interpolation

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected`
- Evidence scale: `toy` black-box interpolation preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; interpolating a source polynomial or finding one relation is not an ECDLP break.

## Falsifiable hypothesis

For each target `R`, there is a compact black-box evaluator for the source enumerator
`F_R(z)=sum_{(i_1,...,i_m): sum F_i=R} z_{i_1}...z_{i_m}`. On a preregistered factor-base regime the polynomial has `s=N^(sigma+o(1))`, `sigma<1/2`, source monomials. Sparse multivariate interpolation recovers every monomial and therefore exact point sources with total evaluation, output, relation, rank, and blind-descent exponents below rho.

## Mechanism-new operation

The operation is **before-event evaluation of a target source enumerator followed by exact sparse interpolation of source monomials**. Moment sketches, Fourier diagnostics, coefficient certificates, and interpolation after enumerating relations are controls. The missing novelty lemma is an evaluator that computes `F_R(z)` without doing the decomposition search it is meant to replace.

## Assumptions

1. `F_R` is exactly defined over an audited field/ring with no cancellation of valid sources.
2. A target-independent evaluator uses sub-rho work and memory.
3. Support sparsity and coefficient height remain sub-rho for relation and target distributions.
4. Interpolation is collision-free or returns a complete ambiguity list.
5. Monomials decode to exact factor-base points/signs.
6. Evaluator setup, probes, failed interpolation, output, `N^beta` rows, rank, and descent are charged.

## Semantic fingerprint

`target_source_enumerator_polynomial | subrho_blackbox_evaluation | exact_sparse_multivariate_interpolation | monomial_to_point_sources | full_relation_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the open source-fiber generator/join question.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, where exact source-fiber generation is cubic.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H669`, the balanced product/source-recovery backend.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`, which already resolves explicit row-root incidences.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the no-promotion output/cost boundary.

## Closest primary literature

- Ben-Or and Tiwari, [A deterministic algorithm for sparse multivariate polynomial interpolation](https://doi.org/10.1145/62212.62241), supplies interpolation given an oracle, not the elliptic source evaluator.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies relation equations but not source-enumerator evaluations.
- Giusti, Lecerf, and Salvy, [A Gröbner-free alternative for polynomial system solving](https://doi.org/10.1006/jcom.2000.0571), shows nearby solution-representation costs.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, enumerator ring, coefficient/source conventions, probe sequence, and exhaustive reference.
2. Prove the evaluator identity and compare every coefficient with exhaustive tuples on tiny curves.
3. Run sparse interpolation, decode monomials to point sources, and verify every elliptic relation.
4. Collect `B+sigma` independent randomized rows; solve and verify factor logs.
5. Evaluate/interpolate masked blind targets, combine calibrated logs, unmask the scalar, and verify all candidates.

## Full rho/BSGS cost model

Rho time and BSGS time/memory exponents are `1/2`. Let evaluator setup `a`, per probe `e`, support exponent `sigma`, probe-count/output exponent `o>=sigma`, factor-base exponent `beta`, inverse relation/target densities `delta,delta_t`, linear algebra `ell`, and memory `mu`. The full exponent is `lambda=max(a,beta+delta+e+o,ell,delta_t+e+o,beta)`. If evaluating one probe already solves/counts the target fiber, its complete hidden cost is charged.

## Likely fatal obstruction

Sparse interpolation is only a backend once a black-box evaluator for `F_R(z)` exists. Evaluating that polynomial is weighted coefficient extraction over the same decomposition fiber and is exactly the occupied pre-event source-enumerator/moment-oracle gap in `P1434`, `ECFG-H676`, and deferred `053`. Generic support may also be dense, and `N^beta` relation targets each require fresh interpolation. No new operation supplies the evaluator without source enumeration.

## Proof track

Construct a sub-rho evaluator identity independent of source enumeration, prove sparsity and collision-free interpolation, exact source lift, and complete cost below rho.

## Disproof track

Reduce evaluator calls to decomposition counting, show support/output/evaluator exponent at least `1/2`, or find cancellation/source ambiguity under every permitted probe field.

## Positive and negative controls

- Planted sparse polynomials with known supports.
- Exhaustive elliptic source enumerators on tiny curves.
- Dense and cancellation-heavy enumerators.
- Aggregate-moment and explicit-incidence controls.
- Random factor bases at equal paid target count.
- Blind masked targets and complete output.

## Quantitative promotion and falsification gates

The identity gate requires exact coefficient equality and zero source misses on every tiny target. Future promotion requires 1,000 verified rows, 100 blind descents, upper 95% `sigma,e+o,lambda,mu<=0.45`, and stable fits. Falsify if evaluator/output lower exponent is at least `0.50` or any monomial/source mismatch independently reproduces.

## Artifact plan

- Evaluator identity: `ideas/artifacts/ECDLP-IDEA-078/source_enumerator.md`
- Prototype: `ideas/artifacts/ECDLP-IDEA-078/sparse_interpolate.sage`
- Truth generator: `ideas/artifacts/ECDLP-IDEA-078/exhaustive_sources.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-078/verify_monomials.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-078/analysis.md`

## Interpretation boundary

This deferred hypothesis is toy, heuristic, model-bound, and novelty-unverified. Sparse interpolation correctness is not evidence that the required elliptic evaluator exists or beats rho.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-078/evaluator_equivalence_boundary.md` reducing every proposed black-box evaluation of the source enumerator to paid decomposition-fiber coefficient extraction and the occupied `053` oracle.
