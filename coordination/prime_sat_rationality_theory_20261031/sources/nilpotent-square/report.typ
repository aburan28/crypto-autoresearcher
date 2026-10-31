#set page(paper: "a4", margin: 18mm, numbering: "1")
#set text(size: 10pt)
= Uniform nilpotent square witness
*2026-10-31 · Unreviewed derivation · No execution*

For a verified split polynomial U of degree k, the ordinate rationality condition has an existential alternative with exponent k instead of an Euler exponent depending on p. This supplies a uniform candidate for every chart, including identically zero B.

#image("diagram.svg", width: 100%)

== Exact equivalence
Let p>3 be prime, f=X³+aX+b define a nonsingular curve, and U be monic, split over the prime field, of positive degree k. Every root α of U has square-or-zero f(α) if and only if there exists C of degree below k such that:
#raw("(C² − f)^k = 0 modulo U.", block: true)
Forward: choose a square root at each distinct root of U and interpolate C. Each linear factor divides C²−f, so its kth power contains every multiplicity in U. Backward: evaluation at any root α gives C(α)²=f(α). This works for repeated roots and k≥p without division by multiplicities. U=1 is an explicit empty case.

== Why exact square roots modulo U are too restrictive
Take f=X³+X, U=X² over any prime p>3. This curve is nonsingular and the support is the rational branch point (0,0). Writing C=c₀+c₁X, the equation C²=f modulo X² forces c₀=0 and then 0=1 in the linear coefficient. It wrongly rejects. The nilpotent equation accepts C=0 because f² is divisible by X². This is a symbolic counterexample, not an executed trial.

== Exact auxiliary multiplicity
If U has r distinct roots and q of their f-values are nonzero squares, there are exactly *2^q p^(k−r)* coefficient witnesses C. Evaluation from k coefficients onto r values is surjective with kernel dimension k−r. Each nonzero square offers two signs. A nonsquare anywhere gives zero witnesses. Repeated roots therefore create redundant coefficients that projected search must eliminate.

== Arithmetic and recovery boundary
The quotient dimension and powering exponent are bounded by k, but k unknown field coefficients are added. Variable-U multiplication/reduction, bit ranges, carries and proof checking must still be counted. Field equations need prime-field membership: solving over an algebraic closure would change the predicate. No degree-of-regularity or runtime advantage follows from this equivalence.

After recovering verified roots of U, evaluate and square-check C to provide balanced root lifts. Retain the residual ratio for unbalanced signs and exact local multiplicities. A target outside U keeps its known ordinate and separate norm factor. Checking a supplied C needs no square-root search; finding C is part of solving.

== Next comparison and provenance
Compare the complete Euler block, the uniform nilpotent-square block, and disjoint B-stratified guards, with identical interval, norm, chart and projected signed outputs. Retain every B=0 chart. Freeze fixtures before software execution; charge auxiliary projection and all reconstruction/checking.

The full proof is in proof.md. Chinese remainder background was read on 2026-10-31 from #link("https://stacks.math.columbia.edu/tag/00DT")[Stacks Project Lemma 10.15.4]. Internal inputs are the unreviewed signed-recovery and conditional-square notes. This note asserts no novelty and changes no accepted finding or canonical graph.
