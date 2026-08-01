# ECDLP-IDEA-372 — Pommaret–Janet involutive syzygy quotient

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_involutive_basis_is_a_grobner_backend_not_a_source_quotient`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; row or syzygy reduction in a toy Macaulay system is not an ECDLP break.

## Falsifiable hypothesis

Pommaret or Janet involutive division exposes degree-born syzygy cones of the Boolean Semaev ideal whose exact quotient removes the source-dimension obstruction and returns relation roots within the P1553 gates.

## Mechanism-new operation

The screened operation is **construct an involutive basis, partition prolongations into multiplicative cones, discard syzygy-covered rows before Macaulay expansion, and solve the resulting exact quotient for one source tuple**. It is distinct only if involutive cones remove quotient variables or source fibres rather than redundant equations, are cheaply computable before source-sized matrices exist, and preserve roots and blind descent.

## Assumptions

1. The Boolean Semaev ideal has a target-uniform involutive structure with subgate basis and cone counts.
2. Degree-born syzygies remove the dominant quotient dimension, not merely linear-algebra rows.
3. Basis construction and target specialization avoid the same degree-of-regularity and fill-in costs as Gröbner/Macaulay solvers.
4. The reduced system returns one exact signed tuple on every source stratum without post-hoc selection.
5. Coordinate expansion, basis/prolongation construction, syzygy discovery, solving, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`Boolean_Semaev_ideal | Pommaret_Janet_involutive_division | degree_born_syzygy_cones | reduced_Macaulay_quotient | exact_root_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `OFQ-autolab-15`; the ledger already requires a genuinely non-Gröbner relation generator to change the obstruction.
2. `inputs/ledger_inventory.json` — imported `ECFG-H465`; only a true quotient or rational identity, not backend substitution, could alter the source surface.
3. `inputs/ledger_inventory.json` — imported `ECFG-H644`; batched non-Gröbner decomposition remains a hypothesis rather than a demonstrated source operation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1420-ZERO-PRODUCT-NO-PROMOTION`; exact polynomial zero tests retained the full outer-pair surface.
5. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a source-resolving circuit remains the missing complete-path object.

## Closest primary literature

- Gerdt and Blinkov, [Involutive Bases of Polynomial Ideals](https://doi.org/10.1016/S0378-4754(97)00127-4), defines involutive divisions and bases for supplied polynomial ideals.
- Gerdt, [Involutive Algorithms for Computing Gröbner Bases](https://arxiv.org/abs/math/9912027), presents involutive methods as Gröbner-basis algorithms rather than new quotient semantics.
- Gerdt and Zinin, [Involutive Bases of Polynomial Ideals over Boolean Rings](https://doi.org/10.1134/S0361768810020106), specializes the machinery to Boolean polynomial systems.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the underlying relation equations but no subgate involutive quotient theorem.

No checked source proves the required Semaev source-dimension collapse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, Boolean encoding, variable order, involutive division, target specialization, masks, and verifier.
2. Construct the target-independent involutive basis and syzygy/cone certificate without materializing source-sized Macaulay rows.
3. On known-log targets, specialize, solve the exact reduced quotient, recover one tuple, and replay it by direct group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply identical specialization and solve rules to fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge coordinate expansion, basis construction, prolongations, syzygies, matrices, solve, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

An involutive basis is a structured, often redundant Gröbner basis. Syzygies eliminate equations and prolongations but do not by themselves reduce the quotient dimension or create a source section. Computing the basis can reproduce the same degree-of-regularity and fill-in costs it is meant to avoid. Without a new mathematical quotient identity this is a solver substitution merging with IDEAs 013, 056, 065, 098, and 152.

## Proof track

Prove a target-uniform involutive Hilbert/cone theorem that strictly lowers the Semaev quotient dimension, preserves all roots, and gives complete construction and solve exponents at most `0.45`.

## Disproof track

Show that involutive pruning changes only row redundancy while leading monomials, quotient dimension, regularity, or source output retain rho-level cost on an infinite family.

## Positive and negative controls

- Positive: supplied Boolean ideals with known Pommaret/Janet bases and intentionally redundant prolongations.
- Negative: ideals with identical quotient dimension after heavy syzygy pruning, variable-order perturbations, repeated/singular source strata, and blind targets.
- Baselines: IDEAs 013/056/065/098/152, direct Macaulay and Gröbner solvers, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved quotient-dimension reduction, root-preserving source recovery, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify when only rows are pruned, basis construction reaches the original regularity/fill, a stratum is lost, source output is hidden, or either exponent is at least `0.50`.
- A smaller toy Macaulay matrix or correct involutive basis is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-372/involutive_quotient_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-372/hilbert_cone_cases.json`
- `ideas/artifacts/ECDLP-IDEA-372/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-372/cost_analysis.md`

## Interpretation boundary

This rejects the screened backend substitution, not involutive bases. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Correct syzygies are not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-372/involutive_quotient_obligations.md` and prove whether involutive cones reduce quotient dimension rather than only Macaulay row count.
