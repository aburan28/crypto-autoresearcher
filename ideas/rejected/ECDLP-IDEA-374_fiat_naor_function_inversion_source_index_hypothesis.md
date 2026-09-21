# ECDLP-IDEA-374 — Fiat–Naor function-inversion source index

## Status and claim labels

- Class: `algorithmic`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_inversion_advice_requires_source_evaluation_and_exceeds_query2p1_gate`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run preflight under `review_required`; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an inversion table or valid toy relation is not an ECDLP break.

## Falsifiable hypothesis

The five-deck endpoint map admits a target-independent Fiat–Naor arbitrary-function inversion index whose advice fits the `B^(9/4)` state gate and whose fresh-target inversion, exact restricted-existence replay, and source output fit the `B^(5/4)` online gate.

## Mechanism-new operation

The screened operation is **preprocess collision-aware chains for the endpoint function, invert a fresh target through distinguished advice, and replay the same index under frozen dyadic deck restrictions until one exact source tuple is isolated**. This is not a renamed solver: survival requires a DLP-free endpoint evaluator and restriction-stable inversion advice that does not store the source incidence table.

## Assumptions

1. A source tuple can be evaluated into a public endpoint without enumerating complement pairs, and the evaluator retains signed occurrence labels.
2. Fiat–Naor preprocessing can be shared across fresh targets and arbitrary dyadic restrictions without rebuilding source-sized tables.
3. Collision probability, chain merges, false alarms, all P1553 strata, source replay, and output are charged exactly.
4. The same frozen advice works for known-log relation collection and scalar-blind `Q+[t]P` target descent.
5. Setup, state, queries, rank, factor logs, ambiguity, verification, bit complexity, and peak memory all satisfy the frozen gates.

## Semantic fingerprint

`five_deck_endpoint_function | Fiat_Naor_collision_aware_inversion_advice | restricted_chain_replay | exact_occurrence_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the complete factor-base-to-target path and all source-bearing work remain mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H674`; reusable target-independent preprocessing is permitted only within the frozen state cap.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact source-resolving circuit or index is the missing object.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless source edges cannot be hidden as free advice.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit source-labelled transition materialization is a no-promotion control.

## Closest primary literature

- Fiat and Naor, [Rigorous Time/Space Trade-offs for Inverting Functions](https://doi.org/10.1137/S0097539795280512), gives inversion tradeoffs for a supplied evaluable function and charges its collision probability.
- Hellman, [A cryptanalytic time-memory trade-off](https://doi.org/10.1109/TIT.1980.1056220), preprocesses chains for a supplied function but does not construct elliptic source access.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint relation baseline, not a restriction-stable inversion index.

No checked source constructs the required source evaluator or restricted replay; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, five pairwise-disjoint signed decks of size `B`, endpoint evaluator, chain functions, advice budget, restrictions, masks, and independent verifier.
2. Build target-independent collision-aware inversion advice without enumerating or storing the `B^5` source domain or `B^2`-by-`B^2` transition incidence.
3. For known-log targets, invert the endpoint, issue charged exact restricted-existence replays along `O(log B)` dyadic children, recover one occurrence-labelled tuple, and verify its group sum.
4. Collect at least `B` verified independent rows, charge duplicates and misses, solve sparse factor logarithms, and independently verify them.
5. Apply the unchanged advice and restriction policy to fresh scalar-blind `Q+[t]P` targets, including mask-collision resampling and rebuilds.
6. Recover a tuple, substitute verified factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge preprocessing, endpoint evaluations, chain steps, collisions, replays, source output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; one complete fresh restricted query must be at most `B^(5/4+o(1))`; promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Fiat–Naor begins with random access to a supplied function over its domain. Here a domain element is already a five-source tuple, while restriction-stable endpoint evaluation and chain replay require the source transitions that Query2P1 is meant to avoid. Generic inversion tradeoffs over a `B^5` domain exceed the state/query rectangle; advice small enough to fit cannot preserve every rare restricted witness. The route therefore merges with IDEAs 051, 134, 168, 344, and 350 unless a new endpoint evaluator and restriction theorem removes that input cost.

## Proof track

Construct the evaluator and advice from endpoints alone, prove collision-complete restricted inversion for every stratum, and derive setup/state `<=B^(9/4)` plus fresh-target work `<=B^(5/4)` with complete exponents at most `0.45`.

## Disproof track

Show that each chain step needs a source-labelled transition, that arbitrary restrictions force advice rebuilds or `B^5` coverage, or that the Fiat–Naor tradeoff itself exceeds either frozen gate.

## Positive and negative controls

- Positive: supplied random functions with explicit evaluators and planted preimages must meet the published inversion tradeoff.
- Negative: equal endpoint summaries with different singleton restricted sources, collision-heavy maps, frozen hashes with all negative children, all P1553 strata, and blind targets.
- Baselines: IDEAs 051/134/168/344/350, explicit source tables, P1553 Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free evaluator, target-independent restriction-stable advice, exact source replay, `1,000` independently verified rows, `100` blind descents, setup/state at most `B^(9/4)`, one fresh query at most `B^(5/4)`, and `lambda,mu<=0.45`.
- Falsify on one hidden source transition, one missed singleton/stratum, post-hoc target advice, source-sized rebuilds, or either exponent at least `0.50`.
- A correct inversion of a supplied toy function is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-374/function_interface_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-374/restricted_chain_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-374/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-374/cost_analysis.md`

## Interpretation boundary

This rejects the screened source-index construction, not Fiat–Naor inversion. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Correct inversion advice is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-374/function_interface_theorem.md` and prove whether one restriction-stable endpoint-chain step is constructible without source incidence.
