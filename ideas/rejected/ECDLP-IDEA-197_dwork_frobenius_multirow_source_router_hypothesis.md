# ECDLP-IDEA-197 — Dwork–Frobenius multirow source router

## Status and claim labels

- Class: `arithmetic-representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_frobenius_trace_counts_without_source_splitting`
- Cohort: `20260718-d`
- Evidence scale: literature and cost audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective tests are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Frobenius trace or point count is not an ECDLP break.

## Falsifiable hypothesis

A target-parametrized five-source fiber admits a low-rank Dwork/rigid-cohomology Frobenius module whose nonlinear batch traces identify many supported targets, and whose Hasse-residue splitting emits multiple independently ranked exact signed sources per batch with complete cost below rho and BSGS.

## Mechanism-new operation

The operation is **target-batch Frobenius trace localization followed by residue-to-source splitting**. It is not merely faster point counting: the load-bearing claim is an exact labelled inverse from a cohomological state to every source tuple. The audit routes ordinary traces to aggregate invariants and the splitting step to dense quotient/source algebra, so the current formulation is a representation backend rather than the missing router.

## Assumptions

1. Public generic ordinary `E/F_p`, prime order `N`, factor base `B=N^beta`, and target are fixed.
2. The fiber family has a Frobenius module of rank `N^h` constructed without dense elimination.
3. Batch traces distinguish supported targets and output more than one independent exact row per charged batch.
4. Residue splitting recovers signs, repeats, infinity, and nonreduced multiplicity.
5. Precision, module construction, failed targets, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`target_parametrized_five_source_fiber | low_rank_Dwork_Frobenius_module | nonlinear_batch_trace_localization | Hasse_residue_exact_source_split | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1477`, the serial-state compression boundary.
2. `inputs/ledger_inventory.json` — imported `P1478`, the exact one-transition norm and dense-composition control.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-H642`, a public support-router hypothesis.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate-root/source-loss boundary.

## Closest primary literature

- Dwork, [On the rationality of the zeta function of an algebraic variety](https://doi.org/10.2307/2372974), supplies cohomological trace rationality, not exact rational-point unranking.
- Dwork, [On the zeta function of a hypersurface](https://doi.org/10.1007/BF02684275), develops the hypersurface trace setting but does not provide a labelled source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the fiber equations.

No checked source gives the complete multirow operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the family, cohomology model, precision, batch targets, residue charts, masks, and verifier.
2. Construct the module and prove its rank/precision bounds without expanding the source fiber.
3. Trace known-log target batches, localize supported endpoints, split exact sources, and verify them.
4. Preserve failed traces, multiplicities, residues, signs, collisions, infinity, and output lists.
5. Collect full-rank rows, solve and verify factor logs.
6. Apply the identical module and splitter to fresh masks `Q+[r]P`.
7. Recover and verify the scalar after subtracting masks.
8. Charge construction, precision, traces, splitting, rank, descent, verification, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs the same time and memory. Let module setup be `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, batch trace plus split `N^q,N^q_m`, ranked rows/batch `N^r`, output/ambiguity `o,u`, and factor-log linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both exponents must be at most `0.45`; point-count correctness is non-promoting.

## Likely fatal obstruction

The relevant fiber degree and Betti/cohomology rank grow with the `B^3` or `B^5` source state. Frobenius traces count or aggregate rational points and cannot label same-trace source tuples. Extracting individual residues requires primary decomposition/eigenvectors of the dense quotient algebra and restores the source traffic this representation was meant to remove.

## Proof track

Bound module rank and precision below the P1515 setup gate, prove a batch trace-to-many-independent-sources biconditional including nonreduced fibers, and derive `lambda,mu<=0.45`.

## Disproof track

Lower-bound module rank by fiber degree/Betti number, exhibit trace-indistinguishable source tuples, reduce residue splitting to dense quotient decomposition, or show complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: low-degree hypersurfaces with supplied rational-point decomposition and exact trace checks.
- Negative control: zeta/trace counts without labels, dense quotient algebras, resultants, and source-indexed residues.
- Negative control: rho, BSGS, known-log batches, and fresh blind masks.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a proved module rank below `B^2.25`, multiple independent exact rows per batch, 100% source/multiplicity recall, zero false tuples, and `lambda,mu<=0.45`. Rank/state `Omega(B^3)`, aggregate-only traces, one missed source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective rank theorem: `ideas/artifacts/ECDLP-IDEA-197/dwork_module_rank_theorem.md`
- Prospective residue-source specification: `ideas/artifacts/ECDLP-IDEA-197/residue_source_split_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-197/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified arithmetic representation work. Any finite check is toy; projections are heuristic and model-bound. A trace, point count, exact source, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-197/dwork_module_rank_theorem.md` proving a sub-`B^2.25` target-family Frobenius module with exact residue-source splitting or deriving a fiber-degree/Betti lower bound that forces `Omega(B^3)` state.

