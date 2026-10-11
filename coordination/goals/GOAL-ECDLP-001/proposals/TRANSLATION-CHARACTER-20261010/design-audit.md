# Translated-character correlation design audit

## Audit basis

- Idea: `IDEA-20261007-c79278`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-13bf67`, and the quadratic-
  character controls.

## Scientific boundary

This is a finite correlation census for one translation on one small curve.
The proposal correctly keeps the sum separate from a Weil-level theorem and
from an ECDLP method. The main issue is that independent fair signings do not
preserve the deterministic translation graph or the asymmetric exclusions in
`S`; the null and its 20-of-200 threshold need a precise statistical contract.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 61, the exact
   discriminant convention/residue, all affine points, and the point-at-
   infinity handling. Verify the selected translation point `T` independently
   and record the tie rule for equal x-coordinates.
2. Define the translation domain exactly. State the complete group-law
   implementation, the cases where `P+T=O`, the exclusions `x(P)=0` and
   `x(P+T)=0`, and the final ordered list `S`. The set need not be invariant
   under translation, so both source and target exclusions must be reported.
3. Freeze character semantics. Define Euler-criterion evaluation for zero,
   residue, and nonresidue, use canonical representatives, and independently
   verify the character table. Emit per-point `(P,P+T,chi(x(P)),chi(x(P+T)))`
   records and the signed product sum.
4. Improve the null model. Independent signs test a generic random sum but do
   not match correlations induced by shared points, translation cycles, or the
   same exclusion mask. Add a permutation/sign null preserving `S` and its
   dependency graph, and state whether the primary null is independent,
   paired, or both.
5. Make the finite decision rule reproducible. Fix the PRNG, seed, signing
   count, replacement rule, and exact threshold comparison. Derive the null
   tail probability for `|sum| >= |S|/4` or report a confidence interval; a
   sample rule of 20 out of 200 is otherwise an uncalibrated instrument gate.
6. Preserve the interpretation boundary. A ratio below 1/4 is one finite
   translation statistic and does not prove a Weil bound, mixing, or an ECDLP
   advantage. Any broader character-sum claim requires a new curve/prime
   panel and a preregistered multiple-comparison plan.
7. Bind execution artifacts. Freeze the exact command, source/input hashes,
   raw point/translation list, character table, null signings, independent
   evaluator, and archive handoff before approval.

## Readiness and disposition

The proposal is close to a finite correlation control, but the null must be
made structurally explicit and the finite tail threshold calibrated. The
translation point and asymmetric domain exclusions also need replayable
certificates.

Disposition: **retain proposed as a candidate translated-character control;
do not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with matched nulls, exact tail accounting, and artifacts,
then recheck capacity and selector admission.
