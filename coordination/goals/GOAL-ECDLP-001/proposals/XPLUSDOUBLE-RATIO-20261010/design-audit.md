# `x(P)+x(2P)` image-ratio design audit

## Audit basis

- Idea: `IDEA-20261007-71c7df`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the separate
  `F_131` x-plus-double image census.

## Scientific boundary

This is a finite image-ratio measurement on one curve. Since `x(P)=x(-P)`,
the domain contains two point representatives for each eligible x-coordinate,
while `t(P)=x(P)+x(2P)` factors through x. The meaningful threshold is
therefore a statement about the image of a rational function on the x-line,
not an independent point-level image. The proposal correctly makes no ECDLP
claim, but the point/orbit normalization should be explicit.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 43, the exact
   discriminant convention/residue, every affine point, the `y=0`/infinity
   exclusions, and the complete point count. Verify all points independently.
2. Report both populations. Give `|D|`, the number of distinct eligible
   x-coordinates, and the exact relationship between them. For each x,
   compute `t(x)` once and separately replay the point-level map to confirm
   `t(P)=t(-P)`; do not let duplicated signs distort the ratio.
3. Define the rational-function exceptional set. State denominator zeros,
   poles, points with `2P=O`, and the field representative used for the sum.
   Emit the distinct x-domain and image set so the ratio can be independently
   checked.
4. Verify the duplication implementation. Compute `x(2P)` from the formula
   and from `P+P`, compare complete points where defined, and reject any
   mismatch before scoring. The distinct-x control must use the same eligible
   domain and exact set semantics.
5. Keep the threshold finite. The ratio `|t(D)|/|D| >= 1/3` is a one-curve
   statement. The degree/fibre heuristic does not prove the threshold, and a
   result below it closes only this curve and chart. Any cross-curve claim
   needs a preregistered panel and uncertainty treatment.
6. Complete execution/archive binding. Freeze the exact command, source/input
   hashes, raw point/x/image artifacts, independent evaluator, and archive
   handoff. A small exhaustive image scan still requires replayable evidence.

## Readiness and disposition

The proposal is close to a ready finite control. Its principal repair is to
make the point-level versus x-orbit denominator explicit and to certify the
rational-function domain and image sets.

Disposition: **retain proposed as a candidate x-plus-double image-ratio
control; do not approve or dispatch the idea record itself.** Convert it to a
complete ready experiment with the exact population, independent evaluator,
and artifacts, then recheck capacity and selector admission.
