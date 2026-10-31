# Semaev degree-five lift exceeds the frozen 64 GiB allocation envelope

- **Status:** open
- **Kind:** resource limit; prospective implementation and placement requirements
- **Affected work:** [degree-six search](../analysis/semaev-degree-five-quotient-lift/README.md), [frozen continuation](../analysis/semaev-degree-five-quotient-lift/highmem-protocol.json)
- **Next action owner:** Codex, continuing the active degree-six search
- **Last updated:** 2026-10-30

## Problem

The degree-five lift for `fresh-n47-rand-00-D5-cascade01-highmem01` cannot run under the frozen instrument's 64 GiB envelope, leaving its prospective LFD >= 6 certificate unresolved.

The input is the fixed n=47, k=24 random subspace recorded in the high-memory plan. The requirement remains an independently accepted degree-five certificate whose codimension lower bound strictly exceeds the exact solution count; allocation admission alone would not satisfy it.

## Evidence and uncertainty

- **Observed:** The [verified terminal record](../analysis/semaev-degree-five-quotient-lift/runs/highmem-rand00-readback-001.json) binds 24 checked artifacts. The original independent checker accepts the D4 map with codimension lower bound 61196; exhaustive counting gives zero solutions. This establishes LFD >= 5. The following D5 producer exits 2 with `refused: lift allocation gate refused` under 68719476736 bytes. Frozen source revision: `0fe0e3ac2cca6b6b00d0f9de64e1ea06a6d88cf3`.
- **Derived or proved:** The refusal occurs at the native producer's conservative allocation-envelope check. The producer also rejects resource arguments above 64 GiB, so merely supplying a larger limit to this binary is not an executable continuation.
- **Suspected explanation:** No additional failure mechanism is inferred. The refusing instrument did not print its envelope. A subsequent SHA-bound calculation reproduces it: 152,976,386,232 bytes at chunk 60000; both border enumerations agree on 126,387 coordinates.
- **Missing capability:** An exact retained capacity calculation, followed by either a separately qualified producer using less memory or a separately qualified larger-limit instrument and actual suitable host placement.
- **What this evidence does not establish:** No measured peak RSS, proof of minimum memory, degree-five acceptance, LFD upper bound, or evidence that LFD >= 6 is impossible. The original capped attempt remains immutable. Other frozen inputs continue independently.

## What would unblock it

- [x] Derive the next-stage border-coordinate count and the exact instrument envelope from the accepted D4 certificate; bind its SHA256 `3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f`, source formula, and independent count control.
- [ ] Qualify and freeze a prospective instrument/resource placement that admits this seed, preserves all original checker conditions, and passes reference-byte and small Semaev cascade controls before a new attempt.
- [ ] Complete that distinct attempt and retain its certificate/checker/count evidence or its explicit terminal failure. Only original-checker acceptance with codimension strictly greater than zero establishes the sought LFD >= 6 bound on this input.

The first two conditions remove this execution obstruction, not the scientific uncertainty. A successful execution can still yield no stronger bound.

## Next discriminating step

- **Action:** Derive a capacity profile from the retained D4 map before selecting hardware or changing the instrument. Keep the active campaign's source, binary, plan and limits unchanged.
- **Inputs and controls:** This exact certificate and its accepted checker/count records; compare full-universe and extension-based border enumeration, as in the existing capacity profiler. A future instrument must retain the existing generic byte-equivalence and independently checked Semaev controls.
- **Execution limits and stop condition:** The current attempt is terminal and will not be relaunched. Any prospective profile or continuation requires its own frozen scope and recovery checkpoint; no additional worker may violate the current ownership or memory limits.
- **Outcomes:** If a qualified placement admits the envelope, run a new named attempt. If the envelope still does not fit, retain the calculation and investigate a smaller representation. A killed-constant quotient, codimension equality, resource refusal or infrastructure failure remains inconclusive for degree six.
- **Recheck trigger:** Completed capacity derivation or a qualified alternative producer and verified host placement.

## Resolution and history

2026-10-30: D4 independently accepted; D5 allocation refused. The sequential driver advanced to the next frozen input. Unresolved; this record preserves the original degree-six requirement and does not establish a new theorem.

2026-10-30: [Exact capacity calculation](../analysis/semaev-degree-five-quotient-lift/reports/native-envelope-001/report.md) completed under its new frozen protocol. Even chunk 1 needs 144,752,755,295 bytes under the source formula, exceeding this host total memory. Next action is prospective implementation/host qualification; no new LFD bound.

2026-10-30: A [separate bounded-export candidate](../analysis/semaev-degree-five-quotient-lift/BOUNDED-EXPORT-MEMORY.md) removes the obsolete full-export-map reservation while preserving matrix operations and 35% margin. Its software controls pass (byte equivalence, nine original-checker stages, resource argument boundaries), but frontier runtime/host qualification is not complete. Calculated envelope at chunk 60000 is 92,117,754,292 bytes. Current pool limit observed at 128 GiB; defer a prospective 112 GiB pod until both current panel jobs finish. No frontier retry launched, no degree-six conclusion.

2026-10-30: The qualified bounded-export worker was submitted under its frozen one-input protocol after both panel jobs ended. [Placement observation](../analysis/semaev-degree-five-quotient-lift/runs/bounded-lift-placement-001.json) records job UID f97c413c-9678-48c6-8cad-ac0dc0e320eb, pod UID 3578a37e-2df3-4d5d-9b5d-52427c21d2ee, Pending with no assigned node. Current-node affinity/taint mismatch is observed; the autoscaler root cause is unknown. Direct event inspection is unavailable because the launcher AssumeRole request was denied. Local deployment source declares a 256 GiB pool while the live service reports 128 GiB, so source configuration is not authoritative live evidence. Next discriminator: node assignment or current NodePool/NodeClaim/controller scheduling diagnostics through an authorized read path. Do not duplicate or silently alter the submitted job. Runtime admission and D5 acceptance remain outstanding; the separate local campaign continues.

## 2026-10-30: cloud placement and runtime controls verified

The existing 112 GiB job acquired node ip-10-84-87-128.us-east-2.compute.internal and started its container at 02:36:46 UTC. The immutable startup record in `../analysis/semaev-degree-five-quotient-lift/validation/bounded-lift-cloud-startup-001/verification.json` verifies the original request, manifest and driver hashes, finite cgroup limit and initial headroom. All three runtime control certificates matched expected bytes and were accepted by the original checker. The saved request is reserialized with sorted keys: its byte hash differs, while parsed contents and the environment-recorded original request hash match. This clears placement and startup qualification only. The retained frontier seed recheck and degree-five lift have no terminal result yet; LFD >= 6 remains unestablished.

## 2026-10-30: admitted cloud attempt ended without a frontier result

The job failed at 02:46:42 UTC with Kubernetes BackoffLimitExceeded. Its pod was unavailable on the follow-up observation and logs were empty. The underlying failure cause is unknown; there is no evidence identifying an OOM, Spot interruption, or algebraic failure. S3 retains the 29 startup artifacts but no frontier check4, produce5 or terminal result. See `../analysis/semaev-degree-five-quotient-lift/runs/bounded-lift-terminal-001.json`. Startup qualification remains valid within its recorded scope. The original one-attempt protocol is exhausted; a continuation must retain this failure and use a new frozen attempt identity. No LFD inference follows from this failure.

## 2026-10-30: interrupted local candidate retained for recheck

At 04:18 UTC the original local driver and producer PIDs were absent, no replacement checker/producer was found, and the owner lock was available. The n47 random02 D4 candidate survived, but its original checker transcript ends at variable40/48 and no result exists. The cause is unknown; host boot identity is unchanged. No acceptance is inferred. The candidate hash and original commands are pinned in `../analysis/semaev-degree-five-quotient-lift/runtime/highmem-rand02-check-recovery-001.json`. A separate4GiB checker recovery with fresh1GiB count was launched after checkpointing and records its result outside the original attempt.

Available local memory was58,919,362,560bytes, below the full64GiB campaign cap. Forty original continuation inputs remain unfinished; no population/sample count is changed. Exit criteria: accept the recovered D4 candidate with the original independent checker, preserve its certificate and fresh count, then reconcile sufficient memory and prepare a separately frozen continuation that reuses the candidate rather than rebuilding it. The original cloud random00 D5 continuation remains active on its distinct host.

## 2026-10-30: durable continuation interrupted by node shutdown

The second cloud job terminated at 05:07:22 UTC. Kubernetes explicitly records imminent node shutdown (DisruptionTarget, TerminationByKubelet), exit137, then BackoffLimitExceeded. This is infrastructure interruption; no OOM diagnosis is inferred. Terminal observation: `../analysis/semaev-degree-five-quotient-lift/runs/bounded-lift-terminal-002.json`. The retained object listing has58 files: completed original-checker D4 acceptance and exact count0 survive, with produce5.started.json at03:59:48 UTC, but no degree-five completion, checker result or certificate. Log retrieval returned a NotFound error. No LFD>=6 conclusion follows.

The previous independent local recovery completed and its D4 certificate is published; the forty-input continuation is frozen in highmem-recovery-protocol-001.json but awaits64GiB host admission. The cloud one-attempt continuation is now exhausted. Before another degree-five attempt, assess a placement protected from interruption or actual producer checkpoint/restart support; stage-start receipts alone cannot restore partial linear algebra. Preserve both failed cloud attempts, original input identity, qualified mathematical instrument and independent checker requirement. Exit criterion remains an accepted D5 certificate with codimension strictly above fresh solution count, not successful resubmission or runtime liveness.
