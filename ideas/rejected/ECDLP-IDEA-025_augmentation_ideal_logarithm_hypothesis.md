# ECDLP-IDEA-025 — Augmentation-ideal logarithm

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; the exact group-ring identity is known and is not an efficiently evaluable ECDLP coordinate.

## Falsifiable hypothesis

For a prime-order subgroup `G=<P>` of order `N`, the augmentation quotient
`I/I^2` of `Z[G]` admits a target-independent, public-orientation realization of
dimension `N^(k+o(1))`, with `k<1/2`, in which the classes of encoded elliptic points
can be evaluated below exponent `1/2`. Since `[Q]-1=x([P]-1) mod I^2`, the public
coordinates then recover `x` below rho/BSGS after all construction, orientation,
collision, verification, and bit-memory costs are charged.

## Mechanism-new operation

Apply **augmentation linearization followed by a compressed coordinate realization**.
The operation is not a formal-group point jet (`004`), theta translation (`015`),
factor-base support oracle, solver change, or curve coordinate model. It seeks an exact
first-order group-ring quotient whose addition law is already linear; the missing new
operation is evaluating that abstract quotient from ordinary curve encodings without
materializing `N` basis states or importing their scalar labels.

## Assumptions

1. The realization and its basis orientation depend only on `E,P,N`, never on `x`.
2. Encoded point classes can be evaluated without enumerating all of `G`.
3. Equality and scalar multiplication in the quotient are exact and independently checked.
4. Construction dimension, coefficient height, collisions, orientation branches, and bit memory are charged.
5. Any hidden group-ring table or known-log labeling invalidates the mechanism arm.
6. Scaling claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`integral_group_ring | augmentation_quotient_I_mod_I2 | compressed_public_orientation | direct_linear_hidden_scalar_coordinate`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the relation/linear-algebra obstruction replaced by a single exact coordinate.
2. `ledger/H-REP-001.yaml` — prevents a curve-coordinate rewrite from counting as this quotient.
3. `ledger/EV-REP-002.yaml` — requires sign and encoding conventions to be fully audited.
4. `ledger/H-FB-001.yaml` — distinguishes one augmentation generator from a reshaped factor base.
5. `ledger/SYNTHESIS-20260716.md` — supplies the complete-cost and no-breakthrough boundary.

## Closest primary literature

- Sandling and Tahara, [Augmentation quotients of group rings and symmetric powers](https://doi.org/10.1017/S0305004100055651), develops the relevant augmentation quotients.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), bounds any realization simulable in the generic group model.

The abstract quotient and generic lower bound are known. No checked source gives the
claimed compressed evaluable realization for elliptic point encodings; novelty is unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is the single public class `L(P)`.

1. Freeze an integral group-ring presentation, quotient convention, coefficient ring, and orientation rule.
2. Construct a compressed candidate realization and prove that it respects `I/I^2`.
3. Evaluate `L(P)` and `L(Q)` directly from their curve encodings, retaining every ambiguity.
4. Solve the one-dimensional equation `L(Q)=xL(P) mod N` in the public basis.
5. Enumerate any collision list and return only a scalar satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Let reciprocal realization availability be `N^zeta`, construction `N^c`, representation
dimension `N^k`, coefficient-height arithmetic `N^h`, point evaluation `N^e`, orientation
branching `N^a`, coordinate solve `N^u`, collision/verification `N^v`, and bit-memory
`N^s`. Pollard rho costs `N^(1/2+o(1))` time and negligible memory; BSGS costs
`N^(1/2+o(1))` time/memory. The candidate has time exponent
`lambda=max(zeta+c,k,h,e,a,u+v)` and memory exponent `mu=max(s,k,h,a)`.
Any `N`-state group ring or order-`N` basis-label DLP contributes exponent at least `1`
or `1/2`, respectively, and kills promotion.

## Likely fatal obstruction

For a cyclic group, `I/I^2` is essentially the abelianization itself. Giving its generator
a public coordinate can be exactly the DLP. A faithful rational realization may require
`Theta(N)` states or coefficients, while any smaller projection may collide on the whole
orbit or secretly use scalar-labeled basis elements.

## Proof track

Construct an explicit sub-square-root realization, prove the augmentation identity and
public orientation, and bound evaluation, coefficient height, ambiguity, and memory so
that `lambda,mu<1/2` without scalar-indexed data.

## Disproof track

Prove every separating realization has dimension/height `N^(1/2-o(1))` or larger, or
show that orienting/evaluating it is equivalent to the original discrete logarithm.

## Positive and negative controls

- Positive control: the additive group `Z/NZ` with its canonical scalar encoding.
- Positive instrumentation control: the full exact `N`-state group ring on tiny groups.
- Negative control: random permutations of point encodings with matched group size.
- Circularity control: blind scalar labels until the realization and basis hash are frozen.
- Cost control: explicitly charge materialized basis states and coefficient bits.

## Quantitative promotion and falsification gates

Use 8–22-bit prime-order curves, at least 100 instances per size, and every exact
realization family frozen before labels are revealed. Promotion only to a scaling study
requires exact quotient identities on 10,000 triples, zero wrong labels, a public
target-independent orientation, and upper 95% `k<=0.30`, `h<=0.30`, `e<=0.40`,
`lambda<=0.45`, and `mu<=0.45`. Falsify if every separating realization has lower 95%
dimension or height exponent at least `0.50`, labeling uses a DLP/table, or one accepted
scalar is wrong. Missing algebra software is infrastructure evidence only.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-025/augmentation_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-025/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-025/runs/<run_id>/quotients.jsonl`
- `ideas/artifacts/ECDLP-IDEA-025/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-025/analysis.md`

## Interpretation boundary

The known identity is not a breakthrough. Every result remains toy, heuristic,
model-bound, and novelty-unverified until a public realization recovers independently
verified targets below both generic baselines with all representation costs charged.

## Exactly one next executable action

1. Enumerate exact toy augmentation-quotient realizations and measure the minimum public rational-coordinate dimension, coefficient height, and collision rate after blinded orientation.
