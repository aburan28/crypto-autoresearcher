# Koblitz/Subfield Index-Calculus Follow-through Campaign

Status: proposed executable research campaign; no attack, speedup, or asymptotic claim.

## Purpose

Prevent promising Koblitz/subfield index-calculus ideas from disappearing after ideation. This campaign binds each idea to a falsifiable experiment, an implementation deliverable, a metric, a dependency, and a next-state rule.

The campaign extends, rather than replaces:

- `research/experiments/orbit_aware_decomposition_experiments.yaml`
- `research/experiments/frobenius_next_wave_experiments.yaml`
- `research/experiments/index_calculus_pipeline_search.yaml`

## North-star metric

Every candidate ultimately reports:

`T_verified_relation = (setup + candidate generation + encoding + solve + extraction + verification) / newly independent verified relations`

and, when enough relations exist:

`T_e2e = T_setup + T_relation + T_linear_algebra + T_target_recovery`.

For Koblitz/subfield curves the rho comparator MUST include all applicable automorphism/Frobenius speedups. Raw solver speed is never sufficient.

## Frobenius factor

Record a common `frobenius_factor` for every eligible arm:

- `orbit_size_raw`
- `effective_factor_base_columns`
- `raw_factor_base_points`
- `orbit_column_reduction = raw_factor_base_points / effective_factor_base_columns`
- `solver_work_reduction` relative to matched non-orbit baseline
- `relation_work_reduction`
- `linear_algebra_dimension_reduction`
- `e2e_work_reduction` when measurable

This is descriptive telemetry, not an assumed n or n^2 speedup.

## Twelve threads and concrete actions

| # | Thread | Existing coverage | New action | Promotion signal |
|---|---|---|---|---|
| 1 | Solve directly in Frobenius orbits | FROB-GAUGE/CANON/ROTATE, IC-FROBJOINT | complete representative+relative-shift encoder and exact tiny equivalence harness | >=25% lower seconds/independent relation |
| 2 | Frobenius-aware Groebner/SAT | FROB-GBORDER/CHARMAC | implement block-order and character-structure instrumentation | lower peak Macaulay/solver cost on largest cells |
| 3 | Orbit-aware factor-base search | IC-FBFORM, STABSTRATA | search Frobenius-stable subspaces/affine seeds by e2e objective | held-out gain at matched effective columns |
| 4 | Trace-zero + Frobenius bases | gap | construct trace-zero/intersection candidates and matched controls | improved relation yield without solver-cost reversal |
| 5 | Representation search | BASISSURR/ACTIVEBASIS | include polynomial/normal/tower/mixed representations under identical semantics | held-out solver/e2e gain |
| 6 | Hybrid SAT-Groebner | IC-SOLVERMATCH | partition orbit/Boolean decisions from nonlinear algebraic core | >=20% net relation-cost reduction |
| 7 | Partial relations / large prime | gap | one- and two-large-orbit relation graph with recombination accounting | lower total relation collection after graph overhead |
| 8 | Tau throughout pipeline | gap | tau-NAF candidate generator vs uniform scalar controls | decomposition likelihood shift survives unbiased validation |
| 9 | General endomorphism-group IC | partial prior-art intake | generic Gamma-orbit interface; Frobenius and GLV/GLS fixtures | same verifier accepts multiple endomorphism families |
| 10 | Partial Weil descent | gap | sweep intermediate subfields/towers and jointly score system+FB | nontrivial interior optimum on held-out fields |
| 11 | Decomposition likelihood model | gap | calibrated pre-solve predictor with abstention/rejection accounting | saves solver calls with zero missed positives in safety mode |
| 12 | System-invariant telemetry | partial | common Hilbert/Macaulay/syzygy/solver-trajectory schema | invariant predicts held-out cost better than size alone |

## Follow-through state machine

Every thread has exactly one state:

`idea -> specified -> implemented -> tiny_verified -> benchmarked -> held_out -> e2e -> reviewed -> promoted|retired`.

A thread may not skip `tiny_verified` when its transformation can alter solution semantics. A timeout is an implementation observation, not mathematical falsification.

Each weekly coordination pass must emit:

1. current state for all 12 threads;
2. last artifact/run supporting that state;
3. blocker if stalled;
4. single next executable action;
5. whether the thread has gone stale (>7 days with no artifact and no explicit blocker).

The Coordinator should preferentially schedule stale high-priority threads before generating more variants of already-active ideas.

## Decomposition-likelihood objective

For candidate relation point R and frozen feature map phi(R), estimate

`p_hat = P(decomposable | phi(R), curve cohort, factor-base contract, arity)`.

Required evaluation:

- Brier score and log loss;
- calibration error/reliability bins;
- ROC/PR only as secondary diagnostics;
- solver calls avoided at a frozen acceptance threshold;
- false-negative count;
- net seconds per independent relation after feature/model cost;
- temporal/curve held-out validation.

A ranking model may reorder attempts. A hard rejection filter is promoted only after a frozen safety mode observes zero false negatives on the preregistered validation corpus.

Candidate features include trace, subtrace where defined, Frobenius orbit length, stabilizer size, normal-basis Hamming/correlation signatures, tau-NAF weight, factor-base projection coordinates, cheap Semaev/Macaulay surrogates, and target-independent invariant evaluations. Hidden discrete logs and evaluator ground truth are forbidden features.

## Required implementation interfaces

`research/code/koblitz_followthrough/` should converge on:

- `features.py`: deterministic candidate features and schema;
- `likelihood.py`: calibration, ranking, threshold policy, metrics;
- `frobenius_metrics.py`: common Frobenius-factor accounting;
- adapters for relation candidates, solver telemetry, and verified-relation outcomes.

These utilities must remain attack-agnostic measurement infrastructure: they do not claim a cryptanalytic improvement.

## Stop generating, start closing

New ideas in this area should first map to one of the twelve threads. Create a thirteenth thread only when the mechanism is materially orthogonal. A thread with an unexecuted specified experiment should normally receive implementation/execution effort before another nearby speculative variant is added.
