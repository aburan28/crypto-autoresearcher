# ECDLP Candidate Checklist

## Candidate name

Symmetry-corrected recursive coordinate expansion and split compiler.

## Target curve family

- prime field: generated ordinary prime-order short-Weierstrass curves over seeded `F_p` with `p mod 4 = 3`
- binary field: no
- extension field: no
- special curve class: no weak curve class selected; the modulus congruence is restricted for deterministic square roots, while special `j`, selected smooth `p-1`, anomalous, supersingular, and non-prime-order cases invalidate a run

## What structure is exploited?

Coordinate predicates define factor-base fibers whose exact additive support may expand near a random set at depth `m`, while smaller split supports may admit reusable fixed-curve advice.

## Why does deployed prime-field ECDLP not obviously kill it?

The candidate uses coordinate membership and fixed-curve preprocessing unavailable in the generic-group model. This is an `UNTESTED` route, not evidence of a deployment-level advantage.

## Factor base

- definition: matched-cardinality random-scalar, random-x, x-interval, square-map, rational-union, and scalar-progression families under sign-canonical and sign-complete modes
- size: smallest even `B` satisfying `binomial(B+m-1,m)/q >= 0.5`; this is a `HEURISTIC` sizing rule only
- membership test cost: recorded through each construction path; random-x uses the same square-root and subgroup path as coordinate predicates

## Relation generation

- relation shape: `P_1 + ... + P_m = Q` for `m in {5,6,8}`
- expected probability: exact `|mA|/q` is primary; unordered Poisson occupancy is only a control
- decomposition method: compile witness-bearing supports of depths `floor(m/2)` and `ceil(m/2)`, scan the smaller side, and stop at the first exact complement
- cost per attempt: measured online group operations and lookups per target
- cost per relation: measured per successful target, with unsuccessful targets retained

## Linear algebra

- matrix dimensions: not yet defined
- density: not yet measured
- rank expectation: `UNTESTED`
- modulus: eventual relations would be over the prime subgroup order `q`

## Individual logarithm / target descent

- method: not yet defined
- expected cost: `OPEN`; a preflight promotion cannot become an attack claim without this gate

## Baselines

- rho cost: measured on every generated curve using the same affine arithmetic; generic expectation is `Theta(sqrt(q))`
- parallel rho cost: not measured in this preflight
- BSGS cost and memory: `Theta(sqrt(q))` reference baseline
- closest known IC cost: rational-map and summation-polynomial point-decomposition methods; this prototype does not claim novelty for those factor-base families

## Claimed advantage

- asymptotic: none
- constant factor: none before a canonical verified run
- memory: promotion charges functional advice deep bytes through a matched-random `S*T^2/(epsilon*q)` ratio; entry count alone cannot pass
- parallelism: not evaluated
- amortized many-target setting: the intended fixed-curve use case, with offline and online costs reported separately

## Things that would kill the idea

- Coordinate families match random exact support and split costs after fair construction controls.
- Compression appears only with proportional loss of final support.
- Functional witness bytes or memory bandwidth dominate the nominal advice count.
- A signal fails across seeds or sizes, disappears under independent replay, or relies on exceptional curves.
- Relation rank, linear algebra, or individual descent erase a preflight advantage.
- Fully charged preprocessing leaves the candidate at or above the generic fixed-curve frontier.

## Frozen outcome

`EXP-ECDLP-RECURSIVE-001` completed and independently replayed. Its frozen gate crossed for three sign-complete `m=8` families, but every passing row had generic-maximum four-term support and near-random advice bytes. One curve was anomalous despite this checklist, and one-draw random controls were too dispersed for family promotion. The decision is `REVISE_INTERPRETATION`, not a compiler or ECDLP promotion.

## Next experiment

Use a versioned successor with non-anomalous/special-`j` enforcement, replicated paired nulls, order-independent scan cost, and exact support percentiles. Preserve both frozen runs unchanged.
