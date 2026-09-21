# Pre-ID duplicate draft — Brandt multigrid source hierarchy

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R03`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_hierarchy_and_smoother`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; fast toy convergence, a relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, endpoint-defined source compatibility has a public nested-grid
representation: smoothing removes local source error and coarse correction transports the
remaining global error. A V-cycle returns exact signed occurrences and completes factor logs
and 100 blind descents with time and memory exponents at most `0.45`.

## Mechanism-new operation

Multigrid alternates relaxation on a fine discretization with restriction, coarse solving, and
prolongation across a hierarchy. It counts only if every level and transfer is compiled from
public endpoints without a source graph, while exact correction retains signs, multiplicities,
and source identities. Coarsening a materialized relation graph is a representation control.

## Assumptions

1. Public endpoints define nested spaces and local smoothers without enumerated tuples.
2. Restriction/prolongation are exact on all exceptional group-law strata.
3. Coarse variables do not aggregate away rare source identity or empty-fibre semantics.
4. V-cycle count, level state, and exact precision satisfy both resource caps.
5. The hierarchy is target-independent and supports arbitrary source restrictions and blind targets.

## Semantic fingerprint

`public_endpoint_nested_source_spaces | smooth_restrict_coarse_correct_prolong | exact_multilevel_source_inverse | restriction_stable_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-d_D12_multilevel_coarsened_source_partition_preid_duplicate.md` — graph coarsening starts from supplied source incidence.
2. `ideas/rejected/preallocation/20260719-a_A08_nested_dissection_schur_source_separator_preid_duplicate.md` — a hierarchy and Schur complements preserve a supplied matrix.
3. `ideas/rejected/preallocation/20260720-a_E04_baker_layered_source_graph_preid_duplicate.md` — layering assumes the source graph and may lose cross-layer witnesses.
4. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — smoothing is a downstream relaxation.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — endpoint-derived exact restricted source return remains the owner.

## Closest primary literature

- Brandt, [Multi-Level Adaptive Solutions to Boundary-Value Problems](https://doi.org/10.1090/S0025-5718-1977-0431719-X), uses multiple supplied discretization levels and interlevel transfer.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), provides equations but no nested source spaces.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source constructs the claimed endpoint-only hierarchy or signed inverse; novelty is
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, level spaces, smoothers, transfer maps, coarse solver, restrictions, strata, and verifier.
2. Build all target-independent levels within `B^(9/4+o(1))`; forbid tuple lists, source graphs, scalar residues, or decomposition oracles.
3. For each known-log target, run the exact V-cycle, replay a signed occurrence, and verify the curve sum before admitting a row.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs.
5. Reuse the identical hierarchy on 100 fresh masked targets, recover points, subtract masks, and verify every scalar.
6. Charge level construction, smoothing, transfers, coarse solves, cycles, failures, output, rank, logs, bit operations, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, V-cycle work/workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log cost `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS retain exponent `0.50`.

## Likely fatal obstruction

A useful grid requires a locality metric and incidence operator on the hidden source space.
Building those objects materializes the missing source catalogue. Coarse restriction also merges
rare and empty fibres; restoring exact occurrence labels through prolongation recreates fine state.

## Proof track

Prove endpoint-only levels, uniform approximation and smoothing properties, exact transfer on
all strata, subcap level complexity, and a restriction-stable signed inverse through blind descent.

## Disproof track

Show one source-labelled node/edge, a coarse collision between empty and nonempty fibres,
target-dependent rebuilding, cycle/precision growth, replay ambiguity, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy elliptic-incidence hierarchy with a planted unique multilevel source.
- Negative: permuted source labels with identical coarse operators, rare singleton fibres,
  empty fibres, exceptional additions, anisotropic hard modes, and blind targets.
- Baselines: heavy-edge coarsening, nested dissection, P1553 R4, rho, and BSGS.
- Linear V-cycle convergence is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact controls at four sizes/all strata, full rank/logs, 100 blind descents,
  both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied hierarchy edge, coarse false positive/negative, source-label loss,
  cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r03_level_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r03_coarse_collision_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r03_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not multigrid. A V-cycle speedup or valid relation is toy,
heuristic, model-bound, and novelty-unverified, not an ECDLP breakthrough.

## Exactly one next executable action

1. Expand the proposed fine-to-coarse restriction map on one endpoint and preserve the first source-labelled incidence or prove exact label-free transfer within both caps.
