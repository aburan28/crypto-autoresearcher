# ECDLP-IDEA-017 — Tropical component-group CRT descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a chip-firing congruence or valid specialization is not a break.

## Falsifiable hypothesis

There is a target-independent family of semistable models and explicit specialization
invariants whose graph Jacobian/component-group images reveal compatible residues of the
hidden scalar `x`, with total modulus product exceeding `N`, while construction, ambiguity,
and CRT recovery cost less than `N^(1/2)`. The hypothesis requires more than ordinary
group-homomorphic specialization: it predicts a certified marked-section invariant that
retains the residue label without a component group of size `N`.

## Mechanism-new operation

Map marked sections to divisors on reduction graphs, solve their chip-firing coordinates,
and combine scalar residues across independent degenerations. The claimed operation is
**multi-model component residue extraction plus CRT**. It differs from idea 016's single
toric DLP and idea 005's global-height lattice; if every invariant is merely a homomorphism
from a prime-order group to a smaller component group, the mechanism is immediately dead.

## Assumptions

1. `E/F_p`, `P`, and `Q=[x]P` lift to each frozen semistable model without using `x`.
2. Each invariant has a proved scalar law and a public map to a modulus `r_i`.
3. Ambiguous lifts and component labels are enumerated and charged.
4. The product of effective pairwise-compatible moduli exceeds `N`.
5. Graph construction, chip firing, model degree, and storage are fully charged.
6. Claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`multiple_semistable_models | marked_section_graph_specialization | component_residue_invariants | chip_firing_CRT_scalar_recovery`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct scalar-residue route.
2. `ledger/H-REP-001.yaml` — distinguishes graph specialization from a coordinate rewrite.
3. `ledger/H-ISO-001.yaml` — distinguishes independent degenerations from isogeny walking.
4. `ledger/H-FB-001.yaml` — no ordinary point factor base is being reshaped.
5. `ledger/SYNTHESIS-20260716.md` — supplies the complete-cost boundary.

## Closest primary literature

- Baker, [Specialization of linear systems from curves to graphs](https://doi.org/10.2140/ant.2008.2.613), develops divisor specialization to graph Jacobians.
- Cais, [Canonical extensions of Néron models of Jacobians](https://arxiv.org/abs/math/0603689), supplies the nearby component/torsion boundary.
- Shoup, [Lower bounds for discrete logarithms](https://www.shoup.net/papers/dlbounds1.pdf), applies if the invariants are generic simulations.

The sources do not provide the residue-extracting family asserted here; novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the union of frozen graph-component generators.

1. Construct each semistable model, reduction graph, component group, and marked-section specialization.
2. Express the images of `P,Q` in the explicit chip-firing basis and derive all permitted scalar residues.
3. Reject trivial maps and retain every ambiguity or incompatible residue.
4. Accumulate models until the certified effective modulus product exceeds `N`.
5. CRT-combine candidate residues, enumerate surviving branches, and verify each candidate on `E`.

## Full rho/BSGS cost model

Let number of models be `N^m`, total construction exponent `c`, largest graph/component
representation exponent `g`, ambiguity exponent `u`, and storage `s`. Rho costs `N^1/2`
time and negligible memory; BSGS costs `N^1/2` time/memory. Here
`lambda=max(m+c,g,u)` and `mu=max(s,g,u)`, with all modulus factoring and CRT included.
The total information must be measured as `log(product r_i)` after collisions, not as raw
component-group sizes.

## Likely fatal obstruction

A homomorphism from a group of prime order `N` to a component group of order coprime to
`N` is trivial; a nontrivial homomorphism forces an `N`-torsion component and therefore
size at least `N`. Nonhomomorphic section labels may depend on arbitrary lifts and fail the
scalar law. This is a strong structural reason to expect immediate falsification.

## Proof track

Construct a genuinely nontrivial marked-section residue invariant, prove its scalar law and
compatibility across models, and show its total information and costs yield
`lambda,mu<1/2`.

## Disproof track

Prove every lift-independent scalar-compatible invariant factors through the component
group homomorphism and is trivial unless the model has size `Omega(N)`, or demonstrate
lift-dependent/colliding residues on exhaustive curves.

## Positive and negative controls

- Positive control: composite-order toy groups with planted maps to coprime component quotients.
- Positive instrumentation control: exact chip-firing coordinates on enumerable reductions.
- Negative control: prime-order groups mapped to coprime component groups.
- Lift-choice control: independently vary every admissible marked section.
- Cost control: one model with an explicit order-`N` component, charged at full size.

## Quantitative promotion and falsification gates

Test 10–26-bit prime and composite controls, at least 100 models per size, and exhaustive
lift choices through 18 bits. Promotion requires exact scalar laws, zero wrong CRT
candidates, effective information at least `log2(N)+32` bits, and upper 95%
`lambda<=0.45`, `mu<=0.45` without any component/model of exponent `>=0.45`.
Falsify the scoped claim if all prime-order images are trivial, any residue changes under
an allowed lift, effective information slope is zero, or every complete-cost lower bound
reaches `0.50`. Missing model support is coverage evidence only.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-017/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-017/component_crt.sage`
- `ideas/artifacts/ECDLP-IDEA-017/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-017/runs/<run_id>/components.jsonl`
- `ideas/artifacts/ECDLP-IDEA-017/runs/<run_id>/residues.jsonl`
- `ideas/artifacts/ECDLP-IDEA-017/analysis.md`

## Interpretation boundary

This is a high-risk toy, heuristic, model-bound, novelty-unverified hypothesis with a
likely group-theoretic obstruction. Correct graph arithmetic is not evidence of an ECDLP
improvement.

## Exactly one next executable action

1. Exhaustively test whether any frozen marked-section component invariant is nontrivial and lift-independent on 10–18-bit prime-order controls.
