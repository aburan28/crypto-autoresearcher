# Scope decision — complementary non-index ECDLP lanes

## Decision

Admit seven complementary lanes into the ECDLP harness as a second-stage hypothesis portfolio. Keep them separate from PR #196 so their narrower assumptions and failure modes can be reviewed independently.

## Why this scope

The first non-index proposal grouped several ideas into broad categories. That was appropriate for initial prioritization, but it left potential theory, categorical embeddings, orbit decomposition, topology, message passing, symbolic dynamics, and random-matrix diagnostics without independent contracts.

This proposal gives each mechanism a distinct falsification target and prevents an attractive visualization or statistical anomaly from being mistaken for a cryptanalytic advantage.

## In scope

- discrete potential theory on sampled public state graphs;
- finite categorical or functorial constructions with executable toy probes;
- semigroup actions and public orbit quotients;
- persistent homology and recurrence topology used to drive decisions;
- probabilistic inference over bounded scalar uncertainty;
- symbolic encodings and finite-state predictors for public traces;
- random-matrix statistics of sampled public operators;
- reusable negative results that close one of these mechanisms.

## Out of scope

- factor bases, relation collection, smoothness, or Semaev decomposition;
- side-channel or implementation leakage;
- scalar-labelled representation learning;
- unbounded abstract machinery without a finite algorithm;
- topology, spectra, or solver convergence reported without an algorithmic consequence;
- asymptotic claims inferred directly from tiny curves;
- omitted preprocessing, model-training, or feature-search costs.

## Stage gates

### Stage 0 — executable hypothesis

Specify public inputs, observable grammar, matched null model, online and offline costs, and the precise scalar information or collision decision sought.

### Stage 1 — leakage smoke test

Run injected-leakage positives and randomized negatives. The harness must reject coordinate artifacts, generator memorization, and scalar-dependent preprocessing.

### Stage 2 — bounded measurement

Evaluate multiple primes, curves, generators, seeds, and bit sizes. Pre-register feature families where possible and correct for multiple comparisons.

### Stage 3 — algorithmic-use test

Require the candidate feature to alter a concrete operation: choose a jump, reduce an interval, predict a collision, canonicalize an orbit, or prune a verified search state.

### Stage 4 — adversarial review

Independently test whether the result is disguised index calculus, random-group generic behavior, finite-size overfitting, or an unpriced memory/preprocessing tradeoff.

### Stage 5 — promotion

Promote only if the lane produces one of:

1. an overhead-inclusive generic-search improvement;
2. a public scalar predicate with an explicit ECDLP reduction;
3. an efficiently computable representation with verified non-random structure and algorithmic use;
4. a rigorous or strongly evidenced barrier closing a substantial family of candidates.

## First-wave tasks

- `ORBIT-SEMIGROUP`: enumerate public action semigroups and test quotient/canonicalization savings.
- `SYMBOLIC-DYN`: build coordinate-invariant trace alphabets and finite-state predictors.
- `POTENTIAL-FUNC`: approximate harmonic, Green, and heat-kernel coordinates on sampled state graphs.
- `COMMON-NULLS-II`: extend random-cycle controls for topology, automata, and operator statistics.

The remaining lanes begin with theory triage and only advance after producing a finite executable probe.