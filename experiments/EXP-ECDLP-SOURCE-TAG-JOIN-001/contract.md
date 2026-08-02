# Experiment Contract v2: source-tagged recursive join

## Status and boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

The v1 contract is preserved as `contract-v1.md`. Independent pre-run review
classified its single-null design and strict materialized-D4 gate `REVISE`.
V2 separates a source-correlation test from a useful-compiler test and adds the
missing exact D2-complement baseline and compositional source null.

This experiment runs only on generated toy prime-order curves. It tests whether
public factor-base provenance helps compile an exact point-decomposition join.
It is not an ECDLP break, an exponent result, or evidence about deployed keys.
A development pass may authorize a replicated successor only; it may not be
promoted directly.

## Hypothesis

For a coordinate-constructed, sign-complete factor base, a compositional tag
derived from a symmetry-bound `D2 = F + F` witness makes the inverse
`D2 + D2` join more predictable than random tag assignments that preserve tag
occupancy, point-negation symmetry, and exact D2 witness multiplicity.

## Null hypothesis

After exact route payload, candidate verification, memory traffic, materialized
`D4`, equal-advice fixed-base BSGS, and Pollard-rho scale are charged, every
tested source tag is indistinguishable from its matched tag-shuffle null or is
strictly worse than a generic or materialized baseline.

## Parameters

- curve family: seeded short-Weierstrass curves over prime fields;
- group: prime order and cofactor one;
- exclusions: trace in `{0,1}`, `j` in `{0,1728}`, singular curves, and repeated
  fields;
- factor bases: `x_interval`, `square_map`, `rational_union`, `random_x`, and
  `random_scalar`;
- factor-base size: the exact sign-complete five-term occupancy rule inherited
  from `EXP-ECDLP-FIXED-COMPILER-001`;
- source-tag families: `ordinal_sum`, `source_x_sum`, and `parameter_mix`;
- witness policies: `symmetry_lex` and `symmetry_hash`;
- public output routers: `x_interval` and `random_x_fiber`;
- compositional null: `source_record_permutation`, with tags recomputed from
  permuted public source records;
- exact-margin null: `multiplicity_orbit_shuffle`, stratified by multiplicity,
  inversion-orbit size, and selected-witness class;
- ineligible positive control: `scalar_interval` for both D2 tags and outputs.

The `random_scalar` constructor emits neither sampled nor canonical scalars.
Its public source records contain only the sanitized family and ordinal. Hidden
scalar indices are allowed only in the positive control, relation audit, and
final scalar verification.

## Symmetry-bound D2 witnesses

Factor points are stored as sign pairs `(2u, 2u+1)`. For every D2 point `A`,
enumerate all unordered factor-index witnesses. Pair `A` with `-A`; choose a
canonical representative of that inversion orbit and bind one witness under a
public policy. The witness for the other point is the factor-wise negation of
the chosen witness. The identity is handled as its own orbit.

For a bound witness `(i,j)`, write `u=floor(i/2)`, `v=floor(j/2)`, and
`sigma=(i mod 2) xor (j mod 2)`. Each eligible tag is a public, symmetric
function of `u`, `v`, `sigma`, and sanitized source data. Consequently the
eligible tags satisfy `tag(A)=tag(-A)`.

## Exact compiled object

For each tag assignment `tau` and output router `h`, compile

`R[(h(a+b), tau(a))] = {tau(b) : a,b in D2}`.

Store:

1. public factor points and sanitized source records;
2. unique D2 points, symmetry-bound pair witnesses, exact multiplicities, and
   assigned tags;
3. tag-bucket directories and distinct route triples;
4. public router and tag parameters.

Do not store D4 point keys in candidate advice. Query a D4 target `Y` by
scanning `a in D2`, reading only right-tag buckets named by
`R[(h(Y),tau(a))]`, and verifying every candidate EC addition. Query a D5
target by scanning `f in F` and invoking the D4 query on `Y=Q-f`.

## Null constructions

### Compositional source null

Permute complete sanitized source records among sign-complete factor fibers,
leave the EC points and witnesses fixed, and recompute every D2 tag with the
candidate's unchanged composition rule. This preserves the source-record
multiset and source composition while breaking its alignment with EC semantics.

### Exact-margin null

For each candidate assignment:

1. partition D2 into point-negation orbits;
2. stratify those orbits by exact unordered D2 witness multiplicity, orbit
   size, and selected-witness class (repeated leaf, inverse pair, or distinct
   fibers with equal/mixed signs);
3. shuffle whole candidate tag records only within a stratum;
4. assign one tag to both members of a size-two inversion orbit;
5. preserve the identity orbit and publish the permutation seed.

The exact-margin null must preserve the candidate tag histogram, occupied-tag
count, point-negation symmetry, D2 multiplicity by tag, and witness class by
tag. The compositional null need not preserve the resulting tag histogram, but
must preserve the complete source-record multiset and recompute tags rather
than shuffle completed D2 labels. Both nulls use the same factor-base points,
output router, target schedule, and advice encoding. Nulls with insufficient
effective movement are disclosed and cannot support a positive claim.

## Metrics

- `|F|`, `|D2|`, `|D4|`, `|D5|`, and exact D5 success probability;
- D2 multiplicity histogram and inversion-orbit checks;
- tag histogram, multiplicity-by-tag and witness-class-by-tag digests, null
  moved-point/fiber fractions;
- occupied tag/output buckets, route keys, route triples, fanout, and entropy;
- exact supported/random D4 and D5 success;
- route probes, bucket reads, tag reads, point reads, witness reads, EC
  additions, field operations, and logical bytes read;
- factor-base, D2, D4, tag, route, and total offline work;
- payload-bit lower estimate, canonical serialized bytes, and Python deep bytes;
- full online advice including factor-base logarithms;
- exact D2-complement hash lookup, materialized-D4 query, and advice;
- fixed-base BSGS at the identical candidate advice-bit budget;
- matched Pollard-rho group-operation scale;
- exploratory log-log slopes over at least three sizes, marked ineligible when
  fixed tag counts saturate the `r^3` route universe.

Exhaustive scalar indexing, full D4/D5 support construction, witness checking,
and private target scalars are audit-only and reported separately.

## Controls

### Positive control

`scalar_interval` uses the private toy scalar index for both D2 and output
buckets. It should produce narrower exact routes than shuffled public tags. It
is ineligible because evaluating it on an arbitrary target is the DLP.

### Negative controls

- at least four seeds for each null family in development and eight in a
  canonical configuration;
- coordinate-null factor bases `random_x` and `random_scalar`;
- `random_x_fiber` output routing, which preserves `h(P)=h(-P)`;
- explicit materialized D4;
- exact packed-hash D2 complement lookup;
- equal-advice fixed-base BSGS;
- route deletion, tag mutation, target mutation, and source-scalar injection
  tests.

## Development configuration

- bit sizes: `10, 12, 14`;
- curve seed: `3317584535`, derived before target generation from
  `SHA256("EXP-ECDLP-SOURCE-TAG-JOIN-001-v2")`;
- factor-base families: all five listed families;
- witness policies: both listed policies;
- source tags: all three listed tags;
- tag counts: `4, 8, 16`;
- public output routers: `x_interval`;
- matched-null seeds: four disclosed seeds;
- supported/random target samples: four per schedule;
- descent challenges: one, with eight attempts;
- rho trials: one.

This configuration is explicitly noncanonical. A canonical run requires a
separate source freeze, independent source review, three curve seeds, eight
null seeds, both output routers, explicit user approval, and the CLI's separate
`--authorize-canonical` flag. The flag is not itself evidence of approval.

## Success criteria

### Structural source-correlation gate

A candidate `(family, witness policy, source tag, tag count, output router)` may
advance to an outer-routing or batch successor only if, at every tested size on
at least two curve seeds:

1. deterministic replay and independent affine/order/support/witness checks
   pass with no route false negatives;
2. the scalar control is narrower than its public comparisons;
3. every null preserves its contracted invariants and moves at least `50%` of
   its movable D2 points or factor fibers;
4. candidate payload bits and route triples are each at most `0.8x` every
   effective matched null;
5. candidate supported-D4, supported-D5, and random-D5 point reads and EC
   additions are each at most `0.8x` every effective matched null;
6. canonical serialized bytes and deep bytes are at most `1.25x` every null;
7. the route universe is not saturated at `r^3` triples;
8. no hidden scalar metadata enters an eligible tag, route, or payload.

A structural pass establishes only a source/addition correlation in this toy
model. It does not establish a useful compiler.

### Useful-compiler gate

In addition to the structural gate, a useful-compiler row must:

1. improve both exact-D2-complement `S*T^2` diagnostics by at least `20%`,
   comparing supported query with supported query and randomized descent with
   randomized descent; query advice excludes factor logs while descent advice
   includes them;
2. lie below two separate measured envelopes: a decomposition envelope over
   exact D2, partial D4, and any full D4 that fits the candidate advice on
   identical supported targets, and a DLP envelope over their randomized
   descents plus fixed-base BSGS;
3. beat a partial-D4 cache in online work when that baseline uses no more advice;
4. disclose that strict online dominance over full materialized D4 is impossible
   under the unchanged outer scan; absent an outer-routing, batching, exact-
   translator, or different-cost-model escape, classify any win only as a
   memory-capped Pareto point or storage/query tradeoff;
5. compare complete descent worst-case work against BSGS, charging every frozen
   attempt, scalar multiplication, target shift, failed query, and final query;
6. solve and independently verify every configured development descent
   challenge; descent outcomes do not participate in the structural gate;
7. reconnect rank, linear algebra, and individual descent using the candidate's
   returned witnesses before any ECDLP-level claim.

Toy slopes are diagnostics only. No fitted exponent from this development run
is eligible for promotion.

## Falsification criterion

Failure of exact coverage, witness validity, null invariants, target matching,
or scalar separation invalidates the implementation. Failure of the remaining
gates is a scoped negative for the tested source tags, witness policies, output
routers, factor bases, and toy regime. It is not a negative result for index
calculus or source-aware decomposition generally.

## Reproduction command

```bash
PYTHONPATH=src python3 -B \
  experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/src/source_tag_join.py \
  --bit-sizes 10 12 14 \
  --seeds 3317584535 \
  --families x_interval square_map rational_union random_x random_scalar \
  --witness-policies symmetry_lex symmetry_hash \
  --source-tags ordinal_sum source_x_sum parameter_mix \
  --tag-counts 4 8 16 \
  --output-routers x_interval \
  --null-seeds 7301 7307 7321 7331 \
  --query-samples 4 \
  --descent-challenges 1 \
  --descent-attempt-limit 8 \
  --rho-trials 1 \
  --output experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/development/DEV-SOURCE-TAG-JOIN-001/raw-result.json
```
