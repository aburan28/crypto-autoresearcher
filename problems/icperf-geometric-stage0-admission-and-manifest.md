# Geometric stage-0 dispatch and run-manifest admission gap

- **Status:** open
- **Kind:** execution admission and output-contract gap; the 2026-10-21 failed release has no established cause.
- **Affected work:** [EXP-ICPERF-b2f2d0](../experiments/EXP-ICPERF-b2f2d0/specification.yaml), [H-ICPERF-5adc9b](../ledger/hypotheses/H-ICPERF-5adc9b.yaml), [TASK-20261017-054f82](../ledger/handoffs/TASK-20261017-054f82.yaml), [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [DEC-20261025-ac9d10](../ledger/decisions/DEC-20261025-ac9d10.yaml).
- **Next action owner:** Coordinator for a fresh-ID prospective protocol and preapproval; an Executor implements a corrected emitter under a separately archived handoff.
- **Last updated:** 2026-10-25

## Problem

The frozen stage-0 contract specifies one seeded sample of 64 geometric
counts at success probability 1/50. Its original
[design queue](../coordination/design/TASK-20261017-054f82/dispatch_queue.json)
still lists the producer as queued and the trial plan points to that queue.
An epoch-1 claim was
[released failed](../coordination/design/TASK-20261017-054f82/claims/TASK-20261017-054f82.1.release.json)
on 2026-10-21 with empty artifact hashes and note RBS-ICPERF-c4a91e. No
trial output is committed under the experiment run directory in the
inspected branch. The release does not identify the failure cause or
establish whether a scientific process started.

Independently of that release, the bound
[runner](../experiments/EXP-ICPERF-b2f2d0/implementation/run.py)
writes a manifest containing run ID, experiment ID, status, stage and
sample fields. The standard supervisor run-schema check requires
run.code, environment, inputs, timing and result, including code.commit
and code.command. The local
[checker](../experiments/EXP-ICPERF-b2f2d0/implementation/check.py)
checks file presence, raw-result fields and manifest ID substrings. Its
exit zero therefore cannot establish supervisor-valid output. The static
source defect is prospective; it is not an explanation of the observed
failed release.

Admission for another claim is also incomplete: the frozen plan lacks
input_sha256, the specification lacks input_bindings, the separate
executor handoff lacks an exact execution map and archived_by, and this
design packet has no verified prospective approvable:true preapproval
receipt, complete archival binding or lawful open lane for a new claim.
The frozen specification is already approved, while the preapproval
probe requires a prospective review_required draft. Reusing the old
queue would not repair these fields.

## Evidence and uncertainty

- **Observed:** The predecessor queue SHA-256 is
  `92a37f0094b6689eeef54c7fb27164e7297ae3e2df0079500687fb297ac2c465`.
  The epoch-1 [claim](../coordination/design/TASK-20261017-054f82/claims/TASK-20261017-054f82.1.claim.json)
  was acquired at 2026-10-21T14:26:38Z and its release at
  2026-10-21T14:26:49Z reports failed, empty artifact_sha256 and the
  runbook-session ID. Only .gitkeep is present under the experiment's
  committed runs directory in this inspected branch. Frozen source
  hashes are listed in
  [CORR-20261025-ec1a62](../ledger/corrections/CORR-20261025-ec1a62.yaml).
- **Derived from code:** The pinned emitter omits required fields and
  experiment_execution.manifest_schema_errors calls
  validate_ledger.check_run. If this emitter reached that gate, the
  manifest it writes would be invalid_output. This is a code-path
  diagnosis, not the diagnosed cause of the failed release.
- **Suspected explanation:** Unknown. The release's note alone cannot
  distinguish admission refusal, runbook failure, output validation or
  another cause. Inspect a separately archived exact session record if
  it becomes available; do not infer one from its ID.
- **Missing capability:** A fresh-ID specification, plan, source,
  checker, runbook, handoff, archive and lane whose exact prospective
  bytes pass preapproval and whose positive and negative emitted
  manifests pass the same standard supervisor used for real output.
- **What this evidence does not establish:** The prerecorded sample
  outcome as a validated run, host latency, an 8 GiB table's probe
  distribution, a curve-specific improvement or an ECDLP cost.

## What would unblock it

- [ ] Allocate fresh EXP, RUN, TASK, batch and approval identities.
  Preserve the one seed 20261017, denominator 50, sample count 64 and
  single trial unless a separately reviewed amendment changes scientific
  scope. Bind exact source/input SHA-256 values and new identities.
- [ ] Emit every required run-manifest field, including code.commit,
  code.command, environment, inputs, timing, result and
  certificate.kind none. A no-science positive fixture must pass the
  standard supervisor using the actual emitter and checker. Negative
  controls must reject missing or empty required output, changed
  provenance, forged digest and a manifest missing one required schema
  field.
- [ ] Match exact execution mapping and archived_by in the new producer
  card and handoff. One Coordinator archive task must depend on the
  producer, name it in source_task_ids, and cover all eight
  supervisor-generated outputs plus the three trial outputs in its
  read scope and content-first receipt.
- [ ] Commit a runbook LINT OK receipt and a lawful goal lane for the
  exact successor queue. While the successor is review_required,
  experiment_preapproval.py --packet must report approvable:true for
  its exact specification, plan, handoff and queue. A committed
  Coordinator approval and archive then precede a Ready selector and
  any /run claim.

These checks establish a runnable instrument and output custody, not
a host-latency mechanism or measured IC improvement. Historical
EXP-ICPERF-b2f2d0 and H-ICPERF-5adc9b retain their approved status;
DEC-20261025-ac9d10 withholds ordinary selection of the old contract.

## Next discriminating step

- **Action or proof obligation:** Prepare a fresh-ID one-seed successor
  and run the read-only prospective preapproval probe; separately
  exercise its emitter through a no-science standard-supervisor fixture
  before scientific dispatch.
- **Inputs and controls:** Keep the original parameter tuple and
  prerecorded expected fields visible. A deliberately incomplete
  manifest must fail the same gate as a real run. Changed source hash,
  missing lane/archive path and missing input binding must each make
  preapproval false.
- **Execution limits and stop condition:** No new claim on the old task.
  The prospective instrument remains one sample with a documented
  60-second watchdog and 1 GiB task protection unless amended; any
  scientific launch goes through /run after approval.
- **Outcomes and next actions:** A complete packet and valid fixtures
  permit Coordinator approval of the fresh protocol subject to ECC
  ranking. False acceptance requires another correction. A fixture
  crash is infrastructure evidence only.
- **Recheck trigger:** A committed fresh-ID candidate with exact
  source/input hashes, valid fixture and lawful queue/lane; or a
  separately archived exact RBS-ICPERF-c4a91e session record that
  explains the historical release.

A planned step is not a completed experiment. Apply the normal
execution, review and archival rules before acting on it.

## Resolution and history

- 2026-10-21: Epoch-1 task claim was released failed with empty
  artifact_sha256 and a runbook-session note. No committed trial output
  is present in this inspected branch. Cause remains unknown.
- 2026-10-25: [DEC-20261025-ac9d10](../ledger/decisions/DEC-20261025-ac9d10.yaml)
  withholds the exact experiment from ordinary selection and
  [CORR-20261025-ec1a62](../ledger/corrections/CORR-20261025-ec1a62.yaml)
  supplies a zero-Ready successor queue. Frozen records are retained.
  No scientific status or claim changes.

Unresolved. Completing this record or merging its PR does not establish a
research result.
