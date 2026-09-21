# Experiment Contract: Factored Divided-Power DAG V1

## Hypothesis

A balanced divided-power DAG for the canonical four-sum cycle can answer exact
point membership and return source witnesses with less online work than
scanning the full D4 support, while retaining fewer records than an expanded
oriented characteristic polynomial.

This is a fixed-factor-base membership index. It is not yet an ECDLP
relation compiler or a generic fixed-curve preprocessing break.

## Null Hypotheses

1. The root degree-four cycle differs from canonical four-tuple enumeration.
2. Recursive membership returns false positives, false negatives, or invalid
   source witnesses.
3. Internal retained state is at least as large as the expanded polynomial or
   explicit D4 support without online benefit.
4. Online child scans remain at or above `sqrt(q)`.
5. Favorable behavior appears only for the scalar control.

## Parameters

- fixed recorded curve `p=971`, `q=953`;
- nested `B in {2,3,4,5}`;
- x-interval, random-x, source-PRF-x, scalar-progression control;
- canonical source-multiset semantics only;
- balanced contiguous factor-base tree;
- truncated divided-power degree `0..4`;
- deterministic positive and negative point queries.

## DAG Definition

For leaf point `R_i`, store typed cycles

`G_i[k]=[k R_i]` for `k=0..4`.

For internal node with children `L,R`, store

`G_v[k]=sum_(a+b=k) add_*(G_L[a] x G_R[b])`.

Every cycle retains multiplicity and a first source-index witness. The root
`G_root[4]` must equal the canonical four-sum pushforward coefficient for
coefficient.

## Membership and Descent

To query `(node,k,Q)`:

1. enumerate degree splits `a+b=k`;
2. scan the smaller child support;
3. compute the required complementary point;
4. look it up in the other child support;
5. recurse into both children;
6. combine and replay the source indices.

Cache only immutable node cycles; do not memoize target answers across the
reported one-target query. The root cycle is used only to authenticate the
build and select deterministic test targets. It is removed from the online
query object. Online membership starts from the two child subtrees without a
root-support prefilter.

At the fixed toy `q`, exhaust every subgroup target and use the true maximum
query work for all gates. The 16 positive and 16 negative receipts remain
deterministic human-sized samples only.

## Metrics

- full-build DAG nodes/edges and degree-specific support/route counts;
- build-peak versus rootless retained-advice records, point fields, routes,
  logical words, and canonical JSON bytes;
- build pair attempts, leaf scalar steps, curve operations, writes, and hash
  lookups;
- root support/multiplicity/witness digests;
- online split attempts, point scans, curve operations, lookups, recursion
  nodes, sort calls/items, route-index copies, and witness replay;
- positive/negative success;
- exact support hash/sorted indexes and reduced-D2 MITM with source routes;
- expanded oriented-polynomial state and separately typed rho/BSGS numerical
  references that are not treated as commensurate storage;
- `S*T^2/q` diagnostic using retained records `S` and worst online scans `T`,
  labeled as a membership-subproblem diagnostic only.

Canonical JSON bytes are serialization diagnostics. Logical words exclude
Python object and hash-table overhead and must not be presented as measured
peak bytes.

## Controls

- root cycle equals the scheme-aware canonical oracle exactly;
- all internal cycle degrees equal their divided-power route counts;
- scalar progression shows expected support compression;
- every positive descends to a valid nondecreasing source tuple;
- every negative is rejected;
- doubling, repeated indices, inverse pairs, and infinity remain typed.

## Success Criterion

Every cycle, query, and witness passes an independent verifier. A positive
algorithmic signal additionally requires both:

- retained records below expanded oriented-polynomial base-field elements;
- worst one-target point scans below `sqrt(q)`.

This gate applies only to canonical D4 membership on the fixed toy factor
base.

A post-hoc same-function diagnostic additionally asks whether the retained
DAG jointly improves state and online work over the exact support indexes and
reduced-D2 MITM. It is not the preregistered promotion gate.

## Falsification Criterion

Any semantic mismatch invalidates the run. If the signal gate fails, preserve
a scoped negative for this factored DAG. If it passes, the next required gate
is integration with typed `A+4R` relation rank, charged construction,
many-target amortization, and held-out descent.

## Reproduction Command

```bash
python3 src/factored_divided_power_dag.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families x_interval scalar_progression_control random_x source_prf_x \
  --b-values 2 3 4 5
```
