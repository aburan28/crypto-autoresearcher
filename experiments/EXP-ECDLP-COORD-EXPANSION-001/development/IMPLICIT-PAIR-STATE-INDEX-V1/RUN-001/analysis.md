# Implicit Pair-State Index V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The independent verifier reproduces all 12 curve/family rows and all 36
target queries exactly. Recursive `D2+D2`, materialized `D4`, exact state-ID
pair indexing, and fingerprint widths 1, 2, 4, and 8 return identical
canonical four-source witness sets. Every accepted witness is replayed after
deferred state-pair expansion, and all five verifier mutations are rejected.

This is a fixed-curve data-structure result, not a generic-prime-field ECDLP
improvement.

## Charged frontier

Across the 36 target queries:

| Route | Advice words | Online work | `S*T^2/q` diagnostic |
|---|---:|---:|---:|
| recursive `D2+D2` | 58-220 | 630-3,886 | 24,156-213,195 |
| materialized `D4` | 390-4,282 | 36-104 | 644-2,972 |
| exact state-ID pair | 378-4,722 | 36-161 | 695-7,851 |
| fingerprint width 1 | 273-3,304 | 1,092-26,250 | 341,598-146,099,114 |
| fingerprint width 2 | 285-3,316 | 240-6,948 | 19,099-10,272,664 |
| fingerprint width 4 | 317-3,542 | 54-654 | 1,105-97,219 |
| fingerprint width 8 | 323-4,009 | 36-191 | 592-9,376 |

The exact state-ID pair route has mean advice `2,416.7` and mean online work
`70.7`, compared with `2,214` and `59.1` for materialized `D4`. It therefore
does remove most of the explicit pair index's four-source payload, but not
enough to dominate the already materialized exact support. Width-8 buckets
are nearly exact and have mean advice `2,051.8` with mean work `78.0`; the
small key saving does not offset deferred replay. Widths 1, 2, and 4 produce
mean state-sum rejection counts of approximately `1,817.7`, `452.5`, and
`28.1` respectively.

## Accounting

- immutable input SHA-256: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`;
- cells: 12; targets: 36;
- D2 build additions: 848;
- D4 build additions: 17,840;
- state-pair build additions: 9,289;
- producer wall time: approximately 0.18 seconds;
- producer peak RSS: 28,835,840 bytes;
- verifier wall time: approximately 0.19 seconds;
- verifier peak RSS: 29,933,568 bytes.

The pair index retains one record per unordered D2 state pair and charges two
state-ID words per record. D2 point keys and all D2 witness lists remain in
advice because they are needed for deferred witness lift. For fingerprint
routes, the state-pair sum is recomputed and charged for every bucket
candidate before witness expansion. All witness products and replay additions
are charged in online work.

## Interpretation

This tests the right payload-compression question: the pair record no longer
stores a four-source tuple. The result is still dominated by the exact
materialized D4 route. The reason is structural: materialized D4 collapses
all state pairs that share the same point sum, while the state-ID index keeps
each pair distinct and pays for deferred witness expansion.

The scoped negative is for explicit unordered state-pair indexing with
deferred witness lift and coordinate fingerprints. It does not rule out an
implicit algebraic representation that groups state pairs before advice is
materialized, or a target-conditioned root operator that computes such groups
without enumerating state pairs.

## Red-team checks

- exact state-ID hits agree with both recursive `D2+D2` and materialized `D4`;
- state-pair records are independently reconstructed from sorted D2 states;
- fingerprint collisions are rejected by recomputed state sums;
- deferred witness products are expanded and replayed, not assumed valid;
- the independent verifier reproduces curve arithmetic, D2/D4 states, pair
  records, indexes, queries, advice, and frontier metrics;
- protocol, producer hash, widths, a query metric, and the promotion boundary
  were mutated; every mutation was rejected.

## Next positive question

The remaining promising distinction is not another explicit pair table: can a
coordinate-adapted algebraic or divisor representation group many D2 pairs
before witness materialization, while retaining exact target-conditioned lift?
The next experiment should measure that grouping operation directly against
the materialized D4 frontier and stop before a larger campaign if its retained
state is merely a renamed pair table.
