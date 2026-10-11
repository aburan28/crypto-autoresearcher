# Digit-grading factor-base design audit

## Audit basis

- Idea: `IDEA-20261009-443717`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- The proposal is explicitly a finite negative control. Its expected negative
  result cannot establish an asymptotic prime-field ECDLP lower bound.

## Contract defects that must be repaired before approval

The proposed parameter grid is not executable as written. The construction
requires `n = d*k`, but most pairs in `n in {31, 61, 89, 127}` and
`d in {2, 3, 5}` do not have an integer `k`. The experiment must publish an
exact table of accepted `(n, d, k, c, p)` rows, with `p = 2^n - c`, a
primality certificate for each `p`, and the exact reason every omitted row is
omitted. It must not silently round `k`, change `n`, or choose a different
prime. The ring relation and reduction map then have a checkable obligation:
`(2^k)^d = 2^n = c (mod p)`.

The closure observable is also underspecified. `D` is described using an
integer ordering on `x(P)`, while the proposed sample is a subset of curve
points and the expected denominator is `p`. The record must define the
canonical representative of every field element, whether `D` contains both
points above an accepted x-coordinate, how the point at infinity is handled,
and the population size `N = #E(F_p)`. The primary ratio should be
`Pr[P+Q in D | P,Q in D] / (|D|/N)` only if the null model justifies that
normalization. A stronger control is an independently generated random point
subset of exactly `|D|` elements of the same group, with the same ordered-pair
sampling and explicit infinity accounting. Point sampling must be uniform; an
x-first sampler with a square-root bias is not an acceptable control.

The proposed `1.00 +/- 0.01` threshold is not tied to its sampling variance.
For sparse `D`, one million pairs may yield too few hits for a one-percent
relative interval. The experiment must freeze a confidence construction (or a
predeclared minimum expected-hit rule), report the raw numerator and
denominator, and use the same rule for the digit set and the random-subset
null. It must state in advance how a ratio of 2 or 3 standard errors is
interpreted; a post-hoc threshold is not a falsification criterion.

The second arm is not yet a mathematical experiment. “Lift `S_3` to the digit
ring” needs the exact polynomial, variable names for base digits and top-digit
variables, coefficient ring, quotient ideal, representative convention,
specialization map, Groebner monomial order, and factorization field. The
record must distinguish a genuine factorization or degree change from a
non-squarefree specialization, a zero polynomial, an invalid quotient
representation, and a factorization-oracle failure. It must retain the
unlifted polynomial, the lifted polynomial, the specialized polynomial, and
the exact factor/degree certificates. The phrase “zeroing the top-digit
variables” is not sufficient to define a reproducible map.

Finally, the closure arm and symbolic-lift arm have different null models and
failure modes. They should be separate experiment arms with separate
validity fields and outcome rules. A symbolic implementation failure must not
be counted as support for the closure prediction, and a closure deviation
must not be attributed to the lift without an independently valid symbolic
artifact.

## Required runnable contract

Before approval, the implementation record should bind:

- the exact accepted parameter table and primality certificates;
- a full curve equation, nonsingularity check, group-order method, and point
  representation;
- the definition of the ordered point set `D`, including the infinity rule;
- an independent uniform point sampler and a second implementation or replay
  path for the group addition and membership predicate;
- a random-subset null with identical cardinality, pair ordering, seed
  derivation, and hit accounting;
- raw pair counts, `|D|`, `#E(F_p)`, null counts, confidence intervals, and
  sampler diagnostics;
- the complete digit-ring `S_3` construction and all specialization and
  factorization certificates; and
- exact commands, source and dependency hashes, seeds, stdout/stderr, raw
  machine-readable outputs, validity status, and the archive handoff.

The stopping rule must be expressed over the repaired accepted-row table,
not the currently invalid Cartesian product. Any row with a failed prime,
sampler, group-law, or symbolic certificate is `invalid` or
`failed_infrastructure`, not negative evidence.

## Interpretation and disposition

If the repaired finite control matches its nulls, the supported statement is
only that the tested digit predicate showed no detectable closure or symbolic
degree/factor anomaly on the named rows. A deviation closes only that exact
predicate, curve, parameter table, and implementation scope. Neither outcome
creates a factor base, a transfer, a private-scalar method, or an asymptotic
ECDLP claim. The existing adjacent factor-base knowledge row may motivate
the control, but it does not substitute for the missing point-domain and lift
specifications.

Disposition: **keep proposed; do not approve or dispatch until the parameter
table, group-size normalization, statistically valid null, and exact symbolic
lift contract are repaired.** The idea remains a low-priority finite control;
its current incompleteness is a protocol impediment, not a mathematical
negative result. If the proposer elects not to repair the symbolic arm, the
closure arm may be reconsidered as a separately scoped control rather than
silently dropping half of the proposal.

Next action: produce a write-once amendment or replacement experiment
specification containing the accepted `(n,d,k,c,p)` rows and both arm
contracts, then rerun the readiness check before any Coordinator approval.
