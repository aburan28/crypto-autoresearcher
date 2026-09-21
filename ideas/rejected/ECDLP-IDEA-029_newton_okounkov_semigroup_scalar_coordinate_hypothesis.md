# ECDLP-IDEA-029 — Newton–Okounkov semigroup scalar coordinate

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valuation body or semigroup computation is not a scalar coordinate.

## Falsifiable hypothesis

For `L=O_E(dO)` and each `R in <P>`, the Picard-twisted section module
`M_R=direct_sum_m H^0(E,L^m tensor O(R-O))` admits a fixed-flag initial-semigroup
normal form `sigma_d(R)` that is additive modulo an explicit lattice, injective on the
order-`N` subgroup, and computable with `d=N^(alpha+o(1))` such that complete time and
memory exponents are below `1/2`. Smith normal form then recovers `x` from
`sigma_d(Q)=x sigma_d(P)` and verifies it on `E`.

## Mechanism-new operation

Apply **valuation-semigroup normalization to a Picard-twisted section module**. This is
not the supported-divisor search of `007/012`, Fourier–Mukai factorization, a curve model,
or a solver substitution. The claimed new operation would retain torsion-sensitive fine
semigroup data even though the ordinary Newton–Okounkov body is numerical and constant
under `Pic^0` twists.

## Assumptions

1. The line bundle, flag, term order, lattice, and normal form are target-independent.
2. Fine semigroup data, not only the numerical body, is computed exactly.
3. Additivity and injectivity on `<P>` are proved or exhaustively tested before scalar labels.
4. Section dimensions, initial-module linear algebra, coefficient bits, and lattice reduction are charged.
5. A divisor-support oracle or scalar-indexed semigroup table invalidates the arm.
6. Evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`Pic0_twisted_section_module | fixed_flag_valuation_semigroup | additive_lattice_normal_form | Smith_scalar_coordinate`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — distinguishes the fine valuation semigroup from a coordinate model.
2. `ledger/EV-REP-001.yaml` — supplies matched representation controls.
3. `ledger/H-FB-001.yaml` — this does not reshape a point factor base.
4. `ledger/FINDING-PF-IC-001.md` — motivates a direct scalar coordinate rather than PDP relations.
5. `ledger/SYNTHESIS-20260716.md` — supplies complete-cost and end-to-end verification gates.

## Closest primary literature

- Lazarsfeld and Mustaţă, [Convex bodies associated to linear series](https://doi.org/10.24033/asens.2102), develops Newton–Okounkov bodies for linear series.
- Kaveh and Khovanskii, [Newton–Okounkov bodies, semigroups of integral points, graded algebras and intersection theory](https://doi.org/10.4007/annals.2012.176.2.5), develops the semigroup boundary.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), controls generic encodings.

The literature establishes the numerical/semigroup machinery, not a torsion-sensitive
additive public normal form. Novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the single semigroup vector `sigma_d(P)`.

1. Freeze `d`, `L`, the flag, valuation, term order, lattice, and exceptional-module policy.
2. Construct `M_P,M_Q` and their exact initial semigroups without scalar labels.
3. Reduce them to public normal forms `sigma_d(P),sigma_d(Q)` and certify additivity.
4. Solve `sigma_d(Q)=x sigma_d(P)` in the explicit lattice quotient by Smith normal form.
5. Enumerate every lattice ambiguity and return only `[x]P=Q`.

## Full rho/BSGS cost model

Let `d=N^alpha`, section/initial-module dimension `N^rho`, construction `N^c`, linear
algebra `N^(omega*rho)`, coefficient-height arithmetic `N^h`, lattice setup `N^ell`,
ambiguity `N^u`, verification `N^v`, and bit-memory `N^s`. Rho costs `N^1/2` time;
BSGS costs `N^1/2` time/memory. The proposal has time exponent
`lambda=max(alpha,c,omega*rho,h,ell,u+v)` and memory exponent `mu=max(s,2*rho,h,u)`. A degree,
semigroup, or table of size `N^(1/2)` fails promotion.

## Likely fatal obstruction

Newton–Okounkov bodies depend only on numerical equivalence, so every `Pic^0` twist has
the same body. Fine semigroup data capable of distinguishing `N` torsion points may first
appear at degree `Omega(N)`. Exact additivity into a torsion-free lattice can also kill
the subgroup entirely.

## Proof track

Prove a torsion-sensitive additive semigroup quotient, injectivity on `<P>`, and
sub-square-root bounds for degree, module rank, lattice arithmetic, ambiguity, and memory.

## Disproof track

Show the normal form is constant on `Pic^0`, additivity kills `N`-torsion, or any
separating fine semigroup requires degree/rank at least `N^(1/2-o(1))`.

## Positive and negative controls

- Positive control: `O,P,2P` exact additivity in a synthetic graded module.
- Positive instrumentation control: known distinct line bundles on a small curve.
- Negative control: numerical Newton–Okounkov bodies of random `Pic^0` twists.
- Representation control: multiple flags and coordinate changes frozen before labels.
- Leakage control: no scalar-indexed section or semigroup table.

## Quantitative promotion and falsification gates

Use exhaustive prime-order curves through 18 bits, degrees through 12 initially, and at
least 100 instances per size. Promotion only to scaling requires exact additivity on
10,000 triples, at least 99% injectivity before collision correction, zero wrong scalars,
and upper 95% `alpha<=0.15`, `omega*rho<=0.40`, `lambda<=0.45`, and `mu<=0.45`.
Falsify if any certified additivity law kills torsion, collisions persist on all flags, or
separating degree/rank has lower 95% exponent at least `0.50`.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-029/okounkov_semigroup_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-029/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-029/runs/<run_id>/semigroups.jsonl`
- `ideas/artifacts/ECDLP-IDEA-029/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-029/analysis.md`

## Interpretation boundary

All results remain toy, heuristic, model-bound, and novelty-unverified. A computed body,
semigroup, or exact additivity identity is not a breakthrough without sub-rho/BSGS
end-to-end scalar recovery.

## Exactly one next executable action

1. Compute fixed-flag initial semigroups of `M_R` through degree 12 on prime-order curves with `p<=257` and exhaustively measure additivity, collisions, rank, height, and blinded scalar recovery.
