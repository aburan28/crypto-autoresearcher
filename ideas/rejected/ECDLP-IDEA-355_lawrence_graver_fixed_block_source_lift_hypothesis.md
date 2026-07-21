# ECDLP-IDEA-355 — Lawrence–Graver fixed-block source lift

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `rejected_solver_substitution_fixed_block_premise_fails`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an integer-program solution or valid tuple is not an ECDLP break.

## Falsifiable hypothesis

One-hot coloured sources and complete elliptic addition compile into a target-independent fixed-bimatrix Lawrence or `n`-fold integer program whose Graver-best augmentation reaches exact relations and blind descents below rho.

## Mechanism-new operation

The screened operation is **encode factor choices in a fixed-block Lawrence lift, start from public slack feasibility, and use Graver augmentation to recover exact sources**. It is distinct only if block dimensions and entries are independent of `B,N,target` and do not contain scalar logs, pair transitions, or a nonlinear source oracle.

Minimum-interface correction: a canonical optimum or all feasible sources are unnecessary. A target-labelled, subset-stable exact feasibility bit under arbitrary dyadic deck restrictions, with `O(log B)` charged IP calls, suffices to recover one tuple.

## Assumptions

1. Complete elliptic addition and target equality have a fixed-width integer linearization.
2. All coefficients are public coordinates rather than hidden scalar labels.
3. Source-free restricted feasibility is exact and subset-stable on every stratum, whether obtained from a feasible start or a decision algorithm.
4. Native augmentation and source output meet the complete gates.
5. Carries, products, branches, feasibility, augmentation, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`one_hot_coloured_sources | addition_compatible_Lawrence_lift | fixed_bimatrix_nfold_IP | subset_stable_exact_feasibility_decision | dyadic_source_bisection | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`; coordinate/addition-circuit expansion does not by itself remove source traffic.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the exact public source-resolving compiler is the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; arithmetic source-fibre generation, not its solver, remains open.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; exact ancestry survives compilation.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-faithful representations retain witness-scale state.

## Closest primary literature

- Hemmecke, Onn, and Romanchuk, [N-fold integer programming in cubic time](https://doi.org/10.1007/s10107-011-0490-y), gives `O(n^3 L)` for a fixed bimatrix; it does not provide a fixed elliptic linearization.
- De Loera, Hemmecke, Onn, and Weismantel, [N-fold integer programming](https://arxiv.org/abs/math/0605242), proves polynomial solvability for the stated fixed structure.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives nonlinear finite-field equations rather than a fixed-width integer matrix.

No checked source establishes the required compilation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze one-hot variables, signs, strata, integer encoding, matrices, masks, and verifier.
2. Compile a target-independent fixed bimatrix and target right-hand side without scalar labels.
3. Decide restricted known-log feasibility, bisect to one exact tuple, and replay it.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Reuse the identical matrix for fresh masked targets.
6. Convert one-hot variables to sources, substitute logs, remove masks, and verify `[x]P=Q`.
7. Charge encoding, coefficients, carries, auxiliary variables, feasibility, Graver augmentation, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(1/5)` and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,1/5+delta+q-r+o,ell,delta_t+q+o+u,1/5)`

`mu=max(a_m,q_m,1/5+o,ell_m,u)`.

Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are `N^(1/2+o(1))`; BSGS memory is `N^(1/2+o(1))`. Even granting fixed blocks with `n≈B`, the cited cubic native bound is `B^3=N^0.6`.

## Likely fatal obstruction

Linear group equality needs scalar coordinates, which are the unknown factor logs. Coordinate-only complete addition is nonlinear; products, branches, carries, or pair transitions make block width or entries grow with `B` or `N`. Taking `n=5` instead puts `Theta(B)` choices inside each block and leaves the fixed-bimatrix theorem. This is an application failure, not a lower bound for arbitrary IP.

## Proof track

Give a symbolic fixed-width public matrix with no scalar/source advice, prove subset-stable exact feasibility plus bisection, and derive sub-gate decision/augmentation costs.

## Disproof track

Show one coefficient is a factor log, block width grows with `B`, nonlinear constraints restore transitions, or native work reaches exponent `0.50` or more.

## Positive and negative controls

- Positive: a cyclic group with deliberately supplied scalar coordinates and fixed linear constraints.
- Negative: identical public curve-coordinate decks with hidden scalar labels permuted.
- Baselines: IDEAs 034/049/081/137/198, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a fixed-width public linearization, subset-stable source-free exact feasibility plus charged bisection, zero errors, 1,000 rows, 100 blind descents, and complete `lambda,mu<=0.45`.
- Falsify on any factor-log coefficient, growing block, source transition, `B^3` augmentation, or exponent at least `0.50`.
- Solver correctness or a valid toy relation cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-355/fixed_bimatrix_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-355/scalar_label_circularity.md`
- `ideas/artifacts/ECDLP-IDEA-355/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-355/cost_analysis.md`

## Interpretation boundary

This rejects the specified fixed-block compilation, not integer programming. All checks would be toy, heuristic, model-bound, and novelty-unverified. Correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-355/fixed_bimatrix_obligations.md` with one symbolic complete elliptic-addition block and audit every coefficient and auxiliary variable for scalar or pair-source advice.
