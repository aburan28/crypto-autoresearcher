# Independent volcano-level rho replication

Frozen: 2026-10-13, before any fresh solve was launched.

Status: **exploratory additive replication; not ledger evidence, a measured
bound, an isogeny-transfer result, or a weak-curve verdict.** The historical
studies remain immutable.

## Question

For the already certified four-node conductor lattices over `GF(2^37)` and
`GF(2^41)`, do fresh independent operation counts reproduce the observation
that native negation-only rho has essentially the same mean work at every
sampled endomorphism-ring level? Separately, how much larger is each native
level's count than the Koblitz crater's signed-Frobenius arm?

The four nodes are a `2 x 2` conductor-factor lattice, not a linear volcano:

- `m=37`: `f_E = 1, 73, 2663, 73*2663`;
- `m=41`: `f_E = 1, 409, 1721, 409*1721`.

## Frozen executions

The exact historical curve samples and solver sources are reused by hash.
All seeds below are disjoint from the historical namespaces.

| study | curves by node | crater arms | fresh solves |
|---|---|---|---:|
| `m37` | `1, 74, 22, 30` | negation and signed `tau`; 10 chunks x 500 each | 136,000 |
| `m41` | `1, 30, 30, 30` | negation and signed `tau`; 15 chunks x 200 each | 24,000 |

Every lower curve uses negation only. Each `m37` lower curve has two chunks
of 500; each `m41` lower curve has one chunk of 200. Jobs are deterministically
shuffled, then assigned to four workers pinned to CPUs 0--3. The runner stages
each output under a `.partial` name, validates it, and atomically publishes it.
Worker exceptions propagate. Resume is deliberately unsupported: any
infrastructure failure preserves that output root and a later attempt must use
a new empty root.

Fresh seeds are

`base_m + 10000*curve_id + 1000*mode + chunk`, with bases
`37,000,000,000` and `41,000,000,000`. Shuffle seed: `2026101317`.

Pinned inputs:

- `m37 rho.c`: `7c8195ae671124f057ab913bb10e98f7a75c5c5e16cbbac3f67b5fd87a20b106`;
- `m37 sample.csv`: `994caf2b456058c8fee9dc87f6289d7a07a22a0c07b03e64bbfb015797f7d4cd`;
- `m41 rho.c`: `212cd0aebf36e9095b42677a02286c85834763d9b37028b49529020de5cec90f`;
- `m41 params.h`: `89c1c89ef929d8758ad43cebe98553091ed9bbb358a8fbe9aca721865cd58ec3`;
- `m41 sample.csv`: `37931f3e0417f1fe0f25965aa18e858e29f6fdc028cff4ae3bccf5d47fd564dc`.

Build command: `gcc -O2 -march=native -o <binary> rho.c`. The runner records
the compiler, host, commit, dirty state, source and binary hashes, exact job
plan, commands, timestamps, and per-job receipts.

## Validity and stopping

The run is valid only if the exact frozen file set exists, every CSV has its
exact row count and schema, run indices are exactly consecutive, and every
planted-key certificate has `ok=1`. Missing, extra, duplicate, nonnumeric, or
unverified rows fail closed. No scientific failure is replaced. A process or
infrastructure failure invalidates that attempt; its files remain preserved
and may not be combined with a later attempt.

The sample counts are fixed. Do not add runs after inspecting effects. Local
trail-cap restarts remain charged work and are diagnostics, not failed solves.

## Metrics and inference

Primary metric: source `ops`, i.e. counted group additions/doublings after the
target is known. It includes target-dependent `Q2` and jump-table setup, walk
starts, look-ahead retries, cycle escapes, and abandoned work. It excludes
curve/generator precomputation, target construction, field-operation pricing,
final verification, and any isogeny map. The exact common setup term is also
removed as a sensitivity analysis: 155 operations at `m=37`, 167 at `m=41`.

For each node report solve count, equal-curve-weighted mean, SD, CV, selected
quantiles, normalized mean over `sqrt(r)`, between-curve spread, walk starts,
cycles, local-cap restarts, useless collisions, and descriptive time. Wall
time and ns/op are `L0` descriptive values only.

The six primary contrasts are the three lower nodes versus crater-negation at
each field size. Use 50,000 fixed-seed three-stage empirical bootstrap
resamples: curves, then process chunks within selected curves, then solves
within selected chunks. The one-curve crater uses chunk then solve resampling.
For bounded memory, first generate exactly 4,096 fixed-seed solve-resampled
means per chunk and propagate those empirical reservoirs through the outer
layers; the analysis records this approximation and a 2,000,000-cell block
limit. Report pointwise 95% intervals, Bonferroni simultaneous 95% intervals,
and simultaneous 90% intervals for the frozen `+/-3%` equivalence band.
Global equivalence is reported only if all six simultaneous 90% ratio
intervals lie inside `[0.97, 1.03]`.

Secondary analyses are:

1. each native node versus crater signed-`tau`, both total and setup-excluded;
2. the four vertical-edge contrasts per lattice;
3. the conductor-factor interaction
   `g_11 - g_10 - g_01 + g_00`, where `g = log2(mean ops)`;
4. fresh point estimates versus the archived pilot, never pooled.

Bootstrap seed: `20261013`. Archived data are planning/context only.

## Known design limitation

This is independent, not target-paired, evidence. In the existing solver,
`setup_curve(seed)` uses one PRNG stream for curve-dependent rejection,
generator/precomputation, target, and walk randomness. Equal command-line
seeds therefore do not make matched targets across curves. A future paired
five-arm experiment must split these streams, freeze a generator per curve,
pass an explicit planted scalar and hash salt, and include A/A controls.

Consequently this run can measure reproducibility and node-level differences
in this implementation. It cannot assign a difference causally to conductor,
establish a fully priced speedup, demonstrate an executable transfer, or label
any source or endpoint weak.
