# ECDLP-IDEA-030 — Marked-connection p-curvature coordinate

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` symbolic derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a connection or p-curvature invariant is not a discrete-log solution.

## Falsifiable hypothesis

A canonically normalized global logarithmic rank-two connection obtained by elementary
modification at `R in E(F_p)` has p-curvature invariants `I(R)` with an explicit
low-degree multiplication law `I([n]P)=F_n(I(P))`, nonconstant on the prime-to-`p`
subgroup. Constructing `I(P),I(Q)`, solving the frozen law for `x`, and verifying it has
complete time and memory exponent below `1/2`.

## Mechanism-new operation

Apply a **global marked elementary modification and read its p-curvature conjugacy
invariant**. This is not the local deformation jet of `004` or unipotent path of `021`:
the source is a global connection and the new required operation is a proved monoidal
composition law for modifications under elliptic addition. It is not a solver, factor
base, isogeny, or post-hoc invariant selector.

## Assumptions

1. The derivation gate freezes `V=O_E^2`, a public pole divisor `D=O+T`, residue conjugacy classes, normalization, and basis independently of `Q`.
2. Elementary modification at `R` is explicit from the point encoding alone.
3. The scalar composition law is proved and tested on held-out multipliers.
4. p-curvature is nonconstant on the prime-to-`p` subgroup and is not a local jet in disguise.
5. Gauge normalization, root branches, coefficient height, and bit memory are charged.
6. Every claim remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`global_logarithmic_connection | point_marked_elementary_modification | p_curvature_conjugacy_invariant | scalar_composition_polynomial`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — distinguishes a global connection from coordinate models.
2. `ledger/EV-REP-002.yaml` — requires gauge, sign, and branch accounting.
3. `ledger/FINDING-PF-IC-001.md` — motivates a direct nonlinear coordinate.
4. `ledger/H-ISO-001.yaml` — excludes same-field isogeny variants.
5. `ledger/SYNTHESIS-20260716.md` — supplies end-to-end and complete-cost boundaries.

## Closest primary literature

- Katz, [Nilpotent connections and the monodromy theorem](https://www.numdam.org/item/PMIHES_1970__39__175_0/), supplies the connection/monodromy boundary.
- Ogus and Vologodsky, [Nonabelian Hodge theory in characteristic p](https://arxiv.org/abs/math/0507476), supplies the characteristic-`p` Higgs/connection boundary.
- Katz, [Algebraic solutions of differential equations (p-curvature and the Hodge filtration)](https://doi.org/10.1007/BF01389714), supplies the p-curvature boundary.

None supplies the stated point-additive scalar-separating invariant. Novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the single invariant `I(P)` and the public law family `F_n`.

1. Freeze the global connection template, modification, gauge normalization, and invariant tuple.
2. Construct and independently verify the marked connections for `P,Q`.
3. Compute exact p-curvature invariants with all gauge and root branches retained.
4. Solve `F_X(I(P))=I(Q)` for every scalar candidate without target-trained laws.
5. Return only candidates satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Let connection construction be `N^c`, module rank `N^rho`, coefficient height/precision
`N^h`, the characteristic size be `p=N^(pi_p+o(1))`, any extra p-curvature algorithm
cost be `N^e`, composition-law degree `N^delta`, equation solve
`N^q`, gauge/root ambiguity `N^u`, verification `N^v`, and bit-memory `N^s`. Rho costs
`N^1/2` time; BSGS costs `N^1/2` time/memory. The candidate has time exponent
`lambda=max(c,omega*rho,h,pi_p+e,delta,q,u+v)` and memory exponent
`mu=max(s,2*rho,h,u)`. Standard p-curvature iteration has `pi_p≈1`; only a proved
sublinear symbolic operation can change that term. A law or root list of degree
`N^(1/2)` kills promotion.

## Likely fatal obstruction

Elementary modification is not monoidal under elliptic addition. p-curvature may see only
characteristic-`p` deformation data and remain constant or vanish on prime-to-`p` torsion.
A scalar-separating normalization can itself encode the DLP or require order-`N` degree.

## Proof track

Construct a canonical global connection, prove its addition-compatible invariant law and
nonvanishing, and bound rank, degree, solving, ambiguity, and memory below `1/2`.

## Disproof track

Show p-curvature is constant/blind on the subgroup, modification lacks an addition law,
gauge normalization depends on the scalar, or separating law degree reaches square root.

## Positive and negative controls

- Positive control: synthetic connections with a planted additive residue coordinate.
- Positive instrumentation control: exact gauge-conjugate connections.
- Negative control: random marked points and unmodified global connections.
- Torsion control: anomalous and ordinary prime-to-`p` subgroups reported separately.
- Leakage control: freeze invariant and laws before revealing held-out multipliers.

## Quantitative promotion and falsification gates

Use exhaustive 7–16-bit curves, ranks `2–4`, at least 100 instances per size, and held-out
scalar triples. Promotion only to scaling requires a proved canonical modified connection,
an explicit symbolic representation of `F_n`, exact gauge invariance and composition
on 10,000 held-out cases, nonconstant signal on at least 90% of ordinary instances, zero
wrong scalars, and upper 95% `rho<=0.15`, `delta<=0.25`, `pi_p+e<=0.40`,
`lambda<=0.45`, and `mu<=0.45`. Falsify if no canonical modified connection exists,
invariants are constant, a held-out law fails, gauge choices alter labels, or the lower
95% degree/ambiguity exponent reaches `0.50`.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-030/p_curvature_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-030/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-030/runs/<run_id>/invariants.jsonl`
- `ideas/artifacts/ECDLP-IDEA-030/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-030/analysis.md`

## Interpretation boundary

All evidence is toy, heuristic, model-bound, and novelty-unverified. Symbolic p-curvature
correctness or a nonconstant toy invariant is not a breakthrough without complete verified
scalar recovery below rho/BSGS.

## Exactly one next executable action

1. Derive or disprove existence and uniqueness of the frozen logarithmic connection on `V=O_E^2` after one elementary modification, including its symbolic p-curvature and addition law, before implementing a scaling experiment.
