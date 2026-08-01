# D4 Membership With Deferred Recovery V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`, with an exact finite
advice/query tradeoff.

The membership-only route retains exact D4 support keys and the D2 witness
table. It recovers witnesses only after a target complement passes membership.
An independent verifier reproduced all 12 cells and 36 target queries exactly
and rejected all five mutations.

## Charged frontier

| Route | Advice words | Online work | `S*T^2/q` diagnostic |
|---|---:|---:|---:|
| recursive `D2+D2` | 58-220 | 630-3,886 | 24,156-213,195 |
| materialized `D4` | 390-4,282 | 36-104 | 644-2,972 |
| membership plus recovery | 168-1,642 | 36-916 | 255-88,305 |

The membership route lowers retained advice in every tested row by removing
the D4 witness payload. Its mean advice is `868.5` versus `2,214` for
materialized D4. However, support-hit recovery raises mean online work to
`228.6` versus `59.1`, and the mean `S*T^2/q` diagnostic to `15,430.6` versus
`1,377.1`. Support hits range from zero to two per target query; recovery
scans 0-110 D2 states across the target rows.

This is a useful fixed-curve advice/query tradeoff, but it is not a net
frontier improvement under the charged diagnostic and does not change an
ECDLP exponent.

## Accounting

- immutable input SHA-256: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`;
- cells: 12; targets: 36;
- D2 build additions: 848;
- D4 build additions: 17,840;
- producer wall time: approximately 0.05 seconds;
- producer peak RSS: 26,935,296 bytes;
- verifier wall time: approximately 0.06 seconds;
- verifier peak RSS: 27,344,896 bytes.

The retained advice is `D2` point and witness advice plus two field elements
per D4 support point. Every support-hit D2 recovery scan, candidate witness
product, and accepted-witness replay is included in online work. The control
routes use the same affine operation proxy and target batch.

## Interpretation

This route isolates a real reusable fixed-curve option: support membership can
be much smaller than witness-bearing D4 advice when the target batch has few
hits. But exact witness recovery is not free. The tested rows do not show a
strictly better fully charged fixed-curve frontier, and the result has no
relation rank, individual-log descent, or cryptographic-scale evidence.

The scoped negative is for D4 support membership combined with recursive D2
recovery. It does not rule out a compact recovery certificate, a batched
recovery method, or an algebraic D4 support representation that avoids both
support enumeration and D2 scanning.

## Red-team checks

- support-only advice excludes all D4 witness tuples but retains the D2 table
  needed for recovery;
- each support hit triggers an explicitly counted D2 scan;
- each recovered witness is replayed against the exact complement;
- materialized D4 and recursive D2+D2 are measured on the same targets;
- independent replay checks all route hit sets and all accounting fields;
- protocol, producer hash, support-hit metric, cost metric, and promotion
  boundary mutations are rejected.

## Next positive question

Can recovery be batched across many target complements using a compact
certificate whose construction is smaller than materialized D4 and whose
application avoids one D2 scan per support hit? The next candidate must report
support-hit rate, recovery certificates, target batch size, and full charged
offline/online costs.
