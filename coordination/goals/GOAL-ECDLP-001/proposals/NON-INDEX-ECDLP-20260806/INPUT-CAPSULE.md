# Non-index-calculus ECDLP research capsule

## Goal

Generate and falsify research directions for generic prime-field ECDLP that do not rely on factor bases, smoothness, relation collection, Semaev-polynomial decomposition, or Gröbner-basis index calculus.

The target is not an immediate P-256 break. The target is a reproducible signal on toy prime-order curves that survives controls and suggests a mechanism capable of reducing generic search, improving rho beyond known constant factors, or exposing a new efficiently computable invariant.

## Hard exclusions

Reject a lane if its core mechanism reduces to any of the following:

- factor-base membership or decomposition;
- collecting linear relations among small subsets of points;
- hidden smoothness or summation-polynomial solving;
- transferring ECDLP to a known easier DLP without a newly justified map;
- training directly on scalar labels without held-out-curve generalization;
- reporting neural prediction accuracy without an end-to-end query or operation advantage.

## Research lanes

### L1 — Automatic invariant discovery

Search symbolic expressions, finite-state summaries, and learned equivariant features of `(P,Q)` for a quantity correlated with `k` or a nontrivial predicate of `k`.

Required controls:

- random cyclic groups of matched order;
- coordinate randomization and curve isomorphisms;
- held-out primes, curves, generators, and scalar intervals;
- permutation tests and multiple-hypothesis correction.

Promotion gate: a reproducible predicate advantage that remains after controls and can be evaluated with substantially fewer than `sqrt(n)` group operations or queries.

### L2 — Spectral and dynamical structure

Treat addition walks and rho iteration functions as operators on the subgroup. Test whether spectral, diffusion, recurrence, or orbit statistics distinguish scalar displacement from matched random-cycle baselines.

Candidate probes:

- transition-operator spectra from sampled observables;
- Koopman-style finite-dimensional approximations;
- return-time and collision-location distributions;
- adaptive jump sets selected by measurable state features;
- quotient walks under efficiently computable automorphisms.

Promotion gate: a statistically stable feature that predicts useful walk progress or lowers measured collision cost beyond the best matched rho baseline, including overhead.

### L3 — Latent linearization

Learn an embedding `phi` for curve points such that addition or scalar multiplication is simpler in latent space, without giving the model discrete-log labels during representation learning.

Required objectives:

- contrastive consistency under known additions;
- equivariance under negation and available automorphisms;
- cycle-consistency across independently sampled curves;
- explicit anti-memorization controls.

Promotion gate: the embedding supports a verified scalar predicate, interval reduction, or collision strategy that generalizes to unseen curves and beats a random-group control.

### L4 — Generic-group walk synthesis

Search directly over Pollard-style iteration policies, jump distributions, distinguished-point rules, and adaptive state machines.

This lane may improve generic algorithms, but must separate:

- true operation-count savings;
- parallelization or hardware effects;
- memory-time tradeoffs;
- benchmark artifacts from nonuniform scalar distributions.

Promotion gate: lower normalized group-operation cost than strong negation-map rho baselines on uniform random instances, with confidence intervals and full overhead accounting.

### L5 — Partial-information and entropy attacks

Search for efficiently computable predicates of the scalar rather than full recovery. Compose weak predicates only when the composition cost is explicit.

Candidate targets:

- parity or residue-class bias;
- interval membership;
- noisy comparisons between two candidate scalar regions;
- compressibility or predictability of observable walk traces.

Promotion gate: non-negligible advantage on uniform scalars, surviving random-group controls, together with a concrete reduction from the predicate to an end-to-end ECDLP speedup.

### L6 — Lifted and approximate representations

Explore p-adic, real/complex, formal-group, deformation, or approximate lifts only where the lift is efficiently computable from public curve data and does not assume knowledge of the scalar.

Promotion gate: a public, stable, precision-bounded observable that carries scalar information not present in matched random encodings, with a complete cost model for lifting and recovery.

### L7 — Circuit, SAT, and proof-complexity structure

Encode bounded ECDLP instances as circuits or constraint systems and measure whether solver behavior reveals exploitable structural asymmetry rather than merely solving tiny instances exponentially.

Promotion gate: a scaling law or reusable decomposition that transfers across primes and curves and implies an algorithmic advantage over generic search.

### L8 — Automated correspondence discovery

Search for efficiently computable maps, pairings, semiconjugacies, or correspondences that transform scalar multiplication into a simpler action while red-teaming every candidate for hidden homomorphism assumptions.

Promotion gate: an explicit public map with verified algebraic properties and a complexity analysis showing that evaluating or inverting it does not already require solving ECDLP.

## Initial priority

1. L4 generic-group walk synthesis — highest chance of measurable near-term progress.
2. L1 automatic invariant discovery — highest scientific upside with clean falsification.
3. L2 spectral/dynamical structure — strong bridge between L1 and L4.
4. L3 latent linearization — proceed only with strict random-group and held-out-curve controls.
5. L5–L8 — theory and toy probes after the first three lanes establish common baselines.

## Shared benchmark contract

- Prime-order short-Weierstrass curves over generic prime fields at several toy bit sizes.
- Uniform random scalar instances and independently sampled generators.
- Matched random cyclic-group oracle baseline where each proposed observable is representable.
- Strong Pollard rho baseline with negation-map handling where applicable.
- Report group operations, field operations, wall time, memory, training cost, and offline precomputation separately.
- No promotion from a single curve, seed, or bit size.
- All claimed advantages require held-out-curve replication and confidence intervals.

## Expected harness outputs

Each lane must produce:

- a hypothesis card;
- a minimal implementation or impossibility argument;
- a preregistered benchmark plan;
- raw artifacts and deterministic seeds;
- a verdict of `SUPPORTED`, `DOES_NOT_SURVIVE`, `INCONCLUSIVE`, or `BLOCKED`;
- a red-team note identifying leakage, memorization, hidden index-calculus behavior, and unpriced preprocessing.
