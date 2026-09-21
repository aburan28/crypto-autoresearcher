# ECDLP-IDEA-066 — Frobenius–Ore transition intersection

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_merged`
- Evidence scale: `toy` exact-module preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with active `ECDLP-IDEA-056` and the P1478 shared-transition open branch
- Breakthrough claim: **none**; a short skew recurrence or correct decomposition is not an ECDLP break.

## Falsifiable hypothesis

For five-term membership split as forward `A2` and backward `R-A3` states, the
extension-field transition correspondence admits a Frobenius-stable module represented
by an Ore polynomial in `K[tau; tau*a=a^p*tau]` of order `L^(alpha+o(1))` with
`alpha<1.5`, where `L=N^beta` is the factor-deck size. A right-gcd/intersection in this
module is biconditional with an actual five-term witness, lifts every endpoint source
without materializing the dense backward state or two-transition resultant, and gives
full time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation was the **curve-specific Frobenius-closed transition module with an
Ore right-intersection and annotated source lift**. Intermediate Semaev roots in a
frozen extension are organized by semilinear Frobenius action; forward and backward
transition images become right submodules, and their common states are recovered by
skew gcd/module intersection. Source annotations are part of the module, not reconstructed
by an explicit state table.

Fast skew-polynomial multiplication, a different solver, an unannotated recurrence, a
dense resultant encoded in Ore notation, or a relation-only common root is a duplicate/control.

Independent review found no representation separation from `ECDLP-IDEA-056`: both
records posit the same two-transition shared module, common-state biconditional, exact
endpoint lift, and avoidance of the dense `L^2` object. Ore notation is only a backend
change unless the state set is proved additively/semilinearly closed and strictly smaller.

## Assumptions

1. `E(F_p)` has a known prime-order subgroup `<P>` of order `N=p^(1+o(1))` and challenge `Q=[x]P`.
2. The factor deck has `L=N^beta` public target-independent atoms and complete source charts.
3. A bounded extension `K/F_p` contains all required intermediate roots and its construction, Frobenius, and arithmetic are fully charged.
4. The transition state set is Frobenius closed and has a faithful Ore-module presentation smaller than the materialized state polynomial.
5. The right-intersection condition is necessary and sufficient, with exact multiplicities and source annotations.
6. Module construction, skew arithmetic, output, relation density, rank, target descent, verification, extension degree, and memory are charged.
7. All claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`five_term_Semaev_split | extension_intermediate_roots | Frobenius_closed_transition_module | Ore_right_gcd_intersection_iff | annotated_endpoint_source_lift | no_dense_backward_state`

No additive/semilinear closure theorem or strict separation from `056` was supplied.
The fingerprint is retained only as a collision key; merely running an Ore solver on the
existing dense object is barred.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, whose next branch is exactly a black-box common-root/source algorithm below `L^1.5` without a dense `L^2` object.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, the dense serial-S3 state and failed held-out recurrence boundary.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the exact one-transition subgroup-norm primitive and quadratic composition experiment.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, which closes tested public linear feature spaces for the same transition data.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, the solver-substitution control for five-term membership.

## Closest primary literature

- Caruso and Le Borgne, [Some algorithms for skew polynomials over finite fields](https://arxiv.org/abs/1212.3582), supplies skew arithmetic and factorization, not an elliptic transition module.
- Caruso and Le Borgne, [Fast multiplication for skew polynomials](https://arxiv.org/abs/1702.01665), supplies a faster backend but no source-resolving Semaev identity.
- Puchinger and Wachter-Zeh, [Fast operations on linearized polynomials](https://arxiv.org/abs/1512.06520), supplies subquadratic semilinear operations and also warns that such arithmetic can encode matrix multiplication.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the underlying relation family.

No checked source gives the stated curve-specific faithful module, biconditional, or
source lift. Novelty and the claimed order reduction remain unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,beta,L`, the factor deck, complete addition charts, extension `K`, and a five-term split.
2. Reproduce exhaustive forward `A2`, backward `R-A3`, and five-term witnesses on tiny curves.
3. Derive the Frobenius action and Ore presentations of both transition modules with source annotations.
4. Compute their right intersection, lift every common state to all endpoint tuples, and verify the biconditional independently.
5. For known `R=[a]P`, stream verified source-labelled relations until `L+margin` independent rows are collected.
6. Solve and independently verify factor-base logarithms.
7. Repeat the identical intersection on randomized `Q+[t]P` targets until a verified descent is found.
8. Substitute logs, remove `t`, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho uses `N^(1/2+o(1))` group operations and constant state; BSGS uses
`N^(1/2+o(1))` time and memory. Let `L=N^beta`, extension degree exponent `e`, module
build exponent `a`, faithful Ore order `L^alpha`, skew-operation exponent `sigma`,
reciprocal relation and target densities `N^delta,N^delta_t`, independent row output
`L^theta`, and retained memory exponent `mu`. Charge
`T_query=N^(e+beta*alpha*sigma+o(1))`, adding `beta*(1-theta)` when a batch emits fewer
than `Theta(L)` independent rows. The complete exponent is
`lambda=max(a,delta+e+beta*alpha*sigma+beta*(1-theta),2beta,delta_t+e+beta*alpha*sigma)`.

If the module order, extension degree, right-gcd output, or source lift is quadratic in
the materialized state size, that full exponent is charged. Promotion requires
`lambda<1/2` and `mu<1/2` against both rho and BSGS.

## Likely fatal obstruction

On rational endpoints Frobenius may add no compression: the semilinear orbit can be
trivial while the intermediate-root orbit has degree equal to the dense state polynomial.
The minimal faithful Ore operator can therefore have the same `Theta(L^2)` order as the
recorded resultant, and an unlabelled common state can have `Theta(L)` or more source
lifts. Extension arithmetic or source output then restores the rho boundary.

## Proof track

Prove Frobenius closure, faithful module order, and logarithmic source annotation; prove
the Ore right-intersection biconditional including exceptional roots; bound extension,
skew arithmetic, output independence, relation density, rank, target descent, verification,
and memory so the displayed `lambda,mu` are below `1/2`.

## Disproof track

Find a biconditional/source error, prove minimal Ore order `Omega(L^2)`, prove extension
degree or source multiplicity cancels the reduction, or establish complete-cost
`lambda>=1/2` on every frozen arm.

## Positive and negative controls

- Positive algebra control: planted low-order Frobenius modules with known right intersection and source labels.
- Positive ECDLP control: exhaustive five-term witnesses and endpoint tuples on tiny ordinary curves.
- Negative semilinear control: matched random transition sets with identical size but full Frobenius orbit degree.
- Mechanism control: dense backward state polynomial and dense two-transition resultant.
- Solver control: fast Ore arithmetic applied after materializing the dense object.
- Leakage control: forbid scalar coordinates, target-specific extensions, source tables, post-hoc root filters, and discarded misses.

## Quantitative promotion and falsification gates

No promotion gate remains because the semantic operation is already active as `056`.
The historical Phase 1 required zero errors in Frobenius closure, module action, multiplicities,
intersection biconditional, and endpoint source lift on all exhaustive instances. Phase 2
uses at least 20 ordinary curves per size, three seeds, `L in {16,32,...,4096}`, and
three preregistered extension policies. Promotion requires at least 1,000 verified
relations and 100 target descents at each of the two largest completed sizes,
`theta>=0.9`, upper 95% `alpha*sigma<=1.25`, and upper 95%
`lambda,mu<=0.45`, with stable sensitivity fits and no dense state artifact.

Falsify on any independently reproduced identity/source error, lower 95% Ore-order or
source-lift exponent at least `2` in `L`, `theta<0.5` at both largest sizes, or lower
95% `lambda>=0.50` in every arm. Infrastructure failures are not mathematical negatives.

## Artifact plan

- Retired draft contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-066_ore_transition_preflight.yaml`
- Derivation: `ideas/artifacts/ECDLP-IDEA-066/ore_module_identity.md`
- Implementation: `ideas/artifacts/ECDLP-IDEA-066/ore_intersection.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-066/verify_sources.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-066/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-066/analysis.md`
- Retain extension definitions, operators, skew polynomials, intersections, roots, sources, relations, ranks, targets, commands, seeds, environment, resources, stdout, and stderr.

## Interpretation boundary

This is a rejected toy, heuristic, model-bound, novelty-unverified representation hypothesis. A
short Ore polynomial, correct common state, valid relation, or recovered toy scalar is
not a breakthrough. Only source-resolving end-to-end costs below matched rho and BSGS can
justify further study.

## Exactly one next executable action

1. Preserve this record and `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-066_ore_transition_preflight.yaml` as the `056` collision control; do not execute it unless a future theorem proves additive Ore closure and a strict representation separation.
