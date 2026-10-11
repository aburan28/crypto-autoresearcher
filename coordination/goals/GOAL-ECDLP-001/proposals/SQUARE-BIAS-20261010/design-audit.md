# Square-bias design audit

## Audit basis

- Idea: `IDEA-20261006-30b5f6`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Relevant boundary records: `KR-RHO-13bf67` and `KN-FIND-ffe1df`.

## What the proposal actually tests

This is a finite character-bit measurement on one explicitly selected small
prime, one curve, one lexicographically selected point `Q`, and one eligible
set `S`. Its observable is the nonzero-square indicator of

`x(P+Q) x(P-Q) - x(P) x(Q)`.

It does not construct a factor base, a relation system, a collision search,
or a sum-compatible bucket index. A passing frequency gap would therefore be
an algebraic-statistical observation only; it would not imply a discrete-log
speedup or alter the generic square-root baseline.

## Load-bearing validity checks

The proposed shuffle null is not automatically exchangeable. Permuting
x-coordinates while retaining the original point-addition graph can break the
algebraic relations among `P`, `Q`, `P+Q`, and `P-Q`, while preserving some
incidental multiplicities. The record must define exactly which x labels are
permuted, which four-term rows are rebuilt, whether repeated coordinates are
allowed, and why the resulting statistic is the intended null. A second null
that redraws independent eligible points under the same curve and selection
rule would help distinguish a graph-breaking permutation artifact from a
genuine character effect.

The primary calculation must use exact field arithmetic and the Legendre
criterion, with zero excluded from the nonzero-square count. Every scored row
must retain on-curve checks for all four points and affine-denominator checks
for both translations. The selected prime, `Q`, `S`, seed derivation, shuffle
algorithm, rank convention, and tie rule must be frozen before scoring.

The expression should be symbolically simplified or independently expanded
from the chord-and-tangent formulas before interpreting a deviation. A hidden
identity could force the expression to be a square, a nonsquare, or zero on a
large subset. Such an identity would explain the observation; it would not by
itself make the bit useful in a walk. Two independent implementations and a
second frozen public point are appropriate controls, but the side point must
not be selected after seeing the primary result.

## Statistics and scope

The 300 shuffles define a finite empirical cutoff, not a universal 95 percent
probability statement. The contract must state the exact order statistic,
whether the observed arrangement is included in the null population, and how
ties are handled. If any secondary point, alternate expression, prime, or
curve is inspected, the primary claim must remain separated from that
exploration; otherwise the percentile becomes a hidden multiple-comparison
threshold.

The first eligible prime rule is reproducible but data-dependent in the sense
that the curve is scanned until a size condition is met. That is acceptable
only if the scan range, eligibility predicate, and stopping rule are immutable
and no later prime is substituted after inspecting the outcome. An empty
eligible set or empty `S` is a failed premise/infrastructure outcome, not a
negative character-bias result.

## Claim ceiling and disposition

A completed measurement could establish only the exact square-bit frequency
and its relationship to the declared finite null on the selected curve and
prime. It cannot establish persistence at larger primes, collision-time
improvement, a sum-compatible filter, or a change to the generic ECDLP
exponent. A null result closes only this expression, selection rule, and
finite scope.

Disposition: **keep proposed as a conditional finite measurement; do not
approve it as an attack direction as filed.** Before a runnable contract is
considered, repair the null model, perform the symbolic-identity check, freeze
the exact permutation and empirical-rank semantics, and bind two independent
implementations. If those checks are satisfied, a small control run could be
admitted under the ordinary readiness gate; any result remains claim-tier
finite measurement.
