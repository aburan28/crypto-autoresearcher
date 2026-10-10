# Paired conductor-gap ECDLP experiment

Status: **protocol only**. No curve pairs generated, solver runs executed, or hardness difference demonstrated.

## Hypothesis
Given ordinary elliptic curves E1,E2 over identical F_q with identical trace t and group order N, but distinct endomorphism conductors f1 != f2, test whether conductor position predicts a reproducible difference in algebraic relation-solving cost.

Do not confuse the conductor f_pi of Z[pi] with the actual endomorphism conductor f_E. Since t^2-4q=f_pi^2 D_K and f_E divides f_pi, certify f_E independently.

## Selection
1. Use SageMath to enumerate small ordinary curves over prime fields, and binary extensions with m=31,51,53,83 when feasible. For the initial feasibility smoke test use much smaller fields where complete endomorphism-ring computation is practical.
2. Group by (field representation, q, t, N, prime-order subgroup r). Select pairs with distinct **certified** f_E; record conductor ratio and the prime factors of the index.
3. Verify j-invariants, point counts, ordinary status, ring discriminants and the isogeny degree/path when available. Preserve unsuccessful candidate searches and time spent.
4. Avoid treating different coordinate models of the same isomorphism class as independent curves. Record twists and field extensions explicitly.
5. If no certified pair is found under budget, emit a negative selection receipt; never substitute unverified curves.

## Paired attack trials
- Same subgroup-order regime, factor-base cardinality, summation-polynomial arity, monomial ordering, Groebner F4/F5/SAT settings, seeds, time and memory budgets.
- Separate representation-dependent performance from structural effects: benchmark each curve in native coordinates and with standardized transformations, and include within-isomorphism controls.
- Record polynomial system dimensions, degree of regularity (only if actually observed), Hilbert function when computable, failed searches, timeout censoring, duplicate and invalid relations, verification, rank increments, preprocessing, elimination and total time.
- Record isogeny construction and evaluation costs separately; do not assume an isogeny degree implies an efficient ECDLP transfer.
- Pair randomized trial order on the same pinned CPU/GPU configuration. Log revision, hardware, compiler, solver version and command.

## Analysis
Primary endpoint: log(total seconds / newly independent verified relation), counting all attempts and setup costs. Secondary endpoints: degree of regularity, relation yield, memory, SAT conflicts, transfer overhead. Compare within matched pairs using bootstrap confidence intervals and a permutation test; retain censored runs, and use survival/censor-aware analysis where needed. Apply multiple-comparison corrections across scanned pairs. No extrapolation to cryptographic-scale security from toy fields.

## Stop/go gates
G0: 2 independently verified pairs with different endomorphism conductors.
G1: reproducible F4/F5 or SAT runs with raw receipts and exact relation verification.
G2: at least 10 paired seeds per pair and a matched same-conductor control.
G3: larger parameter replication with full accounting, blinded pair IDs, confidence intervals.
Report failure of any gate explicitly.

## Deliverables
`curves.jsonl`, `isogeny_edges.jsonl`, `runs.jsonl`, `paired_results.csv`, `analysis.json`, and immutable artifact hashes. Link to the dataset contract in docs/isogeny-anomaly-dataset.md after the associated PR merges.
