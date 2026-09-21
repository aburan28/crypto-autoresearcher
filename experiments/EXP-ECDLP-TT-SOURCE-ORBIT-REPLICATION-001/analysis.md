# Analysis: Source Pair-Sum Orbit-Multiplicity Selector

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND` for the fixed
orbit-multiplicity schedule.

## Result

The selector ranks suffix pairs by descending multiplicity of the affine
x-coordinate among source-only pair sums `R_j + R_k`, then by diagonal status,
index distance, coordinates, and original index. It is target-independent and
uses no relation or held-out support information.

Neither fresh curve has an accepted strict sub-full budget. Full replay is
exact, every full-budget witness is valid, and all matched rho targets are
directly certified. The independent verifier regenerates both fixtures and
passes every selector, source, support, witness, curve, and rho check.

The partial signals are informative but fail the promotion gate:

- On p15667, `random_x` has exact support at 64/100 but misses held-out
  coverage; `rational_union` has exact support at 64/100 but remains rank
  deficient.
- On p15683, `source_prf_x` has exact support and held-out coverage at 64/100
  but remains rank deficient; `rational_union` has exact support and held-out
  coverage at 32/64 but remains rank deficient.

The generator used 201.692 seconds wall time, 189.590 CPU seconds, and
1,487,896,576 bytes peak RSS. Matched rho used 211,901 group operations. The
source-only pair-sum construction costs 100 group operations, 90 additions,
10 doublings, 100 inversions, and 310 field multiplications per family/curve.

## Interpretation

This closes only the tested orbit-multiplicity ordering as a strict fresh-curve
relation locator. It does not rule out other compositional invariants,
non-enumerative source contraction, target-parametric transposed operators, or
fixed-curve preprocessing tradeoffs. The combination of uniform sampling,
single-coordinate ordering, and orbit-multiplicity ordering now gives a useful
set of negative controls: partial support is easy to obtain, while held-out
coverage and quotient rank are the discriminating gates.

The next positive search should use a different mathematical object, such as a
source-derived recursive state operator or circuit-contracted row-space basis,
rather than another scalar ranking of the same suffix table.

