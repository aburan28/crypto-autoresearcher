# DRAFT — A remark on the "fake first fall degree" of Nagao (ePrint 2015/984)

*Isogeny Labs technical note, draft 2026-09-26. Not submitted. Internal
evidence: KN-FIND-936151, EV-SEMBIN-1ca3c8; literature check in
`docs/ecdlp-literature-review-20260926.md` §5.*

## Abstract

Nagao's draft "Complexity of ECDLP under the First Fall Degree Assumption"
(IACR ePrint 2015/984) distinguishes the *first fall degree* d_F of a
polynomial system from a *fake* first fall degree d'_F computed modulo the
field equations. Its Lemma 4 asserts d_F ≤ d'_F, so that a bound on the easily
computed fake quantity bounds the true one. We give two small systems over F_2
for which d'_F = 2 < d_F = 3. We then explain why the paper's own applications
are unaffected: they check the unreduced product degrees instance by instance.
The only consequence is that the inference "fake bound ⇒ true bound" cannot be
used as a general lemma.

## 1. Definitions (as in 2015/984, §5)

Let f_1, …, f_M ∈ K[X_1, …, X_N].

- **First fall degree d_F (Definition 5).** The minimal d for which there are
  g_i with max_i deg(g_i f_i) = d, deg(Σ g_i f_i) < d, and Σ g_i f_i ≠ 0.
- **Fake first fall degree d'_F (Definition 6).** Over F_p, with
  S_fe = {X_i^p − X_i}, the same conditions with every degree taken after
  reduction mod S_fe, and with Σ g_i f_i ≢ 0 mod S_fe.

The printed condition (1) reads "max_i deg(g_i f_i) ≥ d_F". Under that
literal reading every nonzero system has d_F at most the degree of any
nontrivial fall, and the lemma holds only vacuously. We use the equality
reading: the degree at which the fall occurs. That is the reading the paper's
complexity estimates need, and the standard definition (cf. Caminata–Gorla,
ePrint 2021/1611).

## 2. Counterexample

Over F_2[X, Y], let f_1 = X²Y and f_2 = XY + X.

- **True first fall degree.**
  - At degree 2 the only products available are constant multiples of f_2,
    which is nonzero of degree 2, so nothing falls.
  - At degree 3, f_1 + X·f_2 = X²Y + X²Y + X² = X², so a fall occurs.
  - Hence **d_F = 3**.
  - The same holds with the field equations adjoined to the system. At
    degree 2 the leading forms XY, X² and Y² of f_2, X² + X and Y² + Y are
    linearly independent, so there is still no fall.
- **Fake first fall degree.**
  - Modulo S_fe, f_1 ≡ XY, and f_1 + f_2 ≡ X has degree 1 < 2.
  - Hence **d'_F = 2**.

So d'_F = 2 < 3 = d_F, and Lemma 4 fails.

A second witness is f_1 = X_1X_2 + X_3, f_2 = X_1X_3 + X_2 (again 2 < 3).
Among 400 random pairs of multilinear quadratics in three variables over F_2,
94 violate the lemma (23.5%; KN-FIND-936151).

## 3. What survives

The mechanism is simple. Reducing a product g_i f_i mod S_fe can lower its
degree, so a fall that is "fake" (visible only after reduction) need not
correspond to any fall of the unreduced system. The paper's Lemma 3 (the
degree-preserving representation of F ≡ 0 mod S_fe) controls the *sum*. It
says nothing about the individual products whose maximum defines d_F.

The inference can be recovered per instance: if every g_i f_i in a
fake-degree-v certificate already has unreduced degree ≤ v, then d_F ≤ v. The
paper's applications (its Propositions 2–3, following Semaev ePrint 2015/310)
exhibit explicit certificates of this kind. Their conclusions therefore do not
depend on Lemma 4. They remain conditional on the first fall degree
assumption, which Huang–Kosters–Yeo (CRYPTO 2015) and Kosters–Yeo
(arXiv 1503.08001) give evidence against.

## 4. Prior remarks

We found no earlier statement of this defect. The following were checked in
full text:

- Huang–Kosters–Yeo (ePrint 2015/573);
- Galbraith–Gaudry's survey (ePrint 2015/1022, §9.4 discusses Nagao's
  decomposition method only);
- Huang–Petit–Shinohara–Takagi (ePrint 2015/358);
- Kousidis–Wiemers (ePrint 2015/1121);
- Kosters–Yeo (arXiv 1503.08001);
- Caminata–Gorla (ePrint 2021/1611).

The ePrint record of 2015/984 has a single version (2015-10-12).

## To do before posting

- [ ] Independent human check of §2, in particular the degree-2 no-fall
      argument with field equations adjoined.
- [ ] Decide whether to contact the author first. This is a courtesy for a
      draft that was never revised.
- [ ] Typeset (LaTeX, ePrint format) and attach the verification script
      (`tools/lemma4_inside_form.py`, tests `tools/test_lemma4_inside_form.py`).
