# Pre-ID duplicate draft — Wilson cycle-popping source tree

## Status and claim labels

- Prospect: `20260719-d-D05`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `exact_random_tree_sampler` / `high-risk` / high-risk pre-ID screen
- State: `merged_rejected_supplied_transition_graph_and_undefined_accepting_tree_event`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Build an endpoint-derived transition graph on partial elliptic sums, root it at a target label, and apply Wilson's loop-erased random walks/cycle popping to sample a spanning arborescence. A precisely defined source-valid tree-path event would replay a signed source tuple, provide rank-complete relations, and support fresh blind descent below rho and BSGS.

## Mechanism-new operation

Wilson's operation erases loops and pops stacks to sample an exact random spanning tree of a supplied Markov graph. It counts only if the rooted transition graph is constructed endpoint-only, the accepting tree-path event is defined without source advice, and that event has a proved constant probability; random walking on explicit source edges is a control.

## Assumptions

1. A sub-gate public graph has paths biconditional with all signed five-source relations on every chart.
2. Graph construction, transition evaluation, walk length, loop erasure, cover behavior, conditioning, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. Tree paths preserve occurrence consistency rather than recombining unrelated partial sources.
4. One target-independent graph serves known-log and fresh scalar-blind targets without target-conditioned transition advice.
5. No explicit source-neighbor oracle, post-hoc accepting selector, same-field isogeny walk, scalar labels, or uncharged rejection sampling is admitted.

## Semantic fingerprint

`endpoint_partial_sum_transition_graph | Wilson_loop_erasure_cycle_popping | target_reaching_random_arborescence | tree_path_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted target support is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: an endpoint-to-source circuit remains missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: the source fibre cannot be supplied as a transition system.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`: path-faithful edges retain source incidence.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: an explicit transition graph crosses the source boundary.

## Closest primary literature

- Wilson, [Generating random spanning trees more quickly than the cover time](https://doi.org/10.1145/237814.237880), samples a tree from a supplied directed graph/Markov chain; it does not construct elliptic source transitions.
- Propp and Wilson, [Exact sampling with coupled Markov chains and applications to statistical mechanics](https://doi.org/10.1002/(SICI)1098-2418(199608/09)9:1/2%3C223::AID-RSA14%3E3.0.CO;2-O), is the occupied exact-sampling neighborhood and likewise requires transitions/conditioning.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) fix the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, graph, transitions, random stacks, restrictions, stopping rule, and verifier.
2. Build target-independent state within `B^(9/4+o(1))` without source-edge materialization.
3. Supply an exact zero-error no-relation certificate for every restricted query; on positive known-log targets, replay five verified occurrences from the defined tree-path event.
4. Preserve all failed/censored walks, collect at least `B` independent rows, and solve factor-base logarithms.
5. Reuse unchanged graph for fresh scalar-blind `Q+[t]P`, recover/verify a path, remove `t`, and verify `[x]P=Q`.
6. Charge construction, cover/walk time, negative samples, conditioning, replay, rank, logs, descent, verification, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge construction/storage of the rooted transition graph, outgoing-neighbor mechanism, stacks, labels, and exact absence-certificate state; let `q,q_m` charge one restricted query, including all walk/cover time, loop erasure, cycle popping, negative certification, bisection, and replay. Let `delta,delta_t` be reciprocal verified accepting-event success after the precisely defined sampling law, `o` output, `r` verified independent-rank credit, `u` path ambiguity plus failure amplification/rejection/rebuild cost, and `ell,ell_m` factor-log time/state.

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh graph/walk/absence/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho time and BSGS time/memory have exponent `0.50`. Source transitions, target rooting/conditioning, all rejected samples, and zero-error negative certificates are charged.

## Likely fatal obstruction

Wilson sampling requires the transition graph and outgoing-neighbor oracle; making rooted paths biconditional with signed relation sources supplies the missing incidence. A spanning tree always gives graph paths to its root, but no source-valid accepting-path event or probability bound follows until that missing graph semantics is defined. Positive samples also give no exact certificate for a no-relation restriction; source-conditioned rejection or a zero-error absence test would use Query2P1. This merges with IDEAs `147/238/302/316/363/395` and pre-ID `C07`.

## Proof track

Construct an endpoint-only rooted graph/transition kernel, define the accepting tree-path event, prove its constant probability and occurrence-faithful replay, supply an exact no-relation certificate under restrictions, and close full costs.

## Disproof track

Expose source-bearing transitions, an undefined/source-conditioned event, absence of a zero-error no-relation certificate, a proved target family with vanishing event probability, path recombination, or any complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied directed graph with a planted labelled root path must reproduce Wilson's exact tree law and path replay.
- Negative: equal public transition aggregates with different rare paths, no-path targets, long-cover graphs, arbitrary restrictions, and blind targets.
- Baselines: IDEAs `147/238/302/316/363/395`, pre-ID `C07`, explicit source walks, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only transitions, exact all-strata restricted path semantics, a zero-error no-relation certificate, constant positive-event success, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source edge/conditioning bit, one invalid path, no exact absence certificate, vanishing success, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d05_transition_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d05_tree_path_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d05_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic transplant, not Wilson's exact sampler. A correct tree distribution or toy path is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d05_transition_provenance.md` and classify every vertex, transition, root condition, and replay pointer by source dependence before any run.
