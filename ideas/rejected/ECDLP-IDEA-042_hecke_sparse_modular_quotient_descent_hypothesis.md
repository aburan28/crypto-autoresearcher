# ECDLP-IDEA-042 — Hecke-sparse modular quotient descent

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a modular quotient or valid pushforward relation is not a break.

## Falsifiable hypothesis

For a non-negligible family of ordinary prime-field elliptic curves, an explicitly
computable Hecke-stable quotient `pi:J_1(M)_{F_p}->E` admits a sparse inverse on rational
points: given `R in E(F_p)`, it returns a short modular-divisor/Manin-symbol chain over a
frozen atom base whose pushforward is `R`. Known-scalar relation collection, atom-log
linear algebra, and a separate target lift then recover the ECDLP in total time and bit
memory below exponent `1/2`. Claims are toy, heuristic, model-bound, and novelty-unverified.

## Mechanism-new operation

The proposed new operation is a **sparse, witness-producing inverse to a modular
Jacobian quotient**. The returned chain is an explicit divisor equality, not a modular
symbol value or abstract Hecke eigenpacket. This differs from split-Jacobian projected
smoothness (`002`), a characteristic-zero height lift (`005`), CM ray orientation (`018`),
and same-field isogeny walking. If quotient inversion becomes generic divisor smoothness,
requires target-selected preimages, or merely moves the DLP to a Hecke eigenspace, it
merges with `002/005` and fails the novelty gate.

## Assumptions

- `E(F_p)` contains a public prime subgroup `<P>` of order `N=p^(1+o(1))`.
- The level, modular curve, Hecke quotient, reduction map, and atom base are constructed
  from `(E,P,N)` without `Q` or hidden scalar labels.
- Every chain includes enough divisor and quotient data for independent pushforward verification.
- Rejected levels, quotient construction, genus, coefficient fields, fiber ambiguity,
  and modular-symbol arithmetic are charged.
- Atom images need not have known logs; their logs are solved only from known-scalar relations.
- Toy scaling is heuristic and model-bound.

## Semantic fingerprint

`finite_field_modular_Jacobian | explicit_Hecke_elliptic_quotient | sparse_Manin_divisor_inverse | verified_pushforward_atoms | separate_masked_target_lift`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — supplies the generic prime-field cost obstruction.
2. `ledger/H-ISO-001.yaml` — distinguishes this modular-Jacobian inverse from an E-to-E isogeny neighbor.
3. `ledger/EV-ISO-001.yaml` — supplies matched coefficient-variance and same-order controls.
4. `ledger/H-FB-001.yaml` — prevents a modularly named atom set from counting without a new inverse.
5. `ledger/SYNTHESIS-20260716.md` — requires construction, applicability, target descent, and rho accounting.

## Closest primary literature

- Manin, [Parabolic points and zeta functions of modular curves](https://doi.org/10.1070/IM1972v006n01ABEH001867), introduces the modular-symbol relations underlying the proposed chains.
- Edixhoven, Couveignes, de Jong, Merkl, and Bosman, [Computational aspects of modular forms and Galois representations](https://arxiv.org/abs/math/0605244), gives nearby effective modular and Galois-representation machinery.
- Gaudry, [Index calculus for abelian varieties](https://doi.org/10.1016/j.jsc.2008.08.005), is the generic Jacobian relation baseline.

These works do not give a sub-rho sparse inverse to an elliptic modular quotient; novelty
therefore remains unverified.

## Complete factor-base-to-target-descent path

- Enumerate preregistered levels and construct a certified quotient `pi` when applicable.
- Freeze modular-divisor atoms `D_i` and compute their images `F_i=pi(D_i)` on `E`.
- For independent known scalars `r`, compute `R=[r]P` and invoke the sparse inverse.
- Verify the returned chain in the modular Jacobian and verify its pushforward relation on `E`.
- Collect enough independent rows to solve `log_P(F_i)`; charge zero images and dependencies.
- Apply the unchanged inverse to `Q+[t]P`, substitute solved atom logs, remove `t`, and
  independently verify `[x]P=Q`.

## Full rho/BSGS cost model

Let atom-base size be `B=N^beta`; quotient/level construction per attempt `N^c`;
reciprocal applicable-level density `N^zeta`; sparse inverse attempt `N^u`; reciprocal
known-target and masked-target success `N^delta` and `N^delta_t`; target inverse exponent
`u_t`; coefficient-field/genus/height arithmetic `N^h`; and stored quotient, symbols,
divisors, and coefficients `N^s` bits.

- Pollard rho: `N^(1/2+o(1))` time and constant-state exponent.
- BSGS: `N^(1/2+o(1))` time and memory.
- Applicable quotient construction: `N^(c+zeta+o(1))`.
- Relation collection: `N^(beta+u+delta+o(1))`.
- Sparse linear algebra: `N^(2*beta+o(1))` time, or `N^(3*beta)` if measured rows are dense.
- Target lift and descent: `N^(u_t+delta_t+o(1))`.
- All modular coefficient arithmetic contributes the independent exponent `h`.

The optimistic sparse time exponent is
`lambda=max(c+zeta,h,beta+u+delta,2*beta,u_t+delta_t)` and bit-memory exponent is
`mu=max(s,beta,h)`. A supplied favorable curve may omit `zeta` only if the claim is
explicitly restricted to that input family.

## Likely fatal obstruction

The least useful modular level may have genus, coefficient field, or construction cost
`N^(1/2-o(1))`. More fundamentally, inverting the quotient at a marked point may be a
full Jacobian smoothness problem or an ECDLP in the quotient eigenspace; short Manin
relations among cusps may push only to torsion irrelevant to the prime subgroup.

## Proof track

Prove an applicable family of explicit quotients, a target-independent atom base, and a
sparse inverse with complete divisor witnesses and bounded ambiguity. Then prove full
relation rank and masked target descent with `lambda,mu<1/2`.

## Disproof track

Show quotient degree/genus/field size reaches `N^(1/2-o(1))`, sparse inversion is generic
Jacobian decomposition, atom images do not span the prime subgroup, or all complete-cost
parameters have lower confidence bound at least `1/2`.

## Positive and negative controls

- Positive control: a planted small modular quotient with preconstructed short divisor chains.
- Negative control: a matched random Jacobian quotient of equal dimension and atom count.
- Isogeny control: same-order small-isogeny neighbors from the ledger.
- Leakage control: blind target scalars and reject target-selected levels, atoms, or fibers.
- Witness control: modular-symbol values without explicit divisors cannot enter promotion metrics.

## Quantitative promotion and falsification gates

Use `p<=211`, levels `M<=101`, every certified applicable quotient, and exhaustive fibers.
Promotion requires zero invalid divisor or pushforward witnesses, atom images spanning at
least `0.95B`, upper 95% bounds `c+zeta<=0.40`, `h<=0.40`, `u+delta<=0.20`,
`u_t+delta_t<=0.45`, and complete `lambda,mu<=0.45`. Falsify the scoped claim if no
noncuspidal spanning atom set exists, inversion matches random-Jacobian cost within 10%,
or every full-cost fit has lower 95% `lambda>=0.50`.

## Artifact plan

- Specification: `ideas/artifacts/ECDLP-IDEA-042/preflight_spec.yaml`
- Quotient catalog: `ideas/artifacts/ECDLP-IDEA-042/quotients.jsonl`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-042/hecke_sparse_inverse.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-042/runs/<run-id>/`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-042/analysis.md`

## Interpretation boundary

This is a toy, heuristic, model-bound, novelty-unverified representation hypothesis.
A modular quotient, Hecke eigenpacket, valid chain, or toy scalar is not a breakthrough.
Only complete target recovery below rho/BSGS with level search and memory charged matters.

## Exactly one next executable action

1. For every `p<=211` and level `M<=101`, enumerate certified elliptic Hecke quotients, exhaust their rational fibers, and measure minimum explicit Manin-chain length, ambiguity, atom span, and blinded target-lift cost.
