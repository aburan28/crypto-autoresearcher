# EXP-SGCP-EMBED-002 development result v1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, implementation evidence only.
Coordinator disposition: `REVISE`. No hypothesis state promotion is authorized.

## Verified execution

- 16/16 producer rows valid and producer-primary-exact.
- 16/16 full producer objectives exhausted their search frontier.
- 16/16 primary optima independently reconstructed and proved.
- Producer explored 3,124 nodes; independent verifier explored 3,288 nodes.
- Maximum eligible graph: 56 vertices; maximum conflict graph: 636 edges.
- Raw result: 513,609 bytes.
- Public row payloads: 51,993 bytes total.
- Charged private row audits: 439,796 bytes total.
- Sum/max deep row estimates: 2,439,976 / 472,951 bytes.
- Counted producer operations: 274,472 point additions, 202,829 field
  inversions, and 642,859 field multiplications.
- Producer wall time: 0.438s; maximum row: 0.183s.

These are direct Python development measurements, not canonical runner or peak
RSS receipts.

## Exact row observations

`R/raw` is retained balanced-final support over the predecessor-compatible raw
balanced-final support. `R/C` is retained support over constrained labels.
`vs-null` divides `R/C` by the matched row's single hash-x null value.

| q | B | family | R/raw | C/q | R/C | vs-null |
|---:|---:|---|---:|---:|---:|---:|
| 31 | 4 | least-x | 15/25 | 23/31 | 15/23 | 375/529 |
| 31 | 4 | Mobius | 25/31 | 27/31 | 25/27 | 625/621 |
| 31 | 4 | two-Mobius | 19/31 | 23/31 | 19/23 | 475/529 |
| 31 | 4 | hash-x null | 23/31 | 25/31 | 23/25 | 1 |
| 31 | 6 | least-x | 23/31 | 31/31 | 23/31 | 161/186 |
| 31 | 6 | Mobius | 25/31 | 28/31 | 25/28 | 25/24 |
| 31 | 6 | two-Mobius | 20/31 | 26/31 | 10/13 | 35/39 |
| 31 | 6 | hash-x null | 24/31 | 28/31 | 6/7 | 1 |
| 37 | 4 | least-x | 30/37 | 31/37 | 30/31 | 170/93 |
| 37 | 4 | Mobius | 17/37 | 23/37 | 17/23 | 289/207 |
| 37 | 4 | two-Mobius | 27/37 | 29/37 | 27/29 | 51/29 |
| 37 | 4 | hash-x null | 9/33 | 17/37 | 9/17 | 1 |
| 37 | 6 | least-x | 34/37 | 35/37 | 34/35 | 1088/875 |
| 37 | 6 | Mobius | 34/37 | 34/37 | 1 | 32/25 |
| 37 | 6 | two-Mobius | 25/37 | 29/37 | 25/29 | 32/29 |
| 37 | 6 | hash-x null | 25/37 | 32/37 | 25/32 | 1 |

## Interpretation

The valid embedding is not a one-fixture accident: every development row has
nonzero support and a fully proved primary optimum. That is useful
implementation evidence for the family harness.

The family effect is unstable. At q=31, the best Mobius `R/C` ratios are only
`625/621` and `25/24` of one null draw. At q=37, every coordinate row exceeds
that curve's single null by at least `32/29`, and the B=4 null itself retains
only `9/33` raw support. One null draw on one curve can easily create this
contrast. It is not evidence for the preregistered multi-curve effect.

Constrained density is already high: `17/37 <= delta <= 1`. Thus these toy
embeddings do not yet create a useful small-delta regime for the structured
generic-group bound. Persistence of final support alone is insufficient; the
next protocol must optimize and compare support at explicit matched density
budgets.

## Limits discovered

1. The v1 tie order maximizes retained maxima before minimizing constrained
   labels, so its reported `R/C` is not the optimum support-at-density frontier.
2. The field called `ordered_additive_energy` actually counts equal sums of
   unordered formal multisets; ordered-tuple energy needs multinomial weights.
3. Duplicate deterministic curve draws are skipped rather than logged.
4. A capped optimizer reports a frontier bound but does not serialize the live
   frontier states needed to replay that certificate.
5. The raw balanced-final denominator is not the full exact 8F support and must
   be named explicitly beside the separately measured 8F support.

## Decision

Preserve this run as a verified development result and revise the protocol
before any canonical launch. Version 2 should produce a density-budgeted
support frontier, corrected energy fields, complete draw provenance, and
replayable frontier certificates.
