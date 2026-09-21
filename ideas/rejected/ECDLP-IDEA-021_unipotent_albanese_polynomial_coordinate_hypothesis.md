# ECDLP-IDEA-021 — Unipotent Albanese polynomial coordinate

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Revision: independent red-team canonical-lift, path, nonvanishing, and precision-cost findings incorporated
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; evaluating an iterated integral on a toy lift is not a break.

## Falsifiable hypothesis

A canonical depth-at-least-two unipotent path coordinate on a punctured elliptic curve can
be evaluated for `P` and `Q=[x]P`, is nonzero on prime-to-`p` torsion, and obeys an explicit
Baker–Campbell–Hausdorff polynomial law in `x`. Solving that polynomial, including lift,
path, precision, and ambiguity costs, recovers `x` below exponent `1/2`.

## Mechanism-new operation

Use **nonabelian iterated-path coordinates** whose multiplication law contains quadratic
or higher scalar terms. This is distinct from idea 004's finite-order additive deformation
jet: a proposal that collapses to a linear jet/cocycle is a duplicate and fails this record.
The claimed escape is depth-two-or-higher path information, not higher numeric precision.

## Assumptions

1. A canonical lift, puncture, tangential base point, and path convention are public and target-independent.
2. Iterated Coleman/de Rham coordinates are exact enough to distinguish candidates and their precision is charged.
3. The BCH scalar law is proved for the subgroup and does not use the known toy logarithm.
4. Coordinate extraction lands in an explicitly based module, not another DLP.
5. One Frobenius-invariant Coleman path convention is frozen; only its explicitly finite algebraic lift-root and normalization branches, vanishing cases, and scalar-root candidates are enumerated and retained.
6. Scaling remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`punctured_elliptic_curve | depth_two_unipotent_path_torsor | iterated_p_adic_integrals | BCH_polynomial_hidden_scalar_coordinate`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct coordinate rather than PDP relations.
2. `ledger/H-REP-001.yaml` — distinguishes a nonabelian path object from coordinates on `E`.
3. `ledger/EV-REP-001.yaml` — requires all path/sign branches to be retained.
4. `ledger/H-ISO-001.yaml` — this is not an isogeny-neighbor mechanism.
5. `ledger/SYNTHESIS-20260716.md` — supplies the full-cost boundary.

## Closest primary literature

- Kim, [The unipotent Albanese map and Selmer varieties for curves](https://arxiv.org/abs/math/0510441), establishes the nonabelian path framework.
- Beacom, [Computation of the unipotent Albanese map on elliptic and hyperelliptic curves](https://arxiv.org/abs/1711.03932), gives explicit iterated-integral algorithms.
- Bannai, Kobayashi, and Tsuji, [On the de Rham and p-adic realizations of the Elliptic Polylogarithm for CM elliptic curves](https://arxiv.org/abs/0711.1701), supplies the elliptic-polylogarithm boundary.
- Kim and Tamagawa, [The l-component of the unipotent Albanese map](https://arxiv.org/abs/math/0611384), supplies a direct finite-image obstruction boundary in its local-field setting.

These arithmetic-geometric methods do not establish a prime-field torsion DLP coordinate.
Novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is an explicit basis of the truncated unipotent coordinate algebra.

1. Freeze the lift, puncture, path convention, depth, basis, and precision schedule.
2. Evaluate and verify the full coordinate vectors `J(P)` and `J(Q)`, including every ambiguity.
3. Derive the public polynomial action `J([n]P)=F_n(J(P))` at the frozen depth.
4. Solve `F_x(J(P))=J(Q)` for every scalar candidate without using a group-DLP table.
5. Descend candidates to `E/F_p` and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let reciprocal canonical-lift availability be `N^zeta`, lift construction `N^c_lift`,
field degree `N^phi`, ramification/height `N^h`, path construction `N^c_path`, branch
count `N^b`, depth-dependent basis dimension `N^rho`, precision `N^pi`, evaluation
`N^e`, reciprocal usable-coordinate density `N^delta`, polynomial solve `N^q_solve`,
root list `N^u`, verification `N^v`, and other bit-memory `N^s`. Rho is `N^1/2` time;
BSGS is `N^1/2` time/memory. The candidate has time exponent
`lambda=max(zeta+c_lift,phi+h,c_path+b,e+delta,q_solve,u+v)` and
memory exponent `mu=max(s,2*rho+phi+pi,b,u)`. A square-root root list, branch set, or implicit module
DLP kills promotion.

## Likely fatal obstruction

Prime-to-`p` torsion can be invisible to de Rham/unipotent logarithms, and polylogarithmic
coordinates may vanish or depend on a noncanonical path. Choosing a path from `P` to `Q`
can encode `x`, while required precision or coefficient height may reach square-root scale.

## Proof track

Construct a canonical nonabelian coordinate, prove its torsion nonvanishing and polynomial
scalar law, and bound evaluation/root recovery so `lambda,mu<1/2`.

## Disproof track

Show the depth-two coordinates vanish or reduce to the occupied additive jet, vary under
the frozen convention's finite lift-root branches, or leave `N^(1/2)` roots/precision cost.

## Positive and negative controls

- Positive control: a unipotent nilpotent group with a known quadratic BCH coordinate.
- Positive instrumentation control: known rational points on small lifted elliptic curves.
- Negative control: prime-to-`p` torsion under all allowed paths.
- Duplicate control: project onto depth one; any surviving claim there belongs to idea 004.
- Circularity control: audit all path construction and known-log access.

## Quantitative promotion and falsification gates

The first gate freezes one Serre–Tate lift rule, puncture, tangential base point, and
Frobenius-invariant Coleman path convention with zero constant term on 10–18-bit ordinary
curves, enumerates only the convention's finite algebraic lift-root and normalization
branches, and holds out BCH tests. Promotion only to scaling requires exact held-out identities, nonzero branch-independent depth-two signal on at least 90% of ordinary instances, zero wrong
labels, and upper 95% `zeta+c_lift<=0.30`, `phi+h<=0.30`, `e+delta<=0.30`,
`q_solve<=0.40`, `lambda<=0.45`, and `mu<=0.45`. Falsify if depth-two data always
vanishes/reduces to depth one, varies by branch, or an accepted scalar is wrong.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-021/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-021/unipotent_coordinate.sage`
- `ideas/artifacts/ECDLP-IDEA-021/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-021/runs/<run_id>/paths.jsonl`
- `ideas/artifacts/ECDLP-IDEA-021/runs/<run_id>/coordinates.jsonl`
- `ideas/artifacts/ECDLP-IDEA-021/analysis.md`

## Interpretation boundary

Every claim is toy, heuristic, model-bound, and novelty-unverified. A computed iterated
integral or polynomial identity does not imply a sub-rho ECDLP algorithm.

## Exactly one next executable action

1. On the lexicographically first ordinary prime-order curve over `F_101`, freeze its canonical Serre–Tate lift, puncture at `O`, tangent `dx/y`, and the Frobenius-invariant Coleman path normalized to zero constant term; enumerate the resulting finite algebraic lift-root branches for `O,P,2P` and test depth-one/depth-two branch invariance and the held-out BCH law.
