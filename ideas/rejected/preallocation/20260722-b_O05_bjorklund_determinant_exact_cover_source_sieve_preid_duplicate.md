# Pre-ID duplicate draft — Björklund determinant exact-cover source sieve

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O05`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_relation_hypergraph_and_aggregate_detector`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`, `Monte-Carlo`.
- Breakthrough claim: none; detector correctness, an exact cover, or a relation is not an ECDLP result.

## Falsifiable hypothesis

An endpoint-constructible `k`-uniform hypergraph encodes five-source decompositions so
that Björklund's determinant/inclusion-exclusion sieve detects exact covers under every
restriction; charged self-reduction returns signed occurrences and completes blind descent
with `lambda,mu<=0.45`.

## Mechanism-new operation

The native algorithm embeds determinant matching detection into inclusion-exclusion for
a supplied exact-cover hypergraph. It counts only if hyperedges arise from endpoints without
source incidence and the aggregate detector supports exact negatives plus occurrence replay.

## Assumptions

1. The hypergraph is endpoint-derived within setup/state caps.
2. Exact covers are biconditional with the target sum across all strata.
3. Monte Carlo error is frozen, independently checked, and amplified within cost.
4. Restriction self-reduction returns signs, labels, multiplicities, and order.
5. Relation rows and fresh masked targets share the same hypergraph compiler.

## Semantic fingerprint

`public_endpoint_uniform_hypergraph | Bjorklund_determinant_exact_cover_sieve | exact_restricted_cover | charged_signed_self_reduction | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-a_A09_dancing_links_exact_cover_source_unranking_preid_duplicate.md` — exact cover over a supplied matrix is downstream search.
2. `ideas/rejected/ECDLP-IDEA-280_exterior_algebra_multilinear_monomial_source_sieve_hypothesis.md` — algebraic sieves require represented incidence.
3. `ideas/rejected/ECDLP-IDEA-243_pfaffian_zero_locus_derivative_router_hypothesis.md` — determinant detection does not construct or invert source support.
4. `ideas/rejected/ECDLP-IDEA-213_dimer_inverse_spectral_exact_source_router_hypothesis.md` — matching structures begin from a supplied graph.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact target existence and replay owner.

## Closest primary literature

- Björklund, [Exact Covers via Determinants](https://doi.org/10.4230/LIPIcs.STACS.2010.2447), gives randomized exact-cover algorithms for supplied hypergraphs.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not sparse source hyperedges.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The combination is title-new here but semantically merges with exact-cover,
exterior-algebra, and aggregate-detector lanes; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, vertex parts, hyperedge compiler, determinant field/randomness, restrictions, signs, strata, and verifier.
2. Build endpoint-only state within `B^(9/4+o(1))`; prohibit explicit relation hyperedges, dense source matrices, target fitting, and hidden Query2P1 calls.
3. For each known-log target, run the detector under charged restrictions, self-reduce to actual occurrences, and verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and retain seeds/failures.
5. Reuse identical state and frozen randomness for 100 fresh `R=Q+[t]P` targets, replay occurrences, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge hypergraph construction, inclusion-exclusion domain, determinants, amplification, negatives, replay, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; `a,q,u` include hyperedge access,
trials, self-reduction, and all-negative work. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Exact-cover hyperedges are the missing source-incidence object. Building them requires
enumerating compatible tuples or calling the restricted predicate. Determinants return
aggregate existence and may cancel; self-reduction multiplies target-conditioned calls.

## Proof track

Prove an endpoint-only sparse hypergraph compiler, exact target/cover biconditional,
bounded error, charged signed self-reduction, and complete descent inside the caps.

## Disproof track

Find one source-derived hyperedge, detector cancellation, false/missed cover, replay failure,
exponential universe, restriction rebuild, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy uniform hypergraph with one labelled exact cover.
- Negative: no-cover instances, cancelling determinants, multiple covers, repeated points, and blind targets.
- Baselines: dancing links, exterior-algebra sieves, P1553 R4, rho, and BSGS.
- Native success is toy/model-bound, not cryptanalytic promotion.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors over four sizes, bounded error receipts, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied incidence, one semantic error, unpaid amplification/replay, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o05_hypergraph_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o05_determinant_cancellation_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o05_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Björklund's algorithm. Evidence is toy, heuristic,
model-bound, novelty-unverified, and Monte Carlo. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Specify the endpoint-only hyperedge oracle and either prove exact cover/source biconditionality with charged replay or preserve the first source-incidence dependency.
