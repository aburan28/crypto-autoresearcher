# Experiment Contract: EXP-SGCP-EMBED-002, version 2

## Claim status

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.
The experiment is `review_required`; canonical execution is locked at zero runs.

## Hypothesis

At least one fixed coordinate predicate family preserves nonvacuous valid
structured-embedding support across generated 5-8 bit curves and improves the
certified retained-support frontier at matched constrained-label budgets over
hash-ranked x-fiber controls.

## Null hypothesis

After exact matching by curve, factor-base size, and absolute constrained-label
cap, the coordinate families do not show a stable support-at-density advantage,
or valid order ideals lose nearly all balanced-raw final support as the tested
toy size grows.

An implementation failure, invalid control, or unresolved optimizer interval is
not evidence for this null.

## Mathematical object

For each accepted prime-order curve `E(F_p)` and even factor-base size `B`, a
predicate selects `B/2` non-2-torsion x-fibers. The factor base `F` contains both
points over every selected x-coordinate.

The balanced candidate universe and its formal downward closures are inherited
without weakening from EXP-SGCP-EMBED-001. A degree-four maximum is individually
eligible exactly when EC evaluation is injective on its order ideal. Two
eligible maxima conflict exactly when evaluation on the union of their order
ideals is noninjective. A set of maxima is admissible exactly when it is an
independent set in this conflict graph. The verifier must separately test the
pairwise-conflict iff full-union-collision lemma on every exhaustive audit row.

For an admissible selected set `S`, let `A4(S)` be the EC evaluations of its
degree-four maxima and define

```text
R(S) = |{P + Q : P,Q in A4(S), P <= Q}|.
```

The private audit may compute this final join. The public partial operation may
not expose any `A4 x A4` edge.

## Optimizer contract

For each curve order `q`, evaluate the deduplicated absolute caps

```text
C in {floor(q/4), floor(q/2), floor(3q/4), q}.
```

For every cap `C`, require `constrained_count(S) <= C` and use the complete
lexicographic objective:

1. maximize `R(S)`;
2. minimize constrained labels;
3. minimize public nonidentity edges;
4. maximize the number of retained degree-four maxima;
5. choose the lexicographically least maximum list.

The optimizer may terminate by proof, node cap, or cap-cell wall limit. It must
always emit a feasible incumbent with primary lower bound `L` and a
frontier-derived primary upper bound `U`, with `L <= OPT <= U`. Only `L=U`
proves the primary optimum. A nonzero-gap cell may report the incumbent's
secondary fields, but it must not label them optimal or contribute to a
positive family gate.

Every capped search must serialize the complete live frontier. Each state binds
the selected, available, and selected-support masks plus its support/count
upper bounds. This private certificate is charged. The verifier must reconstruct
each state and bound without executing the producer search.

The verifier must exact-enumerate all sufficiently small controls and confirm
that the branch-and-bound interval contains the known optimum. It must also
recompute every bound used to prune a canonical row.

## Curves

- q bit sizes: `5`, `6`, `7`, `8`
- curve seeds: `101`, `211`
- accepted model: `y^2 = x^3 + ax + b` over prime `p > 3`
- exact prime group order `q` with the requested bit length
- reject singular curves, trace zero, anomalous trace one, `j=0`, and `j=1728`
- generator: least nonidentity affine point in canonical order
- frozen regression: `p=19,a=2,b=9,q=23,G=(0,3)`

The sampler must record every rejected draw and its reason. The regression is a
control and is not counted as a random family instance.

## Predicates

Each family selects exactly `B/2` admissible roots and then includes both point
signs.

- `least_x_interval`: rank roots by their canonical integer x-coordinate.
- `mobius_interval`: rank by `(u*x+v)/(x+w) mod p`, with domain-separated,
  public nondegenerate parameters and deterministic pole handling.
- `two_mobius_union`: alternately take roots from two independently derived
  Mobius rankings, skipping duplicates and poles until the exact cardinality is
  reached.
- `hash_x_null`: rank roots by a domain-separated SHA-256 digest. Four
  independent null replicates are matched to each curve and B.

All emitted factor bases include selected roots, both signs, public predicate
parameters, the root polynomial, and a deterministic-selection digest.

## Parameters

- factor-base sizes: `B in {4,6,8}`
- coordinate families: three
- matched null replicates: four
- conflict-graph node cap: `2,000,000` per cap cell
- constrained-label cap fractions: `1/4`, `1/2`, `3/4`, and `1`
- canonical runs before review: zero
- proposed post-review roles: one generator and one independent verifier

The fixed B values are finite stress probes. They are not an `n^(1/5)` scaling
schedule and cannot support an exponent fit.

## Metrics

Primary metrics are the exact axiom vector, direct-final-edge count, per-cap
optimizer interval and gap, balanced-raw/full-eight-fold/retained final
support, attained constrained count and delta, the certified support frontier,
and paired coordinate-versus-null differences at identical absolute caps.

Secondary metrics include `|F|`, `|2F|`, `|4F|`, `|8F|`, additive-energy
histograms under two explicitly separate source measures, candidate/rejection/
conflict graph statistics, components and degeneracy, optimizer pruning counts,
public bytes, charged private bytes, field and point operation counts, memory,
wall time, and complete curve and predicate provenance. Shared precomputation and
each cap cell must have separate operation receipts whose exact sum is the row
total. Public-model, private-audit, and per-cap JSON byte counts must be
independently reproducible from the serialized objects.

For each degree, `formal_multiset_collision_energy` squares multiplicities of
combinations with replacement. `ordered_tuple_additive_energy` first weights
each multiset by its multinomial number of orderings and then squares the
resulting output multiplicities. Neither field may be substituted for the
other.

`balanced_raw_final_support` means the final pair support of the inherited
balanced A4 universe. `eight_fold_support` means the full exact support of all
degree-eight factor-base multisets. Both denominators must appear beside any
retention ratio.

## Controls

1. Reproduce the three frozen EXP-SGCP-EMBED-001 least-x P2 primary outcomes.
2. Re-run its twelve hash-bound controls with their complete predicate vectors.
3. Exact-compare graph independence and direct closure over every subset of
   small registered instances.
4. Exact-compare every density-cap result against exhaustive empty, complete,
   path, cycle, coverage-tie, density-tie, and lexical-tie fixtures.
5. Force a node-capped fixture and replay every serialized frontier state and
   bound around the independently known optimum.
6. Test factor-base cardinality, sign symmetry, Mobius poles, union duplicates,
   and hash-null determinism.
7. Reject every registered special-curve fixture.
8. Require coordinate-decoding and non-homomorphic-permutation mutations to
   fail semantic compatibility.

## Positive criterion

All controls and exact model checks must pass. At least 90 percent of all
coordinate and null cap cells must have zero primary gap, and every remaining
gap must be at most `max(1,ceil(0.05q))`. One fixed coordinate family must have
median retained/balanced-raw support at least `0.25` at the full q cap at every
bit size. At `floor(q/2)` or `floor(3q/4)`, the same family must exceed the
paired four-null median by at least `max(1,ceil(0.05q))` retained targets in at
least three bit strata and have positive paired sign in at least 75 percent of
exact curve-B-cap comparisons.

This would be a toy coordinate-structure signal and would authorize a larger
family replication. It would not authorize an ECDLP claim.

## Falsification and narrowing

With valid controls and sufficiently resolved cap cells, failure of every fixed
family to meet both positive predictions weakens or rejects this exact
hypothesis. If every coordinate family has median retained/balanced-raw support
below `0.10` at the full cap in at least three bit strata, record the narrower
`COLLAPSE` negative for this balanced-order-ideal construction.

Neither result closes coordinate-specific SGGM embeddings in general. The next
positive question would be whether a different formal quotient, model
transformation, or source-recoverable non-tree operation avoids the measured
collision geometry.

## Budgets and stopping

Canonical budget is currently zero. Version 1 consumed 17 of the 18 authorized
development curve-family-B rows. Version 2 authorizes unit and frozen-fixture
controls only; it may not spend the final row or create a new family sweep
without a reviewed amendment.

Stop immediately on a control mismatch, builder-visible scalar material,
unmatched factor-base cardinality or constrained-label cap, invalid curve,
graph/direct disagreement, invalid optimizer bound/frontier state, direct final
edge, confused energy source measure, or uncharged private artifact.

## Claim boundary

No exponent, relation yield, matrix rank, individual logarithm, preprocessing
crossover, rho improvement, or deployment claim is in scope. Isogeny/model
transforms and direct five-term decomposition are separate successors.

## Reproduction command

No canonical reproduction command exists until independent theory, accounting,
and red-team review freeze the implementation and hash-complete execution plan.
