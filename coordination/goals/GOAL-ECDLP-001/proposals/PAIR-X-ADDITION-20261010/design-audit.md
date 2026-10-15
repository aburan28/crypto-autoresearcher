# Pair x-addition equality design audit

## Audit basis

- Idea: `IDEA-20261007-fad964`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-fbd582`, and the finite
  coordinate-image controls.

## Scientific boundary

This is a finite ordered-pair census for one curve. The equality is precisely
defined and the proposal correctly excludes tangent pairs and makes no ECDLP
claim. The remaining obligations are exact pair-domain accounting, an
independent addition implementation, and a reproducible random-field null;
the `8p` ceiling is a pre-registered finite prediction rather than a theorem.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 67, the exact discriminant
   convention/residue, every affine point, and the infinity/2-torsion cases.
   Verify the point list independently before constructing ordered pairs.
2. Define `U` algorithmically. State whether the pair order is `(P,Q)`, how
   equal x-coordinates are excluded, how `Q=-P` and `P+Q=O` are handled, and
   whether the affine-sum condition is redundant or separately checked. Emit
   `|U|` and the excluded-pair categories.
3. Verify the group-law equality. Compute `P+Q` with the chord formula and an
   independent complete addition implementation, compare complete points,
   and evaluate both sides of `x(P+Q)=x(P)+x(Q)` in canonical field form.
   Record the equality witnesses rather than only the counter.
4. Freeze the random control. Specify the PRNG, seed, independent random
   field draw per ordered pair, replacement rule, and raw control outputs.
   Compare its count with the exact binomial interval around `|U|/67`; a
   factor-of-two gate should be justified against that interval and applied
   before interpreting the curve count.
5. Preserve the finite decision rule. The claim is `count <= 8*67` for this
   fixed curve and ordered-pair set. A count above the threshold falsifies
   only this cell; a passing count is not a smoothness, factor-base, or
   relation-collection result.
6. Complete execution/archive binding. Freeze the exact command, source/input
   hashes, raw points/pairs or a replayable pair digest, independent evaluator,
   and archive handoff before approval. The pair scan is small but its
   quadratic domain still needs an auditable receipt.

## Readiness and disposition

The proposal is close to a ready finite control. Its remaining requirements
are exact ordered-pair/exclusion accounting, independent complete addition,
and calibrated random-control artifacts.

Disposition: **retain proposed as a candidate pair x-addition control; do not
approve or dispatch the idea record itself.** Convert it to a complete ready
experiment with the exact null and pair artifacts, then recheck capacity and
selector admission.
