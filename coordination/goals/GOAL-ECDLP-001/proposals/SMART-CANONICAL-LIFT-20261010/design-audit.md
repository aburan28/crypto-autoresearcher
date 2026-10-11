# Smart attack versus canonical-lift design audit

## Audit basis

- Idea: `IDEA-20261009-d94525`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- This is a bounded implementation/control comparison for anomalous curves;
  it is not a general ECDLP claim.

## Required mathematical identity and lift contract

The experiment must first certify the anomalous condition `#E(F_p) = p`, the
ordinary reduction, the actual endomorphism order, and the exact discriminant
used for CM. For trace one, `t^2 - 4p = 1 - 4p`, but that is the Frobenius
discriminant, not automatically the discriminant of `End(E)`; the conductor
must be computed and certified. A Hilbert class polynomial for an assumed
order is not a canonical-lift certificate until its reduction has the chosen
j-invariant as a simple root and the order, twist, and isomorphism class are
matched.

The canonical arm is underspecified by “the Hensel-lifted `H_D` root”. The
record must select the root congruent to the exact input j-invariant, certify
separability and precision, and lift the full curve model and the sampled
points—not just its j-coordinate. Curves with the same j can differ by a
twist, and the point lifts must reduce to the exact original points. The
random arm must define the distribution of integral coefficient perturbations,
the precision, nonsingularity condition, point-lift rule, and independent
seed. All arms must use the same coordinate normalization and Smart statistic.

The mechanism also needs a precise definition of “success” and
“degenerates”. The attack must output a scalar candidate, verify it by the
original finite-field equation, and classify zero denominators, singular
reductions, insufficient p-adic precision, non-lifted points, and incorrect
candidates separately. A zero or constant p-adic logarithm is not by itself a
failure of scalar recovery unless the declared recovery step proves that it
cannot yield a verified candidate. The canonical and random arms must use the
same algorithm and resource ceiling.

## Sampling and statistical gaps

The proposal supplies neither the five primes nor the CM curves. It must
publish an exact prime table, anomalous curve equations, point samples,
endomorphism orders, class numbers, and `deg H_D` values. The claimed
`h(D) <= about 10^3` cutoff is an admission/resource condition, not an
assumption; rows above it are excluded before sampling or recorded as
unavailable, never silently replaced.

The rate `1 - 2/p` is not a useful binomial effect threshold for a sample of
one thousand at cryptographic-size p: it is a per-instance bound whose
allowed failure count is below one, while a finite sample cannot establish
that universal rate. The record should report exact verified successes and
failure categories with a predeclared confidence procedure, or state that
the theorem predicts zero failures in the tested rows and treat the run as a
regression check. The statement “exactly 0” on the canonical arm likewise
needs a defined number of independent point/lift instances and a fixed
precision ceiling; one deterministic run per curve is not a rate estimate.

The non-anomalous control requires an exact alternative: same field-size
bins, an explicitly certified `#E(F_p) != p`, matched lift sampling, and a
predeclared expected outcome. It cannot be summarized as “the attack must
fail on both lifts” without distinguishing the anomalous condition used by
the attack from an implementation failure. Positive controls on anomalous
random lifts are required before a canonical-lift non-success is
interpretable.

## Relation to ECDLP claims

The Smart procedure is a special attack on certified anomalous curves. A
comparison of lift choices does not extend to ordinary curves and does not
change the generic prime-field ECDLP boundary. Any claim that canonicity is
“anti-correlated with usefulness” must be restricted to the declared attack,
curve family, lift distribution, precision, and recovery rule. No asymptotic
or deployed-key conclusion follows from this control.

## Required runnable contract

Before approval, freeze:

- exact primes, anomalous and non-anomalous curve equations, group-order and
  endomorphism-order certificates;
- the Hilbert class polynomial source/hash, order discriminant, root and
  twist selection, full canonical curve/point lift, and precision;
- the random-lift coefficient distribution, nonsingularity test, point-lift
  procedure, seeds, and matched non-anomalous controls;
- the exact Smart implementation, p-adic precision schedule, recovery
  equation, verification equation, resource ceiling, and failure taxonomy;
- raw candidates and verification results, success counts, `deg H_D`, costs,
  stdout/stderr, and all invalid/infrastructure rows; and
- source/dependency hashes, exact commands, and archive handoff.

Rows with an uncertified anomalous order, ambiguous CM root, invalid point
lift, insufficient precision, or unavailable class polynomial are `invalid`
or `failed_infrastructure`, not evidence about canonicality. A recovery
candidate that is not checked in `E(F_p)` is not a success.

## Interpretation and disposition

A valid run could establish only whether the specified Smart implementation
recovers verified scalars on the named random and canonical lifts of the
named anomalous curves, together with its resource and failure breakdown. It
cannot show that all random lifts succeed, that all canonical lifts fail, or
that canonicity controls ECDLP difficulty outside the tested scope.

Disposition: **keep proposed as a narrowly scoped regression control; do not
approve until the CM order, full lift, success criterion, rate design, and
positive/negative controls are repaired.** If exact canonical-lift failure is
the only goal, remove the unsupported `1 - 2/p` universal-rate language and
make the random arm a separately certified positive control.

Next action: publish the exact curve/lift table and recovery contract, then
rerun readiness. Preserve every failed or censored row without converting it
into mathematical evidence.
