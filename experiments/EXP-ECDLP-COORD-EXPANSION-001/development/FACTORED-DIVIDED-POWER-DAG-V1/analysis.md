# Factored Divided-Power DAG V1 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, scoped `NEGATIVE RESULT`.

The retained child-cycle tree performs exact rootless four-sum membership and
source-witness descent on the fixed toy curve. It passes a
representation-specific, unit-mixing record-count/scan diagnostic in 15 of 16
cells. It does not jointly improve state and exhaustive online work over
same-function exact-support or reduced-D2 indexes in any cell.

## Exact Run

- source commit: `ef497e796b032f904124a2294f126009230a2bd7`;
- source tree: `79211601e64ee9334eadf53baa2c57aa38d4918c`;
- fixed curve: `p=971`, `q=953`;
- `B in {2,3,4,5}`;
- x-interval, scalar-progression, random-x, and source-PRF-x families;
- 16 cells;
- 1,424 full-tree pair attempts;
- 208 recorded positive and 256 recorded negative queries;
- 464 reduced-D2 baseline query receipts;
- producer payload wall time/RSS: 0.291 seconds / 32,522,240 bytes;
- producer wrapper wall time/RSS: 0.37 seconds / 32,538,624 bytes;
- verifier wrapper wall time/RSS: 6.36 seconds / 56,197,120 bytes;
- 1,611 stored routes independently checked;
- 432 root-support targets independently descended;
- 15,248 exhaustive subgroup-target queries independently reconstructed;
- 20 targeted artifact mutations rejected;
- zero coefficient, route, query, operation, state, or baseline mismatch.

The verifier independently rebuilds every node cycle and coefficient, checks
every retained route, removes the root cycle from its query object, exhausts
all 953 subgroup targets in every cell, replays the recorded samples,
reconstructs all same-function baselines, and derives the reported operation
and state fields.

## Rootless Query Boundary

The full root cycle is constructed only to authenticate the experiment and
select deterministic positive targets. Before online queries, the query root
is replaced by an object with no cycle map. A query must:

1. enumerate root degree splits;
2. scan a child cycle and look up the complement in the other child;
3. recurse through child cycle maps;
4. terminate at leaf source indices;
5. replay the four source points.

Thus the online route does not use a root-support membership or route lookup.
The full build peak and retained rootless advice are reported separately.

## B=5 Results

`sqrt(q)=30.87`. Query maxima below are exhaustive over all 953 subgroup
targets.

| family | retained records | retained logical words | build-peak records | build-peak words | DAG scans | support hash words | sorted comparisons | D2 records | D2 words | D2 scans |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x-interval | 90 | 489 | 215 | 1,278 | 17 | 483 | 7 | 15 | 75 | 15 |
| scalar progression | 90 | 489 | 159 | 900 | 11 | 201 | 5 | 13 | 65 | 13 |
| random-x | 90 | 489 | 216 | 1,285 | 17 | 490 | 7 | 15 | 75 | 15 |
| source-PRF-x | 90 | 489 | 195 | 1,143 | 17 | 383 | 6 | 14 | 70 | 14 |

The retained canonical JSON payload is 5,653–5,672 bytes. This is a
serialization diagnostic, not a language-independent memory lower bound.
Full-build canonical JSON is 9,783–13,202 bytes. Every `B=5` build charges 241
curve additions, including 50 leaf scalar steps; online sort items, route
copies, and witness replay are reported separately.

## Semantic Construction Result

The child-cycle representation is a genuine exact route index:

- it works without a root-support prefilter;
- positive targets recover four nondecreasing source indices;
- negative targets are rejected by the same rootless procedure;
- infinity, inverse pairs, doubling, and repeated indices remain typed;
- its exhaustive worst point scans are below `sqrt(q)`;
- its retained record count is below the fully expanded oriented-polynomial
  base-field-element count in 15 cells.

This is useful evidence that recursive addition-law state can support exact
decomposition without materializing the final support at query time.

## Why It Does Not Promote

The preregistered diagnostic compares cycle records with base-field
coefficients. Those units are not commensurate, so its 15 passes are not
positive algorithmic signals. The post-hoc same-function gate is false in
every cell.

At `B=5`, reduced-D2 MITM stores only 13–15 point records and 65–75 logical
words. Its exhaustive worst scan count is 13–15, versus 11–17 for the DAG.
The DAG gains two scans only in the scalar control; it loses two scans for
x-interval and random-x and three for source-PRF-x, while using 6.5–7.5 times
as many logical words.

An exact support hash returns a stored source route with one expected lookup.
A sorted exact support uses only 5–7 comparisons. Building those indexes has
different offline costs, but the full DAG build peak is also charged and
reaches 159–216 records and 900–1,285 logical words at `B=5`.

The numerical rho/BSGS values are reported only as typed references. Group
operations, group records, point-cycle records, and base-field words are not
treated as commensurate.

## Strongest Valid Conclusion

> On the fixed `q=953` cells, a balanced source-partition divided-power tree
> can discard its root cycle and still recover exact canonical four-sum
> witnesses with exhaustive maxima of 11–17 point scans at `B=5`. However,
> explicit child-cycle
> retention does not beat the same-function reduced-D2 MITM or exact-support
> indexes when state and online work are reported together.

This is a scoped negative for the explicit child-support representation, not
for recursive addition circuits, compressed algebraic joins, batch
decomposition, or index calculus.

No ECDLP relation compiler, exponent fit, relation rank, individual logarithm,
many-target amortization, or fixed-curve preprocessing frontier is established.

## Next Concrete Action

Do not scale this explicit-support tree unchanged. The next useful experiment
should replace at least one child support map with a coordinate-specific
compressed predicate or transposed batch operator:

1. retain the rootless query and source-witness contract;
2. compare against reduced-D2 MITM and exact support from the start;
3. process a preregistered target batch and charge shared scans, traffic, and
   advice;
4. require the compressed child representation to use fewer than the D2
   baseline's logical words or to lower amortized scans enough to compensate;
5. only then integrate the output with typed `A+4R` relation rank.
