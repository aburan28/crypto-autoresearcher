# Pre-ID duplicate draft — Schroeppel–Shamir four-list source join

## Status and claim labels

- Prospect: `20260721-c-K01`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: time_space_tradeoff / conservative / conservative pre-ID screen.
- State: merged_rejected_explicit_source_lists_and_bsgs_equivalence.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a four-list collision or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Split signed five-source decompositions into four lazily merged endpoint lists, apply the Schroeppel–Shamir time-space tradeoff to answer every restricted existence query, replay an exact tuple, and complete factor logs plus blind target descent with time and memory exponents below rho and BSGS.

## Mechanism-new operation

The native operation forms two monotone streams of pairwise list sums and collides them without storing both full pair-sum lists. It counts only if each stream is generated from public endpoint data without enumerating source pairs and supports restriction-stable occurrence replay; applying the tradeoff to supplied factor lists or scalar-labelled sums is a meet-in-the-middle control.

## Assumptions

1. Source pair lists admit a public total order and lazy successor operation without DLP labels or quadratic preprocessing.
2. Signed, repeated, tangent, vertical, infinity, and empty strata remain occurrence-distinct through stream collisions.
3. Every restriction can be imposed without rebuilding source-sized streams.
4. A collision lifts to one labelled five-source tuple with charged ambiguity.
5. One target-independent state serves relation targets and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_pair_streams | Schroeppel_Shamir_four_list_lazy_join | exact_restricted_collision | collision_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay frontier.
2. `ideas/rejected/ECDLP-IDEA-134_preprocessed_three_sum_source_oracle_hypothesis.md` — preprocessing explicit sum lists retains the source traffic.
3. `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` — subset joins accelerate only a represented source domain.
4. `ideas/rejected/ECDLP-IDEA-362_sparse_nonnegative_convolution_source_router_hypothesis.md` — sparse convolution does not construct endpoint coefficients.
5. `ideas/rejected/ECDLP-IDEA-374_fiat_naor_function_inversion_source_index_hypothesis.md` — inversion advice starts from a supplied source function.

## Closest primary literature

- Schroeppel and Shamir, [A T=O(2^(n/2)), S=O(2^(n/4)) algorithm for certain NP-complete problems](https://doi.org/10.1137/0210033), proves the list time-space tradeoff for supplied decomposable instances.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than lazy source streams.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required endpoint-only ordered streams, restricted collision oracle, or occurrence lift; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, signed decks, restrictions, exceptional charts, ordering, and independent point verifier.
2. Construct and certify four lazy source streams from public endpoint data without pair enumeration, scalar labels, target advice, or `Query2P1`.
3. For each known-log target, make at most `5 ceil(log_2 B)+O(1)` exact restrictions, collide streams, replay labelled `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual factor-base dimension `d_FB`, retain failures and dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge stream construction, heap steps, comparisons, density, restrictions, replay, rank, logs, blind descent, bit time, and peak memory.

## Full rho/BSGS cost model

Charge stream setup and persistent merge state in `a,a_m`, restricted collision/replay in `q,q_m`, and every emitted or ambiguous candidate in `o,u`. For `B=N^beta`, `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, and log costs `ell,ell_m`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state at most `B^(9/4+o(1))`, fresh work/workspace at most `B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho expected time and BSGS time/memory are `0.50`.

## Likely fatal obstruction

Schroeppel–Shamir saves space only after four source lists and an order on their sums are available. For elliptic sources, producing a successor in sorted pair-sum order requires the pair deck, a scalar-compatible order, or repeated scans. The time remains meet-in-the-middle/birthday scale, while restriction and exact occurrence replay restore the source labels the merge tries not to store.

## Proof track

Give an endpoint-only lazy ordering with proved restriction stability and exact all-strata backpointers, then bound total stream advances, retries, and rank/log work inside the complete exponents.

## Disproof track

Trace each stream item, comparison key, successor, and backpointer; falsify on explicit pair enumeration, scalar ordering, repeated quadratic scans, lost occurrences, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sorted integer four-list instances with planted labelled collisions.
- Negative: random elliptic pair decks, duplicated endpoints, empty restrictions, adversarial order ties, and fresh targets.
- Baselines: explicit four-list join, BSGS, rho, IDEAs 134/199/362, and P1553 R4.

## Quantitative promotion and falsification gates

Promote only after endpoint-only stream construction, four increasing sizes, zero false decisions, exact replay on all strata, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both resource caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied lists, scalar ordering, any false answer, lift failure, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k01_stream_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k01_four_list_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k01_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only four-list transplant, not the Schroeppel–Shamir algorithm. Any finite collision remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
