# PEXT prospective source-binding reconciliation

Prepared by the native Codex Coordinator at main `351c9c021c7be044ade54dc7e352b33d3a772244` under policy
`coordinator-orchestration-code`, effort `high`. This is an operational correction,
with zero scientific trials and no scientific status transition. The preparation
is not represented as a repository-dispatched or claimed task; `TASK-20261026-b5c69a` is the
future, separately claimable verification/adoption task and `TASK-20261026-1133c2` owns archival.

## Observation and correction

`experiments/EXP-PEXT-212d5c/trial-plan.json` binds the old Lean source `9768a6311793bf910859fee56fe6ea313851c9cab9c8a92d38a45efbce67148d`. Main contains `101db51900890e8fd619e3f437c15e96f7bb6e7f4b15899541cc249234615f3d`,
introduced by `530f91754413ed88e0f41fb7bed0633f909eed6d`.
The prior native run release for TASK-20261024-672126 in PR #2601 says abandoned:
the supervisor refused on this mismatch before launching a trial. The base
main PEXT runs tree contains only `.gitkeep`.

Only this source digest changes in the plan. Plan SHA `4841ed803323b814ec703c8cedcaf163bed82cf9bf26053933e95896f5acc6a6` becomes `9e47c88492631d31b5e29d704c268a8877b62fcc6bf9664c8869233ebc591417`.
The embedded queue handoff and external executor handoff bind the new digest.
The original approval DEC-20261024-992998 is retained; `experiments/EXP-PEXT-212d5c/amendments/AMD-EXP-PEXT-212d5c-20261026-source-binding.yaml` and `DEC-20261026-8a6d90`
state exactly which execution bindings and precondition they supersede.

## Sources read before choosing this correction

- Internal primary contract: AGENTS.md, agents/coordinator.md,
  docs/task-lifecycle.md, docs/experiment-protocol.md,
  .claude/skills/coordinate/SKILL.md and its workflow/lifecycle references.
- Internal primary PEXT records: DEC-20261024-e29f4c,
  DEC-20261024-992998, H-PEXT-d536a1, the original plan, queue and handoff.
- Primary implementation correction: the actual Lean diff at `530f91754413`,
  docs/reports/pext-n7-lean-validation-20261024/README.md, receipt.json,
  fixed-build.log, hosted-gate-followup.json and its build log. The receipt
  records eight named theorem axiom reports under Lean 4.34.1. This preparation
  checks their recorded source and log hashes; it does not rerun the build or
  promote those lemmas into a proof of the full genus-floor claim.
- Internal procedural precedent:
  experiments/EXP-CMFB-cea1d2/amendments/AMD-EXP-CMFB-cea1d2-20261015-schema.yaml.

All citations above have provenance `internal`, checked by native Coordinator
preparation for `DEC-20261026-8a6d90`. Scientific papers, including KN-LIT-bf1772, are not
relied upon for this execution-binding correction. No novelty, scientific
soundness, genus-floor or transfer judgment is made.

## Invariants and gates

The specification, hypothesis, source files, fixtures, scientific trial list,
run IDs, argv, seeds, controls, counts, limits, metrics and decision rules are
unchanged. `verification.json` records direct byte/hash comparisons. The only
existing handoff/queue edit is the exact old-to-new trial-plan digest.
The goal retains its active status and original stale next action verbatim in
`next_action_before_source_binding_20261026`, then records the correction route.

The newest-experiments selector alone did not catch the original source drift;
full source/input hash verification remains necessary. The preapproval probe
does not accept an already-approved canonical specification, so this packet
does not claim it returned approvable true. It retains existing approval and
uses the ordinary plan, source, queue and publication gates.

Root must publish the task envelope, claim and complete the verification/adoption
task, then claim the archive task and verify its receipt against Git. No
completed archive, commit SHA or successful scientific run is asserted here.
Use content_at_commit to bind the actual correction commit without asserting
the already-prepared package was dispatched earlier. The new correction lane
does not close or take ownership of the original execution lane.

The main validator baseline is tracked by
problems/full-ledger-validation-errors.md: 100 unsuppressed errors in 29 paths,
zero PEXT. Preserve that exact baseline. Canonical research graphs were checked
for scope: this is a source-binding edge in an execution packet, with no change
to a scientific finding or graph edge; no research diagram update is warranted.

## Completion and remaining work

This packet is prepared and unarchived. Publication, exact archive verification
and future native runner admission remain gates. The later execution entry is
`/run EXP-PEXT-212d5c` under TASK-20261024-672126, and is not invoked here. Independent
scientific review and the blind recount remain downstream obligations.
