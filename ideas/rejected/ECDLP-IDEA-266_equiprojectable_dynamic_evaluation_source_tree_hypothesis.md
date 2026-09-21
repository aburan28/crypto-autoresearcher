# ECDLP-IDEA-266 — Equiproj dynamic-evaluation source tree

## Status and claim labels

- Class: `algebraic_source_inversion`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_triangular_source_algebra_or_dense_branch_degree_required`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired review-required zero-run preflight
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a triangular decomposition, a lifted branch, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform equiprojectable decomposition of the five-point summation source fiber, maintained by dynamic evaluation and Hensel lifting rather than a dense Groebner basis, has bounded branching and preserves exact factor-point ancestry.  Its triangular source tree would emit enough relations and invert fresh masked targets with complete time and memory below rho and BSGS.

## Mechanism-new operation

The screened operation is **split the endpoint fiber canonically into equiprojectable triangular components, lift the components while dynamically splitting zero divisors, and read exact factor points from the resulting source-labelled leaves**.  Dynamic evaluation can postpone field factorization and keep incompatible branches separate, but it operates on a supplied zero-dimensional algebra or triangular set.  For the generic elliptic source fiber, constructing that algebra and emitting its components retains the full fiber degree.  This merges with IDEA-063 provenance-preserving subresultants, IDEA-068 elimination motifs, IDEA-084 factor-word rewriting, IDEA-120 serial-state quotients, and IDEA-194 implicit-fiber derivatives once construction and leaf output are charged.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity five, masks, variable order, and exceptional strata are frozen before targets.
2. An endpoint-only algorithm constructs a triangular/equiprojectable representation without enumerating the `B^5` source deck or a same-degree quotient algebra.
3. Dynamic zero-divisor splits retain a biconditional map from every leaf to exact signed elliptic points on smooth, repeated, singular, infinity, and nonreduced strata.
4. Triangular construction, lifting precision, component degree, splitting, leaf output, relation rank, factor logs, masked descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`summation_source_fiber | equiprojectable_triangular_decomposition | dynamic_zero_divisor_splitting | hensel_branch_lift | exact_factor_point_leaves | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1478`, whose exact sparse transition becomes a dense composed resultant.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where an amortized union loses row/source identity.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the exact zero-output boundary.
4. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.
5. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state compression control.

## Closest primary literature

- Dahan, Moreno Maza, Schost, Wu, and Xie, [Lifting Techniques for Triangular Decompositions](https://cs.uwaterloo.ca/~eschost/publications/DMSWX05.pdf), develops Hensel lifting and triangular decomposition for a supplied zero-dimensional system.
- Giusti, Lecerf, and Salvy, [A Groebner Free Alternative for Polynomial System Solving](https://doi.org/10.1006/jcom.2000.0571), gives geometric-resolution algorithms whose cost depends on solution degree.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but not a bounded-degree source-labelled triangular tree.

No checked primary source supplies the required endpoint-only source tree and complete sub-rho descent.  ECDLP novelty is not claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, signed arity, coordinate charts, triangular variable order, masks, splitting rules, and verifier.
2. For a known-log endpoint `R=[r]P`, construct its summation source ideal and an equiprojectable triangular decomposition without expanding the source deck.
3. Dynamically split every zero divisor and Hensel-lift every component; map each terminal branch biconditionally to exact signed factor points and verify their elliptic sum.
4. Collect independently verified rows until factor-base rank `B`, charging failed fibers, branch degree, source output, and rank loss.
5. Solve factor logs and verify every recovered log by scalar multiplication.
6. Apply the identical frozen construction to fresh masks `Q+[t]P`, retaining every component and ambiguity branch.
7. Substitute verified factor logs, subtract `t`, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory receipts.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one triangular construction plus exact leaf inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every polynomial coefficient, triangular-set element, component degree, split, lift, failed target, leaf, relation row, rank defect, factor log, mask, verifier call, bit operation, and live byte is charged.  Promotion requires both the time exponent and peak-memory exponent at most `0.45`; correctness alone has no performance meaning.

## Likely fatal obstruction

Equiproj decomposition is canonical only after a zero-dimensional source algebra or equivalent evaluation representation is supplied.  On the generic five-source fiber, its dimension and total leaf degree are the number of source solutions.  Dynamic evaluation changes when factorization is paid, not how much source information must be constructed or output, so exact ancestry restores the dense deck or an object of the same degree.

## Proof track

Construct an endpoint-only triangular tower with total represented degree, split count, and leaf output exponent at most `0.45`; prove all-strata biconditional point recovery, full factor-log rank, blind masked descent, and both complete exponents at most `0.45`.

## Disproof track

Reduce initial triangular-set construction to the full source algebra, prove total component degree equals the generic source-fiber degree, exhibit source collisions after compression, or show construction, output, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small radical triangular set with independently labelled roots and a known equiprojectable decomposition.
- Negative controls: the same system with labels removed, repeated/nonreduced fibers, reordered variables, dense geometric resolution, IDEA-063, IDEA-194, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only source-tree constructor of exponent at most `0.45`, exact all-strata source recall with zero false leaves, full factor-log rank, blind masked descent, and complete `lambda` and `mu` at most `0.45`.  A supplied source algebra, total represented/output degree at least `N^0.50`, ancestry loss, target-specific splitting, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-266/equiprojectable_source_tree_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-266/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-266/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-266/cost_analysis.md`

All four paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  Correct triangular lifting, a valid relation, an exact source tuple, or a toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-266/equiprojectable_source_tree_theorem.md` proving a sub-rho endpoint-only triangular source tree or the dense source-degree/output obstruction.
