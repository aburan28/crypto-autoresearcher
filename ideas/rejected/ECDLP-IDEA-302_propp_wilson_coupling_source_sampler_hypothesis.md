# ECDLP-IDEA-302 — Propp–Wilson coupling-from-the-past source sampler

## Status and claim labels

- Class: `probabilistic_algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_endpoint_conditioned_transition_oracle_is_source_oracle`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; perfect sampling, coalescence, a valid relation, or toy recovery is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-conditioned monotone Markov chain on partial factor-base decompositions admits source-blind coupling from the past with sub-rho coalescence, returning an exact relation sample that supports reusable factor-log recovery and blind target descent.

## Mechanism-new operation

The screened operation is **run one grand monotone coupling backward from all partial-source states until every trajectory coalesces, then read the exact endpoint-compatible factor tuple**. Unlike ordinary random walks, rejection sampling, or MCMC, coupling from the past would certify an exact stationary draw without a mixing-time approximation. The operation is new at the name level, but its transition/completion kernel must decide which partial tuples extend to the endpoint; that is the missing source oracle. It therefore merges with IDEAs 079, 081, 104, 147, and 282.

## Assumptions

1. Partial decompositions have a public monotone order with endpoint-compatible top and bottom states.
2. One transition and the shared randomness map are computable from the endpoint without enumerating completions or materializing the source graph.
3. The grand coupling coalesces in sub-rho time and state for generic targets.
4. Its stationary output contains exact signed factor points on every source stratum, not only a count or unlabeled class.
5. Transition queries, failed horizons, outputs, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`endpoint_conditioned_partial_sources | monotone_grand_coupling | exact_stationary_sample | coalesced_factor_tuple | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batch generator and transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate-versus-exact-source gap.
5. `inputs/ledger_inventory.json` — imported `P1478`, the compact one-transition primitive whose quadratic composition becomes dense.

## Closest primary literature

- Propp and Wilson, [Exact sampling with coupled Markov chains and applications to statistical mechanics](https://doi.org/10.1002/%28SICI%291098-2418%28199608/09%299%3A1/2%3C223%3A%3AAID-RSA14%3E3.0.CO%3B2-O), gives exact stationary sampling when a simulable monotone coupling and coalescence are already available.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations but not a compact endpoint-conditioned transition oracle.

No checked source constructs the required order, transition kernel, all-strata source return, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, partial-source state space, monotone order, transition map, shared-randomness schedule, horizon doubling, and independent verifier.
2. On known-log endpoints, run the grand coupling backward, charge every transition and failed horizon, return exact signed factor points, and verify each relation.
3. Collect independent rows, solve and verify all factor logs.
4. Reuse the identical state space and transition map on fresh masked targets `Q+[t]P`, without target-trained orders or completion tables.
5. Substitute factor logs, remove masks, retain every ambiguity, and return candidates.
6. Accept only exact `[x]P=Q`, charging setup, transitions, state, output, failures, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation/coalescence densities `N^delta,N^delta_t`, one transition/coupling/source return `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` charges all trajectories and horizon restarts; `o` charges every returned tuple. Rho has time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

The chain cannot move among endpoint-compatible partial decompositions without answering whether a proposed partial state has a completion, sampling such a completion, or storing the full transition graph. That predicate is the original source search. Natural monotonicity is absent for signed elliptic-curve sums, and even a supplied chain can have exponential coalescence.

## Proof track

Prove a public monotone state order and endpoint-only transition identity, exact all-strata stationarity and source return, sub-rho coalescence, sufficient independent relation density, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show that one transition decides source completion, that two source states cannot be ordered monotonically under the endpoint constraint, or that coalescence/state/output has exponent at least `0.50`.

## Positive and negative controls

- Positive: a frozen small distributive-lattice model with a supplied monotone heat-bath kernel must coalesce to exact stationary samples.
- Negative: shuffled endpoint predicates and chains with identical aggregate stationary counts but different exact sources must not be decoded.
- Baselines: rejection sampling, ordinary MCMC, IDEAs 079/081/104/147/282, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata exact sampling, 1,000 verified rows and 100 blind descents per large size, and both full exponents at most `0.45`.
- Falsify if a completion oracle/source graph is required, monotonicity fails, or transition/coalescence/state/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-302/monotone_transition_identity.md`
- `ideas/artifacts/ECDLP-IDEA-302/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-302/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-302/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated endpoint-conditioned coupling operation, not a universal impossibility theorem for perfect sampling. Exact toy samples or a supplied-kernel speedup is not scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-302/monotone_transition_identity.md` giving an endpoint-only transition formula or a reduction from one transition query to exact source completion before any sampler is implemented.
