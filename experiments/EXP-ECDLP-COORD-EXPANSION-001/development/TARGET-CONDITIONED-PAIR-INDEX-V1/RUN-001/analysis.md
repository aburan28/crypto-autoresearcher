# Target-Conditioned Pair Index V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The producer and independently implemented verifier agree on all 12
curve/family cells and all 36 target queries. Recursive `D2+D2`, materialized
`D4`, exact pair indexing, and all four coordinate fingerprint widths return
the same canonical four-source witness sets. The verifier replay is exact and
rejects all five deterministic mutations.

This is an exact fixed-curve representation result, not a generic-prime-field
ECDLP improvement.

## Charged frontier

Across the 36 target queries:

| Route | Advice words | Online work | `S*T^2/q` diagnostic |
|---|---:|---:|---:|
| recursive `D2+D2` | 58-220 | 630-3,886 | 24,156-213,195 |
| materialized `D4` | 390-4,282 | 36-104 | 644-2,972 |
| exact pair index | 594-7,582 | 36-161 | 1,088-12,609 |
| fingerprint width 1 | 484-6,164 | 3,671-82,982 | 6,844,177-2,723,825,962 |
| fingerprint width 2 | 496-6,176 | 669-21,859 | 232,938-189,372,450 |
| fingerprint width 4 | 533-6,402 | 80-1,928 | 3,579-1,527,139 |
| fingerprint width 8 | 539-6,869 | 36-161 | 984-11,419 |

The exact pair index does avoid the recursive scan and has mean online work
`70.7` versus `1,940.0` for recursive `D2+D2`, but it retains mean advice
`3,829` versus `141.2`. Its `S*T^2/q` diagnostic is worse than the
materialized `D4` route and better than the recursive route only in some small
rows. Width-8 fingerprints are close to exact coordinate keys: they save a
small amount of key material but do not change the query frontier. Coarser
fingerprints introduce many rejected candidates; the mean rejected counts are
approximately `1,817.7`, `452.5`, `28.1`, and `0.03` for widths 1, 2, 4, and 8.

## Accounting

- immutable input SHA-256: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`;
- cells: 12; targets: 36;
- D2 build additions: 848;
- D4 build additions: 17,840;
- pair-index build additions: 9,289;
- producer wall time: approximately 0.27 seconds;
- producer peak RSS: 29,376,512 bytes;
- verifier wall time: approximately 0.30 seconds;
- verifier peak RSS: 30,343,168 bytes.

The pair-index build retains every unordered D2-state pair and every product
of their witness records. The four source indices per pair record are charged
in advice. Candidate replay additions are charged in online work, including
rejected coordinate collisions.

## Interpretation

This experiment validates a real target-conditioned nonlinear lookup shape:
the target computes `C=T-A`, a coordinate fingerprint selects a bucket, and
full elliptic replay restores exactness. It does not preserve D2-scale advice.
The pair-record multiplicity makes the representation larger than the
recursive D2 index and, in these cells, larger than materialized D4. The
coordinate fingerprint therefore changes the scan organization but not the
fixed-curve frontier needed for an index-calculus compiler.

The scoped negative is for this pair-sum materialization and fingerprint
family. It does not rule out an implicit pair index, a compositional query
operator, or a source-adapted nonlinear selector that avoids retaining one
record per D2 pair.

## Red-team checks

- exact route equality was checked against both recursive `D2+D2` and
  materialized `D4`;
- false fingerprint candidates were counted and replay-rejected rather than
  silently accepted;
- all witness records were retained and all accepted witnesses were replayed;
- the verifier independently implements curve addition, state generation,
  pair construction, indexing, queries, and advice accounting;
- protocol, producer hash, widths, a metric row, and the promotion boundary
  were mutated; every mutation was rejected.

## Next positive question

Can a target-conditioned operator compute or filter pair sums without storing
one full witness-bearing record per D2 pair? The next candidate must expose a
compositional index or implicit collision operator and must beat materialized
D4 on the same charged advice/query/build frontier before any larger sweep.
