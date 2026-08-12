# EXP-SGCP-EMBED-002 development red-team v1

**Reviewer:** coordinator self-red-team, not independent review
**Disposition:** `REVISE`; canonical maximum runs remain zero

## Finding 1: objective and claimed density metric are misaligned

**Severity:** claim-blocking

Version 1 maximizes final support, then the number of selected degree-four
maxima, and only then minimizes constrained labels. Adding a compatible maximum
can leave support unchanged while increasing constrained density. Therefore the
reported support-per-constrained-label value is not a support-at-density
optimum, yet the positive gate compares that value across families.

**Required repair:** optimize support under explicit constrained-label budgets
or compute a certified Pareto frontier. Match candidate and null comparisons at
the same absolute budget on the same curve.

## Finding 2: energy label is mathematically wrong

**Severity:** measurement-blocking

The producer enumerates combinations with replacement and squares their output
multiplicities. This is formal-multiset collision energy, not ordered additive
energy. Calling it ordered silently changes source measure.

**Required repair:** preserve formal-multiset energy under its correct name and
derive ordered-tuple multiplicities with multinomial weights before squaring.

## Finding 3: capped optimum interval is not replayable from the artifact

**Severity:** evidence-blocking for nonzero gaps

The producer records only the final upper bound and number of live frontier
nodes. It does not emit each selected/available/support state and bound. A hash
or headline number alone cannot certify `OPT <= U` without rerunning producer
logic.

**Required repair:** serialize and charge the complete live frontier for capped
rows, or provide a separately checkable proof object. The verifier must
recompute every frontier bound.

## Finding 4: curve draw provenance omits duplicate draws

**Severity:** protocol repair

The sampler hashes every draw but silently skips a repeated `(p,a,b)` tuple.
The contract says every rejected draw is recorded. This leaves gaps in the draw
audit even though it does not change an accepted curve.

**Required repair:** record duplicate draws with reason `duplicate_candidate`
or define and log attempts separately from unique candidate evaluations.

## Finding 5: denominator naming is ambiguous

**Severity:** interpretation repair

`raw_final_support` is the final pair support of the predecessor-compatible
balanced A4 universe, which omits some formal paths such as identity D2. The
exact full 8F support is separately available in the expansion table. The
short name can be mistaken for full 8F.

**Required repair:** rename it `balanced_raw_final_support` and report full
`eight_fold_support` beside every retention ratio.

## What survived review

- Coordinate-only factor selection and EC arithmetic.
- Exact cardinality and negation-symmetry matching.
- Individual-closure and pair-conflict construction.
- Pairwise-conflict iff full-union-collision on the exhaustive frozen control.
- Exact-or-gap primary optimization machinery.
- Independent reconstruction of all 16 development primary optima.
- Direct final-edge exclusion and all formal embedding axioms.

## Next concrete action

Write version 2 with matched density budgets, corrected energy, complete draw
logs, and replayable gap frontiers; rerun only unit controls because the version
1 development row budget is already at 17/18.
