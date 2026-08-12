# Pre-ID duplicate draft — Sum-product source messages

## Status and claim labels

- Prospect: `20260722-a-N09`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / high-risk / secondary screen.
- State: `merged_rejected_supplied_factor_graph_aggregate_marginals_and_loopy_heuristic`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Labels: finite controls are toy; extrapolations and loopy behavior are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; message convergence or relation validity is not an ECDLP result.

## Falsifiable hypothesis

The five-source relation has a compact endpoint-derived factor graph on which exact or certified sum-product messages give target-conditioned source marginals. Restriction self-reduction would replay signed occurrences often enough to complete factor logs and 100 blind descents below rho/BSGS.

## Mechanism-new operation

The screened operation passes variable-to-factor products and factor-to-variable sums of incoming messages, computing exact marginals on trees and approximate fixed points on loopy graphs. It counts only if the factor graph is endpoint-derived, messages certify exact zero/existence under restrictions, and marginal conditioning returns occurrence-distinct sources.

## Assumptions

1. Local factor functions are compact public endpoint functions, not source truth tables.
2. The graph is acyclic or has a proof making loopy fixed points exact for all targets/restrictions.
3. Message arithmetic avoids finite-field cancellation and numerical false zeros.
4. Marginals plus restrictions replay signed occurrences with charged ambiguity.
5. Target-independent factors/messages are reusable for blind masks.

## Semantic fingerprint

`public_endpoint_factor_graph | exact_sum_product_messages | restricted_nonzero_marginals | conditioned_signed_occurrence | complete_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — aggregates cannot replace exact Query2P1 and source replay.
2. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — aggregate statistics lose rare-source provenance.
3. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — compact messages can merge incompatible histories.
4. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — the factorization/compiler is already the missing representation.
5. `ideas/rejected/preallocation/20260721-c_K07_bcjr_endpoint_trellis_source_decoder_preid_duplicate.md` — exact message passing works only after a source trellis/state graph is supplied.

## Closest primary literature

- Kschischang, Frey, and Loeliger, [Factor Graphs and the Sum-Product Algorithm](https://doi.org/10.1109/18.910572), computes marginals from a supplied factor graph and distinguishes exact tree operation from approximate loopy use.
- Lauritzen and Spiegelhalter, [Local Computations with Probabilities on Graphical Structures](https://doi.org/10.1111/j.2517-6161.1988.tb01721.x), is the exact junction-tree control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply compact source-faithful factors.

No checked source constructs the ECDLP factor graph, exact loopy theorem, or occurrence inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, exceptional strata, factors, semiring/precision, graph, schedule, restrictions, masks, stopping rules, and verifier.
2. Build target-independent factors/messages within `B^(9/4+o(1))`; forbid explicit source products, target-fitted factors, log labels, dense resultants, and Query2P1.
3. For known-log `R`, inject endpoint evidence, compute certified exact messages, apply charged restrictions, replay `(A_i,epsilon_i)`, and verify their point sum.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain failures/dependencies, require rank `d_FB`, and solve every factor log.
5. Reuse eligible state for fresh `R=Q+[t]P`, recompute charged target messages, replay/verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 blind targets.
6. Charge factor construction, every message entry/update, iterations, precision, restrictions, ambiguity, output, verification, density, rank, factor solve, masks, and peak live memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, define setup/state `N^a,N^a_m`, densities `N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, ambiguity/amplification `N^u`, factor-log costs `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain exponent `0.50`. Factor/message size, iterations, and precision are not free.

## Likely fatal obstruction

Sum-product consumes a supplied factor graph. The exact elliptic relation graph is loopy/high-width; tree unrolling duplicates source state, while loopy beliefs are heuristic and can converge to false or uninformative marginals. Even exact marginals aggregate occurrences, and arbitrary conditioning requires the missing exact predicate/source replay. The operation therefore merges with trellis, transfer, aggregate, and graphical-model lanes.

## Proof track

Derive endpoint-only factors and prove exact certified message semantics on the frozen graph, restriction-stable occurrence replay, full rank/logs, blind descent, and sub-rho costs.

## Disproof track

Give a loopy fixed point with false zero/nonzero, equal marginals with different sources, a supplied factor entry, tree-unrolling cap breach, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied tree factor graphs with unique labelled assignments and exact rational messages.
- Negative: loopy pseudomarginals, cancellation, equal marginals/different sources, empty/singleton fibres, repeated strata, and blind targets.
- Baselines: BCJR/junction tree/bucket elimination, P1553 R4, rho, and BSGS.
- All controls are toy/model-bound; convergence is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after four-size exactness, certified zero/nonzero restrictions, charged signed replay, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one false message decision, supplied factor, lost occurrence, cap breach, or complete exponent at least `0.50`.
- Message correctness or a verified tuple is not a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n09_factor_message_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n09_loopy_source_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n09_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects the screened ECDLP transplant, not sum-product. Claims remain toy, heuristic, model-bound, and novelty-unverified. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the factor/message-origin audit and preserve the smallest loopy instance whose converged beliefs disagree with exact target-fibre existence.
