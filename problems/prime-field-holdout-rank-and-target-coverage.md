# Direct holdout matrices leave unresolved base directions

- **Status:** `investigating`
- **Kind:** observed finite rank/target-coverage limitation; cause unknown
- **Affected work:** [A4 results](../research/prime_field_a4_execution_20261030/RESULTS.md), [frozen protocol](../research/prime_field_a4_execution_20261030/protocol.json), and [A3 comparison](../research/prime_field_a3_execution_20261030/RESULTS.md)
- **Next action owner:** prospective design Coordinator, then admitted Executor
- **Last updated:** 2026-10-30

## Problem

The direct signed-three-sum collector does not yet provide full base information
or natural target recovery with base uncertainty remaining on the four A4
holdouts; the effects of source selection and factor-base geometry are unknown.

The completed experiment used two hash-selected prime-order a=2 curves over
each of F8191 and F65537, respectively16 and32 native norm atoms,64public
sources1..64 in hash order, and8 independently hashed point targets per curve.
The same full64 public-anchor projection was used at prefixes0/16/64. No
historical preprocessing or target scalar labels were supplied. Both fields
and base sizes were fixed before native curve generation; this is not an
asymptotic scaling comparison.

## Evidence and uncertainty

- **Observed:** at full64sources, ranks/projected columns were15/16,14/14,
  30/32 and23/31. All generation/source/target/query/affine/kernel/certificate
  checks completed, with zero unknown cells. The sole recovered target was
  p8191-i1/index6 at full source rank; the prospective public diagnostic also
  found [62]Q=-P, an elementary alternate explanation of its scalar1466.
  No early single or joint recovery occurred. See immutable run
  [a4-holdout-panel-c47bc8](../research/prime_field_a4_execution_20261030/runs/a4-holdout-panel-c47bc8/analysis.json),
  scientific source d12aee8d6bec91cd225afe2d5b5ceec605129cd6.
- **Derived:** target-column cancellation adds one base dimension on two
  fixtures at prefix0; at prefix64 the corresponding base gains are0/0/1/0.
  Dense rank subtraction and carried target-unit certificates were checked.
  These rows do not determine a target while base uncertainty remains.
- **Suspected explanation:** the small public scalar window, the first-norm
  base geometry, finite relation coverage or their interaction may account
  for deficient spans. None has been isolated as a cause. Extra rows alone
  do not establish their independent information.
- **Missing capability:** a prospectively matched source-selection control
  on the same curve/base/projection, followed by a separately controlled base
  comparison if needed. Complete weighted costs and matched rho remain
  separate unmeasured obligations.
- **Limits:** four small selected fixtures do not prove a general rank bound,
  impossibility of prime-field index calculus, novelty or a scalable attack.
  A4 is a valid completed finite observation, not an infrastructure failure.
  This record does not replace the broader
  [Prym source-labelled-router problem](prym-assisted-source-labelled-router.md).

## What would unblock it

- [ ] Complete an independently checked source-selection comparison on these
  exact fixtures: same base, original projected columns, table, target points,
  number of public source queries and stopping rule, varying the public scalar
  selection only. Freeze multiple hash seeds before affected generation.
- [ ] Retain all source/base coincidences as explicitly charged affine anchor
  information; do not shrink the unknown space and silently credit that as
  new relation rank. Report relation-only and anchor-augmented scopes clearly.
- [ ] Retain complete kernels, target syndromes, cancellation ranks and public
  recovery certificates in both arms. Record every miss and failure, without
  requiring a positive result to complete the comparison.

These conditions would isolate a finite selection effect if observed. They
would not establish a new algebraic router or a complete attack-cost advantage.
Actual recovery with uncertainty remaining needs a naturally produced target
combination annihilating the retained kernel, with an independently checked
certificate and an explicit public-coincidence explanation boundary.

## Next discriminating step

- **Action:** separately specify a same-size small-window versus hashed-public-
  scalar control, rather than immediately expanding the factor base.
- **Inputs/controls:** all four retained A4 fixtures, original anchors/columns,
  complete pair tables,32fixed targets and prospectively fixed source seeds.
  These fixtures are now observed, so this is a conditioned follow-up, not a
  new blind holdout.
- **Limits/stopping:** a fresh complete source-bound protocol/release and real
  checkpoint must declare the exact stream and protective machine limits;
  no new trial has been authorized by this problem record alone.
- **Outcomes:** changed rank/syndromes motivate fresh holdouts and complete-cost
  study; equal deficient spans motivate a one-factor base-geometry comparison.
  A bounded miss preserves the untested broader direction. An implementation
  failure requires an additive repair, not a mathematical verdict.
- **Recheck:** after the source-control experiment or a new explicit relation
  construction, with its complete retained record.

## Resolution and history

2026-10-30: recorded the completed A4 holdout observations and the next causal
control. Unresolved. No goal, hypothesis or canonical generic-lead status changed.
