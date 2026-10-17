# Affine Weil-descent fixture and solver admission

- **Status:** `investigating`
- **Kind:** implementation admission gap; historical serializer mismatch resolved in a prospective branch
- **Affected work:** [EXP-ICPERF-42ef30 AP-2 and Stage 2](../experiments/EXP-ICPERF-42ef30/specification.yaml), [affine generator](../experiments/EXP-ICPERF-42ef30/code/affine_weil_descent.py)
- **Next action owner:** EXP-ICPERF-42ef30 implementation lane
- **Last updated:** 2026-10-16

## Problem

The affine-slice S4 Weil-descent generator now reproduces the 60 shipped
Magma and WDSat files byte-for-byte in a prospective branch, but
EXP-ICPERF-42ef30 Stage 2 still needs independent admission of arbitrary
affine slices and a WDSat build whose MAX_ID matches the emitted ANF.
This is the specified Koblitz binary-field instrument gate for n=15, 17, 19
and l=5, 6; it establishes nothing about prime-field, ordinary-binary, or
50–63-bit costs.

## Evidence and uncertainty

- **Observed:** The original [fixture audit](../experiments/EXP-ICPERF-42ef30/tests/fixture_audit_20261016.json) preserves the initial 0/60 byte matches in both formats and 60/60 Boolean-equivalent systems. The [successor audit](../experiments/EXP-ICPERF-42ef30/tests/fixture_audit_20261016_v2.json) records 60/60 exact Magma and 60/60 exact ANF byte matches, source and fixture SHA-256 digests, Sage 10.10.rc0, and the command. The [planted-point test](../experiments/EXP-ICPERF-42ef30/tests/test_affine_weil_descent.py) passes on one n=7 affine slice with a genuinely nonmonomial basis [3,5,33], offset 2, changed-target control and dependent-basis rejection. The [parser-only receipt](../experiments/EXP-ICPERF-42ef30/tests/parser_probe_20261016.json) records a build with ANF-derived MAX_ID=195 and the vendored parser consuming the n=7 instance (29 unary variables, 166 distinct nonlinear monomials, 27 equations); search was not invoked. These are implementation checks, not solver or relation-yield experiments.
- **Derived or proved:** The frozen producer's [`semaev_out.c`](../inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent/semaev_out.c) and [`weil_out.c`](../inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent/weil_out.c) enumerate terms by degree, group, then coordinate; applying this ordering discharges the literal 60-fixture byte condition in the tested branch. No general theorem about arbitrary affine correctness follows from the bounded checks.
- **Suspected explanation:** The initial mismatch came from using Sage's polynomial term order and different line formatting instead of the shipped C producer's serializer; the exact-byte successor audit supports this explanation for all shipped fixtures.
- **Missing capability:** Independent admission of the selected n=15,17,19 designed slices and their per-cell Stage-2 WDSat parser/MAX_ID builds.
- **What this evidence does not establish:** It does not certify full generator correctness on every affine slice, parser/build admission for the selected Stage-2 cells, solver behavior, a factor-base advantage, or an end-to-end IC improvement.

## What would unblock it

- [x] Produce all 60 shipped `.in` and `.anf` files byte-for-byte from declared monomial bases, zero offset, and recovered target coordinates, with the generator source, Sage/runtime version, exact inputs, command, and hashes retained in the successor fixture audit.
- [ ] Independently check the selected full-rank n=15,17,19 designed slices, with nonzero-offset controls, against planted curve arithmetic and changed targets; verify each emitted ANF's WDSat parser and exact MAX_ID build under the frozen Stage-2 rule. The n=7 check is a partial control.

These checks would discharge this implementation precondition for Stage 2.
Stage 2's fixed solver controls, costs, relation yield, and end-to-end pipeline
comparison would still need execution and review.

## Next discriminating step

- **Action or proof obligation:** Select the Stage-2 designed slices through the frozen Stage-1 protocol, then independently validate each n=15,17,19 selected slice and run the parser-only build with exact ANF-derived bounds before scientific solver calls.
- **Inputs and controls:** The 60 immutable n15/n17/n19 shipped Magma/ANF pairs; compare both raw bytes and canonical Boolean equations. Keep the n=7 planted nonmonomial slice, target mutation, dependent-basis rejection, and parser receipt as controls for the selected Stage-2 slices.
- **Execution limits and stop condition:** Regenerate exactly the 60 fixtures; stop on any byte mismatch, malformed ANF, or planted-control failure. This is a bounded implementation check, not a scientific run or campaign spending cap.
- **Outcomes and next actions:** Passing independent affine and parser/build checks permits AP-2 and Stage-2 admission review. A planted or parser disagreement triggers implementation debugging. Runtime or parser failure is an infrastructure/implementation outcome and does not count against the factor-base hypothesis.
- **Recheck trigger:** Independent affine validation and exact WDSat build/parser evidence on the prospective generator.

## Resolution and history

Unresolved. The 2026-10-16 first audit failed literal bytes; the successor
audit records exact bytes for every shipped fixture. The frozen AP-2 condition
is unchanged, and downstream parser/build admission and scientific tests are
still pending.
