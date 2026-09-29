# Train the general polynomial solver selectors

The implementation is installed at `/app/polynomial_ml`. Complete one bounded
software run using the frozen quick profile and preserve the resulting data,
models, metrics, logs and verification receipt:

```sh
python -m polynomial_ml run --profile quick --seed 20260904 --fit-seed 0 --output /app/output/run
```

The run measures four public SymPy solver configurations on generated
two-variable polynomial systems, trains a supervised predictor and an offline
one-step contextual bandit, and evaluates them on unseen primes and one unseen
polynomial family. All completed roots must match complete enumeration of the
original equations. Training uses training rows only. Do not edit the frozen
case schedule, controls, implementation or verifier to change the outcome.

The reward is binary software completion and consistency, not speedup. Retain
slower results and timeouts as reported. A timeout is censored, and a crash is
an implementation failure. Do not infer asymptotic behavior from these small
systems. This task concerns general computational algebra only.
