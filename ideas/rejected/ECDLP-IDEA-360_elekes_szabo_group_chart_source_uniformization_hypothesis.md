# ECDLP-IDEA-360 — Elekes-Szabó group-chart source uniformization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_group_chart_has_no_scalar_or_source_section`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired zero-run preflight contract`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; identifying group-like incidence structure is not an ECDLP break.

## Falsifiable hypothesis

An Elekes-Szabó-type group chart uniformizes a bounded-arity Abel-Jacobi relation variety so that restricted target fibres admit exact nonemptiness decisions and bisection to factor-base sources within the P1553 gates.

## Mechanism-new operation

The screened operation is **derive a rational group chart for the relation variety, turn restricted target fibres into bounded-dimensional additive chart equations, and decide their exact nonemptiness**. It is distinct only if chart restriction and decision are computable without restating the elliptic-curve group law or solving DLP.

Minimum-interface correction: a canonical rational section is unnecessary. A target-labelled, subset-stable exact chart-fibre existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged chart queries, suffices to recover one signed tuple.

## Assumptions

1. The relevant relation component satisfies a uniform group-like classification over the finite fields and exceptional strata in scope.
2. The chart and its inverse are explicit from public endpoint equations.
3. Chart coordinates can be solved without enumerating factor-base tuples or computing discrete logs.
4. Restricted chart solving preserves exact zero-versus-nonzero for relation collection and fresh targets, so bisection recovers one signed tuple.
5. Classification, chart construction, exceptions, inversion, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`abel_jacobi_relation_variety | elekes_szabo_group_like_classification | rational_group_chart_uniformization | subset_stable_exact_fibre_decision | dyadic_source_bisection | blind_scalar_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-P1434-GENERATIVE-RULE-POSITIVE-CONTROL`; exact generative relation replay is a control but does not invert endpoint fibres.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1473`; birational or coordinate transport did not provide a source-resolving section.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`; group-law reparameterization preserved the original inversion burden.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public arithmetic source-fibre generation remains the explicit missing theorem.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; exact source terminals retain the witness surface.

## Closest primary literature

- Elekes and Szabó, [How to find groups? (And how to use them in Erdős geometry?)](https://doi.org/10.1007/s00493-012-2505-6), classifies certain high-incidence algebraic relations as group-like; it does not give a finite-field scalar or source section.
- Bays and Martin, [Incidence bounds in positive characteristic](https://doi.org/10.5802/ahl.174), treats positive-characteristic group-like incidence phenomena and exceptional behavior, not exact ECDLP source inversion.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), exposes bounded-arity relation varieties without a canonical rational source section.

No checked source supplies the finite-field chart, exception control, and exact source/scalar section together; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, relation component, chart domain, exceptional locus, inverse section, masks, and verifier.
2. Construct target-independent chart state or a bounded target-fibre update without enumerating source tuples.
3. Decide restricted chart-fibre nonemptiness for known-log targets, bisect one signed tuple, and replay the relation.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Apply the identical restricted chart decision and bisection to fresh masked targets, including every exceptional stratum.
6. Substitute logs, remove masks, retain ambiguity, and verify `[x]P=Q`.
7. Charge classification/theorem instantiation, chart/inverse evaluation, fibre solving, source output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(beta)`, `beta=1/5`, and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `a` charges chart/classification construction, `q` includes target-fibre solving plus restriction updates, `o` is exact source output, and `u` is residual ambiguity. Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are exponent `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

The Abel-Jacobi variety is already group-like because it is defined by the public elliptic-curve law. A classification theorem therefore recovers structure already known, not a subset-stable exact decision for its endpoint fibre. This is a near-direct information-flow merge with IDEA-301's group-configuration coordinatization: both reconstruct the public group while leaving the restricted source decision unsupplied. A chart coordinate that supplies the scalar is DLP; the audited exact decision constructions encode or enumerate the source fibre. Exceptional loci and finite-field rationality add costs rather than remove this scoped obstruction.

## Proof track

Prove a positive-characteristic theorem whose explicit chart gives subset-stable exact fibre decisions independent of discrete logs, covers exceptions, and satisfies the complete gates with bisection.

## Disproof track

Show the chart is only the elliptic-curve group law in new coordinates, exhibit chart automorphisms with different source lifts, or reduce the proposed section to ECDLP/source enumeration.

## Positive and negative controls

- Positive: a supplied rational group surface with an explicit labelled section and known input coordinates.
- Negative: chart automorphisms and source permutations preserving every endpoint and chart invariant while changing the exact tuple.
- Baselines: IDEAs 130/176/239/301/354, H676, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a theorem-domain receipt, an endpoint-only subset-stable exact chart decision plus charged bisection, zero source errors, 1,000 rows, 100 blind descents, and complete exponents at most `0.45`.
- Falsify if the chart merely restates the curve group law, needs a discrete log/source table, misses one stratum, or has complete exponent at least `0.50`.
- Classification as group-like, relation validity, or a toy chart cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-360/theorem_domain_and_chart_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-360/chart_automorphism_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-360/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-360/cost_analysis.md`

## Interpretation boundary

This rejects the current uniformization-to-source-section route, not Elekes-Szabó incidence theory. All prospective checks are toy, heuristic, model-bound, and novelty-unverified. A classification theorem is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-360/theorem_domain_and_chart_obligations.md` as a theorem-domain receipt separating the known elliptic-curve group law from the missing subset-stable exact restricted-fibre decision.
