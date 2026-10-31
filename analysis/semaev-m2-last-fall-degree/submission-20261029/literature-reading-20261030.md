# Primary-source reading custody, 2026-10-30

This records complete extracted-text reading, not independent proof review.
The companion JSON binds the retrieved PDF bytes and text hashes. Copyrighted
PDFs and extracted texts remain in the private runtime directory. No trial,
new bound, or official research-status change follows from this reading.

Kousidis–Wiemers, [arXiv:1906.05594](https://arxiv.org/pdf/1906.05594),
Definitions 2.1–2.2, uses the span/top-form first-fall convention, with trivial
syzygies removed. Remark 3.3 attributes the m=2 value 2 to Kosters–Yeo.
Table 1 averages ten repetitions and reports observed regularity degree 5
for n=37–48. Section 4 defines that observable as the largest Magma step
degree and reports the polynomial-subspace transition at n=45. Its question
(4.1) is about regularity degree, not directly a certified LFD lower bound.
These checks confirm the existing submission README's novelty boundary;
they do not establish that no other rigorous bounds exist.

Huang–Kosters–Yang–Yeo,
[arXiv:1505.02532v2](https://arxiv.org/pdf/1505.02532v2), is the distinct
four-author paper. Definitions 2.1 and 2.5 specify polynomial-ring closure
and LFD; Proposition 2.6(iii) gives the largest-fall characterization.
Proposition 2.6(iv) preserves max(LFD, input degree) under equal spans,
not unconditionally LFD itself. Theorem 4.4 assumes the pre-descent ideal
is radical and zero-dimensional and has an injective coordinate projection.
Section 6 explicitly explains why a single multivariate summation equation
does not meet the zero-dimensional hypothesis without field equations.
The downloaded header says v2, 18 June 2015, while its body date says
24 September 2018; the byte hash identifies this exact copy.

For the campaign, retain the polynomial-ring LFD definition of
[the dossier, §0.2](../theorem-dossier.md). Its Proposition 1.1 supplies
the Boolean-to-polynomial closure bridge for degree at least 2. The
certificate argument uses containment of the true closure in a checked
kernel; equality is unnecessary. An accepted codimension larger than an
independent exact solution count supplies the lower bound. First-fall
conventions must remain separately named. This is a definition cross-check,
not a new certification of the dossier's proofs.

The exact three-author HKY CRYPTO 2015 paper remains inaccessible: both
[ePrint 2015/573](https://eprint.iacr.org/2015/573.pdf) and the
[official IACR archive](https://www.iacr.org/archive/crypto2015/92160209/92160209.pdf)
returned HTTP 403. Reading the expanded four-author paper does not close
that gap. No claim of a complete novelty search is made.
