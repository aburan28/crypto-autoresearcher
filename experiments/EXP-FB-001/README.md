# EXP-FB-001 — matched-control factor-base discovery baseline

Status: **CONTRACT / NOT YET RUN**

## Hypothesis

HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND:

Some structured x-coordinate factor-base families may produce a reproducible
Pareto improvement over same-cardinality random factor bases in one or both of:

1. true point-decomposition availability; and
2. algebraic cost of the associated Semaev system.

A positive result is not an ECDLP break. It is only a candidate mechanism for
later rank, linear-algebra, target-descent, and scaling gates.

## Why this experiment exists

The current harness can measure Semaev `S_3` decomposition and Groebner proxies,
but a solver measurement alone conflates two different questions:

- does a target actually have a short decomposition over the chosen base?;
- can the selected algebraic encoding find that decomposition cheaply?

EXP-FB-001 separates these quantities and introduces matched controls.

## Frozen scope

### Field sizes

```text
20, 24, 28, 32 bits
```

Use at least 3 independent deterministic curve seeds at each size for the
minimum smoke campaign and at least 20 per size for the evidence campaign.

### Decomposition lengths

```text
m = 2
m = 3
```

`m=2` is the first implementation target because exact ground truth can be
measured cheaply. `m=3` may use bounded MITM and must report any censoring or
budget aborts.

### Factor-base families

Required v1 families:

1. interval;
2. QR-window;
3. multiplicative subgroup or coset where `p-1` admits a suitable divisor;
4. sparse polynomial predicate;
5. matched-cardinality random control.

Optional during the first campaign:

- centered interval;
- polynomial image;
- bit/radix window.

### Scope labels

Every run must say whether the factor base is:

```text
full_curve
```

or

```text
target_subgroup
```

A `full_curve` experiment may measure decomposition geometry and solver cost but
must not be interpreted as a valid factor-base logarithm system unless the
relation semantics are separately justified.

## Required matched controls

For every structured candidate `V`:

- construct `V_rand` with identical realized size;
- evaluate fresh target samples;
- evaluate multiple seeds;
- where possible, evaluate affine transforms `aV+b` that preserve realized size;
- repeat on held-out curves.

If a structured base wins only because its realized size differs from the
control, the result is invalid.

## Stage A — factor-base construction

Record:

```text
family
params
requested_size
realized_size
scope
seed
construction_seconds
lift_fraction
membership_cost
factor_base_hash
```

Failure conditions:

- unable to realize requested cardinality within frozen budget;
- duplicate x-values silently reduce size;
- membership predicate uses target-secret information;
- scope is mislabeled.

## Stage B — exact decomposition oracle

For each frozen target, measure whether a short EC decomposition actually
exists independent of the Semaev/Groebner solver.

For `m=2`, use exact EC-group two-sum or equivalent MITM. Both signs of every
lifted x-coordinate must be handled correctly.

Primary metrics:

```text
Y2 = decomposable_targets / targets
Y3 = decomposable_targets / targets
mean_decomposition_multiplicity
oracle_seconds
```

This stage is the ground truth for solver recall.

## Stage C — Semaev compilation and solve

For `m=2`, compare against the existing `harness.semaev.measure_s3_decomposition`
path whenever the membership representation is compatible with it.

Record:

```text
polynomial_count
variable_count
input_max_degree
monomial_count
groebner_seconds
groebner_basis_size
groebner_basis_max_degree
peak_rss_mb if available
timeout
```

`groebner_basis_max_degree` is an implementation-bound proxy, not a claim about
theoretical degree of regularity.

If a new membership predicate is encoded using auxiliary variables, charge all
added variables and equations.

## Stage D — exact relation verification

A solver success is counted only if:

1. x-values lift to E(F_p);
2. signs are resolved;
3. the EC sum equals the target exactly;
4. the relation obeys the declared scope.

Track false/extraneous algebraic solutions explicitly.

## Stage E — relation rank gate

For candidates that survive Stages A-D, collect enough verified relations to
plot rank growth.

Record:

```text
relations_seen
unique_relations
row_weight
marginal_rank_gain
matrix_rank
matrix_columns
```

High raw yield with poor marginal rank is a negative result.

## Stage F — blind descent gate

Freeze:

- factor-base spec;
- solver settings;
- any preprocessing;
- learned proposal state.

Then evaluate held-out targets. Charge all online work.

No target-dependent factor-base tuning is allowed unless it is an explicitly
separate experiment with its cost model frozen in advance.

## Baselines

At minimum compare against:

- matched random factor base;
- the existing seeded factor base in `harness/semaev.py`;
- rho cost for the same toy group;
- BSGS/MITM where applicable;
- existing Groebner instrumentation.

## Primary analysis

Maintain a Pareto table rather than a single score.

Maximize:

```text
Y_m
verified_relations_per_second
independent_relations_per_second
```

Minimize:

```text
solver_seconds
peak_memory
factor_base_size
blind_descent_cost
```

### Promotion condition

A structured candidate is promoted to a follow-up only when it beats its
matched random control in at least one meaningful metric without regressing the
other load-bearing stages enough to erase the advantage.

The strongest anomaly class is:

```text
higher Y_m AND lower algebraic solve cost at matched size
```

and the signal persists on held-out curves.

## Red-team checklist

The independent red-team agent must answer:

1. Was factor-base cardinality actually matched?
2. Did the candidate exploit a special weak curve?
3. Did the experiment measure x-root existence rather than EC relations?
4. Were both point signs handled?
5. Was the factor base outside the target subgroup?
6. Was preprocessing hidden?
7. Did rank saturate early?
8. Does blind target descent preserve the gain?
9. Is the apparent win solver-specific?
10. Does the effect vanish under affine relocation or fresh curves?
11. Is this a duplicate of an existing coordinate-map / monodromy / BKK lane?
12. Does a multi-size sweep suggest the advantage shrinks with p?

## Falsifiers

The headline hypothesis is falsified for a tested family/range if, after matched
controls:

- decomposition yield is indistinguishable from random and solver cost is not
  lower; or
- solver cost improves only because realized cardinality is smaller; or
- the signal disappears on held-out curves; or
- verified relations have no marginal-rank advantage; or
- blind descent erases the gain.

A family-specific negative result must be preserved in the ledger.

## Success criteria for this PR

This PR does not claim experiment results. It succeeds by freezing a reusable
research contract and the FactorBaseLab architecture so future agents do not
confuse relation probability, solver cost, rank, and target descent.

## Follow-up experiments

- `EXP-FB-002`: affine-invariance and placement gate.
- `EXP-FB-003`: Bayesian sparse-predicate proposal search.
- `EXP-FB-004`: marginal-rank gate for top candidates.
- `EXP-FB-005`: blind target-descent gate.
- `EXP-FB-006`: three-plus-size scaling and exponent fit.
