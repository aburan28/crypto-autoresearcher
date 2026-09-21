# Pre-ID duplicate draft — Bloom source-membership gate

## Status and claim labels

- Prospect: 20260720-a-E11; no canonical ECDLP idea ID was allocated
- Class / risk / lane: probabilistic_membership_filter / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_source_keys_false_positives_and_no_replay
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; fast approximate membership is not an ECDLP result.

## Falsifiable hypothesis

Insert target-independent public fingerprints of compatible partial elliptic sums into Bloom filters arranged by signed deck and restriction. A target query with no false negatives would reject most empty cells, while a positive cell could be bisected and verified until one exact source tuple is replayed for factor logs and fresh blind descent below rho and BSGS.

## Mechanism-new operation

A Bloom filter sets several hash bits for each supplied key, giving no false negatives and tunable false positives for membership. It counts only if inserted keys are endpoint-derived without source enumeration, filter positives imply exact restricted existence within charged verification, and an occurrence is replayed. Filtering an explicit source-key table or merely reducing backend constants is a control.

## Assumptions

1. Every inserted key can be generated endpoint-only and is complete for all signed/exceptional sources.
2. Key generation, hashes, bit arrays, false positives, restriction filters, verification, replay, rank, logs, descent, randomness, bit time, and memory are charged.
3. False-positive amplification plus verification remains under the fresh-work cap for singleton and absent cells.
4. Positive bits can be inverted to point-faithful occurrences without source satellites.
5. One frozen filter family serves known-log and fresh scalar-blind targets without target-specific rebuilds or explicit large-prime tables.

## Semantic fingerprint

public_endpoint_membership_keys | Bloom_multi_hash_bitset | exactified_restricted_membership | positive_bits_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted target-label support and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing exact source-resolving circuit.
3. inputs/ledger_inventory_20260719.json — ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY charges inserted labelled records.
4. ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md — aggregate membership data lose source identity.
5. ideas/rejected/ECDLP-IDEA-347_countsketch_heavy_endpoint_source_decoder_hypothesis.md — hashed source updates do not give exact rare replay.

## Closest primary literature

- Bloom, [Space/time trade-offs in hash coding with allowable errors](https://doi.org/10.1145/362686.362692), tests approximate membership in a supplied set with allowable false positives; it does not construct the set or return a member.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but not inserted source keys.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), gives the baseline.

No checked source supplies endpoint-only keys, zero-error source return, or complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, key grammar, hash seeds, bit-array sizes, restriction layout, verifier, and false-positive budget.
2. Construct target-independent filters within B^(9/4+o(1)) without enumerating source products.
3. For known-log R=[kappa]P, exactify every positive restricted query, replay labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) restriction queries plus every false-positive sibling, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve false positives/dependencies, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged filters for fresh R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge inserted keys, hashes, bit arrays, all positives and negative verification, restrictions, replay, rank, logs, descent, scalar checks, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge key construction, all filter arrays, hash descriptions, restriction copies, and any source satellites; q,q_m charge target hashing, false-positive exactification, every restricted query, bisection, and replay. Let delta,delta_t be reciprocal verified relation/target densities, r independent-rank credit, o output, u false-positive amplification/key collisions/rebuilds, and ell,ell_m factor-log time/state.

Let n be inserted keys, m filter bits, k hash functions, Q adaptive queries, eta the global false-positive budget, and C_exact the work to exactify a positive. The native false-positive approximation is p_fp=(1-exp(-kn/m))^k, with optimal m approximately -n ln(p_fp)/(ln 2)^2. Build time is Theta(kn), state m bits, and a global union bound requires Q p_fp<=eta unless a stronger adaptive theorem is proved. Set a=log_N(T_keys+kn), a_m=log_N(m+M_satellite), q=log_N(Q(k+C_exact)+T_replay), and q_m=log_N(m_live+M_exact). Zero false positives require an exact dictionary or an idealization; the filter provides no source inverse.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh exactification/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho and BSGS baselines are 0.50. Full inserted-key count, simultaneous false-positive probability across all queries, verification backend, and restriction filters are charged.
The complete fresh masked-target hashing/exactification/replay path must also be <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds on n,m,k,Q,p_fp, exactification, state/fresh/complete exponents and a simultaneous empty/singleton error bound.

## Likely fatal obstruction

Bloom filters begin after the key set is supplied, so inserting exact compatible partial sums is source enumeration. Their bit arrays have no inverse to source occurrences and positive answers can be false. Reducing false positives enough for every adaptive empty/singleton restriction approaches exact dictionary state, while exactifying positives invokes Query2P1 or scans source keys. This merges with IDEAS 053/344/347/380.

## Proof track

Construct keys endpoint-only, prove a sub-gate simultaneous false-positive/exactification bound and source inverse on all restrictions, then close rank and blind descent.

## Disproof track

Expose one source-bearing inserted key, two sets with the same admitted bit array and different singleton membership, or exactification work/state beyond the caps.

## Positive and negative controls

- Positive: a supplied key set must have no false negatives and planted labelled keys must verify.
- Negative: empty and singleton sets sharing the same bit array, adversarial false positives, absent/exceptional targets, restrictions, equal endpoint keys with different ancestry, and blind targets.
- Baselines: IDEAS 053/344/347/380, explicit hash tables, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only keys, exact all-strata restricted answers and source inverse, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, simultaneous error budget, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source key, one unresolved false positive or absent inverse, target-specific rebuild, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e11_key_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e11_false_positive_inverse_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e11_cost_analysis.md

## Interpretation boundary

This rejects the transplant, not Bloom filters. Correct approximate membership, filter compression, or a verified relation is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e11_key_provenance.md and classify every inserted key and every exactification lookup by whether it already contains source incidence.
