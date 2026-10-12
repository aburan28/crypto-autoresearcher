# Chord-slope fibre design audit

## Audit basis

- Idea: `IDEA-20261006-76e571`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Adjacent proposal: `IDEA-20261007-fd7c23`, a canonical-point chord-slope
  image measurement over `F_19`.

## Novelty and scope

The proposed `F_53` statistic measures image loss of the chord-slope map
`P -> sigma(P)` under translation by one selected subgroup generator, then
asks whether slope labels split after another translation. This is a finite
representation census. It does not define a walk, factor base, relation
system, sum-compatible bucket index, or improvement to the generic
square-root baseline.

The translation/fibre statistic is a real difference from the `F_19`
canonical-point image proposal, but the two belong to the same chord-slope
measurement family. A second execution should be justified by the explicit
translation/fibre question, not by presenting it as a new ECDLP mechanism.

## Contract defects

The definition of `b` is incomplete. For a slope value `s`, the record asks
for the set of `sigma(P+G)` over the fibre `sigma(P)=s`, but the domain only
guarantees `P+G` is in `D`; it does not guarantee `P+2G` is in `D`, which is
needed to evaluate `sigma(P+G)`. The repair must choose one rule before any
counting: restrict to the two-step-valid domain and report the discarded
boundary mass, define a sentinel for the second shift, or use a different
partial-map statistic. The denominator for `b` must then state whether it is
all image values, only values with at least one two-step-valid preimage, or a
weighted point-level fraction.

The curve and subgroup selection also need exact certificates. The record
must bind the selected `B`, discriminant, point count, largest prime factor
`n`, the order certificate for `G`, the subgroup membership test, and the
complete list of excluded identity, `-G`, vertical-chord, and boundary cases.
“First affine point of order n” must be implemented as an order-verified
selection, not inferred from a point-count factor alone.

The vertical-chord sentinel must remain outside `F_53`; any comparison of
image sizes or fibres must count it as a named extra label. All affine
denominators and every translated point used in a scored row require exact
on-curve and subgroup checks. The second-generator arm must be a side control
with the same domain and boundary rules, not a replacement selected after
seeing the primary result.

## Statistical and interpretive limits

The thresholds `L >= 1/5` and `b >= 1/2` are finite decision boundaries on a
subgroup of only a few dozen points. They are not estimates of a limiting
fibre law. The proposed random-surjective-function comparison is a heuristic
nearby null; if it is retained, the codomain size, rejection rule, boundary
handling, and seed stream must be frozen, and a null failure must be reported
as an unusable model rather than converted into support.

A small image can arise from the rational function and the selected finite
domain without yielding a usable collision or a scalar-dependent predicate.
Passing both thresholds therefore does not establish a useful walk or a
cryptanalytic gain. A failed threshold closes only this curve, subgroup,
generator, domain, and statistic; it does not close chord-slope maps in
general.

## Disposition and next action

Disposition: **keep proposed as a conditional finite representation
measurement; do not approve it as an attack direction as filed.** Repair the
definition of `b`, add complete order/domain certificates, and separate the
translation/fibre question from the adjacent `F_19` image census. If the
repair produces a runnable control contract, it may be considered under the
ordinary readiness gate with a finite-measurement claim ceiling. Otherwise
leave the proposal unexecuted and do not promote its two thresholds.
