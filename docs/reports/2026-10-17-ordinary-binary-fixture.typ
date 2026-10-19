#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Ordinary binary subgroup input near 2^59

*Input-selection screen, 2026-10-17 UTC.* Fix GF(2^61) with polynomial
t^61+t^5+t²+t+1 and E_b: y²+xy=x³+b. Inspect b=2..33 in order; stop at the
first curve with a certified prime factor r in [2^50,2^63]. The screen stopped
at b=31 after 30 attempts. Every attempted group order was fully factored,
each factor checked prime, and the product reconstructed.

#image("2026-10-17-ordinary-binary-fixture.svg", width: 100%)

For b=31=z⁴+z³+z²+z+1, j=1/b lies outside F₂. This ordinary binary curve is
not descended from F₂. Its group order is
2,305,843,010,228,847,052 = 4 × 576,460,752,557,211,763,
where r=576,460,752,557,211,763 is prime (log₂ r≈59.00).

The polynomial-basis source point P=(1,446358225178544464) projects by
cofactor four to G=(938161616493806685,1665004790792120888). Independent
Sage arithmetic checked irreducibility, primality, 4P=G, rG=O and curve
membership. Since G has order r and Hasse's interval contains only one
multiple of r, namely 4r, this also certifies the full curve order.

#table(
  columns: (1.3fr, 2fr), inset: 5pt,
  [Stage], [Current evidence],
  [Curve and subgroup], [Explicit generator; independent Sage replay],
  [Factor base, m=2…8, direct S₈], [Unmeasured],
  [Relations, rank, LA, target], [Unmeasured],
  [Complete IC and matched rho], [Unmeasured],
)

This is an input fixture, not a speed comparison. The 30-curve list is a
deterministic bounded search, not a random sample. The direct F₂-x rank gate
for curves descended from F₂ does not apply to this curve. A frozen target-blind
base and complete experiment remain required.

Data: research/icperf_ordinary_binary_fixture_20261017/
Screen, fixture, and Sage replay are source- and input-hash bound.
