# ECDLP-IDEA-331 — MERA tensor-renormalization source decoder

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_tensor_rg_consumes_source_tensor_and_truncation_discards_witness_labels`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low bond dimension, correct tensor contraction, valid relation, or toy witness is not an ECDLP break.

## Falsifiable hypothesis

The six-list elliptic incidence tensor has a target-independent MERA/tensor-renormalization flow with bond dimensions inside `B^(9/4)` whose inverse causal cone returns exact signed source tuples and supports `B^(5/4)` fresh-target queries.

## Mechanism-new operation

The screened operation is **compile the relation predicate as a multiscale tensor network, alternate disentanglers and isometries to truncate bonds, contract coarse tensors, and invert an accepted causal cone to exact source indices**. This merges with IDEAs 035, 050, 060, 253, 259, 324, and P1421: the tensor entries or factor graph are supplied source incidence, while lossy bond truncation preserves aggregates rather than an exact witness. Exact source tags restore bond dimension or output state.

## Assumptions

1. The elliptic incidence tensor is constructible implicitly without enumerating pair/source entries.
2. One target-independent renormalization flow has provably bounded exact bond dimension over the finite field.
3. Every accepted coarse state has a canonical exact causal-cone inverse on all source strata.
4. Tensor construction, optimization, bonds, contractions, truncation error, inverse, output, rank, logs, descent, and memory are charged.
5. The same flow handles blind masked targets without retraining or target advice.

## Semantic fingerprint

`six_list_incidence_tensor | multiscale_disentangler_isometry_flow | exact_bond_truncation | causal_cone_source_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-P1421-EXACT-TRANSPOSED-MATRIX-CONTROL`, the supplied exact pair-state tensor control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full pair-state and tensor-train rank boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H670`, the exact bilinear source-leaf batch hypothesis.
4. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless witness-edge boundary.

## Closest primary literature

- Vidal, [Entanglement renormalization](https://doi.org/10.1103/PhysRevLett.99.220405), introduces multiscale coarse-graining for supplied quantum states.
- Levin and Nave, [Tensor renormalization group approach to two-dimensional classical lattice models](https://doi.org/10.1103/PhysRevLett.99.120601), contracts supplied local tensors with controlled approximations.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a compact source tensor or exact inverse causal cone.

No checked source proves exact finite-field bond truncation, implicit tensor construction, or full ECDLP descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, six coloured decks, tensor grammar, multiscale topology, bond rule, source policy, masks, and verifier.
2. Build the network without source-table materialization, contract known-log targets, invert accepted causal cones to exact tuples, and verify each relation.
3. Collect at least `B` independent rows, solve every factor log, and independently verify them.
4. Reuse the identical network and flow for fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain all branches, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, tensor construction/contraction excluding output `N^q,N^q_m`, rank credit `N^r`, exact causal-cone output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All tensor entries or iterators, optimization, bond dimensions, contraction intermediates, exactification, tags, output, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Tensor RG compresses a supplied tensor by discarding microscopic information judged irrelevant to an aggregate. The elliptic incidence tensor is itself the missing source relation. Requiring exact inverse causal cones for every witness prevents generic truncation; retaining source provenance restores large bonds or explicit tensor state.

## Proof track

Prove implicit tensor construction, exact bounded bonds, a bijective all-strata causal-cone inverse, relation rank, factor-log completion, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit equal coarse tensors with different source supports, prove a bond-rank lower bound for the frozen flattening, or show construction materializes `B^3` incidence state.

## Positive and negative controls

- Positive: supplied exact low-bond tensor networks with labelled leaves must contract and invert perfectly.
- Negative: equal-coarse-tensor/different-support fixtures and approximate truncations must not emit preferred elliptic points.
- Baselines: IDEAs 035/050/060/253/259/324, P1421, dense contraction, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact source-free tensor and inverse theorems, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if the source tensor is supplied, any exact bond or intermediate reaches `B^3`, a witness is lost, or either exponent reaches `0.50`.
- Approximate aggregate accuracy is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-331/source_tensor_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-331/bond_rank_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-331/coarse_support_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-331/cost_analysis.md`

## Interpretation boundary

This rejects the specified exact-source tensor-RG route, not tensor networks generally. Low bond dimension or a correct supplied-tensor contraction is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-331/source_tensor_input_receipt.md` specifying every local tensor entry and proving whether it can be evaluated without a source-edge oracle.
