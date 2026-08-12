# Pre-ID duplicate draft — Bloom-semijoin endpoint filter

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P03`; no canonical ID allocated.
- Disposition: `merged_rejected_approximate_membership_over_supplied_source_keys`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`, `probabilistic`.
- Breakthrough claim: none; filter precision or relation validity is not an ECDLP result.

## Falsifiable hypothesis

A compact Bloom filter built from endpoint-derived partial-relation keys prunes all impossible
complements without false negatives. Exact follow-up probes return signed occurrences, allowing
full relation collection and blind descent with complete exponents at most `0.45`.

## Mechanism-new operation

A Bloom semijoin sends an approximate membership summary of one supplied relation to filter
another before exact joining. It counts only if the filter keys and exact verifier are compiled
from endpoints without enumerating source tuples, false positives are fully charged, and replay
returns occurrences. Filtering a materialized relation table is a control.

## Assumptions

1. Filter construction is target-independent and within the setup/state cap.
2. No true source fibre is lost across restrictions or exceptional strata.
3. False-positive rate, hash independence, rebuilds, and exact follow-up are charged.
4. Exact probes recover signs, multiplicities, and point identities.
5. The same filter and verifier serve fresh masked targets.

## Semantic fingerprint

`public_endpoint_partial_keys | Bloom_approximate_semijoin | no_false_negative_filter | exact_followup_signed_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-a_E11_bloom_source_membership_gate_preid_duplicate.md` — exact occupied Bloom-membership lane.
2. `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md` — semijoin input construction and width are charged.
3. `ideas/rejected/ECDLP-IDEA-307_slepian_wolf_distributed_source_decoder_hypothesis.md` — compressed summaries need a source-faithful inverse.
4. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — aggregate sketches are conditional on missing endpoint moments.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay frontier.

## Closest primary literature

- Bloom, [Space/Time Trade-offs in Hash Coding with Allowable Errors](https://doi.org/10.1145/362686.362692), defines approximate membership on supplied keys.
- Blasgen and Eswaran, [relational access and joins](https://doi.org/10.1147/sj.164.0363), is the supplied-relation database control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), and Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) provide equation and cost controls.

The exact Bloom-membership transplant already exists in the corpus; semijoin placement is a
solver/scheduling variant and novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, key universe, hashes/seeds, bit budget, restrictions, exact verifier,
   and all strata.
2. Build endpoint-only filter state within `B^(9/4+o(1))`; forbid explicit source/pair tables,
   scalar residues, target fitting, and uncharged large-prime storage.
3. For each known-log target, filter candidates, exact-probe every positive, replay signed
   occurrences, and verify the elliptic relation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and
   charge false positives, all negatives, amplification, outputs, and linear algebra.
5. Reuse byte-identical state for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge key construction, hashes, bits, exact probes, replay, rank, factor logs, and memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state are `N^a,N^a_m`, relation/target reciprocal densities
`N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`,
false-positive/amplification cost `N^u`, and factor-log time/memory `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

The filter can only summarize keys already obtained from source tuples. Endpoint-only coarse
keys give overwhelming false positives, while exact keys require the missing partial-source
enumeration. The exact follow-up still performs `Query2P1`.

## Proof track

Prove an endpoint-only key map with bounded false-positive exponent, zero false negatives,
restriction-stable exact replay, and complete descent under both caps.

## Disproof track

Find source-derived filter inputs, one false negative, false-positive exponent reaching rho,
missing occurrence labels, a restriction rebuild, or any complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy key sets with measured false positives and exact labelled follow-up.
- Negative: adversarial collisions, empty fibres, equal summaries/different sources, repeated
  signed points, hash reseeding, and blind targets.
- Baselines: prior Bloom gate, P1511 semijoin, P1553 R4, rho, and BSGS.
- Filter accuracy is toy/model-bound, not cryptanalytic promotion.

## Quantitative promotion and falsification gates

- Promote only with zero false negatives and semantic errors at four sizes, charged false
  positives, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on source-bearing inputs, one false negative, lost replay, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p03_filter_key_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p03_false_positive_matrix.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p03_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This merges a semijoin placement with the existing Bloom gate. All evidence would remain toy,
heuristic, model-bound, probabilistic, and novelty-unverified.

## Exactly one next executable action

1. Audit the proposed filter-key constructor against the existing Bloom gate and preserve the first source-bearing key or unbounded false-positive family.
