# ECDLP-IDEA-136 — Folded-Wronskian branch rank condenser

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_supplied_subspace_condenser`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: any future finite test would be `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; retained rank, correct branches, or a valid toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A folded-Wronskian family applied directly to public branch-evaluation operators preserves the span of every accepted source branch while compressing all forward/backward transition spaces to sub-rho dimension. A small seed list then yields exact source-labelled intersection vectors for relation collection and blind descent without constructing the full evaluation matrices.

## Mechanism-new operation

The proposed operation is **rank condensation before transition-space materialization**: compile folded-Wronskian maps into the factor-polynomial/serial-addition circuit, condense each target branch module, intersect condensed images, and invert surviving columns to exact sources.

After audit the record is merged/rejected. Published condensers preserve the rank of a subspace already supplied by a basis or evaluation oracle; they do not construct the rare source subspace from an endpoint. Applying them after the value matrix, quotient, branch basis, or source rows exist is a linear-algebra backend already bounded by IDEA-056, IDEA-123, and ledger `ECFG-NR-1421`. A successor would need a new direct circuit-to-condensed-source identity, not a new seed or rank routine.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of size `N`, target `Q`, and factor base `F` of size `B=N^beta` are fixed.
2. A target-independent folded-Wronskian seed family is evaluable on the compact elliptic transition circuit without enumerating branch vectors.
3. At least one seed preserves all accepted source directions and admits an exact source inverse, including multiplicity and exceptional strata.
4. Condenser generation, seed trials, rejected seeds, branch output, rank, factor logs, blind descent, and peak memory are charged.
5. No scalar-indexed basis, dense value matrix, quotient basis, or post-hoc source label is allowed.

## Semantic fingerprint

`compact_transition_circuit | folded_Wronskian_rank_condenser | pre_materialization_branch_sketch | rank_preserving_intersection | exact_source_column_inverse`

The pre-materialization source identity would be new. A condenser on a supplied subspace is the rejected duplicate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact value matrices and fixed block/tensor sketches remain full rank.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H669`, which tested low-rank/common-prefix row-norm compression and retained source-loss as the obstruction.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H670`, where exact rank-four factor-root hyperplanes still require all root incidences.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose one-transition compact module densifies at composition.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where every tested public low-dimensional factor-log feature space misses the true log vector.

## Closest primary literature

- Guruswami and Kopparty, [Explicit subspace designs](https://doi.org/10.1007/s00493-014-3169-1), construct folded-Wronskian subspace designs but assume the subspaces to be protected are already represented.
- Forbes and Guruswami, [Dimension expanders via rank condensers](https://arxiv.org/abs/1411.7455), formalize rank condensers and dimension expanders, not endpoint-to-source generation.
- Forbes and Shpilka, [On identity testing of tensors, low-rank recovery and compressed sensing](https://doi.org/10.1145/2213977.2213995), use rank-concentration tools for supplied algebraic objects.

No checked source supplies the missing elliptic circuit-to-source map. Novelty remains unverified, and the specified backend is semantically occupied.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, transition circuit, seed family, exceptional-case policy, and independent source verifier.
2. Produce condensed forward/backward operators directly from the circuit, recording construction cost without a full branch basis.
3. Intersect condensed images for known-log targets, lift every survivor to exact signed factor points, and verify elliptic addition.
4. Collect `B+sigma` rank-`B` rows, solve and verify factor logs.
5. Repeat unchanged on fresh masked targets, enumerate ambiguity, and accept only `[x]P=Q`.
6. Charge construction, all seeds, output, rank, linear algebra, descent, verification, and memory against rho/BSGS.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let direct sketch construction/memory be `N^a,N^a_m`; seed count `N^s`; condensed dimension `N^c`; query/source-lift time and working memory be `N^q,N^q_m`; inverse densities `N^delta,N^delta_t`; output `o`; ambiguity `u`; and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,s+c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
If constructing the input subspace costs its full dimension, `a` already restores the occupied barrier. Toy ranks do not prove asymptotic compression.

## Likely fatal obstruction

Rank condensers are oblivious maps that protect rank; they do not identify which endpoint branch is a valid factor-base source. Building the matrix/subspace they consume can be the complete relation search. Exact source inversion can also require the discarded coordinates or a source dictionary, while protecting every target/source subspace may force enough seeds or output dimension to erase compression.

## Proof track

Derive a direct algebraic identity from compact elliptic equations to condensed columns, prove a seed preserves every source with an exact inverse, and bound the full path below `0.45` without constructing a source basis.

## Disproof track

Show the condenser input is a supplied value/quotient/branch matrix, source inversion needs the original coordinates, or all-source protection forces `lambda>=1/2` or `mu>=1/2`. The current semantic reduction already rejects the specified construction.

## Positive and negative controls

- **Positive control:** planted low-rank subspaces with supplied bases and known protected dimensions.
- **Positive control:** exhaustive tiny elliptic branches with a separately supplied source matrix.
- **Negative control:** full transposed value matrices, random sketches, block-Krylov, fixed tensor trains, and factor-log feature spaces.
- **Negative control:** matched random subspaces with the same rank and coefficient sizes.
- **End-to-end control:** rho/BSGS and blind targets, with source-construction cost included.

## Quantitative promotion and falsification gates

The record is rejected at the supplied-subspace scope. A fresh ID is required only after an independently proved direct circuit-to-condensed-source identity with exact inversion and complete `lambda,mu<=0.45`. Any materialized branch/value matrix, missing source, post-hoc label, or complete exponent at least `0.5` falsifies that successor.

## Artifact plan

- Scoped reduction note: `ideas/artifacts/ECDLP-IDEA-136/supplied_subspace_reduction.md`
- Prospective direct-identity theorem: `ideas/artifacts/ECDLP-IDEA-136/direct_condenser_identity.md`
- Frozen control fixtures: `ideas/artifacts/ECDLP-IDEA-136/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-136/cost_analysis.md`

These paths are prospective; no artifact exists.

## Interpretation boundary

This is preserved rejected evidence. All claims are novelty-unverified, toy if tested, heuristic, and model-bound. Rank preservation is correctness of a linear sketch, not a source generator or ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-136/supplied_subspace_reduction.md` formalizing why every currently specified folded-Wronskian input is already an occupied materialized source/value subspace.
