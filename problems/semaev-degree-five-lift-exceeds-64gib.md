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
