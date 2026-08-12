# Experiment Contract: source-orbit quotient locator

## Hypothesis

For typed five-term relations on ordinary generated prime-field curves, quotienting suffix columns by the source-derived negation orbit of `R2+R3` can reduce the row-space and predicted-entry workload while preserving exact support after an explicitly charged lift to original suffix pairs.

## Null hypothesis

The quotient has no useful class reduction, its row-space is rank-deficient, its lift cost removes any predicted saving, or it fails exact support or held-out recovery on fresh curves.

## Parameters

- field/curve family: two fresh deterministic 14-bit prime-field curves from the committed typed-five fixture generator
- sizes: fresh fixture progression `A=11`, factor base `B=10`, suffix table `B^2=100`
- seeds: `271828`, `161803`
- factor base: `random_x`, `source_prf_x`, `x_interval`, `rational_union`
- relation shape: `A + R0 + R1 + R2 + R3 = Q`
- quotient class: source-only x-coordinate of `R2+R3`; one class contains every source pair with the same x-coordinate, including both negation signs and duplicate source representations
- baseline: materialized exact five-term support plus matched toy Pollard rho
- budgets: `4`, `8`, `full` quotient classes, with all class members lifted only after a predicted quotient zero

## Metrics

- group and field operations for suffix construction, quotient row-space construction, online quotient evaluation, original-predicate lift, reconstruction, witnesses, and relation linear algebra
- quotient class count, class-size distribution, retained advice, cache, and logical source bytes
- predicted quotient entries versus original full entries
- false quotient mismatches, exact support, held-out support, valid witnesses, and relation rank
- matched rho group operations
- wall time and peak RSS from the runner

## Positive control

At the full quotient-class budget, every predicted zero is lifted against every member of its source class and must reproduce the materialized baseline support exactly with valid witnesses and a solved matched rho certificate.

## Negative control

Fresh curves and all four factor-base families are evaluated under the same fixed class construction. A class reduction without full support, held-out, rank, or lift accounting is not accepted as a positive result.

## Success criterion

The experiment is a scoped positive signal only if a sub-full class budget passes exact support, held-out support, full relation rank, and valid-witness gates on both fresh curves for at least one family, and its charged total predicted-plus-lift cost is below the matched full original-predicate cost. It is not an ECDLP break or exponent claim.

## Falsification criterion

Record a scoped negative result if no family satisfies the strict gate on both curves, if class count is effectively `B^2`, if the quotient rank is insufficient, if full lifting does not reproduce baseline support, or if charged quotient work is not below the full original-predicate comparator.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher --repo . run \
  experiments/EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001/specification.json \
  --allow-dirty
```

## Claim boundary

This is toy-scale, fixed-curve, representation-specific evidence. It does not recover a deployed key, improve the generic prime-field ECDLP exponent, or establish a classical attack against cryptographic-size curves.
