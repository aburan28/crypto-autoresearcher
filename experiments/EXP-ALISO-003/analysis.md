# Analysis — Autolab isogeny: p1486_frobenius_midpoint_sweep

## Observation
Date: 2026-07-28

Source excerpt / raw summary:

```
# Experiment Contract: Frobenius Midpoint Increasing-Family Sweep

Date: 2026-07-28

## Hypothesis

For three public AOV sharp primes whose published least conjugate-isogeny
degree is a square,

```text
(p, delta_E, a) = (211,4,2), (1811,9,3), (9623,16,4),
```

an exhaustive public supersingular-graph search finds a non-`F_p`
`j`-invariant with least cyclic conjugate degree `a^2`, and at least one
cyclic degree-`a` quotient has `F_p`-rational `j`. Its Frobenius-dual double
is a cyclic degree-`a^2` isogeny to the conjugate curve.

## Null hypothesis

At least one selected sharp family has no rational half-degree midpoint, all
doubled kernels are noncyclic, or the public path-support selection disagrees
with the published least degree.

## Status

HYPOTHESIS / TOY-EVIDENCE-PENDING / MODEL-BOUND

The sweep tests the restricted square-midpoint theorem. It cannot establish
that cryptographic instances have square or small-squarefree-center short
degrees.

## Parameters

- primes and target degrees fixed above from AOV Tables 4.1 and 5.1;
- all supersingular `j`-invariants obtained from Sage's supersingular
  polynomial, over a deterministic quadratic field;
- exclude `j in F_p`, `j=0`, and `j=1728`;
- test cyclic support for every `1<=n<=a^2` by a fixed sorted prime-factor
  path with same-prime nonbacktracking;
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
