#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false)
#align(center)[#text(size: 17pt, weight: "bold")[P-256 maps, covers and Cartier joint]]
#align(center)[TASK-20261025-9b6553 · Local check · 25 October 2026]

*Outcome:* the assigned mathematics and four serialized isogenies pass the local checks. The Cartier argument excludes an extra rational order-r factor in the quartic Prym without computing its exact Frobenius polynomial. This packet cannot discharge the canonical scientific-review gate: pushed inputs and model verification are absent.

*F5 exact algebra.* Public p and r were proven prime. The published generator has order r, and the full Hasse interval has the single multiple r. Complete prime-factor verification makes the Frobenius discriminant fundamental, forcing f_pi=f_E=1. Fresh division-polynomial factorizations and direct symmetric Vélu formulas reconstruct maps of degrees 3,5,11,11. All serialized maps, endpoints, dual landings and both coordinate compositions in both directions agree. Ten other degree-five factors of psi_11 fail the independent checks.

*F7 geometry and count.* The quartic u⁴=x³−3x+b is smooth of genus three; w²=z⁶−3z²+b is smooth of genus two. For either degree-two cover, norm after pullback is multiplication by two. Hence pullback injects the odd order-r source subgroup. A fresh PARI/SEA count reproduces the genus-two complementary trace 167631093631314538742209370567683050917 and its order below r. Fresh fibre controls include nonsplit supports and the actual infinity multiplicities.

*Cartier proof.* The regular forms dx/u², dx/u³, x dx/u³ have automorphism characters −1,i,i. For p=3 modulo4, semilinear Cartier sends i to −i, whose holomorphic eigenspace is zero. Directly, for p=4m+3, the latter forms have expressions f(x)ᵐ dx/uᵖ and x f(x)ᵐ dx/uᵖ; their numerator degrees are below p−1, so Cartier selects no term. The corrected Achter–Howe congruence gives p dividing A in chi_P=T⁴+A T²+p². Weil bounds give A=k p, k=−2,−1,0,1,2; all five candidate orders are coprime to the actual r. Thus J(C)(Fp) has exactly one r-factor, carried by the source image.

*Control and limits.* At p=5,b=1, the Prym Cartier matrix is [[2,1],[1,0]] and chi_P=T⁴−2T³−T²−10T+25. The forbidden extension to p=1 modulo4 fails. This rational-point conclusion does not remove geometric r-torsion. A destination solver, arbitrary-class quartic arithmetic, useful relation rank and complete attack costs remain unimplemented or unmeasured. Sage/PARI libraries are shared dependencies; no formal proof certificate is claimed.

*Procedure:* blind-derivation.md predates producer table inspection, with one explicitly recorded narrative exposure while locating the equation. The local custody exception preserves the unmet pushed-input precondition. No uploads, git mutations, external messages or official scientific transitions were made.

*Evidence:* independent_checks.py; independent-results.json; fibre_controls.py; fibre-results.json; exact stdout/stderr and commands.json. Source: Achter–Howe, arXiv:1710.10726v5, corrected sections 2.2–2.5, read after the blind record. Full derivation, provenance, coverage and deviations are in review.md and cartier-proof-note.md.

#pagebreak()
#align(center)[#text(size: 16pt, weight: "bold")[Typed correspondence and remaining obligation]]
#v(6mm)
#image("diagram.svg", width: 100%)
#v(6mm)
The solid arrows describe locally checked maps or derived factor decompositions for the exact published P-256 equation. The dashed arrow marks unresolved implementation work. The four elliptic endpoints are defined by their complete coefficients and kernels in the retained producer JSON, whose identities are checked in independent-results.json. The source curve UID is displayed in the diagram.

*Connectedness:* the F5 finite kernels are etale and geometrically disconnected, while the connected Prym is a two-dimensional abelian variety. Rational isogeny kernels are Frobenius-stable subgroups; their nonzero points need not be Fp-rational.

*Scientific scope:* no performance quantity is measured, no attack-cost conclusion is drawn, and no canonical shared graph is changed by this local review.
