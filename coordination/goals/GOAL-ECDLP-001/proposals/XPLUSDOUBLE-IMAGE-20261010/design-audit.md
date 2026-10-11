# `x(P)+x(2P)` image-size design audit

## Audit basis

- Idea: `IDEA-20261006-622d5a`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-IC-5a43e5`, and `KR-RHO-13bf67`.

## Scientific boundary

This is a well-scoped finite image-size census. The proposal explicitly
separates the image defect from a collision-search algorithm and includes two
independent doubling paths plus a label control. Its remaining risk is control
semantics: eligible points can have duplicate x-values under negation, and the
shuffle description does not yet define exactly which labels and doubled
indices are being randomized.

## Load-bearing repairs

1. Fix the eligible point list before any image calculation. Record the full
   affine points with `y != 0`, the excluded infinity/2-torsion points, and
   the deterministic enumeration order. Count points, not x-orbits, exactly
   as stated; retain duplicate x-values from negation.
2. Define the shuffled-label null algebraically. Specify whether the shuffle
   replaces `x(P)` while retaining `x(2P)` from the original point, permutes
   complete point labels, or assigns an independent random field element to
   each index. Preserve the same x-duplication profile if the null is meant to
   model labels, and report the null image size without substituting it for
   the true `I`.
3. Certify the curve and arithmetic. Record primality of 131, the exact
   discriminant convention/residue, point membership, both doubling formulas,
   the infinity case, and equality of the complete doubled points. Verify each
   inserted sum is a field element and emit the image set for independent
   replay.
4. Keep the finite claim literal. `I <= M-1` is an existential statement for
   one fixed curve and eligibility rule. A collision count does not imply a
   factor base, relation yield, or inversion method; any broader image-size
   claim needs a preregistered curve/prime panel and uncertainty treatment.
5. Record the birthday comparison separately. If the random-label model is
   used to motivate the prediction, state its exact replacement distribution
   and compare the observed defect with an occupancy interval. The heuristic
   does not replace the exact finite result or justify transfer to larger p.
6. Complete the execution contract before approval. Bind the exact command,
   source/input hashes, raw point and image-set artifacts, independent
   evaluator, and archive handoff. A deterministic small scan still requires
   those receipts under the research contract.

## Readiness and disposition

The proposal is close to a ready finite arithmetic control. The key repair is
to make the shuffled-label comparison mathematically unambiguous while
preserving the point-level negation multiplicity. No ECDLP conclusion follows
from either image size.

Disposition: **retain proposed as a candidate finite image-size control; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with the exact null, independent evaluator, and artifact
paths, then recheck capacity and selector admission.
