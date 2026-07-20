# Experiment Contract: EXP-SGCP-EMBED-002, version 3

## Claim status

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.
The experiment is `review_required`; curve-family and canonical execution are
locked at zero new rows and zero runs.

## Hypothesis

At least one fixed coordinate predicate family, composed with the frozen
lexicographically least degree-two representative compiler, preserves
nonvacuous structured-embedding support across generated 5-8 bit curves and
improves the exact retained-support frontier over four hash-ranked x-fiber
controls at one same constrained-label cap fraction across strata.

This is a predicate-plus-compiler hypothesis. It is not an invariant of the
factor base or curve.

## Null hypothesis

On one complete valid exact matrix, no fixed coordinate-family and cap-fraction
pair simultaneously passes the full-cap persistence and matched-null advantage
rules below.

Missing rows, unresolved optimization, resource exhaustion, invalid controls,
or implementation and verifier failures are `INCONCLUSIVE`, not evidence for
the null.

## Mathematical object

For each accepted prime-order curve `E(F_p)` and even factor-base size `B`, a
predicate selects `B/2` two-point x-fibers. The factor base `F` contains both
signs above every selected x-coordinate.

The frozen compiler enumerates all degree-two multisets over `F`, groups them
by EC output, discards the identity output, and retains the lexicographically
least formal witness in every remaining output class. The complete
representative table, compiler identifier, and table digest are public.

Pairs of these representatives induce degree-four formal maxima. A maximum is
individually eligible exactly when EC evaluation is injective on its downward
closure. Two eligible maxima conflict exactly when evaluation on the union of
their downward closures is noninjective. For this fixed construction, a set of
maxima is admissible exactly when it is independent in that pair-conflict
graph. The verifier reconstructs individual rejections, first collisions,
eligible universe indices, and pair-conflict first collisions.

For an admissible selected set `S`, let `A4(S)` be the EC evaluations of its
degree-four maxima and define

```text
R(S) = |{P + Q : P,Q in A4(S), P <= Q}|.
```

The final join and `R(S)` are private audit data. The public partial operation
must contain no `A4 x A4` edge.

## Source interface

Every constrained coordinate label must have exactly one formal source in an
emitted public label-to-formal table. The verifier independently reconstructs
that table and its digest. The table is explicit fixed-row advice, and its
serialized bytes are charged inside the public model and each nested cap
receipt.

The legacy `source_recovery` boolean records sorted formal normalization only.
Version 3 interprets source recovery through
`source_recovery_via_public_table`; it does not treat normalization as an
inversion algorithm.

## Optimizer contract

For curve order `q`, use the deduplicated increasing caps

```text
floor(q/4), floor(q/2), floor(3q/4), q.
```

At every cap `C`, require `constrained_count(S) <= C` and use this exact
lexicographic objective:

1. maximize `R(S)`;
2. minimize constrained labels;
3. minimize public nonidentity edges;
4. maximize retained degree-four maxima;
5. choose the lexicographically least maximum list.

The per-cap producer node cap is `2,000,000`. The bound is the minimum of group
size, the global pair-output union, and the incumbent support plus a
conflict-clique-cover pair-capacity bound.

Every canonical cap cell must satisfy all of the following:

- `primary_exact=true`;
- `full_objective_exact=true`;
- lower bound equals upper bound;
- `absolute_gap=0`;
- no remaining or serialized live frontier;
- termination is `full_objective_proved`;
- deterministic independent replay matches every objective and search field;
- a separately written depth-first primary proof finishes and matches the
  optimum.

One unresolved primary or secondary cell invalidates the entire 672-cell
matrix. Gap-bearing cells remain useful only as abstract optimizer controls.

## Curves and provenance

- q bit sizes: `5`, `6`, `7`, `8`
- curve seeds: `101`, `211`
- accepted model: `y^2 = x^3 + ax + b` over prime `p > 3`
- exact prime group order `q` with the requested bit length
- reject duplicate candidates, singular curves, wrong-bit or nonprime q,
  trace zero, anomalous trace one, `j=0`, and `j=1728`
- generator: least nonidentity affine point in canonical order
- frozen regression: `p=19,a=2,b=9,q=23,G=(0,3)`

The sampler is deterministic and generated, not statistically random. It must
record every draw and every applicable rejection reason. Duplicate draws are
retained explicitly. The verifier independently rederives the prime list,
hash-derived `(p,a,b)`, complete rejection transcript, accepted curve,
invariants, generator, and digest. The eight accepted `(p,a,b,q)` records must
be distinct across bit-seed pairs.

The frozen regression is implementation evidence only and is not a family
instance.

## Predicates

Every predicate selects exactly `B/2` admissible roots and includes both signs.

- `least_x_interval`: canonical integer x order.
- `mobius_interval`: `(u*x+v)/(x+w) mod p`, using the first nondegenerate
  domain-separated hash-derived map and deterministic pole removal.
- `two_mobius_union`: alternate through two independently derived Mobius
  rankings, skipping per-map poles and duplicate selected roots until full.
- `hash_x_null`: domain-separated SHA-256 ranking with exact replicate in
  `{0,1,2,3}`.

Coordinate rows require `null_replicate=null`. Hash-null rows require one exact
integer replicate in the frozen range. The verifier rederives every map,
nonce, determinant, ranking, pole list, alternating position, hash value,
selected root, root polynomial, point, sign pair, and selection digest.

## Canonical matrix

The exact order is:

```text
for bits in 5,6,7,8:
  for seed in 101,211:
    for B in 4,6,8:
      least_x_interval
      mobius_interval
      two_mobius_union
      hash_x_null replicate 0
      hash_x_null replicate 1
      hash_x_null replicate 2
      hash_x_null replicate 3
```

This is exactly 168 rows and 672 cap cells. Missing, extra, duplicate,
reordered, wrong-cap, wrong-node-budget, internally inconsistent, or
cross-seed-duplicate rows invalidate the document before interpretation.

## Frozen family gate

All arithmetic is exact rational arithmetic.

### Full-cap persistence

For each coordinate family and bit stratum, take the exact median of the six
full-cap `retained_to_balanced_raw` ratios from two seeds and three B values.
The family passes persistence only if all four medians are at least `1/4`.

### Matched-null advantage

For every curve-B pair and cap fraction `1/2` or `3/4`, take the exact
arithmetic mean of the middle two of the four precommitted null supports.
Duplicate null selections and equal support values remain in the four-value
sample; there is no resampling or deduplication.

Subtract this null median and `max(1,ceil(q/20))` from coordinate support. A
bit stratum passes when the exact median of its six threshold margins is
nonnegative. A fixed family-cap pair passes when at least three bit strata pass
and at least 18 of all 24 unthresholded coordinate-minus-null-median
comparisons are positive.

The gate tests six preregistered family-cap pairs and reports all winners. One
same family and one same cap fraction must pass across strata; half-cap evidence
cannot be spliced with three-quarter-cap evidence.

## Expansion and energy

For degrees `1`, `2`, `4`, and `8`, report exact support under degree-d
factor-base multisets.

`formal_multiset_collision_energy` squares output multiplicities when each
multiset is counted once. `ordered_tuple_additive_energy` first weights each
multiset by its multinomial number of orderings and then squares the resulting
output multiplicities. The verifier independently reconstructs both measures,
their witness totals, maxima, and histograms.

`balanced_raw_final_support` is the final pair support of the compiled balanced
A4 universe. `eight_fold_support` is the exact support of all degree-eight
factor-base multisets. Both denominators appear beside retention ratios.

## Accounting boundary

Version 3 removes producer operation-total claims. It emits only independently
reconstructible combinatorial cells, including multiset evaluations,
representative and parent-pair counts, graph checks, pair-output cells,
optimizer nodes, bound calls, selected maxima, public edges, source-table
entries, and final-pair cells. These are structural work, not CPU instructions,
field-operation totals, or a complete end-to-end cost.

Every cap creates a fresh model cache, so cap-local search receipts do not
depend on cap order. Public-model, private-audit, row-payload, and nested
per-cap canonical-JSON sizes are recomputed by the verifier. The nested sizes
overlap the row-level objects and are explicitly nonadditive.

Producer row and cap wall times are observational and checked only for finite,
nonnegative nesting. The producer makes no peak-memory claim. Any future
canonical execution must obtain generator and verifier wall time, peak RSS,
serialized output size, and memory traffic from the trusted external runner.
Verifier work must be reported as a separate role cost.

This protocol cannot support a fixed-curve preprocessing crossover claim.

## Controls

1. Reproduce the frozen predecessor and inherited hash-bound controls.
2. Exact-compare pair-conflict independence with direct closure on every
   frozen B=4 subset.
3. Exact-compare both optimizers with exhaustive abstract fixtures, including
   density and lexical ties.
4. Force and verify a nonzero optimizer gap at node cap zero.
5. Independently recount all four expansion degrees and both energy measures.
6. Independently rederive generated curve and predicate provenance.
7. Exercise singular, trace-zero, anomalous, `j=0`, `j=1728`, and duplicate
   draw records.
8. Reject illegal replicate bindings and mutations to Mobius nonce, objective
   order, representative table, source table, exactness, structural work, and
   bytes after refreshing enclosing digests.
9. Reject scalar-material additions and extra nested transcript fields under
   the closed schema.
10. Verify one frozen V3 document and reject an empty canonical document.
11. Exact-match producer and independent family gates on a synthetic complete
    168-row matrix; both must reject missing or unresolved cells.

## Positive criterion

After a separately approved canonical launch, all controls, 168 rows, and 672
cap cells must be valid and exact. At least one fixed family-cap pair must pass
both full-cap persistence and matched-null advantage exactly as frozen above.

This would be a toy coordinate-structure signal authorizing a larger compiler
and curve-family replication. It would not authorize an ECDLP claim.

## Falsification and narrowing

On one complete valid exact matrix, failure of every fixed family-cap pair
weakens or rejects this exact predicate-plus-compiler hypothesis. If every
family has full-cap median retention below `1/10` in at least three strata,
record the narrower `COLLAPSE` negative.

Neither result closes coordinate-specific SGGM embeddings in general. The next
positive question would be whether another representative compiler, formal
quotient, model transformation, or source-recoverable non-tree operation
changes the measured collision geometry.

## Budgets and stopping

Version 1 consumed 17 of 18 historical development curve rows. Version 3
authorizes no additional curve-family row. Unit, abstract graph,
generated-curve provenance, factor-base, and frozen p=19 row/document controls
are allowed.

Canonical budget remains:

```text
maximum_runs = 0
wall_clock_seconds_per_run = 0
total_cpu_hours = 0
maximum_memory_gb = 0
```

Fresh independent theory, accounting, and red-team GO on one committed V3
snapshot is necessary but not sufficient to launch. A separate hash-complete
execution plan and coordinator approval must follow before any budget change.

## Claim boundary

No exponent, relation yield, matrix rank, factor-base logarithm, individual
descent, preprocessing crossover, memory-bandwidth advantage, rho improvement,
deployment relevance, or prime-field ECDLP result is in scope. Fixed B values
are finite stress probes, not an `n^(1/5)` schedule.

## Reproduction command

No canonical reproduction command exists while `maximum_runs` is zero. The
current producer refuses both development family rows and canonical execution;
only unit and frozen-fixture functions are authorized for V3 preflight.
