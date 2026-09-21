# Pre-ID duplicate draft — Reservoir source sampler

## Status and claim labels

- Prospect: 20260720-a-E12; no canonical ECDLP idea ID was allocated
- Class / risk / lane: one_pass_uniform_sampling / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_source_stream_and_rare_witness_loss
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; unbiased sampling from a supplied stream is not scalar recovery.

## Falsifiable hypothesis

Scan a target-independent stream of public partial-sum records and maintain a fixed uniform reservoir. If relation-bearing records occur often enough, the reservoir would retain exact source-labelled candidates for known-log relations and, under target masking/restrictions, fresh blind descent below rho and BSGS without storing the full stream.

## Mechanism-new operation

Reservoir sampling maintains a uniform sample without replacement from a supplied stream of initially unknown length using one pass and bounded memory. It counts only if the stream is generated endpoint-only without source enumeration, rare accepting records have a proved sub-rho inclusion probability, and sampled records replay exact sources. Sampling an explicit tuple stream is a control.

## Assumptions

1. A target-independent public stream is complete for all signed and exceptional source occurrences.
2. Stream generation, record count, random draws/skips, reservoir replacements, restrictions, failures, labels, replay, rank, logs, descent, bit time, and memory are charged.
3. Accepting records have target-uniform density sufficient for simultaneous relation and blind-target success.
4. Reservoir records contain point-faithful ancestry without making each record an explicit source tuple.
5. One frozen sampling grammar serves known-log and fresh scalar-blind targets without target-dependent rescans or post-hoc selectors.

## Semantic fingerprint

public_endpoint_record_stream | Vitter_reservoir_sampling | rare_accepting_record_inclusion | sampled_record_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted support and source replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-302_propp_wilson_coupling_source_sampler_hypothesis.md — exact sampling presupposes a source-valid transition/oracle.
4. ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md — source enumeration remains charged even when traversal storage is small.
5. ideas/rejected/ECDLP-IDEA-395_karger_stein_random_contraction_source_router_hypothesis.md — random reduction of supplied incidence can destroy rare witnesses.

## Closest primary literature

- Vitter, [Random sampling with a reservoir](https://doi.org/10.1145/3147.3165), samples uniformly from a supplied stream without knowing its length; it does not generate the stream or amplify a rare accepting class.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) gives endpoint equations, not a source record stream.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) gives the baseline.

No checked source supplies endpoint-only stream generation, exact restricted absence, or complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, stream grammar/order, random seeds, reservoir size, restrictions, and verifier.
2. Generate target-independent stream/reservoir state within B^(9/4+o(1)) without enumerating source products.
3. For known-log R=[kappa]P, obtain a sampled accepting record under each charged restriction, replay labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) restriction queries plus failed reservoirs, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; record every miss/dependency, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse the frozen grammar/state for fresh R=Q+[t]P, recover a sampled tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge every generated/scanned record, reservoir update/skip, restriction rescan, missed witness, replay, rank, logs, descent, scalar verification, bit operation, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge stream grammar/generation, full record count processed, reservoir state, and source labels; q,q_m charge target filtering, restriction rescans, every sampling pass, bisection, and replay. Let delta,delta_t charge only the outer density of targets whose frozen stream contains at least one acceptable record, excluding reservoir inclusion probability and amplification charged below in q. Let r be independent-rank credit, o output, u order effects/ambiguity not already charged by amplification, and ell,ell_m factor-log time/state.

Let L be supplied records, h acceptable records, k reservoir size, Q_R restriction passes, C_gen record-generation cost, and C_access actual record-access cost. The exact hit probability is p_hit=1-binom(L-h,k)/binom(L,k); for h=1 it is k/L. For allowed miss eta, A=ceil(log(eta)/log(1-p_hit)) independent reservoirs are required. Algorithm R scans all L supplied records, while Vitter's Algorithm Z can skip records in a seekable supplied stream; an endpoint generator without random access still pays the records it must generate/access, so selection skipping does not automatically remove Theta(L C_gen). Set a=log_N(T_grammar+C_access), a_m=log_N(k+M_labels), q=log_N(A Q_R(C_access+T_filter)+T_replay), and q_m=log_N(k+M_replay). A, repeated passes, and each restriction-specific rescan are charged once here.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh stream/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. If the stream has L records, accepting count h, and reservoir size k, charge the exact miss probability and the actual record generation/access count: Theta(L) for a sequential endpoint generator, or the measured Algorithm-Z access count for a seekable already-materialized stream whose materialization remains in setup. Bounded reservoir memory does not erase either cost. Each fresh masked-target restriction/sampling/replay path must fit <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds on L,h,k, access/generation, state/fresh/complete exponents and an inclusion interval matching the exact hypergeometric law.

## Likely fatal obstruction

Reservoir sampling reduces storage, not source-generation work. The supplied stream is the missing source catalogue, and a rare singleton has inclusion probability only k/L. Without explicit source labels a retained endpoint record cannot replay an occurrence; with labels it is a sampled tuple. Arbitrary restrictions require new streams/reservoirs, and finite sampling cannot certify empty support. This merges with IDEAS 302/343/395 and within this cohort with E01's source-stream/singleton-loss boundary and E03's rare-sample amplification boundary.

## Proof track

Give an endpoint-only sub-gate stream generator, target-uniform accepting-density theorem, restriction-stable sampling/replay, and complete rank/descent costs.

## Disproof track

Expose one source-bearing record, show k/L forces exponent 0.50 or more for singleton witnesses, or construct identical endpoint records with different source ancestry.

## Positive and negative controls

- Positive: a supplied stream with a high-density planted labelled class must match uniform inclusion probabilities.
- Negative: a unique accepting record in a long stream, identical endpoints with shuffled labels, empty streams, restriction-dependent order, exceptional targets, and blind targets.
- Baselines: IDEAS 302/343/395, explicit uniform tuple sampling, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only stream generation, proved target-uniform accepting density, exact all-strata replay and absence handling, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source record, one singleton inclusion cost reaching exponent 0.50, restriction rescan above cap, target-trained stream, or absent source inverse.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e12_stream_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e12_singleton_inclusion_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e12_cost_analysis.md

## Interpretation boundary

This rejects the ECDLP transplant, not reservoir sampling. Unbiased toy sampling or one retained valid tuple is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e12_stream_provenance.md and derive the full stream length, accepting density, inclusion probability, and source content of one record.
