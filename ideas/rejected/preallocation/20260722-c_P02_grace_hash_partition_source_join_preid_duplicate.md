# Pre-ID duplicate draft — GRACE hash-partition source join

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P02`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_hash_buckets_and_source_keys`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a bucket match or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint-derived complementary partial-relation streams admit a public hash partition whose
matching buckets contain exactly the signed five-source fibres. GRACE-style partition/probe
then supplies relations and fresh target descents with complete exponents at most `0.45`.

## Mechanism-new operation

GRACE recursively partitions supplied relations by join-key hashes so each partition can be
joined in memory. It counts only if endpoint maps construct both keyed streams without source
enumeration and every hash candidate has exact charged occurrence replay. Hashing explicit pair
sums or large-prime tables is a control.

## Assumptions

1. Join keys are public, target-independent, scalar-blind, and exact after verification.
2. Both relations are endpoint-derived inside the setup/state cap.
3. Bucket skew, collisions, recursive repartitioning, and all-negative probes are charged.
4. Restrictions retain signed point identities and exact empty-fibre semantics.
5. Relation collection and fresh descent use the same partition state.

## Semantic fingerprint

`public_endpoint_keyed_relations | GRACE_recursive_hash_partition | exact_bucket_join | charged_signed_collision_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-c_C11_cuckoo_hash_source_peeling_preid_duplicate.md` — hashing does not construct source-bearing keys.
2. `ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md` — perfect lookup still consumes a supplied source dictionary.
3. `ideas/rejected/preallocation/20260721-c_K01_schroeppel_shamir_four_list_source_join_preid_duplicate.md` — materialized list joins preserve the same input floor.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — provenance and width remain charged.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — missing endpoint-labelled exact source return.

## Closest primary literature

- Kitsuregawa, Tanaka, and Moto-oka, [Application of Hash to Data Base Machine and Its Architecture](https://doi.org/10.1007/BF03037022), partitions supplied database relations.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide sparse keyed relation streams.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic control.

The transplant is a hash-join backend over absent relations, so it is semantically occupied
and novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, key functions, hash seeds, partition fanout, restrictions, and verifier.
2. Construct endpoint-only streams and partitions within `B^(9/4+o(1))`; forbid explicit
   pair-sum tables, source incidence, scalar residues, and target caches.
3. For each known-log target, probe restricted matching buckets, replay signed occurrences,
   and verify the elliptic equation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and
   charge skew, spills, collisions, retries, outputs, and linear algebra.
5. Reuse identical partitions for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge relation construction, I/O-equivalent traffic, hashes, recursion, verification,
   rank, factor logs, bit cost, and live memory.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, relation/target reciprocal densities
`N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`,
ambiguity/skew `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Useful hash keys and records already encode partial-source incidence. If constructed from
public endpoints alone they either collapse to coarse group data with huge buckets or require
the same pair enumeration/query operation being replaced.

## Proof track

Construct endpoint-only keyed relations with bounded skew, exact equality semantics,
restriction-stable signed replay, and a full sub-rho descent proof.

## Disproof track

Expose a source-bearing record, unbounded bucket, false/missed join, spill beyond caps,
restriction rebuild, lost sign, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy keyed relations with one labelled matching record.
- Negative: adversarial skew, hash collisions, equal aggregates/different sources, empty
  fibres, repeated points, and blind targets.
- Baselines: cuckoo/FKS dictionaries, four-list joining, P1553 R4, rho, and BSGS.
- Hash-join correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only after zero semantic errors at four sizes, bounded skew, full rank/logs,
  100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on supplied records, one missed/false match, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p02_keyed_stream_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p02_hash_skew_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This is a scoped transplant rejection, not a statement against GRACE. All prospective
evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Expand one proposed endpoint record and hash key to primitive curve operations and preserve the first source-incidence or super-cap bucket dependency.
