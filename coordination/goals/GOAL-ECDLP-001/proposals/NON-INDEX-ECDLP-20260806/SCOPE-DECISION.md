# Scope decision — non-index-calculus ECDLP lanes

## Decision

Admit eight research lanes into the ECDLP harness as a staged hypothesis portfolio. Begin with three bounded pilots: generic-group walk synthesis, automatic invariant discovery, and spectral/dynamical analysis.

## Why this scope

Prior work in the repository has heavily tested relation-generation and index-calculus-style mechanisms. This proposal deliberately moves the search boundary to mechanisms that either improve generic collision search or discover a new efficiently computable observable.

The lanes are exploratory, but they are not exempt from cryptanalytic standards. Every pilot must be falsifiable, benchmarked against matched random cyclic groups, and evaluated using end-to-end operation counts.

## In scope

- toy prime-order curves over generic prime fields;
- generic-group and matched random-cycle controls;
- symbolic invariant search;
- spectral and dynamical statistics of addition walks;
- adaptive Pollard-style iteration policies;
- self-supervised or equivariant representation learning;
- partial scalar predicates with explicit reductions;
- public lifted representations and automated correspondence search;
- circuit and proof-complexity measurements that produce transferable scaling claims.

## Out of scope

- attacks on deployed keys or third-party systems;
- side channels, faulty implementations, nonce failures, or weak curve generation;
- binary-field or extension-field index calculus;
- Semaev/factor-base variants under new terminology;
- model accuracy without a cryptanalytic cost reduction;
- claims extrapolated directly from one tiny curve to P-256.

## Stage gates

### Stage 0 — design

Produce a hypothesis, threat model, random-group control, leakage analysis, cost metric, and falsification threshold.

### Stage 1 — smoke

Run deterministic toy instances at two small bit sizes. Fail fast on leakage, memorization, invalid controls, or overhead exceeding the baseline.

### Stage 2 — measurement

Run multiple curves, generators, seeds, and bit sizes. Fit scaling laws and report uncertainty.

### Stage 3 — adversarial review

Require an independent red-team pass for hidden labels, coordinate artifacts, preprocessing, nonuniform scalars, and implicit index-calculus behavior.

### Stage 4 — promotion

Promote only if the mechanism either:

1. reduces normalized group-operation cost against a strong rho baseline; or
2. computes a scalar predicate with a concrete end-to-end reduction to ECDLP; or
3. establishes a reusable negative theorem or experimental barrier that closes a substantial lane.

## First-wave tasks

- `WALK-SYNTH`: synthesize bounded adaptive rho policies and compare against fixed jump-set baselines.
- `INV-DISC`: search low-complexity symbolic and finite-state invariants with random-group controls.
- `SPECTRAL-DYN`: measure operator spectra, return times, and scalar-displacement predictability under coordinate-invariant observables.
- `REDTEAM-COMMON`: build shared leakage and matched-control tests before interpreting any positive result.
