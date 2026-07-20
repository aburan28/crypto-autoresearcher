# ECDLP-IDEA-253 — Injective-MPS gauge source lift

## Status and claim labels

- Class: `tensor_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_mps_tensor_and_gauge_require_source_state`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation tensor has a compact injective matrix-product-state representation whose canonical form fixes all internal gauges.  Transfer-operator fixed points and canonical tensors would then expose exact factor-source coordinates for complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the endpoint tensor as an injective MPS, put it in canonical gauge, and invert canonical local tensors/transfer fixed points to exact factor sources**.  Injectivity removes ordinary MPS gauge ambiguity but not the need to supply the global relation tensor or a point-to-physical-index dictionary.  The operation therefore merges with IDEA-035 tensor rank, IDEA-135 decomposable circuits, IDEA-142 linear pencils, and IDEA-231 operator tuples when construction and source lift are charged.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A target-uniform MPS tensor of sub-rho bond/physical description is derived from compact elliptic equations without enumerating source tuples.
2. The representation is injective on every required stratum and canonicalization is exact over the prime field with bounded extension/precision costs.
3. Canonical physical indices and transfer fixed points map biconditionally to all signed factor points rather than only aggregate correlations.
4. Tensor construction, canonicalization, contraction, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_relation_tensor | compact_injective_MPS | canonical_gauge | transfer_fixed_point_source_atoms | exact_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/tensor barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the tensor-train and full-rank negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear feature-rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact transition and dense composition control.

## Closest primary literature

- Perez-Garcia, Verstraete, Wolf, and Cirac, Matrix Product State Representations, [https://arxiv.org/abs/quant-ph/0608197](https://arxiv.org/abs/quant-ph/0608197), derives canonical forms for a supplied multipartite tensor/state.
- Fannes, Nachtergaele, and Werner, Finitely correlated states on quantum spin chains, [https://doi.org/10.1007/BF02099178](https://doi.org/10.1007/BF02099178), constructs finite-bond states from supplied transfer data but gives no elliptic point inverse.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies compact equations but not a compact source-faithful MPS.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the endpoint MPS tensors and physical dictionary without expanding the B^5 relation signal or assigning one physical symbol per source point.
3. Canonicalize the MPS, evaluate transfer fixed points/local tensors, map every canonical physical atom to exact signed factor points, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and source inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected parameter, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by source ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every constructor coefficient, represented state, preprocessing query, failed target, branch,
source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation,
and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness
or relation validity alone has no performance meaning.

## Likely fatal obstruction

MPS canonical form compares representations of a supplied state; it does not construct the state from one endpoint.  A source-faithful physical alphabet or local tensor stores point identities, while compression into small bond dimension preserves correlations but not a canonical list of global source words.  Injectivity fixes gauge only up to the represented state and does not solve source unranking.

## Proof track

Give a compact endpoint-to-MPS compiler, prove injectivity and a canonical all-source inverse on every stratum, and derive complete exponents at most 0.45.

## Disproof track

Reduce tensor construction to the explicit relation signal, exhibit gauge-equivalent/correlation-equivalent states with different point labels, or prove bond/physical/output or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied injective MPS tensors with independently known canonical forms and physical source words.
- Negative controls: gauge transforms, source-label permutations, low-bond aggregate states, IDEA-035, IDEA-135, IDEA-142, IDEA-231, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-blind MPS compiler and physical dictionary of exponent at most 0.45, exact all-source recall with zero false sources, bounded bond dimension, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  Supplied tensors, source-coloured physical indices, correlation-only output, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-253/injective_mps_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-253/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-253/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-253/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-253/injective_mps_source_theorem.md` proving a compact endpoint MPS/canonical source inverse or a relation-tensor and physical-dictionary source-deck no-go.
