# Pre-ID duplicate draft — Mackworth AC-3 source-arc filter

## Status and claim labels

- Prospect: `20260722-a-N01`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / conservative / relative conservative screen.
- State: `merged_rejected_supplied_constraint_network_and_local_consistency_only`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; correct arc filtering or one valid relation is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order `E(F_p)`, public endpoints induce a compact five-variable constraint network whose domains are signed factor-base occurrences and whose binary compatibility relations are exact. Mackworth AC-3 then removes unsupported values under arbitrary restrictions and returns an occurrence-labelled target relation often enough to complete factor logs and 100 fresh scalar-blind descents below rho and BSGS in time and live memory.

## Mechanism-new operation

The screened operation is repeated directed-arc revision: delete a domain value when it has no supporting value across a binary constraint, enqueue neighboring arcs, and reconstruct a surviving assignment. It is new only if domains and compatibility tests are endpoint-derived without source tables, local consistency is biconditional with five-way target existence, and surviving values replay one signed occurrence tuple.

## Assumptions

1. Every variable domain and binary compatibility predicate is computed from public curve data within the stated gates.
2. Arc consistency is complete for the frozen five-deck relation language, including repeated, tangent, vertical, and infinity strata.
3. Restrictions update the network without rebuilding explicit `B^2` compatibility tables.
4. A nonempty filtered network yields occurrence-distinct signed sources, not only locally supported values.
5. One target-independent network policy serves known-log rows and fresh masked targets.

## Semantic fingerprint

`public_endpoint_constraint_network | Mackworth_AC3_arc_revision | exact_restricted_nonemptiness | occurrence_assignment_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns exact restricted existence and signed occurrence replay.
2. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — compact local states can merge source histories with different completions.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — a compact constraint representation still needs an endpoint compiler and source inverse.
4. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — local extension support assumes represented elements and a supplied completion predicate.
5. `ideas/rejected/ECDLP-IDEA-147_moser_tardos_relation_resampling_hypothesis.md` — local-event manipulation does not make rare global satisfaction locally complete.

## Closest primary literature

- Mackworth, [Consistency in Networks of Relations](https://doi.org/10.1016/0004-3702(77)90007-8), presents node, arc, and path consistency for supplied constraint networks; it does not compile elliptic endpoint relations.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but not a compact source-faithful binary network.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic comparison control, not a lower bound on every coordinate-sensitive operation.

The exact transplant is absent as a titled record, but its information flow is already covered by supplied-network and local-support obstructions; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the prime-order curve, `B=N^(1/5)`, factor base, five signed decks, exceptional strata, network variables, domains, arc queue, restrictions, randomness, and independent point verifier before targets.
2. Build only target-independent state within `B^(9/4+o(1))`; forbid explicit source products, compatibility tables larger than the cap, discrete-log labels, target-fitted clauses, dense resultants, and Query2P1 calls.
3. For each known-log target `R`, enforce all endpoint constraints, run AC-3 under at most `5 ceil(log_2 B)+O(1)` restriction decisions, recover actual `(A_i,epsilon_i)` occurrences, and verify `sum epsilon_i A_i=R` before retaining a row.
4. With actual factor-base dimension `d_FB`, retain failures and dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every `log_P(A_i)`.
5. Reuse byte-identical target-independent state for fresh scalar-blind `R=Q+[t]P`; filter and replay a signed tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 fresh targets.
6. Charge network construction, arc revisions, restrictions, failed branches, ambiguity, output, verification, density, rank credit, factor-log solve, blind descent, bit complexity, randomness, and peak live memory.

## Full rho/BSGS cost model

For `B=N^beta`, freeze `beta=1/5`. Let setup/state be `N^a,N^a_m`; relation and blind reciprocal densities `N^delta,N^delta_t`; restricted query/workspace `N^q,N^q_m`; verified-rank credit `N^r`; output `N^o`; ambiguity/amplification `N^u`; and factor-log time/memory `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`.

Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh restricted work/workspace `<=B^(5/4+o(1))`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`. Every compatibility lookup, queued arc, deleted value, support pointer, output label, and verifier call is charged.

## Likely fatal obstruction

AC-3 is a local soundness filter, not a complete global solver. A binary network can be arc-consistent while having no five-way solution, and locally supported values can belong to mutually incompatible global tuples. Encoding exact elliptic compatibility materializes source incidence, while restoring completeness needs higher-order constraints or search equivalent to the missing Query2P1/replay interface. Thus the operation merges with existing supplied-network controls.

## Proof track

Prove an endpoint-only bounded-width constraint language for which arc consistency is globally complete on every all-strata restriction, with an occurrence-distinct inverse and complete `lambda,mu<=0.45` descent accounting.

## Disproof track

Exhibit an arc-consistent empty target fibre, equal filtered networks with different source tuples, one explicit source-derived compatibility edge, a restriction requiring network rebuild, or any complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied acyclic toy CSP whose unique assignment is occurrence-labelled.
- Negative: an arc-consistent unsatisfiable cycle, singleton fibres, equal local supports with different global sources, repeated occurrences, and blind targets.
- Baselines: the five anchors, explicit pair/triple compatibility tables, Query2P1/P1553 R4, rho, and BSGS.
- All controls are toy and model-bound; native correctness is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after zero semantic errors over four increasing frozen sizes, exact all-strata restricted answers, charged signed replay, rank `d_FB` from at least `max(d_FB+32,1000)` rows, complete factor logs, 100 blind descents, both resource caps, and `lambda,mu<=0.45`.
- Falsify this transplant on one arc-consistent empty fibre, false deletion/survival, lost occurrence, supplied network edge, cap failure, or either complete exponent at least `0.50`.
- A validator pass, theorem implementation, or correct relation is never by itself a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n01_arc_completeness_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n01_arc_consistent_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n01_cost_analysis.md`

The prospective artifact root is not created by this zero-compute screen.

## Interpretation boundary

This rejects only the screened ECDLP transplant, not AC-3. Finite checks remain toy; extrapolations remain heuristic, model-bound, and novelty-unverified. No experiment, lower bound, scalar recovery, or breakthrough is claimed.

## Exactly one next executable action

1. Write the arc-completeness audit and either prove global completeness for the frozen relation language or preserve the smallest arc-consistent empty fibre.
