# Experiment Contract: source-tagged recursive join

## Status and boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

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
- matched null: `multiplicity_orbit_shuffle`, with independent disclosed seeds;
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

## Matched-null construction

For each candidate assignment:

1. partition D2 into point-negation orbits;
2. stratify those orbits by exact unordered D2 witness multiplicity and orbit
   size;
3. shuffle whole candidate tag records only within a stratum;
4. assign one tag to both members of a size-two inversion orbit;
5. preserve the identity orbit and publish the permutation seed.

Every null must exactly preserve the candidate tag histogram, occupied-tag
count, point-negation symmetry, D2 multiplicity by tag, factor-base instance,
output router, target schedule, and advice encoding. Nulls with no effective
tag movement are disclosed and cannot support a positive claim.

## Metrics

- `|F|`, `|D2|`, `|D4|`, `|D5|`, and exact D5 success probability;
- D2 multiplicity histogram and inversion-orbit checks;
- tag histogram, multiplicity-by-tag digest, null moved-point fraction;
- occupied tag/output buckets, route keys, route triples, fanout, and entropy;
- exact supported/random D4 and D5 success;
- route probes, bucket reads, tag reads, point reads, witness reads, EC
  additions, field operations, and logical bytes read;
- factor-base, D2, D4, tag, route, and total offline work;
- payload-bit lower estimate, canonical serialized bytes, and Python deep bytes;
- full online advice including factor-base logarithms;
- materialized-D4 query and advice;
- fixed-base BSGS at the identical candidate advice-bit budget;
- matched Pollard-rho group-operation scale;
- exploratory log-log slopes over at least three sizes.

Exhaustive scalar indexing, full D4/D5 support construction, witness checking,
and private target scalars are audit-only and reported separately.

## Controls

### Positive control

`scalar_interval` uses the private toy scalar index for both D2 and output
buckets. It should produce narrower exact routes than shuffled public tags. It
is ineligible because evaluating it on an arbitrary target is the DLP.

### Negative controls

- at least four `multiplicity_orbit_shuffle` seeds in development and eight in
  a canonical configuration;
- coordinate-null factor bases `random_x` and `random_scalar`;
- `random_x_fiber` output routing, which preserves `h(P)=h(-P)`;
- explicit materialized D4;
- equal-advice fixed-base BSGS;
- route deletion, tag mutation, target mutation, and source-scalar injection
  tests.

## Development configuration

- bit sizes: `10, 12, 14`;
- seeds: one disclosed seed;
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
null seeds, both output routers, and explicit user approval.

## Success criterion

A candidate `(family, witness policy, source tag, tag count, output router)` may
advance only if, at every tested size on at least two curve seeds:

1. deterministic replay and independent affine/order/support/witness checks
   pass with no route false negatives;
2. the scalar control is narrower than its public comparisons;
3. every matched null preserves the contracted invariants and moves at least
   `50%` of movable D2 points;
4. candidate payload bits and route triples are each at most `0.8x` every
   effective matched null;
5. candidate supported-D4, supported-D5, and random-D5 point reads and EC
   additions are each at most `0.8x` every effective matched null;
6. canonical serialized bytes and deep bytes are at most `1.25x` every null;
7. the full candidate has both lower advice and lower supported-D5 online work
   than materialized D4;
8. the candidate descent beats both sampled-average and deterministic
   worst-case fixed-base BSGS under equal advice;
9. total fitted online exponent is below `0.5`, with offline work, storage, and
   memory traffic reported separately;
10. no hidden scalar metadata enters an eligible tag, route, or payload.

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
  --seeds 3572001 \
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
