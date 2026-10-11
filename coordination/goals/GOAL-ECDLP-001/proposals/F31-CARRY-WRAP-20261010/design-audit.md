# F31 carry-wrap design audit

## Audit basis

- Idea: `IDEA-20261006-dcc7f7`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.

## Scientific boundary

The proposal measures whether an integer carry in the least-nonnegative
representatives of two x-coordinates coincides with a lower x-coordinate of
their elliptic-curve sum on one selected curve over `F_31`. This is a finite
coordinate correlation. It does not define a scalar character, a factor base,
a relation search, or a new rho step, and it has no claimed exponent change.

The carry bit is not a sum-compatible bucket index. Any observed agreement is
therefore a descriptive property of the chosen coordinate cut and point
sample unless a separate, scalar-relevant construction is supplied.

## Selection and exact-count requirements

The scan over `(A,B)` must be completed in the declared lexicographic order
before the selected curve or the 24 pairs are inspected. Record every
rejected model, its discriminant status, trace, point count, and largest-prime
factor reason. The subgroup generator must have an independently verified
order `n`; a factor of the group order alone is not an order certificate.

The 24 accepted pairs must be retained with their original derivation,
rejections, retry outcomes, scalar values, point coordinates, sum, carry bit,
wrap bit, and on-curve certificate. The one-redraw rule can yield an
incomplete sample and must not be silently converted into 24 observations.
The identity exclusion and the `P+Q=O` exclusion must be applied before
scoring, with those cases reported separately.

The negation control tests only that x is sign-invariant; it does not validate
the independence of the two bits. The shuffle control must state whether it
is intended as a null for bit independence or merely a permutation diagnostic:
shuffling carry bits against fixed wrap bits breaks their point-level
dependence and is not automatically an exchangeable distribution for the
original pair-generation process.

## Statistics and interpretation

The binomial `p=1/4` model is not established by the curve or subgroup
definition. The marginal probabilities of carry and wrap can differ from
one quarter, and the 24 pairs are generated from a finite group with possible
repeated or correlated points. The exact binomial tail may be reported as a
reference calculation only. The primary finite comparison should be the
predeclared shuffle distribution, with its seed, algorithm, percentile,
ties, and number of valid shuffles frozen before scoring.

A result at `N >= 11` or below it is meaningful only for the selected curve,
subgroup, scalar-draw rule, coordinate convention, retry policy, and 24-pair
sample. It cannot be generalized to larger primes or interpreted as an
ECDLP distinguisher. A failed premise, invalid control, or incomplete sample
is an invalid/inconclusive measurement rather than negative mathematical
evidence about coordinate statistics in general.

## Disposition and next action

Disposition: **keep proposed as a conditional finite measurement; do not
approve it as an attack experiment as filed.** Repair the pair receipt,
subgroup/order certificates, and null-model definition. If retained, execute
it only as a control attached to a broader representation study, with the
claim ceiling limited to the exact F31 census. Otherwise leave it unexecuted
while the readiness selector has no admitted row and the resource guard is
unfavorable.
