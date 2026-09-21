# Pre-ID duplicate draft — cuckoo-plus-IBLT source peeling

## Status and claim labels

- Prospect: `20260719-c-C11`; no canonical ID allocated
- Class / risk / lane: `composite_hash_dictionary_peeling` / `conservative` / pre-ID screen
- State: `direct_semantic_repeat_cuckoo_placement_plus_IBLT_peeling`
- Evidence: complete-corpus and primary-literature review only; no run
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Hash endpoint-derived relation keys into two cuckoo candidate cells, use Pagh–Rodler displacement/rehashing for placement, then add an IBLT-style count/XOR peeling layer to recover exact signed factor points. Reuse the composite table for independent rows and fresh blind descent below rho/BSGS.

## Mechanism-new operation

This is explicitly a composite, not a new cuckoo-native operation: Pagh–Rodler cuckoo hashing assigns supplied keys to two locations and resolves conflicts by displacement/rehashing, while the added IBLT control supplies count/XOR cells and peeling. It counts only if inserted keys are endpoint-derived without enumerated tuples and the composite returns exact occurrences rather than merely storing known keys. As specified, the peeling stage is a direct occupied control.

## Assumptions

1. A compact public key stream is biconditional with every signed/chart-complete relation.
2. Key generation, hashes, insertions, displacement, rehash failures, restrictions, replay, rank, logs, descent, and memory are charged.
3. Hash collisions are verified exactly and do not erase occurrence provenance.
4. The frozen table serves calibration and fresh scalar-blind targets without target-key insertion proportional to sources.
5. No explicit relation keys, source tags, planted peel order, large-prime table, or uncharged random oracle is admitted.

## Semantic fingerprint

`public_endpoint_relation_keys | cuckoo_two_choice_displacement_and_rehash | IBLT_count_XOR_peeling_control | key_to_signed_occurrence_replay | blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted existence and replay are required.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public exact source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: explicit key/source generators restore materialization.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: key-incidence edges remain source records.
5. `inputs/ledger_inventory_20260719.json` — imported `P1476`: membership, output, rank, descent, and memory must be charged.

## Closest primary literature

- Pagh and Rodler, [Cuckoo Hashing](https://doi.org/10.1016/j.jalgor.2003.12.002), stores supplied keys in a two-choice dictionary.
- Goodrich and Mitzenmacher, [Invertible Bloom Lookup Tables](https://arxiv.org/abs/1101.2245), is the closest explicit inserted-key peeling control.
- Semaev's [summation polynomials](https://eprint.iacr.org/2004/031) do not supply keys; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) remains the baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, key map, hash family, restrictions, and verifier.
2. Build target-independent table/state within `B^(9/4+o(1))` without inserting tuple keys.
3. For known-log targets, decide exact restrictions and peel/replay five verified occurrences.
4. Preserve failed cycles/dependencies, collect at least `B` independent rows, and solve factor logs.
5. Reuse state on fresh scalar-blind `Q+[t]P`, recover/verify a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge key production, hashes, rehashes, misses, output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; Pollard rho time and BSGS time/memory remain `0.50` controls.

## Likely fatal obstruction

Cuckoo hashing stores keys already known. Exact relation keys and source tags are the missing catalogue; hashing coarser endpoints causes collisions, while verification/replay restores source search. Peeling cycle behavior affects storage, not generation of rare accepting tuples. This is a direct ECDLP-stage semantic repeat of pre-ID FKS dictionary `A11` and IBLT controls and also merges with IDEAs `053/347/353/362/374`.

## Proof track

Construct keys endpoint-only, prove exact restricted membership/source replay and bounded rehash costs, then close full descent.

## Disproof track

Charge inserted keys, force a hash collision/cycle or same-key/different-source pair, or exceed the gates.

## Positive and negative controls

- Positive: supplied sparse key sets with labelled cuckoo placements.
- Negative: same hashes with different keys/sources, cyclic components, exceptional charts, restrictions, blind targets.
- Baselines: IDEAs `053/347/353/362/374`, pre-ID `A11`, IBLT, explicit hash tables, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with no enumerated key insertion, exact replay, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing key, one collision/source mismatch, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-c/c11_key_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-c/c11_hash_cycle_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-c/c11_cost_analysis.md`

## Interpretation boundary

This rejects the composite transplant, not cuckoo hashing or IBLT peeling. Successful storage, peeling, or a toy relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-c/c11_key_provenance.md` and charge every key insertion, verifier lookup, and rehash.
