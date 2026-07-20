# ECDLP-IDEA-016 — Semistable toric transport

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Revision: independent red-team citation, applicability, extension-degree, and marked-section findings incorporated
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a degeneration or solving a positive-control torus DLP is not an ECDLP break.

## Falsifiable hypothesis

An input in a declared ordinary family `E/F_p` with prime subgroup `<P>` of order `N≈p`
and `Q=[x]P` admits
an explicit one-parameter semistable deformation with certified marked sections extending
`P,Q`, such that specialization to a split multiplicative fiber is injective on `<P>` and
produces `g,h=g^x` in a constructible finite-field torus. Transport plus a complete
finite-field factor-base relation and individual descent has time and memory exponent
below `1/2` in `N`.

## Mechanism-new operation

Transport marked prime-to-characteristic torsion through a semistable family and
**specialize it into the Tate torus with its scalar relation intact**. The target DLP then
uses finite-field index calculus. This is neither a same-field elliptic isogeny, a global
height relation (`ECDLP-IDEA-005`), nor a trace-zero transfer (`009`); the claimed new
operation is injective marked-section transport across a change of reduction type.

## Assumptions

1. The family, base change, marked sections, and specialization maps are constructed without `x`.
2. The target subgroup remains injective and its order is known in the toric fiber.
3. The torus is represented over a field whose degree, discriminant, and arithmetic are fully charged.
4. The multiplicative factor base, relation collection, linear algebra, and target descent are independently verifiable.
5. Failed deformations, monodromy branches, and section ambiguities enter the cost.
6. Any extrapolation is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`one_parameter_semistable_deformation | marked_prime_to_p_torsion_transport | split_Tate_torus_specialization | finite_field_factor_base_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field elliptic PDP obstruction avoided by changing group type.
2. `ledger/H-ISO-001.yaml` — distinguishes degeneration from an E-to-E isogeny neighbor.
3. `ledger/EV-ISO-001.yaml` — supplies the same-field negative control.
4. `ledger/H-REP-001.yaml` — prevents a mere curve-equation degeneration from counting.
5. `ledger/SYNTHESIS-20260716.md` — requires complete transport and target verification.

## Closest primary literature

- Tate, [The arithmetic of elliptic curves](https://doi.org/10.1007/BF01389745), supplies the arithmetic and reduction framework underlying the Tate-curve boundary.
- Menezes, Okamoto, and Vanstone, [Reducing elliptic curve logarithms to logarithms in a finite field](https://doi.org/10.1145/103418.103434), is the established pairing-based transfer boundary, not this degeneration.
- Chiodo, [Quantitative Néron theory for torsion bundles](https://arxiv.org/abs/math/0603689), gives a nearby semistable torsion-model boundary.

No checked source supplies the stated generic marked-section transport to a cheap toric
DLP. Novelty is therefore unverified, not established.

## Complete factor-base-to-target-descent path

1. Freeze a semistable family, base changes, marked sections for `P,Q`, and a specialization certificate.
2. Prove and verify injectivity on `<P>` and identify the toric images `g,h` with `h=g^x`.
3. Construct a finite-field/torus factor base and collect target-independent multiplicative relations.
4. Solve factor-base logarithms with every extension-field and linear-algebra cost charged.
5. Perform an individual descent of `h`, reconstruct `x mod N`, and retain all branch ambiguity.
6. Verify `[x]P=Q` on the original elliptic curve.

## Full rho/BSGS cost model

Let reciprocal usable-family density be `N^zeta`, family and marked-section construction
be `N^c`, branch/monodromy search `N^b`, ramification and residue degrees contribute
`N^phi`, coefficient/discriminant height `N^h`, and torus dimension `N^j`. Freeze the
combined residue/torus splitting degree `k`, including the geometric base change, with
`k=N^(eta+o(1))` and `ord_N(p^k)=1`; charge field input length `k log p` and require
`eta>=phi` whenever the same extension realizes both costs. With factor-base size `N^beta`,
reciprocal relation density `N^delta`, per-attempt field arithmetic `N^q`, sparse-LA
exponent `omega_s*beta`, individual descent `N^tau`, and bit-memory `N^s`, rho costs
`N^(1/2+o(1))` time and BSGS costs `N^(1/2+o(1))` time/memory. The proposal has
time exponent `lambda=max(zeta+c,b,phi,h,j,eta,beta+delta+q,omega_s*beta,tau)` and
memory exponent `mu=max(s,beta+eta,phi+h)`, with all
field elements charged at `k log p` bits. A formal finite-field `L[1/3]` term is exponent
zero only if every degree and input-size term is `N^o(1)`.

## Likely fatal obstruction

Good-reduction prime-to-`p` torsion does not freely move into a toric component. An
injective order-`N` specialization requires a torus whose residue/extension field contains
order `N`, and its degree or monodromy may be `N^(1-o(1))`. Constructing sections that
preserve both public points can itself encode the DLP. A nodal equation alone loses the
subgroup and is only a positive control.

## Proof track

Give an explicit family and section-transport theorem, prove injectivity and sub-square-root
field/monodromy degree, and combine the finite-field relation/descent bounds into
`lambda,mu<1/2`.

## Disproof track

Show every admissible specialization is trivial/noninjective on `<P>`, forces extension or
component degree `N^(1/2-o(1))`, depends on `x`, or makes the complete torus attack no
cheaper than rho.

## Positive and negative controls

- Positive control: a Tate curve already having split multiplicative reduction and known uniformization.
- Positive instrumentation control: transported small torsion with exhaustive specialization checks.
- Negative control: good-reduction families whose special fiber stays elliptic.
- Mechanism control: MOV-compatible curves, with embedding-degree cost charged separately.
- Leakage control: blind `Q` and audit every section-construction dependency.

## Quantitative promotion and falsification gates

The first gate uses toy `(p,N)` pairs through 18 bits, computes exact `k=ord_N(p)` and
the Tate-curve `N`-torsion sequence, and separately certifies one public section in one
explicit nodal family. Promotion only to a scaling contract requires a written family
equation, base scheme, section equations, specialization map, zero transport failures,
and upper 95% `zeta+c<=0.30`, `phi<=0.30`, `h<=0.30`, `lambda<=0.45`, and
`mu<=0.45`. Falsify if order-`N` toric image always needs lower 95% field/base-change
exponent at least `0.50`, the section depends on `x`, or specialization is noninjective.
Construction crashes are infrastructure evidence, not mathematical negatives.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-016/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-016/semistable_transport.sage`
- `ideas/artifacts/ECDLP-IDEA-016/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-016/runs/<run_id>/specializations.jsonl`
- `ideas/artifacts/ECDLP-IDEA-016/runs/<run_id>/torus_descent.jsonl`
- `ideas/artifacts/ECDLP-IDEA-016/analysis.md`

## Interpretation boundary

All claims remain toy, heuristic, model-bound, and novelty-unverified. A valid family,
section, or torus DLP is not a breakthrough unless the original target is transported and
recovered below rho/BSGS with every field-size term charged.

## Exactly one next executable action

1. For the Legendre family `y^2=x(x-1)(x-t)` over `F_11(t)`, adjoin one root of the 5-division polynomial and the minimal residue extension that splits the two tangent directions of the nodal fiber at `t=0`, compute and charge the combined normalized base change, and certify or disprove specialization of that public 5-torsion section into the split torus.
