#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Koblitz field and subgroup sizes, n=50…63

*Derived input-selection screen, 2026-10-17 UTC.* The reviewed GF(2^53)
Koblitz comparator has target prime r=21,044,858,204,113, about 2^44.26.
Its field has 2^53 elements. These are different size coordinates.

#image("2026-10-17-koblitz-size-screen.svg", width: 100%)

For E_a: y²+xy=x³+a x²+1 over F₂, direct point counts give trace
−1 for a=0 and +1 for a=1. The exact recurrence
 tₙ = t₁ tₙ₋₁ − 2 tₙ₋₂, t₀=2,
then gives group order over GF(2ⁿ) as 2ⁿ+1−tₙ. Every order for n=50…63 was factored and
reconstructed; every factor was checked prime.

#table(
  columns: (1fr, 1fr, 2fr), inset: 5pt,
  [Curve and field n], [Largest r bits], [Largest r],
  [a=0, n=53], [45], [21,044,858,204,113],
  [a=0, n=61], [48], [162,888,033,982,417],
  [a=1, n=59], [45], [25,179,555,920,633],
)

Neither standard binary Koblitz curve has a prime subgroup r≥2^50 at
any field degree n=50…63. The reviewed n=53 result remains a complete
45-bit-subgroup comparator for its exact curve, not a 50-bit-subgroup row.

== Higher field degrees with certified prime divisors

A bounded factor search at n=64…80 found three prime divisors in the requested
2^50…2^63 interval. Each is independently verified prime below 2^64 and
divides the exact group order. Empty search rows are inconclusive.

#table(
  columns: (1fr, 1fr, 2fr), inset: 5pt,
  [Curve and field n], [log₂ r], [Certified r],
  [a=0, n=71], [52.29], [5,513,228,015,079,457],
  [a=0, n=73], [56.26], [86,020,738,150,056,119],
  [a=1, n=73], [62.22], [5,384,682,420,498,870,703],
)

All three rows now have explicit prime-order generators from cofactor projection,
checked in the source arithmetic and independently in Sage. Each Sage replay
checks irreducibility, primality, point validity and rG=O. These are group
fixtures; target panels, factor bases and a complete IC pipeline remain to be
measured. No index-calculus timing or rho comparison was made here.

Data: research/icperf_koblitz_size_screen_20261017/orders.json and
research/icperf_koblitz_subgroup_candidates_20261017/candidates.json.
Fixture and Sage replay: research/icperf_koblitz_subgroup_fixtures_20261017/.
