# Pre-ID duplicate draft — B-tree external-memory source index

## Status and claim labels

- Prospect: 20260720-c-G05; no canonical ECDLP idea ID was allocated
- Class / risk / lane: external_memory_ordered_index / conservative / general pre-ID screen
- State: merged_rejected_storage_backend_after_source_key_materialization
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite I/O controls are toy; asymptotic transplant is model-bound and novelty-unverified
- Breakthrough claim: none; reducing block I/O for a supplied index is not an ECDLP speedup.

## Falsifiable hypothesis

Lay out endpoint-derived source keys in a high-fanout B-tree so canonical restrictions and fresh target lookups touch few blocks. Exact leaf records would replay signed occurrences, enabling relation collection, factor logs, and blind descent below rho and BSGS in bit time and memory.

## Mechanism-new operation

A B-tree maintains a height-balanced multiway search index with block splits/merges and logarithmic block transfers for supplied ordered keys. It counts only if key construction is endpoint-only, source records fit the setup cap, and total bit work as well as I/O is below the cryptanalytic gates. Reblocking an explicit large-prime/source table is a backend control.

## Assumptions

1. Exact public endpoint keys and their total order exist before source enumeration.
2. Key generation, block size, comparisons, splits/merges, cache misses, full bit traffic, restrictions, replay, rank, logs, descent, and memory are charged.
3. A leaf match is biconditional with a signed source and preserves occurrence labels.
4. Canonical restrictions map to bounded key ranges without rebuilding leaves.
5. The same on-disk/in-memory layout serves fresh blind targets.

## Semantic fingerprint

public_ordered_endpoint_records | Btree_block_split_merge_index | exact_restricted_range_lookup | leaf_record_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 requires exact source recovery, not storage locality.
2. ideas/rejected/preallocation/20260719-c_C01_elias_fano_monotone_endpoint_dictionary_preid_duplicate.md — compact monotone storage assumes exact positions.
3. ideas/rejected/preallocation/20260720-a_E07_skiplist_source_order_index_preid_duplicate.md — ordered lookup begins after source keys exist.
4. ideas/rejected/preallocation/20260720-b_F12_fusion_tree_endpoint_predecessor_preid_duplicate.md — faster word-RAM predecessor is a backend substitution.
5. ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md — hashing supplied source records does not compile them.

## Closest primary literature

- Bayer and McCreight, [Organization and maintenance of large ordered indices](https://doi.org/10.1007/BF00288683), develops B-trees for supplied ordered records and external storage.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no ordered source record compiler.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source turns B-tree blocking into endpoint-to-source information; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, record/key format, order, block size, cache model, restriction map, provenance, and verifier.
2. Construct and lay out the target-independent index within B^(9/4+o(1)) bit work/state without explicit pair-pair-singleton matches.
3. For known-log R, use exact restricted ranges to replay A_i,epsilon_i in bounded bisection; verify point equality before recording a row.
4. Collect at least max(d_FB+32,1,000) verified rows, preserve misses/dependencies, require rank d_FB, and solve factor logs.
5. Reuse unchanged state for Q+[t]P, recover a tuple, compute x, and verify the scalar.
6. Charge index construction, all record bytes and I/Os, comparisons, updates, restrictions, replay, density, rank, logs, blind descent, bit time, and peak storage/memory.

## Full rho/BSGS cost model

Let n be records, t the minimum branching parameter, b_blk bits per block, Q_R range queries, V_blk blocks visited, and C_inv replay. Native search/update takes O(log_t n) block transfers on a supplied B-tree, but bit work includes V_blk b_blk plus comparison/record costs. Set a=log_N(T_record_build+T_layout), a_m=log_N(M_index), q=log_N(Q_R(V_blk b_blk+C_compare+C_inv)+T_replay), and q_m=log_N(M_cache+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Report I/O and bit models separately; promotion requires both. Setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho/BSGS are 0.50.

## Likely fatal obstruction

B-trees reduce I/O only after exact source-bearing records are materialized. That materialization is the missing P1553 operation and full bit traffic remains charged. Coarse keys create false leaves; exact keys store the catalogue. This merges with C01/E07/F12/A11 and is not a new mathematical operation on elliptic endpoints.

## Proof track

Prove compact endpoint-only records, exact range/source biconditional, bounded bit traffic under restrictions, provenance, rank, and blind descent.

## Disproof track

Show one leaf key requires enumerated source data or that bit traffic, unlike block I/O, restores the source-sized exponent.

## Positive and negative controls

- Positive: supplied labelled records under a measured external-memory hierarchy.
- Negative: cache-resident versus cold-cache runs, equal keys with different ancestry, empty/singleton ranges, and blind targets.
- Baselines: flat files, C01/E07/F12/A11, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only record construction, exact replay, both I/O and bit caps, rank d_FB, 100 blind descents, and lambda,mu<=0.45.
- Falsify on one source-bearing record, I/O-only accounting, false range hit, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g05_record_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g05_io_bit_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g05_cost_analysis.md

## Interpretation boundary

This rejects B-tree storage as an information-flow improvement, not B-trees. Fewer I/Os or a correct lookup is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g05_record_provenance.md; do not create it under this retired pre-ID screen.
