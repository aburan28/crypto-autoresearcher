# ECDLP-IDEA-024 — Pontryagin-square Chow-regulator coordinate

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cycle identity, regulator value, or recovered toy square is not a break.

## Falsifiable hypothesis

For `R` in a prime-order subgroup of `E(F_p)`, the external Pontryagin square
`z_R=([R]-[O]) box-times ([R]-[O])` has an explicitly computable nonzero `N`-primary
regulator coordinate satisfying `Psi(z_[x]P)=x^2 Psi(z_P)`. Coordinate construction,
module labeling, square-root ambiguity, and verification recover `x` below exponent
`1/2` without a pairing/DLP hidden in `Psi`.

## Mechanism-new operation

Apply a **quadratic cycle functor followed by an explicit readable regulator**. The new
operation would expose `x^2` directly in a motivic/Chow graded piece. It differs from idea
008's outward pairing and return map because no target-group product is returned to `E`;
if `Psi` is a Tate/Weil pairing or field DLP in disguise, this idea is a duplicate and fails.

## Assumptions

1. Cycle products and the quotient group are explicit over `F_p` or a fully charged extension.
2. `Psi` lands in a module with a public basis and nonzero `N`-primary component.
3. The quadratic scalar law and all signs/torsion corrections are proved.
4. Module-coordinate recovery does not require an order-`N` DLP.
5. Both square roots, zero regulators, and every construction failure are retained.
6. Evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`E_times_E_zero_cycle | external_Pontryagin_square | explicit_N_primary_Chow_regulator | quadratic_hidden_scalar_coordinate`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct nonlinear coordinate.
2. `ledger/H-REP-001.yaml` — distinguishes a motivic object from curve coordinates.
3. `ledger/H-ISO-001.yaml` — this is not a same-field map to a neighbor.
4. `ledger/H-FB-001.yaml` — no factor-base reshaping is involved.
5. `ledger/SYNTHESIS-20260716.md` — supplies the no-breakthrough and full-cost boundary.

## Closest primary literature

- Mochizuki, [Motivic interpretation of Milnor K-groups attached to Jacobian varieties](https://arxiv.org/abs/math/0603241), gives the nearby Somekawa/motivic framework.
- Gazaki, [Somekawa K-groups and zero cycles on abelian varieties](https://doi.org/10.2748/tmj.20191030), develops the relevant zero-cycle filtration.
- Mukai, [Duality for abelian varieties](https://doi.org/10.1017/S002776300001922X), is a nearby Pontryagin/Fourier boundary.

None constructs the claimed nonzero readable quadratic regulator over the target finite
fields. Novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is an explicit basis of the regulator module.

1. Freeze the cycle quotient, product conventions, regulator, and module basis.
2. Construct `z_P,z_Q` and verify their cycle relations independently.
3. Evaluate `r_P=Psi(z_P)` and `r_Q=Psi(z_Q)` with all zero/branch cases recorded.
4. Solve `r_Q=y*r_P` for `y=x^2 mod N` in the explicit module without a hidden DLP.
5. Compute both square roots of `y`, test them on `E`, and return only `[x]P=Q`.

## Full rho/BSGS cost model

Let cycle/regulator construction cost `N^c`, evaluation `N^e`, reciprocal nonzero usable
density `N^delta`, module-coordinate recovery `N^u`, representation size `N^k`, ambiguity
`N^a`, and storage `N^s`. Rho is `N^1/2` time; BSGS is `N^1/2` time/memory.
The candidate costs `lambda=max(c,e+delta,u,k,a)` and `mu=s`. Any multiplicative or
module DLP of order `N` contributes exponent `1/2` and kills promotion.

## Likely fatal obstruction

Relevant Somekawa/Chow torsion or regulators can vanish over finite fields, especially on
prime-to-characteristic torsion. A nonzero regulator may reduce to a known pairing whose
coordinate is a field DLP, or require an order-`N` representation. The quadratic law alone
does not make its coefficient readable.

## Proof track

Define `Psi` constructively, prove its nonvanishing and quadratic scalar law on a declared
family, give an explicit module-coordinate algorithm, and bound `lambda,mu<1/2`.

## Disproof track

Prove the regulator vanishes on the target subgroup, identify it with a pairing/field DLP,
show representation size is square-root or larger, or find a failure of the quadratic law.

## Positive and negative controls

- Positive control: a synthetic bilinear cycle module with a planted readable square coordinate.
- Positive instrumentation control: exhaustive cycles and scalar squares on tiny groups.
- Negative control: finite-field cycles predicted to vanish by the chosen quotient.
- Pairing control: compare `Psi` with Weil/Tate pairing traces and reject equivalence.
- Circularity control: audit module coordinates and exclude known-log tables.

## Quantitative promotion and falsification gates

Use ordinary curves with 8–26-bit prime subgroups, at least 100 instances per size, and
every constructible regulator quotient. Promotion requires exact quadratic laws on 10,000
random triples, nonzero usable coordinates on at least 90% of the two largest sizes, zero
wrong scalars, 100 end-to-end recoveries, and upper 95% `c<=0.30`, `e+delta<=0.30`,
`u<=0.40`, `k<=0.30`, `lambda<=0.45`, `mu<=0.45`. Falsify if every regulator
vanishes, `Psi` is pairing/DLP-equivalent, one accepted scalar is wrong, or every
full-cost lower bound reaches `0.50`. Missing symbolic machinery is infrastructure evidence.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-024/contract.yaml`
- `ideas/artifacts/ECDLP-IDEA-024/chow_regulator_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-024/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-024/runs/<run_id>/cycles.jsonl`
- `ideas/artifacts/ECDLP-IDEA-024/runs/<run_id>/regulators.jsonl`
- `ideas/artifacts/ECDLP-IDEA-024/analysis.md`

## Interpretation boundary

This is a high-risk toy, heuristic, model-bound, novelty-unverified hypothesis. Cycle or
regulator correctness is not a breakthrough; only readable end-to-end recovery below both
generic baselines could justify escalation.

## Exactly one next executable action

1. Execute the frozen vanishing-versus-readable-regulator preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-024_chow_regulator_preflight.yaml` after coordinator approval.
