# ECDLP-IDEA-316 — Doob h-transform endpoint-source bridge

## Status and claim labels

- Class: `probabilistic_algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_doob_h_function_is_completion_oracle`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact conditioned chain, valid relation, or toy sample is not an ECDLP break.

## Falsifiable hypothesis

A source-blind Doob `h`-transform of the partial-sum walk can condition on a public endpoint and sample exact signed factor tuples with sub-rho setup, mixing, output, reusable relation rank, and blind target descent.

## Mechanism-new operation

The screened operation is **compute a positive harmonic completion function `h`, reweight every partial-source transition by `h(next)/h(current)`, and sample a path conditioned to end at the public target**. This differs formally from coupling from the past because conditioning is built into the transformed kernel. However `h(state)` is the total endpoint-reaching mass of hidden completions; exact transition ratios compute the missing completion oracle. It merges with IDEAs 081, 104, 147, 282, and 302.

## Assumptions

1. Partial signed sums form a target-independent Markov state space with a public base kernel.
2. The exact endpoint harmonic function is computable implicitly without enumerating completions or storing the source graph.
3. The transformed chain reaches every repeated and signed source stratum and returns exact factor points.
4. Harmonic evaluation, normalization, rejected paths, mixing, output, relation density, rank, factor logs, descent, verification, and memory are charged.
5. The same base kernel and `h`-evaluation rule apply to fresh masked targets.

## Semantic fingerprint

`partial_elliptic_source_walk | endpoint_harmonic_completion_function | Doob_h_conditioned_kernel | exact_factor_path_sample | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic generator and transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless partial-source edge boundary.
5. `inputs/ledger_inventory.json` — imported `P1477`, the explicit serial-state diagnostic whose backward endpoint states remain dense.

## Closest primary literature

- Doob, [Conditional Brownian motion and the boundary limits of harmonic functions](https://numdam.org/articles/10.24033/bsmf.1494/), constructs conditioned processes from a supplied positive harmonic function.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives endpoint constraints but not their compact exact completion masses.

No checked source supplies the required endpoint `h`, exact all-strata factor return, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, signs, partial states, base kernel, harmonic normalization, masks, stopping rule, and independent verifier.
2. For known-log endpoints, evaluate `h` and transformed transitions without enumeration, sample exact factor tuples, and verify each relation.
3. Collect independent rows, solve all factor logs, and independently verify the solution.
4. Reuse the identical base kernel and harmonic evaluator on fresh `Q+[t]P` targets without cached completion tables.
5. Substitute verified logs, remove masks, retain every path/output ambiguity, and return scalar candidates.
6. Accept only `[x]P=Q`, charging setup, harmonic queries, transitions, failures, mixing, output, rank, factor logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one conditioned sample/source return `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` charges all `h` evaluations, transition normalizers, failed paths, and mixing. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

For a partial tuple `s`, the exact harmonic value is a weighted count of completions from `s` to the endpoint. Ratios of these values reveal which next factors admit completions and with what multiplicity. Computing them exactly is the source-fiber counting/sampling oracle, while approximate ratios do not certify an exact relation distribution or all-strata recall.

## Proof track

Prove a compact endpoint-only recurrence for `h`, exact transformed transitions, sub-rho mixing and output, all-strata source recall, sufficient rank, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Reduce one exact `h` query to source completion counting, show exponential variance/mixing or missed strata, or prove that harmonic state, output, or either complete exponent is at least `0.50`.

## Positive and negative controls

- Positive: a supplied finite bridge with an independently enumerated harmonic function must reproduce the exact conditioned path law.
- Negative: endpoint predicates with identical aggregate counts but different completions must not be sampled from endpoint totals alone.
- Baselines: IDEAs 081/104/147/282/302, P1434, P1477, rejection sampling, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata samples, 1,000 verified independent rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if one `h` query needs completion enumeration, exactness fails, a stratum has zero recall, or either complete exponent reaches `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-316/doob_completion_identity.md`
- `ideas/artifacts/ECDLP-IDEA-316/conditioned_path_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-316/independent_doob_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-316/cost_analysis.md`

## Interpretation boundary

This is a scoped rejection of the stated exact endpoint-conditioned transform, not of Doob transforms or probabilistic search generally. Exact toy sampling or a valid relation is not scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-316/doob_completion_identity.md` deriving an endpoint-only recurrence for `h` or a reduction from exact `h` evaluation to source-completion counting.
