#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Prime-field divisor fit and a target-blind m=8 base

*Input preparation and correctness observations, 2026-10-17 UTC.* Exact
factorizations of p−1 were checked for three certified public prime-order
curves. The chart shows the closest divisor to twice the default factor-base
size for m=2…8. Divisor fit is neither realized point count nor ECDLP speed.

#image("2026-10-17-icperf-divisor-fit.svg", width: 100%)

The fixed 53-bit field has p−1 = 2 × 3 × 1501199800786417; its closest small
divisor is 6 for every cell. This excludes a matched-size multiplicative
coset base on that field, not on other 53-bit fields. The 63-bit field has
a divisor within 15% of twice the default size for m=3…8.

== Exact m=8 preparation on the 63-bit field

#table(
  columns: (1.3fr, 2.3fr), inset: 5pt,
  [Quantity], [Recorded value],
  [Default size B], [406],
  [Chosen divisor d], [788; relative divisor gap 24/812 = 2.96%],
  [Realized base], [380 distinct on-curve x-coordinates],
  [Membership equation], [x^788 − g^788; two nonzero terms],
  [Root proof], [ζ has exact order 788; one root draw],
)

The base uses fixed seed 20261017 and was created before any target was chosen.
Its complete point list and digest are in the machine-readable record. The
checker independently enumerated all 788 coset x-values, lifted each one,
compared the ordered 380-point list, and rejected a changed-point control.
The explicit-divisor code avoids factoring all of p−1 during base construction;
the field-divisor selection itself used a Sage factorization and remains setup
work to charge in a future trial.

== Remaining scientific gate

An equal-realized-size 380-point random and small-x control, planted and
unplanted decomposition, direct S8 capacity, eight-summand S9 or chained S3,
observed solver degree, useful relation rank, complete target work and matched
rho are unmeasured. A sparse input equation does not establish low degree of
regularity. The archived 0.053-second constructor timing excludes interpreter
startup, field search and factorization and is not a complete cost.

The canonical ECDLP frontier graph remains unchanged; this search adds no
reviewed attack-cost result. Source paths and exact digests are in the
companion Markdown report.
