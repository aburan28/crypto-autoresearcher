#set page(paper: "a4", margin: (x: 19mm, y: 18mm), numbering: "1")
#set text(font: "Libertinus Serif", size: 10.5pt)
#set par(justify: false, leading: 0.65em)
#set heading(numbering: none)
#set document(title: "Joint ideal layers and specialization", author: "TASK-20261030-6394ed")

= Joint ideal layers and specialization
*A conditional finite certificate · 30 October 2026*

TASK-20261030-6394ed · GOAL-PFDR-fd09e0 · BATCH-ee839d

*Manual derivation; independent review pending. Zero scientific calls.*

The exact three-equation, six-variable Semaev ideal has an explicit global monic ideal-power control. A fixed finite domain additionally needs a clipped-intersection certificate before its formal modulus exponents can be transferred to a full integer lattice index. No ranks, actual cell, numerical reach, root or IC gain were evaluated.

#image("diagram.svg", width: 100%)

The full proof is retained in *joint-certificate.md*. This PDF is a concise overview; the separately retained certificate-schema.yaml, theorem-matrix.yaml, proof-search-map.yaml and source-manifest.json specify exact conditions and provenance.

The input is I=(F1,F2,F3), Jμ=(N,I)^μ, with formal N independent of all coefficient parameters, J∞=0 and x=(z1,z2,z3,z4,h1,h2). The protocol fixes F1=S(c1+z1,c2+z2,d1+h1), F2=S(c3+z3,c4+z4,d2+h2), F3=S(d1+h1,d2+h2,q). There is one modulus. The four leaf bounds X and two internal bounds Y remain distinct.

*Source and evidence status:* primary source reading and manual algebra only. The report is a derivation, not an executed or independently reviewed certificate. Root owns publication and the subsequent distinct review sessions.

#pagebreak()
= What is proved, and what is conditional

*Global structure for the exact equations.* Over A0=Z[a,b,q,c1,c2,c3,c4,d1,d2], use auxiliary x-weights (2,2,2,2,1,1). The unique top terms of F1,F2,F3 are respectively z1²z2², z3²z4², h1²h2², each coefficient 1. The child top weight is 8 versus at most 7 for competing terms; the target top weight is 4 versus at most 3. Centers lower weights.

These three monomials are pairwise coprime. Introduce independent coefficient variables t1,t2,t3. The monic product criterion makes F\_i−t\_i a Gröbner basis over A0[t][x]. Its standard x-monomials W form a free A0[t]-basis of the quotient, which is A0[x] with t\_i acting by F\_i. Each x-monomial uniquely factors as a product of the three leading monomials times w in W. The resulting F^β w have distinct monic leading terms. Therefore the products F^β with total exponent j are a monic Gröbner basis for I^j, and A0[x]/I^j is free over A0. This holds after arbitrary coefficient specialization. It proves global p-saturation of the ideal powers; no regular-sequence assumption is made.

*The auxiliary order does not reproduce the bound-induced native order.* It certifies ideal membership and global flatness. It does not enumerate the actual domain M or determine a clipped rank.

*Exact formal-modulus module.* Fix an explicit finite monomial set M, d=|M|, and V=span(M). Define the joint flag H\_j=I^j∩V and r\_j=dim over Q(c). In an expansion g=Σ N^a g\_a, ideal membership is exactly g\_a in I raised to max(μ−a,0). An adapted flag basis v\_i therefore gives supported module basis N^λ\_i v\_i, with

*q\_N = Σ λ\_i = μd − Σ from j=1 to μ of r\_j.*

This is a formal N-order. A coefficient-field unit can have large integer size or nonzero specialized p-valuation. The identity alone is not an integer determinant formula.

*Finite clipped certificate.* Reduce every m in M by the proved monic product basis of I^j. Let T\_j contain the resulting standard remainder columns. Supply a common invertible matrix B over A0[1/Δ] with inverse, and identities T\_j B=(0,C\_j), L\_j C\_j=identity. These prove that each kernel is exactly the corresponding prefix of B and remains so under every allowed base change. Membership-only vectors or generic row rank are insufficient.

For each fixed finite μ,M, such a nonzero Δ and finite identities exist after localization. The actual T\_j, ranks, B, left inverses and Δ have not been produced for the protocol cells. The quantifiers are “for each fixed packet there exists a finite localization, then every good specialization.” No one Δ, uniform packet size, exceptional-fiber frequency or changing-multiplicity efficiency is inferred.

#pagebreak()
= Prime layers, integer span and height

*Conditional bridge to the full integer lattice.* Put N0=p prime and specialize parameters to integers with p not dividing the clipped certificate's Δ. Work over O=Z\_(p). Global power saturation proves ((p,I)^t:p)=(p,I)^(t−1). The clipped base-change identities then prove L\_t=H\_t+p L\_(t−1), where L\_t=(p,I)^t∩O^M. Its exact p-layers have dimensions r\_(μ−a). The complete supported integer lattice contains p^μ Z^M, so its index has only the prime p and is exactly p^q\_N. Its weighted determinant is

*p^q\_N × product over e in M of X^(e1+…+e4) Y^(e5+e6).*

Its usable determinant-level budget is Σ r\_j. At μ=2, the ten product generators give q\_N=2d−r1−r2. No rank value was evaluated. Suppressing F2,F3 reproduces the archived principal accounting K=t·d−q; the one-polynomial Newton-polytope ceilings do not thereby transfer to the joint ideal.

Selected integer rows can have an additional index m in the complete lattice, multiplying their determinant by m. Rational rank does not show equality; p-local equality only shows p does not divide m. If raw rows have certified full p-local span, their prime-to-p saturation equals the full p-primary lattice. This can remove unit-index losses; actual saturation/congruence-preimage construction, output heights and costs still need evidence. Denominator clearing is a possible raw-row loss, not an unavoidable loss for every implementation.

*Exact controls.* Generic (N,cx)=(N,x), but at c=p,N=p,x=1 the normalized row x evaluates to 1, while both original generators evaluate to p. Clearing the denominator gives valid cx, with coefficient size p. A matrix with rows (1,1) and (1,1+c) has denominator 1 and rational rank two at c=p, but residue rank one. The monic ideal (x+c y), clipped to span(x), has generic intersection zero and intersection span(x) at c=0. At c=p it fails residue clipping despite a free global quotient. These controls separate units, rank minors and clipped base change. Repeating a relation leaves the ideal unchanged.

*Integer heights.* For H bounding 1 and all nine integer parameters, the exact affine inputs satisfy coefficient L1 norm at most 28(H+1)^4. If a retained symbolic row has cleared numerator P\_i=d\_i g\_i with an integral ideal witness, its specialized L1 norm is at most norm1(P\_i) H^degree\_c(P\_i) max(1,|N0|)^degree\_N(P\_i). Charge these degrees/norms, denominator sizes, transformation coefficients and any unremoved row index.

Alternatively, invert d\_i modulo |N0|^μ and center each coefficient of the resulting row. Its absolute coefficients are at most |N0|^μ/2; subtracting multiples of N0^μ preserves membership. Actual leading terms and integer span must be checked again. Products of k certified base rows have multiplicity μk and product L1 norm bounds; coefficient reduction must respect N0^(μk). Fixed-packet bounds with H≤p^C give polynomial bit lengths in k and log p, but a changing μ,M packet needs new uniform bounds.

#pagebreak()
= Source boundaries and the exact next obligation

*Ryan primary, actually read.* Keegan Ryan, “Solving Multivariate Coppersmith Problems with Known Moduli,” ePrint 2024/1577, pinned 52-page PDF, archived primary URL in source-manifest.json; SHA256 begins 15dd6ae6b939c51f and is recorded in full there. Read: §2.5 / Heuristic 1 p6; §3 pp7–8; §4.3 pp11–12; §§6.1–6.2 pp19–20; §6.4 / Heuristic 2 pp21–22; Lemma 7 p23; Algorithm 3 p24; Appendix C pp48–51. Full PDF/text stay external, not in Git.

Section 6.1 requires coefficient denominators to be invertible modulo N raised to the precomputation multiplicity. Section 4's optimal integer lattice is defined by integer span; it is not automatic proof that coefficient-field source rows specialize to a complete integer basis. Heuristic 1 assumes zero-dimensionality of the recovered integer ideal. Heuristic 2 assumes the stated polynomial dimension/determinant functions for suitable sets. Lemma 7 retains these assumptions, shared-root/suitability conditions, proportional specialization, strict bound and its growing-log-p condition. Its polynomial-time statement *excludes final root recovery*. Appendix C's fixed-precomputation coefficient bounds do not certify an arbitrary changing base packet.

*Pinned source reading.* cuso commit fb2747d2105a8e48499bf10a3a717cf80c14d079 was inspected read-only: symbolic problem, convert, ideal, optimal, asymptotic, shift\_set\_properties, limit and utils. Its returned-row denominator list is narrower than this design's full witness/minor/span packet. The native model.hpp bytes matched published owner commit 4f27d0cd0a50b94d4f990a593321cf2951015ce9; no unpublished integration was adopted. Historical assigned reviews and upstream S3 §§1–2 / S4–S5 §§7b–7c were read with their original scope and qualifications.

No knowledge MCP is exposed. Exact repository rg retrieval covered the assigned batch, historical joint audit, lead/problem records and generated indexes. This is a bounded retrieval scope, not an exhaustive novelty claim. The auxiliary-order and clipped (x+c y) directions were suggested by the parent after the initial flag derivation and checked manually by this producer. No independent-review status is claimed.

*JOINT-FINITE-PACKET-6394ed:* supply the actual fixed M, monic remainders T\_j, ranks, shared B/inverse, tail left inverses and Δ; prove native row membership and both supported-span directions. At a concrete prime, check units, the actual bound-order trace, integer representatives, full integer index/saturation and heights. This would qualify a finite algebraic interface only.

*JOINT-UNIFORM-HEIGHT-6394ed:* restrict to a fixed finite base packet or prove explicit uniform degree/norm/size/good-locus and construction-cost bounds for the claimed varying μ,k,M and coefficients. No random-parameter success frequency is derived.

Actual short integer equations, tractable extraction, F\_p y-lifts and signs, subgroup/target equality, random-target yield and independent relations, and matched fully charged IC/rho costs remain open. The existing problem is joint-smallroot-reach-baseline-and-oracle-unverified.md. No global problem, canonical graph or frozen record was edited.

Scientific/algorithm calls, trials, ideal/rank/domain computations, workers and provisioned hosts: *0*. All 24 old cells remain unrun; Q4 is terminal no-retry; prior independence exit1 is unwaived. No state promotion or family closure. Contribution: conditional proof interface; no quantitative advantage. Full nine-artifact source/provenance and rendering inspection are recorded beside this PDF.
