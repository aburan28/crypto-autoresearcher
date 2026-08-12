# Pre-ID duplicate draft — Fossorier–Lin ordered-statistics source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T10`; no canonical ID allocated.
- Disposition: `merged_rejected_posthoc_reliability_order_and_information_set_reprocessing`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; improved soft-decision performance, a decoded word, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-only observables rank signed factor-base positions by source reliability. Ordered
statistics decoding would reprocess only a bounded neighborhood of the most reliable independent
set, recovering exact relation sources, full-rank factor logs, and blind descents below rho.

## Mechanism-new operation

Ordered-statistics decoding sorts supplied channel reliabilities, chooses a reliable information
set, and reprocesses low-order error patterns. It counts only if endpoint data supplies a
predeclared, calibrated, source-free ordering and code/syndrome with an exact occurrence lift.
Reliability-ranked post-hoc search over explicit candidates is a selector/control, not a source
constructor.

## Assumptions

1. Endpoint-only reliability scores are calibrated for exact occurrence membership.
2. A compact code/syndrome represents every signed tuple with a low reprocessing order.
3. Ordering and elimination preserve signs, repeats, order, infinity, tangencies, and all strata.
4. Reprocessing lists, stopping tests, retries, and false candidates meet both caps.
5. The frozen ordering generalizes to full-rank relation rows and 100 fresh blind targets.

## Semantic fingerprint

`public_endpoint_occurrence_reliabilities | reliability_ordered_information_set | bounded_error_pattern_reprocessing | exact_signed_source_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — a public code/syndrome and source lift remain missing.
2. `ideas/rejected/ECDLP-IDEA-336_guruswami_sudan_source_list_decoder_hypothesis.md` — supplied received data is not an endpoint compiler.
3. `ideas/rejected/preallocation/20260723-b_S12_rubinstein_cross_entropy_source_sampler_preid_duplicate.md` — ranked scores amplify a predicate rather than create it.
4. `ideas/rejected/preallocation/20260723-a_R12_auer_ucb_source_arm_selector_preid_duplicate.md` — adaptive selection cannot supply an exact reward/source oracle.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and signed replay remain required.

## Closest primary literature

- Fossorier and Lin, [Soft-decision decoding of linear block codes based on ordered statistics](https://doi.org/10.1109/18.412683), reorders supplied symbol reliabilities and reprocesses candidate error patterns.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no calibrated occurrence reliability ordering.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the ECDLP reliability/code compiler, exact lift, or complete descent.
The transplant remains novelty-unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, code/syndrome, reliability rule, stable sort, information-set and reprocessing orders, restrictions, masks, strata, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding labelled training sources, relation catalogues, and factor logs.
- For known-log endpoints, charge scores, sorting, eliminations, every test pattern/order, stopping rule, candidate lift, signed replay, and verification.
- Collect at least `max(d_FB+32,1000)` verified rows, retain misses/dependencies, require rank `d_FB`, and solve every factor log.
- Reuse byte-identical state on 100 fresh scalar-blind masks, reprocess/replay tuples, subtract masks, and verify scalars.
- Charge score construction, candidate density, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, charge setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, scoring/sorting/reprocessing/replay `N^q,N^q_m`, rank
credit `N^r`, output `N^o`, ambiguity/retries `N^u`, and factor logs
`N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

OSD's gain comes from channel reliabilities correlated with actual error positions. The endpoint
does not reveal analogous occurrence reliabilities. Exact scores encode the missing predicate;
proxy scores can be identical across different fibres. Higher reprocessing order then approaches
explicit support enumeration and restores the original search cost.

## Proof track

Prove a public calibrated reliability/code compiler, bounded correct reprocessing order,
all-strata exact lift, full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Find equal rankings with different exact sources, expose labelled training/post-hoc selection,
force reprocessing order/output beyond caps, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied binary linear-code words with calibrated soft reliabilities.
- Negative: equal-ranking different-source fibres, adversarial misranking, high-order errors, shuffled labels, empty fibres, exceptional charts, and fresh targets.
- Baselines: IDEA-014/336, cross-entropy, UCB selectors, P1553 R4, rho, and BSGS.
- Better soft-decision performance remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public reliability/code/lift theorems, zero errors at four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on source-bearing scores, one ranking/source collision, reprocessing/cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t10_reliability_order_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t10_equal_order_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t10_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects only the stated ECDLP transplant, not ordered-statistics decoding. A decoded word,
ranking gain, or valid relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Enumerate toy endpoint/source pairs and search for two distinct exact fibres that induce the same frozen occurrence-reliability ordering.
