#set page(paper: "a4", margin: (x: 16mm, y: 15mm), numbering: "1")
#set text(size: 10pt)
#set par(leading: 0.55em)
= Signed recovery and localized rationality
*Preliminary derivation — unreviewed, unimplemented, zero trials.*

The projector draft recovers interval coordinates and multiplicities from supplied quotient idempotents. This continuation recovers the signed divisor of a supplied function h=A+B y using exact polynomial valuations. It also identifies a smaller support on which rational-ordinate checks suffice.

#image("diagram.svg", width: 100%)

== Exact domain and norm support
Work over a prime field with p>3 on a nonsingular short Weierstrass curve y²=f(x). The chart has exact pole order d≤6. Its norm is N=A²−f B². For finite target R=(r,s), the checked identity is c N=(X−r)U, with c equal to 1 or −1. Obtain norm roots by taking the independently verified factors of U and adding one occurrence of r. Keep r even outside the interval. For identity target use c N=U.

== Three exact local cases
At a norm root alpha, let m be its norm multiplicity, g=min(v(A),v(B)), and q=m−2g. Polynomial valuations use repeated exact division; the zero polynomial has infinite valuation.

*Nonbranch, q>0.* Remove (X−alpha)^g from A and B to get A₀,B₀. Their values cannot both vanish. The norm identity forces B₀(alpha) nonzero, so beta=−A₀(alpha)/B₀(alpha) is a rational nonzero ordinate. The selected sign has order g+q and the opposite sign has order g. This avoids a square-root computation and a local-series expansion in this case.

*Nonbranch, q=0.* Both signs have order g>0. Use the known target ordinate when alpha=r; otherwise a checked square root of f(alpha) is required. A nonsquare rejects the chart. Choosing the other square root gives the same multiset.

*Two-torsion.* When f(alpha)=0, the local parameter is y and X−alpha has order two. The orders 2v(A) and 2v(B)+1 have different parity, so they cannot cancel. The unique point (alpha,0) has multiplicity min(2v(A),2v(B)+1)=m. This includes characteristic five and identically zero A or B.

== Why the local formulas hold
Away from two-torsion, X−alpha is a uniformizer: (y−beta)(y+beta)=(x−alpha)F(x), and y+beta is a unit. In the q>0 case the involuted residual function is a unit at the selected sign; its norm therefore has precisely the same local order. At two-torsion, nonsingularity gives f'(alpha) nonzero and x−alpha=y²/F(x), with F a unit. No factorial or division by a multiplicity is used.

== Signed output check
The local multiplicities sum to d. For finite R, remove exactly one actual point −R and check its presence. Verify residual degree k, agreement with U multiplicities, curve and declared base/subgroup membership, and exact group sum R. Retain all lower-pole charts; identity padding and distinct permutation expansion follow the chosen output predicate. Checking only h(P)=0 would miss multiplicity errors.

#pagebreak()
== A smaller rationality condition
Let D be the monic gcd(A,B), and write A=D A₁, B=D B₁ with coprime residual polynomials. Assume the norm has already been verified to split over the prime field, as supplied by interval recovery plus the target factor.

Outside D, every nonbranch norm root has a rational ordinate from the ratio formula; branch roots are rational automatically. Roots of D contribute balanced geometric pairs, possibly with an additional rational residual zero. Therefore the whole zero divisor is supported on rational points if and only if f(alpha) is zero or a square at every root alpha of D. A nonsquare common-root pair cannot disappear when subtracting a rational target.

For gD=degree D at least one, define T=f(f^((p−1)/2)−1). Euler's criterion and the root multiplicity bound give the equivalent quotient condition:
#raw("T^gD = 0 modulo D.", block: true)
If D=1, this condition is vacuous. The original rationality test modulo U can thus be localized to D, conditional on exact gcd and split-norm verification. This is an algebraic equivalence; it is not yet a SAT or degree-of-regularity result.

== Exact chart sizes and a solver route
In the five-affine finite-target chart, A is monic cubic and B is at most linear. If B is nonzero, degree D is at most one. If B=0, degree D is three and the balanced-pair chart must be kept. For the five-affine identity-target chart, B is monic linear and A has degree at most two, again giving degree D at most one.

A possible complete encoding stratifies by gcd degree, introduces monic D and coefficient identities A=D A₁, B=D B₁, and checks a Bezout identity for the residual pair. All degree strata, auxiliary fibers, coefficient-generation costs and projections must be specified. Computing gcd after a completed assignment is different from propagating gcd information during search. The next test is whether these strata and localized rationality constraints produce inexpensive certified pruning.

== Cost and proof boundary
After verified U recovery, conservative O(d³) field operations cover norm verification and local polynomial arithmetic for fixed d≤6. Square-root construction remains separately charged. At most floor(d/2) balanced nonbranch coordinates can require roots, because each uses at least two divisor degrees. Known target ordinates and ratio cases require none. Supplied square roots have direct square checks.

This recovers a divisor for a supplied chart. Completeness of chart enumeration, normalization/descent, signed output coverage, partial-assignment propagation, auxiliary-variable costs and regularity still need their own checks. No numerical trials, solver calls or timing measurements occurred.

== Sources and artifacts
Sutherland's MIT18.782 Lecture23 (internally dated26November2013), Theorem23.3 and Theorem23.16, was opened30October2026 for pole-order/basis and group-law background. The local recovery formulas and gcd-support equivalence are the present unreviewed derivation. The detailed argument and source/input hashes are in proof.md and report-inputs.json. Neither source reading nor this rendered report establishes novelty or independent acceptance.
