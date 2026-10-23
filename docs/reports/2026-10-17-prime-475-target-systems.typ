#set page(paper: "a4", margin: 16mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Common target inputs for three 475-point prime bases

*Exact public known-answer input preparation and independent Sage replay,
2026-10-17 UTC.* Seven targets were derived from the certified 63-bit
prime-order curve fixture independently of the three factor bases. The full
record serializes 21 chained-S3 systems for summand counts `m=2…8`, plus the
coset's exact quadratic membership lifts. Target scalars are public correctness
data. There was no solver, relation, regularity or end-to-end measurement.

#image("2026-10-17-prime-475-target-systems.svg", width: 100%)

*Graph:* input monomial occurrences, log scale. Every arm has 475 actual
curve points. At `m=8`, direct coset/random/small-x systems have 118/3910/3902
input occurrences; the coset quadratic lift has 294 occurrences, 103 variables
and 104 equations. These counts do not predict solver work. The coset equation
also accepts 421 field x-values that do not lift to curve points.

== Verification and remaining measurement

Sage independently checked seven target scalar multiplications, all 21 direct
membership and S3 systems, and all coset lift gates against the immutable
record (SHA-256 `4bb75b65b843a4b7ce8c0b7d8521d80a95b958f061e0ddf516639296a15fb589`).
Two initial checker launches were blocked by Sage's cache permissions; the
unchanged inputs passed when the runtime could use its cache.

A Coordinator-approved bounded solver protocol is needed to measure solving
degree, time and memory, certified point relations, useful rank, linear
algebra, a separate unseen same-point target and matched rho, with all setup
and failed attempts charged. The installed msolve's 16-bit safety guard
prevents a valid direct run at this prime. Direct S8 has seven summands plus a
target; the eight-summand row here uses chained S3.

The companion Markdown report links exact inputs, checker, replay and the
open full-width measurement problem. The canonical ECDLP frontier graph was
checked and needs no update from algebraic input counts.
