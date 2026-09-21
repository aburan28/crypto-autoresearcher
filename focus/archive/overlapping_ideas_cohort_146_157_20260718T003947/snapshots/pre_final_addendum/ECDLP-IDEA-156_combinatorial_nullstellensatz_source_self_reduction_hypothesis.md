# ECDLP-IDEA-156 — Combinatorial-Nullstellensatz source self-reduction

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_coefficient_oracle`
- Cohort: `20260718-a`
- Evidence scale: semantic and literature audit only; no experiment ran
- Contract posture: no contract; unapproved; zero runs authorized
- Scale labels: every prospective finite test is `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero coefficient, existence certificate, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a target-independent factor-base grid `F^m`, exact elliptic decomposition of `R` can be represented by a bounded-degree indicator polynomial with a publicly computable extremal coefficient. The Combinatorial Nullstellensatz coefficient formula and a sub-rho conditional-coefficient oracle then self-reduce that nonvanishing certificate to an exact signed source tuple for both relation collection and blind target descent, with complete time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **extremal-coefficient nonvanishing followed by coefficient-conditioned source self-reduction**. One constructs a polynomial nonzero exactly on valid source tuples, proves an extremal grid coefficient is nonzero, fixes source variables one at a time using conditional coefficient evaluations, and verifies the recovered tuple.

A relation-existence certificate, generic coefficient extractor, Gröbner solver, dense resultant, supplied source enumerator, or honest prover is a duplicate or control. The mechanism is new only if the exact finite-field indicator and all conditional coefficients are obtained without summing the full factor-base grid.

The record is rejected because Semaev equations vanish on sources, whereas Nullstellensatz directly certifies nonvanishing. Converting zero membership to an exact indicator uses high-degree finite-field exponentiation or an equivalent quotient representation. The coefficient formula then sums over `F^m`; conditional evaluation is the missing source-fiber oracle, not a source-generating operation.

## Assumptions

1. `E/F_p` contains `<P>` of public prime order `N=p^(1+o(1))`, target `Q=[x]P`, and target-independent signed factor base `F` of size `B=N^beta`.
2. A complete relation indicator handles signs, repetitions, infinity, denominator saturation, and every addition chart.
3. The indicator and extremal coefficient are constructed without target-specific advice, scalar labels, explicit tuple tables, or dense elimination objects.
4. Every conditional coefficient distinguishes at least one extendible source value and is computed in complete exponent below `1/2`.
5. Failed conditionings, output, rank, factor-log linear algebra, blind descent, verification, and peak memory are charged.
6. Finite experiments remain toy; extrapolations remain heuristic and model-bound.

## Semantic fingerprint

`factor_base_grid | exact_relation_indicator_polynomial | extremal_Nullstellensatz_coefficient | conditional_coefficient_source_self_reduction | blind_masked_descent`

The load-bearing operation is a cheap exact conditional-coefficient oracle derived from the endpoint. A nonzero coefficient or existence proof without source extraction is a relation-only certificate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the open public source-fiber generator and target-join requirement.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, where concrete predicates and recursive transcripts fail to compress source edges.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1473`, where exact sparse subgroup-`x` membership does not supply complete relation generation or descent.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where serial state polynomials fail the complete five-term source boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which freezes the required complete query, setup, source, rank, and descent exponents.

## Closest primary literature

- Alon, [Combinatorial Nullstellensatz](https://doi.org/10.1017/S0963548398003411), proves grid nonvanishing from an extremal coefficient and gives a coefficient formula; it does not give a sub-rho source oracle for a rare zero set.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation polynomial but not the required nonvanishing indicator or conditional coefficient algorithm.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/BFb0052236), supplies the generic-group comparison boundary.

No source supplies the exact indicator-to-witness operation. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta,m`, complete charts, grid weights, monomial order, and deterministic conditioning order.
2. Construct the exact relation indicator for endpoint `R`, including saturation and all exceptional cases.
3. Prove and evaluate the designated extremal coefficient without enumerating `F^m`.
4. Repeatedly condition one source variable, recompute conditional coefficients, and retain the first canonically extendible value until an exact tuple is obtained.
5. For known-log targets, verify every tuple directly and retain `B+sigma` independent rows of rank `B`.
6. Solve factor-base logarithms and independently verify each point logarithm.
7. Apply the identical indicator and conditioning order to fresh `Q+[t]P`, enumerate ambiguity, substitute factor logs, remove `t`, and verify `[x]P=Q`.
8. Charge indicator construction, coefficient evaluation, failed branches, source output, rank, linear algebra, descent, verification, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let advice/setup exponents be `a,a_m`; indicator construction and retained representation exponent be `c`; complete conditional self-reduction query and workspace exponents be `q,q_m`; inverse useful-row and target densities be `delta,delta_t`; source-output exponent be `o`; factor-log linear-algebra exponents be `ell,ell_m`; and ambiguity exponent be `u`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Every grid summand, exponentiation, quotient coefficient, conditional branch, and serialized source is included. A symbolic coefficient expression is not a cost bound.

## Likely fatal obstruction

The coefficient formula is a sum over the entire grid. An exact zero-set indicator has degree comparable to the field or requires a quotient algebra already encoding the source set. Conditional coefficients therefore cost `B^(m-o(1))`, or their compact evaluator is precisely the missing source-enumerator oracle. Nonvanishing alone provides no canonical source.

## Proof track

Construct a bounded-degree exact indicator; prove a nonzero extremal coefficient; derive a conditional coefficient recurrence with sub-rho construction and evaluation; prove exact source recovery; and establish `c,q,q_m,lambda,mu<=0.45`.

## Disproof track

Prove any exact indicator has field-scale degree, show the extremal coefficient vanishes generically, reduce conditional evaluation to the full grid sum or source enumeration, exhibit a false conditioning branch, or derive complete exponent at least `0.50`.

## Positive and negative controls

- Positive theorem control: planted low-degree grid polynomials satisfying the Nullstellensatz extremal-coefficient condition.
- Positive source control: tiny relation indicators with exhaustive source truth.
- Negative indicator control: the raw Semaev zero polynomial, which has the wrong nonvanishing orientation.
- Mechanism control: direct `F^m` coefficient summation and generic interpolation.
- Certificate control: report coefficient nonvanishing without source recovery.
- Leakage control: forbid source tables, target-selected monomials, scalar labels, and discarded conditionings.

## Quantitative promotion and falsification gates

A fresh successor requires a symbolic exact indicator with degree and representation exponent at most `0.20`, zero conditional/source errors through exhaustive 16-bit fixtures, at least 1,000 verified relations and 100 blind descents at each of two largest toy sizes, upper 95% `q,q_m<=0.20`, and complete `lambda,mu<=0.45`. Falsify on one generic vanishing extremal coefficient, one conditional false branch, any `B^m` grid stage, or complete `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Prospective coefficient theorem: `ideas/artifacts/ECDLP-IDEA-156/nullstellensatz_coefficient_cost_theorem.md`
- Prospective indicator derivation: `ideas/artifacts/ECDLP-IDEA-156/relation_indicator.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-156/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-156/verify_conditioning.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-156/cost_analysis.md`

No contract, experiment, run, or prospective artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified algorithm evidence. Nullstellensatz correctness or a nonzero coefficient is an existence certificate, not an ECDLP speedup. All finite tests would be toy; all scaling claims are heuristic and model-bound; no such result is a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-156/nullstellensatz_coefficient_cost_theorem.md` deriving the exact degree and grid-summation cost of the finite-field relation indicator before any implementation.
