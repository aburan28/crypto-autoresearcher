# ECDLP-IDEA-243 — Pfaffian zero-locus derivative router

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_pfaffian_pencil_materializes_source_tensor`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A compact endpoint-conditioned skew pencil has Pfaffian zero locus exactly equal to the coloured five-source relation fiber, and complementary Pfaffians or Pfaffian derivatives recover the exact point coordinates on its corank-two branch.  The closed vanishing condition would avoid IDEA-212's nonzero-minor feasibility mismatch and support full blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the relation fiber as a skew pencil, test Pfaffian vanishing, and use Pfaffian-adjugate derivatives as an exact source coordinate residue**.  The proposed closed zero locus differs syntactically from IDEA-212's principal-pivot feasibility condition and from IDEA-050's matchgate evaluation.  Semantic review nevertheless finds that a faithful pencil entry set is the same source tensor, while derivative conditioning is IDEA-194/P1536-style source localization.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. The skew pencil is derived from the public endpoint and factor deck without one row, column, or coefficient per source tuple.
2. The relevant corank is exactly two on simple accepted fibers and complementary Pfaffians determine every signed source coordinate canonically.
3. All exceptional ranks, signs, repeats, infinity charts, coefficient growth, and false Pfaffian branches are handled.
4. Pencil setup, Pfaffian evaluation, derivatives, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_skew_pencil | pfaffian_closed_zero_locus | complementary_pfaffian_derivatives | exact_point_atoms | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate compression barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank tensor/value-matrix boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the exact symmetric-square aggregate boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact one-transition norm and dense composition control.

## Closest primary literature

- Knuth, Overlapping Pfaffians, [https://arxiv.org/abs/math/9503234](https://arxiv.org/abs/math/9503234), gives identities among Pfaffians of a supplied skew matrix.
- Buchsbaum and Eisenbud, Algebra structures for finite free resolutions, [https://doi.org/10.2307/2373926](https://doi.org/10.2307/2373926), uses Pfaffians to describe supplied codimension-three structures, not an elliptic pencil compiler.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies the nonlinear relation that the pencil would still have to encode.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, compile each endpoint into the skew pencil without expanding the relation tensor or conditioning on a known source.
3. Test the exact rank stratum, evaluate complementary Pfaffians and derivatives, map the residues to all signed factor points, and independently verify the elliptic sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
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

Pfaffian identities operate after a skew matrix is supplied.  Encoding generic five-source incidence into its entries materializes the source tensor or a matchgate network, while a compact basis-covariant pencil preserves only a subspace.  Conditioning complementary Pfaffians on the relevant corank either enumerates the vanished source positions or recreates the P1536 derivative-localization problem.

## Proof track

Construct a sub-rho pencil directly from compact elliptic equations and prove a source-biconditional corank-two/Pfaffian-derivative theorem on every stratum with complete exponents at most 0.45.

## Disproof track

Reduce any faithful pencil to the explicit source tensor or matchgate network, exhibit equal Pfaffian jets with different point sources, or prove pencil size, conditioned minors, output, or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: small supplied skew pencils with known corank-two kernels and independently checked complementary Pfaffians.
- Negative controls: basis-congruent pencils, source-label permutations, IDEA-050, IDEA-194, IDEA-212, dense Pfaffians, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a pencil description and Pfaffian/derivative evaluation of exponent at most 0.45, exact source recall with zero false sources, no relation tensor, full row rank and factor logs, 100 blind descents at two largest future toy sizes, and complete lambda and mu at most 0.45.  Any source-indexed matrix, basis-dependent atom, missed rank stratum, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-243/pfaffian_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-243/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-243/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-243/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-243/pfaffian_source_theorem.md` proving a compact endpoint skew-pencil/source biconditional or a reduction showing that every faithful pencil materializes the source tensor.
