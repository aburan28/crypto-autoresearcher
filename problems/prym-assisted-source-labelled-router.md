# Prym-assisted relations lack a source-labelled router

- **Status:** `open`
- **Kind:** missing construction, implementation and comparative measurement;
  a scoped prior algebraic argument is linked, not a universal obstruction
- **Affected work:** [issue #2414](https://github.com/aburan28/crypto-autoresearcher/issues/2414),
  [IDEA-20260909-4c5ee9](../ledger/proposals/IDEA-20260909-4c5ee9.yaml),
  [ECDLP-IDEA-002](../ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md),
  [the follow-up](../research/prym_relation_followup_20261019/README.md),
  RQ-ECDLP-002, GOAL-ECDLP-001 and GOAL-ICEX-001 (existing goal states unchanged;
  design-only work is recorded under BATCH-c406ea)
- **Next action owner:** Coordinator, for mechanism selection and runnable design
- **Last updated:** 2026-10-19

## Problem

The owner-requested Prym-assisted prime-field ECDLP follow-up cannot yet
establish a useful relation-generation improvement because no explicit public
source-labelled router outside the recorded fixed-branch scope, or matched
current IC baseline, is supplied.

For ordinary E/F_p, prime-order G=<P> and Q=[k]P, the intended route keeps G in
J(D) and uses auxiliary Prym constraints to locate relations. It is distinct
from direct algebraic transfer E->Prym: the latter has Frobenius-compatibility
and nonzero-image gates, while the natural anti-invariant projector kills the
conorm image. That fact does not reject auxiliary relation search.

## Evidence and uncertainty

- **Observed:** the existing proposal already includes residual/nonlinear
  Prym companion cancellation. The [P1546 record](../ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md)
  supplies a scoped bounded-branch counting argument and names compact
  growing-degree/adaptive routing as an unresolved operation. The
  [PO-transfer-003 record](../inputs/refs/experiments/ecdlp_isogeny/po_transfer_003_result.md)
  reports earlier toy relation/recovery observations. These are retrieved
  historical records, not fresh execution or an independent review here.
- **Derived or proved:** the follow-up states the standard push-pull and
  anti-invariant identities as interface constraints, not a new certified
  result. P1546's theorem labels are attributed to its frozen record. No
  universal lower bound or absence of other Prym algorithms is established.
- **Suspected explanation:** branch enumeration, duplicate projected images,
  unknown tuple-first source logs, or post-hoc kernel residuals may erase a
  proposed gain. Which applies to a future router remains to be tested.
- **Missing capability:** explicit target-local construction, independently
  checkable source witnesses, admitted fixtures/collector, frozen matched
  baseline and complete costs. These are design/implementation gaps.
- **What this evidence does not establish:** novelty, a new performance
  advantage, below-rho recovery, a weak deployed curve, or impossibility.
  The unsourced count of 32 covers and chat-only F_43 example are not native
  experiment evidence. No new scientific run is cited or authorized.

## What would unblock it

- [ ] Specify one public router/batched constructor, its representation,
  exact source-return interface, degree/genus/field costs and applicability.
  Explain its precise distinction from P1546's fixed-branch/dither scope.
- [ ] Independently check maps, exceptions, norm witnesses, order-r retention,
  unique projected columns and useful rank; prevent hidden-log/target leakage.
- [ ] Bind the current verified IC baseline and freeze a runnable controlled
  successor through existing approval, admission and archive routes.
- [ ] Measure complete S, memory and blind recovery on matched instances,
  retaining all failures, and obtain independent review. A verified reduction
  against the current IC baseline is progress; rho is a separately reported gap.

The first item unblocks design, not a performance claim. The later items are
required for empirical advancement; crossing rho is not a prerequisite for
recording an incremental improvement. No acceptance checkbox changes a
scientific status without the existing Coordinator decision.

## Next discriminating step

- **Bounded engineering tests:** the [four-stage experiment programme](../research/prym_experiment_design_20261019/README.md)
  now specifies geometry checks, public-source/rank controls, a concrete PO003
  companion-bucket selector and blind complete-cost comparison. Arithmetic and
  selector components exist; generator/canonicalizer/checker integration,
  current baseline and native execution admission remain due. This selector
  tests a fixed generator within its existing scope; it does not resolve the
  compact-router problem below.
- **Action or proof obligation:** write the concrete router interface and
  scope comparison described in [the design step](../research/prym_relation_followup_20261019/README.md#next-discriminating-design-step).
- **Inputs and controls:** the pinned existing proposal/P1546 record, direct
  elliptic and split-product controls, known-false source labels and a
  proposed frozen atom base. Actual fixtures are not yet admitted.
- **Execution limits and stop condition:** this is design intake, not a
  runnable trial. Scientific execution requires a separately complete,
  admitted protocol with samples, seeds, machine limits and stopping rules.
  No campaign spending cap or production-target run is introduced.
- **Outcomes and next actions:** a distinct explicit construction proceeds
  to runnable design; a duplicate records its exact scope and missing
  operation; a proof gap remains open; tool/access failure is infrastructure
  evidence only. Never restart IDEA-002 merely because this issue exists.
- **Recheck trigger:** a concrete router/correspondence, source-witness
  implementation, comparative baseline or relevant scoped proof update.

## Resolution and history

2026-10-19: owner-requested follow-up recorded in issue #2414 and the
machine-readable companion. Existing goals, hypotheses, protocols and queues
remain unchanged. The missing operation is unresolved; filing or merging this
record does not establish an algorithmic result.

2026-10-19 follow-up: four proposed hypotheses and review_required experiment
designs added, together with prospective arithmetic/selector components and
software checks. No scientific trial or measured advantage. Existing
scientific records were preserved; a separate design queue tracks this work.
