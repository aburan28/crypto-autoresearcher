# P-256 second-pass launch metadata needs prospective corrections

- **Status:** resolved
- **Kind:** implementation/contract gaps
- **Affected work:** F3/F4 frozen protocols and F2-F8 process recipes in the [second pass](../research/p256_factor_base_parallel_20261026/README.md)
- **Next action owner:** Coordinator prepares additive protocol versions; executor supplies the declared outer process guards
- **Last updated:** 2026-10-26

## Problem

Schema-valid frozen metadata does not by itself make the prepared launch
contracts executable: F3 lacks required source digests, F4 declares an
unimplemented application-checkpoint mechanism, and the literal recipes leave
the external process watchdog unspecified.

The original requirement is unchanged: execute the complete fixed panels with
their controls and retain every outcome, including partial attempts. These
configuration gaps must be corrected prospectively without editing historical
protocols or changing seeds, cases, analysis or observed data.

## Evidence and uncertainty

- **Observed:** The [source inspection](../research/p256_factor_base_parallel_20261026/environment/launch-compatibility-01/inspection.md)
  at `616878bcf` found `f3/protocol.json`'s `extensions.source_sha256` empty,
  while `f3/run.py` lines 402-405 refuse that state before the gate.
- **Observed:** F4 declares application checkpoints every 60 seconds and
  manifest-validated restore, but its runner requires fresh attempts and has
  no periodic checkpoint or restore interface. Its exporter records no row
  restoration. The mandatory S3 pre-launch backup is a separate mechanism.
- **Observed:** The direct F4/F5/F7 recipes supply no external deadline; the
  protocols declare a 120-second process guard. Existing F3/F6/F8 notes also
  require a 120-second outer watchdog alongside their internal timers.
- **Observed:** Original protocol/file/analysis hashes, selected scientific
  inputs and interpreter bytes match their pins. No actual admission or
  scientific execution was attempted. The inspection's separate mixed-time
  checkpoint-script field is corrected in its custody addendum.
- **Derived:** The unchanged F3 v1 guard would refuse a launch regardless of
  later S3 authentication. That is a static control-flow conclusion, not an
  attempted experiment or mathematical outcome.
- **Missing capability:** Correct prospective metadata and explicit outer
  commands. S3 authentication remains independently missing.
- **What is not established:** Arithmetic correctness, a successful gate or
  launch, elapsed runtime, checkpoint restoration, yield or performance.

## What would unblock it

- [x] Preserve original frozen bytes and publish F3 v2 with the exact five
  source digests, matching the original instrument commit, before any data.
- [x] Preserve F4 v1 and publish a before-data v2 declaring no in-row
  application restore, while retaining the separate mandatory S3 gate.
- [x] Supply concrete outer process commands with the declared resource
  guard and the actual per-track CLI/protocol/release paths.
- [x] Validate/freeze the new records and verify that the scientific design,
  analysis and original source/input bytes are unchanged.

These conditions resolve these metadata/recipe gaps only. Actual execution
still needs [checkpoint authentication](p256-pass2-checkpoint-authentication-unconfigured.md),
a genuine successful gate and matching releases. F1 is separately incomplete.

## Next discriminating step

- **Action:** Check the exact allowed deltas for the two v2 drafts, validate
  and freeze their prospective final bytes, and bind the future command plan.
- **Inputs and controls:** Original frozen hashes, original committed source
  objects, exact five-file F3 map, and unchanged scientific fields.
- **Execution limits and stop condition:** Metadata/schema/source inspection
  only; no mathematical program, actual gate or release in this correction.
- **Outcomes and next actions:** Matching before-data corrections clear only
  the named configuration issues. Any unexpected source/design delta is
  refused and preserved for separate prospective treatment.
- **Recheck trigger:** Completed v2 drafts/freeze and command-plan receipts;
  later actual admission remains a distinct observation.

## Resolution and history

Resolved for the named metadata/recipe gaps on 2026-10-26.
[Freeze receipt](../research/p256_factor_base_parallel_20261026/environment/protocol-amendment-freeze-01/result.json)
binds both unchanged-design v2 bodies to prospective draft snapshot
`396d09b942d9fc431974d788bb5276f7929f4a27`.
The [outer-command plan](../research/p256_factor_base_parallel_20261026/environment/phase-b-commands-01.json)
supplies exact CLI/release paths and TERM at119 seconds followed by KILL one
second later, implementing the existing120-second maximum process guard.
These command recipes have not run on a scientific process. S3 authentication,
a genuine gate, task releases and actual execution remain separate unresolved
requirements. No arithmetic correctness or official research-state claim is made.
