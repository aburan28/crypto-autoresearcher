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
- select the lexicographically first field-coordinate `j` whose first support
  is exactly `a^2`;
- enumerate all cyclic degree-`a` subgroups on a maximal model;
- deterministic exhaustive enumeration; no hidden order or endomorphism
  input.

## Metrics

- number of supersingular classes and candidate classes tested;
- complete support vector for `1<=n<=a^2`;
- half-degree subgroup count and rational-midpoint count;
- doubled degree, target match, and prime-torsion kernel sizes;
- modular-neighbor cache size and specialization count;
- wall-clock time and peak resident memory;
- source, output, and canonical-payload hashes.

## Positive control

The supersingular polynomial has the expected degree, every selected curve is
supersingular and maximal after a public quadratic-twist adjustment, and the
selected support vector has its first positive entry at the published
`delta_E`.

## Negative controls

1. Every support bit below `a^2` is false.
2. The ordinary edge/dual backtracking chain has full `ell`-torsion kernel
   and is rejected as noncyclic.
3. `F_p`-rational and exceptional-automorphism `j`-invariants are excluded
   from fixture selection.

## Success criterion

All three increasing families pass the public selection, have at least one
degree-`a` rational midpoint, and reconstruct a cyclic degree-`a^2`
conjugate map. A separately written verifier must replay all selections and
witnesses and reject registered mutations.

## Falsification criterion

Any family failure rejects the unrestricted interpretation of the midpoint
theorem or exposes a model/implementation error that must be resolved before
using the sharp `p=101051` result.

## Reproduction command

```bash
HOME=/private/tmp /usr/local/bin/sage \
  experiments/ecdlp_isogeny/p1486_frobenius_midpoint_sweep.sage.py
```

## Artifact paths

- `research/p1486_frobenius_midpoint_sweep_contract_20260728.md`
- `experiments/ecdlp_isogeny/p1486_frobenius_midpoint_sweep.sage.py`
- `experiments/ecdlp_isogeny/p1486_frobenius_midpoint_sweep_result.json`
- `experiments/ecdlp_isogeny/p1486_frobenius_midpoint_sweep_verify.sage.py`
- `experiments/ecdlp_isogeny/p1486_frobenius_midpoint_sweep_verify_result.json`

