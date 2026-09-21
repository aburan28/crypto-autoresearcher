# ECDLP-IDEA-310 — Mixed-characteristic interlacing source router

## Status and claim labels

- Class: `spectral_algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_interlacing_requires_conditional_source_oracle_and_returns_existential_spectral_bound`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an interlacing family, a small largest root, a valid relation, or toy routing success is not an ECDLP break.

## Falsifiable hypothesis

Signed factor choices for an endpoint can be encoded as rank-one positive-semidefinite updates whose mixed characteristic polynomials form an efficiently conditionable interlacing family, so that root-guided conditional expectations route to an exact factor tuple and support reusable relation generation plus blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode factor choices as rank-one updates, build their mixed characteristic polynomial, and use interlacing-root bounds to fix one choice at a time until an exact source tuple is exposed**. This differs syntactically from solving the endpoint equations: it uses a real-rooted spectral certificate to route among partial assignments. The MSS theorem conditions a supplied assignment distribution and guarantees an appropriate leaf under its hypotheses; it does not recognize endpoint feasibility. In this ECDLP proposal, an efficiently computable polynomial conditioned on endpoint-feasible prefixes is missing, and constructing it by summing valid completions imports the source-fiber generator. The proposal therefore merges with IDEAs 104, 205, 231, 282, and 289.

## Assumptions

1. Finite-field elliptic factor choices admit a public Hermitian positive-semidefinite lift whose characteristic roots preserve endpoint feasibility on every source stratum.
2. Mixed characteristic polynomials conditioned on arbitrary prefixes can be evaluated without enumerating or counting their valid completions.
3. A small-root leaf is biconditional with an exact signed factor tuple rather than merely a well-conditioned aggregate assignment.
4. Matrix construction, coefficient evaluation, branching, failed leaves, tuple output, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`elliptic_factor_rank_one_lift | mixed_characteristic_polynomial | interlacing_conditional_router | exact_source_tuple | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batch generator and transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate spectral phase versus exact-source gap.
5. `inputs/ledger_inventory.json` — imported `P1478`, the compact one-transition primitive whose quadratic composition becomes dense.

## Closest primary literature

- Marcus, Spielman, and Srivastava, [Interlacing Families II: Mixed Characteristic Polynomials and the Kadison–Singer Problem](https://doi.org/10.4007/annals.2015.182.1.8), proves real-rootedness and an existential spectral bound for rank-one positive-semidefinite choices, not an elliptic endpoint source inverse.
- Marcus, Spielman, and Srivastava, [the primary preprint](https://arxiv.org/abs/1306.3969), supplies the mixed-characteristic and interlacing construction but assumes the matrix-choice distribution rather than recovering hidden combinatorial sources.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives endpoint equations without a conditionable interlacing oracle or exact tuple router.

No checked source supplies the finite-field positive-semidefinite compiler, a source-free conditional polynomial, exact factor return, or the complete sub-rho path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed factor base, public rank-one lift, assignment tree, conditioning rule, masks, and independent verifier.
2. For random known-log endpoints, construct the unconditioned mixed characteristic polynomial without enumerating source tuples.
3. At each prefix, evaluate every child polynomial, choose a certified interlacing child, continue to a leaf, return its exact signed factor points, and verify the elliptic relation.
4. Collect independent verified rows, solve the relation matrix, and independently verify every factor-base logarithm.
5. Apply the identical lift and prefix router to fresh masked targets `Q+[t]P`, with no target-trained selector or post-hoc leaf search.
6. Substitute factor logs, remove masks, retain every ambiguity branch, and return scalar candidates.
7. Accept only exact `[x]P=Q`, charging polynomial construction and coefficients, all conditional calls, matrix state, failures, tuples, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one conditional-polynomial/router/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes the positive-semidefinite lift, conditional mixed-characteristic evaluation, routing, exact inverse, and verification; `o` includes all routed and ambiguous tuples. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Under its stated hypotheses, interlacing conditions a supplied assignment distribution and proves the existence of a leaf with a controlled largest root; it does not make endpoint-satisfying assignments recognizable or recover their labels. The ECDLP proposal lacks an efficiently computable endpoint-feasible conditional polynomial. Constructing one by summing over valid completions is the missing source-counting or source-enumeration oracle. Moreover, elliptic finite-field data have no canonical order-preserving Hermitian lift, so a small spectral root need not imply endpoint equality. Making the matrices leaf-faithful explicitly stores the source deck and reaches source-sized state or output.

## Proof track

Prove a public finite-field-to-Hermitian compiler, a polynomial-time prefix-conditioning identity independent of hidden completions, and a biconditional between the selected spectral leaf and exact signed factors on every stratum; then prove independent relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Construct two completion families with identical accessible mixed characteristic data but different endpoint source leaves, prove that conditional evaluation is source counting, or exhibit a valid small-root leaf whose factor tuple misses the endpoint; separately lower-bound any leaf-faithful matrix representation at exponent `0.50` or worse.

## Positive and negative controls

- Positive: supplied toy rank-one families with explicitly labelled feasible leaves must satisfy the interlacing theorem and route to the known leaf.
- Negative: permuted source leaves with identical aggregate mixed characteristic polynomials must not be reported as exact point recovery.
- Baselines: exhaustive leaf enumeration, a random prefix selector, IDEAs 104/205/231/282/289, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata proofs, 1,000 verified relation rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if conditioning calls a source enumerator/counting oracle, the finite-field lift is not endpoint-biconditional, any source stratum fails, or matrix/state/output cost reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-310/interlacing_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-310/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-310/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-310/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated interlacing router, not an impossibility theorem for every spectral ECDLP technique. Real-rootedness, an existential root bound, correct toy routing, or a valid relation does not establish exact target descent or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-310/interlacing_source_theorem.md` proving a source-free conditional-polynomial identity and endpoint biconditional, or giving an explicit equal-polynomial/different-source counterexample, before any implementation.
