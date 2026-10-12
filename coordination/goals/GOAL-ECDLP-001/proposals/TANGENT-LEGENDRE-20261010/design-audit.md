# Tangent-slope Legendre census design audit

## Audit basis

- Idea: `IDEA-20261007-69bc58`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the finite
  character-predicate controls.

## Scientific boundary

This is a clear finite census of a tangent-slope character and a same-point
shift control on one small curve. Its strongest result is the exact tuple of
counts and zero bins. It does not establish a character-sum theorem, a
representation bias at larger primes, or an ECDLP improvement.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 29, the exact
   discriminant convention/residue, every affine point, the `y=0` exclusion,
   and the point-at-infinity handling. Verify the selected curve point list
   independently before scoring characters.
2. Define both zero bins. Report the number of points with tangent slope zero
   and the number with `x(P)+1=0`. Since both zeros remain in `n` but neither
   contributes to its positive count, the two centered deviations have
   different denominators/zero effects; omitting the second bin can make the
   control comparison misleading.
3. Freeze Legendre semantics. Define Euler-criterion evaluation for zero,
   residue, and nonresidue, use the canonical field representative, and
   independently check a table of squares in `F_29`. Verify the tangent
   formula and the inverse of `2y` with a second implementation.
4. Preserve the preregistered thresholds. Treat the `8` and `4` thresholds as
   this one-cell decision rule. Do not infer a distributional bias from the
   result or add curves/primes after observing the count; a broader study
   would need a new sampling and multiple-comparison contract.
5. Record exact artifacts. Emit the point list, slope values or hashes,
   Legendre bins, zero tallies, discriminant, and independent replay result.
   A low-cost exhaustive census still needs a deterministic command and raw
   result receipt before approval.
6. Keep the attack boundary explicit. A character count is not a walk,
   factor base, or target inversion. Any proposed use would need membership,
   precomputation, relation, and rho-comparison costs in a separate contract.

## Readiness and disposition

The proposal is close to a ready finite control. The main repair is reporting
the shift-control zero bin alongside the tangent zero bin and binding the
exact point/character artifacts.

Disposition: **retain proposed as a candidate tangent-slope control; do not
approve or dispatch the idea record itself.** Convert it to a complete ready
experiment with the exact command, zero-bin metrics, independent evaluator,
and archive handoff, then recheck capacity and selector admission.
