# ECDLP-IDEA-028 — Sklyanin central-character descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a Sklyanin algebra or its center is not scalar recovery.

## Falsifiable hypothesis

For translation `tau_P` of prime order `N`, a three-dimensional Sklyanin/twisted
homogeneous coordinate algebra associated with `(E,tau_P)` has an explicitly computable
central or Azumaya character of size below `N^1/2` that separates the point modules for
`O` and `Q=[x]P`. Reading that character recovers `x` below rho/BSGS after center,
PI-degree, module, fiber, labeling, and bit-memory costs are included.

## Mechanism-new operation

Encode scalar translation as a **noncommutative point-module shift and read a center-fiber
character**. This differs from theta-matrix compression (`015`): its source is a
noncommutative graded coordinate algebra, its target is an Azumaya-center fiber, and its
claimed new operation is central-character descent rather than operator diagonalization.
It is not a factor-base oracle, solver substitution, orbit table, or same-field isogeny.

## Assumptions

1. The algebra, center, modules, and public center basis are constructed without `x`.
2. The point module for `Q` is produced directly from `Q`, not from its orbit index.
3. PI degree, center-generator degree/height, splitting fields, and fiber multiplicity are charged.
4. Central-character labeling does not invoke an order-`N` DLP or scalar table.
5. Every isomorphism and Azumaya-exception branch is retained.
6. All claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_Sklyanin_algebra | translation_point_module_shift | Azumaya_center_fiber | scalar_separating_central_character`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct noncommutative coordinate.
2. `ledger/H-REP-001.yaml` — distinguishes the algebra from a curve-coordinate model.
3. `ledger/H-ISO-001.yaml` — excludes same-field isogeny reinterpretation.
4. `ledger/EV-REP-002.yaml` — requires all module/fiber branches to be retained.
5. `ledger/SYNTHESIS-20260716.md` — supplies complete-cost and verification requirements.

## Closest primary literature

- Artin, Tate, and Van den Bergh, [Some Algebras Associated to Automorphisms of Elliptic Curves](https://doi.org/10.1007/978-0-8176-4574-8_3), supplies the elliptic automorphism/algebra construction.
- De Laet, [On the center of 3-dimensional and 4-dimensional Sklyanin algebras](https://arxiv.org/abs/1612.06158), supplies explicit center structure.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic simulation boundary.

No checked source supplies a sub-square-root scalar-separating central character. Novelty
is unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the anchor point module with a public center basis.

1. Freeze the Sklyanin presentation, translation convention, center algorithm, and module normalization.
2. Construct the anchor and target point modules directly from `O` and `Q`.
3. Reduce both modules to exact central/Azumaya characters, retaining all fibers.
4. Decode the shift exponent in the public center basis without orbit enumeration.
5. Verify every candidate by `[x]P=Q`.

## Full rho/BSGS cost model

Let algebra setup be `N^c`, PI degree `N^pi`, center-generator degree/height `N^k`,
splitting-field degree `N^phi`, module reduction `N^e`, reciprocal Azumaya applicability
`N^zeta`, fiber ambiguity `N^u`, label readout `N^r`, verification `N^v`, and bit-memory
`N^s`. Rho costs `N^1/2` time; BSGS costs `N^1/2` time/memory. The candidate has time exponent
`lambda=max(c,pi,k,phi,e,zeta,u,r+v)` and memory exponent `mu=max(s,pi,k,phi,u)`. Full order-`N`
center generators or orbit labels fail the gate.

## Likely fatal obstruction

For order-`N` translation the PI degree or center-generator degree is expected to grow
like `N`. Central characters may be invariant on the entire translation orbit, while a
refinement that distinguishes point modules may simply label all `N` orbit positions.

## Proof track

Give an exact low-degree center quotient, prove separation of the shift orbit and public
label readout, and bound every algebra/module/fiber cost below exponent `1/2`.

## Disproof track

Prove PI/center degree is `N^(1-o(1))`, central characters are orbit-constant, or every
separating refinement is an order-`N` table or DLP.

## Positive and negative controls

- Positive control: exhaustive finite-order translations with full center materialized.
- Positive instrumentation control: synthetic matrix algebras with planted central labels.
- Negative control: commutative polynomial rings and random automorphisms.
- Circularity control: freeze center basis and module hashes before orbit labels.
- Cost control: charge full center generators, field elements, and fiber enumeration.

## Quantitative promotion and falsification gates

Use exact toy translations for prime `N<=31` across all supported Sklyanin parameters.
Promotion only to scaling requires zero center/module errors, a target-independent
separating character on at least 90% of declared instances, and upper 95%
`pi<=0.30`, `k<=0.30`, `u<=0.20`, `lambda<=0.45`, and `mu<=0.45`. Falsify if
PI/center lower 95% exponent reaches `0.50`, characters are orbit-constant, label readout
is an order-`N` DLP/table, or one scalar is wrong.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-028/sklyanin_center_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-028/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-028/runs/<run_id>/characters.jsonl`
- `ideas/artifacts/ECDLP-IDEA-028/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-028/analysis.md`

## Interpretation boundary

All evidence is toy, heuristic, model-bound, and novelty-unverified. Correct algebra or
center computation is not an ECDLP result; only independently verified public scalar
recovery below rho/BSGS can support escalation.

## Exactly one next executable action

1. Build exact toy Sklyanin algebras for prime translation orders through 31 and freeze central-character collision partitions before revealing point-module shift labels.
