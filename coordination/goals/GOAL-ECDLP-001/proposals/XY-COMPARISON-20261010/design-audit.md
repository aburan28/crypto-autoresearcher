# Integer x-versus-y comparison design audit

## Audit basis

- Idea: `IDEA-20261007-6c7d84`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the integer-chart
  representation controls.

## Scientific boundary

This is a finite comparison of canonical integer representatives on one small
curve. It has an appropriate chart definition and a simple pair null, but the
proposal currently leaves an outcome gap: prediction acceptance is deviation
at most `0.1`, while falsification begins only above `0.25`. A result in the
interval between those thresholds must be declared inconclusive rather than
silently treated as either outcome.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 47, the exact
   discriminant convention/residue, the complete affine point list, and the
   infinity exclusion. Verify every listed point independently before
   evaluating the comparison.
2. Freeze representative semantics. Use `[0,46]` for both coordinates,
   define the comparison for equality, and keep balanced or signed residues
   out of the primary metric. Report the exact count, numerator, denominator,
   and any points with `x=y`.
3. Repair the decision partition. Predeclare three outcomes: support for the
   stated band when the deviation is at most `0.1`, falsification only when
   all stated instrument controls pass and the deviation exceeds `0.25`, and
   inconclusive in the interval `(0.1,0.25]`. Do not use the wider
   falsification threshold as if it proved the narrower prediction.
4. Make the null reproducible. Record the random seed, replacement rule,
   exact 200-pair sample, and expected null fraction
   `P[x>y]=(47*46/2)/47^2`. Use the null only as an instrument check; it is
   not a distributional model for elliptic-curve points.
5. Verify the negation control. State how `y=0` behaves under negation and
   require at least one actual comparison flip without changing the primary
   point list. A signed/balanced chart is a separate experiment.
6. Preserve the finite interpretation and archive binding. The result is one
   chart-dependent fraction, not a character, factor base, walk transition,
   or ECDLP cost. Before approval, bind the exact command, raw point list,
   null sample, independent evaluator, and archive handoff.

## Readiness and disposition

The proposal is close to a ready finite control. The outcome gap and exact
null/point artifacts must be repaired before an execution contract can be
approved.

Disposition: **retain proposed as a candidate integer-chart comparison; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with the three-way decision rule and replayable artifacts,
then recheck capacity and selector admission.
