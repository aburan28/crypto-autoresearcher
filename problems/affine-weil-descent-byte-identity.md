# Affine Weil-descent output has not matched the frozen fixture bytes

- **Status:** `investigating`
- **Kind:** implementation gap; serializer provenance unknown
- **Affected work:** [EXP-ICPERF-42ef30 AP-2 and Stage 2](../experiments/EXP-ICPERF-42ef30/specification.yaml), [affine generator](../experiments/EXP-ICPERF-42ef30/code/affine_weil_descent.py)
- **Next action owner:** EXP-ICPERF-42ef30 implementation lane
- **Last updated:** 2026-10-16

## Problem

The affine-slice S4 Weil-descent generator is not yet admissible for
EXP-ICPERF-42ef30 Stage 2 because AP-2 requires byte-identical monomial-slice
output on all 60 shipped Magma and WDSat fixtures, and the new generator prints
the same Boolean equations in a different term order and layout. This is the
specified Koblitz binary-field instrument gate for n=15, 17, 19 and l=5, 6;
it establishes nothing about prime-field, ordinary-binary, or 50–63-bit costs.

## Evidence and uncertainty

- **Observed:** The [frozen fixture audit](../experiments/EXP-ICPERF-42ef30/tests/fixture_audit_20261016.json) records exact source and fixture SHA-256 digests, Sage 10.10.rc0, and the verification command. All 60 Magma systems and all 60 ANF systems agree after Boolean-term canonicalization, while zero of 60 match byte-for-byte in either format. The [independent planted-point test](../experiments/EXP-ICPERF-42ef30/tests/test_affine_weil_descent.py) passes on one n=7 nonmonomial affine slice with offset 2 and rejects a changed target and a dependent basis. This is implementation validation, not a solver or relation-yield experiment.
- **Derived or proved:** Byte identity is a literal AP-2 admission condition in the frozen protocol. Semantic equivalence alone cannot discharge it. No general theorem about the generator's correctness is established by the bounded checks.
- **Suspected explanation:** The shipped files use a different expression/monomial serialization order and line layout than this Sage 10.10.rc0 implementation. A source generator or exact serializer reconstruction would distinguish version drift from another provenance difference.
- **Missing capability:** A fixture-compatible serializer proven on all 60 shipped instances, followed by AP-2's independently checked arbitrary affine-slice correctness and Stage-2 WDSat MAX_ID/build admission.
- **What this evidence does not establish:** It does not certify full generator correctness on every affine slice, WDSat parser acceptance of newly constant-bearing X equations, solver behavior, a factor-base advantage, or an end-to-end IC improvement.

## What would unblock it

- [ ] Produce all 60 shipped `.in` and `.anf` files byte-for-byte from declared monomial bases, zero offset, and recovered target coordinates, with the generator source, Sage/runtime version, exact inputs, command, and hashes retained.
- [ ] Independently check arbitrary full-rank affine slices with nonzero offsets against planted curve arithmetic and a changed-target control; verify the emitted ANF's WDSat parser and MAX_ID admission as the protocol requires.

These checks would discharge this implementation precondition for Stage 2.
Stage 2's fixed solver controls, costs, relation yield, and end-to-end pipeline
comparison would still need execution and review.

## Next discriminating step

- **Action or proof obligation:** Trace how the shipped fixture generator orders algebraic terms and encodes constants, then implement a deterministic compatible serializer or recover the exact source/runtime that produced them.
- **Inputs and controls:** The 60 immutable n15/n17/n19 shipped Magma/ANF pairs; compare both raw bytes and canonical Boolean equations. Keep the n=7 planted nonmonomial slice, target mutation, and dependent-basis rejection as independent controls.
- **Execution limits and stop condition:** Regenerate exactly the 60 fixtures; stop on any byte mismatch, malformed ANF, or planted-control failure. This is a bounded implementation check, not a scientific run or campaign spending cap.
- **Outcomes and next actions:** Full byte identity plus independent checks permits AP-2 review. Continued semantic-only agreement keeps Stage 2 inadmissible and directs work to serialization provenance. A semantic disagreement triggers algebraic debugging. Runtime or parser failure is an infrastructure/implementation outcome.
- **Recheck trigger:** A new serializer, recovered upstream generator/runtime, or a corrected AP-2 contract backed by an authorized Coordinator decision.

## Resolution and history

Unresolved. The 2026-10-16 affine generator and fixture audit narrow the
failure to the required bytes under the tested scope; they do not revise the
frozen AP-2 condition.
