#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Certified public prime-field fixtures for ICPERF

*Engineering preparation, 2026-10-17 UTC.* Three public prime-order curves
were selected before any factor base or target. These are curve fixtures, not
index-calculus trials or speed measurements. The JSON records and source are
linked from the companion Markdown report.

#image("2026-10-17-icperf-prime-fixture.svg", width: 100%)

The chart counts deterministic candidate curves checked at seed 20261017.
At 53 bits a 128-candidate search ended without an accepted curve; the same
sequence extended to candidate index 129. That bounded result says nothing
about other 53-bit curves.

== Exact accepted identities

#table(
  columns: (0.5fr, 0.7fr, 2.1fr, 2.1fr),
  inset: 5pt,
  [Bits], [Checked], [Field prime p], [Certified order N],
  [50], [20], [1125899798684033], [1125899778887903],
  [53], [130], [9007198804718503], [9007198733080069],
  [63], [80], [9223372021248595841], [9223372018953067627],
)

Each record includes the exact a, b, affine witness, candidate prefix, source
SHA-256 and runtime provenance. Source commit: `d5a7a863f34ec321623cd56275243b0a7a851d1a`.

== Independent certificate

The plain-Python verifier checks p and N prime, a nonsingular curve, an affine
nonidentity witness P on it, N P = O, the exact Hasse inequality
`(N-(p+1))² <= 4p`, and `N² > 16p`. Since N is prime, P has order N. Thus N
divides the curve order; the Hasse interval contains N and is narrower than N,
so the curve order equals N. This check does not call Sage cardinality. Sage
proof-mode primality also returned true for p and N in all three records.

== What remains

Factor bases, point decomposition for m=2..8, direct S8 capacity, relation
yield, useful rank, linear algebra, target recovery, and same-point rho have
not been measured on these curves. The prime implementation's compact scan
currently needs p below 2^32; a wide exact path or a charged fallback is the
next implementation gate. Base selection must stay target-blind, and its
construction and rejected candidates belong in cold-start cost.

The canonical ECDLP frontier graph was checked. It is unchanged because this
preparation adds no reviewed attack-cost finding.
