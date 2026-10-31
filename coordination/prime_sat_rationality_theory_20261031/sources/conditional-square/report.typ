#set page(paper: "a4", margin: 18mm, numbering: "1")
#set text(size: 10pt)
= Conditional square witnesses
*2026-10-31 · Unreviewed derivation · No trials or solver runs*

A common-root rationality condition can be encoded without a polynomial gcd witness when the ordinate coefficient B is linear. This note gives an exact existential construction and counts its auxiliary fibers. It leaves the frozen implementation under independent review unchanged.

#image("diagram.svg", width: 100%)

== Preconditions
Over a prime field with p>3, use a nonsingular curve y²=f(x)=x³+a x+b and h=A+B y, with degree A at most three and degree B at most one. Retain the exact norm identity, splitting/interval constraints, target vanishing, all pole strata, multiplicities and signed recovery. Conditional on split norm, only common roots of A and B need an extra rationality condition: outside them the norm equation provides a rational ordinate by division; at a common root both geometric signs must be rational.

== One conditional equation
For B=b₁X+b₀ with b₁ nonzero, impose b₁z=1 and b₁α+b₀=0. Set c=A(α), F=f(α). The desired condition is c nonzero OR F square-or-zero. It is equivalent, by existential projection, to:
#raw("β² = F + c u", block: true)
If c is nonzero, any β works with unique u. If c=0, a square root is required. The fibers have p solutions in the noncommon case, p for c=F=0, and 2p for c=0 with F a nonzero square. Invalid nonsquares give no solutions. This redundancy can burden projected search.

== A guard removes the free choices
Use five equations instead:
#raw("c u = 1−e;   c e = 0;   u e = 0;
(1−e) β = 0;   β² = e F.", block: true)
For c nonzero these force e=0, u=c⁻¹, β=0. For c=0 they force e=1, u=0 and β²=F. Thus fibers have respectively one, one, two, or zero elements in the cases above. Boolean e follows from these equations. The two square-root signs project to the same balanced signed multiset. A canonical half-range β would remove that duplication but adds a bit-comparison cost.

#pagebreak()
== Explicit quadratic lift
Write A=a₃X³+a₂X²+a₁X+a₀ and add:
#raw("q₁=a₃α+a₂;  q₂=q₁α+a₁;  c=q₂α+a₀;
v=α²;  F=αv+aα+b.", block: true)
With the two equations fixing α,z and the five guard equations, this is *ten auxiliary field variables and twelve equations of degree at most two*. The variables are α,z,q₁,q₂,c,v,F,e,u,β. The single slack equation variant uses nine variables and eight equations, with its larger fibers. These are exact symbolic block counts; they exclude the rest of the encoding. Fixed or zero chart coefficients may simplify them.

== Preserve the whole domain
Three disjoint strata cover B: nonconstant linear (the guard above), nonzero constant (no common roots, certified inverse of b₀), and identically zero (retain the full rationality test). Normalized chart shapes determine which strata are possible. Do not delete the zero-B charts, wrapped intervals, repeated roots, target roots outside the interval, or lower-pole cases. The signed reconstruction and certificate checks remain necessary.

== What this establishes and what to check next
This is a derived projection equivalence under split-norm hypotheses. It replaces an Euler rationality block in the linear-B stratum. It does not establish a degree-of-regularity or runtime advantage. Quadratic field generators still require field ranges, carries and arithmetic when translated to SAT, and their highest degree does not determine solving degree.

Next obtain independent review, then implement the complete stratum union under a fixed contract. Compare full Euler, slack and guarded constraints on identical complete projected signed outputs. Charge setup, all constraints, bit conversion, search, projection, reconstruction and certificate checking. Specify generators and term order before any degree measurement.

== Provenance
Full derivation: proof.md in this directory. Prior input: ../shared-chart-signed-recovery/proof.md, common-root localization. Standard pole-order background was reread on 2026-10-31 from Andrew Sutherland, MIT 18.782 Lecture 23, Theorem 23.3:
#link("https://math.mit.edu/classes/18.782/2023sp/LectureNotes23.pdf")[Lecture notes]. The guard and fiber calculation are this note's unreviewed derivation; no literature novelty is asserted. No canonical graph changes because this note changes no accepted finding.
