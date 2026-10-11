# Least-bit doubling agreement design audit

## Audit basis

- Idea: `IDEA-20261006-64c06d`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-cd86f5`, and the coordinate-
  predicate controls.

## Scientific boundary

This is a deterministic finite census of one bit under doubling. The proposal
already excludes walk-spectrum and discrete-log interpretations. Its useful
deliverable is the exact pair `(C,M)` plus independent formula checks; the
independence heuristic is not a theorem and the single curve cannot support a
general bias statement.

## Load-bearing repairs

1. Fix the point population. Record every affine point, the `y=0` exclusions,
   infinity, and the exact enumeration order. Count points rather than
   negation orbits as specified, and ensure each point enters once even though
   its negative has the same x-coordinate.
2. Certify the model. Record primality of 1009, the exact discriminant
   convention/residue, selected point membership, and the complete result of
   the point count. Treat `M=0` and any singular/bad cell as unmeasured.
3. Define both doubling paths. Publish the duplication formula and the
   independent `P+P` implementation, denominator/infinity behavior, and
   complete-point equality. A matching x-coordinate alone is weaker than
   matching y and infinity status.
4. Freeze bit encoding and controls. Use the canonical `[0,p-1]` integer
   representative, define the bit of zero, and verify the simultaneous
   bit-flip control does not change the agreement count. Report signed-residue
   conversions only as a separate implementation check.
5. Keep the finite inference literal. The output `2C-M` is one exact defect
   at one curve and prime. A nonzero defect does not show a transition bias at
   cryptographic size, alter a rho walk constant, or produce an inversion.
   Any broader claim needs independent curves/primes and a predeclared
   sampling/uncertainty plan.
6. Complete the execution/archive binding. Before approval, freeze the exact
   command, source/input hashes, raw point and per-point bit records, formula
   checker, and archive handoff. A small exhaustive scan still requires
   replayable artifacts.

## Readiness and disposition

The proposal is nearly complete as a finite arithmetic control. Its remaining
requirements are exact point-level certificates, independent complete-point
doubling agreement, canonical bit semantics, and execution artifacts.

Disposition: **retain proposed as a candidate least-bit doubling control; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with the exact command and artifacts, then recheck capacity
and selector admission.
