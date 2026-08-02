# Experiment Contract: coordinate-routed compressed join

## Status and boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

This is an authorized experiment on generated toy prime-order curves. A successful router is a point-decomposition data-structure signal, not an ECDLP break. A fitted exponent claim is prohibited until the relation, rank, linear algebra, descent, preprocessing, storage, and memory-traffic layers are restored and independently verified.

## Hypothesis

A public coordinate feature can compress the exact `D2 + D2` witness join below a matched random-label router without moving the saved work into false-candidate verification, and the resulting full `4+1` query can beat fixed-base BSGS under the same advice-bit budget.

## Null hypothesis

Every tested public feature has random-like route entropy or loses after exact candidate verification and equal-advice BSGS are charged.

## Restricted theorem used by this experiment

If `G` has prime order `q` and `H` is a finite group with `|H| < q`, every group homomorphism `G -> H` is trivial. Therefore an exact port of integer modular routing through a smaller group quotient cannot provide a nonconstant bucket map on `G`. This statement does not cover nonlinear coordinate maps, lossy sketches, multi-valued routers, batch algorithms, or larger auxiliary representations.

The proof and its limitations are in `theory.md`.

## Parameters

- curve family: seeded short-Weierstrass curves over prime fields;
- group: prime order, cofactor one;
- exclusions: trace in `{0,1}`, `j` in `{0,1728}`, singular curves, repeated fields;
- field policy: `p mod 4 = 3` only for deterministic square roots; no selection on `p-1` smoothness;
- factor-base size: the exact sign-complete five-term occupancy rule inherited from `EXP-ECDLP-FIXED-COMPILER-001`;
- candidate factor bases: `x_interval`, `square_map`, and `rational_union`;
- matched factor-base nulls: `random_x` and `random_scalar`;
- bucket counts: powers of two, always reported against `|D2|`;
- public routers: `x_mod`, `x_interval`, `xy_linear_mod`, and `legendre_vector`;
- negative router control: `random_label`;
- ineligible positive router control: `scalar_interval`.

The scalar control may enumerate the complete toy group to recover point indices, but those indices are private audit material and must never enter a candidate payload or promotion decision.

## Exact objects

Let `F` be the sign-complete factor base.

1. Build the unique support `D2 = F + F`, retaining one canonical unordered pair witness per point.
2. Enumerate every ordered pair `(a,b) in D2^2` once and compute `y=a+b`.
3. For each router `h:G->[r]`, build the exact reverse relation

   `R_h[(h(y),h(a))] = {h(b) : a+b=y}`.

4. Store `D2` points, pair witnesses, bucket membership, and the distinct route triples. Do not store `y` point keys in the router candidate.
5. Query a four-sum target `Y` by scanning `a in D2`, then only points in the right buckets named by `R_h[(h(Y),h(a))]`, verifying every candidate EC addition.
6. Query a five-term target `Q` by scanning `f in F`, setting `Y=Q-f`, and invoking the four-sum query.

The route is exact for the enumerated `D2`: false positives are permitted and charged; false negatives are not.

## Metrics

- `|F|`, `|D2|`, `|D4|`, and `|D5|`;
- D2 and D4 witness multiplicity histograms;
- occupied source and output buckets;
- distinct route triples and reverse-route fanout;
- conditional route width and entropy;
- exact supported-target success;
- candidate EC additions, route probes, bucket reads, point reads, and witness reads;
- offline EC additions and coordinate-hash work;
- payload-bit lower estimate, canonical serialized bytes, and Python deep bytes;
- full advice including factor-base logarithms;
- materialized-D4 and brute-pair baselines;
- fixed-base BSGS at the identical full advice budget;
- matched Pollard-rho scale;
- exploratory log-log slopes over at least three sizes.

Attack work and audit work must be separate. Exhaustive hidden-scalar recovery, support verification, and private target scalars are audit-only.

## Controls

### Positive control

`scalar_interval` buckets points by their audited scalar position around the prime-order cycle. It should exhibit narrow addition routes. It is ineligible because computing the feature on an arbitrary target is the DLP itself.

### Negative controls

- `random_label`: deterministic public point hash at identical `r`;
- `random_x` and `random_scalar`: matched-cardinality factor bases;
- `pair_scan`: no routing compression;
- mutation tests that delete a route, alter a D2 witness, or relabel a target.

## Development configuration

- bit sizes: `10, 12, 14`;
- seeds: one disclosed seed;
- factor-base families: `x_interval`, `random_x`, `random_scalar`;
- routers: all candidates and controls;
- bucket counts: `4, 8, 16, 32`, capped to the next power of two above `|D2|`;
- random online targets: `16` per row;
- supported D4 targets: `16` per row;
- supported D5 targets: `16` per row;
- rho trials: `1`.

This configuration is explicitly noncanonical. A canonical configuration requires a separate source freeze, independent review, three seeds, and explicit approval.

## Success criterion

A public coordinate router may be routed to a larger successor only if, at every tested size on at least two seeds:

1. all returned D4 and D5 witnesses verify and exact route coverage has no false negatives;
2. the positive scalar control has lower route width than `random_label`;
3. route payload bits are at most `0.8x` `random_label` at the same bucket count;
4. average verified candidate additions on both supported and random queries are at most `0.8x` `random_label`;
5. serialized and deep-memory measurements do not exceed `1.25x` their matched nulls;
6. the complete D5 query beats both sampled-average and deterministic-worst-case fixed-base BSGS under the same full advice-bit budget;
7. no hidden scalar metadata enters the candidate path.

## Falsification criterion

Failure of items 1 or 2 invalidates the experiment implementation. Failure of items 3 through 7 is a scoped negative for the tested router and bucket regime, not for coordinate compilers generally.

## Reproduction command

```bash
PYTHONPATH=src python3 -B experiments/EXP-ECDLP-COMPRESSED-JOIN-001/src/compressed_join.py \
  --bit-sizes 10 12 14 \
  --seeds 3572001 \
  --families x_interval random_x random_scalar \
  --bucket-counts 4 8 16 32 \
  --query-samples 16 \
  --rho-trials 1 \
  --output experiments/EXP-ECDLP-COMPRESSED-JOIN-001/development/DEV-COMPRESSED-JOIN-001/raw-result.json
```
