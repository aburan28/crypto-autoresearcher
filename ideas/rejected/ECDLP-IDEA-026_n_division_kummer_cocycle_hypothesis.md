# ECDLP-IDEA-026 — N-division Kummer cocycle

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; exact Kummer linearity or a toy cocycle is not a cheap scalar coordinate.

## Falsifiable hypothesis

For a prime-order subgroup `G=<P> subset E(F_p)` of order `N`, the Kummer connecting
class `delta_N(R) in H^1(F_p,E[N])` can be represented and publicly oriented in a
sub-square-root quotient of `E[N]/(Frob-1)E[N]`, with division-field, lift, cocycle,
and basis costs below exponent `1/2`. Exact linearity
`delta_N(Q)=x delta_N(P)` then yields and verifies the hidden scalar below rho/BSGS.

## Mechanism-new operation

Compute a **global N-division torsor cocycle and project it to an explicit cohomology
coordinate**. This is not the characteristic-`p` deformation jet of `004`, trace-zero
transfer `009`, cover-orbit enumeration `010`, or a relation certificate. It changes the
point into a Galois cocycle; the required new operation is a compressed public basis and
division lift that does not already encode `x`.

## Assumptions

1. The `N`-division torsor, Frobenius action, and quotient basis are constructed without `x`.
2. Division-field degree, polynomial height, lift multiplicity, and Galois action are fully charged.
3. The quotient retains the order-`N` class and has a public scalar-coordinate rule.
4. Cocycle comparison does not call a DLP in `E[N]` or a roots-of-unity group.
5. Every lift and orientation branch is recorded before scalar labels are revealed.
6. All scaling evidence is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`N_division_torsor | Kummer_connecting_cocycle | Frobenius_coinvariant_quotient | public_scalar_ratio`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field relation bottleneck replaced by a cohomology coordinate.
2. `ledger/H-REP-001.yaml` — distinguishes a Galois cocycle from a curve-equation model.
3. `ledger/H-ISO-001.yaml` — this is not a same-field isogeny neighbor.
4. `ledger/EV-REP-002.yaml` — requires all lift and sign branches to be audited.
5. `ledger/SYNTHESIS-20260716.md` — supplies end-to-end verification and complete-cost gates.

## Closest primary literature

- Schaefer, [Computing a Selmer group of a Jacobian using functions on the curve](https://arxiv.org/abs/1507.08325), supplies the explicit descent/Kummer boundary.
- Tate, [Endomorphisms of Abelian Varieties over Finite Fields](https://eudml.org/doc/141848), supplies the Frobenius-module boundary.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), applies if cocycle evaluation is generically simulable.

These sources do not construct the claimed cheap public orientation for the order-`N`
connecting class. Novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the single cocycle class `delta_N(P)`.

1. Freeze the exact Kummer sequence, torsion field, Frobenius matrix, cocycle convention, and quotient basis rule.
2. Construct all `N`-division lifts of `P,Q` or a certified compressed torsor representation.
3. Evaluate and canonicalize `delta_N(P),delta_N(Q)` with every branch retained.
4. Solve their scalar ratio in the public coinvariant basis.
5. Test every ambiguity and return only `[x]P=Q`.

## Full rho/BSGS cost model

Let torsion-field degree be `N^k`, torsor setup `N^c`, polynomial height `N^h`, cocycle
evaluation `N^e`, lift branching `N^a`, quotient orientation `N^o`, coordinate solve
`N^u`, verification `N^v`, and bit-memory `N^s`. Rho costs `N^1/2` time; BSGS costs
`N^1/2` time/memory. The candidate has time exponent
`lambda=max(k,c,h,e,a,o,u+v)` and memory exponent `mu=max(s,k,h,a)`. An order-`N` torsion DLP,
degree-`N` division field, or `N`-branch lift immediately fails the square-root gate.

## Likely fatal obstruction

Producing an `N`-division lift can require degree `Omega(N^2)`. The rational coinvariant
line has no canonical orientation: choosing a generator may be exactly choosing the
discrete logarithm. Lang-type vanishing can make the abstract class computable only after
solving the same division problem it was meant to replace.

## Proof track

Give an explicit compressed torsor and quotient basis, prove exact Kummer linearity and
nonvanishing on `G`, and bound degree, height, branches, evaluation, and memory below
the generic boundary.

## Disproof track

Show the required division field/lift set is square-root or larger, the coinvariant basis
is unorientable without a DLP, or the computable class vanishes/collides on `G`.

## Positive and negative controls

- Positive control: small-`m` descent where all division points are exhaustively known.
- Positive instrumentation control: oracle division lifts, reported separately.
- Negative control: randomized quotient bases and unmatched Frobenius modules.
- Leakage control: freeze basis and cocycle hashes before revealing point logs.
- Cost control: charge complete division polynomials and extension-field bits.

## Quantitative promotion and falsification gates

Use 7–20-bit prime-order curves, at least 100 instances per size, and exact exhaustive
division truth through 14 bits. Promotion only to scaling requires zero cocycle or scalar
errors, nonzero public classes on at least 90% of promoted instances, and upper 95%
`k<=0.30`, `a<=0.20`, `e<=0.40`, `lambda<=0.45`, and `mu<=0.45`. Falsify if
degree or branching has lower 95% exponent at least `0.50`, orientation is a DLP, every
class vanishes, or one scalar fails verification.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-026/kummer_cocycle_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-026/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-026/runs/<run_id>/cocycles.jsonl`
- `ideas/artifacts/ECDLP-IDEA-026/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-026/analysis.md`

## Interpretation boundary

An exact cocycle identity or oracle-lift toy result is not a break. The hypothesis is
toy, heuristic, model-bound, and novelty-unverified until public target recovery beats
rho/BSGS with all field and lift costs included.

## Exactly one next executable action

1. Compute complete Kummer cocycles on exhaustive toy prime-order curves and measure division-field degree, lift multiplicity, quotient orientation ambiguity, and scalar collisions.
