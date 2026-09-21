# ECDLP-IDEA-339 — Gács–Körner common-part source keys

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_common_part_requires_joint_source_views_and_is_generically_trivial`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a common-information label, connected component, or correlated view is not an ECDLP break.

## Falsifiable hypothesis

Two public overlapping partial-sum views of the endpoint relation have a nontrivial uniformly endpoint-parameterized Gács–Körner common part whose support-component label is a compact exact join key for recovering signed factor tuples below rho and BSGS.

## Mechanism-new operation

The screened operation is **form the bipartite support graph of two partial-sum views, take its connected-component common variable, and use that maximal deterministic common part as an exact source join key**. This differs from statistical mutual information only if both views can be generated from the endpoint without supplying the hidden tuple. It otherwise merges with IDEAs 124, 131, 191, 307, and 320: their aggregate or marginal views do not contain a canonical shared point label.

## Assumptions

1. Endpoint-only public procedures generate paired partial views with the joint law needed for a common-part graph.
2. The common-part alphabet has sub-rho construction and state and is nontrivial on generic fresh curves.
3. Each useful common label has a bounded exact inverse to every signed factor tuple, including overlaps and repeats.
4. The label and inverse are equivariant with blind target masks, so mask changes are tracked exactly and removable after factor-log substitution.
5. Joint-view generation, graph components, failed labels, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`overlapping_endpoint_partial_views | bipartite_support_components | Gacs_Korner_maximal_common_part | exact_source_join_key | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the proposed exact source-resolving feature boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed multi-target source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where aggregate public features remain full-state or noninvertible.
5. `inputs/ledger_inventory.json` — imported `P1479`, where true factor logs lie outside tested public low-dimensional feature spaces.

## Closest primary literature

- Gács and Körner, [Common information is far less than mutual information](https://cs-web.bu.edu/faculty/gacs/papers/commoninf.pdf), identifies the maximal deterministic common variable of supplied correlated sources; it does not construct those sources from an elliptic endpoint.
- As a tangential contrast, Sriperumbudur et al., [Hilbert Space Embeddings and Metrics on Probability Measures](https://www.jmlr.org/papers/v11/sriperumbudur10a.html), studies injective representations of supplied distributions; that does not identify one hidden tuple.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies an existence equation rather than paired source views.

No checked source supplies the endpoint-derived common variable and exact inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, two view maps, pairing rule, common-part graph, inverse, masks, and verifier.
2. Generate known-log endpoint views without using factor tuples or a completion oracle.
3. Compute common components, replay every exact signed tuple, and verify each relation.
4. Collect at least `B` independent rows, solve factor logs, and independently verify them.
5. Generate the identical paired views for fresh scalar-blind masked targets.
6. Invert common labels, substitute logs, remove masks, preserve ambiguity, and verify `[x]P=Q`.
7. Charge view generation, support graph, components, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, common-part query excluding emission `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Joint samples, support edges, component construction, output, and verification are charged; `0<=r<=o`. Promotion requires complete exponents at most `0.45` and fresh-target work at most `0.25`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

For generic overlapping elliptic partial-sum views, the support graph is connected, so the Gács–Körner common part is constant. Making it disconnected requires source-conditioned view pairs or a source-labelled dictionary; those are the missing generator and join key. A nontrivial statistical correlation or mutual information does not produce deterministic exact source labels.

## Proof track

Construct endpoint-only paired views, prove a nonconstant small common-part alphabet with an exact all-strata inverse, and derive complete `lambda,mu<=0.45` on generic fresh curves.

## Disproof track

Prove the support graph connected after deck symmetries, find two distinct tuples in one component, show paired views require source samples, or charge graph construction/output to exponent at least `0.50`.

## Positive and negative controls

- Positive: synthetic paired variables with planted disconnected support and known common labels must invert correctly.
- Negative: connected-support, source-permuted, and independently resampled views must yield no preferred factor points.
- Baselines: IDEAs 124/131/191/307/320, explicit source joins, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free common-part constructor, nontrivial labels on every preregistered large instance, zero inverse errors, 1,000 verified rows, 100 blind descents, and complete exponents at most `0.45`.
- Falsify if the graph is connected, a label merges inequivalent tuples, paired views use hidden sources, state reaches `B^3`, or either exponent reaches `0.50`.
- Mutual-information or correlation gains without deterministic source replay cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-339/endpoint_view_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-339/support_component_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-339/common_part_inverse_spec.md`
- `ideas/artifacts/ECDLP-IDEA-339/cost_analysis.md`

## Interpretation boundary

This rejects the proposed common-part source key, not common-information theory. Every finite check would be toy; scaling is heuristic and model-bound; novelty is unverified. A common label or correlated view is not exact descent or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-339/endpoint_view_input_receipt.md` defining both endpoint-derived views and proving whether their joint support can be constructed without a hidden source tuple.
