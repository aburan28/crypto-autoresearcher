# FactorBaseLab: automated factor-base discovery for prime-field ECDLP

Status: **research design / toy-evidence program**

## Motivation

The existing Semaev lane already measures point decomposition through
`harness/semaev.py`, including direct certificates and implementation-bound
Groebner telemetry. What is missing is a first-class harness lane that varies
**the factor-base definition itself** while holding curve, target, solver, and
cardinality controls fixed.

The core question is not simply whether a candidate factor base has high
relation yield. A useful candidate must simultaneously improve enough of the
full pipeline:

```text
factor-base definition
  -> on-curve lift / membership
  -> true decomposition availability
  -> Semaev system construction
  -> algebraic solve cost
  -> verified relation
  -> marginal relation rank
  -> sparse linear algebra
  -> blind target descent
```

A subproblem speedup is not an ECDLP speedup. FactorBaseLab therefore records
and gates each stage separately.

## Non-duplication rule

This lane does **not** reopen arbitrary coordinate-map, current monodromy/BKK,
or generic summation-yield campaigns merely under new names. A proposal is
admitted only when it changes at least one of:

1. the factor-base predicate or parameterization;
2. the membership encoding presented to the Semaev solver;
3. the matched-control methodology;
4. the objective function (for example marginal rank rather than raw yield);
5. the target-descent model.

## First-class objects

### `FactorBaseSpec`

A canonical, hashable declaration of a factor-base family and parameters.
Required fields:

```yaml
family: interval | centered_interval | qr_window | multiplicative_subgroup |
        multiplicative_coset | polynomial_image | polynomial_predicate |
        bit_window | random_matched | learned_sparse
size: integer
scope: full_curve | target_subgroup
params: {}
seed: integer
```

The serialized form is part of experiment provenance.

### `FactorBaseBuilder`

Produces either an explicit x-coordinate set `V` or an implicit membership
predicate. It must report:

- requested and realized size;
- on-curve lift fraction;
- construction time;
- memory;
- membership-test cost;
- scope (`full_curve` versus `target_subgroup`);
- canonical hash.

### `GroundTruthDecomposer`

For toy instances, measure decomposition availability independently of the
algebraic solver. For length two, use an exact EC-group two-sum/MITM oracle.
For length three, use a bounded MITM oracle when feasible.

This separation is mandatory. It distinguishes:

```text
bad factor base
```

from

```text
good factor base + bad polynomial solver
```

### `SemaevCompiler`

Compile

```text
S_(m+1)(x_1, ..., x_m, x_R) = 0
```

plus the candidate factor-base membership constraints. Record polynomial count,
variables, monomial count, input degrees, encoding size, and a content hash.

### `SolverAdapter`

Initial backend: existing SymPy Groebner instrumentation in
`harness/semaev.py`.

Future adapters may include Singular, Sage, resultants, crossbred solvers, or
other reproducible algebraic backends. Solver-specific telemetry must be labeled
as implementation-bound unless it measures a mathematically defined invariant.

### `RelationVerifier`

No x-coordinate solution is counted as a relation until:

1. every x-value lifts to a curve point;
2. sign choices are resolved;
3. the EC sum exactly equals the target;
4. the relation's scope is valid for the target subgroup when logs are required.

### `RankTracker`

Track incremental relation rank. The primary relation metric is not raw
relation count but **independent verified rows per unit cost**.

### `DescentProbe`

Freeze the factor base and any preprocessing, then test held-out target points.
All online target work is charged. A factor base that helps relation collection
but makes individual logarithms worse fails the end-to-end gate.

## Factor-base families

### FB-BASE-INTERVAL

```text
V = {x : 0 <= x < B}
```

Baseline only. Cheap membership and simple encoding.

### FB-CENTERED-INTERVAL

```text
V = {-B, ..., B} mod p
```

Tests whether additive symmetry affects relation yield or solver behavior.

### FB-QR-WINDOW

```text
V = {x < B : Legendre(x) in {0,1}}
```

Adds arithmetic structure at controlled density.

### FB-MSUBGROUP

A multiplicative subgroup `H <= F_p^*`, intersected with liftable
x-coordinates. Exact subgroup size must divide `p-1`.

### FB-MCOSET

```text
V = aH
```

for a multiplicative subgroup `H`. Compare many cosets at identical
cardinality to separate abstract subgroup structure from placement relative to
the curve coefficients.

### FB-POLY-IMAGE

```text
V = { f(t) : t in T }
```

with sparse degree-2--4 `f` and a simple bounded domain `T`. This gives a
compact algebraic parameterization that can sometimes be substituted directly
into the Semaev system.

### FB-POLY-PRED

A low-degree sparse predicate such as

```text
h(x) in W
```

or a polynomial equation in an auxiliary variable. The key research question
is whether the membership equations interact favorably with the Semaev system.

### FB-BIT-WINDOW

Fixed high or low radix bits of `x`. Artificial but useful as an ML/control
family because density and description complexity are easy to tune.

### FB-RANDOM-MATCHED

Uniform random liftable x-values with exactly the same realized cardinality as
the structured candidate. Every structured candidate must have this control.

### FB-LEARNED-SPARSE

Sparse low-degree polynomial or Boolean predicates proposed by an optimizer.
This is the discovery family, not the starting point.

## Mandatory controls

For every candidate `V`, automatically construct:

1. **matched-cardinality random** `V_rand`;
2. **affine transforms** `aV+b` when well-defined and size-preserving;
3. **fresh seeds** on the same curve;
4. **held-out curves** of the same bit size;
5. **blinded targets** sampled independently of proposal/training data.

A claimed structural anomaly must survive more than one of these controls.

## Metrics

### Base metrics

- `requested_size`
- `realized_size`
- `density`
- `lift_fraction`
- `construction_seconds`
- `membership_ns`
- `bytes`

### Decomposition metrics

- `Y2`, `Y3`, later `Y4`
- decomposable targets / total targets
- number of distinct decompositions when affordable
- decomposition multiplicity distribution
- matched-random lift in yield

### Algebra metrics

- variable count
- polynomial count
- input max degree
- monomial count
- Groebner wall time
- basis size
- basis max degree (proxy; not theoretical degree of regularity)
- peak RSS
- timeout rate
- solver-specific matrix / pair telemetry when available

### Relation metrics

- verified relation rate
- duplicate rate
- row weight
- marginal rank gain
- rank / factor-base size
- relations required for rank saturation

### End-to-end metrics

- verified relations / CPU-second
- independent verified relations / CPU-second
- independent verified relations / GB-second
- preprocessing cost
- blind target-descent cost
- total charged cost versus rho / BSGS / MITM controls

## Selection rule

Do not collapse the experiment to one scalar score initially. Keep a Pareto
front over at least:

```text
maximize: Y_m, independent_relations_per_second
minimize: solver_seconds, peak_memory, |F|, online_descent_cost
```

A candidate is promoted only if it beats matched random controls on both
relation supply and algebraic cost, or supplies an explicit mechanistic reason
why a different Pareto tradeoff is useful.

## ML proposal engine

ML enters only after a trustworthy corpus exists.

### Phase 1: interpretable surrogate

Train gradient-boosted trees to predict:

- `Y_m`;
- log solver time;
- basis max degree;
- memory;
- marginal rank.

Features include factor-base family and parameters, realized size, density,
curve coefficients, j-invariant, subgroup metadata, simple residue statistics,
and Semaev input-system statistics.

### Phase 2: proposal search

Use Bayesian optimization or an evolutionary strategy over sparse predicate
parameters. Optimize expected Pareto improvement, not raw success probability.
Include a novelty penalty for duplicate and affine-equivalent candidates.

### Phase 3: property discovery

For persistent anomalies, run symbolic regression to search for a compact
invariant that predicts the effect. Treat this only as conjecture generation.
A theory agent must then attempt to prove or falsify the proposed mechanism.

## High-value follow-up ideas

### Hierarchical factor bases

Use nested bases

```text
F0 subset F1 subset F2
```

and try cheap decomposition at `F0` before widening. Charge the resulting
relation matrix and early-exit policy end-to-end.

### Solver-aware predicates

Search directly for predicates that lower monomial count, elimination degree,
or observed solving degree of the Semaev system, rather than maximizing point
density.

### Rank-aware proposal objective

Reward candidates for marginal rank, not relation count. This addresses the
common failure mode where a high-yield family produces mostly dependent rows.

### Failure-predictor model

Train a timeout / degree-explosion predictor. Use it to prune expensive
candidate systems while preserving a random exploration budget so the model
does not censor novel regimes.

### Cross-solver anomaly gate

Before escalating an algebraic anomaly, require the signal to survive at least
two independent solving strategies or one solver plus a mathematically defined
proxy.

### Information-gain scheduling

Allocate compute by expected information gain / uncertainty rather than by the
highest current score. This prevents the optimizer from repeatedly exploiting a
toy artifact.

## Promotion gates

A factor-base candidate is not promoted beyond toy research unless all relevant
gates pass:

1. matched random control;
2. affine/placement control;
3. held-out curve control;
4. exact point-relation verification;
5. marginal rank control;
6. blind target descent;
7. all preprocessing charged;
8. at least three-size scaling sweep;
9. rho/BSGS/MITM comparator;
10. independent red-team interpretation.

## First milestone

Implement `EXP-FB-001` before adding a learned proposal engine:

- bit sizes: 20, 24, 28, 32;
- decomposition lengths: 2 and 3;
- candidate families: interval, QR-window, multiplicative subgroup/coset,
  sparse polynomial predicate, matched random;
- exact ground-truth decomposition oracle at toy scale;
- existing Semaev/Groebner telemetry;
- relation verification;
- incremental rank tracking;
- matched and affine controls;
- immutable JSONL/JSON records with seeds and content hashes.

The initial milestone is successful if it produces a trustworthy comparative
corpus, even if every structured factor base loses to random controls.
