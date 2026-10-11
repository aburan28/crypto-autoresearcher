# Quadratic-character doubling design audit

## Audit basis

- Idea: `IDEA-20261007-7541f8`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-13bf67`, and the tangent/
  character predicate controls.

## Scientific boundary

This is a finite disagreement census for two quadratic characters on one
curve, with an independent fair-sign control. It has a clear lower-bound
threshold and no claimed ECDLP consequence. The main readiness gap is the
random-control contract: the fair-sign draw needs a fixed seed, exact sample
size, and a replayable sign list, while the curve census needs explicit
zero/exception tallies.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 71, the exact
   discriminant convention/residue, every affine point, and the infinity and
   `y=0` exclusions. Verify the complete point list independently.
2. Define the eligible set before scoring. State strict zero tests for
   `x(P)` and `x(2P)`, the handling of `[2]P=O`, and the exact cardinality
   `|D|`. Emit counts for each excluded category; do not let the character
   function evaluate zero in the primary disagreement metric.
3. Freeze character arithmetic. Define Euler-criterion evaluation, canonical
   field representatives, and an independent table/exponentiation check for
   residues and nonresidues. Verify both doubling implementations on complete
   points before using their x-coordinates.
4. Make the fair-sign control reproducible. Specify the PRNG, seed, whether
   signs are sampled independently with replacement or as a balanced fixed
   list, and the number of control draws. Report its disagreement count and
   interval; the control validates the character implementation, not the
   curve’s doubling distribution.
5. Preserve the finite threshold. The claim is `fraction >= 1/3` for this
   curve and eligible set, with values below 1/3 falsifying that cell. A
   passing count is not a mixing theorem, a walk constant, or an ECDLP
   algorithm; broader claims require a preregistered curve/prime panel.
6. Bind execution artifacts. Freeze the exact command, source/input hashes,
   per-point character pairs, exclusion tallies, fair-sign list, independent
   evaluator, and archive handoff before approval.

## Readiness and disposition

The proposal is close to a ready finite control. Its remaining requirements
are a deterministic fair-sign control, exact eligible-set/exclusion records,
and independent doubling/character verification.

Disposition: **retain proposed as a candidate quadratic-character doubling
control; do not approve or dispatch the idea record itself.** Convert it to a
complete ready experiment with replayable control artifacts, then recheck
capacity and selector admission.
