# Independent Theory Review

Reviewer task `019fafa3-7029-7aa0-9553-04025a6baeca` audited exact commit
`30793d7d676014f8c044073d7b12e679c4ed694f`.

Decision: `REVISE`.

The review independently replayed 15 rows, 178 listed relations, and 338
supported descents; verified the three group orders; and recomputed quotient
rank `|R|+1`, full-matrix nullity one, and no extra kernel in every recorded
transcript.

The exact scoped theorem is:

> Fixed `A+4R` weight guarantees the gauge direction
> `(-4,0,1,...,1)`. Conditional on quotient rank `|R|+1`, it is the complete
> kernel, and every gauge-compatible target row is exactly evaluable.

Complete kernel, support, and rank are empirical for these toy transcripts.
The observed support range `0.3403-0.4548` is not an asymptotic constant-support
theorem.

A compressed-`4R` route additionally requires constant or charged support,
rank-preserving witness selection, total target work including the complete
`A` scan and witness lift, charged advice construction and writes, sparse
linear algebra, and randomized arbitrary-target descent.

The generic `ST^2` comparison is model-bound and neither rules out nor
validates named elliptic-coordinate structure.
