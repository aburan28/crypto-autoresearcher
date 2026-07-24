# Pre-ID duplicate draft — Luby LT degree-peeling source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T03`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_source_neighbor_graph_and_degree_one_peeling`.
- Class/risk/lane: algorithm / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a successful ripple, recovered packet, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-derived rateless checks over signed factor-base occurrences have a robust-solition-like
degree law and a nonvanishing degree-one ripple. LT peeling would recover exact relation sources
with sub-rho work, supply full-rank factor logs, and support 100 blind masked descents.

## Mechanism-new operation

LT decoding peels a supplied sparse bipartite erasure-code graph whenever an output symbol has one
unknown neighbor. It counts only if the endpoint emits source-free sparse checks and their exact
neighbor labels, and if each peeled symbol is biconditional with an elliptic occurrence. Replacing
a dense relation hypergraph by an already supplied fountain graph or changing the degree
distribution is a representation/control, not a source constructor.

## Assumptions

1. Endpoint data emits rateless sparse checks without enumerating source combinations.
2. Check values and neighbor sets preserve signs, multiplicities, and exceptional strata.
3. The degree-one ripple persists under adversarial restrictions and fresh masked targets.
4. Peeling returns complete exact tuples and not only aggregate symbols or existence certificates.
5. Check generation, overhead, retries, replay, rank, logs, descent, and memory meet both caps.

## Semantic fingerprint

`public_endpoint_rateless_checks | sparse_occurrence_neighbor_graph | degree_one_ripple_peeling | exact_signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-d_L02_kahn_topological_source_peeling_preid_duplicate.md` — peeling assumes an explicit dependency graph and provenance.
2. `ideas/rejected/preallocation/20260721-c_K05_luby_mis_source_peeling_preid_duplicate.md` — a different Luby process still begins from supplied source adjacency.
3. `ideas/rejected/preallocation/20260719-c_C11_cuckoo_hash_source_peeling_preid_duplicate.md` — degree-one peeling cannot create missing source buckets.
4. `ideas/rejected/ECDLP-IDEA-132_high_dimensional_expander_sheaf_decoder_hypothesis.md` — supplied sparse local views remain the shared obstruction.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain the frontier.

## Closest primary literature

- Luby, [LT Codes](https://doi.org/10.1109/SFCS.2002.1181950), analyzes rateless sparse encoding and peeling from supplied source-symbol neighbor sets.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but not rateless source checks or labels.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the endpoint check generator, ripple theorem for exact elliptic sources,
occurrence inverse, or complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, factor base, check generator, degree law, neighbor encoding, ripple policy, restrictions, masks, and verifier.
- Build target-independent seed/state within `B^(9/4+o(1))`, excluding source tables and relation catalogues.
- For known-log endpoints, charge every generated check, neighbor label, XOR/field operation, ripple update, stall/restart, source replay, and relation verification.
- Collect at least `max(d_FB+32,1000)` verified rows, retain failures/dependencies, require rank `d_FB`, and solve all factor logs.
- Reuse identical state for 100 fresh masked targets, peel/replay exact tuples, subtract masks, and verify scalars.
- Charge overhead, rare ripple failure, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state is `N^a,N^a_m`, reciprocal row/target densities
are `N^delta,N^delta_t`, check generation/peeling/replay is `N^q,N^q_m`,
rank credit is `N^r`, output is `N^o`, overhead/failure is `N^u`, and
factor-log solve is `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

An LT check explicitly names the source symbols combined into it. Public elliptic endpoints do not
provide sparse source-labelled checks. Generating neighbor sets independently of hidden sources
gives random aggregates with no exact relation meaning; conditioning them on valid sources performs
the missing source search before peeling begins.

## Proof track

Construct endpoint-only sparse checks with a restriction-uniform ripple theorem, prove exact
occurrence replay on all strata, full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Show neighbor labels derive from source enumeration, exhibit identical check streams with different
fibres, force ripple extinction, or charge check traffic/state to exponent at least `0.50`.

## Positive and negative controls

- Positive: ordinary LT erasure instances with supplied neighbor sets and planted symbols.
- Negative: source-free random checks, stalled ripples, equal-check different-source fibres, duplicate labels, empty restrictions, and blind targets.
- Baselines: Kahn/cuckoo peeling, IDEA-132, P1553 R4, rho, and BSGS.
- Packet recovery or one valid relation remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public check generation, zero semantic errors at four sizes/all strata, overhead and miss bounds at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing neighbor list, stalled exact-positive fibre, false peel, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t03_check_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t03_ripple_failures.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t03_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not LT codes. A healthy ripple, recovered packet, or
verified relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a
breakthrough.

## Exactly one next executable action

1. Audit one proposed endpoint check and list every byte needed to derive its neighbor occurrence labels without enumerating relation sources.
