# ECDLP-IDEA-015 — Compressed theta-group translation logarithm

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Revision: independent red-team citation, dimension, availability, and labeling-cost findings incorporated
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a theta representation or verifying a projective translation is not a discrete-log break.

## Falsifiable hypothesis

For `Q=[x]P` in a prime-order subgroup of size `N≈p`, translations by `P` and `Q` in a
level structure admit a target-independent compressed stable subquotient of dimension
`N^(rho+o(1))`, `rho<1/2`, on which their projective operators satisfy `T_Q=T_P^x` and
the exponent can be labeled without another order-`N` DLP. Construction, cocycle removal,
matrix logarithm, ambiguity, and memory together have exponent below `1/2`.

## Mechanism-new operation

Use the theta/Heisenberg representation of torsion translations, then construct a
**compressed translation-stable subquotient with exponent labeling**. This changes the
group element into a projective linear operator; it is not an elliptic-net recurrence,
scalar-orbit period, pairing return, or coordinate-model swap. A full `N`-dimensional
regular/theta representation is only the negative control.

## Assumptions

1. `<P>` has known prime order `N`; structure availability, full theta dimension, and the charged splitting field are measured rather than assumed.
2. Projective cocycles and roots of unity are normalized without knowing `x`.
3. The compressed subquotient is stable for both operators and preserves enough information to distinguish all candidate exponents.
4. Eigenvalue or matrix labeling does not invoke a DLP in an order-`N` field subgroup.
5. Extension degree, basis conversion, matrices, and ambiguity search are charged.
6. Extrapolation is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`theta_Heisenberg_group | N_torsion_translation_operator | compressed_stable_subquotient | projective_matrix_power_logarithm`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct non-PDP representation.
2. `ledger/H-REP-001.yaml` — distinguishes a new operator algebra from a curve-model rewrite.
3. `ledger/EV-REP-001.yaml` — warns that projective/sign branches must be charged.
4. `ledger/H-ISO-001.yaml` — distinguishes translation representation from an isogeny neighbor.
5. `ledger/SYNTHESIS-20260716.md` — supplies the rho/BSGS and independent-review boundary.

## Closest primary literature

- Mumford, [On the equations defining abelian varieties I](https://eudml.org/doc/141838), establishes theta-group translation representations.
- Kaneko and Kuwata, [Elliptic normal curves of even degree and theta functions](https://arxiv.org/abs/2005.12449), gives nearby explicit level and theta-function models.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic boundary if compression is simulable by group operations.

The checked sources do not construct the proposed separating sub-square-root subquotient.
This is not a novelty proof; novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is a certified basis of the compressed operator module.

1. Build and verify the theta structure, cocycle, and translations for `P` and public `Q`.
2. Construct the target-independent compressed stable subquotient and its explicit basis.
3. Express `T_P` and `T_Q` in that basis and verify projective consistency on held-out sections.
4. Solve the matrix-power labeling problem `T_Q=T_P^x`, retaining every projective/eigenvalue ambiguity.
5. Map each candidate scalar back to `E` and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let the full theta dimension be `N^kappa` and treat its materialization as a separately
reported no-go control. For the proposed implicit route, let splitting-field degree be
`N^phi`, reciprocal structure-availability exponent `zeta`, direct quotient construction
cost `N^c`, quotient search
`N^q`, compressed dimension `N^rho`, matrix/readout costs `N^(omega*rho+phi)` and
`N^tau`, reciprocal usable-target density `N^delta`, residual label list `N^u`,
verification `N^v`, and other storage `N^s`. Pollard rho is `N^(1/2+o(1))` time with
negligible memory; BSGS is `N^(1/2+o(1))` time/memory. The proposal has time exponent
`lambda=max(zeta+c,q,omega*rho+phi,tau+delta,u+v)` and bit-memory exponent
`mu=max(s,2*rho+phi,u)`. If construction materializes the full representation, add
`2*kappa+phi` to memory and `kappa` to time; for `kappa=1` this is an immediate no-go.
Any order-`N` eigenvalue/root-of-unity DLP contributes exponent `1/2` and kills promotion.

## Likely fatal obstruction

On an elliptic curve, a line bundle whose theta kernel contains `E[N]` has degree and an
irreducible Heisenberg representation dimension on the order of `N`. Any separating
subquotient may inherit that lower bound, while diagonalizing the translation can merely
move the original DLP to roots of unity.

## Proof track

Exhibit the stable subquotient, prove separation of all powers, give a public cocycle
normalization and exponent-labeling algorithm, and bound `lambda,mu<1/2`.

## Disproof track

Prove a representation-dimension/separation lower bound, show every compression collides
on `N^(1/2)` or more powers, or reduce exponent labeling to an order-`N` field DLP.

## Positive and negative controls

- Positive control: a small Heisenberg representation with a planted low-dimensional invariant quotient.
- Positive instrumentation control: exhaustive powers of `T_P` on tiny `N`.
- Negative control: the full theta representation with all construction/memory charged.
- Generic control: random cyclic matrices with matched spectrum and dimension.
- Circularity control: reject discrete-log tables or known-`x` eigenvalue labels.

## Quantitative promotion and falsification gates

Use exact Schrödinger representations at prime levels through the largest feasible
20-bit order, at least 100 instances per supported size, and rational-canonical invariant
subquotient enumeration. Promotion requires a certified implicit construction that does
not materialize the full theta representation, zero incorrect labels, exact agreement with
exhaustive powers, a target-independent quotient retaining translation order `N`, and
upper 95% `phi<=0.20`, `rho<=0.18`, `lambda<=0.45`, and
`mu<=0.45`. Falsify if every faithful quotient has lower 95% dimension exponent at
least `0.50`, quotient discovery or labeling is an order-`N` DLP, a label is wrong, or
every complete-cost lower bound reaches `0.50`. Unsupported arithmetic is infrastructure
evidence only.

## Artifact plan

- `ideas/contracts/ECDLP-EXP-CONTRACT-015_theta_quotient_preflight.yaml`
- `ideas/artifacts/ECDLP-IDEA-015/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-015/theta_translation.sage`
- `ideas/artifacts/ECDLP-IDEA-015/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-015/runs/<run_id>/operators.jsonl`
- `ideas/artifacts/ECDLP-IDEA-015/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-015/analysis.md`

## Interpretation boundary

All observations remain toy, heuristic, model-bound, and novelty-unverified. A correct
theta action or compressed toy matrix does not establish a sub-rho ECDLP algorithm.

## Exactly one next executable action

1. Execute the exact faithful-subquotient and root-of-unity-DLP-equivalence preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-015_theta_quotient_preflight.yaml` after coordinator approval.
